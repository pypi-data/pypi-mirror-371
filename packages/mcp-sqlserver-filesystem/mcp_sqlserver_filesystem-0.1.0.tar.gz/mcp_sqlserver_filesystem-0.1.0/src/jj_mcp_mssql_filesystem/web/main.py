"""
Web UI 主管理器
===============

管理Web UI服务器、会话和用户交互。
"""

import asyncio
import json
import os
import threading
import time
import uuid
import webbrowser
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
import tempfile
import socket

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

from ..debug import debug_log, warning_log, error_log, web_debug_log, ui_debug_log
from ..utils.error_handler import ErrorHandler, ErrorType


class WebUIManager:
    """Web UI 管理器"""
    
    def __init__(self, host: str = None, port: int = None):
        """
        初始化Web UI管理器
        
        Args:
            host: 服务器主机地址
            port: 服务器端口
        """
        self.host = host or os.getenv("MCP_WEB_HOST", "127.0.0.1")
        self.port = port or int(os.getenv("MCP_WEB_PORT", "8765"))
        
        # 自动寻找可用端口
        self.port = self._find_available_port(self.port)
        
        self.app = FastAPI(title="MCP SQL Server Filesystem UI", version="0.1.0")
        self.server_thread: Optional[threading.Thread] = None
        self.server_process = None
        self.is_running_flag = False
        
        # 会话管理
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.active_websockets: Set[WebSocket] = set()
        
        # 桌面应用实例（如果有）
        self.desktop_app_instance = None
        
        # 设置路由
        self._setup_routes()
        
        web_debug_log(f"WebUIManager initialized on {self.host}:{self.port}")
    
    def _find_available_port(self, start_port: int) -> int:
        """寻找可用端口"""
        for port in range(start_port, start_port + 100):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind((self.host, port))
                    return port
            except OSError:
                continue
        
        # 如果找不到可用端口，使用原始端口
        warning_log(f"Could not find available port starting from {start_port}, using {start_port}")
        return start_port
    
    def _setup_routes(self):
        """设置FastAPI路由"""
        
        @self.app.get("/", response_class=HTMLResponse)
        async def home(request: Request):
            """主页"""
            return HTMLResponse(self._get_home_html())
        
        @self.app.get("/health")
        async def health():
            """健康检查"""
            return {"status": "ok", "sessions": len(self.sessions)}
        
        @self.app.post("/api/sessions")
        async def create_session(request: Request):
            """创建新会话"""
            try:
                data = await request.json()
                session_id = self.create_session(
                    data.get("workspace_dir", ""),
                    data.get("content", "")
                )
                return {"session_id": session_id}
            except Exception as e:
                error_id = ErrorHandler.log_error_with_context(e, {"endpoint": "create_session"}, ErrorType.UI)
                return JSONResponse(
                    status_code=500,
                    content={"error": f"Failed to create session (ID: {error_id})"}
                )
        
        @self.app.websocket("/ws/{session_id}")
        async def websocket_endpoint(websocket: WebSocket, session_id: str):
            """WebSocket连接"""
            await self._handle_websocket(websocket, session_id)
        
        @self.app.get("/api/sessions/{session_id}")
        async def get_session(session_id: str):
            """获取会话信息"""
            session = self.sessions.get(session_id)
            if not session:
                return JSONResponse(status_code=404, content={"error": "Session not found"})
            return session
        
        @self.app.post("/api/query-results")
        async def show_query_results(request: Request):
            """显示SQL查询结果"""
            try:
                data = await request.json()
                await self.show_query_results(data.get("query", ""), data.get("results", []))
                return {"status": "ok"}
            except Exception as e:
                error_id = ErrorHandler.log_error_with_context(e, {"endpoint": "show_query_results"}, ErrorType.UI)
                return JSONResponse(
                    status_code=500,
                    content={"error": f"Failed to show query results (ID: {error_id})"}
                )
    
    def _get_home_html(self) -> str:
        """获取主页HTML"""
        return """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MCP SQL Server Filesystem UI</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }
        .header p {
            margin: 10px 0 0 0;
            opacity: 0.9;
            font-size: 1.1em;
        }
        .content {
            padding: 40px;
        }
        .feature-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            margin-top: 30px;
        }
        .feature-card {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 25px;
            border-left: 4px solid #4facfe;
            transition: transform 0.2s ease;
        }
        .feature-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .feature-card h3 {
            margin: 0 0 15px 0;
            color: #2c3e50;
            font-size: 1.3em;
        }
        .feature-card p {
            margin: 0;
            color: #666;
            line-height: 1.6;
        }
        .status {
            background: #e8f5e8;
            border: 1px solid #4caf50;
            border-radius: 5px;
            padding: 15px;
            margin: 20px 0;
            text-align: center;
        }
        .status.running {
            background: #e8f5e8;
            border-color: #4caf50;
            color: #2e7d32;
        }
        .footer {
            background: #2c3e50;
            color: white;
            padding: 20px;
            text-align: center;
            font-size: 0.9em;
        }
        .api-info {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 5px;
            padding: 15px;
            margin: 20px 0;
        }
        .api-info h4 {
            margin: 0 0 10px 0;
            color: #856404;
        }
        .api-info code {
            background: #f8f9fa;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 MCP SQL Server Filesystem UI</h1>
            <p>增强的 SQL Server 和文件系统访问界面</p>
        </div>
        
        <div class="content">
            <div class="status running">
                ✅ Web UI 服务器正在运行
            </div>
            
            <div class="feature-grid">
                <div class="feature-card">
                    <h3>🗄️ SQL Server 操作</h3>
                    <p>执行 SQL 查询、查看表结构、管理数据库连接。查询结果将在专用窗口中显示，支持大数据集的分页浏览。</p>
                </div>
                
                <div class="feature-card">
                    <h3>📁 文件系统管理</h3>
                    <p>读取、写入、浏览文件和目录。支持文件内容预览、批量操作确认对话框，确保操作安全。</p>
                </div>
                
                <div class="feature-card">
                    <h3>🔄 实时交互</h3>
                    <p>通过 WebSocket 实现实时通信，支持操作进度显示、状态更新和用户确认对话框。</p>
                </div>
                
                <div class="feature-card">
                    <h3>🛡️ 安全控制</h3>
                    <p>内置 SQL 注入防护、文件系统访问控制、操作日志记录，确保系统安全运行。</p>
                </div>
            </div>
            
            <div class="api-info">
                <h4>📡 API 端点</h4>
                <p><strong>健康检查:</strong> <code>GET /health</code></p>
                <p><strong>创建会话:</strong> <code>POST /api/sessions</code></p>
                <p><strong>WebSocket:</strong> <code>WS /ws/{session_id}</code></p>
                <p><strong>显示查询结果:</strong> <code>POST /api/query-results</code></p>
            </div>
        </div>
        
        <div class="footer">
            <p>MCP SQL Server Filesystem v0.1.0 | 基于 FastAPI 和 WebSocket</p>
        </div>
    </div>
    
    <script>
        // 简单的状态检查
        setInterval(async () => {
            try {
                const response = await fetch('/health');
                const data = await response.json();
                console.log('Health check:', data);
            } catch (error) {
                console.error('Health check failed:', error);
            }
        }, 30000); // 每30秒检查一次
    </script>
</body>
</html>
        """
    
    async def _handle_websocket(self, websocket: WebSocket, session_id: str):
        """处理WebSocket连接"""
        await websocket.accept()
        self.active_websockets.add(websocket)
        
        ui_debug_log(f"WebSocket connected for session {session_id}")
        
        try:
            while True:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # 处理不同类型的消息
                await self._handle_websocket_message(websocket, session_id, message)
                
        except WebSocketDisconnect:
            ui_debug_log(f"WebSocket disconnected for session {session_id}")
        except Exception as e:
            error_log(f"WebSocket error for session {session_id}", e)
        finally:
            self.active_websockets.discard(websocket)
    
    async def _handle_websocket_message(self, websocket: WebSocket, session_id: str, message: Dict[str, Any]):
        """处理WebSocket消息"""
        message_type = message.get("type")
        
        if message_type == "ping":
            await websocket.send_text(json.dumps({"type": "pong"}))
        elif message_type == "get_session":
            session = self.sessions.get(session_id, {})
            await websocket.send_text(json.dumps({"type": "session_data", "data": session}))
        else:
            ui_debug_log(f"Unknown WebSocket message type: {message_type}")
    
    def create_session(self, workspace_dir: str = "", content: str = "") -> str:
        """创建新会话"""
        session_id = str(uuid.uuid4())
        
        # 如果没有指定工作目录，使用临时目录
        if not workspace_dir:
            workspace_dir = tempfile.mkdtemp(prefix="mcp_session_")
        
        session = {
            "id": session_id,
            "workspace_dir": workspace_dir,
            "content": content,
            "created_at": time.time(),
            "last_activity": time.time(),
        }
        
        self.sessions[session_id] = session
        web_debug_log(f"Created session {session_id} with workspace {workspace_dir}")
        
        return session_id
    
    def start_server(self):
        """启动Web服务器"""
        if self.is_running_flag:
            warning_log("Web UI server is already running")
            return
        
        def run_server():
            try:
                web_debug_log(f"Starting Web UI server on {self.host}:{self.port}")
                uvicorn.run(
                    self.app,
                    host=self.host,
                    port=self.port,
                    log_level="warning",  # 减少日志输出
                    access_log=False,
                )
            except Exception as e:
                error_log("Web UI server failed to start", e)
        
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        self.is_running_flag = True
        
        web_debug_log("Web UI server thread started")
    
    def stop_server(self):
        """停止Web服务器"""
        if not self.is_running_flag:
            return
        
        self.is_running_flag = False
        
        # 关闭所有WebSocket连接
        for websocket in list(self.active_websockets):
            try:
                asyncio.create_task(websocket.close())
            except Exception as e:
                error_log("Failed to close WebSocket", e)
        
        web_debug_log("Web UI server stopped")
    
    def is_running(self) -> bool:
        """检查服务器是否运行"""
        return self.is_running_flag and self.server_thread and self.server_thread.is_alive()
    
    async def show_query_results(self, query: str, results: List[Dict[str, Any]]):
        """显示SQL查询结果"""
        message = {
            "type": "query_results",
            "data": {
                "query": query,
                "results": results,
                "timestamp": time.time(),
            }
        }
        
        await self._broadcast_to_websockets(message)
        ui_debug_log(f"Broadcasted query results: {len(results)} rows")
    
    async def show_table_schema(self, table_name: str, schema_name: str, schema_info: List[Dict[str, Any]]):
        """显示表结构"""
        message = {
            "type": "table_schema",
            "data": {
                "table_name": table_name,
                "schema_name": schema_name,
                "schema_info": schema_info,
                "timestamp": time.time(),
            }
        }
        
        await self._broadcast_to_websockets(message)
        ui_debug_log(f"Broadcasted table schema for {schema_name}.{table_name}")
    
    async def show_tables_list(self, schema_name: str, tables: List[str]):
        """显示表列表"""
        message = {
            "type": "tables_list",
            "data": {
                "schema_name": schema_name,
                "tables": tables,
                "timestamp": time.time(),
            }
        }
        
        await self._broadcast_to_websockets(message)
        ui_debug_log(f"Broadcasted tables list for schema {schema_name}: {len(tables)} tables")
    
    async def show_file_content(self, file_path: str, content: str):
        """显示文件内容"""
        message = {
            "type": "file_content",
            "data": {
                "file_path": file_path,
                "content": content,
                "timestamp": time.time(),
            }
        }
        
        await self._broadcast_to_websockets(message)
        ui_debug_log(f"Broadcasted file content for {file_path}")
    
    async def show_file_write_confirmation(self, file_path: str, content_length: int) -> bool:
        """显示文件写入确认对话框"""
        # 在实际实现中，这里会显示确认对话框并等待用户响应
        # 现在简单返回True表示确认
        ui_debug_log(f"File write confirmation for {file_path} ({content_length} chars)")
        return True
    
    async def show_directory_listing(self, dir_path: str, items: List[Dict[str, Any]], recursive: bool):
        """显示目录列表"""
        message = {
            "type": "directory_listing",
            "data": {
                "dir_path": dir_path,
                "items": items,
                "recursive": recursive,
                "timestamp": time.time(),
            }
        }
        
        await self._broadcast_to_websockets(message)
        ui_debug_log(f"Broadcasted directory listing for {dir_path}: {len(items)} items")
    
    async def _broadcast_to_websockets(self, message: Dict[str, Any]):
        """向所有WebSocket连接广播消息"""
        if not self.active_websockets:
            return
        
        message_text = json.dumps(message)
        disconnected = set()
        
        for websocket in self.active_websockets:
            try:
                await websocket.send_text(message_text)
            except Exception as e:
                error_log(f"Failed to send WebSocket message", e)
                disconnected.add(websocket)
        
        # 清理断开的连接
        for websocket in disconnected:
            self.active_websockets.discard(websocket)


# 全局Web UI管理器实例
_web_ui_manager: Optional[WebUIManager] = None
_manager_lock = threading.Lock()


def get_web_ui_manager() -> WebUIManager:
    """获取全局Web UI管理器实例"""
    global _web_ui_manager
    if _web_ui_manager is None:
        with _manager_lock:
            if _web_ui_manager is None:
                _web_ui_manager = WebUIManager()
    return _web_ui_manager
