#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pretty Build - 标准pip安装脚本
支持: pip install -e . 或 pip install .
"""

from setuptools import setup, find_packages
from pathlib import Path
import json

# 读取README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# 读取依赖
requirements = []
requirements_file = this_directory / "requirements.txt"
if requirements_file.exists():
    with open(requirements_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                requirements.append(line)

setup(
    name="pretty-build",
    version="1.1.0",
    author="Pretty Build Team",
    author_email="team@prettybuild.dev",
    description="增强型构建系统包装器 - 美观的构建界面和实时监控",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/prettybuild/pretty-build",
    project_urls={
        "Bug Tracker": "https://github.com/prettybuild/pretty-build/issues",
        "Documentation": "https://prettybuild.readthedocs.io/",
        "Source Code": "https://github.com/prettybuild/pretty-build",
    },
    
    # 包配置 - 直接指定包
    py_modules=["pretty_build", "textual_tui"],
    package_dir={"": "src"},
    
    # 包含非Python文件
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.cfg", "*.conf", "*.example"],
    },
    
    # 依赖
    python_requires=">=3.8",
    install_requires=requirements,
    
    # 可选依赖
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "notifications": [
            "plyer>=2.0",
        ],
        "config": [
            "configparser>=5.0",
        ],
    },
    
    # 分类
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: User Interfaces",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Environment :: Console :: Curses",
    ],
    
    # 关键词
    keywords="build, cmake, make, tui, textual, monitoring, embedded, stm32",
    
    # 入口点
    entry_points={
        "console_scripts": [
            "pretty-build=pretty_build:main",
            "pretty-build-tui=pretty_build:main_tui",
            "pb=pretty_build:main",
            "pbt=pretty_build:main_tui",
        ],
    },
    
    # 数据文件
    data_files=[
        ("share/pretty-build/config", ["config/.pretty_build.conf.example"]),
        ("share/pretty-build/templates", ["config/templates/stm32f103c8t6.cfg"]),
        ("share/pretty-build/scripts", ["scripts/start.bat", "scripts/start.sh"]),
        ("share/pretty-build/docs", [
            "docs/TUI_README.md",
            "docs/TEXTUAL_QUICKSTART.md", 
            "docs/INSTALL_GUIDE.md",
            "docs/USAGE_GUIDE.md"
        ]),
        ("share/pretty-build/examples", [
            "examples/demo.py",
            "examples/demo_tui.py"
        ]),
        ("share/pretty-build/examples/tests", [
            "examples/tests/test_textual_tui.py",
            "examples/tests/test_tui_buttons.py"
        ]),
    ],
    
    # 压缩安全
    zip_safe=False,
)
