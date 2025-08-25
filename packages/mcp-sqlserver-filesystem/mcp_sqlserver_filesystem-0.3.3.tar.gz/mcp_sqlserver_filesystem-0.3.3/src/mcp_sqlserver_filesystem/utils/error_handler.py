"""
错误处理框架
============

提供统一的错误处理、日志记录和用户友好的错误消息。
"""

import traceback
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from ..debug import error_log, warning_log


class ErrorType(Enum):
    """错误类型枚举"""
    SYSTEM = "system"
    NETWORK = "network"
    DATABASE = "database"
    FILESYSTEM = "filesystem"
    VALIDATION = "validation"
    AUTHENTICATION = "authentication"
    PERMISSION = "permission"
    DEPENDENCY = "dependency"
    CONFIGURATION = "configuration"
    FILE_IO = "file_io"
    UI = "ui"


class ErrorHandler:
    """统一错误处理器"""
    
    _error_log: Dict[str, Dict[str, Any]] = {}
    
    @classmethod
    def log_error_with_context(
        cls,
        error: Exception,
        context: Dict[str, Any] = None,
        error_type: ErrorType = ErrorType.SYSTEM,
        user_message: str = None
    ) -> str:
        """
        记录错误并返回错误ID
        
        Args:
            error: 异常对象
            context: 错误上下文信息
            error_type: 错误类型
            user_message: 用户友好的错误消息
            
        Returns:
            错误ID，用于跟踪和查询
        """
        error_id = str(uuid.uuid4())[:8]
        
        error_info = {
            "id": error_id,
            "type": error_type.value,
            "exception": str(error),
            "exception_type": type(error).__name__,
            "context": context or {},
            "user_message": user_message,
            "timestamp": datetime.now().isoformat(),
            "traceback": traceback.format_exc(),
        }
        
        cls._error_log[error_id] = error_info
        
        # 记录到调试日志
        context_str = f" (Context: {context})" if context else ""
        error_log(f"[{error_id}] {error_type.value.upper()} ERROR: {error}{context_str}", error)
        
        return error_id
    
    @classmethod
    def get_error_info(cls, error_id: str) -> Optional[Dict[str, Any]]:
        """获取错误信息"""
        return cls._error_log.get(error_id)
    
    @classmethod
    def format_user_error(
        cls,
        error: Exception,
        error_type: ErrorType = ErrorType.SYSTEM,
        include_technical: bool = False
    ) -> str:
        """
        格式化用户友好的错误消息
        
        Args:
            error: 异常对象
            error_type: 错误类型
            include_technical: 是否包含技术细节
            
        Returns:
            格式化的错误消息
        """
        user_messages = {
            ErrorType.DATABASE: "数据库操作失败，请检查连接设置和查询语法。",
            ErrorType.FILESYSTEM: "文件系统操作失败，请检查文件路径和权限。",
            ErrorType.NETWORK: "网络连接失败，请检查网络设置。",
            ErrorType.VALIDATION: "输入数据验证失败，请检查参数格式。",
            ErrorType.AUTHENTICATION: "身份验证失败，请检查凭据。",
            ErrorType.PERMISSION: "权限不足，无法执行此操作。",
            ErrorType.DEPENDENCY: "依赖组件不可用，请检查安装。",
            ErrorType.CONFIGURATION: "配置错误，请检查设置。",
            ErrorType.FILE_IO: "文件读写失败，请检查文件路径和权限。",
            ErrorType.UI: "用户界面操作失败，请重试。",
            ErrorType.SYSTEM: "系统错误，请联系管理员。",
        }
        
        base_message = user_messages.get(error_type, "操作失败，请重试。")
        
        if include_technical:
            base_message += f"\n技术详情: {str(error)}"
        
        return base_message
    
    @classmethod
    def handle_database_error(cls, error: Exception, query: str = None) -> str:
        """处理数据库错误"""
        context = {"query": query} if query else {}
        error_id = cls.log_error_with_context(error, context, ErrorType.DATABASE)
        
        # 根据具体错误类型提供更详细的消息
        error_str = str(error).lower()
        
        if "login failed" in error_str or "authentication" in error_str:
            user_message = "数据库登录失败，请检查用户名和密码。"
        elif "timeout" in error_str:
            user_message = "数据库连接超时，请检查网络连接和服务器状态。"
        elif "syntax error" in error_str or "invalid" in error_str:
            user_message = "SQL 语法错误，请检查查询语句。"
        elif "permission" in error_str or "access denied" in error_str:
            user_message = "数据库权限不足，无法执行此操作。"
        else:
            user_message = "数据库操作失败，请检查连接设置和查询语法。"
        
        return f"{user_message} (错误ID: {error_id})"
    
    @classmethod
    def handle_filesystem_error(cls, error: Exception, file_path: str = None) -> str:
        """处理文件系统错误"""
        context = {"file_path": file_path} if file_path else {}
        error_id = cls.log_error_with_context(error, context, ErrorType.FILESYSTEM)
        
        # 根据具体错误类型提供更详细的消息
        error_str = str(error).lower()
        
        if "no such file" in error_str or "not found" in error_str:
            user_message = "文件或目录不存在。"
        elif "permission denied" in error_str or "access denied" in error_str:
            user_message = "文件访问权限不足。"
        elif "disk full" in error_str or "no space" in error_str:
            user_message = "磁盘空间不足。"
        elif "file exists" in error_str:
            user_message = "文件已存在。"
        else:
            user_message = "文件系统操作失败。"
        
        return f"{user_message} (错误ID: {error_id})"
    
    @classmethod
    def handle_ui_error(cls, error: Exception, operation: str = None) -> str:
        """处理UI错误"""
        context = {"operation": operation} if operation else {}
        error_id = cls.log_error_with_context(error, context, ErrorType.UI)
        
        user_message = "用户界面操作失败，请刷新页面后重试。"
        return f"{user_message} (错误ID: {error_id})"
    
    @classmethod
    def clear_old_errors(cls, max_age_hours: int = 24):
        """清理旧的错误记录"""
        from datetime import datetime, timedelta
        
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        to_remove = []
        for error_id, error_info in cls._error_log.items():
            try:
                error_time = datetime.fromisoformat(error_info["timestamp"])
                if error_time < cutoff_time:
                    to_remove.append(error_id)
            except (ValueError, KeyError):
                # 如果时间戳格式有问题，也删除
                to_remove.append(error_id)
        
        for error_id in to_remove:
            del cls._error_log[error_id]
        
        if to_remove:
            warning_log(f"清理了 {len(to_remove)} 个旧的错误记录")
    
    @classmethod
    def get_error_statistics(cls) -> Dict[str, Any]:
        """获取错误统计信息"""
        if not cls._error_log:
            return {"total": 0, "by_type": {}, "recent_count": 0}
        
        from datetime import datetime, timedelta
        
        recent_cutoff = datetime.now() - timedelta(hours=1)
        
        stats = {
            "total": len(cls._error_log),
            "by_type": {},
            "recent_count": 0,
        }
        
        for error_info in cls._error_log.values():
            # 按类型统计
            error_type = error_info.get("type", "unknown")
            stats["by_type"][error_type] = stats["by_type"].get(error_type, 0) + 1
            
            # 最近一小时的错误数量
            try:
                error_time = datetime.fromisoformat(error_info["timestamp"])
                if error_time > recent_cutoff:
                    stats["recent_count"] += 1
            except (ValueError, KeyError):
                pass
        
        return stats


