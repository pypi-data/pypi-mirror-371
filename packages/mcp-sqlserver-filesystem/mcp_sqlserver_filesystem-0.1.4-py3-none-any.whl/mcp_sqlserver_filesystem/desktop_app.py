"""
Desktop Application Module for MCP SQL Server Filesystem

This module provides the desktop application functionality using Tauri framework.
It integrates with the existing MCP server to provide a native desktop experience.
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Optional, Dict, Any

from .config import config
from .web.main import get_web_ui_manager

logger = logging.getLogger(__name__)


class DesktopApp:
    """Desktop application manager using Tauri."""
    
    def __init__(self, test_mode: bool = False):
        self.test_mode = test_mode
        self.tauri_process: Optional[subprocess.Popen] = None
        self.web_manager = None
        self.is_running = False
        
    async def launch(self) -> bool:
        """Launch the desktop application."""
        try:
            logger.info("Launching desktop application...")
            
            # Start web server backend
            await self._start_web_backend()
            
            # Launch Tauri desktop app
            await self._launch_tauri_app()
            
            self.is_running = True
            logger.info("Desktop application launched successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to launch desktop application: {e}")
            return False
    
    async def _start_web_backend(self):
        """Start the web backend server."""
        try:
            # Set environment variables for desktop mode
            os.environ["MCP_DESKTOP_MODE"] = "true"
            os.environ["MCP_WEB_HOST"] = "127.0.0.1"
            os.environ["MCP_WEB_PORT"] = "8765"
            
            # Get web UI manager
            self.web_manager = get_web_ui_manager()
            
            if self.test_mode:
                # For test mode, start in background thread
                def start_server():
                    self.web_manager.start_server()
                
                server_thread = threading.Thread(target=start_server, daemon=True)
                server_thread.start()
                
                # Wait for server to start
                await asyncio.sleep(2)
                
                if (
                    self.web_manager.server_thread and 
                    self.web_manager.server_thread.is_alive()
                ):
                    logger.info(f"Web backend started on {self.web_manager.host}:{self.web_manager.port}")
                else:
                    raise Exception("Failed to start web backend server")
            else:
                # For production, start normally
                self.web_manager.start_server()
                
        except Exception as e:
            logger.error(f"Failed to start web backend: {e}")
            raise
    
    async def _launch_tauri_app(self):
        """Launch the Tauri desktop application."""
        try:
            tauri_dir = Path(__file__).parent.parent.parent / "src-tauri"
            
            if not tauri_dir.exists():
                raise Exception(f"Tauri directory not found: {tauri_dir}")
            
            # Check if we're in development or production
            if self._is_development():
                await self._launch_tauri_dev()
            else:
                await self._launch_tauri_prod()
                
        except Exception as e:
            logger.error(f"Failed to launch Tauri app: {e}")
            raise
    
    def _is_development(self) -> bool:
        """Check if we're running in development mode."""
        # Check if we have Cargo.toml and src directory (development indicators)
        tauri_dir = Path(__file__).parent.parent.parent / "src-tauri"
        return (tauri_dir / "Cargo.toml").exists() and (tauri_dir / "src").exists()
    
    async def _launch_tauri_dev(self):
        """Launch Tauri in development mode."""
        logger.info("Launching Tauri in development mode...")
        
        tauri_dir = Path(__file__).parent.parent.parent / "src-tauri"
        
        # Check if tauri-cli is available
        try:
            subprocess.run(["cargo", "tauri", "--version"], 
                         check=True, capture_output=True, cwd=tauri_dir)
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise Exception("Tauri CLI not found. Please install with: cargo install tauri-cli")
        
        # Launch in development mode
        cmd = ["cargo", "tauri", "dev"]
        
        if self.test_mode:
            # For test mode, run in background
            self.tauri_process = subprocess.Popen(
                cmd,
                cwd=tauri_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )
            
            # Wait a bit for the app to start
            await asyncio.sleep(5)
            
            if self.tauri_process.poll() is not None:
                # Process ended, check for errors
                stdout, stderr = self.tauri_process.communicate()
                error_msg = stderr.decode() if stderr else "Unknown error"
                raise Exception(f"Tauri dev process failed: {error_msg}")
                
            logger.info("Tauri development app launched")
        else:
            # For production, run synchronously
            result = subprocess.run(cmd, cwd=tauri_dir)
            if result.returncode != 0:
                raise Exception(f"Tauri dev command failed with code: {result.returncode}")
    
    async def _launch_tauri_prod(self):
        """Launch Tauri production build."""
        logger.info("Launching Tauri production app...")
        
        tauri_dir = Path(__file__).parent.parent.parent / "src-tauri"
        target_dir = tauri_dir / "target" / "release"
        
        # Find the executable
        executable_name = self._get_executable_name()
        executable_path = target_dir / executable_name
        
        if not executable_path.exists():
            # Try to build it
            logger.info("Production build not found, building...")
            await self._build_tauri_app()
        
        if not executable_path.exists():
            raise Exception(f"Tauri executable not found: {executable_path}")
        
        # Launch the executable
        if self.test_mode:
            self.tauri_process = subprocess.Popen(
                [str(executable_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )
            logger.info("Tauri production app launched")
        else:
            subprocess.run([str(executable_path)])
    
    def _get_executable_name(self) -> str:
        """Get the executable name for the current platform."""
        if sys.platform == "win32":
            return "mcp-sqlserver-filesystem.exe"
        elif sys.platform == "darwin":
            return "mcp-sqlserver-filesystem.app"
        else:
            return "mcp-sqlserver-filesystem"
    
    async def _build_tauri_app(self):
        """Build the Tauri application."""
        logger.info("Building Tauri application...")
        
        tauri_dir = Path(__file__).parent.parent.parent / "src-tauri"
        
        # Build command
        cmd = ["cargo", "tauri", "build"]
        
        result = subprocess.run(
            cmd,
            cwd=tauri_dir,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            error_msg = result.stderr or "Unknown build error"
            raise Exception(f"Failed to build Tauri app: {error_msg}")
        
        logger.info("Tauri application built successfully")
    
    def stop(self):
        """Stop the desktop application."""
        try:
            logger.info("Stopping desktop application...")
            
            # Stop Tauri process
            if self.tauri_process:
                self.tauri_process.terminate()
                try:
                    self.tauri_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.tauri_process.kill()
                self.tauri_process = None
            
            # Stop web backend
            if self.web_manager:
                self.web_manager.stop_server()
            
            self.is_running = False
            logger.info("Desktop application stopped")
            
        except Exception as e:
            logger.error(f"Error stopping desktop application: {e}")
    
    def is_available(self) -> bool:
        """Check if desktop application is available."""
        try:
            tauri_dir = Path(__file__).parent.parent.parent / "src-tauri"
            
            # Check if Tauri configuration exists
            if not (tauri_dir / "tauri.conf.json").exists():
                return False
            
            if not (tauri_dir / "Cargo.toml").exists():
                return False
            
            # Check if Rust/Cargo is available
            try:
                subprocess.run(["cargo", "--version"], 
                             check=True, capture_output=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                return False
            
            return True
            
        except Exception:
            return False


# Global desktop app instance
_desktop_app_instance: Optional[DesktopApp] = None


async def launch_desktop_app(test_mode: bool = False) -> DesktopApp:
    """Launch the desktop application.
    
    Args:
        test_mode: If True, run in test mode (background processes)
        
    Returns:
        DesktopApp instance
        
    Raises:
        Exception: If launch fails
    """
    global _desktop_app_instance
    
    if _desktop_app_instance and _desktop_app_instance.is_running:
        logger.warning("Desktop application already running")
        return _desktop_app_instance
    
    app = DesktopApp(test_mode=test_mode)
    
    if not app.is_available():
        raise Exception(
            "Desktop application not available. "
            "Please ensure Rust and Tauri CLI are installed."
        )
    
    success = await app.launch()
    if not success:
        raise Exception("Failed to launch desktop application")
    
    _desktop_app_instance = app
    return app


def get_desktop_app() -> Optional[DesktopApp]:
    """Get the current desktop application instance."""
    return _desktop_app_instance


def is_desktop_app_available() -> bool:
    """Check if desktop application is available."""
    try:
        app = DesktopApp()
        return app.is_available()
    except Exception:
        return False


# Compatibility functions for existing code
async def start_desktop_app(test_mode: bool = False) -> DesktopApp:
    """Compatibility function for starting desktop app."""
    return await launch_desktop_app(test_mode=test_mode)


def stop_desktop_app():
    """Stop the currently running desktop application."""
    global _desktop_app_instance
    
    if _desktop_app_instance:
        _desktop_app_instance.stop()
        _desktop_app_instance = None