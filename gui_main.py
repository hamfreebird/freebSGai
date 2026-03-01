#!/usr/bin/env python3
"""
2D宇宙太空战物理模拟 - GUI主程序
基于pygame的图形界面，提供完整的模拟控制和可视化
"""
import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.gui_manager import GUIManager


def main():
    """主函数"""
    print("=" * 60)
    print("2D Space Combat Physics Simulator - GUI Version")
    print("=" * 60)
    
    try:
        # 创建GUI管理器
        gui = GUIManager("config.json")
        
        # 运行主循环
        gui.run()
        
    except FileNotFoundError as e:
        print(f"错误: 配置文件未找到 - {e}")
        print("请确保config.json文件存在")
        return 1
    except ImportError as e:
        print(f"错误: 模块导入失败 - {e}")
        print("请确保所有依赖已安装: pip install pygame numpy")
        return 1
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())