[中文文档](README_CN.md)

> This document is a translation of the original Chinese documentation. For the original version, please refer to `README_CN.md`.

# KAIST Dataloader

> Easily read point cloud data and pose information from the KAIST dataset.

## Project Overview

This project aims to provide an efficient and user-friendly point cloud data loader for the KAIST dataset, supporting multiple coordinate system conversions, iteration, slicing operations, and more. It is suitable for scenarios such as autonomous driving, SLAM, and 3D reconstruction.

## Features

- **Multiple Coordinate Systems Supported**:  
  - `base_link`: Vehicle local coordinate system  
  - `map`: Coordinate system with the first frame as the origin  
  - `world`: Global GPS coordinate system
- **Iterator & Slicing**: Supports iteration, slicing, and random access
- **Numpy Compatibility**: Can read directly from numpy arrays
- **Dataset Length Retrieval**: Supports the `len()` method
- **Mixed Loading**: Automatically mixes and loads VLP_Left and VLP_Right point clouds sorted by timestamp

## Installation

```bash
pip install -e .
# Or use uv
uv pip install -e .
```

## Quick Start

```python
from kaist_dataloader import KaistPointCloudLoader

loader = KaistPointCloudLoader("/path/to/kaist/campus00", frame_id="map")
cld, pose = loader[0]  # Read the first point cloud and its pose

# Iterative access
for cld, pose in loader[:10]:
    # Process point cloud and pose
    pass

# Get dataset length
print(len(loader))
```

## C++/pybind11 Example

This project supports direct invocation of the Python loader in C++ via pybind11, suitable for integration with C++ projects.  
Sample code can be found in `example/cpp/main.cc`. Ensure the `root` path points to a valid KAIST dataset directory.

### Build and Run Steps

1. **Activate Python virtual environment** (ensure kaist-dataloader and pybind11 are installed)  
2. Modify line 18 in `main.cc` to set the `root` variable to your dataset path, e.g., `/ws/data/kaist/campus00`
3. Build the project:
   ```bash
   cd example/cpp
   cmake -S . -B build
   cmake --build build
   ```
4. Run the example:
   ```bash
   ./build/embed_loader
   ```

After running, the output will show the dataset length, and the shapes of the point cloud and pose.

## Notes

- The loader mixes left and right LiDAR data by default, and the returned pose is in the specified coordinate system.
- For fine-grained control over loading, use the `kaist_dataloader.basic` module.
- Point cloud data format: `[x, y, z, intensity]`; pose format: `4x4` transformation matrix.

## Dependencies

- numpy
- scipy

Development/testing dependencies:
- open3d
- matplotlib
- pytest
- ipykernel

## Changelog

- **v0.1.0**: Initial version, implemented the