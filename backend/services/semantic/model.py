import requests
import numpy as np
from PIL import Image
from io import BytesIO
import sys
import os
import torch

from towhee import pipe, ops
from transformers import AutoTokenizer, AlignModel, AutoProcessor, AutoModel
import open_clip

class AlignEmbedding:
    def __init__(self):
        self.device = 'cpu'
        self.model = AlignModel.from_pretrained("kakaobrain/align-base").to('cpu')
        self.feature_extractor = AutoProcessor.from_pretrained("kakaobrain/align-base", device='cpu')
        self.tokenizer = AutoTokenizer.from_pretrained("kakaobrain/align-base", device='cpu')
    
    def embed_text(self, text: str) -> np.ndarray:
        inputs = self.tokenizer(text=[text], return_tensors="pt", padding="max_length", max_length=256)
        text_emb = self.model.get_text_features(**inputs)
        text_emb_np = text_emb.cpu().detach().numpy()
        text_emb = np.array(text_emb_np).reshape(-1)
        return text_emb

    def embed_image(self, image_path: str) -> np.ndarray:
        if image_path.startswith("http://") or image_path.startswith("https://"):
            response = requests.get(image_path)
            image = Image.open(BytesIO(response.content)).convert("RGB")
        else:
            image = Image.open(image_path).convert("RGB")
        inputs = self.feature_extractor(images=[image], return_tensors="pt").to('cpu')
        image_emb = self.model.get_image_features(**inputs)

        image_emb_np = image_emb.cpu().detach().numpy()
        image_emb = np.array(image_emb_np).reshape(-1)
        return image_emb

class Blip1Embedding:
    def __init__(self):
        self.device = "cpu"
        self.text_model = ops.image_text_embedding.blip(model_name='blip_itm_large_coco', modality='text', device=self.device)
        self.image_model = ops.image_text_embedding.blip(model_name='blip_itm_large_coco', modality='image', device=self.device)
        self.text_pipe = (
            pipe.input('text')
            .map('text', 'vec', self.text_model)
            .output('vec')
        )
        self.img_pipe = (
            pipe.input('img')
            .map('img', 'vec', self.image_model)  
            .output('vec')
        )
        
    def embed_text(self, text: str) -> np.ndarray:
        output_text = self.text_pipe(text)
        text_embedd = output_text.get()
        text_vec = np.array(text_embedd).reshape(-1)
        return text_vec
    
    def embed_image(self, image_path: str) -> np.ndarray:
        if image_path.startswith("http://") or image_path.startswith("https://"):
            response = requests.get(image_path)
            image = Image.open(BytesIO(response.content)).convert("RGB")
        else:
            image = Image.open(image_path).convert("RGB")

        output_image = self.img_pipe(image)
        image_embedd = output_image.get()
        image_vec = np.array(image_embedd).reshape(-1)
        return image_vec
    
class CoCaEmbedding:
    def __init__(self):
        self.device = 'cpu'
        self.model, _, self.transform = open_clip.create_model_and_transforms(
            model_name="coca_ViT-L-14",
            pretrained="mscoco_finetuned_laion2B-s13B-b90k",
        )
        self.tokenizer = open_clip.get_tokenizer('coca_ViT-L-14')
    
    def embed_text(self, text: str) -> np.ndarray:
        inputs = self.tokenizer(text)
        text_emb = self.model.encode_text(inputs)
        text_emb_np = text_emb.cpu().detach().numpy()
        text_emb = np.array(text_emb_np).reshape(-1)
        return text_emb

    def embed_image(self, image_path: str) -> np.ndarray:
        if image_path.startswith("http://") or image_path.startswith("https://"):
            response = requests.get(image_path)
            image = Image.open(BytesIO(response.content)).convert("RGB")
        else:
            image = Image.open(image_path).convert("RGB")
        inputs = self.transform(image).unsqueeze(0).to('cpu')
        image_emb = self.model.encode_image(inputs)

        image_emb_np = image_emb.cpu().detach().numpy()
        image_emb = np.array(image_emb_np).reshape(-1)
        return image_emb
    
