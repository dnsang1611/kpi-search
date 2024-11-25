# CUDA_VISIBLE_DEVICES=2
# CONFIG_FILE=configs/ViTAEv2_S/TotalText/finetune_150k_tt_mlt_13_15_textocr.yaml
# MODEL_PATH=pretrained/tt_vitaev2-s_finetune_synth-tt-mlt-13-15-textocr.pth
# IMAGES_FOLDER_OR_ONE_IMAGE_PATH=datasets/vintext/test_images
# OUTPUT_PATH=vis_res/vintext

# python3 tools/train_net.py \
#         --config-file ${CONFIG_FILE} \
#         --eval-only MODEL.WEIGHTS ${MODEL_PATH}

# python3 demo/demo.py \
#         --config-file ${CONFIG_FILE} \
#         --input ${IMAGES_FOLDER_OR_ONE_IMAGE_PATH} \
#         --output ${OUTPUT_PATH} \
#         --opts MODEL.WEIGHTS ${MODEL_PATH}

CUDA_VISIBLE_DEVICES=2
CONFIG_FILE=configs/ViTAEv2_S/VinText/finetune_vintext.yaml
MODEL_PATH=output/vitaev2_s/150k_tt_mlt_13_15_textocr/finetune/vintext/model_0017999.pth
IMAGES_FOLDER_OR_ONE_IMAGE_PATH=datasets/vintext/test_images
OUTPUT_PATH=vis_res/vintext

# python3 tools/train_net.py \
#         --config-file ${CONFIG_FILE} \
#         --eval-only MODEL.WEIGHTS ${MODEL_PATH}

python3 demo/demo.py \
        --config-file ${CONFIG_FILE} \
        --input ${IMAGES_FOLDER_OR_ONE_IMAGE_PATH} \
        --output ${OUTPUT_PATH} \
        --opts MODEL.WEIGHTS ${MODEL_PATH} 