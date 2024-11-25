import os
import pandas as pd
from skimage import io
import numpy as np
import cv2

import argparse


def parse_args():
    parser = argparse.ArgumentParser(description="Color extractor args parser")

    # Add arguments to the parser
    parser.add_argument('--data-dir', type=str, help='Directory to data')
    parser.add_argument('--features-dir', type=str, help='Directory to features')
    parser.add_argument('--color-table', type=str, help='Path to color table')
    parser.add_argument('--start-batch', type=int, help='Index of start batch')
    parser.add_argument('--end-batch', type=int, help='Index of end batch')
    parser.add_argument('--visualize', action='store_true', help='Enable verbose mode')

    # Parse the arguments
    args = parser.parse_args()
    return args

class ColorExtractor:
    def __init__(self, color_table_path):
        self.COLORS = {
            'black' : [0.00, 0.00, 0.00],
            'blue'  : [0.00, 0.00, 1.00],
            'brown' : [0.50, 0.40, 0.25],
            'grey'  : [0.50, 0.50, 0.50],
            'green' : [0.00, 1.00, 0.00],
            'orange': [1.00, 0.80, 0.00],
            'pink'  : [1.00, 0.50, 1.00],
            'purple': [1.00, 0.00, 1.00],
            'red'   : [1.00, 0.00, 0.00],
            'white' : [1.00, 1.00, 1.00],
            'yellow': [1.00, 1.00, 0.00],
        }

        self.LABEL_MAP = list(self.COLORS.keys())

        self.color_map = self.read_color_table(color_table_path)

    def read_color_table(self, color_table_path):
        n_colors = len(self.COLORS)
        column_names = ['R', 'G', 'B'] + list(range(n_colors))
        color_table = pd.read_csv(color_table_path, names=column_names, index_col=['R','G','B'], sep='\s+')
        pixel2color_idx = color_table.idxmax(axis=1).values
        return pixel2color_idx

    def extract(self, data_dir, features_dir, 
                visualize=False, start_batch=-1, end_batch=100,
                n_rows=5, n_cols=5):
        for batch_folder in sorted(os.listdir(data_dir)):
            batch_id = int(batch_folder[-2:])
            
            if batch_id < start_batch or batch_id > end_batch:
                continue
            print(batch_folder)
            
            batch_dir = os.path.join(data_dir, batch_folder)
            out_batch_dir = os.path.join(features_dir, batch_folder)
            os.makedirs(out_batch_dir, exist_ok=True)

            for video_folder in sorted(os.listdir(batch_dir)):
                video_dir = os.path.join(batch_dir, video_folder)
                out_video_dir = os.path.join(out_batch_dir, video_folder)
                os.makedirs(out_video_dir, exist_ok=True)

                for image_file in sorted(os.listdir(video_dir)):
                    # Extract feature of image
                    image_path = os.path.join(video_dir, image_file)
                    feature, ohe_feature = self.extract_one_image(image_path, n_rows, n_cols)

                    # Visualize
                    if visualize:
                        save_dir = os.path.join('vis_res', video_folder)
                        os.makedirs(save_dir, exist_ok=True)
                        save_path = os.path.join(save_dir, image_file)
                        self.visualize(feature, image_path, save_path, n_rows, n_cols)

                    # Save feature
                    feature_path = os.path.join(out_video_dir, image_file.split('.')[0] + '.npy')
                    np.save(feature_path, ohe_feature)

    def extract_one_image(self, image_path, n_rows, n_cols):
        # read image
        image_np = self.load_image(image_path)

        # map whole image to color index
        idx_image = (image_np // 8).astype(np.uint16)
        idx_image *= np.array([1, 32, 1024], dtype=np.uint16).reshape((1, 1, 3))
        idx_image = idx_image.sum(axis=2)
        idx_image = self.color_map[idx_image]

        im_h = image_np.shape[0]
        im_w = image_np.shape[1]

        cell_h = im_h // n_rows
        cell_w = im_w // n_cols

        feature = []
        for r in range(n_rows):
            for c in range(n_cols):
                cell = idx_image[
                    r * cell_h: (r + 1) * cell_h,
                    c * cell_w: (c + 1) * cell_w,
                ]

                colors, cnts = np.unique(cell, return_counts=True)
                dom_color = colors[np.argmax(cnts)]
                feature.append(dom_color)

        ohe_feature = self.ohe_color(feature)

        return feature, ohe_feature

    def ohe_color(self, feature):
        ohe_feature = []
        for color in feature:
            ohe = np.zeros((len(self.COLORS)))
            ohe[color] = 1
            ohe_feature.append(ohe)
        
        return np.hstack(ohe_feature).astype(np.uint8)

    def visualize(self, feature, image_path, save_path, n_rows, n_cols):
        raw_img = cv2.imread(image_path)
        h, w, _ = raw_img.shape

        for i in range(len(feature)):
            feature[i] = self.COLORS[self.LABEL_MAP[feature[i]]]
        
        feature = np.clip(np.array(feature) * 255, 0, 255).astype(np.uint8)
        feature = feature.reshape((n_rows, n_cols, 3))
        color_img = cv2.resize(feature, (w, h), interpolation=cv2.INTER_NEAREST)
        color_img = cv2.cvtColor(color_img, cv2.COLOR_BGR2RGB)
        save_img = cv2.hconcat([raw_img, color_img])
        cv2.imwrite(save_path, save_img)

    def load_image(self, image_path):
        try:
            image_np = io.imread(image_path)
            # TODO convert to RGB if not
        except KeyboardInterrupt as e:
            raise e
        except:
            print(f'{image_path}: Error loading image')
            return None

        return image_np

if __name__ == '__main__':
    args = parse_args()

    color_extractor = ColorExtractor(args.color_table)
    color_extractor.extract(
        data_dir=args.data_dir, features_dir=args.features_dir, 
        visualize=args.visualize,
        start_batch=args.start_batch, end_batch=args.end_batch,
        n_rows=5, n_cols=5
    )