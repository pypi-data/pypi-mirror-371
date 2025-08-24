"""
资源管理器
==========

提供临时文件管理、资源清理和内存管理功能。
"""

import os
import tempfile
import threading
import time
import weakref
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from contextlib import contextmanager

from ..debug import debug_log, warning_log, error_log


class ResourceManager:
    """资源管理器，负责管理临时文件和资源清理"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        self._temp_files: Set[Path] = set()
        self._temp_dirs: Set[Path] = set()
        self._cleanup_callbacks: List[callable] = []
        self._lock = threading.RLock()
        
        # 注册程序退出时的清理
        import atexit
        atexit.register(self.cleanup_all)
        
        debug_log("ResourceManager initialized")
    
    def create_temp_file(self, suffix: str = "", prefix: str = "mcp_", content: str = None) -> Path:
        """
        创建临时文件
        
        Args:
            suffix: 文件后缀
            prefix: 文件前缀
            content: 初始内容
            
        Returns:
            临时文件路径
        """
        with self._lock:
            try:
                # 创建临时文件
                fd, temp_path = tempfile.mkstemp(suffix=suffix, prefix=prefix)
                temp_file = Path(temp_path)
                
                # 写入初始内容
                if content is not None:
                    with os.fdopen(fd, 'w', encoding='utf-8') as f:
                        f.write(content)
                else:
                    os.close(fd)
                
                # 记录临时文件
                self._temp_files.add(temp_file)
                debug_log(f"Created temp file: {temp_file}")
                
                return temp_file
                
            except Exception as e:
                error_log(f"Failed to create temp file", e)
                raise
    
    def create_temp_dir(self, suffix: str = "", prefix: str = "mcp_") -> Path:
        """
        创建临时目录
        
        Args:
            suffix: 目录后缀
            prefix: 目录前缀
            
        Returns:
            临时目录路径
        """
        with self._lock:
            try:
                temp_dir = Path(tempfile.mkdtemp(suffix=suffix, prefix=prefix))
                self._temp_dirs.add(temp_dir)
                debug_log(f"Created temp directory: {temp_dir}")
                return temp_dir
                
            except Exception as e:
                error_log(f"Failed to create temp directory", e)
                raise
    
    def register_cleanup_callback(self, callback: callable) -> None:
        """注册清理回调函数"""
        with self._lock:
            self._cleanup_callbacks.append(callback)
            debug_log(f"Registered cleanup callback: {callback.__name__}")
    
    def cleanup_temp_file(self, file_path: Path) -> bool:
        """
        清理指定的临时文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否成功清理
        """
        with self._lock:
            try:
                if file_path in self._temp_files:
                    if file_path.exists():
                        file_path.unlink()
                    self._temp_files.remove(file_path)
                    debug_log(f"Cleaned up temp file: {file_path}")
                    return True
                return False
                
            except Exception as e:
                error_log(f"Failed to cleanup temp file {file_path}", e)
                return False
    
    def cleanup_temp_dir(self, dir_path: Path) -> bool:
        """
        清理指定的临时目录
        
        Args:
            dir_path: 目录路径
            
        Returns:
            是否成功清理
        """
        with self._lock:
            try:
                if dir_path in self._temp_dirs:
                    if dir_path.exists():
                        import shutil
                        shutil.rmtree(dir_path)
                    self._temp_dirs.remove(dir_path)
                    debug_log(f"Cleaned up temp directory: {dir_path}")
                    return True
                return False
                
            except Exception as e:
                error_log(f"Failed to cleanup temp directory {dir_path}", e)
                return False
    
    def cleanup_all(self) -> None:
        """清理所有资源"""
        with self._lock:
            debug_log("Starting resource cleanup...")
            
            # 执行清理回调
            for callback in self._cleanup_callbacks:
                try:
                    callback()
                    debug_log(f"Executed cleanup callback: {callback.__name__}")
                except Exception as e:
                    error_log(f"Cleanup callback failed: {callback.__name__}", e)
            
            # 清理临时文件
            for temp_file in list(self._temp_files):
                self.cleanup_temp_file(temp_file)
            
            # 清理临时目录
            for temp_dir in list(self._temp_dirs):
                self.cleanup_temp_dir(temp_dir)
            
            debug_log("Resource cleanup completed")
    
    def get_resource_stats(self) -> Dict[str, Any]:
        """获取资源统计信息"""
        with self._lock:
            return {
                "temp_files_count": len(self._temp_files),
                "temp_dirs_count": len(self._temp_dirs),
                "cleanup_callbacks_count": len(self._cleanup_callbacks),
                "temp_files": [str(f) for f in self._temp_files],
                "temp_dirs": [str(d) for d in self._temp_dirs],
            }
    
    @contextmanager
    def temp_file_context(self, suffix: str = "", prefix: str = "mcp_", content: str = None):
        """
        临时文件上下文管理器
        
        用法:
        with resource_manager.temp_file_context(".txt", content="test") as temp_file:
            # 使用临时文件
            pass
        # 文件会自动清理
        """
        temp_file = self.create_temp_file(suffix, prefix, content)
        try:
            yield temp_file
        finally:
            self.cleanup_temp_file(temp_file)
    
    @contextmanager
    def temp_dir_context(self, suffix: str = "", prefix: str = "mcp_"):
        """
        临时目录上下文管理器
        
        用法:
        with resource_manager.temp_dir_context() as temp_dir:
            # 使用临时目录
            pass
        # 目录会自动清理
        """
        temp_dir = self.create_temp_dir(suffix, prefix)
        try:
            yield temp_dir
        finally:
            self.cleanup_temp_dir(temp_dir)


# 全局资源管理器实例
_resource_manager = None
_resource_manager_lock = threading.Lock()


def get_resource_manager() -> ResourceManager:
    """获取全局资源管理器实例"""
    global _resource_manager
    if _resource_manager is None:
        with _resource_manager_lock:
            if _resource_manager is None:
                _resource_manager = ResourceManager()
    return _resource_manager


def create_temp_file(suffix: str = "", prefix: str = "mcp_", content: str = None) -> Path:
    """便捷函数：创建临时文件"""
    return get_resource_manager().create_temp_file(suffix, prefix, content)


def create_temp_dir(suffix: str = "", prefix: str = "mcp_") -> Path:
    """便捷函数：创建临时目录"""
    return get_resource_manager().create_temp_dir(suffix, prefix)


def cleanup_all_resources():
    """便捷函数：清理所有资源"""
    get_resource_manager().cleanup_all()


# 弱引用清理器
class WeakResourceCleaner:
    """使用弱引用自动清理资源"""
    
    def __init__(self):
        self._refs: Dict[int, callable] = {}
        self._lock = threading.Lock()
    
    def register(self, obj: Any, cleanup_func: callable) -> None:
        """注册对象和其清理函数"""
        with self._lock:
            ref = weakref.ref(obj, self._cleanup_callback)
            self._refs[id(ref)] = cleanup_func
    
    def _cleanup_callback(self, ref: weakref.ref) -> None:
        """弱引用回调，对象被垃圾回收时调用"""
        with self._lock:
            cleanup_func = self._refs.pop(id(ref), None)
            if cleanup_func:
                try:
                    cleanup_func()
                except Exception as e:
                    error_log("Weak reference cleanup failed", e)


# 全局弱引用清理器
_weak_cleaner = WeakResourceCleaner()
