# Pretty Build - Textual TUI 快速开始

## 🚀 快速启动

### 方法 1: 通过 Pretty Build 启动
```bash
python pretty_build.py --tui
```

### 方法 2: 独立测试
```bash
python test_textual_tui.py
```

### 方法 3: 演示模式
```bash
python demo_tui.py
```

## ⌨️ 键盘快捷键

### 全局快捷键
- **Ctrl+C**: 退出应用
- **Ctrl+B**: 开始构建
- **Ctrl+L**: 清理构建
- **Ctrl+R**: 重新构建
- **F1**: 显示帮助
- **F5**: 刷新界面

### 导航
- **Tab**: 在组件间切换
- **Shift+Tab**: 反向切换
- **Enter**: 激活按钮
- **Esc**: 返回/取消

## 📋 功能特性

### ✅ 已实现
- 🎨 现代化 Textual 界面
- 📱 响应式布局
- 🎯 标签页导航 (Main, Config, Logs, Performance, Plugins, Help)
- ⌨️ 完整键盘快捷键
- 📊 实时状态显示
- 🔨 模拟构建过程
- 📜 彩色日志显示
- 📈 性能监控界面
- 🔌 插件管理界面

### 🚧 开发中
- 真实构建系统集成
- 配置文件读写
- 插件系统集成

## 📁 文件说明

- `textual_tui.py`: 主要的 Textual TUI 实现
- `test_textual_tui.py`: 独立测试脚本
- `demo_tui.py`: 演示脚本
- `TUI_README.md`: 详细文档

## 🛠️ 依赖要求

```bash
pip install textual rich psutil
```

## 🎯 使用建议

1. 首次使用建议运行 `python demo_tui.py` 了解功能
2. 使用 `python test_textual_tui.py` 进行独立测试
3. 在实际项目中使用 `python pretty_build.py --tui`

享受现代化的构建体验！ 🎉