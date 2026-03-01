#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试相机移动和缩放逻辑
"""

import numpy as np

def test_camera_logic():
    """测试相机移动和缩放逻辑"""
    
    # 模拟当前配置
    camera_move_speed = 1e9  # 米/秒
    camera_zoom = 1e-9  # 初始缩放
    fps = 60
    
    print("=== 相机移动和缩放逻辑测试 ===")
    print(f"相机移动速度: {camera_move_speed} 米/秒")
    print(f"初始缩放: {camera_zoom} 像素/米")
    print(f"FPS: {fps}")
    print()
    
    # 测试不同缩放级别下的移动距离
    zoom_levels = [1e-9, 1e-8, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1.0]
    
    print("缩放级别 vs 每帧移动距离:")
    for zoom in zoom_levels:
        move_distance = camera_move_speed / zoom * (1/fps)
        print(f"  缩放 {zoom:.1e} -> 每帧移动 {move_distance:.1e} 米")
    
    print()
    
    # 测试世界坐标到屏幕坐标转换
    print("世界坐标到屏幕坐标转换测试:")
    camera_position = np.array([0.0, 0.0])
    world_pos = np.array([1.496e11, 0.0])  # 地球位置
    
    for zoom in [1e-9, 1e-8, 1e-7]:
        relative_x = world_pos[0] - camera_position[0]
        relative_y = world_pos[1] - camera_position[1]
        screen_x = 1920 // 2 + int(relative_x * zoom)
        screen_y = 1080 // 2 + int(relative_y * zoom)
        
        print(f"  缩放 {zoom:.1e}: 世界位置 {world_pos[0]:.2e} -> 屏幕位置 ({screen_x}, {screen_y})")
        print(f"    相对位置: {relative_x:.2e}, 乘积: {relative_x * zoom:.2f}, 取整: {int(relative_x * zoom)}")
    
    print()
    
    # 分析问题
    print("=== 问题分析 ===")
    print("1. 移动速度与缩放成反比:")
    print("   - 缩放越小（放大），移动速度越大")
    print("   - 缩放越大（缩小），移动速度越小")
    print("   - 这导致用户体验不一致")
    print()
    
    print("2. 坐标转换精度问题:")
    print("   - 使用int()转换可能导致精度损失")
    print("   - 当缩放很小时，relative_x * zoom可能小于1，取整后为0")
    print()
    
    print("3. 建议的修复方案:")
    print("   a. 移动速度应该与缩放级别成正比或保持恒定")
    print("   b. 使用浮点数坐标进行渲染，避免过早取整")
    print("   c. 添加平滑缩放和移动过渡")

if __name__ == "__main__":
    test_camera_logic()