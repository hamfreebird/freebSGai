"""
freebSEngine 纯 Python 备用实现模块

当 Rust 扩展不可用时，提供纯 Python 的实现。
性能较低，但功能完整。
"""

import math
from dataclasses import dataclass
from typing import List, Optional, Tuple

import numpy as np

# 导入常量（这些会在 __init__.py 中定义）
from . import (
    ASTRONOMICAL_UNIT,
    EARTH_MASS,
    GRAVITATIONAL_CONSTANT,
    SOLAR_MASS,
    SPEED_OF_LIGHT,
)


@dataclass
class OrbitState:
    """轨道状态"""

    position: np.ndarray  # 位置向量 [x, y, z]
    velocity: np.ndarray  # 速度向量 [vx, vy, vz]
    epoch: float  # 时间（Unix时间戳）

    @property
    def distance(self) -> float:
        """到原点的距离"""
        return np.linalg.norm(self.position)

    @property
    def speed(self) -> float:
        """速度大小"""
        return np.linalg.norm(self.velocity)


def propagate_orbit(
    r0: List[float],
    v0: List[float],
    epoch: float,
    step_seconds: float,
    num_steps: int,
) -> np.ndarray:
    """计算天体轨道位置（纯Python实现）

    Args:
        r0: 初始位置向量 [x, y, z] (米)
        v0: 初始速度向量 [vx, vy, vz] (米/秒)
        epoch: 起始时间（Unix时间戳）
        step_seconds: 时间步长（秒）
        num_steps: 步数

    Returns:
        numpy.ndarray: 形状为 (num_steps, 3) 的位置数组
    """
    # 转换为 numpy 数组
    r = np.array(r0, dtype=np.float64)
    v = np.array(v0, dtype=np.float64)

    # 假设中心天体是太阳（简化）
    mu = GRAVITATIONAL_CONSTANT * 1.98847e30  # 太阳引力参数

    # 存储所有位置
    positions = np.zeros((num_steps, 3), dtype=np.float64)

    # 使用简化的轨道传播（二体问题，使用开普勒方程）
    # 计算轨道根数
    h = np.cross(r, v)  # 比角动量
    h_norm = np.linalg.norm(h)

    # 偏心率向量
    e_vec = np.cross(v, h) / mu - r / np.linalg.norm(r)
    e = np.linalg.norm(e_vec)

    # 半长轴
    energy = np.linalg.norm(v) ** 2 / 2 - mu / np.linalg.norm(r)
    a = -mu / (2 * energy) if energy < 0 else float("inf")

    # 轨道周期
    if a > 0 and not np.isinf(a):
        period = 2 * math.pi * math.sqrt(a**3 / mu)
    else:
        period = float("inf")

    # 初始真近点角
    if e > 0:
        cos_nu = np.dot(e_vec, r) / (e * np.linalg.norm(r))
        nu0 = math.acos(max(-1, min(1, cos_nu)))
        if np.dot(r, v) < 0:
            nu0 = 2 * math.pi - nu0
    else:
        nu0 = 0.0

    # 对于每个时间步，计算位置
    for i in range(num_steps):
        t = i * step_seconds

        if period < float("inf"):
            # 椭圆轨道：使用平均近点角
            M = 2 * math.pi * t / period
            # 简化：假设小偏心率，直接使用平均近点角近似真近点角
            nu = nu0 + M
        else:
            # 双曲线或抛物线轨道：简化处理
            nu = nu0 + 0.01 * t  # 小角度变化

        # 计算位置（在轨道平面内）
        p = a * (1 - e**2) if not np.isinf(a) else h_norm**2 / mu
        r_current = p / (1 + e * math.cos(nu))

        # 轨道平面内的坐标
        x_orb = r_current * math.cos(nu)
        y_orb = r_current * math.sin(nu)

        # 简化：假设轨道在xy平面内
        positions[i] = [x_orb, y_orb, 0.0]

    return positions


def compute_keplerian_elements(
    r: List[float],
    v: List[float],
    epoch: float,
) -> np.ndarray:
    """计算开普勒轨道根数（纯Python实现）

    Args:
        r: 位置向量 [x, y, z] (米)
        v: 速度向量 [vx, vy, vz] (米/秒)
        epoch: 时间（Unix时间戳）

    Returns:
        numpy.ndarray: [a, e, i, Ω, ω, ν] 数组
                      (半长轴, 偏心率, 倾角, 升交点赤经, 近地点幅角, 真近点角)
    """
    r_vec = np.array(r, dtype=np.float64)
    v_vec = np.array(v, dtype=np.float64)

    # 假设中心天体是太阳
    mu = GRAVITATIONAL_CONSTANT * 1.98847e30

    # 计算比角动量
    h = np.cross(r_vec, v_vec)
    h_norm = np.linalg.norm(h)

    # 计算偏心率向量
    e_vec = np.cross(v_vec, h) / mu - r_vec / np.linalg.norm(r_vec)
    e = np.linalg.norm(e_vec)

    # 计算比机械能
    energy = np.linalg.norm(v_vec) ** 2 / 2 - mu / np.linalg.norm(r_vec)

    # 计算半长轴
    if energy < 0:
        a = -mu / (2 * energy)
    else:
        a = float("inf")

    # 计算倾角
    i = math.degrees(math.acos(h[2] / h_norm)) if h_norm > 0 else 0.0

    # 计算升交点赤经
    n = np.cross([0, 0, 1], h)
    n_norm = np.linalg.norm(n)
    if n_norm > 0:
        raan = math.degrees(math.acos(n[0] / n_norm))
        if n[1] < 0:
            raan = 360 - raan
    else:
        raan = 0.0

    # 计算近地点幅角
    if n_norm > 0 and e > 0:
        argp = math.degrees(math.acos(np.dot(n, e_vec) / (n_norm * e)))
        if e_vec[2] < 0:
            argp = 360 - argp
    else:
        argp = 0.0

    # 计算真近点角
    if e > 0:
        cos_nu = np.dot(e_vec, r_vec) / (e * np.linalg.norm(r_vec))
        nu = math.degrees(math.acos(max(-1, min(1, cos_nu))))
        if np.dot(r_vec, v_vec) < 0:
            nu = 360 - nu
    else:
        nu = 0.0

    # 返回所有元素
    return np.array([a, e, i, raan, argp, nu], dtype=np.float64)


