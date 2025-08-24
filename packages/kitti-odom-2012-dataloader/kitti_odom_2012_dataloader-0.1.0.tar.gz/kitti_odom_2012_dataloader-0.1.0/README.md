# KITTI Odometry 2012 Point Cloud Data Loader (English Translation)

> This is an English translation of the original [中文版](./README_CN.md).

> **Dataset Homepage**: [KITTI Odometry Benchmark](http://www.cvlibs.net/datasets/kitti/eval_odometry.php)

## Project Overview

This project provides an efficient and user-friendly point cloud data loader for the KITTI Odometry 2012 dataset. It supports multiple coordinate system conversions, iteration, slicing, and is suitable for scenarios such as autonomous driving, SLAM, and 3D reconstruction.

## Features

- **Multiple Coordinate Systems Supported**
  - `BASE_LINK`: Vehicle local coordinate system
  - `MAP_KITTI`: KITTI official global coordinate system (RDF)
  - `MAP_FLU`: Common FLU global coordinate system
- **Iterator and Slicing**: Supports iteration, slicing, and random access
- **Numpy Compatible**: Can read directly from numpy arrays
- **Dataset Length**: Supports the `len()` method

## Installation

It is recommended to use [uv](https://github.com/astral-sh/uv) or pip to install dependencies:

```bash
uv pip install -e .
```

Or use pip directly:

```bash
pip install kitti-odom-2012-dataloader
```

## Quick Start

```python
from kitti_odom_2012_dataloader import PointCloudLoader, FrameID

loader = PointCloudLoader("/path/to/kitti/sequences/00", frame_id=FrameID.MAP_FLU)
cld, pose = loader[0]  # Read the first point cloud and its pose

# Iterate over the first 10 frames
for cld, pose in loader[:10]:
    # Process point cloud and pose
    pass

# Get dataset length
print(len(loader))
```

## C++/pybind11 Example

This project supports direct invocation of the Python loader in C++ via pybind11, suitable for integration with C++ projects.  
See `example/cpp/main.cc` for sample code. Ensure the `root` path points to a valid KITTI dataset directory.

### Build and Run Steps

1. **Activate Python virtual environment** (ensure kitti-odom-2012-dataloader and pybind11 are installed)
2. Modify line 18 in `main.cc` to set the `root` variable to your dataset path, e.g., `/ws/data/kitti/sequences/00`
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

After running, it will output the dataset length, point cloud, and pose shapes.

### Main Code Logic

- Start Python interpreter  
  ```cpp
  #include <pybind11/embed.h>
  namespace py = pybind11;
  py::scoped_interpreter guard{};
  ```
- Import `kitti_odom_2012_dataloader` module  
  ```cpp
  py::module_ kd = py::module_::import("kitti_odom_2012_dataloader");
  py::object PointCloudLoader = kd.attr("PointCloudLoader");
  py::object FrameID = kd.attr("FrameID");
  ```
- Create `PointCloudLoader` instance  
  ```cpp
  const char* root = "/ws/data/kitti/sequences/00";
  py::object loader =
    PointCloudLoader(root, py::arg("frame_id") = FrameID.attr("MAP_FLU"));
  ```
- Read dataset length  
  ```cpp
  std::size_t n = loader.attr("__len__")().cast<std::size_t>();
  std::cout << "dataset length = " << n << "\n";
  ```
- Read point cloud and pose, print shapes  
  ```cpp
  py::tuple item0 = loader[py::int_(0)];
  py::array_t<float> cld = item0[0].cast<py::array_t<float>>();
  py::array_t<double> pose = item0[1].cast<py::array_t<double>>();
  std::cout << "points shape = (" << cld.shape(0) << ", " << cld.shape(1) << ")\n";
  std::cout << "pose shape   = (" << pose.shape(0) << ", " << pose.shape(1) << ")\n";
  ```
- Iterate over first 10 frames (optional)  
  ```cpp
  for (py::size_t i = 0; i < 10 && i < n; ++i) {
    py::tuple it = loader[py::int_(i)];
    // Process point cloud and pose here
  }
  ```

See `example/cpp/main.cc` for detailed code.

## Coordinate System Description

- `BASE_LINK`: Vehicle local coordinate system, point cloud transformed by calibration matrix
- `MAP_KITTI`: KITTI official global coordinate system (RDF), point cloud transformed by global pose
- `MAP_FLU`: Common FLU global coordinate system, point cloud converted from RDF to FLU

You can switch coordinate systems via the `frame_id` parameter or attribute:

```python
loader.frame_id = FrameID.MAP_FLU
cld, pose = loader[0]
```

## API Reference

- [`PointCloudLoader`](src/kitti_odom_2012_dataloader/pointcloud.py): Main loader class, supports indexing, slicing, iteration
- [`FrameID`](src/kitti_odom_2012_dataloader/pointcloud.py): Coordinate system enum type
- [`get_lidar_files`](src/kitti_odom_2012_dataloader/basic.py): Get point cloud file list
- [`read_lidar`](src/kitti_odom_2012_dataloader/basic.py): Read single frame point cloud
- [`load_calib_matrix`](src/kitti_odom_2012_dataloader/basic.py): Read calibration matrix
- [`load_global_poses`](src/kitti_odom_2012_dataloader/basic.py): Read global poses
- [`transform_point_cloud`](src/kitti_odom_2012_dataloader/basic.py): Point cloud coordinate transformation

## Data Format

- Point cloud data shape: `[N, 4]`, representing `[x, y, z, intensity]`
- Pose matrix shape: `[4, 4]`

## Dependencies

- numpy

Development/testing dependencies (see [pyproject.toml](pyproject.toml)):
- open3d
- matplotlib
- pytest
- ipykernel
- ruff

## Testing

Unit tests are included. Run:

```bash
uv pip install .[dev]
uv run pytest
```

## Changelog

- **v0.1.0**: Initial version, basic functionality implemented