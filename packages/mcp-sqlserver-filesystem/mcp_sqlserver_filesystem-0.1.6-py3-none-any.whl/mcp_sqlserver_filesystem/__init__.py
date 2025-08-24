"""
MCP SQL Server Filesystem
=========================

Enhanced MCP server for SQL Server and filesystem access with dual interface support.

Features:
- SQL Server database operations with UI display
- Filesystem operations with confirmation dialogs
- Web UI interface for interactive operations
- Desktop application support (cross-platform)
- Smart environment detection (SSH Remote, WSL, Local)
- Real-time WebSocket communication
- Session management and tracking
- Memory monitoring and resource management

Author: penjay
Email: peng.it@qq.com
License: MIT
"""

__version__ = "0.1.6"
__author__ = "PJ"
__email__ = "peng.it@qq.com"
__license__ = "MIT"

# 导出主要组件
from .server import main

__all__ = ["main", "__version__", "__author__", "__email__", "__license__"]
