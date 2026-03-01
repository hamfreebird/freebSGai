"""
工具函数和辅助类
"""
import numpy as np
from typing import List, Tuple, Dict, Any, Optional
from entities.entity import Entity, Object


def create_star(mass: float = 1.989e30,  # 太阳质量
                position: Tuple[float, float] = (0, 0),
                velocity: Tuple[float, float] = (0, 0),
                name: str = "恒星") -> Entity:
    """创建恒星实体"""
    density = 1408  # 太阳平均密度 kg/m³
    return Entity(
        mass=mass,
        density=density,
        radius=6.957e8,  # 太阳半径
        position=np.array(position),
        velocity=np.array(velocity),
        color=(255, 255, 0),  # 黄色
        name=name
    )


def create_planet(mass: float = 5.972e24,  # 地球质量
                  distance: float = 1.496e11,  # 1 AU
                  orbital_speed: float = 29780,  # 地球轨道速度 m/s
                  name: str = "行星") -> Entity:
    """创建行星实体（在圆形轨道上）"""
    density = 5514  # 地球平均密度 kg/m³
    position = np.array([distance, 0])
    velocity = np.array([0, orbital_speed])
    
    return Entity(
        mass=mass,
        density=density,
        radius=6.371e6,  # 地球半径
        position=position,
        velocity=velocity,
        color=(0, 100, 200),  # 蓝色
        name=name
    )


def create_spaceship(position: Tuple[float, float] = (1.5e11, 0),
                     velocity: Tuple[float, float] = (0, 30000),
                     label: str = "飞船") -> Object:
    """创建飞船对象"""
    return Object(
        position=np.array(position),
        velocity=np.array(velocity),
        label=label,
        attributes={
            'mass': 1000.0,  # 1吨
            'fuel_mass': 500.0,
            'engine_efficiency': 0.8,
            'max_thrust': 10000.0
        },
        health=100.0,
        max_acceleration=10.0,
        remaining_dv=5000.0,
        weapon_range=10000.0,
        weapon_damage=20.0
    )


def create_asteroid(position: Tuple[float, float] = (2e11, 1e11),
                    velocity: Tuple[float, float] = (-5000, 0),
                    mass: float = 1e12,
                    density: float = 2000,
                    name: str = "小行星") -> Entity:
    """创建小行星实体"""
    radius = (3 * mass / (4 * np.pi * density)) ** (1/3)
    
    return Entity(
        mass=mass,
        density=density,
        radius=radius,
        position=np.array(position),
        velocity=np.array(velocity),
        color=(150, 150, 150),  # 灰色
        name=name
    )


def calculate_circular_orbit_speed(central_mass: float, 
                                  distance: float) -> float:
    """
    计算圆形轨道速度
    
    Args:
        central_mass: 中心天体质量 (kg)
        distance: 轨道半径 (m)
        
    Returns:
        轨道速度 (m/s)
    """
    G = 6.67430e-11
    return np.sqrt(G * central_mass / distance)


def calculate_escape_velocity(mass: float, radius: float) -> float:
    """
    计算逃逸速度
    
    Args:
        mass: 天体质量 (kg)
        radius: 天体半径 (m)
        
    Returns:
        逃逸速度 (m/s)
    """
    G = 6.67430e-11
    return np.sqrt(2 * G * mass / radius)


def calculate_orbital_period(semi_major_axis: float, 
                            central_mass: float) -> float:
    """
    计算轨道周期（开普勒第三定律）
    
    Args:
        semi_major_axis: 半长轴 (m)
        central_mass: 中心天体质量 (kg)
        
    Returns:
        轨道周期 (s)
    """
    G = 6.67430e-11
    return 2 * np.pi * np.sqrt(semi_major_axis ** 3 / (G * central_mass))


def interpolate_position(positions: List[np.ndarray], 
                        times: List[float],
                        target_time: float) -> np.ndarray:
    """
    插值计算位置
    
    Args:
        positions: 位置列表
        times: 时间列表
        target_time: 目标时间
        
    Returns:
        插值位置
    """
    if not positions or not times:
        return np.zeros(2)
    
    if target_time <= times[0]:
        return positions[0]
    if target_time >= times[-1]:
        return positions[-1]
    
    # 找到时间区间
    for i in range(len(times) - 1):
        if times[i] <= target_time <= times[i + 1]:
            t0, t1 = times[i], times[i + 1]
            p0, p1 = positions[i], positions[i + 1]
            
            # 线性插值
            alpha = (target_time - t0) / (t1 - t0)
            return p0 + alpha * (p1 - p0)
    
    return positions[-1]


def calculate_distance_matrix(positions: List[np.ndarray]) -> np.ndarray:
    """
    计算位置之间的距离矩阵
    
    Args:
        positions: 位置列表
        
    Returns:
        距离矩阵 (n x n)
    """
    n = len(positions)
    dist_matrix = np.zeros((n, n))
    
    for i in range(n):
        for j in range(i + 1, n):
            dist = np.linalg.norm(positions[i] - positions[j])
            dist_matrix[i, j] = dist
            dist_matrix[j, i] = dist
    
    return dist_matrix


