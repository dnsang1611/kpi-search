import numpy as np
# from lavis.models import load_model_and_preprocess
from scipy.spatial.distance import cosine
import os
from natsort import natsorted
from PIL import Image
import argparse

from transformers import AutoTokenizer, AutoModel, AutoProcessor

def parse_args():
    parser = argparse.ArgumentParser(description="Color extractor args parser")

    # Add arguments to the parser
    parser.add_argument('--keyframe-dir', type=str, help='Directory to data')
    parser.add_argument('--features-dir', type=str, help='Directory to features')
    parser.add_argument('--start-batch', type=int, help='Index of start batch')
    parser.add_argument('--end-batch', type=int, help='Index of end batch')

    # Parse the arguments
    args = parser.parse_args()
    return args

model = AutoModel.from_pretrained('jinaai/jina-clip-v1', trust_remote_code=True).to('cuda')


args = parse_args()
device = 'cuda'
keyframes_folder = '/mnt/mmlab2024nas/visedit/AIC2024/code/Data/Newframe'
features_dir = '/mnt/mmlab2024nas/visedit/AIC2024/code/Features/JINA'
start_index = args.start_batch
end_index = args.end_batch

# Loop through each Lxx folder starting from L11
for idx, folder_name in enumerate(natsorted(os.listdir(keyframes_folder))):
    if idx < start_index - 1:
        continue  # Skip folders until L11
    if idx > end_index:
        break

    folder_path = os.path.join(keyframes_folder, folder_name)
    if os.path.isdir(folder_path):
        print(f"Processing folder {folder_name} ({idx + 1}/{len(os.listdir(keyframes_folder))})")

        # Loop through each Lxx_Vxxx subfolder
        for subfolder_name in natsorted(os.listdir(folder_path)):
            subfolder_path = os.path.join(folder_path, subfolder_name)
            if os.path.isdir(subfolder_path):
                vectors = []
                print(f"Processing subfolder {subfolder_name}")

                # Loop through each .jpg image file
                image_paths = natsorted([f for f in os.listdir(subfolder_path) if f.endswith('.jpg')])
                for image_idx, image_name in enumerate(image_paths):
                    image_path = os.path.join(subfolder_path, image_name)
                    image = Image.open(image_path)
                    # inputs = feature_extractor(images=[image], return_tensors="pt").to('cuda')
                    image_embedding = model.encode_image([image])
                    # print(image_embedding.shape)
                    image_emb_np = np.array(image_embedding).reshape(-1)
                    # print(image_emb_np.shape)
                    vectors.append(image_emb_np)
                    print(f"Processed image {image_name} ({image_idx + 1}/{len(image_paths)})")

                # Transform the vectors list into a numpy array
                vectors = np.array(vectors)

                # Save the numpy array to a .npy file
                output_file_path = os.path.join(features_dir, f'{subfolder_name}.npy')
                np.save(output_file_path, vectors)
                print(f"Saved vectors to {output_file_path}")

        print(f"Finished processing folder {folder_name} ({idx + 1}/{len(os.listdir(keyframes_folder))})")
