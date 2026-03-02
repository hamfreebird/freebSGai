#!/usr/bin/env python3
"""
测试修复结果
"""
import numpy as np
import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from entities.entity import Entity
from gui.gui_manager import GUIManager

def test_fixed_entity_drawing():
    """测试修复后的实体绘制"""
    print("=== 测试修复后的实体绘制 ===")
    
    # 创建GUI管理器
    gui = GUIManager("config.json")
    
    print(f"相机缩放: {gui.camera_zoom}")
    print(f"实体数量: {len(gui.simulation.entities)}")
    print(f"对象数量: {len(gui.simulation.objects)}")
    
    # 测试坐标转换
    for entity in gui.simulation.entities:
        screen_pos = gui.world_to_screen_int(entity.position)
        print(f"\n实体: {entity.name}")
        print(f"  世界坐标: ({entity.position[0]:.2e}, {entity.position[1]:.2e})")
        print(f"  屏幕坐标: ({screen_pos[0]}, {screen_pos[1]})")
        print(f"  颜色: {entity.color}")
        
        # 检查是否在屏幕内
        if 0 <= screen_pos[0] <= gui.config.width and 0 <= screen_pos[1] <= gui.config.height:
            print("  状态: 在屏幕内 [OK]")
        else:
            print("  状态: 在屏幕外 [OUT]")
    
    # 测试对象
    for obj in gui.simulation.objects:
        screen_pos = gui.world_to_screen_int(obj.position)
        print(f"\n对象: {obj.label}")
        print(f"  世界坐标: ({obj.position[0]:.2e}, {obj.position[1]:.2e})")
        print(f"  屏幕坐标: ({screen_pos[0]}, {screen_pos[1]})")
        print(f"  颜色: {getattr(obj, 'color', '默认')}")
        
        if 0 <= screen_pos[0] <= gui.config.width and 0 <= screen_pos[1] <= gui.config.height:
            print("  状态: 在屏幕内 [OK]")
        else:
            print("  状态: 在屏幕外 [OUT]")

def test_visual_sizes():
    """测试视觉大小"""
    print("\n=== 测试视觉大小 ===")
    
    # 测试不同实体的视觉大小
    test_entities = [
        ("太阳", "太阳", (255, 255, 200)),
        ("地球", "行星", (100, 200, 255)),
        ("火星", "行星", (255, 150, 100)),
        ("小行星带", "小行星", (150, 150, 150)),
    ]
    
    for name, entity_type, color in test_entities:
        if "太阳" in name or "star" in name.lower():
            radius = 15
        elif "行星" in name or "planet" in name.lower():
            radius = 8
        elif "小行星" in name or "asteroid" in name.lower():
            radius = 4
        else:
            radius = 6
        
        print(f"{name} ({entity_type}): 视觉半径 = {radius} 像素")

def run_quick_gui_test():
    """运行快速GUI测试"""
    print("\n=== 运行快速GUI测试 ===")
    print("注意: 这将打开一个短暂的GUI窗口进行测试")
    print("按ESC键退出测试")
    
    try:
        # 导入pygame
        import pygame
        
        # 创建GUI管理器
        gui = GUIManager("config.json")
        
        # 运行几帧进行测试
        clock = pygame.time.Clock()
        running = True
        frame_count = 0
        
        while running and frame_count < 60:  # 运行约1秒
            # 处理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            
            # 更新模拟
            gui.update_simulation()
            
            # 渲染
            gui.render()
            
            # 更新FPS
            gui.update_fps()
            
            clock.tick(60)
            frame_count += 1
        
        pygame.quit()
        print("GUI测试完成")
        
    except Exception as e:
        print(f"GUI测试错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_fixed_entity_drawing()
    test_visual_sizes()
    
    # 询问用户是否运行GUI测试
    print("\n是否运行GUI测试？(y/n)")
    response = input().strip().lower()
    if response == 'y':
        run_quick_gui_test()
    else:
        print("跳过GUI测试")