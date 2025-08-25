#!/usr/bin/env python3
"""
MCP SQL Server Filesystem - 主程序入口
=====================================

此文件允许包通过 `python -m mcp_sqlserver_filesystem` 执行。

使用方法:
  python -m mcp_sqlserver_filesystem        # 启动 MCP 服务器
  python -m mcp_sqlserver_filesystem test   # 执行测试
"""

import argparse
import asyncio
import os
import sys
import warnings


# 抑制 Windows 上的 asyncio ResourceWarning
if sys.platform == "win32":
    warnings.filterwarnings(
        "ignore", category=ResourceWarning, message=".*unclosed transport.*"
    )
    warnings.filterwarnings("ignore", category=ResourceWarning, message=".*unclosed.*")

    # 设置 asyncio 事件循环策略以减少警告
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    except AttributeError:
        pass


def main():
    """主程序入口点"""
    parser = argparse.ArgumentParser(
        description="MCP SQL Server Filesystem - 增强的 SQL Server 和文件系统访问 MCP 服务器"
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # 服务器命令（默认）
    subparsers.add_parser("server", help="启动 MCP 服务器（默认）")

    # 测试命令
    test_parser = subparsers.add_parser("test", help="执行测试")
    test_parser.add_argument(
        "--web", action="store_true", help="测试 Web UI (自动持续运行)"
    )
    test_parser.add_argument(
        "--desktop", action="store_true", help="测试桌面应用程序"
    )
    test_parser.add_argument(
        "--timeout", type=int, default=60, help="测试超时时间 (秒)"
    )

    # 版本命令
    subparsers.add_parser("version", help="显示版本信息")

    # UI functionality has been removed for simplicity

    args = parser.parse_args()

    # 处理命令
    if args.command == "version":
        show_version()
    elif args.command == "server" or args.command is None:
        run_server()
    else:
        # 不应该到达这里
        parser.print_help()
        sys.exit(1)


def run_server():
    """启动 MCP 服务器"""
    import asyncio
    from .server import main as server_main

    return asyncio.run(server_main())


# UI test functionality has been removed for simplicity


# All test functions have been removed for simplicity


def show_version():
    """显示版本信息"""
    from . import __author__, __version__

    print(f"MCP SQL Server Filesystem v{__version__}")
    print(f"作者: {__author__}")
    print("GitHub: https://github.com/ppengit/mcp-sqlserver-filesystem")


if __name__ == "__main__":
    main()
