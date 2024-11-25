KEYFRAME_DIR='/mnt/mmlab2024nas/visedit/AIC2024/code/Data/Newframe'
FEAT_DIR='/mnt/mmlab2024nas/visedit/AIC2024/code/Features/COCA'

(
    python extract_coca.py --keyframe-dir ${KEYFRAME_DIR} \
                            --features-dir ${FEAT_DIR} \
                            --start-batch 27 \
                            --end-batch 27
) &
(
    python extract_coca.py --keyframe-dir ${KEYFRAME_DIR} \
                            --features-dir ${FEAT_DIR} \
                            --start-batch 29 \
                            --end-batch 29
)