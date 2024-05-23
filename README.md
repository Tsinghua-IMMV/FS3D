# FS3D
FS3D: A Large-Scale Dataset of Paired Freehand Sketches and 3D CAD Models
### Setup
```
In your base environment: conda install -y -c conda-forge mamba
conda create -n FS3D python=3.9
conda activate FS3D
mamba install -y pythonocc-core -c conda-forge
mamba install -y freecad -c conda-forge
pip install pymeshlab open3d matplotlib svgpathtools tqdm
```