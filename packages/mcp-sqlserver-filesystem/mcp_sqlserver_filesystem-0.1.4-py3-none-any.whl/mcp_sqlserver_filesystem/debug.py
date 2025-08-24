"""
调试工具模块
============

提供统一的调试日志功能，支持条件输出和多级别日志。
"""

import os
import sys
from datetime import datetime
from typing import Any


def is_debug_enabled() -> bool:
    """检查是否启用调试模式"""
    return os.getenv("MCP_DEBUG", "").lower() in ("true", "1", "yes", "on")


def debug_log(message: str, level: str = "INFO") -> None:
    """
    输出调试日志
    
    Args:
        message: 日志消息
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
    """
    if not is_debug_enabled():
        return
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    formatted_message = f"[{timestamp}] [{level}] {message}"
    
    # 输出到 stderr 以避免干扰 MCP 协议通信
    print(formatted_message, file=sys.stderr, flush=True)


def server_debug_log(message: str) -> None:
    """服务器调试日志"""
    debug_log(f"[SERVER] {message}")


def web_debug_log(message: str) -> None:
    """Web UI 调试日志"""
    debug_log(f"[WEB] {message}")


def db_debug_log(message: str) -> None:
    """数据库调试日志"""
    debug_log(f"[DB] {message}")


def fs_debug_log(message: str) -> None:
    """文件系统调试日志"""
    debug_log(f"[FS] {message}")


def ui_debug_log(message: str) -> None:
    """UI 交互调试日志"""
    debug_log(f"[UI] {message}")


def error_log(message: str, exception: Exception = None) -> None:
    """错误日志"""
    if exception:
        debug_log(f"[ERROR] {message}: {exception}", "ERROR")
    else:
        debug_log(f"[ERROR] {message}", "ERROR")


def warning_log(message: str) -> None:
    """警告日志"""
    debug_log(f"[WARNING] {message}", "WARNING")


def format_dict_for_log(data: dict, max_length: int = 200) -> str:
    """
    格式化字典用于日志输出
    
    Args:
        data: 要格式化的字典
        max_length: 最大长度，超过会截断
        
    Returns:
        格式化后的字符串
    """
    try:
        import json
        formatted = json.dumps(data, ensure_ascii=False, indent=None)
        if len(formatted) > max_length:
            formatted = formatted[:max_length] + "..."
        return formatted
    except Exception:
        return str(data)[:max_length]


def log_function_call(func_name: str, args: dict = None, result: Any = None) -> None:
    """
    记录函数调用日志
    
    Args:
        func_name: 函数名
        args: 参数字典
        result: 返回结果
    """
    if not is_debug_enabled():
        return
    
    message = f"CALL {func_name}"
    
    if args:
        args_str = format_dict_for_log(args, 100)
        message += f" with args: {args_str}"
    
    if result is not None:
        if isinstance(result, (dict, list)):
            result_str = format_dict_for_log(result if isinstance(result, dict) else {"result": result}, 100)
        else:
            result_str = str(result)[:100]
        message += f" -> {result_str}"
    
    debug_log(message)


class DebugContext:
    """调试上下文管理器"""
    
    def __init__(self, operation: str, **kwargs):
        self.operation = operation
        self.kwargs = kwargs
        self.start_time = None
    
    def __enter__(self):
        if is_debug_enabled():
            import time
            self.start_time = time.time()
            
            context_info = ""
            if self.kwargs:
                context_info = f" ({format_dict_for_log(self.kwargs, 100)})"
            
            debug_log(f"START {self.operation}{context_info}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if is_debug_enabled() and self.start_time:
            import time
            duration = time.time() - self.start_time
            
            if exc_type:
                debug_log(f"FAILED {self.operation} after {duration:.3f}s: {exc_val}", "ERROR")
            else:
                debug_log(f"COMPLETED {self.operation} in {duration:.3f}s")


# 便捷的调试装饰器
def debug_trace(func):
    """
    调试跟踪装饰器
    
    用法:
    @debug_trace
    def my_function(arg1, arg2):
        return result
    """
    def wrapper(*args, **kwargs):
        if is_debug_enabled():
            func_name = f"{func.__module__}.{func.__name__}"
            
            # 记录参数（避免敏感信息）
            safe_args = {}
            if args:
                safe_args["args"] = [str(arg)[:50] for arg in args]
            if kwargs:
                safe_args["kwargs"] = {k: str(v)[:50] for k, v in kwargs.items()}
            
            try:
                result = func(*args, **kwargs)
                log_function_call(func_name, safe_args, result)
                return result
            except Exception as e:
                error_log(f"Function {func_name} failed", e)
                raise
        else:
            return func(*args, **kwargs)
    
    return wrapper
