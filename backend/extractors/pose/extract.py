import numpy as np
import cv2
import torch
from pathlib import Path
from natsort import natsorted
import os
import matplotlib.pyplot as plt
import json
from xtcocotools.coco import COCO

try:
    from mmdet.apis import inference_detector, init_detector, show_result_pyplot
    has_mmdet = True
except (ImportError, ModuleNotFoundError):
    has_mmdet = False

from mmpose.apis import (inference_top_down_pose_model, init_pose_model,
                         process_mmdet_results, vis_pose_result)
from mmpose.datasets import DatasetInfo

import sys
sys.path.append('./MogaNet')
import models  # register_model for MogaNet

def get_pose_feat_without_norm(pose):
    '''
        Input:
            - pose: normed or non-normed pose with height and width of image
            (normed pose with h, w can lead to error in direction)
        Return: 
            - Feature vector of pose
                Calculate substraction between vectors in pose
                The term without_norm in function name means that: Don't norm substraction vector
                Care about length and direction
    '''
    num_points = len(pose) // 2
    feat_vec = []

    for i in range(1, num_points):
        pivot_x, pivot_y = pose[0], pose[1]
        current_x, current_y = pose[i * 2], pose[i * 2 + 1]

        # If keypoint is incomplete, assign -100 to sub_x, sub_y to 
        # isolate these incomplete pose
        if current_x == -1 or pivot_x == -1:
            sub_x = sub_y = -100
        else:
            sub_x = current_x - pivot_x
            sub_y = current_y - pivot_y

        feat_vec.extend([sub_x, sub_y])

        for j in range(1, i):
            prev_x, prev_y = pose[j * 2], pose[j * 2 + 1]

            sub_x = sub_y = None
            if current_x == -1 or prev_x == -1:
                sub_x = sub_y = -100
            else:
                sub_x = current_x - prev_x
                sub_y = current_y - prev_y
                
            feat_vec.extend([sub_x, sub_y])

    return np.array(feat_vec)

def get_pose_feat_with_norm(pose):
    '''
        Input:
            - pose: non-normed pose with height and width of image
            (normed pose with h, w can lead to error in direction)
        Return: 
            - Feature vector of pose
                Calculate substraction between vectors in pose then normalize them
                The term with_norm in function name means that: Norm substraction vector
                Only care about direction
    '''
    num_points = len(pose) // 2
    feat_vec = []

    for i in range(1, num_points):
        pivot_x, pivot_y = pose[0], pose[1]
        current_x, current_y = pose[i * 2], pose[i * 2 + 1]

        # If keypoint is incomplete, assign -100 to sub_x, sub_y to 
        # isolate these incomplete pose
        if current_x == -1 or pivot_x == -1:
            sub_x = sub_y = -100
        else:
            sub_x = current_x - pivot_x
            sub_y = current_y - pivot_y
            vec_len = np.sqrt(sub_x**2 + sub_y**2)
            sub_x, sub_y = sub_x / vec_len, sub_y / vec_len

        feat_vec.extend([sub_x, sub_y])

        for j in range(1, i):
            prev_x, prev_y = pose[j * 2], pose[j * 2 + 1]

            sub_x = sub_y = None
            if current_x == -1 or prev_x == -1:
                sub_x = sub_y = -100
            else:
                sub_x = current_x - prev_x
                sub_y = current_y - prev_y
                vec_len = np.sqrt(sub_x**2 + sub_y**2)
                sub_x, sub_y = sub_x / vec_len, sub_y / vec_len
                
            feat_vec.extend([sub_x, sub_y])

    return np.array(feat_vec)

