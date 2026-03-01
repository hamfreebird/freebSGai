#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试相机坐标转换
"""

import numpy as np

def test_world_to_screen():
    """测试世界坐标到屏幕坐标转换"""
    
    # 模拟相机参数
    camera_position = np.array([0.0, 0.0])
    camera_zoom = 1e-9
    config_width = 1920
    config_height = 1080
    
    # 测试位置（地球位置）
    world_pos = np.array([1.496e11, 0.0])
    
    # 计算相对位置
    relative_x = world_pos[0] - camera_position[0]
    relative_y = world_pos[1] - camera_position[1]
    
    print("=== 世界坐标到屏幕坐标转换测试 ===")
    print(f"世界位置: {world_pos}")
    print(f"相机位置: {camera_position}")
    print(f"相机缩放: {camera_zoom}")
    print(f"屏幕尺寸: {config_width}x{config_height}")
    print()
    
    print("计算过程:")
    print(f"相对位置: ({relative_x:.2e}, {relative_y:.2e})")
    print(f"相对位置 * 缩放: ({relative_x * camera_zoom:.2f}, {relative_y * camera_zoom:.2f})")
    
    # 浮点数坐标
    screen_x_float = config_width // 2 + relative_x * camera_zoom
    screen_y_float = config_height // 2 + relative_y * camera_zoom
    print(f"浮点数屏幕坐标: ({screen_x_float:.2f}, {screen_y_float:.2f})")
    
    # 整数坐标
    screen_x_int = int(screen_x_float)
    screen_y_int = int(screen_y_float)
    print(f"整数屏幕坐标: ({screen_x_int}, {screen_y_int})")
    
    print()
    print("类型检查:")
    print(f"浮点数坐标类型: {type(screen_x_float)}, {type(screen_y_float)}")
    print(f"整数坐标类型: {type(screen_x_int)}, {type(screen_y_int)}")
    print(f"整数元组: {type((screen_x_int, screen_y_int))}")
    
    # 测试Pygame draw.circle参数
    print()
    print("Pygame draw.circle参数测试:")
    print("正确: pygame.draw.circle(screen, color, (x, y), radius)")
    print(f"示例: pygame.draw.circle(screen, color, ({screen_x_int}, {screen_y_int}), 10)")
    
    # 测试错误情况
    print()
    print("常见错误:")
    print("1. 传递元组而不是两个单独的数字: (x, y) 而不是 x, y")
    print("2. 坐标不是数字类型")
    print("3. 坐标是numpy数组而不是Python标量")

if __name__ == "__main__":
    test_world_to_screen()