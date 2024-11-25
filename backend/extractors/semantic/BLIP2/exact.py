import numpy as np
from lavis.models import load_model_and_preprocess
from scipy.spatial.distance import cosine
import os
from natsort import natsorted
from PIL import Image

device = 'cuda'
model, vis_processors, txt_processors = load_model_and_preprocess(name="blip2_feature_extractor", model_type="pretrain", is_eval=True, device=device)
keyframes_folder = '/mnt/mmlabworkspace/Students/visedit/AIC2023/Data/Reframe'

# Set the index to start from (L11)
start_index = 1
end_index = 36

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
                    image = Image.open(image_path).convert("RGB")
                    image_processed = vis_processors["eval"](image).unsqueeze(0).to(device)
                    sample = {"image": image_processed}
                    image_emb = model.extract_features(sample, mode="image").image_embeds.mean(dim=1)
                    image_emb_np = image_emb.cpu().detach().numpy()
                    vectors.append(np.array(image_emb_np).reshape(-1))
                    print(f"Processed image {image_name} ({image_idx + 1}/{len(image_paths)})")

                # Transform the vectors list into a numpy array
                vectors = np.array(vectors)

                # Save the numpy array to a .npy file
                output_file_path = os.path.join('/mnt/mmlabworkspace/Students/visedit/AIC2024/Features/B2vecs', f'{subfolder_name}.npy')
                np.save(output_file_path, vectors)
                print(f"Saved vectors to {output_file_path}")

        print(f"Finished processing folder {folder_name} ({idx + 1}/{len(os.listdir(keyframes_folder))})")