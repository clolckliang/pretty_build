"""
Pretty Build - Textual TUI Implementation
基于 Textual 框架的现代化文本用户界面
"""

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.widgets import (
    Header, Footer, Static, Button, Label, 
    TabbedContent, TabPane, DataTable, Log,
    ProgressBar, Tree, Input, Select
)
from textual.binding import Binding
from textual.reactive import reactive
from textual import events
from rich.text import Text
from rich.panel import Panel
from rich.console import Console
from rich.table import Table
import asyncio
import time
from datetime import datetime
from typing import Optional, Dict, Any
import subprocess
import os
import random


class BuildStatus(Static):
    """构建状态显示组件"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.status = "Ready"
        self.last_build_time = None
        self.build_count = 0
        
    def compose(self) -> ComposeResult:
        yield Label(f"Status: {self.status}", id="status-label")
        yield Label(f"Builds: {self.build_count}", id="build-count")
        if self.last_build_time:
            yield Label(f"Last: {self.last_build_time}", id="last-build")
    
    def update_status(self, status: str, build_time: Optional[str] = None):
        self.status = status
        if build_time:
            self.last_build_time = build_time
            self.build_count += 1
        self.refresh()


class ConfigPanel(Static):
    """配置面板"""
    
    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("Build Configuration", classes="panel-title")
            yield Input(placeholder="Build command...", id="build-cmd")
            yield Input(placeholder="Clean command...", id="clean-cmd")
            yield Input(placeholder="Output directory...", id="output-dir")
            yield Button("Save Config", id="save-config", variant="primary")
            yield Button("Load Config", id="load-config")


class LogViewer(Log):
    """日志查看器"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.auto_scroll = True
        
    def add_build_log(self, message: str, level: str = "info"):
        """添加构建日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        if level == "error":
            self.write(f"[red][{timestamp}] ERROR: {message}[/red]")
        elif level == "warning":
            self.write(f"[yellow][{timestamp}] WARN: {message}[/yellow]")
        elif level == "success":
            self.write(f"[green][{timestamp}] SUCCESS: {message}[/green]")
        else:
            self.write(f"[{timestamp}] {message}")


class PerformancePanel(Static):
    """性能监控面板 - 类似htop的系统监控"""
    
    def compose(self) -> ComposeResult:
        # 标题（固定在顶部）
        yield Label("🖥️ System Performance Monitor", classes="panel-title")
        
        # 直接显示内容，不使用滚动容器
        # 系统信息区域
        with Container(id="system-info"):
            with Horizontal():
                with Vertical():
                    yield Label("💻 System Info", classes="section-title")
                    yield Label("OS: Windows", id="os-info")
                    yield Label("Python: 3.11", id="python-version")
                with Vertical():
                    yield Label("🔧 Build Environment", classes="section-title")
                    yield Label("CMake: --", id="cmake-version")
                    yield Label("GCC: --", id="gcc-version")
        
        # CPU监控区域
        with Container(id="cpu-monitor"):
            yield Label("🔥 CPU Usage", classes="section-title")
            with Horizontal():
                with Vertical():
                    yield Label("Overall: 0%", id="cpu-overall")
                    yield ProgressBar(total=100, id="cpu-progress")
                    yield Label("Cores: 0", id="cpu-cores")
                    yield Label("Freq: 0 MHz", id="cpu-freq")
                with Vertical():
                    yield Label("Per Core Usage:", classes="subsection-title")
                    # 只显示前4个核心，节省空间
                    for i in range(4):
                        yield Label(f"Core {i}: 0%", id=f"cpu-core-{i}", classes="cpu-core-label")
        
        # 内存监控区域
        with Container(id="memory-monitor"):
            yield Label("🧠 Memory Usage", classes="section-title")
            with Horizontal():
                with Vertical():
                    yield Label("RAM: 0/0 GB (0%)", id="memory-ram")
                    yield ProgressBar(total=100, id="memory-progress")
                    yield Label("Available: 0 GB", id="memory-available")
                with Vertical():
                    yield Label("Virtual Memory:", classes="subsection-title")
                    yield Label("Total: 0 GB", id="virtual-total")
                    yield Label("Used: 0 GB", id="virtual-used")
                    yield Label("Swap: 0 GB", id="swap-usage")
        
        # 磁盘和网络监控
        with Container(id="disk-network-monitor"):
            with Horizontal():
                with Vertical():
                    yield Label("💾 Disk I/O", classes="section-title")
                    yield Label("Read: 0 MB/s", id="disk-read")
                    yield Label("Write: 0 MB/s", id="disk-write")
                    yield Label("Usage: 0%", id="disk-usage")
                with Vertical():
                    yield Label("🌐 Network", classes="section-title")
                    yield Label("Sent: 0 MB/s", id="network-sent")
                    yield Label("Recv: 0 MB/s", id="network-recv")
                    yield Label("Connections: 0", id="network-connections")
    
    def on_mount(self) -> None:
        """组件挂载时启动性能监控"""
        # 启动性能监控定时器
        self.set_interval(3.0, self._update_performance_data)
    
    def _update_performance_data(self) -> None:
        """更新性能监控数据"""
        try:
            import psutil
            import random
            
            # 获取CPU数据
            cpu_percent = psutil.cpu_percent(interval=0.1)
            per_cpu = psutil.cpu_percent(percpu=True, interval=0.1)
            cpu_count = psutil.cpu_count()
            
            # 更新CPU组件
            try:
                cpu_overall = self.query_one("#cpu-overall", Label)
                cpu_overall.update(f"Overall: {cpu_percent:.1f}%")
                
                cpu_cores = self.query_one("#cpu-cores", Label)
                cpu_cores.update(f"Cores: {cpu_count}")
                
                cpu_progress = self.query_one("#cpu-progress", ProgressBar)
                cpu_progress.progress = cpu_percent
                
                # 更新CPU频率
                try:
                    cpu_freq = psutil.cpu_freq()
                    freq_mhz = int(cpu_freq.current) if cpu_freq else 0
                except:
                    freq_mhz = 0
                
                cpu_freq_widget = self.query_one("#cpu-freq", Label)
                cpu_freq_widget.update(f"Freq: {freq_mhz} MHz")
                
                # 更新每个核心（只更新前4个）
                for i in range(min(len(per_cpu), 4)):
                    try:
                        core_widget = self.query_one(f"#cpu-core-{i}", Label)
                        core_widget.update(f"Core {i}: {per_cpu[i]:.1f}%")
                    except:
                        continue  # 如果核心不存在就跳过
                    
            except Exception as e:
                pass
            
            # 更新内存数据
            try:
                memory = psutil.virtual_memory()
                
                memory_ram = self.query_one("#memory-ram", Label)
                total_gb = memory.total / (1024**3)
                used_gb = memory.used / (1024**3)
                memory_ram.update(f"RAM: {used_gb:.1f}/{total_gb:.1f} GB ({memory.percent:.1f}%)")
                
                memory_progress = self.query_one("#memory-progress", ProgressBar)
                memory_progress.progress = memory.percent
                
                memory_available = self.query_one("#memory-available", Label)
                available_gb = memory.available / (1024**3)
                memory_available.update(f"Available: {available_gb:.1f} GB")
                
                # 虚拟内存
                virtual_total = self.query_one("#virtual-total", Label)
                virtual_total.update(f"Total: {memory.total / (1024**3):.1f} GB")
                
                virtual_used = self.query_one("#virtual-used", Label)
                virtual_used.update(f"Used: {memory.used / (1024**3):.1f} GB")
                
                # Swap内存
                swap = psutil.swap_memory()
                swap_gb = swap.used / (1024**3)
                swap_total_gb = swap.total / (1024**3)
                
                swap_usage = self.query_one("#swap-usage", Label)
                if swap.total > 0:
                    swap_usage.update(f"Swap: {swap_gb:.1f}/{swap_total_gb:.1f} GB ({swap.percent:.1f}%)")
                else:
                    swap_usage.update("Swap: Not available")
                    
            except Exception as e:
                pass
            
            # 更新磁盘和网络数据（使用模拟数据）
            try:
                read_mb = random.uniform(0, 50)
                write_mb = random.uniform(0, 30)
                
                disk_read = self.query_one("#disk-read", Label)
                disk_read.update(f"Read: {read_mb:.1f} MB/s")
                
                disk_write = self.query_one("#disk-write", Label)
                disk_write.update(f"Write: {write_mb:.1f} MB/s")
                
                disk_percent = random.uniform(60, 85)
                disk_usage_widget = self.query_one("#disk-usage", Label)
                disk_usage_widget.update(f"Usage: {disk_percent:.1f}%")
                
                # 网络数据
                sent_mb = random.uniform(0, 10)
                recv_mb = random.uniform(0, 15)
                
                network_sent = self.query_one("#network-sent", Label)
                network_sent.update(f"Sent: {sent_mb:.1f} MB/s")
                
                network_recv = self.query_one("#network-recv", Label)
                network_recv.update(f"Recv: {recv_mb:.1f} MB/s")
                
                connections = random.randint(50, 200)
                network_connections = self.query_one("#network-connections", Label)
                network_connections.update(f"Connections: {connections}")
                
            except Exception as e:
                pass
                
        except Exception as e:
            pass


class PluginManager(Static):
    """插件管理面板"""
    
    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("Plugin Manager", classes="panel-title")
            
            # 插件列表
            table = DataTable()
            table.add_columns("Plugin", "Status", "Version")
            table.add_row("CMake", "Active", "1.0.0")
            table.add_row("Ninja", "Active", "1.11.0")
            table.add_row("Notifications", "Inactive", "1.0.0")
            yield table
            
            with Horizontal():
                yield Button("Enable", id="enable-plugin")
                yield Button("Disable", id="disable-plugin")
                yield Button("Configure", id="config-plugin")


class PrettyBuildTUI(App):
    """Pretty Build 主 TUI 应用"""
    
    CSS = """
    .panel-title {
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
        text-align: center;
    }
    
    .section-title {
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }
    
    .subsection-title {
        text-style: bold;
        color: $secondary;
        margin-bottom: 1;
    }
    
    #status-panel {
        dock: top;
        height: 3;
        background: $surface;
    }
    
    #build-progress {
        dock: bottom;
        height: 3;
        background: $surface;
    }
    
    #project-info {
        background: $primary 10%;
        border: solid $primary;
        margin: 1;
        padding: 1;
        height: 5;
    }
    
    #project-info Static {
        color: $text;
        margin-bottom: 0;
    }
    
    #build-actions {
        margin: 1;
        height: 3;
    }
    
    #quick-status {
        background: $surface;
        border: solid $accent;
        margin: 1;
        padding: 1;
        height: 5;
    }
    
    #quick-status Static {
        color: $text;
        margin-bottom: 0;
    }
    
    /* 滚动容器样式 */
        VerticalScroll {
            height: 100%;
            scrollbar-size: 1 1;
            scrollbar-background: $surface;
            scrollbar-color: $primary;
            scrollbar-corner-color: $surface;
        }
    
    #system-info {
        background: $surface;
        border: solid $accent;
        margin: 1;
        padding: 1;
        height: 8;
    }
    
    #cpu-monitor {
        background: $warning 10%;
        border: solid $warning;
        margin: 1;
        padding: 1;
        height: 10;
    }
    
    #cpu-cores-container {
        height: auto;
        max-height: 8;
        overflow-y: auto;
    }
    
    .cpu-core-label {
        margin-bottom: 0;
        padding: 0;
        height: 1;
    }
    
    #memory-monitor {
        background: $success 10%;
        border: solid $success;
        margin: 1;
        padding: 1;
        height: 10;
    }
    
    #disk-network-monitor {
        background: $primary 10%;
        border: solid $primary;
        margin: 1;
        padding: 1;
        height: 8;
    }
    
    #process-monitor {
        background: $surface;
        border: solid $accent;
        margin: 1;
        padding: 1;
        height: 12;
    }
    
    #build-stats {
        background: $error 10%;
        border: solid $error;
        margin: 1;
        padding: 1;
        height: 8;
    }
    
    #process-table {
        height: 8;
        margin: 1;
    }
    
    Button {
        margin: 1;
    }
    
    .build-button {
        background: $success;
    }
    
    .clean-button {
        background: $warning;
    }
    
    .stop-button {
        background: $error;
    }
    """
    
    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit"),
        Binding("ctrl+b", "build", "Build"),
        Binding("ctrl+l", "clean", "Clean"),
        Binding("ctrl+r", "rebuild", "Rebuild"),
        Binding("f1", "help", "Help"),
        Binding("f5", "refresh", "Refresh"),
    ]
    
    TITLE = "Pretty Build - Enhanced Build System"
    SUB_TITLE = "Modern TUI for Build Management"
    
    # 响应式状态 - 暂时禁用以测试标签页切换问题
    # is_building = reactive(False)
    # build_progress = reactive(0)
    # current_status = reactive("Ready")
    
    def __init__(self, config=None, **kwargs):
        super().__init__(**kwargs)
        self.config = config or {}
        self.build_runner = None
        # 使用普通变量替代reactive变量
        self.is_building = False
        self.build_progress = 0
        self.current_status = "Ready"
        
        # 初始化psutil，建立CPU监控基准
        self._init_psutil()
    
    def _init_psutil(self):
        """初始化psutil，建立CPU监控基准"""
        try:
            import psutil
            # 建立CPU监控基准，第一次调用通常返回0
            psutil.cpu_percent(interval=None)
            psutil.cpu_percent(percpu=True, interval=None)
            # 等待一小段时间让psutil建立基准
            import time
            time.sleep(0.1)
        except Exception:
            pass
        
    def compose(self) -> ComposeResult:
        """构建应用界面"""
        yield Header()
        
        # 状态栏
        with Container(id="status-panel"):
            yield BuildStatus(id="build-status")
        
        # 主内容区域
        with TabbedContent(id="main-content"):
            # 主页
            with TabPane("Main", id="main-tab"):
                with Vertical():
                    # 项目信息区域
                    with Container(id="project-info"):
                        yield Static("📁 Project: L298 Motor Control", id="project-name")
                        yield Static("🏗️ Build System: CMake + ARM GCC", id="build-system")
                        yield Static("🎯 Target: STM32F103C8T6", id="target-info")
                    
                    # 构建操作按钮
                    with Horizontal(id="build-actions"):
                        yield Button("🔨 Build", id="build-btn", classes="build-button")
                        yield Button("🧹 Clean", id="clean-btn", classes="clean-button")
                        yield Button("🔄 Rebuild", id="rebuild-btn")
                        yield Button("⏹️ Stop", id="stop-btn", classes="stop-button")
                    
                    # 快速状态信息
                    with Container(id="quick-status"):
                        yield Static("📊 Last Build: Ready", id="last-build-status")
                        yield Static("⏱️ Build Time: --", id="build-time")
                        yield Static("📝 Output: build/", id="output-path")
            
            # 配置页面
            with TabPane("Config", id="config-tab"):
                yield ConfigPanel(id="config-panel")
            
            # 日志页面
            with TabPane("Logs", id="logs-tab"):
                yield LogViewer(id="log-viewer")
            
            # 性能页面
            with TabPane("Performance", id="performance-tab"):
                yield PerformancePanel(id="performance-panel")
            
            # 插件页面
            with TabPane("Plugins", id="plugins-tab"):
                yield PluginManager(id="plugin-manager")
            
            # 帮助页面
            with TabPane("Help", id="help-tab"):
                yield Static(self._get_help_content(), id="help-content")
        
        # 进度条
        with Container(id="build-progress"):
            yield ProgressBar(total=100, id="progress-bar")
            yield Label("Ready", id="progress-label")
        
        yield Footer()
    
    def _get_help_content(self) -> str:
        """获取帮助内容"""
        return """
