"""实用工具函数模块"""

import numpy as np
from typing import List, Tuple, Optional
import functools

# 导入日志系统
from .logging_config import get_logger

# 获取工具模块的日志记录器
_logger = get_logger("freebSEngine.utils")

from . import (
    GRAVITATIONAL_CONSTANT,
    ASTRONOMICAL_UNIT,
    SOLAR_MASS,
    EARTH_MASS,
)

def au_to_meters(au: float) -> float:
    """天文单位转换为米
    
    Args:
        au: 天文单位值
        
    Returns:
        米值
    """
    return au * ASTRONOMICAL_UNIT

def meters_to_au(meters: float) -> float:
    """米转换为天文单位
    
    Args:
        meters: 米值
        
    Returns:
        天文单位值
    """
    return meters / ASTRONOMICAL_UNIT

def solar_mass_to_kg(solar_masses: float) -> float:
    """太阳质量转换为千克
    
    Args:
        solar_masses: 太阳质量值
        
    Returns:
        千克值
    """
    return solar_masses * SOLAR_MASS

def kg_to_solar_mass(kg: float) -> float:
    """千克转换为太阳质量
    
    Args:
        kg: 千克值
        
    Returns:
        太阳质量值
    """
    return kg / SOLAR_MASS

def earth_mass_to_kg(earth_masses: float) -> float:
    """地球质量转换为千克
    
    Args:
        earth_masses: 地球质量值
        
    Returns:
        千克值
    """
    return earth_masses * EARTH_MASS

def kg_to_earth_mass(kg: float) -> float:
    """千克转换为地球质量
    
    Args:
        kg: 千克值
        
    Returns:
        地球质量值
    """
    return kg / EARTH_MASS

def days_to_seconds(days: float) -> float:
    """天数转换为秒
    
    Args:
        days: 天数
        
    Returns:
        秒数
    """
    return days * 24 * 3600

def seconds_to_days(seconds: float) -> float:
    """秒转换为天数
    
    Args:
        seconds: 秒数
        
    Returns:
        天数
    """
    return seconds / (24 * 3600)

def years_to_seconds(years: float) -> float:
    """年转换为秒
    
    Args:
        years: 年数
        
    Returns:
        秒数
    """
    return years * 365.25 * 24 * 3600

def seconds_to_years(seconds: float) -> float:
    """秒转换为年
    
    Args:
        seconds: 秒数
        
    Returns:
        年数
    """
    return seconds / (365.25 * 24 * 3600)

def calculate_gravitational_parameter(mass: float) -> float:
    """计算引力参数 μ = G * M
    
    Args:
        mass: 中心天体质量（千克）
        
    Returns:
        引力参数 μ (m³/s²)
    """
    return GRAVITATIONAL_CONSTANT * mass

def sphere_of_influence(primary_mass: float, secondary_mass: float, distance: float) -> float:
    """计算希尔球半径（影响球半径）
    
    Args:
        primary_mass: 主天体质量（千克）
        secondary_mass: 次天体质量（千克）
        distance: 两天体间距离（米）
        
    Returns:
        希尔球半径（米）
    """
    return distance * (secondary_mass / (3 * primary_mass)) ** (1/3)

def orbital_energy(semi_major_axis: float, mu: float) -> float:
    """计算轨道比机械能
    
    Args:
        semi_major_axis: 半长轴（米）
        mu: 引力参数（m³/s²）
        
    Returns:
        比机械能 (J/kg)
    """
    return -mu / (2 * semi_major_axis)

def vis_viva_equation(r: float, a: float, mu: float) -> float:
    """使用活力公式计算轨道速度
    
    Args:
        r: 当前位置距离（米）
        a: 半长轴（米）
        mu: 引力参数（m³/s²）
        
    Returns:
        轨道速度（米/秒）
    """
    return np.sqrt(mu * (2/r - 1/a))

