#!/usr/bin/env python3
"""
桌面应用智能启动器
================

参考 mcp-feedback-enhanced 的实现方式，提供智能的桌面应用启动机制。
优先尝试预编译二进制文件，失败后自动回退到Web UI。
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
from typing import Optional
import tempfile
import stat
import shutil

from .web.main import WebUIManager


class DesktopLauncher:
    """桌面应用智能启动器"""
    
    def __init__(self, test_mode: bool = False):
        self.test_mode = test_mode
        self.process = None
        self.web_manager = None
    
    def launch(self) -> bool:
        """启动桌面应用，失败时自动回退到Web UI"""
        try:
            print("🖥️ 正在启动桌面应用...")
            
            # 尝试启动预编译的桌面应用
            if self._try_launch_prebuilt():
                print("✅ 桌面应用启动成功")
                return True
                
        except Exception as e:
            print(f"🔄 桌面应用启动失败: {e}")
            
        # 自动回退到Web UI
        print("🌐 自动回退到 Web UI 模式...")
        print("💡 Web UI 提供完全相同的功能，无需额外安装")
        return self._launch_web_ui()
    
    def _try_launch_prebuilt(self) -> bool:
        """尝试启动预编译的桌面应用"""
        binary_path = self._find_prebuilt_binary()
        
        if not binary_path:
            print("📦 未找到预编译的桌面二进制文件")
            return False
            
        print(f"✅ 找到预编译二进制文件: {binary_path.name}")
        
        # 准备可执行文件
        executable_path = self._prepare_executable(binary_path)
        if not executable_path:
            return False
            
        # 启动Web后端
        self._start_web_backend()
        
        # 启动桌面应用
        try:
            if self.test_mode:
                self.process = subprocess.Popen(
                    [str(executable_path)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
                )
                
                # 等待应用启动
                import time
                time.sleep(3)
                
                if self.process.poll() is not None:
                    stdout, stderr = self.process.communicate()
                    error_msg = stderr.decode() if stderr else "Unknown error"
                    raise Exception(f"桌面应用启动失败: {error_msg}")
                    
            else:
                subprocess.run([str(executable_path)])
                
            return True
            
        except Exception as e:
            print(f"❌ 执行桌面二进制文件失败: {e}")
            return False
    
    def _find_prebuilt_binary(self) -> Optional[Path]:
        """查找预编译的桌面二进制文件"""
        try:
            # 获取当前平台信息
            current_platform = platform.system().lower()
            current_arch = platform.machine().lower()
            
            # 标准化架构名称
            if current_arch in ['amd64', 'x86_64']:
                current_arch = 'x86_64'
            elif current_arch in ['arm64', 'aarch64']:
                current_arch = 'arm64'
            
            # 查找桌面二进制文件目录
            binaries_dir = Path(__file__).parent / "desktop_binaries"
            if not binaries_dir.exists():
                return None
            
            # 构建文件名模式
            if current_platform == "windows":
                pattern = f"mcp-sqlserver-filesystem.exe.windows-{current_arch}"
            elif current_platform == "darwin":
                pattern = f"mcp-sqlserver-filesystem.macos-{current_arch}"
            elif current_platform == "linux":
                pattern = f"mcp-sqlserver-filesystem.linux-{current_arch}"
            else:
                print(f"⚠️ 不支持的平台: {current_platform}")
                return None
            
            binary_path = binaries_dir / pattern
            if binary_path.exists():
                return binary_path
            
            # 回退：查找任何匹配的二进制文件
            for file_path in binaries_dir.glob("mcp-sqlserver-filesystem*"):
                if current_platform in file_path.name:
                    print(f"🔍 使用回退二进制文件: {file_path.name}")
                    return file_path
            
            return None
            
        except Exception as e:
            print(f"❌ 查找预编译二进制文件时出错: {e}")
            return None
    
    def _prepare_executable(self, binary_path: Path) -> Optional[Path]:
        """准备可执行文件"""
        try:
            # 创建临时目录
            temp_dir = Path(tempfile.gettempdir()) / "mcp-sqlserver-filesystem"
            temp_dir.mkdir(exist_ok=True)
            
            # 确定可执行文件名
            if sys.platform == "win32":
                exec_name = "mcp-sqlserver-filesystem.exe"
            else:
                exec_name = "mcp-sqlserver-filesystem"
            
            executable_path = temp_dir / exec_name
            
            # 复制二进制文件到临时位置
            shutil.copy2(binary_path, executable_path)
            
            # 在Unix系统上设置执行权限
            if sys.platform != "win32":
                executable_path.chmod(executable_path.stat().st_mode | stat.S_IEXEC)
            
            print(f"📁 可执行文件准备完成: {executable_path}")
            return executable_path
            
        except Exception as e:
            print(f"❌ 准备可执行文件失败: {e}")
            return None
    
    def _start_web_backend(self):
        """启动Web后端服务"""
        try:
            # 设置桌面模式环境变量
            os.environ["MCP_DESKTOP_MODE"] = "true"
            os.environ["MCP_WEB_HOST"] = "127.0.0.1"
            os.environ["MCP_WEB_PORT"] = "8765"
            
            # 获取Web UI管理器
            self.web_manager = WebUIManager()
            
            if self.test_mode:
                # 测试模式：后台启动
                import threading
                
                def start_server():
                    self.web_manager.start_server()
                
                server_thread = threading.Thread(target=start_server, daemon=True)
                server_thread.start()
                
                # 等待服务器启动
                import time
                time.sleep(2)
                
                if self.web_manager.server_thread and self.web_manager.server_thread.is_alive():
                    print(f"✅ Web后端服务启动成功: {self.web_manager.host}:{self.web_manager.port}")
                else:
                    raise Exception("Web后端服务启动失败")
            else:
                # 生产模式：直接启动
                self.web_manager.start_server()
                print(f"✅ Web后端服务启动成功: {self.web_manager.host}:{self.web_manager.port}")
                
        except Exception as e:
            print(f"❌ Web后端服务启动失败: {e}")
            raise
    
    def _launch_web_ui(self) -> bool:
        """启动Web UI作为回退方案"""
        try:
            import tempfile
            import time
            import webbrowser
            
            # 设置测试模式环境变量
            os.environ["MCP_TEST_MODE"] = "true"
            os.environ["MCP_WEB_HOST"] = "127.0.0.1"
            os.environ["MCP_WEB_PORT"] = "9765"
            
            print("🔧 启动 Web UI 管理器...")
            manager = WebUIManager()
            
            # 显示最终使用的端口
            if manager.port != 9765:
                print(f"💡 端口 9765 被占用，已自动切换到端口 {manager.port}")
            
            print("🔧 创建测试会话...")
            with tempfile.TemporaryDirectory() as temp_dir:
                test_content = """# MCP SQL Server Filesystem - 桌面应用测试

