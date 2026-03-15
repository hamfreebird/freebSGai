"""天体对象定义模块

包含太阳系主要天体的物理参数和轨道数据。
"""

import numpy as np
from dataclasses import dataclass
from typing import Dict, Optional
from . import (
    GRAVITATIONAL_CONSTANT,
    ASTRONOMICAL_UNIT,
    SOLAR_MASS,
    EARTH_MASS,
)

@dataclass
class CelestialBody:
    """天体对象类"""
    name: str
    mass: float  # 千克
    radius: float  # 米
    color: tuple  # RGB颜色
    orbital_period: Optional[float] = None  # 轨道周期（秒）
    semi_major_axis: Optional[float] = None  # 半长轴（米）
    eccentricity: Optional[float] = None  # 偏心率
    inclination: Optional[float] = None  # 倾角（度）
    
    @property
    def gravitational_parameter(self) -> float:
        """引力参数 μ = G * M"""
        return GRAVITATIONAL_CONSTANT * self.mass
    
    @property
    def surface_gravity(self) -> float:
        """表面重力加速度 (m/s²)"""
        return GRAVITATIONAL_CONSTANT * self.mass / (self.radius ** 2)
    
    @property
    def escape_velocity(self) -> float:
        """逃逸速度 (m/s)"""
        return np.sqrt(2 * GRAVITATIONAL_CONSTANT * self.mass / self.radius)
    
    @property
    def density(self) -> float:
        """平均密度 (kg/m³)"""
        volume = (4/3) * np.pi * self.radius ** 3
        return self.mass / volume

# 太阳系天体数据
SUN = CelestialBody(
    name="Sun",
    mass=1.98847e30,  # 千克
    radius=6.957e8,   # 米
    color=(1.0, 0.8, 0.2),  # 黄色
)

MERCURY = CelestialBody(
    name="Mercury",
    mass=3.3011e23,   # 千克
    radius=2.4397e6,  # 米
    color=(0.7, 0.7, 0.7),  # 灰色
    orbital_period=87.969 * 24 * 3600,  # 天转换为秒
    semi_major_axis=0.3871 * ASTRONOMICAL_UNIT,
    eccentricity=0.2056,
    inclination=7.005,
)

VENUS = CelestialBody(
    name="Venus",
    mass=4.8675e24,   # 千克
    radius=6.0518e6,  # 米
    color=(0.9, 0.7, 0.3),  # 橙黄色
    orbital_period=224.701 * 24 * 3600,
    semi_major_axis=0.7233 * ASTRONOMICAL_UNIT,
    eccentricity=0.0068,
    inclination=3.3946,
)

EARTH = CelestialBody(
    name="Earth",
    mass=5.9722e24,   # 千克
    radius=6.371e6,   # 米
    color=(0.2, 0.4, 0.8),  # 蓝色
    orbital_period=365.256 * 24 * 3600,
    semi_major_axis=1.0 * ASTRONOMICAL_UNIT,
    eccentricity=0.0167,
    inclination=0.0,
)

MARS = CelestialBody(
    name="Mars",
    mass=6.4171e23,   # 千克
    radius=3.3895e6,  # 米
    color=(0.8, 0.3, 0.2),  # 红色
    orbital_period=686.98 * 24 * 3600,
    semi_major_axis=1.5237 * ASTRONOMICAL_UNIT,
    eccentricity=0.0934,
    inclination=1.850,
)

JUPITER = CelestialBody(
    name="Jupiter",
    mass=1.8982e27,   # 千克
    radius=6.9911e7,  # 米
    color=(0.8, 0.6, 0.4),  # 棕色
    orbital_period=4332.59 * 24 * 3600,
    semi_major_axis=5.2028 * ASTRONOMICAL_UNIT,
    eccentricity=0.0489,
    inclination=1.303,
)

SATURN = CelestialBody(
    name="Saturn",
    mass=5.6834e26,   # 千克
    radius=5.8232e7,  # 米
    color=(0.9, 0.8, 0.5),  # 浅黄色
    orbital_period=10759.22 * 24 * 3600,
    semi_major_axis=9.5388 * ASTRONOMICAL_UNIT,
    eccentricity=0.0565,
    inclination=2.485,
)

URANUS = CelestialBody(
    name="Uranus",
    mass=8.6810e25,   # 千克
    radius=2.5362e7,  # 米
    color=(0.6, 0.8, 0.9),  # 浅蓝色
    orbital_period=30688.5 * 24 * 3600,
    semi_major_axis=19.1914 * ASTRONOMICAL_UNIT,
    eccentricity=0.0461,
    inclination=0.772,
)

NEPTUNE = CelestialBody(
    name="Neptune",
    mass=1.02413e26,  # 千克
    radius=2.4622e7,  # 米
    color=(0.3, 0.5, 0.8),  # 深蓝色
    orbital_period=60182 * 24 * 3600,
    semi_major_axis=30.0611 * ASTRONOMICAL_UNIT,
    eccentricity=0.0097,
    inclination=1.769,
)

PLUTO = CelestialBody(
    name="Pluto",
    mass=1.303e22,    # 千克
    radius=1.1883e6,  # 米
    color=(0.7, 0.5, 0.3),  # 棕色
    orbital_period=90560 * 24 * 3600,
    semi_major_axis=39.482 * ASTRONOMICAL_UNIT,
    eccentricity=0.2488,
    inclination=17.16,
)

MOON = CelestialBody(
    name="Moon",
    mass=7.342e22,    # 千克
    radius=1.7374e6,  # 米
    color=(0.8, 0.8, 0.8),  # 浅灰色
    orbital_period=27.3217 * 24 * 3600,  # 绕地球周期
    semi_major_axis=3.844e8,  # 地月距离
    eccentricity=0.0549,
    inclination=5.145,
)