def orbital_elements_to_cartesian(
    a: float,      # 半长轴 (m)
    e: float,      # 偏心率
    i: float,      # 倾角 (度)
    raan: float,   # 升交点赤经 (度)
    argp: float,   # 近地点幅角 (度)
    nu: float,     # 真近点角 (度)
    mu: float,     # 引力参数
) -> Tuple[np.ndarray, np.ndarray]:
    """将开普勒轨道根数转换为笛卡尔坐标
    
    Args:
        a: 半长轴 (米)
        e: 偏心率
        i: 倾角 (度)
        raan: 升交点赤经 (度)
        argp: 近地点幅角 (度)
        nu: 真近点角 (度)
        mu: 引力参数 (m³/s²)
        
    Returns:
        (位置向量, 速度向量)
    """
    # 转换为弧度
    i_rad = np.deg2rad(i)
    raan_rad = np.deg2rad(raan)
    argp_rad = np.deg2rad(argp)
    nu_rad = np.deg2rad(nu)
    
    # 计算轨道参数
    p = a * (1 - e**2)  # 半通径
    r = p / (1 + e * np.cos(nu_rad))  # 距离
    
    # 位置在轨道平面内
    x_orb = r * np.cos(nu_rad)
    y_orb = r * np.sin(nu_rad)
    
    # 速度在轨道平面内
    h = np.sqrt(mu * p)  # 比角动量
    vx_orb = -mu/h * np.sin(nu_rad)
    vy_orb = mu/h * (e + np.cos(nu_rad))
    
    # 旋转到惯性系
    # 旋转矩阵: R = R_z(-Ω) * R_x(-i) * R_z(-ω)
    
    # 位置旋转
    x = (np.cos(raan_rad) * np.cos(argp_rad + nu_rad) - 
         np.sin(raan_rad) * np.sin(argp_rad + nu_rad) * np.cos(i_rad)) * r
    y = (np.sin(raan_rad) * np.cos(argp_rad + nu_rad) + 
         np.cos(raan_rad) * np.sin(argp_rad + nu_rad) * np.cos(i_rad)) * r
    z = np.sin(argp_rad + nu_rad) * np.sin(i_rad) * r
    
    # 速度旋转（简化计算）
    vx = (np.cos(raan_rad) * (vx_orb * np.cos(argp_rad) - vy_orb * np.sin(argp_rad)) -
          np.sin(raan_rad) * np.cos(i_rad) * (vx_orb * np.sin(argp_rad) + vy_orb * np.cos(argp_rad)))
    vy = (np.sin(raan_rad) * (vx_orb * np.cos(argp_rad) - vy_orb * np.sin(argp_rad)) +
          np.cos(raan_rad) * np.cos(i_rad) * (vx_orb * np.sin(argp_rad) + vy_orb * np.cos(argp_rad)))
    vz = np.sin(i_rad) * (vx_orb * np.sin(argp_rad) + vy_orb * np.cos(argp_rad))
    
    position = np.array([x, y, z])
    velocity = np.array([vx, vy, vz])
    
    return position, velocity

def calculate_orbital_plane_normal(r: np.ndarray, v: np.ndarray) -> np.ndarray:
    """计算轨道平面法向量（角动量方向）
    
    Args:
        r: 位置向量
        v: 速度向量
        
    Returns:
        轨道平面法向量（单位向量）
    """
    h = np.cross(r, v)  # 比角动量
    return h / np.linalg.norm(h)

def calculate_true_anomaly(r: np.ndarray, v: np.ndarray, mu: float) -> float:
    """计算真近点角
    
    Args:
        r: 位置向量
        v: 速度向量
        mu: 引力参数
        
    Returns:
        真近点角（度）
    """
    r_norm = np.linalg.norm(r)
    v_norm = np.linalg.norm(v)
    
    # 比机械能
    energy = v_norm**2 / 2 - mu / r_norm
    
    # 半长轴
    a = -mu / (2 * energy)
    
    # 偏心率向量
    e_vec = ((v_norm**2 - mu/r_norm) * r - np.dot(r, v) * v) / mu
    e = np.linalg.norm(e_vec)
    
    # 真近点角
    cos_nu = np.dot(e_vec, r) / (e * r_norm)
    nu = np.arccos(np.clip(cos_nu, -1, 1))
    
    # 调整象限
    if np.dot(r, v) < 0:
        nu = 2 * np.pi - nu
    
    return np.rad2deg(nu)