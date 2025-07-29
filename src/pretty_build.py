#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 Pretty Build - Universal Build Wrapper with Rich
A beautiful wrapper for various build systems using Rich library

Enhanced version with responsive grid layout, keyboard interactions, and real-time configuration.
"""

import asyncio
import shutil
import subprocess
import sys
import re
import time
import argparse
import os
import signal
import threading
import queue
import json
import hashlib
import pickle
import psutil
import platform
import socket
from datetime import datetime
from typing import Tuple, Optional, Dict, List, Any, Protocol, NamedTuple, Callable, Union
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
from contextlib import contextmanager
from abc import ABC, abstractmethod
import configparser
import tempfile
import logging

# Rich imports
from rich.console import Console, Group
from rich.panel import Panel
from rich.progress import (
    Progress,
    BarColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
    MofNCompleteColumn,
    SpinnerColumn
)
from rich.text import Text
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from rich.align import Align
from rich.rule import Rule
from rich.tree import Tree
from rich import box
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich.status import Status
from rich.columns import Columns
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.traceback import install
from rich.padding import Padding
from rich.spinner import Spinner
from rich.layout import Layout
from rich.live import Live
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn, TimeRemainingColumn
from rich.align import Align
from rich.console import Group
import time

# Install rich traceback handler
install(show_locals=True)


# === Enhanced Type Definitions ===
class MessageType(Enum):
    """Build message types for better categorization"""
    PROGRESS = "progress"
    ERROR = "error"
    WARNING = "warning"
    SUCCESS = "success"
    INFO = "info"
    DEBUG = "debug"
    MEMORY = "memory"  # New type for memory usage
    PERFORMANCE = "performance"  # New type for performance metrics
    CACHE = "cache"  # New type for cache operations


class InteractionMode(Enum):
    """Keyboard interaction modes"""
    NORMAL = "normal"
    CONFIG = "config"
    HELP = "help"
    MENU = "menu"
    PERFORMANCE = "performance"
    PLUGINS = "plugins"


class KeyAction(Enum):
    """Available keyboard actions"""
    PAUSE_RESUME = "pause_resume"
    ABORT = "abort"
    CONFIG = "config"
    HELP = "help"
    VERBOSE = "verbose"
    CLEAR = "clear"
    SAVE_LOG = "save_log"
    MENU = "menu"
    REFRESH = "refresh"
    PERFORMANCE = "performance"
    PLUGINS = "plugins"
    CACHE_CLEAR = "cache_clear"
    NOTIFICATIONS = "notifications"


class BuildPhase(Enum):
    """Build phases for better tracking"""
    INITIALIZATION = "initialization"
    CONFIGURATION = "configuration"
    COMPILATION = "compilation"
    LINKING = "linking"
    PACKAGING = "packaging"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    CLEANUP = "cleanup"


class NotificationType(Enum):
    """Notification types"""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class CacheStatus(Enum):
    """Cache operation status"""
    HIT = "hit"
    MISS = "miss"
    INVALID = "invalid"
    UPDATED = "updated"


@dataclass(frozen=True)
class GridConfig:
    """Responsive grid configuration"""
    min_width: int = 80
    breakpoints: Dict[str, int] = field(default_factory=lambda: {
        'xs': 480,
        'sm': 768,
        'md': 1024,
        'lg': 1280,
        'xl': 1536
    })

    def get_breakpoint(self, width: int) -> str:
        """Get current breakpoint based on terminal width"""
        for name, min_width in reversed(self.breakpoints.items()):
            if width >= min_width:
                return name
        return 'xs'


@dataclass
class BuildConfig:
    """Enhanced build configuration"""
    parallel_jobs: int = field(default_factory=lambda: os.cpu_count() or 4)
    verbose_mode: bool = False
    debug_mode: bool = False
    optimization_level: str = "O2"
    warnings_as_errors: bool = False
    enable_sanitizers: bool = False
    custom_flags: List[str] = field(default_factory=list)
    target_arch: str = "native"
    build_type: str = "Release"
    
    # Enhanced configuration options
    enable_cache: bool = True
    cache_dir: str = field(default_factory=lambda: str(Path.home() / ".pretty_build_cache"))
    enable_notifications: bool = True
    notification_sound: bool = False
    auto_save_logs: bool = True
    log_level: str = "INFO"
    max_log_files: int = 10
    enable_performance_monitoring: bool = True
    memory_limit_mb: Optional[int] = None
    timeout_seconds: Optional[int] = None
    retry_on_failure: bool = False
    max_retries: int = 3
    incremental_build: bool = True
    ccache_enabled: bool = True
    distcc_enabled: bool = False
    unity_build: bool = False
    link_time_optimization: bool = False
    profile_guided_optimization: bool = False
    
    # Plugin configuration
    enabled_plugins: List[str] = field(default_factory=list)
    plugin_config: Dict[str, Any] = field(default_factory=dict)

    def to_cmake_args(self) -> List[str]:
        """Convert to CMake arguments"""
        args = []
        if self.build_type:
            args.extend(['-DCMAKE_BUILD_TYPE=' + self.build_type])
        if self.optimization_level and self.build_type == "Release":
            args.extend([f'-DCMAKE_CXX_FLAGS_RELEASE=-{self.optimization_level} -DNDEBUG'])
        if self.warnings_as_errors:
            args.extend(['-DCMAKE_CXX_FLAGS=-Werror'])
        if self.unity_build:
            args.extend(['-DCMAKE_UNITY_BUILD=ON'])
        if self.link_time_optimization:
            args.extend(['-DCMAKE_INTERPROCEDURAL_OPTIMIZATION=ON'])
        if self.ccache_enabled and shutil.which('ccache'):
            args.extend(['-DCMAKE_CXX_COMPILER_LAUNCHER=ccache'])
        return args

    def to_make_args(self) -> List[str]:
        """Convert to Make arguments"""
        args = []
        if self.parallel_jobs > 1:
            args.extend(['-j', str(self.parallel_jobs)])
        if self.verbose_mode:
            args.append('VERBOSE=1')
        args.extend(self.custom_flags)
        return args

    def to_ninja_args(self) -> List[str]:
        """Convert to Ninja arguments"""
        args = []
        if self.parallel_jobs > 1:
            args.extend(['-j', str(self.parallel_jobs)])
        if self.verbose_mode:
            args.append('-v')
        return args
    
    def save_to_file(self, path: Path):
        """Save configuration to file"""
        config = configparser.ConfigParser()
        config['build'] = {
            'parallel_jobs': str(self.parallel_jobs),
            'verbose_mode': str(self.verbose_mode),
            'debug_mode': str(self.debug_mode),
            'optimization_level': self.optimization_level,
            'warnings_as_errors': str(self.warnings_as_errors),
            'enable_sanitizers': str(self.enable_sanitizers),
            'target_arch': self.target_arch,
            'build_type': self.build_type,
            'enable_cache': str(self.enable_cache),
            'cache_dir': self.cache_dir,
            'enable_notifications': str(self.enable_notifications),
            'notification_sound': str(self.notification_sound),
            'auto_save_logs': str(self.auto_save_logs),
            'log_level': self.log_level,
            'max_log_files': str(self.max_log_files),
            'enable_performance_monitoring': str(self.enable_performance_monitoring),
            'retry_on_failure': str(self.retry_on_failure),
            'max_retries': str(self.max_retries),
            'incremental_build': str(self.incremental_build),
            'ccache_enabled': str(self.ccache_enabled),
            'distcc_enabled': str(self.distcc_enabled),
            'unity_build': str(self.unity_build),
            'link_time_optimization': str(self.link_time_optimization),
            'profile_guided_optimization': str(self.profile_guided_optimization),
        }
        
        if self.memory_limit_mb:
            config['build']['memory_limit_mb'] = str(self.memory_limit_mb)
        if self.timeout_seconds:
            config['build']['timeout_seconds'] = str(self.timeout_seconds)
            
        config['custom_flags'] = {f'flag_{i}': flag for i, flag in enumerate(self.custom_flags)}
        config['enabled_plugins'] = {f'plugin_{i}': plugin for i, plugin in enumerate(self.enabled_plugins)}
        
        with open(path, 'w') as f:
            config.write(f)
    
    @classmethod
    def load_from_file(cls, path: Path) -> 'BuildConfig':
        """Load configuration from file"""
        config = configparser.ConfigParser()
        config.read(path)
        
        build_config = cls()
        
        if 'build' in config:
            build_section = config['build']
            build_config.parallel_jobs = build_section.getint('parallel_jobs', build_config.parallel_jobs)
            build_config.verbose_mode = build_section.getboolean('verbose_mode', build_config.verbose_mode)
            build_config.debug_mode = build_section.getboolean('debug_mode', build_config.debug_mode)
            build_config.optimization_level = build_section.get('optimization_level', build_config.optimization_level)
            build_config.warnings_as_errors = build_section.getboolean('warnings_as_errors', build_config.warnings_as_errors)
            build_config.enable_sanitizers = build_section.getboolean('enable_sanitizers', build_config.enable_sanitizers)
            build_config.target_arch = build_section.get('target_arch', build_config.target_arch)
            build_config.build_type = build_section.get('build_type', build_config.build_type)
            build_config.enable_cache = build_section.getboolean('enable_cache', build_config.enable_cache)
            build_config.cache_dir = build_section.get('cache_dir', build_config.cache_dir)
            build_config.enable_notifications = build_section.getboolean('enable_notifications', build_config.enable_notifications)
            build_config.notification_sound = build_section.getboolean('notification_sound', build_config.notification_sound)
            build_config.auto_save_logs = build_section.getboolean('auto_save_logs', build_config.auto_save_logs)
            build_config.log_level = build_section.get('log_level', build_config.log_level)
            build_config.max_log_files = build_section.getint('max_log_files', build_config.max_log_files)
            build_config.enable_performance_monitoring = build_section.getboolean('enable_performance_monitoring', build_config.enable_performance_monitoring)
            build_config.retry_on_failure = build_section.getboolean('retry_on_failure', build_config.retry_on_failure)
            build_config.max_retries = build_section.getint('max_retries', build_config.max_retries)
            build_config.incremental_build = build_section.getboolean('incremental_build', build_config.incremental_build)
            build_config.ccache_enabled = build_section.getboolean('ccache_enabled', build_config.ccache_enabled)
            build_config.distcc_enabled = build_section.getboolean('distcc_enabled', build_config.distcc_enabled)
            build_config.unity_build = build_section.getboolean('unity_build', build_config.unity_build)
            build_config.link_time_optimization = build_section.getboolean('link_time_optimization', build_config.link_time_optimization)
            build_config.profile_guided_optimization = build_section.getboolean('profile_guided_optimization', build_config.profile_guided_optimization)
            
            if 'memory_limit_mb' in build_section:
                build_config.memory_limit_mb = build_section.getint('memory_limit_mb')
            if 'timeout_seconds' in build_section:
                build_config.timeout_seconds = build_section.getint('timeout_seconds')
        
        if 'custom_flags' in config:
            build_config.custom_flags = list(config['custom_flags'].values())
        
        if 'enabled_plugins' in config:
            build_config.enabled_plugins = list(config['enabled_plugins'].values())
            
        return build_config


@dataclass
class KeyBinding:
    """Keyboard binding configuration"""
    key: str
    action: KeyAction
    description: str
    modifier: Optional[str] = None


# Default key bindings
DEFAULT_KEY_BINDINGS = [
    KeyBinding('p', KeyAction.PAUSE_RESUME, '暂停/恢复构建'),
    KeyBinding('q', KeyAction.ABORT, '中止构建 (Ctrl+C)'),
    KeyBinding('c', KeyAction.CONFIG, '配置构建参数'),
    KeyBinding('h', KeyAction.HELP, '显示帮助'),
    KeyBinding('v', KeyAction.VERBOSE, '切换详细模式'),
    KeyBinding('l', KeyAction.CLEAR, '清空输出'),
    KeyBinding('s', KeyAction.SAVE_LOG, '保存构建日志'),
    KeyBinding('m', KeyAction.MENU, '显示菜单'),
    KeyBinding('r', KeyAction.REFRESH, '刷新显示'),
    KeyBinding('f', KeyAction.PERFORMANCE, '性能分析'),
    KeyBinding('g', KeyAction.PLUGINS, '插件管理'),
    KeyBinding('x', KeyAction.CACHE_CLEAR, '清理缓存'),
    KeyBinding('n', KeyAction.NOTIFICATIONS, '通知设置'),
]


# === Plugin System ===
class BuildPlugin(ABC):
    """Abstract base class for build plugins"""
    
    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.enabled = True
    
    @abstractmethod
    def initialize(self, config: BuildConfig, console: Console) -> bool:
        """Initialize the plugin"""
        pass
    
    @abstractmethod
    def on_build_start(self, build_state: 'BuildState') -> None:
        """Called when build starts"""
        pass
    
    @abstractmethod
    def on_build_end(self, build_state: 'BuildState', return_code: int) -> None:
        """Called when build ends"""
        pass
    
    @abstractmethod
    def process_message(self, message: str, msg_type: MessageType) -> Optional[str]:
        """Process build messages, return modified message or None"""
        pass
    
    def cleanup(self) -> None:
        """Cleanup plugin resources"""
        pass


class PluginManager:
    """Plugin management system"""
    
    def __init__(self, console: Console):
        self.console = console
        self.plugins: Dict[str, BuildPlugin] = {}
        self.plugin_dir = Path.home() / ".pretty_build_plugins"
        self.plugin_dir.mkdir(exist_ok=True)
    
    def register_plugin(self, plugin: BuildPlugin) -> bool:
        """Register a plugin"""
        try:
            if plugin.name in self.plugins:
                self.console.print(f"[yellow]插件 {plugin.name} 已存在，将被替换[/yellow]")
            
            self.plugins[plugin.name] = plugin
            self.console.print(f"[green]插件 {plugin.name} v{plugin.version} 注册成功[/green]")
            return True
        except Exception as e:
            self.console.print(f"[red]插件 {plugin.name} 注册失败: {e}[/red]")
            return False
    
    def initialize_plugins(self, config: BuildConfig) -> None:
        """Initialize all enabled plugins"""
        for name, plugin in self.plugins.items():
            if plugin.enabled and name in config.enabled_plugins:
                try:
                    if plugin.initialize(config, self.console):
                        self.console.print(f"[green]插件 {name} 初始化成功[/green]")
                    else:
                        self.console.print(f"[yellow]插件 {name} 初始化失败[/yellow]")
                        plugin.enabled = False
                except Exception as e:
                    self.console.print(f"[red]插件 {name} 初始化异常: {e}[/red]")
                    plugin.enabled = False
    
    def on_build_start(self, build_state: 'BuildState') -> None:
        """Notify all plugins of build start"""
        for plugin in self.plugins.values():
            if plugin.enabled:
                try:
                    plugin.on_build_start(build_state)
                except Exception as e:
                    self.console.print(f"[red]插件 {plugin.name} 构建开始回调异常: {e}[/red]")
    
    def on_build_end(self, build_state: 'BuildState', return_code: int) -> None:
        """Notify all plugins of build end"""
        for plugin in self.plugins.values():
            if plugin.enabled:
                try:
                    plugin.on_build_end(build_state, return_code)
                except Exception as e:
                    self.console.print(f"[red]插件 {plugin.name} 构建结束回调异常: {e}[/red]")
    
    def process_message(self, message: str, msg_type: MessageType) -> str:
        """Process message through all plugins"""
        processed_message = message
        for plugin in self.plugins.values():
            if plugin.enabled:
                try:
                    result = plugin.process_message(processed_message, msg_type)
                    if result is not None:
                        processed_message = result
                except Exception as e:
                    self.console.print(f"[red]插件 {plugin.name} 消息处理异常: {e}[/red]")
        return processed_message
    
    def cleanup_plugins(self) -> None:
        """Cleanup all plugins"""
        for plugin in self.plugins.values():
            try:
                plugin.cleanup()
            except Exception as e:
                self.console.print(f"[red]插件 {plugin.name} 清理异常: {e}[/red]")


# === Build Cache System ===
class BuildCache:
    """Intelligent build cache system"""
    
    def __init__(self, cache_dir: str, console: Console):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.console = console
        self.cache_index_file = self.cache_dir / "cache_index.json"
        self.cache_index = self._load_cache_index()
    
    def _load_cache_index(self) -> Dict[str, Any]:
        """Load cache index from file"""
        if self.cache_index_file.exists():
            try:
                with open(self.cache_index_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.console.print(f"[yellow]缓存索引加载失败: {e}[/yellow]")
        return {"files": {}, "targets": {}, "metadata": {"version": "1.0"}}
    
    def _save_cache_index(self) -> None:
        """Save cache index to file"""
        try:
            with open(self.cache_index_file, 'w') as f:
                json.dump(self.cache_index, f, indent=2)
        except Exception as e:
            self.console.print(f"[red]缓存索引保存失败: {e}[/red]")
    
    def _get_file_hash(self, file_path: Path) -> str:
        """Get file content hash"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception:
            return ""
    
    def _get_file_mtime(self, file_path: Path) -> float:
        """Get file modification time"""
        try:
            return file_path.stat().st_mtime
        except Exception:
            return 0.0
    
    def check_file_changed(self, file_path: Path) -> bool:
        """Check if file has changed since last cache"""
        file_str = str(file_path)
        if file_str not in self.cache_index["files"]:
            return True
        
        cached_info = self.cache_index["files"][file_str]
        current_mtime = self._get_file_mtime(file_path)
        
        # Quick check with modification time
        if current_mtime != cached_info.get("mtime", 0):
            # Double check with hash for accuracy
            current_hash = self._get_file_hash(file_path)
            return current_hash != cached_info.get("hash", "")
        
        return False
    
    def update_file_cache(self, file_path: Path) -> None:
        """Update cache information for a file"""
        file_str = str(file_path)
        self.cache_index["files"][file_str] = {
            "hash": self._get_file_hash(file_path),
            "mtime": self._get_file_mtime(file_path),
            "cached_at": time.time()
        }
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_files = len(self.cache_index["files"])
        cache_size = 0
        
        try:
            for item in self.cache_dir.rglob("*"):
                if item.is_file():
                    cache_size += item.stat().st_size
        except Exception:
            pass
        
        return {
            "total_files": total_files,
            "cache_size_mb": cache_size / (1024 * 1024),
            "cache_dir": str(self.cache_dir)
        }
    
    def clear_cache(self) -> bool:
        """Clear all cache data"""
        try:
            import shutil
            if self.cache_dir.exists():
                shutil.rmtree(self.cache_dir)
                self.cache_dir.mkdir(parents=True, exist_ok=True)
            self.cache_index = {"files": {}, "targets": {}, "metadata": {"version": "1.0"}}
            self._save_cache_index()
            self.console.print("[green]缓存已清理[/green]")
            return True
        except Exception as e:
            self.console.print(f"[red]缓存清理失败: {e}[/red]")
            return False
    
    def save(self) -> None:
        """Save cache index"""
        self._save_cache_index()


