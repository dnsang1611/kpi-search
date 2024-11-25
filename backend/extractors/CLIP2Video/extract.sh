SHOTS_INFOS_PATH=post_processed_scenes.csv
SAVE_DIR="/mnt/mmlab2024nas/visedit/AIC2024/code/Features/clip2video"

# (
#     python extract_clip2video.py \
#         --shots-infos-path ${SHOTS_INFOS_PATH} \
#         --save-dir ${SAVE_DIR} \
#         --start-batch 25 \
#         --end-batch 25
# ) &
(
    python extract_clip2video.py \
        --shots-infos-path ${SHOTS_INFOS_PATH} \
        --save-dir ${SAVE_DIR} \
        --start-batch 26 \
        --end-batch 26
)
# (
#     python extract_clip2video.py \
#         --shots-infos-path ${SHOTS_INFOS_PATH} \
#         --save-dir ${SAVE_DIR} \
#         --start-batch 27 \
#         --end-batch 30
# )