# 便捷的错误处理装饰器
def handle_errors(error_type: ErrorType = ErrorType.SYSTEM, user_message: str = None):
    """
    错误处理装饰器
    
    用法:
    @handle_errors(ErrorType.DATABASE, "数据库操作失败")
    def database_operation():
        # 可能抛出异常的代码
        pass
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_id = ErrorHandler.log_error_with_context(
                    e, 
                    {"function": func.__name__, "args": str(args)[:100]}, 
                    error_type,
                    user_message
                )
                
                # 重新抛出异常，但添加错误ID信息
                formatted_message = ErrorHandler.format_user_error(e, error_type)
                raise type(e)(f"{formatted_message} (错误ID: {error_id})") from e
        
        return wrapper
    return decorator


# 异步错误处理装饰器
def handle_async_errors(error_type: ErrorType = ErrorType.SYSTEM, user_message: str = None):
    """
    异步错误处理装饰器

    用法:
    @handle_async_errors(ErrorType.DATABASE, "数据库操作失败")
    async def async_database_operation():
        # 可能抛出异常的异步代码
        pass
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                error_id = ErrorHandler.log_error_with_context(
                    e,
                    {"function": func.__name__, "args": str(args)[:100]},
                    error_type,
                    user_message
                )

                # 重新抛出异常，但添加错误ID信息
                formatted_message = ErrorHandler.format_user_error(e, error_type)
                raise type(e)(f"{formatted_message} (错误ID: {error_id})") from e

        return wrapper
    return decorator
