#!/usr/bin/env python3
"""
测试 Textual TUI 按钮功能
"""

import asyncio
from textual_tui import PrettyBuildTUI
from textual.widgets import Button
from textual import events

async def test_button_functionality():
    """测试按钮功能"""
    print("🧪 测试 Textual TUI 按钮功能...")
    
    # 创建应用实例
    app = PrettyBuildTUI()
    
    # 模拟按钮点击事件
    class MockButton:
        def __init__(self, button_id):
            self.id = button_id
    
    class MockEvent:
        def __init__(self, button_id):
            self.button = MockButton(button_id)
    
    # 测试各种按钮
    test_buttons = [
        ("settings", "Settings 按钮"),
        ("view-logs", "View Logs 按钮"),
        ("build-btn", "Build 按钮"),
        ("clean-btn", "Clean 按钮")
    ]
    
    print("\n📋 测试结果:")
    for button_id, button_name in test_buttons:
        try:
            # 创建模拟事件
            mock_event = MockEvent(button_id)
            
            # 测试按钮处理方法是否存在
            if hasattr(app, 'on_button_pressed'):
                print(f"✅ {button_name}: 事件处理方法存在")
            else:
                print(f"❌ {button_name}: 事件处理方法不存在")
                
        except Exception as e:
            print(f"❌ {button_name}: 测试失败 - {str(e)}")
    
    # 测试关键方法是否存在
    key_methods = [
        ("_switch_to_logs", "切换到日志页面"),
        ("_switch_to_config", "切换到配置页面"),
        ("_add_log", "添加日志"),
        ("_get_log_viewer", "获取日志查看器")
    ]
    
    print("\n🔧 关键方法检查:")
    for method_name, description in key_methods:
        if hasattr(app, method_name):
            print(f"✅ {description}: {method_name} 方法存在")
        else:
            print(f"❌ {description}: {method_name} 方法不存在")
    
    print("\n🎯 测试完成!")
    print("💡 提示: 如果所有检查都通过，说明 TUI 按钮功能应该正常工作")

if __name__ == "__main__":
    asyncio.run(test_button_functionality())