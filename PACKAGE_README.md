# Pretty Build v1.1.0

## 📦 包结构

这个包采用清晰的目录结构组织:

```
pretty_build_v1.1.0/
├── README.md                    # 主要文档
├── requirements.txt             # Python依赖
├── setup.py                     # 自动安装脚本
├── src/                         # 核心程序
│   ├── pretty_build.py          # 主程序
│   └── textual_tui.py           # TUI界面
├── examples/                    # 演示和测试
│   ├── demo.py                  # 功能演示
│   ├── demo_tui.py              # TUI演示
│   └── tests/                   # 测试文件
│       ├── test_textual_tui.py  # TUI测试
│       └── test_tui_buttons.py  # 按钮测试
├── docs/                        # 文档
│   ├── TUI_README.md            # TUI使用说明
│   ├── TEXTUAL_QUICKSTART.md    # 快速开始指南
│   └── INSTALL_GUIDE.md         # 安装指南
├── config/                      # 配置文件
│   ├── .pretty_build.conf.example  # 配置模板
│   └── templates/               # 配置模板
│       └── stm32f103c8t6.cfg    # STM32配置
└── scripts/                     # 启动脚本
    ├── start.bat                # Windows启动脚本
    └── start.sh                 # Linux/macOS启动脚本
```

## 🚀 快速开始

### 1. 安装依赖
```bash
python setup.py
```

### 2. 运行程序
```bash
# 标准模式
python src/pretty_build.py

# TUI模式
python src/pretty_build.py --tui

# 使用启动脚本 (推荐)
# Windows:
scripts/start.bat

# Linux/macOS:
chmod +x scripts/start.sh
scripts/start.sh
```

### 3. 查看演示
```bash
python examples/demo.py          # 基本演示
python examples/demo_tui.py      # TUI演示
```

## 📋 系统要求

- **Python**: 3.8+
- **操作系统**: Windows/Linux/macOS
- **终端**: 支持ANSI颜色和Unicode

## 🎯 主要功能

- ✨ **美观界面**: 现代化的构建界面
- ⚡ **实时监控**: 构建过程实时监控
- 🧠 **智能缓存**: 增量构建支持
- 🔌 **插件系统**: 可扩展的插件架构
- 🖥️ **TUI界面**: 基于Textual的现代TUI
- ⚙️ **配置管理**: 灵活的配置系统
- 🔔 **通知系统**: 构建状态通知

## 📚 文档

- `docs/TUI_README.md` - TUI详细使用说明
- `docs/TEXTUAL_QUICKSTART.md` - 快速开始指南
- `docs/INSTALL_GUIDE.md` - 详细安装指南

## ⚙️ 配置

1. 复制配置模板:
   ```bash
   cp config/.pretty_build.conf.example .pretty_build.conf
   ```

2. 编辑配置文件根据需要调整设置

## 🔧 开发和测试

```bash
# 运行测试
python examples/tests/test_textual_tui.py
python examples/tests/test_tui_buttons.py

# 查看功能演示
python examples/demo.py
python examples/demo_tui.py
```

## 📞 支持

如有问题，请查看 `docs/` 目录下的文档或联系开发团队。

---
**构建信息**
- 版本: 1.1.0
- 构建时间: 2025-07-29 15:24:24
- 包结构: 分层目录组织
