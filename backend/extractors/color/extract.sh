DATA_DIR=/mnt/mmlab2024nas/visedit/AIC2024/code/Data/Newframe
FEATURES_DIR=/mnt/mmlab2024nas/visedit/AIC2024/code/Features/color_visione
COLOR_TABLE_PATH=tables/w2c.txt

(
    python extract.py --data-dir ${DATA_DIR} \
                    --features-dir ${FEATURES_DIR} \
                    --color-table ${COLOR_TABLE_PATH} \
                    --start-batch 6 \
                    --end-batch 6
) &
(
    python extract.py --data-dir ${DATA_DIR} \
                    --features-dir ${FEATURES_DIR} \
                    --color-table ${COLOR_TABLE_PATH} \
                    --start-batch 9 \
                    --end-batch 9
) &
(
    python extract.py --data-dir ${DATA_DIR} \
                    --features-dir ${FEATURES_DIR} \
                    --color-table ${COLOR_TABLE_PATH} \
                    --start-batch 24 \
                    --end-batch 24
) &
(
    python extract.py --data-dir ${DATA_DIR} \
                    --features-dir ${FEATURES_DIR} \
                    --color-table ${COLOR_TABLE_PATH} \
                    --start-batch 25 \
                    --end-batch 25
)