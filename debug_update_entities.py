#!/usr/bin/env python3
"""
调试update_entities函数
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from entities.entity import Entity
from physics.motion import update_entities

def debug_update_entities():
    """调试update_entities函数"""
    print("=== 调试update_entities函数 ===")
    
    # 创建测试实体
    sun = Entity(
        name="Sun",
        mass=1.989e30,
        density=1408,
        radius=0.0,
        position=np.array([0.0, 0.0]),
        velocity=np.array([0.0, 0.0]),
        color=(255, 255, 200)
    )
    
    earth = Entity(
        name="Earth",
        mass=5.972e24,
        density=5515,
        radius=0.0,
        position=np.array([1.496e11, 0.0]),
        velocity=np.array([0.0, 29780.0]),
        color=(100, 200, 255)
    )
    
    mars = Entity(
        name="Mars",
        mass=6.39e23,
        density=3933,
        radius=0.0,
        position=np.array([2.279e11, 0.0]),
        velocity=np.array([0.0, 24130.0]),
        color=(255, 150, 100)
    )
    
    entities = [sun, earth, mars]
    
    print(f"更新前实体数量: {len(entities)}")
    for i, entity in enumerate(entities):
        print(f"  实体 {i}: {entity.name}, ID: {entity.id}")
    
    # 更新实体
    dt = 1.0  # 1秒
    updated_entities = update_entities(entities, dt)
    
    print(f"\n更新后实体数量: {len(updated_entities)}")
    for i, entity in enumerate(updated_entities):
        print(f"  实体 {i}: {entity.name}, ID: {entity.id}")
    
    # 检查ID是否匹配
    print(f"\nID匹配检查:")
    original_ids = [e.id for e in entities]
    updated_ids = [e.id for e in updated_entities]
    
    for i, (orig_id, upd_id) in enumerate(zip(original_ids, updated_ids)):
        match = orig_id == upd_id
        print(f"  实体 {i}: 原始ID={orig_id[:8]}..., 更新ID={upd_id[:8]}..., 匹配={match}")
    
    # 检查属性是否保留
    print(f"\n属性检查:")
    for i, (orig, upd) in enumerate(zip(entities, updated_entities)):
        print(f"  实体 {i} ({orig.name}):")
        print(f"    名称匹配: {orig.name == upd.name}")
        print(f"    颜色匹配: {orig.color == upd.color}")
        print(f"    质量匹配: {orig.mass == upd.mass}")
        print(f"    半径匹配: {orig.radius == upd.radius}")
    
    return entities, updated_entities

if __name__ == "__main__":
    debug_update_entities()