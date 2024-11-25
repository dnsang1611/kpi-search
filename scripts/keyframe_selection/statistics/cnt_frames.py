import json
import os

groups_dir = "/mnt/mmlab2024nas/visedit/AIC2024/code/Script/keyframe_selection/backend/db/videos_groups"
cnt_total = 0
cnt_kept = 0
for groups_file in sorted(os.listdir(groups_dir)):
    groups_path = os.path.join(groups_dir, groups_file)
    with open(groups_path, "r") as rf:
        groups = json.load(rf)

    cnt_kept += len(groups)
    for group in groups:
        cnt_total += len(group)

print("Number of frames:", cnt_total)
print("Number of selected frames:", cnt_kept)
print("Decrease by:", cnt_total - cnt_kept)

print(len(os.listdir(groups_dir)))