class PoseFeatureExtractor:

    def make_prediction(self, in_folder: str, out_folder: str,
                        start_index: int = 0, end_index: int = None):
        # Init pipeline
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        det_config = './mmdetection/configs/faster_rcnn/faster_rcnn_r50_caffe_fpn_mstrain_1x_coco-person.py'
        det_checkpoint = './checkpoints/faster_rcnn_r50_fpn_1x_coco-person_20201216_175929-d022e227.pth'
        pose_config = './MogaNet/pose_estimation/configs/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/moganet_b_coco_384x288.py'
        pose_checkpoint = './checkpoints/moganet_b_coco_384x288.pth'
        det_cat_id = 0

        det_model = init_detector(
            det_config, det_checkpoint, device=device.lower())

        pose_model = init_pose_model(
                pose_config, pose_checkpoint, device=device.lower())

        dataset = pose_model.cfg.data['test']['type']
        dataset_info = pose_model.cfg.data['test'].get('dataset_info', None)
        if dataset_info is None:
            warnings.warn(
                'Please set `dataset_info` in the config.'
                'Check https://github.com/open-mmlab/mmpose/pull/663 for details.',
                DeprecationWarning)
        else:
            dataset_info = DatasetInfo(dataset_info)

        # Main process
        base_path = Path(in_folder)
        output_base_path = Path(out_folder)

        sorted_folders = natsorted(base_path.iterdir())
        if end_index is None:
            end_index = len(sorted_folders)

        for idx, l_folder in enumerate(sorted_folders):
            if idx < start_index or idx >= end_index:
                continue  # Skip folders outside the specified range

            if l_folder.is_dir():
                for v_folder in natsorted(l_folder.iterdir()):
                    if v_folder.is_dir():
                        relative_path = v_folder.relative_to(Path(base_path))
                        det_output_path = output_base_path.joinpath(relative_path.parent, relative_path.stem, 'det')
                        pose_output_path = output_base_path.joinpath(relative_path.parent, relative_path.stem, 'pose')
                        det_output_path.mkdir(parents=True, exist_ok=True)
                        pose_output_path.mkdir(parents=True, exist_ok=True)

                        for img_file in natsorted(v_folder.glob("*.jpg")):
                            # Inference
                            mmdet_results = inference_detector(det_model, str(img_file))
                            person_results = process_mmdet_results(mmdet_results, det_cat_id) # Get bboxes of people

                            try:
                                pose_results, returned_outputs = inference_top_down_pose_model(
                                    pose_model,
                                    str(img_file),
                                    person_results,
                                    bbox_thr=0,
                                    format='xyxy',
                                    dataset=dataset,
                                    dataset_info=dataset_info,
                                    return_heatmap=False,
                                    outputs=None)
                            except:
                                print(f'{img_file} not found')
                            
                            if not pose_results:
                                continue

                            bbox_file = det_output_path.joinpath(img_file.stem).with_suffix('.npy')
                            pose_file = pose_output_path.joinpath(img_file.stem).with_suffix('.npy')

                            bboxes = np.vstack([pose_result['bbox'] for pose_result in pose_results])
                            poses = np.array([pose_result['keypoints'] for pose_result in pose_results])

                            assert bboxes.shape[0] == poses.shape[0], 'Num bboxes != Num poses'

                            np.save(bbox_file, bboxes)
                            np.save(pose_file, poses)
    
    def extract_feature(self, img_folder: str, pose_res_folder: str, out_folder: str,
                        get_pose_feature, drop_pose=False,
                        start_index=0, end_index=None, 
                        vis_folder='vis_res', visualize=False, 
                        bbox_thr=0.3, kpt_thr=0.3):
        '''
            Input:
                - img_folder: Directory of raw image folder
                - pose_res_folder: Directory of prediction from pose estimator
                - out_folder: Directory of feature (output) folder
                - get_pose_feature: This function receive a pose and return feature vector.
                    For more detail see function get_pose_feature_without_norm
                - drop_pose: Whether remove an incomplete pose or not. An incomplete pose is
                    a pose containing at least 1 keypoint that have kpt_conf < kpt_thrs. If False,
                    these keypoints will be set to (-100, -100) for further process.
                - start_index: Start index
                - end_index: End index
                - vis_folder: Directory of visualization
                - visualized: Whether to visualize or not
                - bbox_thr, kpt_thr

            Return:
                None
        '''
        pose_res_base_path = Path(pose_res_folder)
        img_base_path = Path(img_folder)
        output_base_path = Path(out_folder)

        sorted_folders = natsorted(pose_res_base_path.iterdir())
        if end_index is None:
            end_index = len(sorted_folders)

        for idx, l_folder in enumerate(sorted_folders):
            if idx < start_index or idx >= end_index:
                continue  # Skip folders outside the specified range

            if l_folder.is_dir():
                for v_folder in natsorted(l_folder.iterdir()):
                    if v_folder.is_dir():
                        relative_path = v_folder.relative_to(Path(pose_res_base_path))
                        img_path = img_base_path.joinpath(relative_path.parent, relative_path.stem)
                        output_path = output_base_path.joinpath(relative_path.parent, relative_path.stem)
                        output_path.mkdir(parents=True, exist_ok=True)

                        for pose_file in natsorted(os.listdir(v_folder.joinpath('pose'))):
                            # Load prediction from pose estimator
                            pose_path = v_folder.joinpath('pose', pose_file)
                            bbox_path = v_folder.joinpath('det', pose_file)
                            poses = np.load(pose_path)
                            bboxes = np.load(bbox_path)
                            
                            # Filter kpts, poses
                            img_file = img_path.joinpath(pose_file.split('.')[0]).with_suffix('.jpg')
                            fil_poses = self.filter_poses(poses, bboxes, bbox_thr, kpt_thr, drop_pose)

                            # Visualize
                            if visualize:
                                vis_path = Path(vis_folder).joinpath(relative_path.parent, relative_path.stem)
                                vis_path.mkdir(parents=True, exist_ok=True)
                                vis_file = vis_path.joinpath(img_file.stem).with_suffix('.jpg')
                                self.visualize_poses(fil_poses, img_file, vis_file)
                                
                            if len(fil_poses) == 0:
                                print(f"Skipping image due to no poses.")
                                continue

                            # Get image feature from poses
                            # img_height, img_width = cv2.imread(img_file).shape[:2]
                            # norm_poses = self.normalize_poses(fil_poses, img_width, img_height)
                            
                            fil_poses = np.array(fil_poses).reshape(fil_poses.shape[0], -1)
                            img_feat = self.get_img_feat(fil_poses, get_pose_feature)

                            # Save results
                            out_file = output_path.joinpath(pose_file.split('.')[0]).with_suffix('.npy')
                            np.save(out_file, img_feat)

    def filter_poses(self, poses, bboxes, bbox_thr, kpt_thr, drop_pose):
        # Set up important keypoints
        indices = [0, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
        # expected_length = len(indices) * 2
        res_poses = []

        for i in range(bboxes.shape[0]):
            bbox = bboxes[i]
            pose = poses[i]
            
            if bbox[-1] < bbox_thr:
                print(f"Skipping person due to low bbox confidence.")
                continue
            
            # Select important keypoints
            filtered_pose = pose[indices]
            if drop_pose and np.sum(filtered_pose[:,-1] < kpt_thr):
                print(f"Skipping person due to incomplete keypoints.")
                continue
            else:
                condition = filtered_pose[:, -1] < kpt_thr
                filtered_pose[condition] = np.array([-1, -1, 0])
            filtered_pose = filtered_pose[:, :2]
            
            # Add midpoint to pose
            midpoint = np.array([round((pose[5][0] + pose[6][0]) / 2, 3), round((pose[5][1] + pose[6][1]) / 2, 3)]).reshape(1, -1)
            filtered_pose = np.concatenate((filtered_pose, midpoint), axis=0)
            res_poses.append(filtered_pose)
        
        return np.array(res_poses)

    def normalize_poses(self, poses, img_width, img_height):
        norm_poses = []
        for pose in poses:
            norm_pose = [coord / img_width if i % 2 == 0 else coord / img_height for keypoint in pose for i, coord in enumerate(keypoint[:2])]
            norm_poses.append(norm_pose)

        return np.array(norm_poses)

    def get_img_feat(self, poses, get_pose_feature):
        img_feat = []
        for pose in poses:
            pose_feat = get_pose_feature(pose)
            img_feat.append(pose_feat)

        return np.vstack(img_feat)
    
    def visualize_poses(self, poses, input_file, output_file):
        image = cv2.imread(input_file)
        connections = [
            (1, 2), (1, 3), (2, 4), (3, 5), (4, 6),
            (1, 7), (2, 8), (7, 8), (7, 9), (8, 10), (9, 11), (10, 12),
            (0, 13) 
        ]

        for pose in poses:
            for start_idx, end_idx in connections:
                if start_idx < len(pose) and end_idx < len(pose):
                    start_point = (int(pose[start_idx][0]), int(pose[start_idx][1]))
                    end_point = (int(pose[end_idx][0]), int(pose[end_idx][1]))
                    cv2.line(image, start_point, end_point, (0, 255, 0), 2)  # Green line with thickness 2

            for x, y in pose:
                x_abs = int(x)
                y_abs = int(y)
                cv2.circle(image, (x_abs, y_abs), 5, (255, 0, 0), -1)  # Blue circle with radius 5

        cv2.imwrite(output_file, image)
        print(f"Visualized image saved to {output_file}")

if __name__ == '__main__':
    img_path = "/mnt/mmlabworkspace/Students/visedit/AIC2024/Data/Newframe"
    pose_res_path = '/mnt/mmlabworkspace/Students/visedit/AIC2024/Backend/POSE/pose_results'
    feature_path = '/mnt/mmlabworkspace/Students/visedit/AIC2024/Features/POSE'
    vis_folder = 'vis_res'

    extractor = PoseFeatureExtractor()
    extractor.make_prediction(img_path, pose_res_path, start_index=0, end_index=None)
    extractor.extract_feature(img_path, pose_res_path, feature_path, 
                              get_pose_feat_with_norm, drop_pose=False, 
                              start_index=0, end_index=None,
                              vis_folder=vis_folder, visualize=False, 
                              bbox_thr=0.3, kpt_thr=0.3)