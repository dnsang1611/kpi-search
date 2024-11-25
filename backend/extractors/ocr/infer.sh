KEYFRAME_DIR=/mnt/mmlab2024nas/visedit/AIC2024/code/Data/Newframe
JSON_DIR=/mnt/mmlab2024nas/visedit/AIC2024/code/JSON/ocr/ocr_batch3

# Note: done 30

# (
#     CUDA_VISIBLE_DEVICES=0 python3.8 infer.py \
#                 --keyframe-dir ${KEYFRAME_DIR} \
#                 --json-path ${JSON_DIR}/rerun_videos.json \
#                 --start-batch 1 \
#                 --end-batch 30 \
#                 --det-batch-size 4
# ) 

(
    CUDA_VISIBLE_DEVICES=1 python3.8 infer.py \
                --keyframe-dir ${KEYFRAME_DIR} \
                --json-path ${JSON_DIR}/ocr_batch3_26-26.json \
                --start-batch 26 \
                --end-batch 26 \
                --det-batch-size 3
)