import os
from PIL import Image
from math import ceil, floor
import asyncio
import traceback
import numpy as np
import csv
from natsort import natsorted
from datetime import datetime
import time
from multiprocessing import Pool
import re
import copy
import json

import uvicorn
from fastapi import FastAPI, Form, Depends, Request, HTTPException, File, UploadFile, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.param_functions import File
from pydantic import BaseModel
from typing import List, Dict, Any, Callable

from meili import Meilisearch

from services import (
    ColorIndexer, ColorSearchEngine,
    ObjectSearchEngine,
    PoseIndexer, PoseSearchEngine,
    ImageSemanticIndexer, ImageSemanticSearchEngine, CoCaEmbedding,
    VideoSemanticIndexer, VideoSemanticSearchEngine, CLIP2VideoTextEncoder,
    RerankImages
)

os.environ["TOKENIZERS_PARALLELISM"] = "false"

## ============ 1. GLOBAL VARIABLES ======================
KEYFRAME_PATH = "/mnt/mmlab2024nas/visedit/AIC2024/code/frontend/public/Data/Newframe"
MAPFRAME_PATH = "/mnt/mmlab2024nas/visedit/AIC2024/code/frontend/public/Data/Mapframe"
METADATA_PATH = "/mnt/mmlab2024nas/visedit/AIC2024/code/frontend/public/Data/Metadata"
VIDEO_ROOT = "/mnt/mmlab2024nas/visedit/AIC2024/data/Video_a" # Get fps

# Semantic
# IMG_SEM_FEAT_DIR = "/mnt/mmlab2024nas/visedit/AIC2024/code/Features/ALIGN"
# IMG_SEM_INDXER_DIR = "/mnt/mmlab2024nas/visedit/AIC2024/code/Indexer/ALIGN"
# IMG_SEM_FEAT_DIR = "/mnt/mmlab2024nas/visedit/AIC2024/code/Features/JINA"
# IMG_SEM_INDXER_DIR = "/mnt/mmlab2024nas/visedit/AIC2024/code/Indexer/JINA"
IMG_SEM_FEAT_DIR = "/mnt/mmlab2024nas/visedit/AIC2024/code/Features/COCA"
IMG_SEM_INDXER_DIR = "/mnt/mmlab2024nas/visedit/AIC2024/code/Indexer/COCA"
SELECTED_KEYFRAME_DIR = "/mnt/mmlab2024nas/visedit/AIC2024/code/Script/keyframe_selection/backend/db/videos_groups"
VIDEO_SEM_FEAT_DIR = "/mnt/mmlab2024nas/visedit/AIC2024/code/Features/clip2video"
VIDEO_SEM_INDEXER_DIR = "/mnt/mmlab2024nas/visedit/AIC2024/code/Indexer/clip2video"
VIDEO_CKPT_DIR = "/mnt/mmlab2024nas/visedit/AIC2024/code/Backend/extractors/CLIP2Video/pretrained"
VIDEO_CLIP_PATH = "/mnt/mmlab2024nas/visedit/AIC2024/code/Backend/extractors/CLIP2Video/pretrained/ViT-B-32.pt"

# OCR

# ASR

# COLOR
COLOR_FEAT_DIR = "/mnt/mmlab2024nas/visedit/AIC2024/code/Features/color_visione"
COLOR_INDEXER_DIR = "/mnt/mmlab2024nas/visedit/AIC2024/code/Indexer/color_visione"

# OBJ
OBJ_FEAT_PATH = "/mnt/mmlab2024nas/visedit/AIC2024/code/JSON/obj/obj_final/obj_final.json"

# POSE
POSE_FEAT_DIR = "/mnt/mmlabworkspace/Students/visedit/AIC2024/Features/POSE"
POSE_INDEXER_DIR = '/mnt/mmlabworkspace/Students/visedit/AIC2024/Features/POSE_INDEX'

