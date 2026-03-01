"""
碰撞检测和合并模块
处理对象与实体、实体与实体之间的碰撞
"""
import numpy as np
from typing import List, Tuple, Dict, Any, Optional
from entities.entity import Entity, Object


def check_object_entity_collision(obj: Object, entity: Entity) -> bool:
    """
    检查对象与实体是否碰撞
    
    Args:
        obj: 对象
        entity: 实体
        
    Returns:
        是否碰撞
    """
    # 计算距离
    distance = np.linalg.norm(obj.position - entity.position)
    
    # 如果距离小于实体半径，则碰撞
    return distance <= entity.radius


def check_entity_entity_collision(entity1: Entity, entity2: Entity) -> bool:
    """
    检查两个实体是否碰撞
    
    Args:
        entity1: 第一个实体
        entity2: 第二个实体
        
    Returns:
        是否碰撞
    """
    # 计算距离
    distance = np.linalg.norm(entity1.position - entity2.position)
    
    # 如果距离小于两实体半径之和，则碰撞
    return distance <= (entity1.radius + entity2.radius)


def check_object_object_collision(obj1: Object, obj2: Object, threshold: float = 1.0) -> bool:
    """
    检查两个对象是否碰撞
    
    Args:
        obj1: 第一个对象
        obj2: 第二个对象
        threshold: 碰撞阈值 (m)
        
    Returns:
        是否碰撞
    """
    # 计算距离
    distance = np.linalg.norm(obj1.position - obj2.position)
    
    # 如果距离小于阈值，则碰撞
    return distance <= threshold


def find_all_collisions(objects: List[Object], entities: List[Entity]) -> Dict[str, List[Any]]:
    """
    查找所有碰撞
    
    Args:
        objects: 对象列表
        entities: 实体列表
        
    Returns:
        碰撞信息字典
    """
    collisions = {
        'object_entity': [],  # 对象-实体碰撞
        'entity_entity': [],  # 实体-实体碰撞
        'object_object': []   # 对象-对象碰撞
    }
    
    # 检查对象与实体碰撞
    for obj in objects:
        for entity in entities:
            if check_object_entity_collision(obj, entity):
                collisions['object_entity'].append({
                    'object_id': obj.id,
                    'entity_id': entity.id,
                    'object_position': obj.position.tolist(),
                    'entity_position': entity.position.tolist(),
                    'distance': np.linalg.norm(obj.position - entity.position)
                })
    
    # 检查实体与实体碰撞
    n_entities = len(entities)
    for i in range(n_entities):
        for j in range(i + 1, n_entities):
            entity1 = entities[i]
            entity2 = entities[j]
            
            if check_entity_entity_collision(entity1, entity2):
                collisions['entity_entity'].append({
                    'entity1_id': entity1.id,
                    'entity2_id': entity2.id,
                    'entity1_position': entity1.position.tolist(),
                    'entity2_position': entity2.position.tolist(),
                    'distance': np.linalg.norm(entity1.position - entity2.position),
                    'radius_sum': entity1.radius + entity2.radius
                })
    
    # 检查对象与对象碰撞
    n_objects = len(objects)
    for i in range(n_objects):
        for j in range(i + 1, n_objects):
            obj1 = objects[i]
            obj2 = objects[j]
            
            if check_object_object_collision(obj1, obj2):
                collisions['object_object'].append({
                    'object1_id': obj1.id,
                    'object2_id': obj2.id,
                    'object1_position': obj1.position.tolist(),
                    'object2_position': obj2.position.tolist(),
                    'distance': np.linalg.norm(obj1.position - obj2.position)
                })
    
    return collisions


def handle_object_entity_collision(obj: Object, entity: Entity) -> Tuple[Optional[Object], Optional[Entity]]:
    """
    处理对象与实体碰撞
    
    Args:
        obj: 对象
        entity: 实体
        
    Returns:
        (处理后的对象, 处理后的实体)
        对象死亡返回None，实体不变
    """
    # 对象撞上实体，对象死亡（消失）
    return None, entity


def merge_entities(entity1: Entity, entity2: Entity) -> Entity:
    """
    合并两个碰撞的实体
    
    Args:
        entity1: 第一个实体
        entity2: 第二个实体
        
    Returns:
        合并后的新实体
    """
    # 计算新实体的质心（加权平均）
    total_mass = entity1.mass + entity2.mass
    new_position = (entity1.mass * entity1.position + entity2.mass * entity2.position) / total_mass
    
    # 计算新实体的速度（动量守恒）
    total_momentum = entity1.get_momentum() + entity2.get_momentum()
    new_velocity = total_momentum / total_mass
    
    # 计算平均密度
    new_density = (entity1.density + entity2.density) / 2
    
    # 计算新半径（根据质量和平均密度）
    new_volume = total_mass / new_density
    new_radius = (3 * new_volume / (4 * np.pi)) ** (1/3)
    
    # 创建新实体
    merged_entity = Entity(
        mass=total_mass,
        density=new_density,
        radius=new_radius,
        position=new_position,
        velocity=new_velocity,
        color=(
            (entity1.color[0] + entity2.color[0]) // 2,
            (entity1.color[1] + entity2.color[1]) // 2,
            (entity1.color[2] + entity2.color[2]) // 2
        ),
        name=f"Merged({entity1.name},{entity2.name})"
    )
    
    return merged_entity