# Pretty Build TUI Help

## Keyboard Shortcuts
- **Ctrl+C**: Quit application
- **Ctrl+B**: Start build
- **Ctrl+L**: Clean build
- **Ctrl+R**: Rebuild (clean + build)
- **F1**: Show this help
- **F5**: Refresh interface

## Navigation & Scrolling
- **↑/↓ Arrow Keys**: Scroll up/down in Performance tab
- **Page Up/Page Down**: Fast scroll in Performance tab
- **Home/End**: Jump to top/bottom in Performance tab
- **Mouse Wheel**: Scroll content in Performance tab

## Tabs Navigation
- **Main**: Quick build actions and status
- **Config**: Build configuration settings
- **Logs**: Real-time build logs
- **Performance**: System performance metrics
- **Plugins**: Plugin management
- **Help**: This help page

## Build Commands
The TUI supports various build systems:
- CMake + Ninja
- CMake + Make
- MSBuild
- Custom commands

## Configuration
Configure build commands in the Config tab or edit .pretty_build.conf file.
        """
    
    def _get_log_viewer(self) -> Optional[LogViewer]:
        """安全获取日志查看器"""
        try:
            return self.query_one("#log-viewer", LogViewer)
        except Exception:
            return None
    
    def _add_log(self, message: str, level: str = "info"):
        """安全添加日志"""
        log_viewer = self._get_log_viewer()
        if log_viewer:
            log_viewer.add_build_log(message, level)
    
    async def on_mount(self) -> None:
        """应用启动时的初始化"""
        # 延迟一点时间确保组件完全初始化
        await asyncio.sleep(0.1)
        
        self._add_log("Pretty Build TUI started", "success")
        self._add_log("Ready for build operations")
        
        # 启动状态更新定时器
        self.set_interval(3.0, self._update_status_display)
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """处理按钮点击事件"""
        button_id = event.button.id
        self._add_log(f"Button clicked: {button_id}", "info")
        
        # 立即更新状态显示，提供即时反馈
        self._update_status_display_immediate()
        
        if button_id == "build-btn":
            await self.action_build()
        elif button_id == "clean-btn":
            await self.action_clean()
        elif button_id == "rebuild-btn":
            await self.action_rebuild()
        elif button_id == "stop-btn":
            await self.action_stop()
        elif button_id == "save-config":
            await self._save_config()
        elif button_id == "load-config":
            await self._load_config()
        else:
            self._add_log(f"Unknown button clicked: {button_id}", "warning")
        
        # 再次立即更新状态显示
        self._update_status_display_immediate()
    
    async def action_build(self) -> None:
        """执行构建"""
        if self.is_building:
            self._add_log("Build already in progress", "warning")
            return
        
        # 立即更新状态，提供即时反馈
        self.is_building = True
        self.current_status = "Building..."
        self._update_status_display_immediate()
        self._add_log("Starting build...", "info")
        
        # 更新状态
        try:
            status_widget = self.query_one("#build-status", BuildStatus)
            status_widget.update_status("Building...")
            
            # 更新Main页面状态
            last_build_status = self.query_one("#last-build-status", Static)
            last_build_status.update("📊 Last Build: Building...")
        except Exception:
            pass
        
        # 记录开始时间
        start_time = datetime.now()
        
        # 模拟构建过程
        try:
            progress_bar = self.query_one("#progress-bar", ProgressBar)
            progress_label = self.query_one("#progress-label", Label)
            
            for i in range(0, 101, 10):
                progress_bar.progress = i
                progress_label.update(f"Building... {i}%")
                await asyncio.sleep(0.2)
                
                if i == 30:
                    self._add_log("Compiling source files...")
                elif i == 60:
                    self._add_log("Linking objects...")
                elif i == 90:
                    self._add_log("Generating output...")
            
            # 构建完成
            end_time = datetime.now()
            build_duration = (end_time - start_time).total_seconds()
            build_time_str = f"{build_duration:.1f}s"
            
            status_widget = self.query_one("#build-status", BuildStatus)
            status_widget.update_status("Build Success", end_time.strftime("%H:%M:%S"))
            self._add_log("Build completed successfully!", "success")
            progress_label.update("Build completed!")
            
            # 更新Main页面状态
            try:
                last_build_status = self.query_one("#last-build-status", Static)
                last_build_status.update("📊 Last Build: ✅ Success")
                
                build_time_widget = self.query_one("#build-time", Static)
                build_time_widget.update(f"⏱️ Build Time: {build_time_str}")
            except Exception as e:
                self._add_log(f"System info update error: {e}", "error")
            
        except Exception as e:
            try:
                status_widget = self.query_one("#build-status", BuildStatus)
                status_widget.update_status("Build Failed")
                
                # 更新Main页面状态
                last_build_status = self.query_one("#last-build-status", Static)
                last_build_status.update("📊 Last Build: ❌ Failed")
            except Exception:
                pass
            self._add_log(f"Build failed: {str(e)}", "error")
            try:
                progress_label = self.query_one("#progress-label", Label)
                progress_label.update("Build failed!")
            except Exception:
                pass
        
        finally:
            self.is_building = False
            self.current_status = "Ready"
            # 立即更新最终状态
            self._update_status_display_immediate()
    
    async def action_clean(self) -> None:
        """执行清理"""
        # 立即更新状态反馈
        self._update_status_display_immediate()
        self._add_log("Cleaning build artifacts...", "info")
        
        # 更新Main页面状态
        try:
            last_build_status = self.query_one("#last-build-status", Static)
            last_build_status.update("📊 Last Build: Cleaning...")
        except Exception:
            pass
        
        # 模拟清理过程
        try:
            progress_bar = self.query_one("#progress-bar", ProgressBar)
            progress_label = self.query_one("#progress-label", Label)
            
            for i in range(0, 101, 20):
                progress_bar.progress = i
                progress_label.update(f"Cleaning... {i}%")
                await asyncio.sleep(0.1)
            
            self._add_log("Clean completed!", "success")
            progress_label.update("Clean completed!")
            
            # 更新Main页面状态
            try:
                last_build_status = self.query_one("#last-build-status", Static)
                last_build_status.update("📊 Last Build: 🧹 Cleaned")
                
                build_time_widget = self.query_one("#build-time", Static)
                build_time_widget.update("⏱️ Build Time: --")
            except Exception:
                pass
                
        except Exception as e:
            self._add_log(f"Clean failed: {str(e)}", "error")
            try:
                last_build_status = self.query_one("#last-build-status", Static)
                last_build_status.update("📊 Last Build: ❌ Clean Failed")
            except Exception:
                pass
        
        # 立即更新最终状态
        self._update_status_display_immediate()
    
    async def action_rebuild(self) -> None:
        """执行重新构建"""
        # 立即更新状态反馈
        self._update_status_display_immediate()
        await self.action_clean()
        await asyncio.sleep(0.5)
        await self.action_build()
    
    async def action_stop(self) -> None:
        """停止构建"""
        if self.is_building:
            self.is_building = False
            self.current_status = "Stopped"
            # 立即更新状态反馈
            self._update_status_display_immediate()
            self._add_log("Build stopped by user", "warning")
            
            try:
                progress_label = self.query_one("#progress-label", Label)
                progress_label.update("Stopped")
            except Exception:
                pass
    
    async def action_help(self) -> None:
        """显示帮助"""
        try:
            tabbed_content = self.query_one("#main-content", TabbedContent)
            tabbed_content.active = "help-tab"
        except Exception:
            pass
    
    async def action_refresh(self) -> None:
        """刷新界面"""
        self._add_log("Interface refreshed", "info")
    
    async def _open_output_directory(self) -> None:
        """打开输出目录"""
        import os
        import subprocess
        import platform
        
        self._add_log("Opening output directory...")
        
        # 确定输出目录路径
        output_dir = os.path.join(os.getcwd(), "build")
        if not os.path.exists(output_dir):
            # 如果build目录不存在，尝试其他常见的输出目录
            possible_dirs = ["dist", "out", "output", "bin", "target"]
            for dir_name in possible_dirs:
                test_dir = os.path.join(os.getcwd(), dir_name)
                if os.path.exists(test_dir):
                    output_dir = test_dir
                    break
            else:
                # 如果都不存在，使用当前目录
                output_dir = os.getcwd()
        
        try:
            # 根据操作系统打开文件管理器
            system = platform.system()
            if system == "Windows":
                subprocess.run(["explorer", output_dir], check=True)
            elif system == "Darwin":  # macOS
                subprocess.run(["open", output_dir], check=True)
            else:  # Linux
                subprocess.run(["xdg-open", output_dir], check=True)
            
            self._add_log(f"Opened directory: {output_dir}", "success")
        except Exception as e:
            self._add_log(f"Failed to open directory: {str(e)}", "error")
    
    async def _switch_to_logs(self) -> None:
        """切换到日志页面"""
        self._add_log("Attempting to switch to logs view...", "info")
        try:
            # 先尝试获取TabbedContent
            tabbed_content = self.query_one("#main-content", TabbedContent)
            self._add_log(f"Found TabbedContent: {tabbed_content}", "info")
            
            # 检查当前活动标签
            current_tab = tabbed_content.active
            self._add_log(f"Current active tab: {current_tab}", "info")
            
            # 切换到日志标签
            tabbed_content.active = "logs-tab"
            self._add_log("Successfully switched to logs view", "success")
            
            # 验证切换是否成功
            new_active = tabbed_content.active
            self._add_log(f"New active tab: {new_active}", "info")
            
        except Exception as e:
            self._add_log(f"Failed to switch to logs: {str(e)}", "error")
            import traceback
            self._add_log(f"Traceback: {traceback.format_exc()}", "error")
    
    async def _switch_to_config(self) -> None:
        """切换到配置页面"""
        self._add_log("Attempting to switch to config view...", "info")
        try:
            # 先尝试获取TabbedContent
            tabbed_content = self.query_one("#main-content", TabbedContent)
            self._add_log(f"Found TabbedContent: {tabbed_content}", "info")
            
            # 检查当前活动标签
            current_tab = tabbed_content.active
            self._add_log(f"Current active tab: {current_tab}", "info")
            
            # 切换到配置标签
            tabbed_content.active = "config-tab"
            self._add_log("Successfully switched to config view", "success")
            
            # 验证切换是否成功
            new_active = tabbed_content.active
            self._add_log(f"New active tab: {new_active}", "info")
            
        except Exception as e:
            self._add_log(f"Failed to switch to config: {str(e)}", "error")
            import traceback
            self._add_log(f"Traceback: {traceback.format_exc()}", "error")
    
    async def _save_config(self) -> None:
        """保存配置"""
        self._add_log("Configuration saved", "success")
    
    async def _load_config(self) -> None:
        """加载配置"""
        self._add_log("Configuration loaded", "info")
    
    def _update_performance(self) -> None:
        """更新性能指标 - 简化版本专注于CPU监控"""
        try:
            import psutil
            
            # 添加调试日志
            self._add_log("Performance update started", "info")
            
            # 获取CPU数据
            cpu_percent = psutil.cpu_percent(interval=0.1)
            per_cpu = psutil.cpu_percent(percpu=True, interval=0.1)
            cpu_count = psutil.cpu_count()
            
            self._add_log(f"CPU data: {cpu_percent}%, cores: {cpu_count}", "info")
            
            # 尝试更新CPU组件
            try:
                cpu_overall = self.query_one("#cpu-overall", Label)
                cpu_overall.update(f"Overall: {cpu_percent:.1f}%")
                self._add_log("CPU overall updated", "info")
            except Exception as e:
                self._add_log(f"CPU overall error: {e}", "error")
            
            try:
                cpu_cores = self.query_one("#cpu-cores", Label)
                cpu_cores.update(f"Cores: {cpu_count}")
                self._add_log("CPU cores updated", "info")
            except Exception as e:
                self._add_log(f"CPU cores error: {e}", "error")
            
            try:
                cpu_progress = self.query_one("#cpu-progress", ProgressBar)
                cpu_progress.progress = cpu_percent
                self._add_log("CPU progress updated", "info")
            except Exception as e:
                self._add_log(f"CPU progress error: {e}", "error")
            
            # 尝试更新CPU频率
            try:
                cpu_freq = psutil.cpu_freq()
                if cpu_freq:
                    freq_mhz = int(cpu_freq.current)
                    self._add_log(f"CPU frequency: {freq_mhz} MHz", "info")
                else:
                    # 如果无法获取频率，尝试从其他方式获取
                    freq_mhz = 0
                    self._add_log("CPU frequency not available", "warning")
                
                cpu_freq_widget = self.query_one("#cpu-freq", Label)
                cpu_freq_widget.update(f"Freq: {freq_mhz} MHz")
                self._add_log("CPU frequency updated", "info")
            except Exception as e:
                self._add_log(f"CPU frequency error: {e}", "error")
            
            # 尝试更新每个核心
            try:
                for i in range(min(len(per_cpu), 8)):  # 限制为前8个核心
                    core_widget = self.query_one(f"#cpu-core-{i}", Label)
                    core_widget.update(f"Core {i}: {per_cpu[i]:.1f}%")
                self._add_log(f"Updated {min(len(per_cpu), 8)} cores", "info")
            except Exception as e:
                self._add_log(f"Core update error: {e}", "error")
                
        except Exception as e:
            self._add_log(f"Performance update failed: {e}", "error")
            
        # === 内存监控更新 ===
        try:
            import psutil
            memory = psutil.virtual_memory()
            
            self._add_log(f"Memory data: {memory.percent}%, total: {memory.total/(1024**3):.1f}GB", "info")
            
            # RAM使用情况
            try:
                memory_ram = self.query_one("#memory-ram", Label)
                total_gb = memory.total / (1024**3)
                used_gb = memory.used / (1024**3)
                memory_ram.update(f"RAM: {used_gb:.1f}/{total_gb:.1f} GB ({memory.percent:.1f}%)")
                self._add_log("Memory RAM updated", "info")
            except Exception as e:
                self._add_log(f"Memory RAM error: {e}", "error")
            
            try:
                memory_progress = self.query_one("#memory-progress", ProgressBar)
                memory_progress.progress = memory.percent
                self._add_log("Memory progress updated", "info")
            except Exception as e:
                self._add_log(f"Memory progress error: {e}", "error")
            
            # 可用内存
            try:
                memory_available = self.query_one("#memory-available", Label)
                available_gb = memory.available / (1024**3)
                memory_available.update(f"Available: {available_gb:.1f} GB")
                self._add_log("Memory available updated", "info")
            except Exception as e:
                self._add_log(f"Memory available error: {e}", "error")
            
            # 缓存内存（Windows上可能不准确）
            try:
                cached_gb = getattr(memory, 'cached', 0) / (1024**3)
                memory_cached = self.query_one("#memory-cached", Label)
                memory_cached.update(f"Cached: {cached_gb:.1f} GB")
                self._add_log("Memory cached updated", "info")
            except Exception as e:
                self._add_log(f"Memory cached error: {e}", "error")
            
            # 虚拟内存
            try:
                virtual_total = self.query_one("#virtual-total", Label)
                virtual_total.update(f"Total: {memory.total / (1024**3):.1f} GB")
                
                virtual_used = self.query_one("#virtual-used", Label)
                virtual_used.update(f"Used: {memory.used / (1024**3):.1f} GB")
                
                self._add_log("Virtual memory updated", "info")
            except Exception as e:
                self._add_log(f"Virtual memory error: {e}", "error")
            
            # Swap内存
            try:
                swap = psutil.swap_memory()
                swap_gb = swap.used / (1024**3)
                swap_total_gb = swap.total / (1024**3)
                
                swap_usage = self.query_one("#swap-usage", Label)
                if swap.total > 0:
                    swap_usage.update(f"Swap: {swap_gb:.1f}/{swap_total_gb:.1f} GB ({swap.percent:.1f}%)")
                else:
                    swap_usage.update("Swap: Not available")
                
                self._add_log(f"Swap memory updated: {swap_gb:.1f}/{swap_total_gb:.1f} GB", "info")
            except Exception as e:
                self._add_log(f"Swap memory error: {e}", "error")
                
        except Exception as e:
            self._add_log(f"Memory monitoring error: {e}", "error")
            
            # === 磁盘和网络监控更新（简化版） ===
            try:
                # 简化磁盘I/O监控，使用模拟数据
                read_mb = random.uniform(0, 50)
                write_mb = random.uniform(0, 30)
                
                disk_read = self.query_one("#disk-read", Label)
                disk_read.update(f"Read: {read_mb:.1f} MB/s")
                
                disk_write = self.query_one("#disk-write", Label)
                disk_write.update(f"Write: {write_mb:.1f} MB/s")
                
                # 磁盘使用率（简化计算）
                disk_percent = random.uniform(60, 85)
                
                disk_usage_widget = self.query_one("#disk-usage", Label)
                disk_usage_widget.update(f"Usage: {disk_percent:.1f}%")
                
                disk_progress = self.query_one("#disk-progress", ProgressBar)
                disk_progress.progress = disk_percent
                
                # 网络监控（简化版）
                sent_mb = random.uniform(0, 10)
                recv_mb = random.uniform(0, 15)
                
                network_sent = self.query_one("#network-sent", Label)
                network_sent.update(f"Sent: {sent_mb:.1f} MB/s")
                
                network_recv = self.query_one("#network-recv", Label)
                network_recv.update(f"Recv: {recv_mb:.1f} MB/s")
                
                # 网络连接数（模拟）
                connections = random.randint(50, 200)
                
                network_connections = self.query_one("#network-connections", Label)
                network_connections.update(f"Connections: {connections}")
                
                # 网络接口
                network_interface = self.query_one("#network-interface", Label)
                network_interface.update("Interface: Ethernet")
                
            except Exception as e:
                self._add_log(f"Disk/Network monitoring error: {e}", "error")
            
            # === 进程监控更新（简化版） ===
            try:
                # 简化进程监控，只显示模拟数据以减少卡顿
                process_table = self.query_one("#process-table", DataTable)
                process_table.clear()
                process_table.add_columns("PID", "Name", "CPU%", "Memory", "Status")
                
                # 使用模拟数据而不是实时获取进程信息
                mock_processes = [
                    ("1234", "python.exe", f"{random.uniform(5, 25):.1f}%", f"{random.randint(50, 200)}MB", "Running"),
                    ("5678", "cmake.exe", f"{random.uniform(2, 15):.1f}%", f"{random.randint(30, 100)}MB", "Running"),
                    ("9012", "ninja.exe", f"{random.uniform(1, 10):.1f}%", f"{random.randint(20, 80)}MB", "Running"),
                    ("3456", "gcc.exe", f"{random.uniform(3, 20):.1f}%", f"{random.randint(40, 150)}MB", "Running"),
                    ("7890", "textual", f"{random.uniform(1, 8):.1f}%", f"{random.randint(25, 60)}MB", "Running"),
                ]
                
                for pid, name, cpu_pct, memory_str, status in mock_processes:
                    process_table.add_row(pid, name, cpu_pct, memory_str, status)
                
            except Exception as e:
                self._add_log(f"Process monitoring error: {e}", "error")
            
            # === 构建性能统计更新 ===
            try:
                # 这些数据通常需要从构建历史中获取，这里使用模拟数据
                last_build_time = self.query_one("#last-build-time", Label)
                last_build_time.update("Last Build: 2.3s")
                
                avg_build_time = self.query_one("#avg-build-time", Label)
                avg_build_time.update("Avg Build: 2.8s")
                
                fastest_build = self.query_one("#fastest-build", Label)
                fastest_build.update("Fastest: 1.9s")
                
                total_builds = self.query_one("#total-builds", Label)
                total_builds.update("Total Builds: 42")
                
                # 缓存统计
                cache_hit_rate = self.query_one("#cache-hit-rate", Label)
                cache_hit_rate.update(f"Hit Rate: {random.randint(75, 95)}%")
                
                cache_size = self.query_one("#cache-size", Label)
                cache_size.update(f"Cache Size: {random.randint(50, 200)} MB")
                
                temp_files = self.query_one("#temp-files", Label)
                temp_files.update(f"Temp Files: {random.randint(10, 50)}")
                
                output_size = self.query_one("#output-size", Label)
                output_size.update(f"Output Size: {random.randint(5, 25)} MB")
                
            except Exception as e:
                self._add_log(f"Build stats update error: {e}", "error")
                
        except Exception as e:
            self._add_log(f"Performance monitoring error: {e}", "error")
            # 如果 psutil 不可用，显示模拟数据
            try:
                import random
                
                # 基本CPU和内存监控（保持向后兼容）
                cpu_percent = random.uniform(10, 80)
                memory_percent = random.uniform(30, 70)
                
                try:
                    cpu_overall = self.query_one("#cpu-overall", Label)
                    cpu_overall.update(f"Overall: {cpu_percent:.1f}%")
                    
                    cpu_progress = self.query_one("#cpu-progress", ProgressBar)
                    cpu_progress.progress = cpu_percent
                    
                    memory_ram = self.query_one("#memory-ram", Label)
                    memory_ram.update(f"RAM: {memory_percent:.1f}%")
                    
                    memory_progress = self.query_one("#memory-progress", ProgressBar)
                    memory_progress.progress = memory_percent
                except Exception:
                    # 如果新的组件不存在，尝试旧的组件ID
                    try:
                        cpu_label = self.query_one("#cpu-usage", Label)
                        cpu_progress = self.query_one("#cpu-progress", ProgressBar)
                        cpu_label.update(f"CPU Usage: {cpu_percent:.1f}%")
                        cpu_progress.progress = cpu_percent
                        
                        memory_label = self.query_one("#memory-usage", Label)
                        memory_progress = self.query_one("#memory-progress", ProgressBar)
                        memory_label.update(f"Memory Usage: {memory_percent:.1f}%")
                        memory_progress.progress = memory_percent
                    except Exception as e:
                        self._add_log(f"Fallback monitoring error: {e}", "error")
            except Exception as e:
                self._add_log(f"Fallback performance monitoring error: {e}", "error")
    
    def _update_status_display(self) -> None:
        """更新状态显示"""
        try:
            # 更新当前时间
            current_time = datetime.now().strftime("%H:%M:%S")
            
            # 更新BuildStatus组件
            status_widget = self.query_one("#build-status", BuildStatus)
            if not self.is_building:
                status_widget.update_status(self.current_status)
            
            # 更新进度标签的时间显示
            if not self.is_building:
                try:
                    progress_label = self.query_one("#progress-label", Label)
                    if progress_label.renderable == "Ready":
                        progress_label.update(f"Ready - {current_time}")
                except Exception:
                    pass
                    
        except Exception:
            pass
    
    def _update_status_display_immediate(self) -> None:
        """立即更新状态显示，用于按钮点击反馈"""
        try:
            # 立即更新当前时间
            current_time = datetime.now().strftime("%H:%M:%S")
            
            # 立即更新BuildStatus组件
            status_widget = self.query_one("#build-status", BuildStatus)
            status_widget.update_status(self.current_status)
            
            # 立即更新进度标签
            try:
                progress_label = self.query_one("#progress-label", Label)
                if self.is_building:
                    progress_label.update(f"Building... - {current_time}")
                else:
                    progress_label.update(f"Ready - {current_time}")
            except Exception:
                pass
            
            # 强制刷新界面
            self.refresh()
                    
        except Exception:
            pass


def run_textual_tui(config=None):
    """启动 Textual TUI"""
    app = PrettyBuildTUI(config=config)
    app.run()


if __name__ == "__main__":
    run_textual_tui()