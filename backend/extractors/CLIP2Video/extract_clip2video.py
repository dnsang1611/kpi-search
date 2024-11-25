import argparse
import os
import subprocess
import sys

import numpy as np
import pandas as pd
from PIL import Image
import torch
import torchvision.transforms as T
from torch.utils.data import DataLoader

from common import init_device, init_model, set_seed_logger
from config import Config

from post_process_scenes import seconds_to_timecode

import argparse


def parse_args():
    parser = argparse.ArgumentParser(description='Extract features from clip2video')
    parser.add_argument('--shots-infos-path', type=str, help="Path to shots infos")
    parser.add_argument('--save-dir', type=str, help="Directory to features")
    parser.add_argument('--start-batch', type=int, help="Start batch")
    parser.add_argument('--end-batch', type=int, help="End batch")

    parser.add_argument('--pad-shot-to', type=float, default=5, help="Pad shots shorter than this duration (in seconds) before extracting features")
    parser.add_argument('--shot-fps', type=float, default=5, help="FPS to use when extracting shots from videos")
    parser.add_argument('--input-size', type=int, default=224, help="Size of the input images to the model")
    parser.add_argument('--batch-size', type=int, default=1, help="Batch size")
    parser.add_argument('--num-workers', type=int, default=0, help="Number of workers for data loading")
    parser.add_argument('--ffmpeg-threads', type=int, default=2, help="Number of threads to use for each ffmpeg worker")
    parser.add_argument('--device', type=str, default="gpu")

    return parser.parse_args()

def load_shot(
    shot_info,
    *,
    pad_shot_to_seconds=5,
    fps=5,
    max_frames=100,
    sample_framerate=2,
    size=224,
    transform=None,
    ffmpeg_threads=2,
):
    video = torch.empty(1, max_frames, 3, size, size)
    video_mask = torch.zeros(1, max_frames, dtype=torch.long)

    # video_id, shot_id, video_path, start_frame, start_time, end_frame, end_time = shot_info
    video_name, video_path, old_start_time, old_end_time = shot_info[["video_name", "video_path", "start_time", "end_time"]]

    duration = old_end_time - old_start_time
    start_time, end_time = old_start_time, old_end_time

    if duration < pad_shot_to_seconds:
        pad = (pad_shot_to_seconds - duration) / 2
        start_time = max(0, old_start_time - pad)
        end_time = old_start_time + pad_shot_to_seconds  # FIXME: this could overshoot the end of the video
        duration = pad_shot_to_seconds

    cmd = [
        'ffmpeg',
        '-y',
        '-hide_banner',
        '-loglevel', 'fatal',
        '-threads', f'{ffmpeg_threads}',
        '-ss', f'{start_time:.2f}',
        '-i', video_path,
        '-t', f'{duration:.2f}',
        '-r', f'{fps}',
        '-q', '0',
        '-vf', f'scale=320x240',
        '-pix_fmt', 'rgb24',
        '-f', 'rawvideo',
        'pipe:',
    ]

    ffmpeg = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    video, _ = ffmpeg.communicate()
    if ffmpeg.returncode != 0:
        print("Error in processing video {}, shot {}".format(video_name, old_start_time, old_end_time), file=sys.stderr)
        return video, video_mask, video_name, old_start_time, old_end_time
    try:
        video = torch.frombuffer(video, dtype=torch.uint8).reshape(-1, 240, 320, 3).detach().clone()
    except:
        print("Error in processing video {}, shot {}".format(video_name, old_start_time, old_end_time), file=sys.stderr)
        print(f"{video_name} {old_start_time} {old_end_time}", file=sys.stderr)
        raise

    video = video.permute(0, 3, 1, 2)  # T x 3 x H x W
    video = video[::sample_framerate, ...]
    video = video / 255.0  # convert to [0, 1]

    if transform:
        video = transform(video)

    video_len = video.shape[0]
    if video_len > max_frames:
        idx = np.linspace(0, video_len - 1, num=max_frames, dtype=int)
        video = video[idx, ...]
        video_len = max_frames
    else:
        pad = torch.zeros(max_frames - video_len, 3, size, size)
        video = torch.cat((video, pad), dim=0)

    # video is (T, 3, H, W)
    video = video.unsqueeze(1)  # T x 1 x 3 x H x W
    video = video.unsqueeze(0)  # 1 x T x 1 x 3 x H x W
    video_mask[0, :video_len] = 1

    return (
        video, video_mask, video_name, 
        seconds_to_timecode(start_time), seconds_to_timecode(end_time), 
        seconds_to_timecode(old_start_time), seconds_to_timecode(old_end_time)
    )


