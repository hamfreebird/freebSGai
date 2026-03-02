#!/usr/bin/env python3
"""
测试碰撞检测逻辑
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from entities.entity import Entity
from physics.collision import check_entity_entity_collision

def test_collision_logic():
    """测试碰撞检测逻辑"""
    print("=== 测试碰撞检测逻辑 ===")
    
    # 创建测试实体（基于配置文件中的数据）
    sun = Entity(
        name="Sun",
        mass=1.989e30,
        density=1408,
        radius=0.0,  # 会自动计算
        position=np.array([0.0, 0.0]),
        velocity=np.array([0.0, 0.0]),
        color=(255, 255, 200)
    )
    
    earth = Entity(
        name="Earth",
        mass=5.972e24,
        density=5515,
        radius=0.0,  # 会自动计算
        position=np.array([1.496e11, 0.0]),
        velocity=np.array([0.0, 29780.0]),
        color=(100, 200, 255)
    )
    
    mars = Entity(
        name="Mars",
        mass=6.39e23,
        density=3933,
        radius=0.0,  # 会自动计算
        position=np.array([2.279e11, 0.0]),
        velocity=np.array([0.0, 24130.0]),
        color=(255, 150, 100)
    )
    
    print(f"太阳半径: {sun.radius:.2f} 米")
    print(f"地球半径: {earth.radius:.2f} 米")
    print(f"火星半径: {mars.radius:.2f} 米")
    
    print(f"\n太阳-地球距离: {np.linalg.norm(sun.position - earth.position):.2e} 米")
    print(f"太阳-火星距离: {np.linalg.norm(sun.position - mars.position):.2e} 米")
    print(f"地球-火星距离: {np.linalg.norm(earth.position - mars.position):.2e} 米")
    
    print(f"\n太阳半径 + 地球半径: {(sun.radius + earth.radius):.2e} 米")
    print(f"太阳半径 + 火星半径: {(sun.radius + mars.radius):.2e} 米")
    print(f"地球半径 + 火星半径: {(earth.radius + mars.radius):.2e} 米")
    
    print(f"\n碰撞检测:")
    print(f"太阳-地球碰撞: {check_entity_entity_collision(sun, earth)}")
    print(f"太阳-火星碰撞: {check_entity_entity_collision(sun, mars)}")
    print(f"地球-火星碰撞: {check_entity_entity_collision(earth, mars)}")
    
    # 计算实际距离与半径之和的比例
    sun_earth_distance = np.linalg.norm(sun.position - earth.position)
    sun_earth_radius_sum = sun.radius + earth.radius
    ratio = sun_earth_distance / sun_earth_radius_sum
    
    print(f"\n太阳-地球距离 / (太阳半径+地球半径) = {ratio:.2f}")
    
    if ratio < 1:
        print("错误：距离小于半径之和，不应该发生碰撞！")
        print("可能的问题：实体半径计算错误或距离数据错误")
    else:
        print("正确：距离大于半径之和，不应该碰撞")
    
    # 检查碰撞检测函数的逻辑
    print(f"\n碰撞检测函数逻辑:")
    print(f"  距离 <= 半径之和？ {sun_earth_distance <= sun_earth_radius_sum}")
    print(f"  距离: {sun_earth_distance:.2e}")
    print(f"  半径之和: {sun_earth_radius_sum:.2e}")

if __name__ == "__main__":
    test_collision_logic()