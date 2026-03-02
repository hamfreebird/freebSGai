#!/usr/bin/env python3
"""
调试模拟问题
"""
import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from physics.simulation import UniverseSimulation, SimulationConfig
from entities.entity import Entity, Object
import numpy as np

def test_simulation_directly():
    """直接测试模拟引擎"""
    print("=== 直接测试模拟引擎 ===")
    
    # 创建模拟配置
    config = SimulationConfig(
        time_step=60.0,
        max_time_scale=100.0,
        simulation_boundary=1e12,
        screen_width=1920,
        screen_height=1080
    )
    
    # 创建模拟引擎
    sim = UniverseSimulation(config)
    
    print(f"初始实体数量: {len(sim.entities)}")
    print(f"初始对象数量: {len(sim.objects)}")
    
    # 手动创建实体
    sun = Entity(
        mass=1.989e30,
        density=1408,
        radius=6.957e8,
        position=np.array([0, 0]),
        velocity=np.array([0, 0]),
        name="Sun",
        color=(255, 255, 200)
    )
    
    earth = Entity(
        mass=5.972e24,
        density=5515,
        radius=6.371e6,
        position=np.array([1.496e11, 0]),
        velocity=np.array([0, 29780]),
        name="Earth",
        color=(100, 200, 255)
    )
    
    # 添加到模拟
    print("\n添加实体到模拟...")
    result1 = sim.add_entity(sun)
    result2 = sim.add_entity(earth)
    
    print(f"添加太阳: {'成功' if result1 else '失败'}")
    print(f"添加地球: {'成功' if result2 else '失败'}")
    print(f"模拟实体数量: {len(sim.entities)}")
    
    # 创建对象
    spaceship = Object(
        position=np.array([1.496e11, 1e10]),
        velocity=np.array([0, 30780]),
        label="E.SS",
        attributes={'mass': 1000.0}
    )
    spaceship.color = (255, 100, 100)
    
    print("\n添加对象到模拟...")
    result3 = sim.add_object(spaceship)
    print(f"添加飞船: {'成功' if result3 else '失败'}")
    print(f"模拟对象数量: {len(sim.objects)}")
    
    # 列出所有实体和对象
    print("\n模拟中的实体:")
    for i, entity in enumerate(sim.entities):
        print(f"  {i}: {entity.name}, ID: {entity.id}")
    
    print("\n模拟中的对象:")
    for i, obj in enumerate(sim.objects):
        print(f"  {i}: {obj.label}, ID: {obj.id}")
    
    # 测试更新
    print("\n测试模拟更新...")
    result = sim.update(apply_thrust=False)
    print(f"更新结果: {result['objects_count']}个对象, {result['entities_count']}个实体")

def test_gui_loading():
    """测试GUI加载"""
    print("\n=== 测试GUI加载 ===")
    
    from gui.gui_manager import GUIManager
    
    try:
        gui = GUIManager("config.json")
        
        print(f"GUI模拟实体数量: {len(gui.simulation.entities)}")
        print(f"GUI模拟对象数量: {len(gui.simulation.objects)}")
        
        # 检查simulation对象
        print("\n检查simulation对象:")
        print(f"  simulation类型: {type(gui.simulation)}")
        print(f"  simulation ID: {id(gui.simulation)}")
        
        # 直接访问entities和objects
        print(f"  直接访问entities: {len(gui.simulation.entities)}")
        print(f"  直接访问objects: {len(gui.simulation.objects)}")
        
        # 列出所有实体
        print("\nGUI中的实体:")
        for i, entity in enumerate(gui.simulation.entities):
            print(f"  {i}: {entity.name}, ID: {entity.id}")
        
        print("\nGUI中的对象:")
        for i, obj in enumerate(gui.simulation.objects):
            print(f"  {i}: {obj.label}, ID: {obj.id}")
            
    except Exception as e:
        print(f"GUI加载测试失败: {e}")
        import traceback
        traceback.print_exc()

def check_config_file():
    """检查配置文件"""
    print("\n=== 检查配置文件 ===")
    
    import json
    
    try:
        with open("config.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        scenario = data['initial_scenario']
        print(f"场景名称: {scenario['name']}")
        print(f"实体数量: {len(scenario['entities'])}")
        print(f"对象数量: {len(scenario['objects'])}")
        
        # 检查实体数据
        print("\n配置文件中的实体:")
        for i, entity_data in enumerate(scenario['entities']):
            print(f"  实体 {i}: {entity_data['name']}")
            print(f"    类型: {entity_data['type']}")
            print(f"    位置: {entity_data['position']}")
            
        print("\n配置文件中的对象:")
        for i, object_data in enumerate(scenario['objects']):
            print(f"  对象 {i}: {object_data['label']}")
            print(f"    类型: {object_data['type']}")
            print(f"    位置: {object_data['position']}")
            
    except Exception as e:
        print(f"配置文件检查失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simulation_directly()
    test_gui_loading()
    check_config_file()