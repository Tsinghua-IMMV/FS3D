# Author: Di Huang

import os
import random
import numpy as np
from PIL import Image
import cairosvg
import hashlib
import json


def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)


def remove_transparency(img_path):
    with Image.open(img_path).convert("RGBA") as img:
        if img.mode in ('RGBA', 'LA'):
            background = Image.new("RGBA", img.size, (255, 255, 255, 255))
            background.paste(img, mask=img.split()[-1])
            img = background
        img = img.convert("RGB")
        img.save(img_path)


def svg2img(svg_path, img_path, img_size=(2160, 1344)):
    cairosvg.svg2png(url=svg_path, write_to=img_path, output_width=img_size[0], output_height=img_size[1])
    remove_transparency(img_path)


def hash_file(filepath, chunk_size=8192):
    hasher = hashlib.md5()
    with open(filepath, 'rb') as file:
        while chunk := file.read(chunk_size):
            hasher.update(chunk)
    return hasher.hexdigest()


def read_json(filepath, key):
    with open(filepath, 'r') as file:
        data = json.load(file)
    return data.get(key)