## 🎯 测试目标
验证 MCP SQL Server Filesystem 的桌面应用回退机制

### ✨ 功能特性

#### 数据库操作
- **SQL 查询** - 执行 SELECT 查询并在 UI 中显示结果
- **SQL 执行** - 执行 INSERT/UPDATE/DELETE 操作
- **表结构查询** - 获取表的详细结构信息
- **表列表** - 列出数据库中的所有表

#### 文件系统操作
- **文件读取** - 读取文件内容
- **文件写入** - 写入内容到文件
- **目录列表** - 列出目录内容

### 🌐 界面说明
此界面是桌面应用的Web UI回退版本，提供完全相同的功能。

### 🔒 安全特性
- SQL注入防护
- 文件系统访问控制
- 环境变量管理

---

**状态**: ✅ Web UI 回退模式正常运行"""

                created_session_id = manager.create_session(temp_dir, test_content)
                
                if created_session_id:
                    print("✅ 会话创建成功")
                    
                    print("🚀 启动 Web 服务器...")
                    manager.start_server()
                    time.sleep(3)  # 等待服务器启动
                    
                    if manager.server_thread and manager.server_thread.is_alive():
                        print("✅ Web 服务器启动成功")
                        url = f"http://{manager.host}:{manager.port}"
                        print(f"🌐 Web UI 运行在: {url}")
                        
                        # 尝试打开浏览器
                        print("🌐 正在打开浏览器...")
                        try:
                            webbrowser.open(url)
                            print("✅ 浏览器已打开")
                        except Exception as e:
                            print(f"⚠️ 无法自动打开浏览器: {e}")
                            print(f"💡 请手动打开浏览器并访问: {url}")
                        
                        print("📝 Web UI 启动完成，进入持续模式...")
                        print("💡 提示：服务器将持续运行，按 Ctrl+C 停止")
                        
                        if self.test_mode:
                            try:
                                # 保持服务器运行
                                while True:
                                    time.sleep(1)
                            except KeyboardInterrupt:
                                print("\n🛑 停止服务器...")
                                return True
                        
                        return True
                    else:
                        print("❌ Web 服务器启动失败")
                        return False
                else:
                    print("❌ 会话创建失败")
                    return False
                    
        except Exception as e:
            print(f"❌ Web UI 启动失败: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            # 清理环境变量
            os.environ.pop("MCP_TEST_MODE", None)
            os.environ.pop("MCP_WEB_HOST", None)
            os.environ.pop("MCP_WEB_PORT", None)
    
    def stop(self):
        """停止桌面应用"""
        try:
            print("🛑 停止桌面应用...")
            
            # 停止桌面进程
            if self.process:
                self.process.terminate()
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                self.process = None
            
            # 停止Web后端
            if self.web_manager:
                self.web_manager.stop_server()
            
            print("✅ 桌面应用已停止")
            
        except Exception as e:
            print(f"❌ 停止桌面应用时出错: {e}")


def launch_desktop_app(test_mode: bool = False) -> bool:
    """启动桌面应用的便捷函数"""
    launcher = DesktopLauncher(test_mode=test_mode)
    return launcher.launch()