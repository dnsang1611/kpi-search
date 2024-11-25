import cv2
import numpy as np
from detectron2.data.transforms import Augmentation, PadTransform
import random
from PIL import Image, ImageDraw, ImageFont

def segment_image(ori_img, polygons):
    mask = np.zeros(ori_img.shape[:2], np.uint8)
    cv2.fillPoly(mask, polygons, color=(255, 255, 255))
    segmented_img = ori_img * mask[:,:, np.newaxis]
    return segmented_img

def crop_image(img, polygons):
    cropped_imgs = []
    for polygon in polygons:
        rect = cv2.boundingRect(polygon)
        x,y,w,h = rect
        cropped_imgs.append(img[y:y+h, x:x+w])
    return cropped_imgs

class Pad(Augmentation):
    def __init__(self, divisible_size = 32):
        super().__init__()
        self._init(locals())

    def get_transform(self, img):
        ori_h, ori_w = img.shape[:2]  # h, w
        if ori_h % 32 == 0:
            pad_h = 0
        else:
            pad_h = 32 - ori_h % 32
        if ori_w % 32 == 0:
            pad_w = 0
        else:
            pad_w = 32 - ori_w % 32
        # pad_h, pad_w = 32 - ori_h % 32, 32 - ori_w % 32
        return PadTransform(
            0, 0, pad_w, pad_h, pad_value=0
        )
    
def visualize(save_path, img, polygons, texts):
    colors = [(0,0.5,0),(0,0.75,0),(1,0,1),(0.75,0,0.75),(0.5,0,0.5),(1,0,0),(0.75,0,0),(0.5,0,0),
        (0,0,1),(0,0,0.75),(0.75,0.25,0.25),(0.75,0.5,0.5),(0,0.75,0.75),(0,0.5,0.5),(0,0.3,0.75)]
    font = ImageFont.truetype('Arial.ttf', size=12)

    polygon_img = Image.new('RGBA', img.size, (0, 0, 0, 0))
    text_img = Image.new('RGBA', img.size, (0, 0, 0, 0))

    polygon_draw = ImageDraw.Draw(polygon_img)
    text_draw = ImageDraw.Draw(text_img)

    for polygon, text in zip(polygons, texts):
        color = random.choice(colors)
        color = tuple(map(lambda channel: int(255 * channel), color))
        polygon = list(map(tuple, polygon))
        polygon_draw.polygon(polygon, fill=color + (90,), outline=color + (255,))
        x_min, y_min = np.min(polygon, axis=0)
        text_size = text_draw.textsize(text, font=font)
        text_draw.rectangle([x_min, y_min - 10, x_min + text_size[0], y_min - 8 + text_size[1]], 
                            fill=(255, 255, 255, 255))
        text_draw.text((x_min, y_min - 9), text, font=font, fill=color + (255, ))

    img = img.convert("RGBA")
    img = Image.alpha_composite(img, polygon_img)
    img = Image.alpha_composite(img, text_img)
    img = img.convert("RGB")

    img.save(save_path)