# Author: Di Huang

import os
import shutil
import argparse
from tqdm import tqdm

from utils import *
from contour_generation import generate_contour
from contour_deformation import contour_deformation
from snapshot_generation import generate_snapshot
from step2pcd import step2pcd


def get_cam_info(filepath):
    cam_info = {}
    with open(filepath, "r", encoding="utf-8") as file:
        for line in file:
            if ":" in line:
                key, value = line.strip().split(": ")
                cam_info[key] = list(map(float, value.split(','))) if ',' in value else float(value)
    return cam_info


def group_contour_data(step_path, contour_path, cam_info, img_size):
    direction, up, eye, scale = cam_info["Direction"], cam_info["Up"], cam_info["Eye"], cam_info["Scale"]
    temp_contour_ = f'{os.path.splitext(contour_path)[0]}'
    temp_contour_path = f'{os.path.splitext(contour_path)[0]}.svg'
    generate_contour(step_path, temp_contour_path, direction=direction, up=up, line_width=args.line_width)
    contour_deformation(temp_contour_path, temp_contour_path, output_color=f'{temp_contour_}_color.svg')
    svg2img(temp_contour_path, contour_path, img_size=img_size)


def main(args):
    hash2path = {}
    for root, dirs, files in os.walk(args.cad_data_root):
        for filename in files:
            if not filename.lower().endswith(('.step', '.stp')):
                continue
            filepath = os.path.join(root, filename)
            hash2path[hash_file(filepath)] = os.path.join(root, filename)

    sample_paths = []
    for root, dirs, files in os.walk(args.collected_data_root):
        for filename in files:
            if filename == 'meta.json':
                sample_paths.append(os.path.dirname(os.path.join(root, filename)))
    sample_paths = sorted(sample_paths)

    for i, sample_path in enumerate(tqdm(sample_paths)):
        sample_name = os.path.basename(sample_path)
        print(f'\n----- [{i + 1}/{len(sample_paths)}] Processing {sample_name}')
        step_path = hash2path.get(sample_name)
        step_path = step_path if step_path else read_json(os.path.join(sample_path, 'meta.json'), 'MD5')
        if not step_path or not os.path.exists(step_path):
            print(f'----- Failed to locate its STEP file: {sample_path}')
            continue

        step_basename = os.path.splitext(os.path.basename(step_path))[0]
        if args.group == 'all' or args.group == 'pcd':
            pcd_path = os.path.join(sample_path, f'{step_basename}.txt')
            if args.restart or not os.path.exists(pcd_path):
                step2pcd(step_path, pcd_path, samplenum=args.num_point)

        if args.group == 'all' or args.group == 'cd':
            cam_info_list = []
            for file in os.listdir(sample_path):
                if file.startswith("cam_"):
                    cam_info = get_cam_info(os.path.join(sample_path, file))
                    index = os.path.splitext(file)[0].split('_')[1]
                    cam_info_list.append((index, cam_info))
            
            for index, cam_info in cam_info_list:
                contour_path = os.path.join(sample_path, f"contour_{index}.png")
                if args.restart or not os.path.exists(contour_path):
                    group_contour_data(step_path, contour_path, cam_info, img_size=(args.img_width, args.img_height))
                remove_transparency(os.path.join(sample_path, f'sketch_{index}.png'))

        if args.restart or not os.path.exists(os.path.join(sample_path, os.path.basename(step_path))):
            shutil.copy(step_path, sample_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("collected_data_root", type=str, help="The root directory of the collected data.")
    parser.add_argument("cad_data_root", type=str, help="The root directory of the CAD data.")
    parser.add_argument("--line_width", type=float, default=0.8, help="Line width.")
    parser.add_argument("-R", "--restart", action='store_true', default=False, help="Continue working.")
    parser.add_argument("--img_width", type=int, default=2160, help="Image width.")
    parser.add_argument("--img_height", type=int, default=1344, help="Image height.")
    parser.add_argument("-G", "--group", type=str, default='all', help="Data to be grouped. all: everything, pcd: only point cloud data, cd: only contour data")
    parser.add_argument("--num_point", type=int, default=10000, help="The number of samples in the point cloud data.")
    args = parser.parse_args()

    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    relative_path = os.path.relpath(args.collected_data_root, current_script_dir)
    args.collected_data_root = relative_path
    relative_path = os.path.relpath(args.cad_data_root, current_script_dir)
    args.cad_data_root = relative_path
    
    set_seed(0)
    main(args)

