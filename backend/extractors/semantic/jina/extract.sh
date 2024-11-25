KEYFRAME_DIR='/mnt/mmlab2024nas/visedit/AIC2024/code/Data/Newframe'
FEAT_DIR='/mnt/mmlab2024nas/visedit/AIC2024/code/Features/JINA'

(
    python extract_jina.py --keyframe-dir ${KEYFRAME_DIR} \
                            --features-dir ${FEAT_DIR} \
                            --start-batch 24 \
                            --end-batch 25
) 