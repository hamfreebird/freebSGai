#!/usr/bin/env python3
"""
调试物理模拟问题
检查为什么实体位置不更新
"""

import numpy as np
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from physics.simulation import UniverseSimulation
from entities.entity import Entity

def debug_physics_update():
    """调试物理更新问题"""
    print("=== 调试物理模拟问题 ===")
    
    # 创建模拟
    simulation = UniverseSimulation()
    
    # 创建简单的测试实体
    entity1 = Entity(
        name="Test1",
        mass=1e24,
        density=1000,
        radius=1e6,
        position=np.array([0.0, 0.0]),
        velocity=np.array([1000.0, 0.0]),  # 1 km/s 向右
        color=(255, 0, 0)
    )
    
    entity2 = Entity(
        name="Test2",
        mass=1e24,
        density=1000,
        radius=1e6,
        position=np.array([1e7, 0.0]),  # 10,000 km 右边
        velocity=np.array([0.0, 0.0]),
        color=(0, 255, 0)
    )
    
    # 添加实体到模拟
    simulation.add_entity(entity1)
    simulation.add_entity(entity2)
    
    print(f"实体数量: {len(simulation.entities)}")
    print(f"实体1初始位置: {entity1.position}")
    print(f"实体1初始速度: {entity1.velocity}")
    print(f"实体2初始位置: {entity2.position}")
    
    # 检查模拟的entities列表
    print(f"\n模拟中的实体: {len(simulation.entities)}")
    for i, e in enumerate(simulation.entities):
        print(f"  实体{i}: {e.name}, 位置: {e.position}, 速度: {e.velocity}")
    
    # 测试更新
    dt = 1.0  # 1秒
    print(f"\n更新 {dt} 秒...")
    
    # 保存初始位置
    initial_pos1 = entity1.position.copy()
    initial_pos2 = entity2.position.copy()
    
    # 调用模拟更新
    simulation.update(dt)
    
    print(f"更新后实体1位置: {entity1.position}")
    print(f"更新后实体2位置: {entity2.position}")
    
    # 检查位置变化
    displacement1 = np.linalg.norm(entity1.position - initial_pos1)
    displacement2 = np.linalg.norm(entity2.position - initial_pos2)
    
    print(f"\n位移:")
    print(f"  实体1: {displacement1:.1f} m (预期: {np.linalg.norm(entity1.velocity)*dt:.1f} m)")
    print(f"  实体2: {displacement2:.1f} m")
    
    # 检查速度变化
    print(f"\n速度变化:")
    print(f"  实体1速度: {entity1.velocity}")
    print(f"  实体2速度: {entity2.velocity}")
    
    # 检查引力计算
    print(f"\n=== 检查引力计算 ===")
    
    # 计算两个实体之间的引力
    from physics.gravity import G, calculate_gravitational_force
    
    r = entity2.position - entity1.position
    distance = np.linalg.norm(r)
    force_magnitude = G * entity1.mass * entity2.mass / (distance ** 2)
    
    print(f"实体间距离: {distance:.1f} m")
    print(f"引力大小: {force_magnitude:.2e} N")
    
    # 计算加速度
    acceleration1 = force_magnitude / entity1.mass
    acceleration2 = force_magnitude / entity2.mass
    
    print(f"实体1加速度: {acceleration1:.6f} m/s^2")
    print(f"实体2加速度: {acceleration2:.6f} m/s^2")
    
    # 检查模拟的update方法
    print(f"\n=== 检查模拟update方法 ===")
    
    # 查看simulation.py中的update方法
    print("需要检查 physics/simulation.py 中的 update 方法")
    print("可能的问题:")
    print("  1. update方法没有正确调用实体更新")
    print("  2. 实体更新逻辑有问题")
    print("  3. 时间步长处理错误")
    
    return simulation

def check_simulation_update_method():
    """检查simulation.py中的update方法"""
    print("\n=== 检查simulation.py update方法 ===")
    
    # 读取simulation.py文件
    sim_file = "physics/simulation.py"
    if os.path.exists(sim_file):
        with open(sim_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 查找update方法
        if "def update(" in content:
            start = content.find("def update(")
            end = content.find("\n\n", start)
            if end == -1:
                end = content.find("\nclass", start)
            if end == -1:
                end = len(content)
                
            update_method = content[start:end]
            print("找到update方法:")
            print(update_method[:500] + "..." if len(update_method) > 500 else update_method)
            
            # 检查关键部分
            if "self.entities" in update_method and "position" in update_method:
                print("\n✓ update方法引用了entities和position")
            else:
                print("\n✗ update方法可能没有正确更新实体位置")
                
            # 检查是否调用了运动更新
            if "update_position_and_velocity" in update_method:
                print("✓ 调用了update_position_and_velocity")
            else:
                print("✗ 没有调用update_position_and_velocity")
        else:
            print("✗ 没有找到update方法")
    else:
        print(f"✗ 文件不存在: {sim_file}")

if __name__ == "__main__":
    debug_physics_update()
    check_simulation_update_method()