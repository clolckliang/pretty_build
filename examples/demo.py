#!/usr/bin/env python3
"""
Pretty Build Demo Script
演示 Pretty Build 的各种功能
"""

import os
import sys
import time
import subprocess
from pathlib import Path

def print_header(title):
    """打印标题"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_step(step, description):
    """打印步骤"""
    print(f"\n🔸 步骤 {step}: {description}")
    print("-" * 40)

def run_demo():
    """运行演示"""
    print_header("Pretty Build 功能演示")
    
    print("这个演示将展示 Pretty Build 的各种功能:")
    print("• 美观的构建界面")
    print("• 实时性能监控")
    print("• 智能缓存系统")
    print("• 插件系统")
    print("• 交互式配置")
    print("• 通知系统")
    
    input("\n按 Enter 开始演示...")
    
    # 步骤 1: 显示帮助信息
    print_step(1, "显示帮助信息")
    os.system("python /../../pretty_build.py --help")
    input("\n按 Enter 继续...")
    
    # 步骤 2: 检查构建系统检测
    print_step(2, "构建系统检测")
    print("Pretty Build 会自动检测项目中的构建系统:")
    
    # 检查各种构建文件
    build_files = {
        "build.ninja": "Ninja",
        "Makefile": "Make", 
        "CMakeLists.txt": "CMake",
        "build/build.ninja": "Ninja (在 build 目录)",
        "build/Makefile": "Make (在 build 目录)"
    }
    
    for file_path, build_system in build_files.items():
        if Path(file_path).exists():
            print(f"✅ 发现 {build_system}: {file_path}")
        else:
            print(f"❌ 未找到 {build_system}: {file_path}")
    
    input("\n按 Enter 继续...")
    
    # 步骤 3: 配置文件演示
    print_step(3, "配置文件系统")
    print("Pretty Build 支持配置文件来保存设置:")
    
    config_file = Path(".pretty_build.conf")
    example_config = Path(".pretty_build.conf.example")
    
    if example_config.exists():
        print(f"✅ 示例配置文件: {example_config}")
        print("配置文件内容预览:")
        with open(example_config, 'r', encoding='utf-8') as f:
            lines = f.readlines()[:10]  # 显示前10行
            for line in lines:
                print(f"  {line.rstrip()}")
        print("  ...")
    
    if config_file.exists():
        print(f"✅ 当前配置文件: {config_file}")
    else:
        print(f"ℹ️  配置文件将在首次运行时创建: {config_file}")
    
    input("\n按 Enter 继续...")
    
    # 步骤 4: 依赖检查
    print_step(4, "依赖检查")
    print("检查 Pretty Build 的依赖项:")
    
    dependencies = [
        "rich",
        "click", 
        "psutil",
        "plyer",
        "configparser"
    ]
    
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep} - 已安装")
        except ImportError:
            print(f"❌ {dep} - 未安装")
    
    print("\n如果有缺失的依赖，请运行:")
    print("pip install -r requirements.txt")
    
    input("\n按 Enter 继续...")
    
    # 步骤 5: 功能特性展示
    print_step(5, "主要功能特性")
    
    features = [
        ("🎨 响应式界面", "自适应终端大小的美观界面"),
        ("⚡ 性能监控", "实时 CPU 和内存使用监控"),
        ("💾 智能缓存", "基于文件哈希的构建缓存"),
        ("🔌 插件系统", "可扩展的插件架构"),
        ("⌨️  交互控制", "构建过程中的实时控制"),
        ("🔔 通知系统", "跨平台构建完成通知"),
        ("📊 统计报告", "详细的构建统计和报告"),
        ("🛠️  多构建系统", "支持 Ninja、Make、CMake")
    ]
    
    for feature, description in features:
        print(f"{feature}: {description}")
        time.sleep(0.5)
    
    input("\n按 Enter 继续...")
    
    # 步骤 6: 键盘快捷键
    print_step(6, "交互式键盘快捷键")
    
    shortcuts = [
        ("P", "暂停/恢复构建"),
        ("Q", "退出构建"),
        ("C", "打开配置界面"),
        ("H", "显示帮助信息"),
        ("F", "性能监控界面"),
        ("G", "插件管理界面"),
        ("X", "缓存管理"),
        ("N", "通知设置")
    ]
    
    print("在构建过程中可以使用以下快捷键:")
    for key, description in shortcuts:
        print(f"  {key}: {description}")
    
    input("\n按 Enter 继续...")
    
    # 步骤 7: 使用示例
    print_step(7, "使用示例")
    
    examples = [
        "python pretty_build.py",
        "python pretty_build.py --config",
        "python pretty_build.py --clean",
        "python pretty_build.py --rebuild",
        "python pretty_build.py -j 8",
        "python pretty_build.py ninja -v",
        "python pretty_build.py -- VERBOSE=1"
    ]
    
    print("常用命令示例:")
    for example in examples:
        print(f"  {example}")
    
    print_header("演示完成")
    print("感谢您体验 Pretty Build!")
    print("现在您可以在项目中使用 Pretty Build 来获得更好的构建体验。")
    print("\n更多信息请查看 README.md 文件。")

if __name__ == "__main__":
    try:
        run_demo()
    except KeyboardInterrupt:
        print("\n\n演示被中断。")
    except Exception as e:
        print(f"\n演示过程中出现错误: {e}")
        sys.exit(1)