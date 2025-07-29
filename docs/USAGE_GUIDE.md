# Pretty Build 运行方式指南

## 🚀 多种运行方式

### 方式1: 直接使用可执行文件（推荐）
```bash
# 完整路径
C:\Users\James\AppData\Roaming\Python\Python311\Scripts\pretty-build.exe --tui

# 或者添加到PATH后直接使用
pretty-build --tui
```

### 方式2: 使用项目提供的批处理文件
```bash
# 在项目目录下
.\pretty-build-tui.bat        # 直接启动TUI
.\pretty-build.bat --help     # 查看帮助
.\pretty-build.bat --tui      # 启动TUI
```

### 方式3: Python模块方式
```bash
python -c "import pretty_build; pretty_build.main_tui()"
python -c "import pretty_build; pretty_build.main()" --tui
```

### 方式4: 添加到系统PATH（一次性设置）
1. 将 `C:\Users\James\AppData\Roaming\Python\Python311\Scripts` 添加到系统PATH
2. 重启终端后可直接使用：
   ```bash
   pretty-build --tui
   pb --tui
   pbt
   ```

## 🎯 推荐使用方式

**最简单**: 使用项目提供的批处理文件
```bash
.\pretty-build-tui.bat
```

**最通用**: 添加到PATH后使用
```bash
pretty-build --tui
```

## 📁 项目文件说明

- `pretty-build.bat` - 通用启动脚本，支持所有参数
- `pretty-build-tui.bat` - 专用TUI启动脚本
- `dist/pretty_build_v1.0.1.tar.gz` - pip安装包
- `dist/PIP_INSTALL_GUIDE.md` - 详细安装指南

## ✅ 验证安装

```bash
# 检查安装状态
pip show pretty-build

# 测试功能
.\pretty-build.bat --help
.\pretty-build-tui.bat
```

---
**Pretty Build v1.0.1** - 现在支持多种便捷运行方式！ 🎉