# 天体数据库
CELESTIAL_BODIES: Dict[str, CelestialBody] = {
    body.name.lower(): body for body in [
        SUN, MERCURY, VENUS, EARTH, MARS, JUPITER,
        SATURN, URANUS, NEPTUNE, PLUTO, MOON
    ]
}

def get_body(name: str) -> CelestialBody:
    """获取指定名称的天体对象
    
    Args:
        name: 天体名称（不区分大小写）
        
    Returns:
        CelestialBody 对象
        
    Raises:
        ValueError: 如果找不到指定名称的天体
    """
    name_lower = name.lower()
    if name_lower not in CELESTIAL_BODIES:
        raise ValueError(f"Unknown celestial body: {name}. Available bodies: {list(CELESTIAL_BODIES.keys())}")
    return CELESTIAL_BODIES[name_lower]

def get_solar_system_bodies() -> Dict[str, CelestialBody]:
    """获取太阳系所有行星（包括太阳）
    
    Returns:
        天体名称到对象的映射
    """
    return CELESTIAL_BODIES.copy()

def calculate_orbital_velocity(body: CelestialBody, distance: float) -> float:
    """计算在指定距离处的圆形轨道速度
    
    Args:
        body: 中心天体
        distance: 距离中心天体的距离（米）
        
    Returns:
        圆形轨道速度（米/秒）
    """
    return np.sqrt(body.gravitational_parameter / distance)

def calculate_hill_sphere(body: CelestialBody, central_body: CelestialBody, distance: float) -> float:
    """计算天体的希尔球半径
    
    Args:
        body: 次天体
        central_body: 主天体
        distance: 两天体间距离（米）
        
    Returns:
        希尔球半径（米）
    """
    return distance * (body.mass / (3 * central_body.mass)) ** (1/3)

def create_solar_system_simulation() -> Dict[str, dict]:
    """创建太阳系模拟的初始条件
    
    Returns:
        包含每个天体初始位置和速度的字典
    """
    # 简化：假设所有行星都在圆形轨道上，且在同一平面上
    simulation = {}
    
    for name, body in CELESTIAL_BODIES.items():
        if body.semi_major_axis is not None:
            # 计算圆形轨道速度
            orbital_velocity = calculate_orbital_velocity(SUN, body.semi_major_axis)
            
            # 初始位置在x轴正方向，速度在y轴正方向
            initial_position = [body.semi_major_axis, 0.0, 0.0]
            initial_velocity = [0.0, orbital_velocity, 0.0]
            
            simulation[name] = {
                'body': body,
                'position': initial_position,
                'velocity': initial_velocity,
                'mass': body.mass,
            }
    
    return simulation

class OrbitalSimulation:
    """轨道模拟器类"""
    
    def __init__(self, central_body: CelestialBody):
        """
        Args:
            central_body: 中心天体
        """
        self.central_body = central_body
        self.orbiting_bodies = []
        
    def add_body(self, body: CelestialBody, position: list, velocity: list):
        """添加绕行天体
        
        Args:
            body: 绕行天体
            position: 初始位置向量 [x, y, z] (米)
            velocity: 初始速度向量 [vx, vy, vz] (米/秒)
        """
        self.orbiting_bodies.append({
            'body': body,
            'position': np.array(position, dtype=np.float64),
            'velocity': np.array(velocity, dtype=np.float64),
        })
        
    def calculate_orbital_elements(self, body_index: int) -> dict:
        """计算指定天体的轨道根数
        
        Args:
            body_index: 天体索引
            
        Returns:
            包含轨道根数的字典
        """
        body_data = self.orbiting_bodies[body_index]
        r = body_data['position']
        v = body_data['velocity']
        mu = self.central_body.gravitational_parameter
        
        # 计算比角动量
        h = np.cross(r, v)
        h_norm = np.linalg.norm(h)
        
        # 计算偏心率向量
        e_vec = np.cross(v, h) / mu - r / np.linalg.norm(r)
        e = np.linalg.norm(e_vec)
        
        # 计算半长轴
        energy = np.linalg.norm(v)**2 / 2 - mu / np.linalg.norm(r)
        a = -mu / (2 * energy) if energy < 0 else float('inf')
        
        # 计算倾角
        i = np.arccos(h[2] / h_norm)
        
        # 计算升交点赤经
        n = np.cross([0, 0, 1], h)
        n_norm = np.linalg.norm(n)
        if n_norm > 0:
            raan = np.arccos(n[0] / n_norm)
            if n[1] < 0:
                raan = 2 * np.pi - raan
        else:
            raan = 0.0
            
        # 计算近地点幅角
        if n_norm > 0 and e > 0:
            argp = np.arccos(np.dot(n, e_vec) / (n_norm * e))
            if e_vec[2] < 0:
                argp = 2 * np.pi - argp
        else:
            argp = 0.0
            
        # 计算真近点角
        if e > 0:
            nu = np.arccos(np.dot(e_vec, r) / (e * np.linalg.norm(r)))
            if np.dot(r, v) < 0:
                nu = 2 * np.pi - nu
        else:
            nu = 0.0
            
        return {
            'semi_major_axis': a,
            'eccentricity': e,
            'inclination': np.rad2deg(i),
            'right_ascension': np.rad2deg(raan),
            'argument_of_periapsis': np.rad2deg(argp),
            'true_anomaly': np.rad2deg(nu),
            'orbital_period': 2 * np.pi * np.sqrt(a**3 / mu) if a > 0 else float('inf'),
        }