# Author: Di Huang

import os
import argparse
from tqdm import tqdm
from utils import *


parser = argparse.ArgumentParser()
parser.add_argument("input_path", type=str, help="The root directory of the collected data.")
args = parser.parse_args()
input_path = args.input_path
file_mapping_path = os.path.join(args.input_path, "file_mapping.txt")

file_mapping_dict = {}
with open(file_mapping_path, "r", encoding="utf-8") as file:
    for line in file:
        if "->" in line:
            key, value = line.strip().split(" -> ")
            file_mapping_dict[key] = value

sample_paths = []
for root, dirs, files in os.walk(input_path):
    for filename in files:
        if filename == 'meta.json':
            sample_paths.append(os.path.dirname(os.path.join(root, filename)))
sample_paths = sorted(sample_paths)

for sample_path in tqdm(sample_paths):
    sample_name = os.path.basename(sample_path)
    step_path = file_mapping_dict[sample_name]
    md5 = hash_file(step_path)
    os.rename(sample_path, os.path.join(os.path.dirname(sample_path), md5))
