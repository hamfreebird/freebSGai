#!/usr/bin/env python3
"""
测试显示问题
"""
import numpy as np
import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from entities.entity import Entity
from gui.gui_manager import GUIManager

def test_entity_properties():
    """测试实体属性"""
    print("=== 测试实体属性 ===")
    
    # 创建太阳实体（根据配置文件）
    sun = Entity(
        mass=1.989e30,
        density=1408,
        radius=7e8,  # 太阳半径约7e8米
        position=np.array([0, 0]),
        velocity=np.array([0, 0]),
        name="太阳",
        color=(255, 255, 200)
    )
    
    # 创建地球实体
    earth = Entity(
        mass=5.972e24,
        density=5515,
        radius=6.371e6,  # 地球半径约6.371e6米
        position=np.array([1.496e11, 0]),
        velocity=np.array([0, 29780]),
        name="地球",
        color=(100, 200, 255)
    )
    
    print(f"太阳半径: {sun.radius:.2e} 米")
    print(f"地球半径: {earth.radius:.2e} 米")
    print(f"太阳颜色: {sun.color}")
    print(f"地球颜色: {earth.color}")
    
    # 测试相机缩放计算
    camera_zoom = 1e-9  # 默认缩放
    print(f"\n相机缩放: {camera_zoom:.2e} 像素/米")
    
    # 计算屏幕上的半径
    sun_screen_radius = sun.radius * camera_zoom
    earth_screen_radius = earth.radius * camera_zoom
    
    print(f"太阳屏幕半径: {sun_screen_radius:.2f} 像素")
    print(f"地球屏幕半径: {earth_screen_radius:.2f} 像素")
    
    # 使用GUI管理器中的实际计算逻辑
    if sun.radius > 1e7:
        log_radius = np.log10(sun.radius)
        base_radius = 5
        scaled_radius = base_radius * log_radius * camera_zoom
        print(f"太阳对数缩放半径: {scaled_radius:.2f} 像素")
    
    if earth.radius > 1e7:
        log_radius = np.log10(earth.radius)
        base_radius = 5
        scaled_radius = base_radius * log_radius * camera_zoom
        print(f"地球对数缩放半径: {scaled_radius:.2f} 像素")
    else:
        scaled_radius = earth.radius * camera_zoom
        print(f"地球线性缩放半径: {scaled_radius:.2f} 像素")

def test_coordinate_conversion():
    """测试坐标转换"""
    print("\n=== 测试坐标转换 ===")
    
    # 模拟GUI管理器中的坐标转换
    config_width = 1920
    config_height = 1080
    camera_position = np.array([0.0, 0.0])
    camera_zoom = 1e-9
    
    # 地球位置
    earth_position = np.array([1.496e11, 0])
    
    # 计算相对位置
    relative_x = earth_position[0] - camera_position[0]
    relative_y = earth_position[1] - camera_position[1]
    
    # 应用缩放
    screen_x = config_width // 2 + relative_x * camera_zoom
    screen_y = config_height // 2 + relative_y * camera_zoom
    
    print(f"地球世界坐标: ({earth_position[0]:.2e}, {earth_position[1]:.2e}) 米")
    print(f"相对位置: ({relative_x:.2e}, {relative_y:.2e}) 米")
    print(f"屏幕坐标: ({screen_x:.2f}, {screen_y:.2f}) 像素")
    
    # 检查是否在屏幕内
    if 0 <= screen_x <= config_width and 0 <= screen_y <= config_height:
        print("地球在屏幕内")
    else:
        print("地球在屏幕外")

def test_gui_initialization():
    """测试GUI初始化"""
    print("\n=== 测试GUI初始化 ===")
    
    try:
        # 尝试创建GUI管理器
        gui = GUIManager("config.json")
        
        print(f"模拟实体数量: {len(gui.simulation.entities)}")
        print(f"模拟对象数量: {len(gui.simulation.objects)}")
        
        if gui.simulation.entities:
            for i, entity in enumerate(gui.simulation.entities):
                print(f"实体 {i}: {entity.name}, 位置: ({entity.position[0]:.2e}, {entity.position[1]:.2e}), 颜色: {entity.color}")
        
        if gui.simulation.objects:
            for i, obj in enumerate(gui.simulation.objects):
                print(f"对象 {i}: {obj.label}, 位置: ({obj.position[0]:.2e}, {obj.position[1]:.2e})")
        
        print(f"相机位置: {gui.camera_position}")
        print(f"相机缩放: {gui.camera_zoom}")
        
    except Exception as e:
        print(f"GUI初始化错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_entity_properties()
    test_coordinate_conversion()
    test_gui_initialization()