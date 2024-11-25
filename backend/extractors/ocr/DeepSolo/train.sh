CONFIG_FILE=configs/ViTAEv2_S/VinText/finetune_vintext.yaml
CUDA_VISIBLE_DEVICES=2,3 python3 tools/train_net.py \
        --config-file ${CONFIG_FILE} \
        --num-gpus 2