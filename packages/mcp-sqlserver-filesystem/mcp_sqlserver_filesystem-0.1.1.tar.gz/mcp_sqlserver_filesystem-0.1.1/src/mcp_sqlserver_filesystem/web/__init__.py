"""
Web UI 模块
===========

提供基于FastAPI的Web用户界面，支持：
- SQL查询结果展示
- 文件操作确认对话框
- 目录浏览界面
- 实时状态监控
- WebSocket通信
"""

from .main import WebUIManager, get_web_ui_manager

__all__ = ["WebUIManager", "get_web_ui_manager"]
