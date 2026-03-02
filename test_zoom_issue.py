#!/usr/bin/env python3
"""
测试QE缩放后实体消失的问题
"""

import numpy as np
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gui.gui_manager import GUIManager
from physics.simulation import UniverseSimulation
from entities.entity import Entity
from physics.gravity import G

def test_zoom_issue():
    """测试缩放问题"""
    print("=== 测试QE缩放后实体消失的问题 ===")
    
    # 创建模拟
    simulation = UniverseSimulation()
    
    # 创建GUI管理器
    gui = GUIManager(simulation)
    
    # 测试初始缩放
    print(f"初始相机缩放: {gui.camera_zoom}")
    print(f"初始相机位置: {gui.camera_position}")
    
    # 创建测试实体
    sun = Entity(
        name="Sun",
        mass=1.989e30,
        density=1408,
        position=np.array([0.0, 0.0]),
        velocity=np.array([0.0, 0.0]),
        color=(255, 255, 0)
    )
    
    earth = Entity(
        name="Earth",
        mass=5.972e24,
        density=5515,
        position=np.array([1.496e11, 0.0]),  # 1 AU
        velocity=np.array([0.0, 29780.0]),
        color=(0, 100, 255)
    )
    
    # 添加实体到模拟
    simulation.add_entity(sun)
    simulation.add_entity(earth)
    
    print(f"\n实体数量: {len(simulation.entities)}")
    
    # 测试坐标转换
    print("\n=== 测试坐标转换 ===")
    
    # 测试太阳位置
    sun_screen = gui.world_to_screen(sun.position)
    print(f"太阳世界坐标: {sun.position}")
    print(f"太阳屏幕坐标: {sun_screen}")
    
    # 测试地球位置
    earth_screen = gui.world_to_screen(earth.position)
    print(f"地球世界坐标: {earth.position}")
    print(f"地球屏幕坐标: {earth_screen}")
    
    # 测试缩放效果
    print("\n=== 测试缩放效果 ===")
    
    # 模拟按Q键放大
    original_zoom = gui.camera_zoom
    gui.target_camera_zoom *= gui.config.zoom_speed  # 放大
    gui.camera_zoom = gui.target_camera_zoom  # 立即应用
    
    print(f"放大后相机缩放: {gui.camera_zoom}")
    
    # 重新计算坐标
    sun_screen_zoomed = gui.world_to_screen(sun.position)
    earth_screen_zoomed = gui.world_to_screen(earth.position)
    
    print(f"放大后太阳屏幕坐标: {sun_screen_zoomed}")
    print(f"放大后地球屏幕坐标: {earth_screen_zoomed}")
    
    # 检查是否在屏幕内
    screen_width = gui.config.width
    screen_height = gui.config.height
    
    def is_on_screen(x, y):
        return 0 <= x <= screen_width and 0 <= y <= screen_height
    
    print(f"\n=== 屏幕边界检查 ===")
    print(f"屏幕尺寸: {screen_width}x{screen_height}")
    print(f"太阳在屏幕内: {is_on_screen(sun_screen_zoomed[0], sun_screen_zoomed[1])}")
    print(f"地球在屏幕内: {is_on_screen(earth_screen_zoomed[0], earth_screen_zoomed[1])}")
    
    # 测试极端缩放
    print("\n=== 测试极端缩放 ===")
    
    # 测试最小缩放
    gui.camera_zoom = gui.config.min_zoom
    print(f"最小缩放: {gui.camera_zoom}")
    sun_screen_min = gui.world_to_screen(sun.position)
    earth_screen_min = gui.world_to_screen(earth.position)
    print(f"最小缩放太阳坐标: {sun_screen_min}")
    print(f"最小缩放地球坐标: {earth_screen_min}")
    
    # 测试最大缩放
    gui.camera_zoom = gui.config.max_zoom
    print(f"最大缩放: {gui.camera_zoom}")
    sun_screen_max = gui.world_to_screen(sun.position)
    earth_screen_max = gui.world_to_screen(earth.position)
    print(f"最大缩放太阳坐标: {sun_screen_max}")
    print(f"最大缩放地球坐标: {earth_screen_max}")
    
    # 分析问题
    print("\n=== 问题分析 ===")
    
    # 计算缩放因子对坐标的影响
    zoom_factors = [original_zoom, original_zoom * gui.config.zoom_speed, 
                   gui.config.min_zoom, gui.config.max_zoom]
    
    for zoom in zoom_factors:
        gui.camera_zoom = zoom
        earth_screen = gui.world_to_screen(earth.position)
        distance_from_center = np.sqrt((earth_screen[0] - screen_width/2)**2 + 
                                      (earth_screen[1] - screen_height/2)**2)
        print(f"缩放={zoom:.2e}: 地球距离中心={distance_from_center:.1f}像素, "
              f"在屏幕内={is_on_screen(earth_screen[0], earth_screen[1])}")
    
    return gui, simulation

if __name__ == "__main__":
    test_zoom_issue()