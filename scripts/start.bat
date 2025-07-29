@echo off
chcp 65001 >nul
title Pretty Build Launcher

echo.
echo 🚀 Pretty Build 启动器
echo ========================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到 Python
    echo 请先安装 Python 3.8 或更高版本
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python 已安装
python --version

REM 检查主程序是否存在
if not exist "pretty_build.py" (
    echo ❌ 错误: 未找到 pretty_build.py
    echo 请确保在正确的目录中运行此脚本
    pause
    exit /b 1
)

echo ✅ Pretty Build 程序已找到
echo.

:menu
echo 请选择操作:
echo [1] 标准模式启动
echo [2] TUI 模式启动  
echo [3] 查看演示
echo [4] 安装/更新依赖
echo [5] 查看帮助
echo [6] 退出
echo.

set /p choice="请输入选择 (1-6): "

if "%choice%"=="1" goto standard
if "%choice%"=="2" goto tui
if "%choice%"=="3" goto demo
if "%choice%"=="4" goto install
if "%choice%"=="5" goto help
if "%choice%"=="6" goto exit

echo 无效选择，请重新输入
echo.
goto menu

:standard
echo.
echo 🔨 启动标准模式...
python pretty_build.py
goto end

:tui
echo.
echo 🖥️ 启动 TUI 模式...
python pretty_build.py --tui
goto end

:demo
echo.
echo 🎮 启动演示模式...
python demo.py
goto end

:install
echo.
echo 📦 安装/更新依赖...
if exist "setup.py" (
    python setup.py
) else (
    echo 正在安装依赖...
    pip install -r requirements.txt
)
echo.
echo 依赖安装完成！
pause
goto menu

:help
echo.
echo 📚 显示帮助信息...
python pretty_build.py --help
echo.
pause
goto menu

:end
echo.
echo 程序已结束
pause

:exit
echo.
echo 👋 再见！
exit /b 0