## ============== 2. SEARCH ENGINE ===========================
# Semantic search
semantic_embedd = CoCaEmbedding()
image_semantic_indexer = ImageSemanticIndexer(IMG_SEM_FEAT_DIR, IMG_SEM_INDXER_DIR, SELECTED_KEYFRAME_DIR, KEYFRAME_PATH)
image_semantic_search_engine = ImageSemanticSearchEngine(image_semantic_indexer)

video_text_embedd = CLIP2VideoTextEncoder(VIDEO_CKPT_DIR, VIDEO_CLIP_PATH)
video_semantic_indexer = VideoSemanticIndexer(
    VIDEO_SEM_FEAT_DIR, VIDEO_SEM_INDEXER_DIR, 
    sel_keyframe_dir=SELECTED_KEYFRAME_DIR, 
    keyframe_dir=KEYFRAME_PATH, 
    video_root=VIDEO_ROOT
)
video_semantic_search_engine = VideoSemanticSearchEngine(video_semantic_indexer)

# Color Search Engine
color_indexer = ColorIndexer(COLOR_FEAT_DIR, COLOR_INDEXER_DIR, sel_keyframe_dir=SELECTED_KEYFRAME_DIR)
color_search_engine = ColorSearchEngine(color_indexer)

## Meilisearch
ocr_search_engine = Meilisearch('OCR')
asr_search_engine = Meilisearch('ASR')

### Object Retrieval
obj_search_engine = ObjectSearchEngine(OBJ_FEAT_PATH)

# Re-rank Images
rerank_images = RerankImages(alpha=1, beta=1, gamma=1)


## ============= 3. Helper function ===============
def find_image_position(folder_name, image_name):
    files = natsorted(os.listdir(folder_name))
    try:
        position = files.index(image_name)
        return position
    except ValueError:
        return -1

def split_path(input_path):
    directory = os.path.dirname(input_path)
    filename = os.path.basename(input_path)
    return directory, filename

def get_video_name(image_path):
    parts = image_path.split('/')
    video_name = parts[-2]
    return video_name

def get_feature_vector(feats_dir, image_path):
    directory, filename = split_path(image_path)
    video_name = get_video_name(image_path)
    feat_path = os.path.join(feats_dir, f'{video_name}.npy')
    position = find_image_position(directory, filename)
    if position != -1:
        return np.load(feat_path)[position]
    else:
        return None

def calculate_relative_distances(vector):
    num_points = len(vector) // 2
    distances = []
    for i in range(1, num_points):
        pivot_x, pivot_y = vector[0], vector[1]
        current_x, current_y = vector[i * 2], vector[i * 2 + 1]
        distances.extend([abs(current_x - pivot_x), abs(current_y - pivot_y)])
        for j in range(1, i):
            prev_x, prev_y = vector[j * 2], vector[j * 2 + 1]
            distances.extend([abs(current_x - prev_x), abs(current_y - prev_y)])
    return np.array(distances)

def calculate_f1(a, b):
    return 2 * a * b / (a + b + 1e-6)

def harmonic_mean(scores):
    scores = np.array(scores)
    eps = 1e-6
    hmean = len(scores) / (1 / (scores + eps)).sum()
    return hmean

def frame_name_to_number(frame_name):
    pattern = r"Videos_L(\d+)/L(\d+)_V(\d+)/(\d+).jpg"
    match = re.match(pattern, frame_name)
    batch_id = int(match.group(1))
    video_id = int(match.group(3))
    frame_id = int(match.group(4))

    number = f"{batch_id:02}{video_id:03}{frame_id:05}"
    return np.int64(number)

def number_to_frame_name(number):
    number = f"{number:010}"
    batch_id = int(number[:2])
    video_id = int(number[2:5])
    frame_id = int(number[5:])
    return f"Videos_L{batch_id:02}/L{batch_id:02}_V{video_id:03}/{frame_id:06}.jpg"