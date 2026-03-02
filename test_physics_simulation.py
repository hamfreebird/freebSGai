#!/usr/bin/env python3
"""
测试物理模拟是否正常工作
检查地球和火星相对于太阳的运动
"""

import numpy as np
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from physics.simulation import UniverseSimulation
from entities.entity import Entity
from physics.gravity import G

def test_earth_mars_motion():
    """测试地球和火星相对于太阳的运动"""
    print("=== 测试地球和火星相对于太阳的运动 ===")
    
    # 创建模拟
    simulation = UniverseSimulation()
    
    # 创建太阳、地球、火星
    # 计算半径（根据质量和密度）
    sun_radius = (3 * (1.989e30 / 1408) / (4 * np.pi)) ** (1/3)
    earth_radius = (3 * (5.972e24 / 5515) / (4 * np.pi)) ** (1/3)
    mars_radius = (3 * (6.39e23 / 3933) / (4 * np.pi)) ** (1/3)
    
    sun = Entity(
        name="Sun",
        mass=1.989e30,  # 太阳质量
        density=1408,
        radius=sun_radius,
        position=np.array([0.0, 0.0]),
        velocity=np.array([0.0, 0.0]),
        color=(255, 255, 0)
    )
    
    earth = Entity(
        name="Earth",
        mass=5.972e24,  # 地球质量
        density=5515,
        radius=earth_radius,
        position=np.array([1.496e11, 0.0]),  # 1 AU = 1.496e11 米
        velocity=np.array([0.0, 29780.0]),  # 地球轨道速度 ~29.78 km/s
        color=(0, 100, 255)
    )
    
    mars = Entity(
        name="Mars",
        mass=6.39e23,  # 火星质量
        density=3933,
        radius=mars_radius,
        position=np.array([2.279e11, 0.0]),  # 1.524 AU = 2.279e11 米
        velocity=np.array([0.0, 24070.0]),  # 火星轨道速度 ~24.07 km/s
        color=(255, 100, 0)
    )
    
    # 添加实体到模拟
    simulation.add_entity(sun)
    simulation.add_entity(earth)
    simulation.add_entity(mars)
    
    print(f"实体数量: {len(simulation.entities)}")
    print(f"太阳质量: {sun.mass:.2e} kg")
    print(f"地球质量: {earth.mass:.2e} kg")
    print(f"火星质量: {mars.mass:.2e} kg")
    
    # 计算初始距离
    earth_distance = np.linalg.norm(earth.position - sun.position)
    mars_distance = np.linalg.norm(mars.position - sun.position)
    print(f"\n初始距离:")
    print(f"  地球-太阳: {earth_distance/1e11:.2f} x10^11 m ({earth_distance/1.496e11:.2f} AU)")
    print(f"  火星-太阳: {mars_distance/1e11:.2f} x10^11 m ({mars_distance/1.496e11:.2f} AU)")
    
    # 计算初始速度
    earth_speed = np.linalg.norm(earth.velocity)
    mars_speed = np.linalg.norm(mars.velocity)
    print(f"\n初始速度:")
    print(f"  地球: {earth_speed/1000:.2f} km/s")
    print(f"  火星: {mars_speed/1000:.2f} km/s")
    
    # 计算轨道周期（近似）
    # 开普勒第三定律: T² ∝ a³
    earth_period = 2 * np.pi * earth_distance / earth_speed  # 秒
    mars_period = 2 * np.pi * mars_distance / mars_speed  # 秒
    
    print(f"\n近似轨道周期:")
    print(f"  地球: {earth_period/86400:.1f} 天 ({earth_period/31557600:.2f} 年)")
    print(f"  火星: {mars_period/86400:.1f} 天 ({mars_period/31557600:.2f} 年)")
    
    # 测试模拟更新
    print("\n=== 模拟更新测试 ===")
    
    # 保存初始位置
    initial_earth_pos = earth.position.copy()
    initial_mars_pos = mars.position.copy()
    
    # 更新模拟（1小时 = 3600秒）
    dt = 3600.0  # 1小时
    simulation.update(dt)
    
    # 检查位置变化
    earth_displacement = np.linalg.norm(earth.position - initial_earth_pos)
    mars_displacement = np.linalg.norm(mars.position - initial_mars_pos)
    
    print(f"更新 {dt} 秒后:")
    print(f"  地球位移: {earth_displacement/1000:.1f} km")
    print(f"  火星位移: {mars_displacement/1000:.1f} km")
    
    # 计算预期位移（基于轨道速度）
    expected_earth_displacement = earth_speed * dt
    expected_mars_displacement = mars_speed * dt
    
    print(f"\n预期位移（基于速度）:")
    print(f"  地球: {expected_earth_displacement/1000:.1f} km")
    print(f"  火星: {expected_mars_displacement/1000:.1f} km")
    
    # 检查引力影响
    print("\n=== 引力影响检查 ===")
    
    # 计算地球受到的太阳引力
    r_earth = earth.position - sun.position
    distance_earth = np.linalg.norm(r_earth)
    force_earth = G * sun.mass * earth.mass / (distance_earth ** 2)
    acceleration_earth = force_earth / earth.mass
    
    print(f"地球受到的太阳引力:")
    print(f"  距离: {distance_earth/1e11:.2f} x10^11 m")
    print(f"  引力: {force_earth:.2e} N")
    print(f"  加速度: {acceleration_earth:.6f} m/s^2")
    
    # 计算向心加速度（v^2/r）
    centripetal_acc_earth = earth_speed ** 2 / distance_earth
    print(f"  向心加速度: {centripetal_acc_earth:.6f} m/s^2")
    print(f"  加速度比: {acceleration_earth/centripetal_acc_earth:.4f}")
    
    # 测试多次更新
    print("\n=== 长期模拟测试 ===")
    
    # 重置位置
    earth.position = initial_earth_pos.copy()
    mars.position = initial_mars_pos.copy()
    
    # 模拟1天（24小时）
    positions_earth = []
    positions_mars = []
    
    for i in range(24):  # 24小时
        simulation.update(3600)  # 每小时更新一次
        positions_earth.append(earth.position.copy())
        positions_mars.append(mars.position.copy())
    
    # 计算轨道形状
    if len(positions_earth) > 1:
        # 计算地球轨道半径变化
        radii_earth = [np.linalg.norm(pos - sun.position) for pos in positions_earth]
        min_radius_earth = min(radii_earth)
        max_radius_earth = max(radii_earth)
        
        print(f"地球轨道半径变化:")
        print(f"  最小: {min_radius_earth/1e11:.4f} x10^11 m")
        print(f"  最大: {max_radius_earth/1e11:.4f} x10^11 m")
        print(f"  变化率: {(max_radius_earth - min_radius_earth)/min_radius_earth*100:.2f}%")
    
    return simulation

def analyze_physics_issues():
    """分析物理模拟问题"""
    print("\n=== 物理模拟问题分析 ===")
    
    print("1. 可能的问题:")
    print("   a) 时间步长太大导致数值不稳定")
    print("   b) 引力计算精度不足")
    print("   c) 速度更新算法有问题")
    print("   d) 实体位置更新顺序错误")
    
    print("\n2. 建议的修复:")
    print("   a) 减小时间步长（如从3600秒减小到60秒）")
    print("   b) 使用更精确的数值积分方法（如Verlet或RK4）")
    print("   c) 检查velocity和position更新顺序")
    print("   d) 添加能量守恒检查")
    
    print("\n3. 当前实现检查:")
    print("   - physics/simulation.py: update方法")
    print("   - physics/gravity.py: calculate_gravitational_force函数")
    print("   - physics/motion.py: update_position_and_velocity函数")

if __name__ == "__main__":
    test_earth_mars_motion()
    analyze_physics_issues()