"""UI Manager for desktop application interface."""

import asyncio
import json
import logging
import os
import subprocess
import sys
import threading
import time
import webbrowser
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import websockets
from websockets.server import WebSocketServerProtocol

from .config import config

logger = logging.getLogger(__name__)


class UIManager:
    """Manages desktop UI interactions using WebSocket communication."""
    
    def __init__(self):
        self.websocket_server = None
        self.websocket_port = 8766
        self.connected_clients = set()
        self.desktop_process = None
        self.web_server_process = None
        self.is_running = False
        
    async def start(self):
        """Start the UI manager."""
        if self.is_running:
            return
            
        try:
            # Start WebSocket server
            await self._start_websocket_server()
            
            # Start desktop application or web interface
            await self._start_ui_interface()
            
            self.is_running = True
            logger.info("UI Manager started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start UI Manager: {e}")
            raise
    
    async def stop(self):
        """Stop the UI manager."""
        if not self.is_running:
            return
            
        try:
            # Close all WebSocket connections
            if self.connected_clients:
                await asyncio.gather(
                    *[client.close() for client in self.connected_clients],
                    return_exceptions=True
                )
                self.connected_clients.clear()
            
            # Stop WebSocket server
            if self.websocket_server:
                self.websocket_server.close()
                await self.websocket_server.wait_closed()
                self.websocket_server = None
            
            # Stop desktop application
            if self.desktop_process:
                self.desktop_process.terminate()
                self.desktop_process = None
            
            # Stop web server
            if self.web_server_process:
                self.web_server_process.terminate()
                self.web_server_process = None
            
            self.is_running = False
            logger.info("UI Manager stopped")
            
        except Exception as e:
            logger.error(f"Error stopping UI Manager: {e}")
    
    async def _start_websocket_server(self):
        """Start WebSocket server for UI communication."""
        try:
            self.websocket_server = await websockets.serve(
                self._handle_websocket_connection,
                "localhost",
                self.websocket_port
            )
            logger.info(f"WebSocket server started on port {self.websocket_port}")
            
        except Exception as e:
            logger.error(f"Failed to start WebSocket server: {e}")
            raise
    
    async def _handle_websocket_connection(self, websocket: WebSocketServerProtocol, path: str):
        """Handle WebSocket connection from UI."""
        self.connected_clients.add(websocket)
        logger.info(f"UI client connected: {websocket.remote_address}")
        
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self._handle_ui_message(websocket, data)
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON received: {message}")
                except Exception as e:
                    logger.error(f"Error handling UI message: {e}")
        
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"UI client disconnected: {websocket.remote_address}")
        
        finally:
            self.connected_clients.discard(websocket)
    
    async def _handle_ui_message(self, websocket: WebSocketServerProtocol, data: Dict[str, Any]):
        """Handle message from UI."""
        message_type = data.get("type")
        
        if message_type == "ping":
            await websocket.send(json.dumps({"type": "pong"}))
        
        elif message_type == "user_response":
            # Handle user responses (confirmations, inputs, etc.)
            response_id = data.get("response_id")
            response_data = data.get("data")
            
            # Store response for retrieval by waiting functions
            if hasattr(self, '_pending_responses'):
                self._pending_responses[response_id] = response_data
        
        else:
            logger.warning(f"Unknown message type: {message_type}")
    
    async def _start_ui_interface(self):
        """Start desktop application or web interface."""
        desktop_mode = os.getenv("MCP_DESKTOP_MODE", "false").lower() == "true"
        
        if desktop_mode:
            await self._start_desktop_app()
        else:
            await self._start_web_interface()
    
    async def _start_desktop_app(self):
        """Start Tauri desktop application."""
        try:
            # Check if desktop app exists
            desktop_app_path = Path(__file__).parent.parent.parent / "src-tauri" / "target" / "release"
            
            if sys.platform == "win32":
                app_executable = desktop_app_path / "mcp-sqlserver-filesystem.exe"
            elif sys.platform == "darwin":
                app_executable = desktop_app_path / "mcp-sqlserver-filesystem.app" / "Contents" / "MacOS" / "mcp-sqlserver-filesystem"
            else:
                app_executable = desktop_app_path / "mcp-sqlserver-filesystem"
            
            if app_executable.exists():
                # Start desktop application
                self.desktop_process = subprocess.Popen([str(app_executable)])
                logger.info("Desktop application started")
            else:
                logger.warning("Desktop application not found, falling back to web interface")
                await self._start_web_interface()
                
        except Exception as e:
            logger.error(f"Failed to start desktop application: {e}")
            await self._start_web_interface()
    
    async def _start_web_interface(self):
        """Start web interface."""
        try:
            # Start simple HTTP server for web interface
            web_port = 8765
            web_dir = Path(__file__).parent / "web"
            
            if web_dir.exists():
                # Start HTTP server in background
                import http.server
                import socketserver
                
                def start_server():
                    os.chdir(web_dir)
                    handler = http.server.SimpleHTTPRequestHandler
                    with socketserver.TCPServer(("", web_port), handler) as httpd:
                        httpd.serve_forever()
                
                server_thread = threading.Thread(target=start_server, daemon=True)
                server_thread.start()
                
                # Open browser
                webbrowser.open(f"http://localhost:{web_port}")
                logger.info(f"Web interface started on http://localhost:{web_port}")
            else:
                logger.warning("Web interface files not found")
                
        except Exception as e:
            logger.error(f"Failed to start web interface: {e}")
    
    async def _send_to_ui(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send message to UI and optionally wait for response."""
        if not self.connected_clients:
            logger.warning("No UI clients connected")
            return None
        
        message_json = json.dumps(message)
        
        # Send to all connected clients
        await asyncio.gather(
            *[client.send(message_json) for client in self.connected_clients],
            return_exceptions=True
        )
        
        # If expecting response, wait for it
        if message.get("expect_response"):
            response_id = message.get("id")
            if response_id:
                return await self._wait_for_response(response_id)
        
        return None
    
    async def _wait_for_response(self, response_id: str, timeout: float = 30.0) -> Optional[Dict[str, Any]]:
        """Wait for user response."""
        if not hasattr(self, '_pending_responses'):
            self._pending_responses = {}
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            if response_id in self._pending_responses:
                response = self._pending_responses.pop(response_id)
                return response
            await asyncio.sleep(0.1)
        
        logger.warning(f"Timeout waiting for response {response_id}")
        return None
    
    async def show_query_results(self, query: str, results: List[Dict[str, Any]], parameters: Optional[Dict[str, Any]] = None):
        """Show SQL query results in UI."""
        message = {
            "type": "show_query_results",
            "data": {
                "query": query,
                "results": results,
                "parameters": parameters or {},
                "timestamp": time.time()
            }
        }
        await self._send_to_ui(message)
    
    async def show_table_schema(self, schema_info: Dict[str, Any]):
        """Show table schema in UI."""
        message = {
            "type": "show_table_schema",
            "data": schema_info
        }
        await self._send_to_ui(message)
    
    async def show_table_list(self, schema_name: str, tables: List[str]):
        """Show table list in UI."""
        message = {
            "type": "show_table_list",
            "data": {
                "schema_name": schema_name,
                "tables": tables
            }
        }
        await self._send_to_ui(message)
    
    async def show_file_content(self, file_path: str, content: str):
        """Show file content in UI."""
        message = {
            "type": "show_file_content",
            "data": {
                "file_path": file_path,
                "content": content
            }
        }
        await self._send_to_ui(message)
    
    async def show_directory_listing(self, dir_path: str, items: List[Dict[str, Any]]):
        """Show directory listing in UI."""
        message = {
            "type": "show_directory_listing",
            "data": {
                "dir_path": dir_path,
                "items": items
            }
        }
        await self._send_to_ui(message)
    
    async def show_confirmation(self, title: str, message: str) -> bool:
        """Show confirmation dialog and return user response."""
        response_id = f"confirm_{int(time.time() * 1000)}"
        
        ui_message = {
            "type": "show_confirmation",
            "id": response_id,
            "expect_response": True,
            "data": {
                "title": title,
                "message": message
            }
        }
        
        response = await self._send_to_ui(ui_message)
        return response.get("confirmed", False) if response else False
    
    async def show_info(self, title: str, message: str):
        """Show info dialog."""
        ui_message = {
            "type": "show_info",
            "data": {
                "title": title,
                "message": message
            }
        }
        await self._send_to_ui(ui_message)
    
    async def show_error(self, title: str, message: str):
        """Show error dialog."""
        ui_message = {
            "type": "show_error",
            "data": {
                "title": title,
                "message": message
            }
        }
        await self._send_to_ui(ui_message)


# Global UI manager instance
ui_manager = UIManager()
