# from meili import Meilisearch
# import json
# import os

# sel_keyframe_dir = "/mnt/mmlab2024nas/visedit/AIC2024/code/Script/keyframe_selection/backend/db/videos_groups"
# asr_dir = ""
# ocr_dir = "/mnt/mmlab2024nas/visedit/AIC2024/code/JSON/ocr/ocr_final"
# index_ocr = True
# index_asr = False

# if sel_keyframe_dir:
#     sel_frames = []
    
#     for video_file in sorted(os.listdir(sel_keyframe_dir)):
#         with open(os.path.join(sel_keyframe_dir, video_file), "r", encoding="utf-8") as rf:
#             groups = json.load(rf)
#             sel_frames.extend([group[-1]["frame"] for group in groups])

# def index_meli(modality, data_dir):
#     index = Meilisearch(modality)
#     print(index.check_health_status())
#     # ocr_index.delete()
#     print(index.check_health_status())
    
#     temp_dir = os.path.join(data_dir, "temp")
#     os.makedirs(temp_dir)

#     # If use keyframe selection
#     if sel_keyframe_dir:
#         for data_file in sorted(os.listdir(data_dir)):    
#             # Select texts for all selected keyframes
#             with open(os.path.join(data_dir, data_file), "r", encoding="utf-8") as rf:
#                 old_features = json.load(rf)
            
#             features = [
#                 feature
#                 for feature in old_features
#                 if feature["frame"] in sel_frames
#             ]
        
#             # Save file
#             save_path = os.path.join(temp_dir, "sel_" + data_file)
#             print(f"Saving file to {save_path}")
#             with open(save_path, "w", encoding="utf-8") as wf:
#                 json.dump(features, wf)

#             # Insert
#             print(f"Inserting new records ...")
#             index.insert(save_path)
#     else:
#         for data_file in sorted(os.listdir(data_dir)):
#             print(data_file)
#             print(f"Inserting new records ...")   
#             index.insert(os.path.join(data_dir, data_file))
        
#     print(index.check_health_status())

# if index_ocr:
#     index_meli("OCR", ocr_dir)

# # if index_asr:
# #     index_meli("ASR", asr_dir)


from meili import Meilisearch

ocr_index = Meilisearch('OCR')
print(ocr_index.check_health_status())
ocr_index.delete()
print(ocr_index.check_health_status())
ocr_index.insert('JSON/ocr/ocr_final/ocr_batch1.json')
ocr_index.insert('JSON/ocr/ocr_final/ocr_batch2.json')
ocr_index.insert('JSON/ocr/ocr_final/ocr_batch3.json')
print(ocr_index.check_health_status())

# asr_index = Meilisearch('ASR')
# asr_index.delete()
# print(asr_index.check_health_status())
# asr_index.insert('JSON/asr/asr_batch1_1.json')
# asr_index.insert('JSON/asr/asr_batch1_2.json')
# asr_index.insert('JSON/asr/asr_batch1_3.json')
# print(asr_index.check_health_status())
# asr_index.insert('JSON/asr/asr_batch2_1.json')
# asr_index.insert('JSON/asr/asr_batch2_2.json')
# asr_index.insert('JSON/asr/asr_batch2_3.json')
# print(asr_index.check_health_status())
# asr_index.insert('JSON/asr/asr_batch3_1.json')
# asr_index.insert('JSON/asr/asr_batch3_2.json')
# asr_index.insert('JSON/asr/asr_batch3_3.json')
# print(asr_index.check_health_status())