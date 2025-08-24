# %%
from collections.abc import Iterator
from enum import Enum, auto
from pathlib import Path
from typing import overload

import numpy as np

from .basic import (
    get_lidar_files,
    load_calib_matrix,
    load_global_poses,
    read_lidar,
    transform_point_cloud,
)

VLP_DIR = "velodyne"
CLB_PATH = "calib.txt"
STAMP_PATH = "times.txt"
GLOBAL_POSE_DIR = "../../poses"


class FrameID(Enum):
    BASE_LINK = auto()
    MAP_KITTI = auto()
    MAP_FLU = auto()

    @classmethod
    def help(cls) -> str:
        names = [f"FrameID.{e.name}: {e.__doc__}" for e in FrameID]
        return f"Valid frame_id choices:\n\t{'\n\t'.join(names)}"


FrameID.BASE_LINK.__doc__ = "Vehicle frame"
FrameID.MAP_KITTI.__doc__ = "Global frame, Kitti coordinate system (RDF)"
FrameID.MAP_FLU.__doc__ = "Global frame, Commonly used FLU coordinate system"


# %%
class PointCloudLoader:
    def __init__(self, root_dir: str, frame_id: FrameID = FrameID.BASE_LINK) -> None:
        if not isinstance(frame_id, FrameID):
            raise TypeError(FrameID.help())
        self._frame_id = frame_id

        seq = Path(root_dir).name
        self.root_dir = Path(root_dir)
        self.velodyne_dir = self.root_dir / VLP_DIR
        self.clb_path = self.root_dir / CLB_PATH
        self.stamp_path = self.root_dir / STAMP_PATH
        self.global_pose_path = self.root_dir / GLOBAL_POSE_DIR / f"{seq}.txt"
        self.global_pose_path = self.global_pose_path.resolve()

        # 验证路径是否存在
        assert self.velodyne_dir.is_dir(), f"{self.velodyne_dir} not exists"
        assert self.clb_path.is_file(), f"{self.clb_path} not exists"
        assert self.stamp_path.is_file(), f"{self.stamp_path} not exists"
        assert self.global_pose_path.is_file(), f"{self.global_pose_path} not exists"

        # 加载转换矩阵
        self.Tr = load_calib_matrix(str(self.clb_path))
        # Kitti 使用 RDF 坐标系, 我们常用的 FLU 坐标系, 这个是从 RDF 到 FLU 的转换矩阵
        self.Tb = np.array(
            [
                [0.015499, -0.028853, 0.999464, -1.150242],
                [-0.999770, 0.014367, 0.015919, -1.051121],
                [-0.014819, -0.999480, -0.028624, 0.360401],
                [0.000000, 0.000000, 0.000000, 1.000000],
            ]
        )

        # 预加载所有点云文件路径和全局位姿
        self.global_poses = load_global_poses(str(self.global_pose_path))
        self.lidar_files = get_lidar_files(str(self.velodyne_dir))
        assert len(self.lidar_files) == len(self.global_poses), (
            "Lidar frame num should match global pose num"
        )

        # 迭代器用的状态量
        self._current_index = 0
        self._length = len(self.lidar_files)

    def __len__(self) -> int:
        return self._length

    @property
    def frame_id(self) -> str:
        return self._frame_id.name

    @frame_id.setter
    def frame_id(self, value: FrameID) -> None:
        if not isinstance(value, FrameID):
            raise TypeError(FrameID.help())
        self._frame_id = value

    def __get_one(self, idx: int) -> tuple[np.ndarray, np.ndarray]:
        """
        Returns the point cloud and global pose at the given index.
        Args:
            idx (int): The index of the point cloud to retrieve.
        Returns:
            tuple[np.ndarray, np.ndarray]: A tuple containing the point cloud
                (N, 4) and the global pose (4, 4).
        Raises:
            IndexError: If the index is out of range.
        """
        if idx < 0 or idx >= len(self):
            raise IndexError("Index out of range")

        # 读取点云
        lidar_path = self.lidar_files[idx]
        cld = read_lidar(lidar_path)  # (N, 4)
        mtx = np.eye(4)
        if self._frame_id == FrameID.BASE_LINK:
            mtx = self.Tr
        elif self._frame_id == FrameID.MAP_KITTI:
            mtx = self.global_poses[idx] @ mtx
        elif self._frame_id == FrameID.MAP_FLU:
            mtx = self.Tb @ self.global_poses[idx] @ self.Tr
        else:
            raise ValueError(f"Unsupported frame_id: {self._frame_id.name}")
        cld_t = transform_point_cloud(cld[:, :3], mtx)  # (N, 4)
        return np.hstack((cld_t, cld[:, 3:4])), mtx

    @overload
    def __getitem__(self, idx: int) -> tuple[np.ndarray, np.ndarray]:
        """
        Returns the LiDAR point cloud and transformation matrix for a single index.
        Args:
            idx (int): The index of the LiDAR data to retrieve.
        Returns:
            tuple[np.ndarray, np.ndarray]: A tuple containing the point cloud and transformation matrix.
        """
        ...

    @overload
    def __getitem__(self, idx: slice) -> list[tuple[np.ndarray, np.ndarray]]:
        """
        Returns the LiDAR point clouds and transformation matrices for a slice of indices.
        Args:
            idx (slice): A slice object specifying the range of indices to retrieve.
        Returns:
            Iterator[tuple[np.ndarray, np.ndarray]]: An iterator of tuples, each containing a point cloud and transformation matrix.
        """
        ...

    @overload
    def __getitem__(self, idx: np.ndarray) -> list[tuple[np.ndarray, np.ndarray]]:
        """
        Returns the LiDAR point clouds and transformation matrices for an array of indices.
        Args:
            idx (np.ndarray): A numpy array of indices to retrieve.
        Returns:
            Iterator[tuple[np.ndarray, np.ndarray]]: An iterator of tuples, each containing a point cloud and transformation matrix.
        """
        ...

    def __getitem__(
        self, idx: int | slice | np.ndarray
    ) -> tuple[np.ndarray, np.ndarray] | list[tuple[np.ndarray, np.ndarray]]:
        if isinstance(idx, int):
            ret = self.__get_one(idx)
        elif isinstance(idx, slice):
            start, stop, step = idx.indices(self._length)
            ret = list(map(self.__get_one, range(start, stop, step)))
        elif isinstance(idx, np.ndarray):
            if idx.dtype == np.int_:
                ret = list(map(self.__get_one, idx))
            else:
                raise TypeError("Index array must be of integer type.")
        else:
            raise TypeError(
                "Index must be an integer, slice, or numpy array of integers."
            )
        return ret

    def __iter__(self) -> Iterator[tuple[np.ndarray, np.ndarray]]:
        return map(self.__get_one, range(len(self)))
