"""
运动更新模块
处理实体和对象的位置、速度更新
"""
import numpy as np
from typing import List, Tuple, Dict, Any
from entities.entity import Entity, Object
from physics.gravity import calculate_total_forces_between_entities, calculate_total_force_on_object


def update_entities(entities: List[Entity], dt: float) -> List[Entity]:
    """
    更新所有实体的位置和速度（基于相互引力）
    
    Args:
        entities: 实体列表
        dt: 时间步长 (s)
        
    Returns:
        更新后的实体列表
    """
    # 计算所有实体之间的引力
    forces = calculate_total_forces_between_entities(entities)
    
    # 更新每个实体
    updated_entities = []
    for entity in entities:
        # 获取作用在该实体上的总力
        total_force = forces[entity.id]
        
        # 计算加速度 a = F / m
        acceleration = total_force / entity.mass
        
        # 更新速度 v = v0 + a * dt
        new_velocity = entity.velocity + acceleration * dt
        
        # 更新位置 x = x0 + v * dt + 0.5 * a * dt²
        new_position = entity.position + entity.velocity * dt + 0.5 * acceleration * dt ** 2
        
        # 直接修改原实体的位置和速度，保持ID不变
        entity.position = new_position
        entity.velocity = new_velocity
        updated_entities.append(entity)
    
    return updated_entities


def update_objects(objects: List[Object], entities: List[Entity], 
                   dt: float, apply_thrust: bool = True) -> Tuple[List[Object], List[Dict[str, Any]]]:
    """
    更新所有对象的位置和速度
    
    Args:
        objects: 对象列表
        entities: 实体列表
        dt: 时间步长 (s)
        apply_thrust: 是否应用推力（机动）
        
    Returns:
        (更新后的对象列表, 推力信息列表)
    """
    updated_objects = []
    thrust_infos = []
    
    for obj in objects:
        # 计算引力
        gravitational_force = calculate_total_force_on_object(obj, entities)
        obj_mass = obj.attributes.get('mass', 1.0)
        gravitational_acc = gravitational_force / obj_mass
        
        # 初始化总加速度
        total_acceleration = gravitational_acc.copy()
        thrust_info = {
            'object_id': obj.id,
            'thrust_applied': False,
            'delta_v': np.zeros(2),
            'dv_used': 0.0
        }
        
        # 如果对象正在机动且允许应用推力
        if apply_thrust and obj._is_throttling and obj.remaining_dv > 0:
            # 计算推力方向（默认沿当前速度方向）
            if np.linalg.norm(obj.velocity) > 0:
                thrust_direction = obj.velocity / np.linalg.norm(obj.velocity)
            else:
                thrust_direction = np.array([1.0, 0.0])
            
            # 应用推力
            delta_v, dv_used = obj.apply_thrust(thrust_direction, dt)
            
            if dv_used > 0:
                # 计算推力加速度
                thrust_acc = delta_v / dt
                total_acceleration += thrust_acc
                
                thrust_info.update({
                    'thrust_applied': True,
                    'delta_v': delta_v,
                    'dv_used': dv_used,
                    'thrust_direction': thrust_direction.tolist()
                })
        
        # 更新对象位置（直接修改原对象，保持ID不变）
        obj.update_position(total_acceleration, dt)
        
        # 注意：remaining_dv已在apply_thrust中更新
        
        updated_objects.append(obj)
        thrust_infos.append(thrust_info)
    
    return updated_objects, thrust_infos


def calculate_trajectory(obj: Object, entities: List[Entity], 
                         total_time: float, dt: float = 1.0) -> List[np.ndarray]:
    """
    计算对象的轨迹（无机动）
    
    Args:
        obj: 对象
        entities: 实体列表
        total_time: 总模拟时间 (s)
        dt: 时间步长 (s)
        
    Returns:
        位置列表
    """
    steps = int(total_time / dt)
    positions = []
    
    # 创建副本用于模拟
    sim_obj = obj.copy()
    sim_obj._is_throttling = False  # 禁用机动
    
    for _ in range(steps):
        # 计算引力
        gravitational_force = calculate_total_force_on_object(sim_obj, entities)
        obj_mass = sim_obj.attributes.get('mass', 1.0)
        gravitational_acc = gravitational_force / obj_mass
        
        # 更新位置
        sim_obj.update_position(gravitational_acc, dt)
        positions.append(sim_obj.position.copy())
    
    return positions


def calculate_collision_time(obj1: Object, obj2: Object, 
                            max_time: float = 3600.0, dt: float = 1.0) -> float:
    """
    计算两个对象预计碰撞的时间（线性近似）
    
    Args:
        obj1: 第一个对象
        obj2: 第二个对象
        max_time: 最大搜索时间 (s)
        dt: 时间步长 (s)
        
    Returns:
        碰撞时间 (s)，如果不会碰撞则返回inf
    """
    # 相对位置和速度
    r = obj2.position - obj1.position
    v = obj2.velocity - obj1.velocity
    
    # 解二次方程 |r + v*t| = 0
    # 实际上我们寻找最小距离时刻
    # 距离平方函数: d²(t) = |r + v*t|²
    # 对t求导: 2(r·v) + 2|v|²t = 0
    # t_min = -(r·v) / |v|²
    
    v_squared = np.dot(v, v)
    if v_squared == 0:
        return float('inf')  # 相对速度为零
    
    r_dot_v = np.dot(r, v)
    t_min = -r_dot_v / v_squared
    
    if t_min < 0 or t_min > max_time:
        return float('inf')
    
    # 计算最小距离
    r_min = r + v * t_min
    min_distance = np.linalg.norm(r_min)
    
    # 如果最小距离小于碰撞阈值（假设为1m）
    collision_threshold = 1.0
    if min_distance <= collision_threshold:
        return t_min
    
    return float('inf')


def calculate_relative_state(obj: Object, reference: Entity) -> Dict[str, Any]:
    """
    计算对象相对于实体的状态
    
    Args:
        obj: 对象
        reference: 参考实体
        
    Returns:
        相对状态字典
    """
    # 相对位置和速度
    rel_position = obj.position - reference.position
    rel_velocity = obj.velocity - reference.velocity
    
    # 相对距离和速度大小
    distance = np.linalg.norm(rel_position)
    speed = np.linalg.norm(rel_velocity)
    
    # 相对加速度（近似）
    obj_mass = obj.attributes.get('mass', 1.0)
    force_on_obj = calculate_total_force_on_object(obj, [reference])
    force_on_ref = calculate_total_force_on_object(Object(position=reference.position, 
                                                         velocity=reference.velocity,
                                                         attributes={'mass': 1.0}), 
                                                  [reference])
    
    obj_acc = force_on_obj / obj_mass
    ref_acc = force_on_ref / 1.0  # 假设参考质量为1kg
    rel_acceleration = obj_acc - ref_acc
    
    return {
        'relative_position': rel_position.tolist(),
        'relative_velocity': rel_velocity.tolist(),
        'relative_acceleration': rel_acceleration.tolist(),
        'distance': distance,
        'relative_speed': speed,
        'bearing': np.arctan2(rel_position[1], rel_position[0])  # 方位角
    }