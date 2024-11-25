# import os
# import pandas as pd
# import json

# # Đường dẫn tới file đầu vào và đầu ra
# txt_file_path = '/mnt/mmlab2024nas/visedit/AIC2024/code/Backend/extractors/ASR/FINAL_RESULT/Batch1.txt'
# csv_folder_path = '/mnt/mmlab2024nas/visedit/AIC2024/code/Data/Mapframe'
# frame_folder_path = '/mnt/mmlab2024nas/visedit/AIC2024/code/Data/Newframe'
# output_json_path = '/mnt/mmlab2024nas/visedit/AIC2024/code/JSON/asr/asr_batch1.json'

# # Khởi tạo list chứa các dict cho JSON output
# json_list = []

# # Khởi tạo cache để lưu các frames đã xét
# frames_cache = {}

# # Khởi tạo danh sách các video cần xử lý
# videos_to_process = set()

# # Duyệt qua toàn bộ file txt để thu thập các video cần xử lý
# with open(txt_file_path, 'r') as txt_file:
#     lines = txt_file.readlines()

#     for line in lines:
#         # Tách đường dẫn
#         wav_path, transcription = line.strip().split('\t')
        
#         # Lấy tên video và tên file .wav
#         path_parts = wav_path.split('/')
#         video_name = path_parts[-2]
#         video_batch, _ = video_name.split('_')
        
#         # Tạo đường dẫn đầy đủ của thư mục frames
#         frame_folder_full_path = os.path.join(frame_folder_path, f"Videos_{video_batch}", video_name)
        
#         # Thêm video cần xử lý vào danh sách nếu chưa có
#         if frame_folder_full_path not in videos_to_process:
#             videos_to_process.add(frame_folder_full_path)

# # Duyệt qua các video trong danh sách và cache lại frames
# for frame_folder_full_path in videos_to_process:
#     if os.path.exists(frame_folder_full_path):
#         frames = os.listdir(frame_folder_full_path)
#         frame_numbers = [int(f.split('.')[0]) for f in frames if f.endswith('.jpg')]
#         frames_cache[frame_folder_full_path] = frame_numbers
#     else:
#         print(f"--- Thư mục không tồn tại: {frame_folder_full_path} ---")

# # Tiến hành xử lý các dòng trong file txt
# for idx, line in enumerate(lines):
#     # Tách đường dẫn và transcription
#     wav_path, transcription = line.strip().split('\t')
    
#     # Lấy tên video và tên file .wav
#     path_parts = wav_path.split('/')
#     video_name = path_parts[-2]
#     video_batch, _ = video_name.split('_')
#     wav_name = path_parts[-1].replace('.wav', '')
    
#     # Tách frame_start và frame_end từ tên file .wav
#     frame_start_num, frame_end_num = wav_name.split('_')
    
#     # Tìm file CSV tương ứng
#     csv_file_path = os.path.join(csv_folder_path, f"{video_name}.csv")
    
#     if not os.path.exists(csv_file_path):
#         print(f"File CSV không tồn tại: {csv_file_path}")
#         continue  # Nếu file CSV không tồn tại, bỏ qua

#     # Đọc file CSV với pandas
#     df = pd.read_csv(csv_file_path)

#     # Truy xuất frame_idx tương ứng với frame_start và frame_end
#     frame_start = df.loc[int(frame_start_num)-1, 'frame_idx']
#     frame_end = df.loc[int(frame_end_num)-1, 'frame_idx']

#     # Tạo đường dẫn đầy đủ của thư mục frames
#     frame_folder_full_path = os.path.join(frame_folder_path, f"Videos_{video_batch}", video_name)

#     # Lấy frame_numbers từ cache
#     frame_numbers = frames_cache.get(frame_folder_full_path, [])

#     # Tìm chặn trên bé nhất của frame_start (số lớn hơn hoặc bằng frame_start)
#     upper_bound = min([f for f in frame_numbers if f >= frame_start], default=None)

#     # Tìm chặn dưới lớn nhất của frame_end (số nhỏ hơn hoặc bằng frame_end)
#     lower_bound = max([f for f in frame_numbers if f <= frame_end], default=None)

#     if upper_bound is None or lower_bound is None:
#         print(f"--- Không tìm thấy frame thích hợp cho {wav_path} ---")
#         continue