def find_closest_object(target_position: np.ndarray,
                       objects: List[Object]) -> Optional[Tuple[Object, float]]:
    """
    找到距离目标位置最近的对象
    
    Args:
        target_position: 目标位置
        objects: 对象列表
        
    Returns:
        (最近的对象, 距离) 或 None
    """
    if not objects:
        return None
    
    closest_obj = None
    min_distance = float('inf')
    
    for obj in objects:
        distance = np.linalg.norm(obj.position - target_position)
        if distance < min_distance:
            min_distance = distance
            closest_obj = obj
    
    return closest_obj, min_distance


def find_closest_entity(target_position: np.ndarray,
                       entities: List[Entity]) -> Optional[Tuple[Entity, float]]:
    """
    找到距离目标位置最近的实体
    
    Args:
        target_position: 目标位置
        entities: 实体列表
        
    Returns:
        (最近的实体, 距离) 或 None
    """
    if not entities:
        return None
    
    closest_entity = None
    min_distance = float('inf')
    
    for entity in entities:
        distance = np.linalg.norm(entity.position - target_position)
        if distance < min_distance:
            min_distance = distance
            closest_entity = entity
    
    return closest_entity, min_distance


def calculate_center_of_mass(entities: List[Entity]) -> np.ndarray:
    """
    计算实体系统的质心
    
    Args:
        entities: 实体列表
        
    Returns:
        质心位置
    """
    if not entities:
        return np.zeros(2)
    
    total_mass = sum(entity.mass for entity in entities)
    if total_mass == 0:
        return np.zeros(2)
    
    weighted_sum = np.zeros(2)
    for entity in entities:
        weighted_sum += entity.mass * entity.position
    
    return weighted_sum / total_mass


def calculate_total_momentum(objects: List[Object], 
                           entities: List[Entity]) -> np.ndarray:
    """
    计算总动量
    
    Args:
        objects: 对象列表
        entities: 实体列表
        
    Returns:
        总动量向量
    """
    total_momentum = np.zeros(2)
    
    for obj in objects:
        mass = obj.attributes.get('mass', 1.0)
        total_momentum += mass * obj.velocity
    
    for entity in entities:
        total_momentum += entity.mass * entity.velocity
    
    return total_momentum


def calculate_total_energy(objects: List[Object],
                          entities: List[Entity]) -> Dict[str, float]:
    """
    计算总能量
    
    Args:
        objects: 对象列表
        entities: 实体列表
        
    Returns:
        能量字典
    """
    G = 6.67430e-11
    
    # 动能
    kinetic_energy = 0.0
    for obj in objects:
        mass = obj.attributes.get('mass', 1.0)
        v_squared = np.dot(obj.velocity, obj.velocity)
        kinetic_energy += 0.5 * mass * v_squared
    
    for entity in entities:
        v_squared = np.dot(entity.velocity, entity.velocity)
        kinetic_energy += 0.5 * entity.mass * v_squared
    
    # 势能
    potential_energy = 0.0
    n_entities = len(entities)
    
    for i in range(n_entities):
        for j in range(i + 1, n_entities):
            entity_i = entities[i]
            entity_j = entities[j]
            
            distance = np.linalg.norm(entity_i.position - entity_j.position)
            if distance > 0:
                potential_energy -= G * entity_i.mass * entity_j.mass / distance
    
    # 对象与实体之间的势能
    for obj in objects:
        obj_mass = obj.attributes.get('mass', 1.0)
        for entity in entities:
            distance = np.linalg.norm(obj.position - entity.position)
            if distance > 0:
                potential_energy -= G * obj_mass * entity.mass / distance
    
    total_energy = kinetic_energy + potential_energy
    
    return {
        'kinetic_energy': kinetic_energy,
        'potential_energy': potential_energy,
        'total_energy': total_energy
    }


def format_distance(distance: float) -> str:
    """格式化距离显示"""
    if distance >= 1e12:  # 万亿米
        return f"{distance/1e12:.2f} Tm"
    elif distance >= 1e9:  # 十亿米
        return f"{distance/1e9:.2f} Gm"
    elif distance >= 1e6:  # 百万米
        return f"{distance/1e6:.2f} Mm"
    elif distance >= 1e3:  # 千米
        return f"{distance/1e3:.2f} km"
    else:
        return f"{distance:.2f} m"


def format_time(seconds: float) -> str:
    """格式化时间显示"""
    if seconds >= 365 * 24 * 3600:  # 年
        years = seconds / (365 * 24 * 3600)
        return f"{years:.2f} 年"
    elif seconds >= 24 * 3600:  # 天
        days = seconds / (24 * 3600)
        return f"{days:.2f} 天"
    elif seconds >= 3600:  # 小时
        hours = seconds / 3600
        return f"{hours:.2f} 小时"
    elif seconds >= 60:  # 分钟
        minutes = seconds / 60
        return f"{minutes:.2f} 分钟"
    else:
        return f"{seconds:.2f} 秒"


def format_velocity(velocity: float) -> str:
    """格式化速度显示"""
    if velocity >= 1e6:  # 千米/秒
        return f"{velocity/1e3:.2f} km/s"
    elif velocity >= 1e3:  # 米/秒
        return f"{velocity:.2f} m/s"
    else:
        return f"{velocity:.2f} m/s"