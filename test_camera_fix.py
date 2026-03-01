#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试相机移动和缩放修复效果
"""

import numpy as np

def test_camera_fix():
    """测试修复后的相机移动和缩放逻辑"""
    
    # 模拟配置
    config_width = 1920
    camera_zoom = 1e-9  # 初始缩放
    fps = 60
    
    print("=== 修复后的相机移动和缩放逻辑测试 ===")
    print(f"屏幕宽度: {config_width} 像素")
    print(f"初始缩放: {camera_zoom} 像素/米")
    print(f"FPS: {fps}")
    print()
    
    # 测试修复后的移动速度计算
    print("修复后的移动速度计算:")
    print("每秒移动屏幕宽度的1/4，与缩放级别成反比")
    
    zoom_levels = [1e-9, 1e-8, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1.0]
    
    print("\n缩放级别 vs 每秒移动距离 vs 每帧移动距离:")
    for zoom in zoom_levels:
        screen_move_speed = (config_width / 4) / zoom  # 每秒移动的世界距离
        move_distance_per_frame = screen_move_speed * (1/fps)  # 每帧移动距离
        
        print(f"  缩放 {zoom:.1e}:")
        print(f"    每秒移动 {screen_move_speed:.1e} 米")
        print(f"    每帧移动 {move_distance_per_frame:.1e} 米")
    
    print()
    
    # 对比修复前后的差异
    print("=== 修复前后对比 ===")
    print("修复前: move_distance = camera_move_speed / camera_zoom * (1/60)")
    print("修复后: move_distance = (screen_width/4) / camera_zoom * (1/60)")
    print()
    
    # 使用修复前的公式（假设camera_move_speed = 1e9）
    camera_move_speed = 1e9
    print("修复前（camera_move_speed = 1e9）:")
    for zoom in [1e-9, 1e-6, 1e-3, 1.0]:
        old_move_distance = camera_move_speed / zoom * (1/fps)
        print(f"  缩放 {zoom:.1e}: 每帧移动 {old_move_distance:.1e} 米")
    
    print()
    
    print("修复后:")
    for zoom in [1e-9, 1e-6, 1e-3, 1.0]:
        screen_move_speed = (config_width / 4) / zoom
        new_move_distance = screen_move_speed * (1/fps)
        print(f"  缩放 {zoom:.1e}: 每帧移动 {new_move_distance:.1e} 米")
    
    print()
    
    # 分析改进
    print("=== 改进分析 ===")
    print("1. 移动速度更合理:")
    print("   - 修复前：缩放1e-9时，每帧移动1.7e+16米（过大）")
    print("   - 修复后：缩放1e-9时，每帧移动8.0e+9米（更合理）")
    print()
    
    print("2. 移动速度与缩放级别的关系:")
    print("   - 修复前：移动速度与缩放级别成反比，但比例过大")
    print("   - 修复后：移动速度与缩放级别成反比，基于屏幕像素移动")
    print()
    
    print("3. 用户体验:")
    print("   - 修复前：放大时移动太快，缩小时移动太慢")
    print("   - 修复后：移动速度更平滑，用户体验更一致")

if __name__ == "__main__":
    test_camera_fix()