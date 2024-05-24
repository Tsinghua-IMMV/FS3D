# Author: Di Huang
# README:
# 1. conda install -y -c conda-forge mamba
# 2. conda create -n YOUR_ENV_NAME python=3.9
# 3. conda activate YOUR_ENV_NAME
# 4. pip install pymeshlab open3d tqdm
# 5. mamba install -y freecad -c conda-forge
# 6. Place the folder containing the STEP models in the same directory as this script.
# 7. Use the script: python step2pcd.py <directory containing STEP models or a single STEP file>
# 8. The point cloud data will be saved in the pcd directory.

import os
import argparse
import sys
import pymeshlab
import open3d as o3d
import numpy as np
from tqdm import tqdm

# sys.path.append(FREECAD_PATH)
# import FreeCAD
import freecad
import FreeCAD as App
import Part
import Mesh

OBJ_CACHE = 'obj_cache.obj'


def step2obj(input_):
    shape = Part.Shape()
    shape.read(input_)
    doc = App.newDocument('Doc')
    pf = doc.addObject('Part::Feature', OBJ_CACHE)
    pf.Shape = shape
    Mesh.export([pf], OBJ_CACHE)


def obj2pcd(output_, input_=OBJ_CACHE, samplenum=10000, include_normal=True, visualize=False):
    ms = pymeshlab.MeshSet()
    ms.load_new_mesh(input_)

    ms.generate_sampling_poisson_disk(samplenum=samplenum)

    vertex_matrix = ms.current_mesh().vertex_matrix()
    if include_normal:
        normal_matrix = ms.current_mesh().vertex_normal_matrix()
        data = np.hstack((vertex_matrix, normal_matrix))
    else:
        data = vertex_matrix

    np.savetxt(output_, data, fmt='%.6f', delimiter=' ')

    if visualize:
        point_cloud = o3d.geometry.PointCloud()
        point_cloud.points = o3d.utility.Vector3dVector(vertex_matrix)
        if args.include_normal:
            point_cloud.normals = o3d.utility.Vector3dVector(normal_matrix)

        o3d.visualization.draw_geometries([point_cloud], point_show_normal=args.include_normal)


def step2pcd(step_path, pcd_path, samplenum=10000, include_normal=True, visualize=False):
    try:
        step2obj(step_path)
    except OSError as e:
        print(f"\nOSError occurs when processing {step_path}")
        return step_path
    obj2pcd(pcd_path, samplenum=samplenum, include_normal=include_normal, visualize=visualize)
    return None


def main(args):
    if os.path.isfile(args.input_path):
        output_ = f'{os.path.splitext(os.path.basename(args.input_path))[0]}.txt'
        error_log = step2pcd(args.input_path, output_, samplenum=args.samplenum, include_normal=args.include_normal, visualize=args.visualize)
        if error_log:
            print('STEP file failed to process:', error_log)
        return

    filepath_list = []
    error_logs = []
    for root, dirs, files in os.walk(args.input_path):
        for filename in files:
            if not filename.lower().endswith(".step") and \
               not filename.lower().endswith(".stp"):
                continue
            filepath_list.append(os.path.join(root, filename))

    for filepath in tqdm(filepath_list):
        filename = os.path.basename(filepath)
        output_ = os.path.join(args.output_root_path, os.path.dirname(filepath))
        os.makedirs(output_, exist_ok=True)
        file_basename = os.path.splitext(filename)[0]
        output_ = os.path.join(output_, f'{file_basename}.txt')
        if args.continue_work and os.path.exists(output_):
            continue
        error_log = step2pcd(filepath, output_, samplenum=args.samplenum, include_normal=args.include_normal, visualize=args.visualize)
        if error_log:
            error_logs.append(error_log)

    print()
    if error_logs:
        print('STEP files failed to process:', error_logs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_path", type=str, help="Input folder or file.")
    parser.add_argument("-O", "--output_root_path", type=str, default="pcd", help="The root directory of the program output.")
    parser.add_argument("-N", "--samplenum", type=int, default=10000, help="The number of samples in point cloud data.")
    parser.add_argument("-E", "--exclude_normal", action='store_true', default=False, help="Exclude normal vectors.")
    parser.add_argument("-V", "--visualize", action='store_true', default=False, help="Visualize point cloud.")
    parser.add_argument("-C", "--continue_work", action='store_true', default=False, help="Continue working.")
    args = parser.parse_args()
    args.include_normal = not args.exclude_normal

    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    relative_path = os.path.relpath(args.input_path, current_script_dir)
    args.input_path = relative_path

    main(args)
    if os.path.exists(OBJ_CACHE):
        os.remove(OBJ_CACHE)
    print('STEP to point cloud data conversion completed!')