# === Performance Monitor ===
@dataclass
class PerformanceMetrics:
    """Performance metrics data"""
    cpu_usage: float = 0.0
    memory_usage_mb: float = 0.0
    disk_io_read_mb: float = 0.0
    disk_io_write_mb: float = 0.0
    network_io_mb: float = 0.0
    build_time_seconds: float = 0.0
    compilation_rate: float = 0.0  # files per second
    peak_memory_mb: float = 0.0
    average_cpu: float = 0.0


class PerformanceMonitor:
    """Real-time performance monitoring"""
    
    def __init__(self, console: Console):
        self.console = console
        self.metrics = PerformanceMetrics()
        self.monitoring = False
        self.start_time = 0.0
        self.process: Optional[psutil.Process] = None
        self.monitor_thread: Optional[threading.Thread] = None
        self.metrics_history: List[PerformanceMetrics] = []
        
    def start_monitoring(self, process_pid: Optional[int] = None) -> None:
        """Start performance monitoring"""
        self.monitoring = True
        self.start_time = time.time()
        
        if process_pid:
            try:
                self.process = psutil.Process(process_pid)
            except psutil.NoSuchProcess:
                self.console.print(f"[yellow]进程 {process_pid} 不存在[/yellow]")
        
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self) -> None:
        """Stop performance monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
    
    def _monitor_loop(self) -> None:
        """Performance monitoring loop"""
        while self.monitoring:
            try:
                current_metrics = PerformanceMetrics()
                
                # System-wide metrics
                current_metrics.cpu_usage = psutil.cpu_percent(interval=0.1)
                memory = psutil.virtual_memory()
                current_metrics.memory_usage_mb = memory.used / (1024 * 1024)
                
                # Process-specific metrics
                if self.process and self.process.is_running():
                    try:
                        proc_memory = self.process.memory_info()
                        current_metrics.peak_memory_mb = max(
                            current_metrics.peak_memory_mb,
                            proc_memory.rss / (1024 * 1024)
                        )
                        current_metrics.cpu_usage = self.process.cpu_percent()
                    except psutil.NoSuchProcess:
                        self.process = None
                
                current_metrics.build_time_seconds = time.time() - self.start_time
                
                # Update running averages
                if self.metrics_history:
                    self.metrics.average_cpu = sum(m.cpu_usage for m in self.metrics_history[-10:]) / min(10, len(self.metrics_history))
                
                self.metrics = current_metrics
                self.metrics_history.append(current_metrics)
                
                # Keep only recent history
                if len(self.metrics_history) > 100:
                    self.metrics_history = self.metrics_history[-50:]
                
                time.sleep(1.0)
                
            except Exception as e:
                self.console.print(f"[red]性能监控异常: {e}[/red]")
                time.sleep(1.0)
    
    def get_metrics(self) -> PerformanceMetrics:
        """Get current performance metrics"""
        return self.metrics
    
    def get_performance_report(self) -> str:
        """Generate performance report"""
        if not self.metrics_history:
            return "无性能数据"
        
        avg_cpu = sum(m.cpu_usage for m in self.metrics_history) / len(self.metrics_history)
        max_memory = max(m.memory_usage_mb for m in self.metrics_history)
        
        report = f"""
