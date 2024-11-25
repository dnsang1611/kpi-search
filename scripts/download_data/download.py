import wget
import pandas as pd
import os
import zipfile

excel_path = './excel_files/[Public] Dữ liệu vòng sơ tuyển 2024.xlsx'
save_dir = '/mnt/mmlabworkspace/Datasets/AIC2024'
sheet_name = 0
file_types = ['Video']
with_download = False

# Download
if with_download:
    df = pd.read_excel(excel_path, sheet_name=sheet_name)

    for i in range(len(df)):
        file_type = df.loc[i, 'Type']
        url = df.loc[i, 'Video with audio']
        fname = df.loc[i, 'Filename']

        if file_type not in file_types:
            continue

        type_save_dir = os.path.join(save_dir, f'{file_type}_a')
        os.makedirs(type_save_dir, exist_ok=True)
        save_path = os.path.join(type_save_dir, fname)

        wget.download(url, out=save_path)

        print(f"\nDownloaded {save_path}")

# Unzip
for file_type in file_types:
    type_save_dir = os.path.join(save_dir, f'{file_type}_a')
    for fname in sorted(os.listdir(type_save_dir)):
        zip_path = os.path.join(type_save_dir, fname)
        extracted_dir = os.path.join(type_save_dir, fname.split('.')[0])
        os.makedirs(extracted_dir, exist_ok=True)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extracted_dir)
    
        os.remove(zip_path)