#     # Định dạng frame_start và frame_end theo yêu cầu
#     formatted_frame_start = f"Videos_{video_batch}/{video_name}/{str(upper_bound).zfill(6)}.jpg"
#     formatted_frame_end = f"Videos_{video_batch}/{video_name}/{str(lower_bound).zfill(6)}.jpg"
    
#     # Thêm vào json_list
#     json_list.append({
#         "id": idx + 1,  # id bắt đầu từ 1
#         "frame_start": formatted_frame_start,
#         "frame_end": formatted_frame_end,
#         "text": transcription
#     })
#     print(f"Đã add {wav_path}")

# # Lưu json_list vào file JSON
# with open(output_json_path, 'w', encoding='utf-8') as json_file:
#     json.dump(json_list, json_file, ensure_ascii=False, indent=4)

# print(f"Đã tạo file JSON: {output_json_path}")


import os
import pandas as pd
import json

# Đường dẫn tới file đầu vào và đầu ra
txt_file_path = '/mnt/mmlab2024nas/visedit/AIC2024/code/Backend/extractors/ASR/FINAL_RESULT/Batch1.txt'
csv_folder_path = '/mnt/mmlab2024nas/visedit/AIC2024/code/Data/Mapframe'
frame_folder_path = '/mnt/mmlab2024nas/visedit/AIC2024/code/Data/Newframe'
output_json_path = '/mnt/mmlab2024nas/visedit/AIC2024/code/JSON/asr/asr_batch1.json'

# Khởi tạo list chứa các dict cho JSON output
json_list = []

# Khởi tạo cache để lưu các frames đã xét
frames_cache = {}

# Khởi tạo cache để lưu các DataFrame đã đọc
csv_cache = {}

# Khởi tạo danh sách các video cần xử lý
videos_to_process = set()

# Duyệt qua toàn bộ file txt để thu thập các video cần xử lý
with open(txt_file_path, 'r') as txt_file:
    lines = txt_file.readlines()

    for line in lines:
        # Tách đường dẫn và transcription
        parts = line.strip().split('\t')
        if len(parts) != 2:
            print(f"--- Dòng không hợp lệ (bỏ qua): {line.strip()} ---")
            continue
        wav_path, transcription = parts
        
        # Lấy tên video và tên file .wav
        path_parts = wav_path.split('/')
        if len(path_parts) < 2:
            print(f"--- Đường dẫn không hợp lệ (bỏ qua): {wav_path} ---")
            continue
        video_name = path_parts[-2]
        try:
            video_batch, _ = video_name.split('_')
        except ValueError:
            print(f"--- Tên video không hợp lệ (bỏ qua): {video_name} ---")
            continue
        
        # Tạo đường dẫn đầy đủ của thư mục frames
        frame_folder_full_path = os.path.join(frame_folder_path, f"Videos_{video_batch}", video_name)
        
        # Thêm video cần xử lý vào danh sách nếu chưa có
        if frame_folder_full_path not in videos_to_process:
            videos_to_process.add(frame_folder_full_path)

# Duyệt qua các video trong danh sách và cache lại frames
for frame_folder_full_path in videos_to_process:
    if os.path.exists(frame_folder_full_path):
        frames = os.listdir(frame_folder_full_path)
        frame_numbers = [int(f.split('.')[0]) for f in frames if f.endswith('.jpg') and f.split('.')[0].isdigit()]
        frames_cache[frame_folder_full_path] = sorted(frame_numbers)
    else:
        print(f"--- Thư mục không tồn tại: {frame_folder_full_path} ---")

