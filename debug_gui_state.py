#!/usr/bin/env python3
"""
调试GUI状态：检查为什么只显示1个实体
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pygame
from gui.gui_manager import GUIManager

def debug_gui_state():
    """调试GUI状态"""
    print("=== 调试GUI状态 ===")
    
    # 创建GUI管理器
    gui = GUIManager("config.json")
    
    print(f"\n1. 模拟状态:")
    print(f"   实体数量: {len(gui.simulation.entities)}")
    print(f"   对象数量: {len(gui.simulation.objects)}")
    
    print(f"\n2. 实体详细信息:")
    for i, entity in enumerate(gui.simulation.entities):
        print(f"   实体 {i}: {entity.name}")
        print(f"     位置: {entity.position}")
        print(f"     速度: {entity.velocity}")
        print(f"     质量: {entity.mass}")
        print(f"     半径: {entity.radius}")
        print(f"     颜色: {entity.color}")
        print(f"     ID: {entity.id}")
    
    print(f"\n3. 对象详细信息:")
    for i, obj in enumerate(gui.simulation.objects):
        print(f"   对象 {i}: {obj.label}")
        print(f"     位置: {obj.position}")
        print(f"     速度: {obj.velocity}")
        print(f"     颜色: {obj.attributes.get('color', 'Unknown')}")
        print(f"     ID: {obj.id}")
    
    print(f"\n4. 相机状态:")
    print(f"   相机位置: {gui.camera_position}")
    print(f"   相机缩放: {gui.camera_zoom}")
    print(f"   屏幕尺寸: {gui.config.width} x {gui.config.height}")
    
    print(f"\n5. 坐标转换测试:")
    for entity in gui.simulation.entities:
        screen_pos = gui.world_to_screen_int(entity.position)
        print(f"   {entity.name}: 世界位置 {entity.position} -> 屏幕位置 {screen_pos}")
        
        # 检查是否在屏幕内
        in_screen = (0 <= screen_pos[0] <= gui.config.width and 
                    0 <= screen_pos[1] <= gui.config.height)
        print(f"     在屏幕内: {'是' if in_screen else '否'}")
    
    print(f"\n6. 渲染测试:")
    # 创建一个临时表面来测试渲染
    test_surface = pygame.Surface((gui.config.width, gui.config.height))
    test_surface.fill((0, 0, 0))
    
    # 保存原始屏幕
    original_screen = gui.screen
    gui.screen = test_surface
    
    # 测试绘制实体
    print("   绘制实体...")
    try:
        gui.draw_entities()
        print("   实体绘制成功")
    except Exception as e:
        print(f"   实体绘制失败: {e}")
    
    # 测试绘制对象
    print("   绘制对象...")
    try:
        gui.draw_objects()
        print("   对象绘制成功")
    except Exception as e:
        print(f"   对象绘制失败: {e}")
    
    # 恢复原始屏幕
    gui.screen = original_screen
    
    print(f"\n7. 模拟更新测试:")
    # 更新模拟一次
    gui.update_simulation()
    print(f"   更新后实体数量: {len(gui.simulation.entities)}")
    print(f"   更新后对象数量: {len(gui.simulation.objects)}")
    
    print(f"\n=== 调试完成 ===")
    
    # 总结问题
    print(f"\n可能的问题:")
    if len(gui.simulation.entities) < 3:
        print(f"  - 实体加载不完整（期望3个，实际{len(gui.simulation.entities)}个）")
        print(f"  - 检查_load_initial_scenario方法")
    else:
        print(f"  - 实体加载成功（{len(gui.simulation.entities)}个）")
        print(f"  - 问题可能在渲染或坐标转换")
    
    return gui

if __name__ == "__main__":
    pygame.init()
    try:
        debug_gui_state()
    finally:
        pygame.quit()