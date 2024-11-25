from transformers import AutoProcessor, AutoModelForZeroShotObjectDetection
import torch
from PIL import Image
import os
import json
from tqdm import tqdm
from natsort import natsorted
import random
import cv2
import numpy as np
from pathlib import Path
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Color extractor args parser")

    # Add arguments to the parser
    parser.add_argument('--keyframe-dir', type=str, help='Directory to data')
    parser.add_argument('--sel-keyframe-dir', type=str, help="Directory to sel keyframes")
    parser.add_argument('--json-path', type=str, help='Directory to features')
    parser.add_argument('--cat-path', type=str, help="Path to category file")
    parser.add_argument('--start-batch', type=int, help='Index of start batch')
    parser.add_argument('--end-batch', type=int, help='Index of end batch')
    parser.add_argument('--batch-size', type=int, default=32, help='Batch size of recognition')

    # Parse the arguments
    args = parser.parse_args()
    return args

args = parse_args()
image_folder = args.keyframe_dir
json_output_path = args.json_path
category_path = args.cat_path
start_batch = args.start_batch
end_batch = args.end_batch
batch_size = args.batch_size
save_json_per = 10

# Model
model_id = "IDEA-Research/grounding-dino-base"
device = "cuda" if torch.cuda.is_available() else "cpu"

processor = AutoProcessor.from_pretrained(model_id)
model = AutoModelForZeroShotObjectDetection.from_pretrained(model_id).to(device)

# Utils
COLORS = [[0.000, 0.447, 0.741], [0.850, 0.325, 0.098], [0.929, 0.694, 0.125],
          [0.494, 0.184, 0.556], [0.466, 0.674, 0.188], [0.301, 0.745, 0.933]]

# Hàm chuyển đổi Tensor sang list (nếu cần)
def tensor_to_list(tensor):
    if isinstance(tensor, torch.Tensor):
        return tensor.tolist()
    return tensor

# Hàm lưu dữ liệu vào file JSON
def save_results_to_json(json_output_path, data):
    if os.path.exists(json_output_path):
        with open(json_output_path, 'r') as f:
            existing_data = json.load(f)
        existing_data.update(data)
    else:
        existing_data = data

    with open(json_output_path, 'w') as f:
        json.dump(existing_data, f, indent=4)

def obj_detect_batch(image_paths, processor, model, label_batches, visualize=False, vis_res='vis_res'):
    images = [Image.open(image_path).convert("RGB") for image_path in image_paths]  # Resize images
    
    if visualize:
        vis_images = []
        for image in images:
            vis_image = np.array(image, dtype=np.uint8)[:, :, ::-1]
            vis_image = cv2.cvtColor(vis_image, cv2.COLOR_RGB2BGR)
            vis_images.append(vis_image)

    all_results = [{} for i in range(len(images))]

    for idx, label_batch in enumerate(label_batches):
        inputs = processor(images=images, text=[label_batch for _ in images], return_tensors="pt").to(device)
        
        outputs = model(**inputs)        
        
        results = processor.post_process_grounded_object_detection(
            outputs,
            inputs.input_ids,
            box_threshold=0.3,
            text_threshold=0.3,
            target_sizes=[image.size[::-1] for image in images]
        )

        for i in range(len(images)):
            image_width, image_height = images[i].size
            result = results[i]
            detections_dict = all_results[i]
            
            for box, label in zip(result['boxes'], result['labels']):
                # Convert box from cxcywh to xyxy
                x_tl, y_tl, x_br, y_br = box.tolist()
                w = x_br - x_tl
                h = y_br - y_tl

                # Visualize
                if visualize:
                    vis_image = vis_images[i]

                    # Draw boxes
                    color = np.array(random.randint(0, len(COLORS) - 1)) * 100
                    thickness = 2
                    cv2.rectangle(vis_image, (int(x_tl), int(y_tl)), (int(x_br), int(y_br)), (255, 0, 0), thickness)

                    # Put label
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    font_scale = 1
                    color = (255, 255, 255)
                    cv2.putText(vis_image, label, (int(x_tl), int(y_tl)), font, font_scale, color, thickness)

                # Normalize bounding box
                normalized_box = [
                    round(x_tl / image_width, 4),
                    round(y_tl / image_height, 4),
                    round(w / image_width, 4),
                    round(h / image_height, 4)
                ]

                if label not in detections_dict:
                    detections_dict[label] = []

                detections_dict[label].append(normalized_box)

    if visualize:
        for i in range(len(vis_images)):
            vis_image = vis_images[i]
            rel_path = os.path.relpath(image_paths[i], image_folder)
            vis_frame_path = os.path.join(vis_res, rel_path)
            video_dir = os.path.dirname(vis_frame_path)
            os.makedirs(video_dir, exist_ok=True)
            cv2.imwrite(vis_frame_path, vis_image)

    return all_results

def to_batches(iterable, batch_size):
    for i in range(0, len(iterable), batch_size):
        yield iterable[i:i + batch_size]

def get_label_batches(category_path, batch_size=80):
    with open(category_path, 'r') as rf:
        categories = json.load(rf)

    categories = list(categories.values())
    return [' . '.join(categories[i: i + batch_size]) for i in range(0, len(categories), batch_size)]


label_batches = get_label_batches(category_path, 40)
print("# of label batches:", len(label_batches))
print(label_batches)

# Load ckpt inference
if os.path.exists(json_output_path):
    with open(json_output_path, "r") as rf:
        ckpt = json.load(rf)
        all_results = ckpt.copy()
else:
    all_results = {}
    ckpt = {}

# Main process
for video_json_file in sorted(os.listdir(args.sel_keyframe_dir)):
    # Select keyframes
    with open(os.path.join(args.sel_keyframe_dir, video_json_file), "r") as rf:
        groups = json.load(rf)
        image_names = [group[-1]["frame"] for group in groups]

    # Filter out processed frames
    image_paths = []
    for image_name in image_names:
        batch_id = int(image_name[8:10])

        if (start_batch > batch_id or batch_id > end_batch):
            continue

        if (image_name not in ckpt):
            image_paths.append(os.path.join(args.keyframe_dir, image_name))
        else:
            print(f"{image_name} found in ckpt. Skip ...")
    
    print(video_json_file)
    
    # Inference
    for batch_idx, batch in enumerate(tqdm(list(to_batches(image_paths, batch_size)), desc=f"Processing {start_batch} - {end_batch} ({video_json_file})", leave=False)):
        with torch.no_grad():
            batch_results = {}
            results_batch = obj_detect_batch(batch, processor, model, label_batches, visualize=False)
            for image_path, results in zip(batch, results_batch):
                image_name = os.path.relpath(image_path, image_folder)
                # Chuyển đổi tất cả các giá trị Tensor thành list để có thể serialize sang JSON
                batch_results[image_name] = {k: [tensor_to_list(v) for v in val] if isinstance(val, list) else tensor_to_list(val) for k, val in results.items()}

            # Sau mỗi save_json_per batch thì lưu kết quả vào file JSON
            if (batch_idx + 1) % save_json_per == 0:
                save_results_to_json(json_output_path, all_results)

            # Thêm kết quả của batch này vào `all_results`
            all_results.update(batch_results)

            del results_batch
            torch.cuda.empty_cache()

# Lưu kết quả cuối cùng
save_results_to_json(json_output_path, all_results)
