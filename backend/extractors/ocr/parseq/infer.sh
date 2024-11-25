python3 infer_custom.py '../pretrained/vintext_best_parseq.ckpt' \
        --images '../cropped' \
        --outfile preds.txt \
        --device 'cuda' \
        --batch_size 128