# Tiến hành xử lý các dòng trong file txt
for idx, line in enumerate(lines):
    # Tách đường dẫn và transcription
    parts = line.strip().split('\t')
    if len(parts) != 2:
        print(f"--- Dòng không hợp lệ (bỏ qua): {line.strip()} ---")
        continue
    wav_path, transcription = parts
    
    # Lấy tên video và tên file .wav
    path_parts = wav_path.split('/')
    if len(path_parts) < 2:
        print(f"--- Đường dẫn không hợp lệ (bỏ qua): {wav_path} ---")
        continue
    video_name = path_parts[-2]
    try:
        video_batch, _ = video_name.split('_')
    except ValueError:
        print(f"--- Tên video không hợp lệ (bỏ qua): {video_name} ---")
        continue
    wav_name = path_parts[-1].replace('.wav', '')
    
    # Tách frame_start và frame_end từ tên file .wav
    if '_' not in wav_name:
        print(f"--- Tên file .wav không hợp lệ (bỏ qua): {wav_path} ---")
        continue
    frame_parts = wav_name.split('_')
    if len(frame_parts) != 2:
        print(f"--- Tên file .wav không hợp lệ (bỏ qua): {wav_path} ---")
        continue
    frame_start_num, frame_end_num = frame_parts
    if not (frame_start_num.isdigit() and frame_end_num.isdigit()):
        print(f"--- Số frame không hợp lệ (bỏ qua): {wav_path} ---")
        continue
    
    # Chuyển đổi frame numbers sang integers
    frame_start_num = int(frame_start_num)
    frame_end_num = int(frame_end_num)
    
    # Tìm file CSV tương ứng
    csv_file_path = os.path.join(csv_folder_path, f"{video_name}.csv")
    
    if not os.path.exists(csv_file_path):
        print(f"--- File CSV không tồn tại (bỏ qua): {csv_file_path} ---")
        continue  # Nếu file CSV không tồn tại, bỏ qua
    
    # Đọc file CSV với pandas, sử dụng cache nếu đã đọc trước đó
    if csv_file_path in csv_cache:
        df = csv_cache[csv_file_path]
    else:
        try:
            df = pd.read_csv(csv_file_path)
            csv_cache[csv_file_path] = df
        except Exception as e:
            print(f"--- Lỗi khi đọc CSV {csv_file_path} (bỏ qua): {e} ---")
            continue
    
    # Kiểm tra số lượng hàng trong DataFrame
    num_rows = len(df)
    if (frame_start_num - 1) >= num_rows or (frame_end_num - 1) >= num_rows:
        print(f"--- frame_start_num hoặc frame_end_num vượt quá số hàng trong CSV cho {wav_path} ---")
        continue
    
    # Truy xuất frame_idx tương ứng với frame_start và frame_end sử dụng iloc
    try:
        frame_start = df.iloc[frame_start_num - 1]['frame_idx']
        frame_end = df.iloc[frame_end_num - 1]['frame_idx']
    except IndexError as ie:
        print(f"--- Lỗi truy cập DataFrame cho {wav_path}: {ie} ---")
        continue
    except KeyError as ke:
        print(f"--- Cột 'frame_idx' không tồn tại trong CSV {csv_file_path} ---")
        continue
    
    # Tạo đường dẫn đầy đủ của thư mục frames
    frame_folder_full_path = os.path.join(frame_folder_path, f"Videos_{video_batch}", video_name)
    
    # Lấy frame_numbers từ cache
    frame_numbers = frames_cache.get(frame_folder_full_path, [])
    
    if not frame_numbers:
        print(f"--- Không có frames trong cache cho {frame_folder_full_path} (bỏ qua): {wav_path} ---")
        continue
    
    # Tìm chặn trên bé nhất của frame_start (số lớn hơn hoặc bằng frame_start)
    upper_bounds = [f for f in frame_numbers if f >= frame_start]
    upper_bound = min(upper_bounds) if upper_bounds else None
    
    # Tìm chặn dưới lớn nhất của frame_end (số nhỏ hơn hoặc bằng frame_end)
    lower_bounds = [f for f in frame_numbers if f <= frame_end]
    lower_bound = max(lower_bounds) if lower_bounds else None
    
    if upper_bound is None or lower_bound is None:
        print(f"--- Không tìm thấy frame thích hợp cho {wav_path} ---")
        continue
    
    # Định dạng frame_start và frame_end theo yêu cầu
    formatted_frame_start = f"Videos_{video_batch}/{video_name}/{str(upper_bound).zfill(6)}.jpg"
    formatted_frame_end = f"Videos_{video_batch}/{video_name}/{str(lower_bound).zfill(6)}.jpg"
    
    # Thêm vào json_list
    json_list.append({
        "id": idx + 1,  # id bắt đầu từ 1
        "frame_start": formatted_frame_start,
        "frame_end": formatted_frame_end,
        "text": transcription
    })
    print(f"Đã add {wav_path}")

# Lưu json_list vào file JSON
try:
    with open(output_json_path, 'w', encoding='utf-8') as json_file:
        json.dump(json_list, json_file, ensure_ascii=False, indent=4)
    print(f"Đã tạo file JSON: {output_json_path}")
except Exception as e:
    print(f"--- Lỗi khi lưu JSON: {e} ---")