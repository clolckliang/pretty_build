# Pretty Build 安装和使用指南

## 📦 包内容说明

这个包包含了完整的 Pretty Build 系统，包括：

### 🔧 核心组件
- **pretty_build.py** - 主程序，提供构建系统包装功能
- **textual_tui.py** - 现代化的文本用户界面
- **requirements.txt** - Python 依赖列表

### 🎮 演示和测试
- **demo.py** - 功能演示脚本
- **demo_tui.py** - TUI 演示脚本
- **test_textual_tui.py** - TUI 独立测试
- **test_tui_buttons.py** - 按钮功能测试

### 📚 文档
- **README.md** - 完整的使用文档
- **TUI_README.md** - TUI 详细说明
- **TEXTUAL_QUICKSTART.md** - 快速开始指南
- **PACKAGE_README.md** - 包说明文档

### ⚙️ 配置
- **.pretty_build.conf.example** - 配置文件模板
- **package_info.json** - 包信息文件
- **setup.py** - 自动安装脚本

### 🚀 启动脚本
- **start.bat** - Windows 启动脚本
- **start.sh** - Linux/macOS 启动脚本

## 🚀 快速开始

### Windows 用户
1. 解压包到任意目录
2. 双击 `start.bat` 启动
3. 选择相应的功能选项

### Linux/macOS 用户
1. 解压包到任意目录
2. 在终端中运行：`chmod +x start.sh && ./start.sh`
3. 选择相应的功能选项

### 手动安装
1. 解压包
2. 运行 `python setup.py` 安装依赖
3. 运行 `python pretty_build.py` 开始使用

## 🎯 使用方法

### 基本使用
```bash
# 自动检测构建系统并构建
python pretty_build.py

# 指定构建系统
python pretty_build.py --build-system ninja
python pretty_build.py --build-system make
python pretty_build.py --build-system cmake

# 并行构建
python pretty_build.py --jobs 8

# 详细输出
python pretty_build.py --verbose
```

### TUI 模式
```bash
# 启动现代化 TUI 界面
python pretty_build.py --tui
```

### 演示模式
```bash
# 查看功能演示
python demo.py

# TUI 演示
python demo_tui.py
```

## ⌨️ TUI 快捷键

### 全局快捷键
- **Ctrl+C**: 退出应用
- **Ctrl+B**: 开始构建
- **Ctrl+L**: 清理构建
- **Ctrl+R**: 重新构建
- **F1**: 显示帮助
- **F5**: 刷新界面

### 导航快捷键
- **Tab**: 切换焦点
- **Shift+Tab**: 反向切换焦点
- **↑/↓**: 在列表中导航
- **Enter**: 确认选择
- **Esc**: 返回上级

## 🎨 功能特性

### ✨ 美观界面
- 响应式布局，自适应终端大小
- 彩色输出和语法高亮
- 实时进度显示
- 现代化 TUI 界面

### ⚡ 性能优化
- 智能并行构建
- 增量构建支持
- 构建缓存系统
- 内存使用监控

### 🔌 扩展性
- 插件系统
- 自定义构建脚本
- 配置文件支持
- 多构建系统支持

### 🔔 通知系统
- 构建完成通知
- 错误警告提醒
- 系统托盘集成（Windows）

## 📋 系统要求

- **Python**: 3.8 或更高版本
- **操作系统**: Windows 10+, Linux, macOS
- **终端**: 支持 ANSI 颜色和 Unicode
- **内存**: 建议 512MB 以上可用内存

## 🐛 故障排除

### 常见问题

1. **依赖安装失败**
   ```bash
   # 手动安装依赖
   pip install -r requirements.txt
   ```

2. **TUI 显示异常**
   ```bash
   # 检查终端支持
   python -c "import rich; print('Rich 支持:', rich.get_console().is_terminal)"
   ```

3. **构建系统检测失败**
   ```bash
   # 手动指定构建系统
   python pretty_build.py --build-system ninja
   ```

4. **权限问题**
   ```bash
   # 确保有执行权限
   chmod +x pretty_build.py
   ```

---

**Pretty Build v1.0.0-final**  
构建时间: 2025-07-29 10:33:31  
包含文件: 15+ 个  
总大小: ~40KB