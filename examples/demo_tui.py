#!/usr/bin/env python3
"""
Pretty Build TUI Demo - Textual 版本
演示 Pretty Build 的 Textual TUI 功能
"""

import sys
import subprocess
import time
from pathlib import Path


def main():
    """演示 Pretty Build TUI 功能"""
    print("🚀 Pretty Build TUI Demo - Textual 版本")
    print("=" * 50)

    # 检查 pretty_build.py 是否存在
    if not Path("pretty_build.py").exists():
        print("❌ 错误: 找不到 pretty_build.py 文件")
        print("请确保在正确的目录中运行此脚本")
        return 1

    print("📋 可用的演示选项:")
    print("1. 启动 Textual TUI 界面")
    print("2. 查看 TUI 帮助信息")
    print("3. 查看构建系统信息")
    print("4. 退出")

    while True:
        try:
            choice = input("\n请选择一个选项 (1-4): ").strip()

            if choice == "1":
                print("\n🚀 启动 Textual TUI 界面...")
                print("提示: 使用 Ctrl+C 退出 TUI")
                time.sleep(2)

                # 启动 Textual TUI
                try:
                    subprocess.run([sys.executable, "pretty_build.py", "--tui"])
                except KeyboardInterrupt:
                    print("\n✅ TUI 已退出")
                except Exception as e:
                    print(f"\n❌ 启动 TUI 失败: {e}")

            elif choice == "2":
                print("\n📖 显示 TUI 帮助信息...")
                subprocess.run([sys.executable, "pretty_build.py", "--help"])

            elif choice == "3":
                print("\n🔍 显示构建系统信息...")
                subprocess.run([sys.executable, "pretty_build.py"])

            elif choice == "4":
                print("\n👋 再见!")
                break

            else:
                print("❌ 无效选择，请输入 1-4")

        except KeyboardInterrupt:
            print("\n\n👋 演示已取消，再见!")
            break
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")
            break

    return 0


if __name__ == "__main__":
    sys.exit(main())
