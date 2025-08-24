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

    # 添加直接测试选项（类似参考项目的 uvx mcp-feedback-enhanced@latest test --desktop）
    parser.add_argument(
        "--test-web", action="store_true", help="快速测试 Web UI"
    )
    parser.add_argument(
        "--test-desktop", action="store_true", help="快速测试桌面应用程序"
    )

    args = parser.parse_args()

    # 处理直接测试选项（优先级最高）
    if args.test_web:
        print("🧪 快速测试 Web UI...")
        test_args = argparse.Namespace(web=True, desktop=False, timeout=60)
        run_tests(test_args)
    elif args.test_desktop:
        print("🖥️ 快速测试桌面应用程序...")
        test_args = argparse.Namespace(web=False, desktop=True, timeout=60)
        run_tests(test_args)
    elif args.command == "test":
        run_tests(args)
    elif args.command == "version":
        show_version()
    elif args.command == "server" or args.command is None:
        run_server()
    else:
        # 不应该到达这里
        parser.print_help()
        sys.exit(1)


def run_server():
    """启动 MCP 服务器"""
    from .server import main as server_main

    return server_main()


def run_tests(args):
    """执行测试"""
    # 启用调试模式以显示测试过程
    os.environ["MCP_DEBUG"] = "true"

    # 在 Windows 上抑制 asyncio 警告
    if sys.platform == "win32":
        import warnings

        # 设置更全面的警告抑制
        os.environ["PYTHONWARNINGS"] = (
            "ignore::ResourceWarning,ignore::DeprecationWarning"
        )
        warnings.filterwarnings("ignore", category=ResourceWarning)
        warnings.filterwarnings("ignore", message=".*unclosed transport.*")
        warnings.filterwarnings("ignore", message=".*I/O operation on closed pipe.*")
        warnings.filterwarnings("ignore", message=".*unclosed.*")
        # 抑制 asyncio 相关的所有警告
        warnings.filterwarnings("ignore", module="asyncio.*")

    if args.web:
        print("🧪 执行 Web UI 测试...")
        success = test_web_ui_simple()
        if not success:
            sys.exit(1)
    elif args.desktop:
        print("🖥️ 启动桌面应用程序...")
        success = test_desktop_app()
        if not success:
            sys.exit(1)
    else:
        print("❌ 测试功能已简化")
        print("💡 可用的测试选项：")
        print("  --web         测试 Web UI")
        print("  --desktop     启动桌面应用程序")
        print("💡 对于开发者：使用 'uv run pytest' 执行完整测试")
        sys.exit(1)


def test_web_ui_simple():
    """简单的 Web UI 测试"""
    try:
        import tempfile
        import time
        import webbrowser

        from .web.main import WebUIManager

        # 设置测试模式，禁用自动清理避免权限问题
        os.environ["MCP_TEST_MODE"] = "true"
        os.environ["MCP_WEB_HOST"] = "127.0.0.1"
        # 设置更高的端口范围避免系统保留端口
        os.environ["MCP_WEB_PORT"] = "9765"

        print("🔧 创建 Web UI 管理器...")
        manager = WebUIManager()  # 使用环境变量控制主机和端口

        # 显示最终使用的端口（可能因端口占用而自动切换）
        if manager.port != 9765:
            print(f"💡 端口 9765 被占用，已自动切换到端口 {manager.port}")

        print("🔧 创建测试会话...")
        with tempfile.TemporaryDirectory() as temp_dir:
            test_content = """# SQL Server 和文件系统访问测试

## 🎯 测试目标
验证 MCP SQL Server Filesystem 的功能

### ✨ 支持的功能

#### 数据库操作
- **SQL 查询** - 执行 SELECT 查询并在 UI 中显示结果
- **SQL 执行** - 执行 INSERT/UPDATE/DELETE 操作
- **表结构查询** - 获取表的详细结构信息
- **表列表** - 列出数据库中的所有表

#### 文件系统操作
- **文件读取** - 读取文件内容
- **文件写入** - 写入内容到文件
- **目录列表** - 列出目录内容

### 📋 技术特性

```sql
-- SQL 查询示例
SELECT TOP 10 * FROM Users WHERE Status = 'Active'
```

```python
# 文件操作示例
with open('config.json', 'r') as f:
    config = json.load(f)
```

### 🔗 UI 交互

- 查询结果在专用窗口中显示
- 支持确认对话框
- 实时状态更新

> **安全特性**: 包含 SQL 注入防护和文件系统访问控制。

---

**测试状态**: ✅ 功能正常运作"""

            created_session_id = manager.create_session(temp_dir, test_content)

            if created_session_id:
                print("✅ 会话创建成功")

                print("🚀 启动 Web 服务器...")
                manager.start_server()
                time.sleep(5)  # 等待服务器完全启动

                if (
                    manager.server_thread is not None
                    and manager.server_thread.is_alive()
                ):
                    print("✅ Web 服务器启动成功")
                    url = f"http://{manager.host}:{manager.port}"
                    print(f"🌐 服务器运行在: {url}")

                    # 如果端口有变更，额外提醒
                    if manager.port != 9765:
                        print(
                            f"📌 注意：由于端口 9765 被占用，服务已切换到端口 {manager.port}"
                        )

                    # 尝试开启浏览器
                    print("🌐 正在开启浏览器...")
                    try:
                        webbrowser.open(url)
                        print("✅ 浏览器已开启")
                    except Exception as e:
                        print(f"⚠️  无法自动开启浏览器: {e}")
                        print(f"💡 请手动开启浏览器并访问: {url}")

                    print("📝 Web UI 测试完成，进入持续模式...")
                    print("💡 提示：服务器将持续运行，可在浏览器中测试交互功能")
                    print("💡 按 Ctrl+C 停止服务器")

                    try:
                        # 保持服务器运行
                        while True:
                            time.sleep(1)
                    except KeyboardInterrupt:
                        print("\n🛑 停止服务器...")
                        return True
                else:
                    print("❌ Web 服务器启动失败")
                    return False
            else:
                print("❌ 会话创建失败")
                return False

    except Exception as e:
        print(f"❌ Web UI 测试失败: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        # 清理测试环境变量
        os.environ.pop("MCP_TEST_MODE", None)
        os.environ.pop("MCP_WEB_HOST", None)
        os.environ.pop("MCP_WEB_PORT", None)


def test_desktop_app():
    """测试桌面应用程序功能"""
    try:
        print("🖥️ 测试桌面应用程序功能")
        print("=" * 50)
        
        print("🔧 检查桌面应用程序依赖...")
        
        # 使用新的智能启动器
        try:
            from .desktop_launcher import launch_desktop_app
            print("✅ 找到桌面应用启动器")
            
            # 启动桌面应用（智能回退机制）
            success = launch_desktop_app(test_mode=True)
            return success
            
        except ImportError as e:
            print(f"❌ 无法导入桌面应用启动器: {e}")
            print("🔄 自动回退到 Web UI 模式...")
            return test_web_ui_simple()
            
    except Exception as e:
        print(f"❌ 桌面应用程序测试失败: {e}")
        print("🔄 自动回退到 Web UI 模式...")
        return test_web_ui_simple()


def show_version():
    """显示版本信息"""
    from . import __author__, __version__

    print(f"MCP SQL Server Filesystem v{__version__}")
    print(f"作者: {__author__}")
    print("GitHub: https://github.com/ppengit/mcp-sqlserver-filesystem")


if __name__ == "__main__":
    main()
