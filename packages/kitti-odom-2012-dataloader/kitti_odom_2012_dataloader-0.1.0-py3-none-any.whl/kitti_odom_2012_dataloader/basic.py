# %%
import numpy as np
import os


# %%
def get_lidar_files(base_path: str) -> list[str]:
    """Get a list of all LiDAR files in the specified directory.

    Args:
        base_path (str): The base directory containing the LiDAR files.

    Returns:
        list[str]: A list of file paths to the LiDAR files.
    """
    lidar_files = sorted(os.listdir(base_path))
    lidar_files = [
        os.path.join(base_path, f) for f in lidar_files if f.endswith(".bin")
    ]
    return lidar_files


# %%
def read_lidar(lidar_file: str) -> np.ndarray:
    """Read a LiDAR file and return the point cloud data.

    Args:
        file_path (str): The path to the LiDAR file.

    Returns:
        np.ndarray: A numpy array of shape (N, 4) containing the point cloud data.
    """
    point_cloud = np.fromfile(lidar_file, dtype=np.float32).reshape(-1, 4)
    return point_cloud


# %%
def load_calib_matrix(calib_file: str) -> np.ndarray:
    """Load the calibration matrix from a text file.

    Args:
        calib_file (str): The path to the calibration file.

    Returns:
        np.ndarray: A 4x4 numpy array representing the calibration matrix.
    """
    with open(calib_file, "r") as f:
        lines = f.readlines()

    # Assuming the calibration file has a line starting with 'Tr:' for the transformation matrix
    for line in lines:
        if line.startswith("Tr:"):
            values = list(map(float, line.strip().split()[1:]))
            calib_matrix = np.eye(4)
            calib_matrix[:3, :] = np.array(values).reshape(3, 4)
            return calib_matrix

    raise ValueError("Calibration matrix not found in the file.")


# %%
def load_global_poses(pose_file: str) -> np.ndarray:
    """Load global poses from a text file.

    Args:
        pose_file (str): The path to the pose file.

    Returns:
        np.ndarray: An array of shape (N, 4, 4) containing the global poses.
    """
    poses = []
    for line in open(pose_file, "r").readlines():
        values = list(map(float, line.strip().split()))
        pose = np.eye(4)
        pose[:3, :] = np.array(values).reshape(3, 4)
        poses.append(pose)

    return np.array(poses)


# %%
def transform_point_cloud(points: np.ndarray, T: np.ndarray) -> np.ndarray:
    """
    Transforms a point cloud using a transformation matrix.
    Args:
        points (np.ndarray): A numpy array of shape (N, 3) containing the points.
        T (np.ndarray): A 4x4 transformation matrix.
    Returns:
        np.ndarray: A numpy array of shape (N, 3) containing the transformed points.
    """
    assert points.shape[1] == 3, "Points should be of shape (N, 3)."
    assert T.shape == (4, 4), "Transformation matrix should be of shape (4, 4)."
    num = points.shape[0]
    points_homogeneous = np.hstack((points, np.ones((num, 1))))
    return (T @ points_homogeneous.T).T[:, :3]


# %%
# import open3d as o3d

# files = get_lidar_files('/ws/data/kitti/sequences/00/velodyne/')
# cld0 = read_lidar(files[0])
# Tr = load_calib_matrix('/ws/data/kitti/sequences/00/calib.txt')
# gposes = load_global_poses('/ws/data/kitti/poses/00.txt')
# cld0_base_link = transform_point_cloud(cld0[:, :3], Tr)

# cld0_world = transform_point_cloud(cld0_base_link, T_bias @ gposes[0])

# pcd0 = o3d.geometry.PointCloud()
# pcd0.points = o3d.utility.Vector3dVector(cld0_world)
# pcd0.colors = o3d.utility.Vector3dVector(np.tile(cld0[:, 3:4], (1, 3)) / 255.0)
# o3d.visualization.draw_geometries([pcd0])
# o3d.io.write_point_cloud("cld0.pcd", pcd0)
