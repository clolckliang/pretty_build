#!/bin/bash

# Pretty Build Launcher for Linux/macOS
# 设置颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "🚀 Pretty Build 启动器"
echo "========================"
echo -e "${NC}"

# 检查 Python 是否安装
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo -e "${RED}❌ 错误: 未找到 Python${NC}"
        echo "请先安装 Python 3.8 或更高版本"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

echo -e "${GREEN}✅ Python 已安装${NC}"
$PYTHON_CMD --version

# 检查主程序是否存在
if [ ! -f "pretty_build.py" ]; then
    echo -e "${RED}❌ 错误: 未找到 pretty_build.py${NC}"
    echo "请确保在正确的目录中运行此脚本"
    exit 1
fi

echo -e "${GREEN}✅ Pretty Build 程序已找到${NC}"
echo

show_menu() {
    echo "请选择操作:"
    echo "[1] 标准模式启动"
    echo "[2] TUI 模式启动"
    echo "[3] 查看演示"
    echo "[4] 安装/更新依赖"
    echo "[5] 查看帮助"
    echo "[6] 退出"
    echo
}

while true; do
    show_menu
    read -p "请输入选择 (1-6): " choice
    
    case $choice in
        1)
            echo
            echo -e "${CYAN}🔨 启动标准模式...${NC}"
            $PYTHON_CMD pretty_build.py
            break
            ;;
        2)
            echo
            echo -e "${PURPLE}🖥️ 启动 TUI 模式...${NC}"
            $PYTHON_CMD pretty_build.py --tui
            break
            ;;
        3)
            echo
            echo -e "${YELLOW}🎮 启动演示模式...${NC}"
            $PYTHON_CMD demo.py
            break
            ;;
        4)
            echo
            echo -e "${BLUE}📦 安装/更新依赖...${NC}"
            if [ -f "setup.py" ]; then
                $PYTHON_CMD setup.py
            else
                echo "正在安装依赖..."
                $PYTHON_CMD -m pip install -r requirements.txt
            fi
            echo
            echo -e "${GREEN}依赖安装完成！${NC}"
            read -p "按 Enter 继续..."
            echo
            ;;
        5)
            echo
            echo -e "${CYAN}📚 显示帮助信息...${NC}"
            $PYTHON_CMD pretty_build.py --help
            echo
            read -p "按 Enter 继续..."
            echo
            ;;
        6)
            echo
            echo -e "${GREEN}👋 再见！${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}无效选择，请重新输入${NC}"
            echo
            ;;
    esac
done

echo
echo -e "${GREEN}程序已结束${NC}"