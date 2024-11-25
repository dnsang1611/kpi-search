KEYFRAME_DIR=/mnt/mmlab2024nas/visedit/AIC2024/code/Data/Newframe
SEL_KEYFRAME_DIR=/mnt/mmlab2024nas/visedit/AIC2024/code/Script/keyframe_selection/backend/db/videos_groups
JSON_DIR=/mnt/mmlab2024nas/visedit/AIC2024/code/JSON/obj
CAT_PATH=categories/coco_categories.json

# ( # 202
#     CUDA_VISIBLE_DEVICES=0 python extract_object.py \
#                 --keyframe-dir ${KEYFRAME_DIR} \
#                 --sel-keyframe-dir ${SEL_KEYFRAME_DIR} \
#                 --json-path ${JSON_DIR}/batch_1-2_1-18.json \
#                 --cat-path ${CAT_PATH} \
#                 --start-batch 1 \
#                 --end-batch 18 \
#                 --batch-size 8
# ) 
( # 245
    CUDA_VISIBLE_DEVICES=2 python extract_object.py \
                --keyframe-dir ${KEYFRAME_DIR} \
                --sel-keyframe-dir ${SEL_KEYFRAME_DIR} \
                --json-path ${JSON_DIR}/batch_2_19-24.json \
                --cat-path ${CAT_PATH} \
                --start-batch 19 \
                --end-batch 24 \
                --batch-size 4
) #&
# ( # 245
#     CUDA_VISIBLE_DEVICES=0 python extract_object.py \
#                 --keyframe-dir ${KEYFRAME_DIR} \
#                 --sel-keyframe-dir ${SEL_KEYFRAME_DIR} \
#                 --json-path ${JSON_DIR}/batch_3_25-30.json \
#                 --cat-path ${CAT_PATH} \
#                 --start-batch 25 \
#                 --end-batch 30 \
#                 --batch-size 10
# )