def orbital_period(semi_major_axis: float, mu: float) -> float:
    """计算轨道周期（秒）

    Args:
        semi_major_axis: 半长轴（米）
        mu: 引力参数（m³/s²）

    Returns:
        轨道周期（秒）
    """
    if semi_major_axis <= 0:
        raise ValueError("半长轴必须为正数")
    if mu <= 0:
        raise ValueError("引力参数必须为正数")

    return 2 * math.pi * math.sqrt(semi_major_axis**3 / mu)


def nbody_simulation(
    positions: List[List[float]],
    velocities: List[List[float]],
    masses: List[float],
    epoch: float,
    dt: float,
    steps: int,
) -> np.ndarray:
    """运行 N 体模拟（纯Python实现）

    Args:
        positions: 初始位置列表 [[x1,y1,z1], [x2,y2,z2], ...]
        velocities: 初始速度列表
        masses: 质量列表
        epoch: 起始时间
        dt: 时间步长
        steps: 步数

    Returns:
        numpy.ndarray: 形状为 (steps, n_bodies, 3) 的位置数组
    """
    n = len(positions)

    # 转换为 numpy 数组
    pos = np.array(positions, dtype=np.float64)  # shape: (n, 3)
    vel = np.array(velocities, dtype=np.float64)  # shape: (n, 3)
    mass = np.array(masses, dtype=np.float64)  # shape: (n,)

    # 存储所有时间步的位置
    all_positions = np.zeros((steps, n, 3), dtype=np.float64)

    # 使用简化的N体模拟（使用 leapfrog 积分器）
    for step in range(steps):
        # 存储当前位置
        all_positions[step] = pos.copy()

        # 计算加速度
        acc = np.zeros((n, 3), dtype=np.float64)

        for i in range(n):
            for j in range(n):
                if i != j:
                    # 计算距离向量
                    r_vec = pos[j] - pos[i]
                    r = np.linalg.norm(r_vec)

                    if r > 0:
                        # 引力加速度
                        acc[i] += GRAVITATIONAL_CONSTANT * mass[j] * r_vec / r**3

        # 更新速度（半步）
        vel += acc * (dt / 2)

        # 更新位置
        pos += vel * dt

        # 重新计算加速度
        acc_new = np.zeros((n, 3), dtype=np.float64)
        for i in range(n):
            for j in range(n):
                if i != j:
                    r_vec = pos[j] - pos[i]
                    r = np.linalg.norm(r_vec)
                    if r > 0:
                        acc_new[i] += GRAVITATIONAL_CONSTANT * mass[j] * r_vec / r**3

        # 更新速度（另外半步）
        vel += acc_new * (dt / 2)

    return all_positions


def circular_orbit_velocity(radius: float, central_mass: float) -> float:
    """计算圆形轨道速度

    Args:
        radius: 轨道半径（米）
        central_mass: 中心天体质量（千克）

    Returns:
        圆形轨道速度（米/秒）
    """
    if radius <= 0:
        raise ValueError("半径必须为正数")
    if central_mass <= 0:
        raise ValueError("中心天体质量必须为正数")

    return math.sqrt(GRAVITATIONAL_CONSTANT * central_mass / radius)


def escape_velocity(radius: float, central_mass: float) -> float:
    """计算逃逸速度

    Args:
        radius: 距离中心天体的距离（米）
        central_mass: 中心天体质量（千克）

    Returns:
        逃逸速度（米/秒）
    """
    if radius <= 0:
        raise ValueError("半径必须为正数")
    if central_mass <= 0:
        raise ValueError("中心天体质量必须为正数")

    return math.sqrt(2 * GRAVITATIONAL_CONSTANT * central_mass / radius)


# 测试函数
def _test_functions():
    """测试所有函数"""
    print("测试纯Python备用实现...")

    # 测试常量
    print(f"G = {GRAVITATIONAL_CONSTANT:.3e}")
    print(f"c = {SPEED_OF_LIGHT:.3e}")
    print(f"AU = {ASTRONOMICAL_UNIT:.3e}")

    # 测试圆形轨道速度
    earth_radius = 6.371e6
    earth_mass = 5.9722e24
    v_circular = circular_orbit_velocity(earth_radius, earth_mass)
    print(f"地球表面圆形轨道速度: {v_circular / 1000:.2f} km/s")

    # 测试逃逸速度
    v_escape = escape_velocity(earth_radius, earth_mass)
    print(f"地球逃逸速度: {v_escape / 1000:.2f} km/s")

    # 测试轨道周期
    earth_orbit_radius = 1.496e11
    sun_mass = 1.98847e30
    mu = GRAVITATIONAL_CONSTANT * sun_mass
    period = orbital_period(earth_orbit_radius, mu)
    print(f"地球轨道周期: {period / (24 * 3600):.2f} 天")

    print("测试完成！")


if __name__ == "__main__":
    _test_functions()
