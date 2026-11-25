"""公共地理计算模块：Haversine 球面距离（公里）

供 01_extract_tea.py 与 04_robustness.py 共用，消除重复实现。
输入支持标量或 numpy 数组（向量化），输出与输入同形。
"""
import numpy as np

EARTH_RADIUS_KM = 6371.0


def haversine_matrix(lat1, lon1, lat2, lon2):
    """向量化 Haversine 球面距离（公里）。

    lat/lon 单位为度；可为标量或形状相同的数组，返回同形距离数组。
    """
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_KM * np.arcsin(np.sqrt(a))
