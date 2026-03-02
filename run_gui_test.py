#!/usr/bin/env python3
"""
运行GUI测试
"""
import sys
import os
import pygame

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.gui_manager import GUIManager

def main():
    """运行GUI测试"""
    print("启动GUI测试")
    print("=" * 60)
    print("控制说明:")
    print("  ESC: 退出")
    print("  WASD: 移动视野")
    print("  Q/E: 缩放")
    print("  Space: 暂停/继续")
    print("  TAB: 切换选中对象")
    print("=" * 60)
    
    try:
        # 创建GUI管理器
        gui = GUIManager("config.json")
        
        # 运行主循环
        clock = pygame.time.Clock()
        running = True
        frame_count = 0
        
        print("\n开始测试...")
        print("如果能看到太阳、地球、火星和飞船，说明修复成功")
        print("如果看不到，请检查控制台输出")
        
        while running and frame_count < 300:  # 运行5秒（60 FPS × 5）
            # 处理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        print("用户按ESC退出")
            
            # 更新模拟
            gui.update_simulation()
            
            # 渲染
            gui.render()
            
            # 更新FPS
            gui.update_fps()
            
            # 每60帧打印一次状态
            if frame_count % 60 == 0:
                seconds = frame_count // 60
                print(f"运行时间: {seconds}秒, FPS: {gui.fps:.1f}")
                print(f"实体数量: {len(gui.simulation.entities)}, 对象数量: {len(gui.simulation.objects)}")
                
                # 打印实体位置
                for entity in gui.simulation.entities:
                    screen_pos = gui.world_to_screen_int(entity.position)
                    print(f"  {entity.name}: 屏幕位置({screen_pos[0]}, {screen_pos[1]})")
            
            clock.tick(60)
            frame_count += 1
        
        pygame.quit()
        print(f"\n测试完成，共运行{frame_count}帧")
        
        # 总结
        print("\n测试总结:")
        print(f"  实体数量: {len(gui.simulation.entities)}")
        print(f"  对象数量: {len(gui.simulation.objects)}")
        print(f"  相机缩放: {gui.camera_zoom}")
        print(f"  相机位置: {gui.camera_position}")
        
        # 检查实体是否可见
        print("\n实体可见性检查:")
        for entity in gui.simulation.entities:
            screen_pos = gui.world_to_screen_int(entity.position)
            in_screen = (0 <= screen_pos[0] <= gui.config.width and 
                        0 <= screen_pos[1] <= gui.config.height)
            print(f"  {entity.name}: 在屏幕内={'是' if in_screen else '否'}, 位置({screen_pos[0]}, {screen_pos[1]})")
        
        return True
        
    except Exception as e:
        print(f"GUI测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)