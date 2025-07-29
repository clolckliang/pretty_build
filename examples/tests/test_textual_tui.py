#!/usr/bin/env python3
"""
Textual TUI 独立测试脚本
直接测试 Textual TUI 功能，不依赖 pretty_build.py
"""

from textual_tui import run_textual_tui

def main():
    """运行 Textual TUI 测试"""
    print("🚀 启动 Textual TUI 独立测试...")
    print("提示: 使用 Ctrl+C 退出")
    
    # 模拟配置对象
    class MockConfig:
        def __init__(self):
            self.build_command = "ninja"
            self.clean_command = "ninja clean"
            self.output_dir = "build"
            self.parallel_jobs = 4
            self.enable_notifications = True
    
    config = MockConfig()
    
    try:
        run_textual_tui(config=config)
        print("✅ TUI 测试完成")
    except KeyboardInterrupt:
        print("\n✅ TUI 已退出")
    except Exception as e:
        print(f"❌ TUI 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()