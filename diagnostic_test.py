#!/usr/bin/env python3
"""
详细诊断测试
"""
import numpy as np
import sys
import os
import json

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from entities.entity import Entity, Object
from gui.gui_manager import GUIManager

def test_config_loading():
    """测试配置文件加载"""
    print("=== 测试配置文件加载 ===")
    
    try:
        with open("config.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"配置文件加载成功")
        print(f"场景名称: {data['initial_scenario']['name']}")
        print(f"实体数量: {len(data['initial_scenario']['entities'])}")
        print(f"对象数量: {len(data['initial_scenario']['objects'])}")
        
        # 打印实体详情
        print("\n实体详情:")
        for i, entity_data in enumerate(data['initial_scenario']['entities']):
            print(f"  实体 {i}: {entity_data['name']}")
            print(f"    类型: {entity_data['type']}")
            print(f"    位置: {entity_data['position']}")
            print(f"    速度: {entity_data['velocity']}")
            print(f"    颜色: {entity_data['color']}")
        
        # 打印对象详情
        print("\n对象详情:")
        for i, object_data in enumerate(data['initial_scenario']['objects']):
            print(f"  对象 {i}: {object_data['label']}")
            print(f"    类型: {object_data['type']}")
            print(f"    位置: {object_data['position']}")
            print(f"    速度: {object_data['velocity']}")
            print(f"    颜色: {object_data['color']}")
            
        return True
    except Exception as e:
        print(f"配置文件加载失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_entity_creation():
    """测试实体创建"""
    print("\n=== 测试实体创建 ===")
    
    try:
        # 创建GUI管理器
        gui = GUIManager("config.json")
        
        print(f"模拟实体数量: {len(gui.simulation.entities)}")
        print(f"模拟对象数量: {len(gui.simulation.objects)}")
        
        # 检查每个实体
        print("\n实体检查:")
        for i, entity in enumerate(gui.simulation.entities):
            print(f"  实体 {i}: {entity.name}")
            print(f"    ID: {entity.id}")
            print(f"    质量: {entity.mass:.2e} kg")
            print(f"    半径: {entity.radius:.2e} m")
            print(f"    位置: ({entity.position[0]:.2e}, {entity.position[1]:.2e})")
            print(f"    速度: ({entity.velocity[0]:.2f}, {entity.velocity[1]:.2f}) m/s")
            print(f"    颜色: {entity.color}")
            print(f"    密度: {entity.density:.2f} kg/m³")
            
            # 检查颜色是否有效
            if len(entity.color) != 3:
                print(f"    [错误] 颜色格式不正确: {entity.color}")
            else:
                r, g, b = entity.color
                if not (0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255):
                    print(f"    [错误] 颜色值超出范围: {entity.color}")
        
        # 检查每个对象
        print("\n对象检查:")
        for i, obj in enumerate(gui.simulation.objects):
            print(f"  对象 {i}: {obj.label}")
            print(f"    ID: {obj.id}")
            print(f"    位置: ({obj.position[0]:.2e}, {obj.position[1]:.2e})")
            print(f"    速度: ({obj.velocity[0]:.2f}, {obj.velocity[1]:.2f}) m/s")
            print(f"    颜色: {getattr(obj, 'color', '未设置')}")
            print(f"    剩余dv: {obj.remaining_dv:.1f} m/s")
            
            # 检查颜色属性
            if hasattr(obj, 'color'):
                color = obj.color
                if len(color) != 3:
                    print(f"    [错误] 颜色格式不正确: {color}")
                else:
                    r, g, b = color
                    if not (0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255):
                        print(f"    [错误] 颜色值超出范围: {color}")
            else:
                print(f"    [警告] 对象没有颜色属性")
        
        return True
    except Exception as e:
        print(f"实体创建测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_coordinate_system():
    """测试坐标系"""
    print("\n=== 测试坐标系 ===")
    
    try:
        gui = GUIManager("config.json")
        
        print(f"屏幕尺寸: {gui.config.width} x {gui.config.height}")
        print(f"相机位置: {gui.camera_position}")
        print(f"相机缩放: {gui.camera_zoom}")
        
        # 测试坐标转换
        test_points = [
            ("原点", np.array([0.0, 0.0])),
            ("地球位置", np.array([1.496e11, 0.0])),
            ("火星位置", np.array([2.279e11, 0.0])),
            ("飞船位置", np.array([1.496e11, 1e10])),
        ]
        
        for name, world_pos in test_points:
            screen_pos = gui.world_to_screen_int(world_pos)
            print(f"  {name}:")
            print(f"    世界坐标: ({world_pos[0]:.2e}, {world_pos[1]:.2e})")
            print(f"    屏幕坐标: ({screen_pos[0]}, {screen_pos[1]})")
            
            # 检查是否在屏幕内
            in_screen = (0 <= screen_pos[0] <= gui.config.width and 
                        0 <= screen_pos[1] <= gui.config.height)
            print(f"    在屏幕内: {'是' if in_screen else '否'}")
        
        return True
    except Exception as e:
        print(f"坐标系测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_drawing_functions():
    """测试绘制函数"""
    print("\n=== 测试绘制函数 ===")
    
    try:
        gui = GUIManager("config.json")
        
        # 测试实体绘制逻辑
        print("实体绘制逻辑:")
        for entity in gui.simulation.entities:
            entity_name_lower = entity.name.lower()
            if "太阳" in entity.name or "star" in entity_name_lower:
                radius = 15
                type_name = "太阳"
            elif "行星" in entity.name or "planet" in entity_name_lower:
                radius = 8
                type_name = "行星"
            elif "小行星" in entity.name or "asteroid" in entity_name_lower:
                radius = 4
                type_name = "小行星"
            else:
                radius = 6
                type_name = "默认"
            
            print(f"  {entity.name}: 类型={type_name}, 视觉半径={radius}像素")
        
        # 测试对象绘制逻辑
        print("\n对象绘制逻辑:")
        for obj in gui.simulation.objects:
            size = 8  # 固定大小
            print(f"  {obj.label}: 大小={size}像素")
        
        return True
    except Exception as e:
        print(f"绘制函数测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_edge_indicators():
    """测试边缘箭头指示"""
    print("\n=== 测试边缘箭头指示 ===")
    
    try:
        # 检查是否有draw_edge_indicators函数
        gui = GUIManager("config.json")
        
        if hasattr(gui, 'draw_edge_indicators'):
            print("draw_edge_indicators函数存在")
            
            # 检查函数实现
            import inspect
            source = inspect.getsource(gui.draw_edge_indicators)
            print(f"函数长度: {len(source)} 字符")
            
            # 简单分析函数
            if "pygame.draw" in source:
                print("函数包含pygame.draw调用")
            else:
                print("警告: 函数可能不包含绘制代码")
                
            if "arrow" in source.lower() or "triangle" in source.lower():
                print("函数包含箭头或三角形绘制")
            else:
                print("警告: 函数可能不绘制箭头")
        else:
            print("错误: draw_edge_indicators函数不存在!")
            
        return True
    except Exception as e:
        print(f"边缘指示器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("详细诊断测试")
    print("=" * 60)
    
    tests = [
        ("配置文件加载", test_config_loading),
        ("实体创建", test_entity_creation),
        ("坐标系", test_coordinate_system),
        ("绘制函数", test_drawing_functions),
        ("边缘箭头指示", test_edge_indicators),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n执行测试: {test_name}")
        print("-" * 40)
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"测试异常: {e}")
            results.append((test_name, False))
    
    # 打印总结
    print("\n" + "=" * 60)
    print("测试总结:")
    print("-" * 40)
    
    all_passed = True
    for test_name, success in results:
        status = "通过" if success else "失败"
        print(f"  {test_name}: {status}")
        if not success:
            all_passed = False
    
    print("\n总体结果:", "所有测试通过" if all_passed else "有测试失败")
    
    if not all_passed:
        print("\n建议:")
        print("1. 检查config.json文件格式是否正确")
        print("2. 检查实体和对象的创建逻辑")
        print("3. 检查绘制函数的实现")
        print("4. 运行实际GUI测试查看具体问题")

if __name__ == "__main__":
    main()