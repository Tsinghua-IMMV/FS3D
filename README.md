# FS3D
FS3D: A Large-Scale Dataset of Paired Freehand Sketches and 3D CAD Models
### Setup
```
In your base environment: conda install -y -c conda-forge mamba
conda create -n FS3D python=3.9
conda activate FS3D
mamba install -y pythonocc-core -c conda-forge
mamba install -y freecad -c conda-forge
pip install pymeshlab open3d matplotlib svgpathtools CairoSVG PyQt5 tqdm
```
### Construct the dataset
```
In your cad_data_root, rename each sample folder to the MD5 hash code of its corresponding STEP file.
python regroup_data.py <your collected_data_root> <your cad_data_root>
```