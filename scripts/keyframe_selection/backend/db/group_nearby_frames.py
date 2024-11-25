import os
import numpy as np
import json

data_dir = "/mnt/mmlab2024nas/visedit/AIC2024/code/Data/Newframe"
features_dir = "/mnt/mmlab2024nas/visedit/AIC2024/code/Features/COCA"
output_dir = "./videos_groups"
threshold = 0.97

def cal_score(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

groups = []
for vid_feat_file in sorted(os.listdir(features_dir)):
    print(vid_feat_file)

    # Load video features
    vid_feat_path = os.path.join(features_dir, vid_feat_file)
    features = np.load(vid_feat_path)

    # Load frames names
    vid_name = vid_feat_file.split(".")[0]
    batch_name = "Videos_" + vid_name[:3]
    video_dir = os.path.join(data_dir, batch_name, vid_name)
    frame_names = sorted(os.listdir(video_dir))
    frame_names = [os.path.join(batch_name, vid_name, frame_name) for frame_name in frame_names]

    # Check compatibility
    assert len(frame_names) == features.shape[0]

    # Group 
    group = [{"frame": frame_names[0], "kept": False}]
    anchor_feature = features[0]
    idx = 1

    while idx < features.shape[0]:
        cur_frame = frame_names[idx]
        cur_feature = features[idx]
        score = cal_score(anchor_feature, cur_feature)

        if score >= threshold:
            group.append({"frame": cur_frame, "kept": False})
        else:
            groups.append(group)
            group = [{"frame": cur_frame, "kept": False}]
            anchor_feature = cur_feature
        
        idx += 1

    groups.append(group)

    # Save
    output_path = os.path.join(output_dir, vid_feat_file.split(".")[0] + ".json")

    # Select final frame in each group
    for group in groups:
        group[-1]["kept"] = True

    with open(output_path, "w") as wf:
        json.dump(groups, wf, indent=3)

    groups = []