性能报告:
- 平均 CPU 使用率: {avg_cpu:.1f}%
- 峰值内存使用: {max_memory:.1f} MB
- 构建时间: {self.metrics.build_time_seconds:.1f} 秒
- 监控样本数: {len(self.metrics_history)}
"""
        return report.strip()


# === Notification System ===
class NotificationManager:
    """Cross-platform notification system"""
    
    def __init__(self, console: Console, config: BuildConfig):
        self.console = console
        self.config = config
        self.notifications_enabled = config.enable_notifications
    
    def send_notification(self, title: str, message: str, notification_type: NotificationType = NotificationType.INFO) -> None:
        """Send a system notification"""
        if not self.notifications_enabled:
            return
        
        try:
            if platform.system() == "Windows":
                self._send_windows_notification(title, message, notification_type)
            elif platform.system() == "Darwin":  # macOS
                self._send_macos_notification(title, message, notification_type)
            elif platform.system() == "Linux":
                self._send_linux_notification(title, message, notification_type)
            
            if self.config.notification_sound:
                self._play_notification_sound(notification_type)
                
        except Exception as e:
            self.console.print(f"[yellow]通知发送失败: {e}[/yellow]")
    
    def _send_windows_notification(self, title: str, message: str, notification_type: NotificationType) -> None:
        """Send Windows notification"""
        try:
            import win10toast
            toaster = win10toast.ToastNotifier()
            icon_path = None  # You can add custom icons here
            toaster.show_toast(title, message, icon_path=icon_path, duration=5)
        except ImportError:
            # Fallback to simple console notification
            self.console.print(f"[bold cyan]通知: {title}[/bold cyan] - {message}")
    
    def _send_macos_notification(self, title: str, message: str, notification_type: NotificationType) -> None:
        """Send macOS notification"""
        try:
            import subprocess
            subprocess.run([
                "osascript", "-e",
                f'display notification "{message}" with title "{title}"'
            ], check=True)
        except Exception:
            self.console.print(f"[bold cyan]通知: {title}[/bold cyan] - {message}")
    
    def _send_linux_notification(self, title: str, message: str, notification_type: NotificationType) -> None:
        """Send Linux notification"""
        try:
            import subprocess
            subprocess.run([
                "notify-send", title, message
            ], check=True)
        except Exception:
            self.console.print(f"[bold cyan]通知: {title}[/bold cyan] - {message}")
    
    def _play_notification_sound(self, notification_type: NotificationType) -> None:
        """Play notification sound"""
        try:
            if platform.system() == "Windows":
                import ctypes
                if notification_type == NotificationType.ERROR:
                    ctypes.windll.user32.MessageBeep(0x00000010)  # MB_ICONHAND
                elif notification_type == NotificationType.SUCCESS:
                    ctypes.windll.user32.MessageBeep(0x00000040)  # MB_ICONASTERISK
                else:
                    ctypes.windll.user32.MessageBeep(0x00000040)  # MB_ICONASTERISK
        except Exception:
            pass  # Ignore sound errors


# === TUI System ===
class TUIScreen(Enum):
    """TUI screen types"""
    MAIN = "main"
    BUILD = "build"
    CONFIG = "config"
    LOGS = "logs"
    PERFORMANCE = "performance"
    PLUGINS = "plugins"
    HELP = "help"


@dataclass
class TUIState:
    """TUI application state"""
    current_screen: TUIScreen = TUIScreen.MAIN
    build_running: bool = False
    build_paused: bool = False
    selected_menu_item: int = 0
    log_scroll_position: int = 0
    show_help: bool = False
    last_key: Optional[str] = None
    status_message: str = ""
    build_progress: float = 0.0


class TUIManager:
    """Text User Interface Manager"""
    
    def __init__(self, console: Console, config: BuildConfig):
        self.console = console
        self.config = config
        self.state = TUIState()
        self.layout = Layout()
        self.live: Optional[Live] = None
        self.key_bindings = {kb.key: kb for kb in DEFAULT_KEY_BINDINGS}
        self.menu_items = [
            "🚀 开始构建",
            "⚙️  配置设置", 
            "📊 性能监控",
            "🔌 插件管理",
            "📋 查看日志",
            "🧹 清理项目",
            "❓ 帮助",
            "🚪 退出"
        ]
        self.build_runner: Optional['InteractiveBuildRunner'] = None
        
    def set_build_runner(self, runner: 'InteractiveBuildRunner'):
        """Set the build runner reference"""
        self.build_runner = runner
        
    def setup_layout(self):
        """Setup the TUI layout"""
        self.layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=3)
        )
        
        self.layout["main"].split_row(
            Layout(name="sidebar", size=30),
            Layout(name="content", ratio=1)
        )
        
    def create_header(self) -> Panel:
        """Create header panel"""
        title = Text("🚀 Pretty Build TUI", style="bold cyan")
        if self.state.build_running:
            status = Text(" [构建中...]", style="yellow blink")
            title.append(status)
        elif self.state.build_paused:
            status = Text(" [已暂停]", style="red")
            title.append(status)
            
        return Panel(
            Align.center(title),
            box=box.ROUNDED,
            style="cyan"
        )
        
    def create_sidebar(self) -> Panel:
        """Create sidebar with menu"""
        menu_table = Table(show_header=False, box=None, padding=(0, 1))
        menu_table.add_column("", style="white")
        
        for i, item in enumerate(self.menu_items):
            style = "bold yellow on blue" if i == self.state.selected_menu_item else "white"
            prefix = "▶ " if i == self.state.selected_menu_item else "  "
            menu_table.add_row(f"{prefix}{item}", style=style)
            
        return Panel(
            menu_table,
            title="📋 菜单",
            box=box.ROUNDED,
            style="blue"
        )
        
    def create_main_content(self) -> Panel:
        """Create main content area based on current screen"""
        if self.state.current_screen == TUIScreen.MAIN:
            return self.create_main_screen()
        elif self.state.current_screen == TUIScreen.BUILD:
            return self.create_build_screen()
        elif self.state.current_screen == TUIScreen.CONFIG:
            return self.create_config_screen()
        elif self.state.current_screen == TUIScreen.LOGS:
            return self.create_logs_screen()
        elif self.state.current_screen == TUIScreen.PERFORMANCE:
            return self.create_performance_screen()
        elif self.state.current_screen == TUIScreen.PLUGINS:
            return self.create_plugins_screen()
        elif self.state.current_screen == TUIScreen.HELP:
            return self.create_help_screen()
        else:
            return Panel("未知屏幕", title="错误")
            
    def create_main_screen(self) -> Panel:
        """Create main welcome screen"""
        content = Group(
            Text("欢迎使用 Pretty Build TUI!", style="bold green", justify="center"),
            Text(""),
            Text("使用方向键导航菜单，回车键选择", justify="center"),
            Text("按 'q' 退出，'h' 查看帮助", justify="center"),
            Text(""),
            self.create_project_info(),
            Text(""),
            self.create_quick_stats()
        )
        
        return Panel(
            content,
            title="🏠 主页",
            box=box.ROUNDED,
            style="green"
        )
        
    def create_project_info(self) -> Table:
        """Create project information table"""
        table = Table(title="📁 项目信息", box=box.SIMPLE)
        table.add_column("属性", style="cyan")
        table.add_column("值", style="white")
        
        cwd = Path.cwd()
        table.add_row("项目目录", str(cwd))
        table.add_row("构建系统", "CMake + Ninja")
        table.add_row("构建类型", self.config.build_type)
        table.add_row("并行任务", str(self.config.parallel_jobs))
        table.add_row("详细模式", "是" if self.config.verbose_mode else "否")
        
        return table
        
    def create_quick_stats(self) -> Table:
        """Create quick statistics table"""
        table = Table(title="📊 快速统计", box=box.SIMPLE)
        table.add_column("指标", style="cyan")
        table.add_column("值", style="white")
        
        # Add some basic stats
        table.add_row("CPU 核心数", str(os.cpu_count() or "未知"))
        table.add_row("可用内存", f"{psutil.virtual_memory().available // (1024**3)} GB")
        table.add_row("磁盘空间", f"{psutil.disk_usage('.').free // (1024**3)} GB")
        
        return table
        
    def create_build_screen(self) -> Panel:
        """Create build progress screen"""
        if not self.build_runner:
            return Panel("构建器未初始化", title="错误", style="red")
            
        content = Group(
            Text("构建进度", style="bold yellow"),
            Text(""),
            self.create_build_progress(),
            Text(""),
            self.create_build_stats(),
            Text(""),
            Text("按 'p' 暂停/恢复，'q' 中止构建", style="dim")
        )
        
        return Panel(
            content,
            title="🔨 构建中",
            box=box.ROUNDED,
            style="yellow"
        )
        
    def create_build_progress(self) -> Progress:
        """Create build progress bar"""
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
        )
        
        task = progress.add_task("构建中...", total=100)
        progress.update(task, completed=self.state.build_progress)
        
        return progress
        
    def create_build_stats(self) -> Table:
        """Create build statistics table"""
        table = Table(title="构建统计", box=box.SIMPLE)
        table.add_column("指标", style="cyan")
        table.add_column("值", style="white")
        
        if self.build_runner and hasattr(self.build_runner, 'build_state'):
            state = self.build_runner.build_state
            table.add_row("已编译文件", str(state.stats.files_compiled))
            table.add_row("构建目标", str(state.stats.targets_built))
            table.add_row("错误数", str(state.stats.errors))
            table.add_row("警告数", str(state.stats.warnings))
        else:
            table.add_row("状态", "等待中...")
            
        return table
        
    def create_config_screen(self) -> Panel:
        """Create configuration screen"""
        content = Group(
            Text("构建配置", style="bold cyan"),
            Text(""),
            self.create_config_table(),
            Text(""),
            Text("按数字键编辑对应配置项", style="dim")
        )
        
        return Panel(
            content,
            title="⚙️ 配置",
            box=box.ROUNDED,
            style="cyan"
        )
        
    def create_config_table(self) -> Table:
        """Create configuration table"""
        table = Table(box=box.SIMPLE)
        table.add_column("#", style="dim", width=3)
        table.add_column("配置项", style="cyan")
        table.add_column("当前值", style="yellow")
        table.add_column("描述", style="white")
        
        configs = [
            ("1", "详细输出", str(self.config.verbose_mode), "显示详细构建信息"),
            ("2", "并行任务", str(self.config.parallel_jobs), "并行编译任务数"),
            ("3", "构建类型", self.config.build_type, "Debug/Release"),
            ("4", "启用通知", str(self.config.enable_notifications), "系统通知"),
            ("5", "性能监控", str(self.config.enable_performance_monitoring), "实时性能监控"),
            ("6", "启用缓存", str(self.config.enable_cache), "构建缓存"),
        ]
        
        for num, name, value, desc in configs:
            table.add_row(num, name, value, desc)
            
        return table
        
    def create_logs_screen(self) -> Panel:
        """Create logs viewing screen"""
        content = Group(
            Text("构建日志", style="bold green"),
            Text(""),
            Text("最近的构建输出:", style="dim"),
            Text(""),
            # Here you would add actual log content
            Text("暂无日志内容", style="dim italic"),
            Text(""),
            Text("按 'c' 清空日志，'s' 保存日志", style="dim")
        )
        
        return Panel(
            content,
            title="📋 日志",
            box=box.ROUNDED,
            style="green"
        )
        
    def create_performance_screen(self) -> Panel:
        """Create performance monitoring screen"""
        content = Group(
            Text("性能监控", style="bold magenta"),
            Text(""),
            self.create_performance_table(),
            Text(""),
            Text("实时系统性能指标", style="dim")
        )
        
        return Panel(
            content,
            title="📊 性能",
            box=box.ROUNDED,
            style="magenta"
        )
        
    def create_performance_table(self) -> Table:
        """Create performance metrics table"""
        table = Table(box=box.SIMPLE)
        table.add_column("指标", style="cyan")
        table.add_column("当前值", style="yellow")
        table.add_column("状态", style="white")
        
        # Get current system metrics
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('.')
        
        table.add_row("CPU 使用率", f"{cpu_percent:.1f}%", "🟢" if cpu_percent < 80 else "🟡" if cpu_percent < 95 else "🔴")
        table.add_row("内存使用", f"{memory.percent:.1f}%", "🟢" if memory.percent < 80 else "🟡" if memory.percent < 95 else "🔴")
        table.add_row("磁盘使用", f"{(disk.used/disk.total)*100:.1f}%", "🟢")
        
        return table
        
    def create_plugins_screen(self) -> Panel:
        """Create plugins management screen"""
        content = Group(
            Text("插件管理", style="bold blue"),
            Text(""),
            self.create_plugins_table(),
            Text(""),
            Text("管理构建插件", style="dim")
        )
        
        return Panel(
            content,
            title="🔌 插件",
            box=box.ROUNDED,
            style="blue"
        )
        
    def create_plugins_table(self) -> Table:
        """Create plugins table"""
        table = Table(box=box.SIMPLE)
        table.add_column("插件名", style="cyan")
        table.add_column("版本", style="yellow")
        table.add_column("状态", style="white")
        table.add_column("描述", style="dim")
        
        # Add some example plugins
        table.add_row("logging", "1.0.0", "✅ 已启用", "构建日志记录")
        table.add_row("notifications", "1.0.0", "❌ 已禁用", "系统通知")
        
        return table
        
    def create_help_screen(self) -> Panel:
        """Create help screen"""
        help_content = Group(
            Text("快捷键帮助", style="bold yellow"),
            Text(""),
            self.create_keybindings_table(),
            Text(""),
            Text("使用说明:", style="bold"),
            Text("• 按数字键 1-6 切换不同屏幕"),
            Text("• 按 'q' 退出程序"),
            Text("• 按 'h' 显示此帮助屏幕"),
            Text("• 按 'b' 快速进入构建屏幕"),
            Text("• 按 'c' 快速进入配置屏幕"),
            Text(""),
            Text("屏幕导航:", style="bold"),
            Text("1 - 主页    2 - 构建    3 - 配置"),
            Text("4 - 日志    5 - 性能    6 - 插件"),
        )
        
        return Panel(
            help_content,
            title="❓ 帮助",
            box=box.ROUNDED,
            style="yellow"
        )
        
    def create_keybindings_table(self) -> Table:
        """Create keybindings help table"""
        table = Table(box=box.SIMPLE)
        table.add_column("按键", style="cyan", width=8)
        table.add_column("功能", style="white")
        
        # Current TUI keybindings
        keybindings = [
            ("Q", "退出程序"),
            ("H", "显示帮助"),
            ("1", "主页屏幕"),
            ("2", "构建屏幕"),
            ("3", "配置屏幕"),
            ("4", "日志屏幕"),
            ("5", "性能监控"),
            ("6", "插件管理"),
            ("B", "快速构建"),
            ("C", "快速配置"),
        ]
        
        for key, description in keybindings:
            table.add_row(key, description)
            
        return table
        
    def create_footer(self) -> Panel:
        """Create footer panel"""
        footer_content = Group(
            Text(f"状态: {self.state.status_message}", style="white"),
            Text(f"最后按键: {self.state.last_key or '无'} | 当前屏幕: {self.state.current_screen.value}", style="dim")
        )
        
        return Panel(
            footer_content,
            box=box.ROUNDED,
            style="blue"
        )
        
    def handle_key(self, key: str) -> bool:
        """Handle keyboard input"""
        self.state.last_key = key
        
        # Global keys
        if key.lower() == 'q':
            return False  # Exit
        elif key.lower() == 'h':
            self.state.current_screen = TUIScreen.HELP
        elif key.lower() == 'esc':
            self.state.current_screen = TUIScreen.MAIN
            
        # Navigation keys
        elif key == 'up':
            self.state.selected_menu_item = max(0, self.state.selected_menu_item - 1)
        elif key == 'down':
            self.state.selected_menu_item = min(len(self.menu_items) - 1, self.state.selected_menu_item + 1)
        elif key == 'enter':
            self.handle_menu_selection()
            
        # Screen-specific keys
        elif self.state.current_screen == TUIScreen.CONFIG:
            self.handle_config_key(key)
        elif self.state.current_screen == TUIScreen.BUILD:
            self.handle_build_key(key)
            
        return True
        
    def handle_menu_selection(self):
        """Handle menu item selection"""
        selected = self.state.selected_menu_item
        
        if selected == 0:  # 开始构建
            self.state.current_screen = TUIScreen.BUILD
            self.start_build()
        elif selected == 1:  # 配置设置
            self.state.current_screen = TUIScreen.CONFIG
        elif selected == 2:  # 性能监控
            self.state.current_screen = TUIScreen.PERFORMANCE
        elif selected == 3:  # 插件管理
            self.state.current_screen = TUIScreen.PLUGINS
        elif selected == 4:  # 查看日志
            self.state.current_screen = TUIScreen.LOGS
        elif selected == 5:  # 清理项目
            self.clean_project()
        elif selected == 6:  # 帮助
            self.state.current_screen = TUIScreen.HELP
        elif selected == 7:  # 退出
            return False
            
    def handle_config_key(self, key: str):
        """Handle configuration screen keys"""
        if key.isdigit():
            config_num = int(key)
            if 1 <= config_num <= 6:
                self.edit_config_item(config_num)
                
    def handle_build_key(self, key: str):
        """Handle build screen keys"""
        if key.lower() == 'p':
            self.toggle_build_pause()
        elif key.lower() == 'q':
            self.abort_build()
            
    def edit_config_item(self, item_num: int):
        """Edit a configuration item"""
        # This would open a dialog to edit the config item
        self.state.status_message = f"编辑配置项 {item_num}"
        
    def start_build(self):
        """Start the build process"""
        self.state.build_running = True
        self.state.status_message = "构建已开始"
        
    def toggle_build_pause(self):
        """Toggle build pause state"""
        self.state.build_paused = not self.state.build_paused
        self.state.status_message = "构建已暂停" if self.state.build_paused else "构建已恢复"
        
    def abort_build(self):
        """Abort the build process"""
        self.state.build_running = False
        self.state.build_paused = False
        self.state.current_screen = TUIScreen.MAIN
        self.state.status_message = "构建已中止"
        
    def clean_project(self):
        """Clean the project"""
        self.state.status_message = "项目清理完成"
        
    def update_layout(self):
        """Update the layout with current content"""
        self.layout["header"].update(self.create_header())
        self.layout["sidebar"].update(self.create_sidebar())
        self.layout["content"].update(self.create_main_content())
        self.layout["footer"].update(self.create_footer())
        
    def run(self) -> bool:
        """Run the TUI application"""
        self.setup_layout()
        
        try:
            with Live(self.layout, console=self.console, refresh_per_second=4) as live:
                self.live = live
                self.state.status_message = "TUI 已启动 - 使用数字键选择菜单，q 退出，h 帮助"
                
                while True:
                    self.update_layout()
                    
                    # Check for keyboard input (non-blocking)
                    try:
                        # Use a simple input method for now
                        # In a production version, you'd use a proper keyboard library
                        import select
                        import sys
                        
                        # Check if input is available (Windows compatible approach)
                        if sys.platform == "win32":
                            import msvcrt
                            if msvcrt.kbhit():
                                key = msvcrt.getch().decode('utf-8', errors='ignore')
                                if self.handle_key_input(key):
                                    break
                        else:
                            # Unix-like systems
                            if select.select([sys.stdin], [], [], 0.1)[0]:
                                key = sys.stdin.read(1)
                                if self.handle_key_input(key):
                                    break
                    except:
                        # Fallback: just sleep and continue
                        pass
                    
                    time.sleep(0.1)  # Small delay to prevent high CPU usage
                    
        except KeyboardInterrupt:
            self.state.status_message = "用户中断"
            return False
            
        return True
    
    def handle_key_input(self, key: str) -> bool:
        """Handle keyboard input, return True to exit"""
        key = key.lower()
        
        if key == 'q':
            self.state.status_message = "正在退出..."
            return True
        elif key == 'h':
            self.state.current_screen = TUIScreen.HELP
            self.state.status_message = "帮助屏幕 - 按 q 退出，其他数字键切换屏幕"
        elif key == '1':
            self.state.current_screen = TUIScreen.MAIN
            self.state.status_message = "主页 - 按数字键切换屏幕"
        elif key == '2':
            self.state.current_screen = TUIScreen.BUILD
            self.state.status_message = "构建屏幕 - 按数字键切换屏幕"
        elif key == '3':
            self.state.current_screen = TUIScreen.CONFIG
            self.state.status_message = "配置屏幕 - 按数字键切换屏幕"
        elif key == '4':
            self.state.current_screen = TUIScreen.LOGS
            self.state.status_message = "日志屏幕 - 按数字键切换屏幕"
        elif key == '5':
            self.state.current_screen = TUIScreen.PERFORMANCE
            self.state.status_message = "性能监控屏幕 - 按数字键切换屏幕"
        elif key == '6':
            self.state.current_screen = TUIScreen.PLUGINS
            self.state.status_message = "插件屏幕 - 按数字键切换屏幕"
        elif key == 'b':
            # Start build
            self.state.current_screen = TUIScreen.BUILD
            self.state.status_message = "开始构建... (演示模式)"
        elif key == 'c':
            # Show config
            self.state.current_screen = TUIScreen.CONFIG
            self.state.status_message = "配置屏幕 - 按数字键编辑配置"
        else:
            self.state.status_message = f"未知按键: {key} - 按 h 查看帮助"
            
        return False


class BuildSystemProtocol(Protocol):
    """Protocol for build system implementations"""

    def get_command(self, args: List[str], config: BuildConfig) -> List[str]: ...

    def get_clean_command(self, args: List[str]) -> List[str]: ...

    def parse_progress(self, line: str) -> Optional[Tuple[int, int, str]]: ...

    def categorize_message(self, line: str) -> MessageType: ...


# === Enhanced Build System Implementations ===
class NinjaBuildSystem:
    """Enhanced Ninja build system implementation"""

    def get_command(self, args: List[str], config: BuildConfig) -> List[str]:
        cmd = ["ninja"] + config.to_ninja_args()
        return cmd + args

    def get_clean_command(self, args: List[str]) -> List[str]:
        return ["ninja", "clean"]

    def parse_progress(self, line: str) -> Optional[Tuple[int, int, str]]:
        match = re.match(r'\[(\d+)/(\d+)\]\s*(.+)', line)
        if match:
            current, total, description = match.groups()
            return int(current), int(total), description.strip()
        return None

    def categorize_message(self, line: str) -> MessageType:
        line_lower = line.lower()
        if 'memory region' in line_lower or re.match(r'\s*(RAM|FLASH):', line):
            return MessageType.MEMORY
        if any(keyword in line_lower for keyword in ['error', 'failed', 'fatal']):
            return MessageType.ERROR
        elif any(keyword in line_lower for keyword in ['warning', 'warn']):
            return MessageType.WARNING
        elif 'ninja: build stopped' in line_lower:
            return MessageType.ERROR
        elif self.parse_progress(line):
            return MessageType.PROGRESS
        return MessageType.INFO


class MakeBuildSystem:
    """Enhanced GNU Make build system implementation"""

    def get_command(self, args: List[str], config: BuildConfig) -> List[str]:
        cmd = ["make"] + config.to_make_args()
        return cmd + args

    def get_clean_command(self, args: List[str]) -> List[str]:
        return ["make", "clean"]

    def parse_progress(self, line: str) -> Optional[Tuple[int, int, str]]:
        match = re.match(r'^\[\s*(\d+)%\]\s*(.+)', line)
        if match:
            percentage, description = match.groups()
            return int(percentage), 100, description.strip()
        return None

    def categorize_message(self, line: str) -> MessageType:
        line_lower = line.lower()
        if 'memory region' in line_lower or re.match(r'\s*(RAM|FLASH):', line):
            return MessageType.MEMORY
        if any(keyword in line_lower for keyword in ['error', 'failed', 'no rule']):
            return MessageType.ERROR
        elif any(keyword in line_lower for keyword in ['warning', 'warn']):
            return MessageType.WARNING
        elif 'make:' in line_lower and ('entering' in line_lower or 'leaving' in line_lower):
            return MessageType.DEBUG
        elif self.parse_progress(line):
            return MessageType.PROGRESS
        return MessageType.INFO


class CMakeBuildSystem:
    """Enhanced CMake build system implementation"""

    def get_command(self, args: List[str], config: BuildConfig) -> List[str]:
        cmd = ["cmake", "--build", "."]
        if config.parallel_jobs > 1:
            cmd.extend(["--parallel", str(config.parallel_jobs)])
        if config.verbose_mode:
            cmd.append("--verbose")
        # Add any extra arguments passed by the user
        if args:
            cmd.extend(['--'] + args)
        return cmd

    def get_clean_command(self, args: List[str]) -> List[str]:
        return ["cmake", "--build", ".", "--target", "clean"]

    def parse_progress(self, line: str) -> Optional[Tuple[int, int, str]]:
        match = re.match(r'^\[\s*(\d+)%\]\s*(.+)', line)
        if match:
            percentage, description = match.groups()
            return int(percentage), 100, description.strip()
        return None

    def categorize_message(self, line: str) -> MessageType:
        line_lower = line.lower()
        if 'memory region' in line_lower or re.match(r'\s*(RAM|FLASH):', line):
            return MessageType.MEMORY
        if any(keyword in line_lower for keyword in ['error', 'failed', 'cmake error']):
            return MessageType.ERROR
        elif any(keyword in line_lower for keyword in ['warning', 'warn']):
            return MessageType.WARNING
        elif 'configuring done' in line_lower or 'generating done' in line_lower:
            return MessageType.SUCCESS
        elif line.startswith('--'):
            return MessageType.INFO
        elif self.parse_progress(line):
            return MessageType.PROGRESS
        return MessageType.INFO


# === Responsive Grid Layout System ===
class ResponsiveGridLayout:
    """Responsive grid layout manager"""

    def __init__(self, console: Console):
        self.console = console
        self.grid_config = GridConfig()
        self._cached_width = 0
        self._cached_breakpoint = "md"

    @property
    def terminal_width(self) -> int:
        """Get current terminal width"""
        return self.console.size.width

    @property
    def terminal_height(self) -> int:
        """Get current terminal height"""
        return self.console.size.height

    @property
    def current_breakpoint(self) -> str:
        """Get current responsive breakpoint"""
        width = self.terminal_width
        if width != self._cached_width:
            self._cached_width = width
            self._cached_breakpoint = self.grid_config.get_breakpoint(width)
        return self._cached_breakpoint

    def create_layout(self) -> Layout:
        """Create responsive layout based on terminal size"""
        layout = Layout(name="root")

        # A more compact layout
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="progress", size=3),
            Layout(name="output", ratio=1, minimum_size=8),
            Layout(name="stats", size=1),
            Layout(name="footer", size=1),
        )
        return layout


# === Interactive Configuration Manager ===
class InteractiveConfigManager:
    """Interactive configuration manager with keyboard controls"""

    def __init__(self, console: Console, config: BuildConfig):
        self.console = console
        self.config = config
        self.key_bindings = {kb.key: kb for kb in DEFAULT_KEY_BINDINGS}

        # Configuration options for interactive editing
        self.config_options = {
            'parallel_jobs': {
                'name': '并行任务数',
                'type': int,
                'min': 1,
                'max': (os.cpu_count() or 4) * 2,
                'description': '并行编译任务的数量'
            },
            'build_type': {
                'name': '构建类型',
                'type': str,
                'choices': ['Debug', 'Release', 'RelWithDebInfo', 'MinSizeRel'],
                'description': 'CMake 构建类型配置'
            },
            'optimization_level': {
                'name': '优化级别',
                'type': str,
                'choices': ['O0', 'O1', 'O2', 'O3', 'Os', 'Oz'],
                'description': '编译器优化级别'
            },
            'verbose_mode': {
                'name': '详细模式',
                'type': bool,
                'description': '启用详细的构建输出'
            },
            'warnings_as_errors': {
                'name': '警告即错误',
                'type': bool,
                'description': '将警告视为编译错误'
            },
            'enable_sanitizers': {
                'name': '启用 Sanitizers',
                'type': bool,
                'description': '启用地址/内存 sanitizers'
            }
        }

    def show_interactive_config(self) -> bool:
        """Show interactive configuration interface using prompts."""
        original_config_dict = self.config.__dict__.copy()

        self.console.clear()
        self.console.print(Panel(
            "[bold cyan]🔧 构建配置[/bold cyan]",
            subtitle="输入选项编号进行编辑, 's' 保存, 'q' 退出。"
        ))

        while True:
            self.console.print(self._create_config_panel())
            self.console.print(self._create_config_preview())

            choice = Prompt.ask("[bold]选择一个选项[/bold]", default="s")

            if choice.lower() == 'q':
                self.console.print("[yellow]配置已取消。恢复原始设置。[/yellow]")
                self.config.__dict__.update(original_config_dict)  # Restore original
                return False
            if choice.lower() == 's':
                self.console.print("[green]配置已保存。[/green]")
                return True

            try:
                option_index = int(choice) - 1
                if not (0 <= option_index < len(self.config_options)):
                    raise ValueError

                key_to_edit = list(self.config_options.keys())[option_index]
                option = self.config_options[key_to_edit]
                current_value = getattr(self.config, key_to_edit)

                if option['type'] == bool:
                    new_value = Confirm.ask(f"启用 {option['name']}?", default=current_value)
                    setattr(self.config, key_to_edit, new_value)
                elif option['type'] == int:
                    new_value = IntPrompt.ask(
                        f"为 {option['name']} 输入新值",
                        default=int(current_value) if current_value is not None else 1
                    )
                    setattr(self.config, key_to_edit, new_value)
                elif 'choices' in option:
                    new_value = Prompt.ask(
                        f"为 {option['name']} 选择",
                        choices=option['choices'],
                        default=str(current_value)
                    )
                    setattr(self.config, key_to_edit, new_value)

                self.console.clear()  # Clear screen for next prompt
                self.console.print(Panel("[bold cyan]🔧 构建配置[/bold cyan]",
                                         subtitle="输入选项编号进行编辑, 's' 保存, 'q' 退出。"))

            except (ValueError, IndexError):
                self.console.print("[red]无效选项，请重试。[/red]")

    def _create_config_panel(self) -> Panel:
        """Create configuration options panel"""
        table = Table(box=box.SIMPLE, show_header=True, header_style="bold cyan")
        table.add_column("#", style="dim", width=3)
        table.add_column("选项", style="yellow", width=20)
        table.add_column("当前值", style="green", width=15)
        table.add_column("描述", style="dim", overflow="fold")

        for i, (key, option) in enumerate(self.config_options.items()):
            current_value = getattr(self.config, key)
            value_str = str(current_value)

            if isinstance(current_value, bool):
                value_str = "✅ 是" if current_value else "❌ 否"

            table.add_row(
                str(i + 1),
                f"[bold]{option['name']}[/bold]",
                value_str,
                option['description']
            )

        return Panel(
            table,
            title="[bold]配置选项[/bold]",
            border_style="cyan"
        )

    def _create_config_preview(self) -> Panel:
        """Create configuration preview panel"""
        preview_text = Text()
        preview_text.append("生成的参数:\n\n", style="bold yellow")

        # CMake args
        cmake_args = self.config.to_cmake_args()
        if cmake_args:
            preview_text.append("CMake: ", style="cyan bold")
            preview_text.append(" ".join(cmake_args), style="white")
            preview_text.append("\n\n")

        # Make args
        make_args = self.config.to_make_args()
        if make_args:
            preview_text.append("Make: ", style="blue bold")
            preview_text.append(" ".join(make_args), style="white")
            preview_text.append("\n\n")

        # Ninja args
        ninja_args = self.config.to_ninja_args()
        if ninja_args:
            preview_text.append("Ninja: ", style="green bold")
            preview_text.append(" ".join(ninja_args), style="white")

        return Panel(
            preview_text,
            title="[bold]预览[/bold]",
            border_style="yellow"
        )

    def show_help_screen(self):
        """Show help screen with key bindings"""
        help_table = Table(title="🔧 键盘控制", box=box.ROUNDED)
        help_table.add_column("按键", style="yellow bold", width=8)
        help_table.add_column("操作", style="cyan", width=20)
        help_table.add_column("描述", style="white")

        for binding in DEFAULT_KEY_BINDINGS:
            help_table.add_row(
                binding.key.upper(),
                binding.action.value.replace('_', ' ').title(),
                binding.description
            )

        help_panel = Panel(
            help_table,
            title="[bold cyan]帮助与控制[/bold cyan]",
            border_style="cyan",
            padding=(1, 2)
        )

        self.console.print(help_panel)
        Prompt.ask("\n[dim]按 Enter 继续...[/dim]", default="")


# === Enhanced Build State Management ===
@dataclass
class BuildMessage:
    """Structured build message with enhanced metadata"""
    content: str
    message_type: MessageType
    timestamp: float
    file_path: Optional[str] = None
    line_number: Optional[int] = None


@dataclass
class MemoryInfo:
    """Stores memory usage information."""
    region: str
    used: str
    total: str
    percent: str


@dataclass
class BuildStats:
    """Enhanced build statistics tracking"""
    files_compiled: int = 0
    targets_built: int = 0
    warnings: int = 0
    errors: int = 0
    start_time: float = field(default_factory=time.time)
    memory_reports: List[MemoryInfo] = field(default_factory=list)

    @property
    def duration(self) -> float:
        return time.time() - self.start_time


@dataclass
class BuildState:
    """Enhanced build state management with real-time updates"""
    current_target: str = "Initializing..."
    current_step: int = 0
    total_steps: int = 0
    messages: List[BuildMessage] = field(default_factory=list, repr=False)
    stats: BuildStats = field(default_factory=BuildStats)
    is_cancelled: bool = False
    is_paused: bool = False
    build_phase: BuildPhase = BuildPhase.INITIALIZATION
    start_time: float = field(default_factory=time.time)

    def add_message(self, content: str, msg_type: MessageType):
        """Add a structured message to the build state"""
        file_path, line_number = self._extract_file_info(content)
        message = BuildMessage(
            content=content,
            message_type=msg_type,
            timestamp=time.time(),
            file_path=file_path,
            line_number=line_number,
        )
        self.messages.append(message)

        # Keep only recent messages
        if len(self.messages) > 500:
            self.messages = self.messages[-250:]

        if msg_type == MessageType.ERROR:
            self.stats.errors += 1
        elif msg_type == MessageType.WARNING:
            self.stats.warnings += 1

    def _extract_file_info(self, content: str) -> Tuple[Optional[str], Optional[int]]:
        """Extract file path and line number from compiler output"""
        match = re.match(r'^([^:]+):(\d+):(?:\d+:)?\s*', content)
        if match:
            file_path, line_number_str = match.groups()
            if os.path.exists(file_path):
                return file_path, int(line_number_str)
        return None, None

    def get_recent_output(self, count: int = 8) -> List[BuildMessage]:
        """Get recent build output messages."""
        # Filter out memory messages from the main output panel
        return [msg for msg in self.messages if msg.message_type != MessageType.MEMORY][-count:]

    def update_phase(self, phase: BuildPhase):
        """Update the current build phase"""
        self.build_phase = phase


# === Enhanced Output Formatter ===
class ResponsiveOutputFormatter:
    """Responsive output formatter with grid-aware layouts"""

    def __init__(self, console: Console):
        self.console = console
        self.layout_manager = ResponsiveGridLayout(console)
        self.progress = self._create_progress_bar()

    def _create_progress_bar(self) -> Progress:
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=None),
            MofNCompleteColumn(),
            TimeElapsedColumn(),
            expand=True
        )

    def create_build_display(self, state: BuildState, config: BuildConfig, build_system: str,
                             args: List[str]) -> Layout:
        """Create the main build display layout."""
        layout = self.layout_manager.create_layout()

        # Header
        header_text = Text.from_markup(
            f"🚀 [bold]{build_system.title()}[/] │ 📂 [dim]{os.path.basename(os.getcwd())}[/] │ 🕐 [dim]{datetime.now():%H:%M:%S}[/] │ ⚙️ [dim]{' '.join(args)}[/]")
        layout["header"].update(header_text)

        # Progress
        self.progress.tasks[0].description = self._format_target(state.current_target)
        self.progress.tasks[0].total = state.total_steps
        self.progress.tasks[0].completed = state.current_step
        layout["progress"].update(self.progress)

        # Output
        layout["output"].update(self._create_output_panel(state))

        # Stats
        stats_text = self._create_stats_line(state)
        layout["stats"].update(stats_text)

        # Footer
        footer_text = Text.from_markup("[dim] P: 暂停 │ Q: 退出 │ C: 配置 │ H: 帮助[/]")
        layout["footer"].update(Align.center(footer_text))

        return layout

    def _format_target(self, target: str, max_len: int = 60) -> str:
        """Truncate and format the target description."""
        # Clean up common build prefixes
        target = re.sub(r'^(Building|Compiling|Linking) (CXX|C) object\s*', '', target)
        target = re.sub(r'\.o$', '', target)

        if len(target) > max_len:
            return target[:max_len - 3] + "..."
        return target

    def _create_output_panel(self, state: BuildState) -> Panel:
        """Create the panel for recent build output."""
        output_text = Text()
        recent_output = state.get_recent_output(count=10)

        for msg in recent_output:
            style = "white"
            icon = "  "
            if msg.message_type == MessageType.ERROR:
                style = "red"
                icon = "❌"
            elif msg.message_type == MessageType.WARNING:
                style = "yellow"
                icon = "⚠️ "

            line_content = Text(f"{icon} ", style=style)
            line_content.append(msg.content)
            output_text.append(line_content)
            output_text.append("\n")

        return Panel(
            output_text,
            title=f"Build Output (最近 {len(recent_output)} 行)",
            title_align="left",
            border_style="dim",
            box=box.MINIMAL
        )

    def _create_stats_line(self, state: BuildState) -> Text:
        """Create the single-line statistics display."""
        stats = state.stats
        progress_pct = (state.current_step / state.total_steps * 100) if state.total_steps > 0 else 0

        parts = [
            f"⏱️ [yellow]{stats.duration:.1f}s[/]",
            f"📁 {stats.files_compiled}",
            f"🎯 {stats.targets_built}",
        ]
        if stats.warnings > 0:
            parts.append(f"⚠️ [yellow]{stats.warnings}[/]")
        if stats.errors > 0:
            parts.append(f"❌ [red]{stats.errors}[/]")

        parts.append(f"📊 {progress_pct:.0f}%")

        return Text(" │ ".join(parts), justify="center")

    def show_final_results(self, state: BuildState, return_code: int):
        """Display the final build summary."""
        stats = state.stats

        # Create the main summary text
        if return_code == 0 and stats.errors == 0:
            title = "[bold green]🎉 构建成功[/bold green]"
            border_style = "green"
            summary_text = f"构建在 [bold]{stats.duration:.2f}s[/] 内成功完成。"
            if stats.warnings > 0:
                summary_text += f"\n带有 [yellow]{stats.warnings}[/] 个警告。"
        else:
            title = "[bold red]💥 构建失败[/bold red]"
            border_style = "red"
            summary_text = f"构建在 [bold]{stats.duration:.2f}s[/] 后失败。"
            if stats.errors > 0:
                summary_text += f"\n发现 [red]{stats.errors}[/] 个错误。"
            if stats.warnings > 0:
                summary_text += f"\n发现 [yellow]{stats.warnings}[/] 个警告。"

        # Create a renderable group for the final panel
        render_group = [Align.center(summary_text)]

        # If memory report is available, add it
        if stats.memory_reports:
            mem_table = Table(title="[bold]内存使用情况[/bold]", box=box.MINIMAL, title_style="", show_header=True,
                              header_style="bold cyan")
            mem_table.add_column("内存区域")
            mem_table.add_column("已用大小", justify="right")
            mem_table.add_column("区域大小", justify="right")
            mem_table.add_column("使用率", justify="right")

            for report in stats.memory_reports:
                mem_table.add_row(report.region, report.used, report.total, report.percent)

            render_group.append(Rule(style="dim"))
            render_group.append(mem_table)

            # Add visualization bars
            vis_items = []
            for report in stats.memory_reports:
                try:
                    percent_float = float(report.percent.strip().replace('%', ''))
                except ValueError:
                    percent_float = 0.0

                # Choose color based on usage
                if percent_float > 85:
                    bar_style = "red"
                elif percent_float > 60:
                    bar_style = "yellow"
                else:
                    bar_style = "green"

                # Create a temporary Progress object to render a single bar
                bar_progress = Progress(BarColumn(bar_width=40, style=bar_style), expand=False)
                task_id = bar_progress.add_task("mem", total=100)
                bar_progress.update(task_id, completed=percent_float)

                vis_table = Table.grid(expand=True)
                vis_table.add_column(width=6)
                vis_table.add_column(ratio=1)
                vis_table.add_column(width=8, justify="right")
                vis_table.add_row(
                    Text(f"{report.region: <5}", style="bold"),
                    bar_progress,
                    Text(f"{percent_float:.2f}%", style=bar_style)
                )
                vis_items.append(vis_table)

            render_group.append(Group(*vis_items))

        self.console.print(Panel(
            Group(*render_group),
            title=title,
            border_style=border_style,
            padding=1
        ))


# === Keyboard Input Handler ===
class KeyboardInputHandler:
    """Handles keyboard input in a non-blocking way."""

    def __init__(self):
        self.input_queue = queue.Queue()
        self.running = False
        self.input_thread = None

    def start(self):
        if self.running: return
        self.running = True
        self.input_thread = threading.Thread(target=self._input_worker, daemon=True)
        self.input_thread.start()

    def stop(self):
        if not self.running: return
        self.running = False
        if self.input_thread:
            self.input_thread.join(timeout=0.5)

    def _input_worker(self):
        """Worker thread for keyboard input. Uses platform-specific methods."""
        if os.name == 'nt':
            import msvcrt
            while self.running:
                if msvcrt.kbhit():
                    try:
                        key = msvcrt.getch().decode('utf-8', errors='ignore')
                        self.input_queue.put(key)
                    except UnicodeDecodeError:
                        pass  # Ignore non-utf8 keys
                time.sleep(0.05)
        else:
            import tty, termios, select
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setcbreak(fd)
                while self.running:
                    if select.select([sys.stdin], [], [], 0.05)[0]:
                        key = sys.stdin.read(1)
                        self.input_queue.put(key)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def get_key(self) -> Optional[str]:
        """Get a pressed key if available."""
        try:
            return self.input_queue.get_nowait()
        except queue.Empty:
            return None


# === Enhanced Build Runner ===
class InteractiveBuildRunner:
    """Enhanced build runner with keyboard interaction support"""

    def __init__(self, console: Console):
        self.console = console
        self.config = BuildConfig()
        
        # Load configuration from file if exists
        config_file = Path.cwd() / ".pretty_build.conf"
        if config_file.exists():
            try:
                self.config = BuildConfig.load_from_file(config_file)
                console.print(f"[green]已加载配置文件: {config_file}[/green]")
            except Exception as e:
                console.print(f"[yellow]配置文件加载失败: {e}[/yellow]")
        
        self.config_manager = InteractiveConfigManager(console, self.config)
        self.formatter = ResponsiveOutputFormatter(console)
        self.keyboard_handler = KeyboardInputHandler()
        self._process: Optional[subprocess.Popen] = None
        
        # Initialize new components
        self.plugin_manager = PluginManager(console)
        self.build_cache = BuildCache(self.config.cache_dir, console) if self.config.enable_cache else None
        self.performance_monitor = PerformanceMonitor(console) if self.config.enable_performance_monitoring else None
        self.notification_manager = NotificationManager(console, self.config)
        
        # Register built-in plugins
        self._register_builtin_plugins()
        
        # Setup logging
        self._setup_logging()

    def _register_builtin_plugins(self):
        """Register built-in plugins"""
        # Example: Register a simple logging plugin
        class LoggingPlugin(BuildPlugin):
            def __init__(self):
                super().__init__("logging", "1.0.0")
                self.log_file = None
            
            def initialize(self, config: BuildConfig, console: Console) -> bool:
                if config.auto_save_logs:
                    log_dir = Path.cwd() / "build_logs"
                    log_dir.mkdir(exist_ok=True)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    self.log_file = log_dir / f"build_{timestamp}.log"
                    return True
                return False
            
            def on_build_start(self, build_state: 'BuildState') -> None:
                if self.log_file:
                    with open(self.log_file, 'w') as f:
                        f.write(f"Build started at {datetime.now()}\n")
            
            def on_build_end(self, build_state: 'BuildState', return_code: int) -> None:
                if self.log_file:
                    with open(self.log_file, 'a') as f:
                        f.write(f"Build ended at {datetime.now()} with code {return_code}\n")
                        f.write(f"Errors: {build_state.stats.errors}, Warnings: {build_state.stats.warnings}\n")
            
            def process_message(self, message: str, msg_type: MessageType) -> Optional[str]:
                if self.log_file:
                    with open(self.log_file, 'a') as f:
                        f.write(f"[{msg_type.value}] {message}\n")
                return None
        
        # Register the logging plugin
        logging_plugin = LoggingPlugin()
        self.plugin_manager.register_plugin(logging_plugin)
        if "logging" not in self.config.enabled_plugins:
            self.config.enabled_plugins.append("logging")

    def _setup_logging(self):
        """Setup logging configuration"""
        log_level = getattr(logging, self.config.log_level.upper(), logging.INFO)
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('pretty_build.log'),
                logging.StreamHandler()
            ]
        )

    def run_build(self, build_system_name: str, args: List[str], is_rebuild: bool = False) -> int:
        """Run the build with interactive features."""
        implementations = {
            'make': MakeBuildSystem(),
            'ninja': NinjaBuildSystem(),
            'cmake': CMakeBuildSystem()
        }
        implementation: Optional[BuildSystemProtocol] = implementations.get(build_system_name)
        if not implementation:
            self.console.print(f"❌ [red]不支持的构建系统: {build_system_name}[/red]")
            return 1

        # Initialize plugins
        self.plugin_manager.initialize_plugins(self.config)

        state = BuildState()
        
        # Notify plugins of build start
        self.plugin_manager.on_build_start(state)
        
        # Start performance monitoring
        if self.performance_monitor:
            self.performance_monitor.start_monitoring()

        cmd = implementation.get_command(args, self.config)

        self.keyboard_handler.start()

        try:
            self._process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                errors='ignore'
            )

            # Start monitoring the build process
            if self.performance_monitor:
                self.performance_monitor.start_monitoring(self._process.pid)

            # Add a single task to the progress bar
            self.formatter.progress.add_task("[green]Building...", total=None)

            return_code = self._monitor_build(implementation, state, build_system_name, args)
            
            # Notify plugins of build end
            self.plugin_manager.on_build_end(state, return_code)
            
            # Send notification
            if return_code == 0:
                self.notification_manager.send_notification(
                    "构建成功", 
                    f"项目构建完成，用时 {state.stats.duration:.1f} 秒",
                    NotificationType.SUCCESS
                )
            else:
                self.notification_manager.send_notification(
                    "构建失败", 
                    f"构建失败，错误数: {state.stats.errors}",
                    NotificationType.ERROR
                )
            
            return return_code

        except FileNotFoundError:
            self.console.print(f"💥 [red]命令未找到: {cmd[0]}。请确保它已安装并在您的 PATH 中。[/red]")
            return 1
        except Exception as e:
            self.console.print(f"💥 [red]启动构建失败: {e}[/red]")
            return 1
        finally:
            # Stop performance monitoring
            if self.performance_monitor:
                self.performance_monitor.stop_monitoring()
            
            # Save cache
            if self.build_cache:
                self.build_cache.save()
            
            # Save configuration
            config_file = Path.cwd() / ".pretty_build.conf"
            try:
                self.config.save_to_file(config_file)
            except Exception as e:
                self.console.print(f"[yellow]配置保存失败: {e}[/yellow]")
            
            self.keyboard_handler.stop()
            if self._process and self._process.poll() is None:
                self._process.kill()
            self._process = None
            
            # Cleanup plugins
            self.plugin_manager.cleanup_plugins()

    def _monitor_build(self, implementation: BuildSystemProtocol, state: BuildState, build_system_name: str,
                       args: List[str]) -> int:
        """Monitor the build process with a live display."""
        with Live(
                self.formatter.create_build_display(state, self.config, build_system_name, args),
                console=self.console,
                refresh_per_second=10,
                transient=True,  # Clear the live display on exit
                screen=True  # Use alternate screen to prevent visual glitches
        ) as live:
            while self._process and self._process.poll() is None:
                self._handle_input(state, live)

                if state.is_paused:
                    time.sleep(0.1)
                    continue

                line = self._process.stdout.readline()
                if line:
                    self._process_line(line.strip(), implementation, state)

                live.update(self.formatter.create_build_display(state, self.config, build_system_name, args))

        return_code = self._process.wait() if self._process else 1
        self.formatter.show_final_results(state, return_code)
        return return_code

    def _handle_input(self, state: BuildState, live: Live):
        """Handle keyboard inputs."""
        key = self.keyboard_handler.get_key()
        if not key:
            return

        key = key.lower()
        if key == 'p':
            state.is_paused = not state.is_paused
            self.formatter.progress.tasks[
                0].description = "[yellow]Paused" if state.is_paused else self.formatter._format_target(
                state.current_target)
        elif key == 'q' or key == '\x03':  # q or Ctrl+C
            live.stop()
            if Confirm.ask("您确定要中止构建吗?", console=self.console):
                if self._process: self._process.terminate()
                state.is_cancelled = True
        elif key == 'c':
            live.stop()
            self.config_manager.show_interactive_config()
            live.start()  # Resume live display
        elif key == 'h':
            live.stop()
            self.config_manager.show_help_screen()
            live.start()
        elif key == 'f':
            live.stop()
            self._show_performance_screen()
            live.start()
        elif key == 'g':
            live.stop()
            self._show_plugins_screen()
            live.start()
        elif key == 'x':
            live.stop()
            self._handle_cache_clear()
            live.start()
        elif key == 'n':
            live.stop()
            self._show_notifications_screen()
            live.start()

    def _show_performance_screen(self):
        """Show performance monitoring screen"""
        if not self.performance_monitor:
            self.console.print("[yellow]性能监控未启用[/yellow]")
            Prompt.ask("\n[dim]按 Enter 继续...[/dim]", default="")
            return
        
        report = self.performance_monitor.get_performance_report()
        metrics = self.performance_monitor.get_metrics()
        
        perf_table = Table(title="🚀 性能监控", box=box.ROUNDED)
        perf_table.add_column("指标", style="cyan", width=20)
        perf_table.add_column("当前值", style="yellow", width=15)
        perf_table.add_column("描述", style="white")
        
        perf_table.add_row("CPU 使用率", f"{metrics.cpu_usage:.1f}%", "当前 CPU 使用率")
        perf_table.add_row("内存使用", f"{metrics.memory_usage_mb:.1f} MB", "当前内存使用量")
        perf_table.add_row("峰值内存", f"{metrics.peak_memory_mb:.1f} MB", "构建过程中的峰值内存")
        perf_table.add_row("构建时间", f"{metrics.build_time_seconds:.1f} 秒", "已用构建时间")
        perf_table.add_row("平均 CPU", f"{metrics.average_cpu:.1f}%", "平均 CPU 使用率")
        
        self.console.print(Panel(perf_table, border_style="green"))
        self.console.print(Panel(report, title="详细报告", border_style="blue"))
        Prompt.ask("\n[dim]按 Enter 继续...[/dim]", default="")

    def _show_plugins_screen(self):
        """Show plugins management screen"""
        plugins_table = Table(title="🔌 插件管理", box=box.ROUNDED)
        plugins_table.add_column("插件名称", style="cyan", width=20)
        plugins_table.add_column("版本", style="yellow", width=10)
        plugins_table.add_column("状态", style="green", width=10)
        plugins_table.add_column("描述", style="white")
        
        for name, plugin in self.plugin_manager.plugins.items():
            status = "✅ 启用" if plugin.enabled else "❌ 禁用"
            plugins_table.add_row(plugin.name, plugin.version, status, f"插件: {name}")
        
        self.console.print(Panel(plugins_table, border_style="magenta"))
        Prompt.ask("\n[dim]按 Enter 继续...[/dim]", default="")

    def _handle_cache_clear(self):
        """Handle cache clearing"""
        if not self.build_cache:
            self.console.print("[yellow]缓存未启用[/yellow]")
            Prompt.ask("\n[dim]按 Enter 继续...[/dim]", default="")
            return
        
        stats = self.build_cache.get_cache_stats()
        self.console.print(f"[cyan]缓存统计:[/cyan]")
        self.console.print(f"  文件数: {stats['total_files']}")
        self.console.print(f"  缓存大小: {stats['cache_size_mb']:.2f} MB")
        self.console.print(f"  缓存目录: {stats['cache_dir']}")
        
        if Confirm.ask("确定要清理缓存吗?", default=False):
            self.build_cache.clear_cache()

    def _show_notifications_screen(self):
        """Show notifications settings screen"""
        notif_table = Table(title="🔔 通知设置", box=box.ROUNDED)
        notif_table.add_column("设置", style="cyan", width=20)
        notif_table.add_column("当前值", style="yellow", width=15)
        notif_table.add_column("描述", style="white")
        
        notif_table.add_row("通知启用", "✅ 是" if self.config.enable_notifications else "❌ 否", "是否启用系统通知")
        notif_table.add_row("通知声音", "✅ 是" if self.config.notification_sound else "❌ 否", "是否播放通知声音")
        
        self.console.print(Panel(notif_table, border_style="yellow"))
        
        if Confirm.ask("要修改通知设置吗?", default=False):
            self.config.enable_notifications = Confirm.ask("启用通知?", default=self.config.enable_notifications)
            self.config.notification_sound = Confirm.ask("启用通知声音?", default=self.config.notification_sound)
            self.notification_manager.notifications_enabled = self.config.enable_notifications

    def _process_line(self, line: str, implementation: BuildSystemProtocol, state: BuildState):
        """Process a single line of build output."""
        if not line:
            return

        msg_type = implementation.categorize_message(line)
        
        # Process through plugins
        processed_line = self.plugin_manager.process_message(line, msg_type)
        
        state.add_message(processed_line, msg_type)

        if msg_type == MessageType.PROGRESS:
            progress_info = implementation.parse_progress(processed_line)
            if progress_info:
                current, total, description = progress_info
                state.current_step = current
                state.total_steps = total
                state.current_target = description
                state.stats.files_compiled = current  # Approximation
                if current == total:
                    state.stats.targets_built += 1
        elif msg_type == MessageType.INFO and 'built target' in processed_line.lower():
            state.stats.targets_built += 1
        elif msg_type == MessageType.MEMORY:
            # Regex to capture the memory line, e.g., "   RAM:   2392 B      20 KB      11.68%"
            match = re.match(r'\s*(RAM|FLASH):\s*(\d+\s*B)\s*(\d+\s*KB)\s*([\d.]+\s*%)', processed_line)
            if match:
                region, used, total, percent = match.groups()
                mem_info = MemoryInfo(
                    region=region.strip(),
                    used=used.strip(),
                    total=total.strip(),
                    percent=percent.strip()
                )
                state.stats.memory_reports.append(mem_info)


# === Build System Detector ===
class BuildSystemDetector:
    """Intelligent build system detection."""

    @staticmethod
    def detect_from_files(directory: Optional[Path] = None) -> Optional[str]:
        """Detect build system from project files."""
        if directory is None:
            directory = Path.cwd()

        detection_files = [
            ('build.ninja', 'ninja'),
            ('Makefile', 'make'),
            ('makefile', 'make'),
            ('CMakeLists.txt', 'cmake'),
        ]

        for filename, system in detection_files:
            if (directory / filename).exists():
                return system

        return None

    @classmethod
    def detect(cls) -> Optional[str]:
        """Detect build system, preferring files, then availability."""
        from_files = cls.detect_from_files()
        if from_files:
            return from_files

        available = [sys for sys in ['ninja', 'make', 'cmake'] if shutil.which(sys)]
        if available:
            return available[0]  # Default to first available

        return None


def main():
    """Enhanced main function with interactive features"""
    parser = argparse.ArgumentParser(
        prog='pb',
        description='🚀 Pretty Build - 交互式通用构建封装工具',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
示例:
  %(prog)s                  # 自动检测并以交互模式构建
  %(prog)s --tui             # 启动 TUI 界面
  %(prog)s ninja -j8        # 使用 8 个任务运行 ninja
  %(prog)s --config         # 在构建前进行配置
  %(prog)s --rebuild         # 清理并重新构建
  %(prog)s --clean           # 仅清理项目
  %(prog)s -- CXX=clang++   # 将参数传递给构建系统 (make/cmake)
"""
    )

    parser.add_argument('--clean', action='store_true', help='清理构建文件')
    parser.add_argument('--rebuild', action='store_true', help='清理并重新构建')
    parser.add_argument('--config', action='store_true', help='在开始前配置构建参数')
    parser.add_argument('--tui', action='store_true', help='启动 TUI (文本用户界面) 模式')
    parser.add_argument('-C', '--directory', metavar='DIR', help='在构建前切换到目录')
    parser.add_argument('-j', '--jobs', type=int, metavar='N', help='并行任务数')
    parser.add_argument('build_args', nargs=argparse.REMAINDER, help='传递给构建系统的参数')

    args = parser.parse_args()

    console = Console(stderr=True)

    if args.directory:
        try:
            os.chdir(args.directory)
            console.print(f"📂 [cyan]已切换到: {os.getcwd()}[/cyan]")
        except Exception as e:
            console.print(f"❌ [red]目录错误: {e}[/red]")
            return 1

    runner = InteractiveBuildRunner(console)

    # TUI mode
    if args.tui:
        try:
            # 导入 Textual TUI
            from textual_tui import run_textual_tui
            console.print("🚀 [cyan]启动 Textual TUI 模式...[/cyan]")
            time.sleep(1)  # Brief pause to show the message
            run_textual_tui(config=runner.config)
            return 0
        except ImportError:
            console.print("❌ [red]Textual 库未安装。请运行: pip install textual[/red]")
            return 1
        except Exception as e:
            console.print(f"❌ [red]TUI 模式启动失败: {e}[/red]")
            console.print_exception()
            return 1

    if args.config:
        if not runner.config_manager.show_interactive_config():
            console.print("配置已取消。")
            return 1

    if args.jobs:
        runner.config.parallel_jobs = args.jobs

    # Detect build system
    build_system_name = BuildSystemDetector.detect()
    if not build_system_name:
        console.print("❌ [red]未找到支持的构建系统 (Makefile, build.ninja, CMakeLists.txt)。[/red]")
        return 1
    console.print(f"🔍 [cyan]检测到的构建系统: {build_system_name}[/cyan]")

    # Handle build arguments (e.g., --)
    build_args = []
    if args.build_args:
        if args.build_args[0] == '--':
            build_args = args.build_args[1:]
        else:
            build_args = args.build_args

    # Get build system implementation for clean commands
    implementations = {'ninja': NinjaBuildSystem(), 'make': MakeBuildSystem(), 'cmake': CMakeBuildSystem()}
    implementation = implementations.get(build_system_name)

    try:
        if args.rebuild or args.clean:
            console.print(f"🧹 [yellow]正在清理项目...[/yellow]")
            clean_cmd = implementation.get_clean_command(build_args)
            result = subprocess.run(clean_cmd, capture_output=True, text=True)
            if result.returncode == 0:
                console.print("✅ [green]清理成功。[/green]")
            else:
                console.print(f"❌ [red]清理失败。[/red]")
                console.print(Panel(result.stdout, title="清理输出", border_style="red"))
                if not args.rebuild:  # If only cleaning, exit on failure
                    return result.returncode

        if args.clean:  # If only cleaning, we are done
            return 0

        # Run the build
        return runner.run_build(build_system_name, build_args, is_rebuild=args.rebuild)

    except Exception:
        console.print_exception(show_locals=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
