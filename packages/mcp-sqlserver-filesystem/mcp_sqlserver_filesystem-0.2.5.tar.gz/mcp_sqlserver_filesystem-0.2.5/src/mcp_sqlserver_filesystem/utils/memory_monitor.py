"""
内存监控模块
============

提供内存使用监控、内存泄漏检测和自动清理功能。
"""

import gc
import os
import psutil
import threading
import time
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime, timedelta

from ..debug import debug_log, warning_log, error_log


class MemoryMonitor:
    """内存监控器"""
    
    def __init__(self, check_interval: int = 60, memory_threshold: float = 0.8):
        """
        初始化内存监控器
        
        Args:
            check_interval: 检查间隔（秒）
            memory_threshold: 内存使用阈值（0.0-1.0）
        """
        self.check_interval = check_interval
        self.memory_threshold = memory_threshold
        self.is_monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._callbacks: List[Callable[[Dict[str, Any]], None]] = []
        self._memory_history: List[Dict[str, Any]] = []
        self._max_history = 100
        
        # 获取进程对象
        self._process = psutil.Process(os.getpid())
        
        debug_log(f"MemoryMonitor initialized with interval={check_interval}s, threshold={memory_threshold}")
    
    def add_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """添加内存状态变化回调"""
        self._callbacks.append(callback)
        debug_log(f"Added memory monitor callback: {callback.__name__}")
    
    def start_monitoring(self) -> None:
        """开始内存监控"""
        if self.is_monitoring:
            warning_log("Memory monitoring is already running")
            return
        
        self.is_monitoring = True
        self._stop_event.clear()
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        
        debug_log("Memory monitoring started")
    
    def stop_monitoring(self) -> None:
        """停止内存监控"""
        if not self.is_monitoring:
            return
        
        self.is_monitoring = False
        self._stop_event.set()
        
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=5)
        
        debug_log("Memory monitoring stopped")
    
    def get_memory_info(self) -> Dict[str, Any]:
        """获取当前内存信息"""
        try:
            # 进程内存信息
            process_memory = self._process.memory_info()
            process_percent = self._process.memory_percent()
            
            # 系统内存信息
            system_memory = psutil.virtual_memory()
            
            # Python 垃圾回收信息
            gc_stats = gc.get_stats()
            
            memory_info = {
                "timestamp": datetime.now().isoformat(),
                "process": {
                    "rss": process_memory.rss,  # 物理内存
                    "vms": process_memory.vms,  # 虚拟内存
                    "percent": process_percent,  # 内存使用百分比
                    "rss_mb": process_memory.rss / 1024 / 1024,
                    "vms_mb": process_memory.vms / 1024 / 1024,
                },
                "system": {
                    "total": system_memory.total,
                    "available": system_memory.available,
                    "percent": system_memory.percent,
                    "used": system_memory.used,
                    "free": system_memory.free,
                    "total_gb": system_memory.total / 1024 / 1024 / 1024,
                    "available_gb": system_memory.available / 1024 / 1024 / 1024,
                },
                "gc": {
                    "collections": sum(stat["collections"] for stat in gc_stats),
                    "collected": sum(stat["collected"] for stat in gc_stats),
                    "uncollectable": sum(stat["uncollectable"] for stat in gc_stats),
                }
            }
            
            return memory_info
            
        except Exception as e:
            error_log("Failed to get memory info", e)
            return {}
    
    def _monitor_loop(self) -> None:
        """内存监控循环"""
        while not self._stop_event.wait(self.check_interval):
            try:
                memory_info = self.get_memory_info()
                if not memory_info:
                    continue
                
                # 添加到历史记录
                self._memory_history.append(memory_info)
                if len(self._memory_history) > self._max_history:
                    self._memory_history.pop(0)
                
                # 检查内存使用情况
                process_percent = memory_info["process"]["percent"] / 100.0
                system_percent = memory_info["system"]["percent"] / 100.0
                
                # 触发回调
                for callback in self._callbacks:
                    try:
                        callback(memory_info)
                    except Exception as e:
                        error_log(f"Memory monitor callback failed: {callback.__name__}", e)
                
                # 检查是否超过阈值
                if process_percent > self.memory_threshold or system_percent > self.memory_threshold:
                    warning_log(f"High memory usage detected - Process: {process_percent:.1%}, System: {system_percent:.1%}")
                    self._handle_high_memory_usage(memory_info)
                
                # 定期垃圾回收
                if len(self._memory_history) % 10 == 0:
                    collected = gc.collect()
                    if collected > 0:
                        debug_log(f"Garbage collection freed {collected} objects")
                
            except Exception as e:
                error_log("Memory monitoring loop error", e)
    
    def _handle_high_memory_usage(self, memory_info: Dict[str, Any]) -> None:
        """处理高内存使用情况"""
        try:
            # 强制垃圾回收
            collected = gc.collect()
            debug_log(f"High memory usage - forced GC collected {collected} objects")
            
            # 可以在这里添加更多的内存清理逻辑
            # 例如清理缓存、关闭不必要的连接等
            
        except Exception as e:
            error_log("Failed to handle high memory usage", e)
    
    def get_memory_history(self, minutes: int = 60) -> List[Dict[str, Any]]:
        """获取指定时间范围内的内存历史"""
        if not self._memory_history:
            return []
        
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        
        filtered_history = []
        for record in self._memory_history:
            try:
                record_time = datetime.fromisoformat(record["timestamp"])
                if record_time >= cutoff_time:
                    filtered_history.append(record)
            except (ValueError, KeyError):
                continue
        
        return filtered_history
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """获取内存统计信息"""
        if not self._memory_history:
            return {}
        
        try:
            recent_records = self.get_memory_history(60)  # 最近1小时
            
            if not recent_records:
                return {}
            
            process_percents = [r["process"]["percent"] for r in recent_records]
            process_rss_mb = [r["process"]["rss_mb"] for r in recent_records]
            system_percents = [r["system"]["percent"] for r in recent_records]
            
            stats = {
                "monitoring_duration_minutes": len(self._memory_history) * self.check_interval / 60,
                "total_records": len(self._memory_history),
                "recent_records": len(recent_records),
                "process": {
                    "current_percent": process_percents[-1] if process_percents else 0,
                    "avg_percent": sum(process_percents) / len(process_percents) if process_percents else 0,
                    "max_percent": max(process_percents) if process_percents else 0,
                    "min_percent": min(process_percents) if process_percents else 0,
                    "current_rss_mb": process_rss_mb[-1] if process_rss_mb else 0,
                    "avg_rss_mb": sum(process_rss_mb) / len(process_rss_mb) if process_rss_mb else 0,
                    "max_rss_mb": max(process_rss_mb) if process_rss_mb else 0,
                },
                "system": {
                    "current_percent": system_percents[-1] if system_percents else 0,
                    "avg_percent": sum(system_percents) / len(system_percents) if system_percents else 0,
                    "max_percent": max(system_percents) if system_percents else 0,
                    "min_percent": min(system_percents) if system_percents else 0,
                }
            }
            
            return stats
            
        except Exception as e:
            error_log("Failed to calculate memory stats", e)
            return {}
    
    def force_cleanup(self) -> Dict[str, Any]:
        """强制内存清理"""
        try:
            debug_log("Starting forced memory cleanup...")
            
            # 垃圾回收前的内存信息
            before_memory = self.get_memory_info()
            
            # 执行垃圾回收
            collected_objects = gc.collect()
            
            # 垃圾回收后的内存信息
            after_memory = self.get_memory_info()
            
            # 计算清理效果
            rss_freed = before_memory.get("process", {}).get("rss", 0) - after_memory.get("process", {}).get("rss", 0)
            
            cleanup_result = {
                "collected_objects": collected_objects,
                "rss_freed_bytes": rss_freed,
                "rss_freed_mb": rss_freed / 1024 / 1024,
                "before_memory": before_memory,
                "after_memory": after_memory,
            }
            
            debug_log(f"Memory cleanup completed - freed {rss_freed / 1024 / 1024:.2f} MB, collected {collected_objects} objects")
            
            return cleanup_result
            
        except Exception as e:
            error_log("Failed to perform memory cleanup", e)
            return {}


# 全局内存监控器实例
_memory_monitor: Optional[MemoryMonitor] = None
_monitor_lock = threading.Lock()


def get_memory_monitor() -> MemoryMonitor:
    """获取全局内存监控器实例"""
    global _memory_monitor
    if _memory_monitor is None:
        with _monitor_lock:
            if _memory_monitor is None:
                _memory_monitor = MemoryMonitor()
    return _memory_monitor


def start_memory_monitoring(check_interval: int = 60, memory_threshold: float = 0.8) -> None:
    """启动内存监控"""
    monitor = get_memory_monitor()
    monitor.check_interval = check_interval
    monitor.memory_threshold = memory_threshold
    monitor.start_monitoring()


def stop_memory_monitoring() -> None:
    """停止内存监控"""
    if _memory_monitor:
        _memory_monitor.stop_monitoring()


def get_current_memory_info() -> Dict[str, Any]:
    """获取当前内存信息"""
    return get_memory_monitor().get_memory_info()


def force_memory_cleanup() -> Dict[str, Any]:
    """强制内存清理"""
    return get_memory_monitor().force_cleanup()