class C2VDataset(torch.utils.data.Dataset):
    def __init__(self, shots_infos_path, start_batch, end_batch, **kwargs):
        self.shots_infos = pd.read_csv(shots_infos_path)
        self.kwargs = kwargs

        # Filter out invalid batch
        self.shots_infos = self.shots_infos[
            (start_batch <= self.shots_infos["batch_id"]) &
            (self.shots_infos["batch_id"] <= end_batch)
        ].reset_index(drop=True)

    def __len__(self):
        return len(self.shots_infos)

    def __getitem__(self, item_id):
        return load_shot(self.shots_infos.loc[item_id], **self.kwargs)

class CLIP2VideoExtractor:
    def __init__(self, args):
        self.args = args
        self.device = None
        self.model = None

        # obtain the hyper-parameter, set the seed and device
        self.conf = Config(checkpoint='pretrained', clip_path='pretrained/ViT-B-32.pt')
        self.conf, self.logger = set_seed_logger(self.conf)
        self.conf.gpu = args.device

        self.load_shot_args = {
            'pad_shot_to_seconds': args.pad_shot_to,
            'fps': args.shot_fps,
            'max_frames': self.conf.max_frames,
            'sample_framerate': self.conf.feature_framerate,
            'size': args.input_size,
            'transform': T.Compose([
                T.Resize(args.input_size, interpolation=Image.BICUBIC),
                T.CenterCrop(args.input_size),
                # T.ToTensor(),
                T.Normalize((0.48145466, 0.4578275, 0.40821073), (0.26862954, 0.26130258, 0.27577711)),
            ]),
            'ffmpeg_threads': args.ffmpeg_threads,
        }

    def setup(self):
        if self.model is None:
            # init device and model
            self.device, self.n_gpu = init_device(self.conf, self.conf.local_rank, self.logger)
            self.model = init_model(self.conf, self.device, self.logger)

            if hasattr(self.model, 'module'):
                self.model = self.model.module

            self.model = self.model.to(self.device)
            self.model.eval()

    def forward_batch(self, batch):
        video, video_mask, video_names, start_times, end_times, old_start_times, old_end_times = batch
        video, video_mask = video.to(self.device), video_mask.to(self.device)
        visual_output = self.model.get_visual_output(video, video_mask)
        video_features = self.model.get_video_features(visual_output, video_mask)
        video_features = [f for f in video_features.cpu().numpy()]
        return video_names, start_times, end_times, old_start_times, old_end_times, video_features

    def extract(self, shots_infos_path, save_dir, start_batch, end_batch):
        self.setup()  # lazy load model

        # init test dataloader
        dataset = C2VDataset(shots_infos_path, start_batch, end_batch, **self.load_shot_args)
        dataloader = DataLoader(dataset, batch_size=self.args.batch_size, num_workers=self.args.num_workers)

        with torch.no_grad():
            for batch in dataloader:
                video_names, start_timecodes, end_timecodes, old_start_timecodes, old_end_timecodes, video_features = self.forward_batch(batch)
                for i in range(len(video_names)):
                    video_name = video_names[i]
                    start_time = start_timecodes[i]
                    end_time = end_timecodes[i]
                    old_start_time = old_start_timecodes[i]
                    old_end_time = old_end_timecodes[i]
                    video_feature = video_features[i]

                    # Save features
                    sub_save_dir = os.path.join(save_dir, "Videos_" + video_name[:3], video_name)
                    os.makedirs(sub_save_dir, exist_ok=True)

                    save_path = os.path.join(
                        sub_save_dir,
                        f"{video_name}-{old_start_time}-{old_end_time}-{start_time}-{end_time}.npy"
                    )

                    np.save(save_path, video_feature)

if __name__ == "__main__":
    args = parse_args()
    extractor = CLIP2VideoExtractor(args)
    extractor.extract(args.shots_infos_path, args.save_dir, args.start_batch, args.end_batch)