"""
引力计算模块
基于牛顿万有引力定律计算物体间的引力
"""
import numpy as np
from typing import List, Tuple, Dict, Any
from entities.entity import Entity, Object


G = 6.67430e-11  # 万有引力常数 (m³ kg⁻¹ s⁻²)


def calculate_gravitational_force(entity1: Entity, entity2: Entity) -> np.ndarray:
    """
    计算两个实体之间的引力
    
    Args:
        entity1: 第一个实体
        entity2: 第二个实体
        
    Returns:
        作用在entity1上的引力向量 (N)
    """
    # 计算距离
    r_vec = entity2.position - entity1.position
    r = np.linalg.norm(r_vec)
    
    # 避免除以零
    if r == 0:
        return np.zeros(2)
    
    # 计算引力大小 F = G * m1 * m2 / r²
    force_magnitude = G * entity1.mass * entity2.mass / (r ** 2)
    
    # 计算方向 (单位向量)
    direction = r_vec / r
    
    return force_magnitude * direction


def calculate_gravitational_force_on_object(obj: Object, entity: Entity) -> np.ndarray:
    """
    计算实体对对象的引力
    
    Args:
        obj: 对象
        entity: 实体
        
    Returns:
        作用在对象上的引力向量 (N)
    """
    # 假设对象有质量（从属性中获取，默认为1kg）
    obj_mass = obj.attributes.get('mass', 1.0)
    
    # 计算距离
    r_vec = entity.position - obj.position
    r = np.linalg.norm(r_vec)
    
    if r == 0:
        return np.zeros(2)
    
    # 计算引力大小
    force_magnitude = G * obj_mass * entity.mass / (r ** 2)
    
    # 方向
    direction = r_vec / r
    
    return force_magnitude * direction


def calculate_total_force_on_object(obj: Object, entities: List[Entity]) -> np.ndarray:
    """
    计算所有实体对对象的总引力
    
    Args:
        obj: 对象
        entities: 实体列表
        
    Returns:
        总引力向量 (N)
    """
    total_force = np.zeros(2)
    
    for entity in entities:
        force = calculate_gravitational_force_on_object(obj, entity)
        total_force += force
    
    return total_force


def calculate_total_forces_between_entities(entities: List[Entity]) -> Dict[str, np.ndarray]:
    """
    计算所有实体之间的相互引力
    
    Args:
        entities: 实体列表
        
    Returns:
        字典：实体ID -> 作用在该实体上的总引力
    """
    n = len(entities)
    forces = {entity.id: np.zeros(2) for entity in entities}
    
    # 计算所有实体对之间的引力
    for i in range(n):
        for j in range(i + 1, n):
            entity_i = entities[i]
            entity_j = entities[j]
            
            # 计算i对j的引力
            force_on_j = calculate_gravitational_force(entity_i, entity_j)
            # j对i的引力大小相等方向相反
            force_on_i = -force_on_j
            
            forces[entity_i.id] += force_on_i
            forces[entity_j.id] += force_on_j
    
    return forces


def calculate_acceleration_from_force(force: np.ndarray, mass: float) -> np.ndarray:
    """
    根据力和质量计算加速度 a = F / m
    
    Args:
        force: 力向量 (N)
        mass: 质量 (kg)
        
    Returns:
        加速度向量 (m/s²)
    """
    if mass == 0:
        return np.zeros(2)
    return force / mass


def predict_orbit(obj: Object, entities: List[Entity], 
                  dt: float, steps: int = 1000) -> List[np.ndarray]:
    """
    预测对象的轨道（假设无机动）
    
    Args:
        obj: 对象
        entities: 实体列表
        dt: 时间步长 (s)
        steps: 预测步数
        
    Returns:
        预测的位置列表
    """
    # 创建对象的副本用于模拟
    sim_obj = obj.copy()
    positions = [sim_obj.position.copy()]
    
    for _ in range(steps):
        # 计算总引力
        total_force = calculate_total_force_on_object(sim_obj, entities)
        
        # 计算加速度
        obj_mass = sim_obj.attributes.get('mass', 1.0)
        acceleration = calculate_acceleration_from_force(total_force, obj_mass)
        
        # 更新位置和速度
        sim_obj.update_position(acceleration, dt)
        positions.append(sim_obj.position.copy())
    
    return positions


def calculate_orbital_parameters(obj: Object, primary: Entity) -> Dict[str, Any]:
    """
    计算对象相对于主天体的轨道参数
    
    Args:
        obj: 对象
        primary: 主天体（如恒星、行星）
        
    Returns:
        轨道参数字典
    """
    # 相对位置和速度
    r_vec = obj.position - primary.position
    v_vec = obj.velocity - primary.velocity
    
    r = np.linalg.norm(r_vec)
    v = np.linalg.norm(v_vec)
    
    # 标准引力参数 μ = G * M
    mu = G * primary.mass
    
    # 比角动量 h = r × v
    h_vec = np.cross(np.append(r_vec, 0), np.append(v_vec, 0))
    h = np.linalg.norm(h_vec)
    
    # 轨道能量 ε = v²/2 - μ/r
    epsilon = v ** 2 / 2 - mu / r
    
    # 半长轴 a = -μ/(2ε) （如果ε < 0则为椭圆）
    if epsilon != 0:
        a = -mu / (2 * epsilon)
    else:
        a = float('inf')
    
    # 偏心率 e = sqrt(1 + 2εh²/μ²)
    e = np.sqrt(1 + 2 * epsilon * h ** 2 / mu ** 2)
    
    # 轨道周期 T = 2π√(a³/μ) （如果是椭圆）
    if epsilon < 0 and a > 0:
        T = 2 * np.pi * np.sqrt(a ** 3 / mu)
    else:
        T = float('inf')
    
    return {
        'semi_major_axis': a,
        'eccentricity': e,
        'orbital_energy': epsilon,
        'specific_angular_momentum': h,
        'orbital_period': T,
        'distance': r,
        'speed': v
    }