import numpy as np
import os
from scipy.spatial.transform import Rotation as R
from scipy.spatial.transform import Slerp


def get_lidar_stamps(base_path: str) -> np.ndarray:
    bins = os.listdir(base_path)
    stamps = [int(os.path.splitext(bn)[0]) for bn in bins if bn.endswith(".bin")]
    stamps = np.array(sorted(stamps), dtype=int)
    return stamps


def read_lidar(stamp: int, base_path: str) -> np.ndarray:
    """
    Reads a LiDAR point cloud from a binary file.
    Args:
        stamp (int): The timestamp of the LiDAR data.
        base_path (str): The directory where the LiDAR files are stored.
    Returns:
        np.ndarray: A numpy array of shape (N, 4) containing the LiDAR points.
    The points are in the format [x, y, z, intensity].
    """
    bin_file = os.path.join(base_path, f"{stamp}.bin")
    assert os.path.exists(bin_file), f"LiDAR file {bin_file} does not exist."
    return np.fromfile(bin_file, dtype=np.float32).reshape(-1, 4)


def load_calib_matrix(calib_file: str) -> np.ndarray:
    """
    Loads a calibration matrix from a file.
    Args:
        calib_file (str): The path to the calibration file.
    Returns:
        np.ndarray: A 4x4 numpy array representing the calibration matrix.
    """
    assert os.path.exists(calib_file), f"Calibration file {calib_file} does not exist."
    rstr, tstr = open(calib_file, "r").readlines()[-2:]
    r = np.fromstring(rstr.split(":")[-1].strip(), sep=" ").reshape(3, 3)
    t = np.fromstring(tstr.split(":")[-1].strip(), sep=" ").reshape(3, 1)
    rt = np.eye(4)
    rt[:3, :3] = r
    rt[:3, 3:] = t
    return rt


def load_global_poses(pose_file: str) -> tuple[np.ndarray, np.ndarray]:
    """
    Loads global poses from a CSV file.
    Args:
        pose_file (str): The path to the pose file.
    Returns:
        tuple: A tuple containing:
            - np.ndarray: An array of timestamps shape (N,).
            - np.ndarray: An array of pose matrices of shape (N, 4, 4).
    """
    assert os.path.exists(pose_file), f"Pose file {pose_file} does not exist."
    contents = np.loadtxt(
        pose_file, dtype=[("stamp", "S20"), ("mtx", "12f8")], delimiter=","
    )
    stamps = np.array([int(stamp.decode("utf-8")) for stamp in contents["stamp"]])
    poses = np.array([mtx.reshape(3, 4) for mtx in contents["mtx"]])
    assert (
        stamps.shape[0] == poses.shape[0]
    ), "Mismatch between number of stamps and poses."
    assert (
        poses.shape[1] == 3 and poses.shape[2] == 4
    ), "Pose matrices should be of shape (N, 4, 3)."
    # Convert to homogeneous coordinates
    poses_homogeneous = []
    for i in range(poses.shape[0]):
        ph = np.eye(4)
        ph[:3] = poses[i]
        poses_homogeneous.append(ph)
    poses = np.array(poses_homogeneous)
    return stamps, poses


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


def interpolate_pose(stamp: int, gstamps: np.ndarray, gposes: np.ndarray) -> np.ndarray:
    """
    Interpolates the pose for a given timestamp using linear interpolation.
    Args:
        stamp (int): The timestamp for which to interpolate the pose.
    Returns:
        np.ndarray: A 4x4 numpy array representing the interpolated pose.
    """
    idx = np.searchsorted(gstamps, stamp, side="left")
    up_bound = np.clip(idx, 0, len(gstamps) - 1)
    low_bound = np.clip(idx - 1, 0, len(gstamps) - 1)

    if up_bound == low_bound:
        return gposes[up_bound]

    t_up = gstamps[up_bound]
    t_low = gstamps[low_bound]
    alpha = (stamp - t_low) / (t_up - t_low)

    pose_low = gposes[low_bound]
    pose_up = gposes[up_bound]

    # Linear interpolation
    translation = (1 - alpha) * pose_low[:3, 3] + alpha * pose_up[:3, 3]
    rotations = R.from_matrix([pose_low[:3, :3], pose_up[:3, :3]])
    slerp = Slerp([0, 1], rotations)
    rotation_interp = slerp(alpha)
    pose_interp = np.eye(4)
    pose_interp[:3, :3] = rotation_interp.as_matrix()
    pose_interp[:3, 3] = translation
    return pose_interp