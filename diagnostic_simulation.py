#!/usr/bin/env python3
"""
诊断脚本：检查模拟状态，找出为什么只显示太阳的问题
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import json
import numpy as np
from physics.simulation import UniverseSimulation
from entities.entity import Entity
from physics.motion import Object

def load_config():
    """加载配置文件"""
    config_path = "config.json"
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_simulation():
    """创建模拟实例"""
    config = load_config()
    simulation = UniverseSimulation()
    
    # 获取初始场景配置
    initial_scenario = config.get("initial_scenario", {})
    
    # 创建实体
    for entity_config in initial_scenario.get("entities", []):
        entity = Entity(
            name=entity_config["name"],
            mass=entity_config["mass"],
            density=entity_config["density"],
            radius=0.0,  # 传递0，让__post_init__根据质量和密度计算半径
            position=np.array(entity_config["position"], dtype=np.float64),
            velocity=np.array(entity_config["velocity"], dtype=np.float64),
            color=tuple(entity_config["color"])
        )
        simulation.add_entity(entity)
        print(f"创建实体: {entity.name}, 位置: {entity.position}, 质量: {entity.mass}, 半径: {entity.radius}")
    
    # 创建对象
    for object_config in initial_scenario.get("objects", []):
        # 创建属性字典
        attributes = {
            'color': tuple(object_config["color"]),
            'max_acceleration': object_config.get("max_acceleration", 5.0),
            'remaining_dv': object_config.get("remaining_dv", 1000.0)
        }
        
        obj = Object(
            label=object_config["label"],
            position=np.array(object_config["position"], dtype=np.float64),
            velocity=np.array(object_config["velocity"], dtype=np.float64),
            attributes=attributes,
            max_acceleration=object_config.get("max_acceleration", 5.0),
            remaining_dv=object_config.get("remaining_dv", 1000.0)
        )
        simulation.add_object(obj)
        print(f"创建对象: {obj.label}, 位置: {obj.position}, 速度: {obj.velocity}, 颜色: {attributes['color']}")
    
    return simulation

def check_simulation_state(simulation):
    """检查模拟状态"""
    print("\n=== 模拟状态诊断 ===")
    
    # 检查实体
    print(f"实体数量: {len(simulation.entities)}")
    for i, entity in enumerate(simulation.entities):
        print(f"  实体 {i}: {entity.name}")
        print(f"    位置: {entity.position}")
        print(f"    速度: {entity.velocity}")
        print(f"    质量: {entity.mass}")
        print(f"    半径: {entity.radius}")
        print(f"    颜色: {entity.color}")
    
    # 检查对象
    print(f"\n对象数量: {len(simulation.objects)}")
    for i, obj in enumerate(simulation.objects):
        print(f"  对象 {i}: {obj.label}")
        print(f"    位置: {obj.position}")
        print(f"    速度: {obj.velocity}")
        print(f"    颜色: {obj.attributes.get('color', 'Unknown')}")
    
    # 检查模拟更新
    print("\n=== 模拟更新测试 ===")
    simulation.update(1.0)  # 更新1秒
    
    print("更新后实体位置:")
    for entity in simulation.entities:
        print(f"  {entity.name}: {entity.position}")
    
    print("\n更新后对象位置:")
    for obj in simulation.objects:
        print(f"  {obj.label}: {obj.position}")

def check_coordinate_system():
    """检查坐标系统"""
    print("\n=== 坐标系统检查 ===")
    
    # 创建测试位置
    test_positions = [
        np.array([0.0, 0.0]),  # 原点
        np.array([1e11, 0.0]),  # 地球距离太阳约1.5e11米
        np.array([2.28e11, 0.0]),  # 火星距离
        np.array([1e12, 1e12]),  # 远距离
    ]
    
    # 测试相机缩放
    camera_scale = 1e-11  # 当前使用的缩放
    screen_center = np.array([800, 600])  # 假设屏幕中心
    
    print(f"相机缩放: {camera_scale}")
    print(f"屏幕中心: {screen_center}")
    
    for pos in test_positions:
        screen_pos = screen_center + pos * camera_scale
        print(f"世界位置 {pos} -> 屏幕位置 {screen_pos}")
        
        # 检查是否在屏幕内
        in_screen = (0 <= screen_pos[0] <= 1600 and 0 <= screen_pos[1] <= 1200)
        print(f"  在屏幕内: {in_screen}")

def check_entity_visibility():
    """检查实体可见性"""
    print("\n=== 实体可见性检查 ===")
    
    simulation = create_simulation()
    
    # 检查每个实体是否在屏幕内
    camera_scale = 1e-11
    screen_center = np.array([800, 600])
    screen_width = 1600
    screen_height = 1200
    
    for entity in simulation.entities:
        screen_pos = screen_center + entity.position * camera_scale
        
        in_screen_x = 0 <= screen_pos[0] <= screen_width
        in_screen_y = 0 <= screen_pos[1] <= screen_height
        
        print(f"{entity.name}:")
        print(f"  世界位置: {entity.position}")
        print(f"  屏幕位置: {screen_pos}")
        print(f"  在屏幕内: {in_screen_x and in_screen_y}")
        
        if not (in_screen_x and in_screen_y):
            print(f"  警告: {entity.name} 可能不在屏幕内!")
            
            # 计算需要调整的相机缩放
            # 找到使实体可见的最小缩放
            max_distance = max(abs(entity.position[0]), abs(entity.position[1]))
            if max_distance > 0:
                suggested_scale = min(screen_width, screen_height) / (2 * max_distance)
                print(f"  建议缩放: {suggested_scale:.2e} (当前: {camera_scale:.2e})")

def main():
    """主函数"""
    print("开始模拟诊断...")
    
    # 创建模拟
    simulation = create_simulation()
    
    # 检查模拟状态
    check_simulation_state(simulation)
    
    # 检查坐标系统
    check_coordinate_system()
    
    # 检查实体可见性
    check_entity_visibility()
    
    print("\n=== 诊断完成 ===")
    
    # 总结问题
    print("\n可能的问题:")
    print("1. 相机缩放太小 - 实体可能超出屏幕范围")
    print("2. 实体位置数据错误 - 检查配置文件")
    print("3. 渲染函数错误 - 检查draw_entities()和draw_objects()")
    print("4. 模拟更新问题 - 实体可能被意外移除")
    print("5. 颜色或半径计算错误 - 导致实体不可见")

if __name__ == "__main__":
    main()