KEYFRAME_DIR='/mnt/mmlab2024nas/visedit/AIC2024/code/Data/Newframe'
FEAT_DIR='/mnt/mmlab2024nas/visedit/AIC2024/code/Features/ALIGN'

(
    python extract_align.py --keyframe-dir ${KEYFRAME_DIR} \
                            --features-dir ${FEAT_DIR} \
                            --start-batch 26 \
                            --end-batch 25
)