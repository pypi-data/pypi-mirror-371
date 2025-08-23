# %%
import numpy as np
import os
from typing import Iterator, overload
from .basic import (
    read_lidar,
    load_calib_matrix,
    get_lidar_stamps,
    load_global_poses,
    interpolate_pose,
    transform_point_cloud,
)


VLP_LEFT_DIR = "sensor_data/VLP_left"
VLP_LEFT_STAMP_PATH = "sensor_data/VLP_left_stamp.csv"
CLB_VLP_LEFT_PATH = "calibration/Vehicle2LeftVLP.txt"

VLP_RIGHT_DIR = "sensor_data/VLP_right"
VLP_RIGHT_STAMP_PATH = "sensor_data/VLP_right_stamp.csv"
CLB_VLP_RIGHT_PATH = "calibration/Vehicle2RightVLP.txt"

GLOBAL_POSE_PATH = "global_pose.csv"

FRAME_ID_CHOICES = [
    "base_link",
    "map",
    "world",
]


class KaistPointCloudLoader:
    def __init__(self, base_dir: str, frame_id: str = "base_link"):
        """
        Initializes the KaistPointCloudLoader.
        Args:
            base_dir (str): The base directory where the data is stored. eg: '/kaist/campus00'
            frame_id (str): The default frame ID to use for loading data. Must be one of FRAME_ID_CHOICES.
        Raises:
            AssertionError: If the frame_id is not in FRAME_ID_CHOICES.
        """
        assert frame_id in FRAME_ID_CHOICES, f"Invalid frame_id: {frame_id}"
        self.base_dir = base_dir
        self._frame_id = frame_id
        # self.llidar_stamps = np.loadtxt(
        #     os.path.join(base_dir, VLP_LEFT_STAMP_PATH), dtype=int
        # )
        # self.rlidar_stamps = np.loadtxt(
        #     os.path.join(base_dir, VLP_RIGHT_STAMP_PATH), dtype=int
        # )
        self.llidar_stamps = get_lidar_stamps(os.path.join(base_dir, VLP_LEFT_DIR))
        self.rlidar_stamps = get_lidar_stamps(os.path.join(base_dir, VLP_RIGHT_DIR))
        self.T_llidar_vehicle = load_calib_matrix(
            os.path.join(base_dir, CLB_VLP_LEFT_PATH)
        )
        self.T_rlidar_vehicle = load_calib_matrix(
            os.path.join(base_dir, CLB_VLP_RIGHT_PATH)
        )
        self._gstamps, self._gposes = load_global_poses(
            os.path.join(base_dir, GLOBAL_POSE_PATH)
        )

        # 合并左、右LiDAR的时间戳和来源
        self.lidar_stamps = np.concatenate((self.llidar_stamps, self.rlidar_stamps))
        self.lidar_stamps_source = np.concatenate(
            (
                np.zeros_like(self.llidar_stamps),
                np.ones_like(self.rlidar_stamps),
            )
        )
        sorted_indices = np.argsort(self.lidar_stamps)
        self.lidar_stamps = self.lidar_stamps[sorted_indices]
        self.lidar_stamps_source = self.lidar_stamps_source[sorted_indices]

        # 车辆初始位置，用于转换到map坐标系
        pose0 = interpolate_pose(self.llidar_stamps[0], self._gstamps, self._gposes)
        self.T_world_pose0 = np.linalg.inv(pose0)

        # 迭代器用的状态量
        self._current_index = 0
        self._length = len(self.lidar_stamps)

    @property
    def frame_id(self):
        """
        Getter for the frame_id property.
        Returns:
            str: The current frame ID.
        """
        return self._frame_id

    @frame_id.setter
    def frame_id(self, new_id: str):
        """
        Setter for the frame_id property.
        Args:
            new_id (str): The new frame ID to set. Must be one of FRAME_ID_CHOICES.
        Raises:
            AssertionError: If the new_id is not in FRAME_ID_CHOICES.
        """
        assert new_id in FRAME_ID_CHOICES, f"Invalid frame_id: {new_id}"
        self._frame_id = new_id

    @property
    def global_stamps(self) -> np.ndarray:
        """
        Returns the global timestamps of the LiDAR data.
        Returns:
            np.ndarray: A numpy array of shape (N,) containing the global timestamps.
        """
        return self.lidar_stamps

    @property
    def global_poses(self) -> np.ndarray:
        """
        Returns the global poses corresponding to the LiDAR data.
        Returns:
            np.ndarray: A numpy array of shape (N, 4, 4) containing the global poses.
        """
        return self._gposes

    def __len__(self) -> int:
        """
        Returns the number of LiDAR point clouds available.
        Returns:
            int: The number of LiDAR point clouds.
        """
        return self._length

    def __get_one(self, idx: int) -> tuple[np.ndarray, np.ndarray]:
        """
        Returns the LiDAR point cloud for a given index.
        Args:
            idx (int): The index of the LiDAR data to retrieve.
        Returns:
            np.ndarray: A numpy array of shape (N, 4) containing the LiDAR points.
        Raises:
            IndexError: If the index is out of bounds.
        """
        if idx < 0 or idx >= self._length:
            raise IndexError("Index out of bounds.")
        stamp = self.lidar_stamps[idx]
        lidar_source = self.lidar_stamps_source[idx]
        base_dir = os.path.join(
            self.base_dir, VLP_LEFT_DIR if lidar_source == 0 else VLP_RIGHT_DIR
        )
        cld = read_lidar(stamp, base_dir)
        mtx = self.T_llidar_vehicle if lidar_source == 0 else self.T_rlidar_vehicle
        if self._frame_id in ["map", "world"]:
            pose = interpolate_pose(stamp, self._gstamps, self._gposes)
            mtx = pose @ mtx
            mtx = (self.T_world_pose0 if self._frame_id == "map" else np.eye(4)) @ mtx
        elif self._frame_id != "base_link":
            raise NotImplementedError(f"Not implemented {self._frame_id}")

        cld_t = transform_point_cloud(cld[:, :3], mtx)
        # Add intensity back to the point cloud
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
    def __getitem__(self, idx: slice) -> Iterator[tuple[np.ndarray, np.ndarray]]:
        """
        Returns the LiDAR point clouds and transformation matrices for a slice of indices.
        Args:
            idx (slice): A slice object specifying the range of indices to retrieve.
        Returns:
            Iterator[tuple[np.ndarray, np.ndarray]]: An iterator of tuples, each containing a point cloud and transformation matrix.
        """
        ...

    @overload
    def __getitem__(self, idx: np.ndarray) -> Iterator[tuple[np.ndarray, np.ndarray]]:
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
    ) -> tuple[np.ndarray, np.ndarray] | Iterator[tuple[np.ndarray, np.ndarray]]:
        if isinstance(idx, int):
            return self.__get_one(idx)
        elif isinstance(idx, slice):
            start, stop, step = idx.indices(self._length)
            return map(self.__get_one, range(start, stop, step))
        elif isinstance(idx, np.ndarray):
            if idx.dtype == np.int_:
                return map(self.__get_one, idx)
            else:
                raise TypeError("Index array must be of integer type.")
        else:
            raise TypeError(
                "Index must be an integer, slice, or numpy array of integers."
            )

    def __iter__(self):
        """
        Returns an iterator over the timestamps of the left LiDAR data.
        Yields:
            int: The timestamp of each left LiDAR point cloud.
        """
        return self

    def __next__(self):
        """
        Returns the next timestamp of the left LiDAR data.
        Raises:
            StopIteration: If there are no more timestamps to return.
        Returns:
            int: The next timestamp of the left LiDAR point cloud.
        """
        if self._current_index >= self._length:
            raise StopIteration
        ret = self.__get_one(self._current_index)
        self._current_index += 1
        return ret