def handle_entity_entity_collisions(entities: List[Entity], 
                                   collisions: List[Dict[str, Any]]) -> Tuple[List[Entity], List[Entity]]:
    """
    处理所有实体-实体碰撞
    
    Args:
        entities: 原始实体列表
        collisions: 碰撞信息列表
        
    Returns:
        (更新后的实体列表, 被删除的实体列表)
    """
    # 创建实体字典以便快速查找
    entity_dict = {entity.id: entity for entity in entities}
    entities_to_remove = set()
    new_entities = []
    
    # 处理每个碰撞
    for collision in collisions:
        entity1_id = collision['entity1_id']
        entity2_id = collision['entity2_id']
        
        # 如果任一实体已被标记删除，跳过
        if entity1_id in entities_to_remove or entity2_id in entities_to_remove:
            continue
        
        entity1 = entity_dict[entity1_id]
        entity2 = entity_dict[entity2_id]
        
        # 合并实体
        merged_entity = merge_entities(entity1, entity2)
        
        # 标记原实体为待删除
        entities_to_remove.add(entity1_id)
        entities_to_remove.add(entity2_id)
        
        # 添加新实体
        new_entities.append(merged_entity)
    
    # 构建最终实体列表
    final_entities = []
    for entity in entities:
        if entity.id not in entities_to_remove:
            final_entities.append(entity)
    
    # 添加新合并的实体
    final_entities.extend(new_entities)
    
    # 获取被删除的实体
    removed_entities = [entity_dict[eid] for eid in entities_to_remove if eid in entity_dict]
    
    return final_entities, removed_entities


def handle_object_object_collision(obj1: Object, obj2: Object) -> Tuple[Optional[Object], Optional[Object]]:
    """
    处理两个对象的碰撞
    
    Args:
        obj1: 第一个对象
        obj2: 第二个对象
        
    Returns:
        (处理后的对象1, 处理后的对象2)
        默认两者都存活，可根据需要修改
    """
    # 简单处理：两者都存活但受到伤害
    damage = 10.0
    obj1.take_damage(damage)
    obj2.take_damage(damage)
    
    # 如果对象死亡，返回None
    obj1_result = obj1 if obj1.is_alive() else None
    obj2_result = obj2 if obj2.is_alive() else None
    
    return obj1_result, obj2_result


def process_all_collisions(objects: List[Object], entities: List[Entity]) -> Tuple[List[Object], List[Entity], Dict[str, Any]]:
    """
    处理所有碰撞并返回更新后的对象和实体
    
    Args:
        objects: 对象列表
        entities: 实体列表
        
    Returns:
        (更新后的对象列表, 更新后的实体列表, 碰撞统计信息)
    """
    # 查找所有碰撞
    collisions = find_all_collisions(objects, entities)
    
    # 处理对象-实体碰撞
    objects_to_remove = set()
    for collision in collisions['object_entity']:
        obj_id = collision['object_id']
        entity_id = collision['entity_id']
        
        # 找到对应的对象和实体
        obj = next((o for o in objects if o.id == obj_id), None)
        entity = next((e for e in entities if e.id == entity_id), None)
        
        if obj and entity:
            # 对象死亡
            objects_to_remove.add(obj_id)
    
    # 更新对象列表（移除死亡的对象）
    updated_objects = [obj for obj in objects if obj.id not in objects_to_remove]
    
    # 处理实体-实体碰撞
    updated_entities, removed_entities = handle_entity_entity_collisions(
        entities, collisions['entity_entity']
    )
    
    # 处理对象-对象碰撞
    for collision in collisions['object_object']:
        obj1_id = collision['object1_id']
        obj2_id = collision['object2_id']
        
        obj1 = next((o for o in updated_objects if o.id == obj1_id), None)
        obj2 = next((o for o in updated_objects if o.id == obj2_id), None)
        
        if obj1 and obj2:
            new_obj1, new_obj2 = handle_object_object_collision(obj1.copy(), obj2.copy())
            
            # 更新对象列表
            updated_objects = [o for o in updated_objects if o.id not in [obj1_id, obj2_id]]
            if new_obj1:
                updated_objects.append(new_obj1)
            if new_obj2:
                updated_objects.append(new_obj2)
    
    # 收集统计信息
    stats = {
        'total_collisions': len(collisions['object_entity']) + len(collisions['entity_entity']) + len(collisions['object_object']),
        'object_entity_collisions': len(collisions['object_entity']),
        'entity_entity_collisions': len(collisions['entity_entity']),
        'object_object_collisions': len(collisions['object_object']),
        'objects_destroyed': len(objects_to_remove),
        'entities_merged': len(removed_entities),
        'objects_remaining': len(updated_objects),
        'entities_remaining': len(updated_entities)
    }
    
    return updated_objects, updated_entities, stats