class JinaEmbedding:
    def __init__(self):
        self.device = 'cpu'
        self.model = AutoModel.from_pretrained('jinaai/jina-clip-v1', trust_remote_code=True).to('cpu')
        # self.feature_extractor = AutoProcessor.from_pretrained("kakaobrain/align-base", device='cpu')
        # self.tokenizer = AutoTokenizer.from_pretrained("kakaobrain/align-base", device='cpu')
    
    def embed_text(self, text: str) -> np.ndarray:
        text_emb = self.model.encode_text([text])
        text_emb_np = text_emb#.cpu().detach().numpy()
        text_emb = np.array(text_emb_np).reshape(-1)
        return text_emb

    def embed_image(self, image_path: str) -> np.ndarray:
        if image_path.startswith("http://") or image_path.startswith("https://"):
            response = requests.get(image_path)
            image = Image.open(BytesIO(response.content)).convert("RGB")
        else:
            image = Image.open(image_path).convert("RGB")
        image_emb = self.model.encode_image([image_path])

        image_emb_np = image_emb#.cpu().detach().numpy()
        image_emb = np.array(image_emb_np).reshape(-1)
        return image_emb
    
    
module_path = os.path.join(os.path.abspath(__file__).rsplit("/", maxsplit=3)[0], "extractors/CLIP2Video")
sys.path.append(module_path)

from common import init_device, init_model, set_seed_logger
from config import Config
from modules.tokenization_clip import SimpleTokenizer as ClipTokenizer

class CLIP2VideoTextEncoder:
    def __init__(self, checkpoint, clip_path):
        args = Config(
            video_path=None,
            checkpoint=checkpoint, # 'visione/services/analysis/features-clip2video/checkpoint',
            clip_path=clip_path # 'visione/services/analysis/features-clip2video/checkpoint/ViT-B-32.pt'
        )
        
        args.gpu = False
        
        args, self.logger = set_seed_logger(args)
        device, n_gpu = init_device(args, args.local_rank, self.logger)
        self.device = device

        # setting tokenizer
        self.tokenizer = ClipTokenizer()

        # start and end token
        self.SPECIAL_TOKEN = {"CLS_TOKEN": "<|startoftext|>", "SEP_TOKEN": "<|endoftext|>",
                              "MASK_TOKEN": "[MASK]", "UNK_TOKEN": "[UNK]", "PAD_TOKEN": "[PAD]"}

        self.max_words = args.max_words

        # init model
        self.model = init_model(args, self.device, self.logger)

    def encode_text(self, caption):
        """get tokenized word feature

        Args:
            caption: caption

        Returns:
            pairs_text: tokenized text
            pairs_mask: mask of tokenized text
            pairs_segment: type of tokenized text

        """

        # tokenize word
        words = self.tokenizer.tokenize(caption)

        # add cls token
        words = [self.SPECIAL_TOKEN["CLS_TOKEN"]] + words
        total_length_with_CLS = self.max_words - 1
        if len(words) > total_length_with_CLS:
            words = words[:total_length_with_CLS]

        # add end token
        words = words + [self.SPECIAL_TOKEN["SEP_TOKEN"]]

        # convert token to id according to the vocab
        input_ids = self.tokenizer.convert_tokens_to_ids(words)

        # add zeros for feature of the same length
        input_mask = [1] * len(input_ids)
        segment_ids = [0] * len(input_ids)
        while len(input_ids) < self.max_words:
            input_ids.append(0)
            input_mask.append(0)
            segment_ids.append(0)

        # ensure the length of feature to be equal with max words
        assert len(input_ids) == self.max_words
        assert len(input_mask) == self.max_words
        assert len(segment_ids) == self.max_words
        pairs_text = torch.LongTensor(input_ids)
        pairs_mask = torch.LongTensor(input_mask)
        pairs_segment = torch.LongTensor(segment_ids)

        return pairs_text, pairs_mask, pairs_segment

    def get_text_embedding(self, caption):
        input_ids, input_mask, segment_ids = self.encode_text(caption)

        input_ids, segment_ids, input_mask = input_ids.unsqueeze(0), segment_ids.unsqueeze(0), input_mask.unsqueeze(0)  # emulate bs = 1
        input_ids, segment_ids, input_mask = input_ids.to(self.device), segment_ids.to(self.device), input_mask.to(self.device)
        with torch.no_grad():
            sequence_output = self.model.get_sequence_output(input_ids, segment_ids, input_mask)

            text_feature = self.model.get_text_features(sequence_output, input_mask)
            text_feature = text_feature.squeeze(0).cpu().numpy()
        return text_feature