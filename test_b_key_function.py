#!/usr/bin/env python3
"""
测试B键查看对象/实体参数的功能
"""

import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_b_key_logic():
    """测试B键逻辑"""
    print("=== 测试B键查看对象/实体参数的功能 ===")
    
    # 分析当前代码逻辑
    print("\n1. B键功能分析:")
    print("   - B键和TAB键功能相同：切换选中对象或实体")
    print("   - 优先切换对象，如果没有对象则切换实体")
    print("   - 选中后信息面板会显示选中对象/实体的参数")
    
    print("\n2. 可能的问题:")
    print("   a) 用户不知道需要先选中对象/实体才能看到参数")
    print("   b) 信息面板可能被其他UI元素遮挡")
    print("   c) 字体颜色可能与背景相似导致看不见")
    print("   d) 模拟暂停时B键可能不响应")
    
    print("\n3. 建议的修复方案:")
    print("   a) 改进用户提示：在信息面板中明确显示'按B键查看参数'")
    print("   b) 确保信息面板始终可见且可读")
    print("   c) 添加调试输出，确认B键被按下")
    print("   d) 修复可能的字体或颜色问题")
    
    print("\n4. 代码检查点:")
    print("   - gui/gui_manager.py 第841行: B键事件处理")
    print("   - gui/gui_manager.py 第566行: draw_info_panel函数")
    print("   - 确保selected_object_id和selected_entity_id正确设置")
    
    return True

def create_fix_suggestion():
    """创建修复建议"""
    print("\n=== 修复建议 ===")
    
    fix_code = '''
# 修复1: 在draw_info_panel中添加更明确的提示
def draw_info_panel(self):
    """绘制信息面板"""
    # ... 现有代码 ...
    
    if not self.selected_object_id and not self.selected_entity_id:
        # 没有选中任何对象或实体时显示提示
        text = self.font_small.render("按B或TAB键选择对象/实体查看参数", True, (255, 255, 255))
        self.screen.blit(text, (left_panel_rect.x + 10, left_panel_rect.y + y_offset))
        y_offset += 20

# 修复2: 在B键事件处理中添加调试输出
elif event.key == pygame.K_TAB or event.key == pygame.K_b:
    print(f"[DEBUG] B键按下: 当前选中对象={self.selected_object_id}, 实体={self.selected_entity_id}")
    # ... 现有切换逻辑 ...

# 修复3: 确保信息面板背景足够不透明
pygame.draw.rect(self.screen, (0, 0, 0, 230), left_panel_rect)  # 增加不透明度

# 修复4: 添加键盘帮助提示
def draw_controls_help(self):
    """绘制控制帮助"""
    # 添加B键说明
    help_lines = [
        # ... 现有行 ...
        "B/TAB: 切换选中对象/实体并查看参数",
        # ... 其他行 ...
    ]
'''
    
    print(fix_code)
    
    print("\n=== 测试步骤 ===")
    print("1. 运行GUI")
    print("2. 按B键或TAB键切换选中对象/实体")
    print("3. 查看左上角信息面板是否显示参数")
    print("4. 如果没有显示，检查控制台是否有调试输出")

if __name__ == "__main__":
    test_b_key_logic()
    create_fix_suggestion()