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
            # First try to launch pre-built executable
            if self._has_prebuilt_executable():
                await self._launch_prebuilt_executable()
            else:
                # Fallback: try to build and run (development mode)
                tauri_dir = Path(__file__).parent.parent.parent / "src-tauri"
                
                if not tauri_dir.exists():
                    raise Exception(f"Tauri directory not found: {tauri_dir}")
                
                # Check if we're in development or production
                if self._is_development():
                    await self._launch_tauri_dev()
                else:
                    raise Exception("No pre-built executable found and not in development mode")
                
        except Exception as e:
            logger.error(f"Failed to launch Tauri app: {e}")
            raise
    
    async def _launch_prebuilt_executable(self):
        """Launch pre-built Tauri executable."""
        logger.info("Launching pre-built desktop application...")
        
        executable_path = None
        
        # First try development build location
        tauri_dir = Path(__file__).parent.parent.parent / "src-tauri"
        target_dir = tauri_dir / "target" / "release"
        executable_name = self._get_executable_name()
        dev_executable = target_dir / executable_name
        
        if dev_executable.exists():
            executable_path = dev_executable
            logger.info(f"Using development build: {executable_path}")
        else:
            # Try to extract from package
            package_binary = self._get_package_binary_path()
            if package_binary and package_binary.exists():
                # Copy to temp location and make executable
                import tempfile
                import stat
                
                temp_dir = Path(tempfile.gettempdir()) / "mcp-sqlserver-filesystem"
                temp_dir.mkdir(exist_ok=True)
                
                executable_path = temp_dir / executable_name
                
                # Copy binary to temp location
                import shutil
                shutil.copy2(package_binary, executable_path)
                
                # Make executable (Unix systems)
                if sys.platform != "win32":
                    executable_path.chmod(executable_path.stat().st_mode | stat.S_IEXEC)
                
                logger.info(f"Extracted package binary to: {executable_path}")
        
        if not executable_path or not executable_path.exists():
            raise Exception("No pre-built executable found")
        
        logger.info(f"Launching executable: {executable_path}")
        
        # Launch the executable
        if self.test_mode:
            self.tauri_process = subprocess.Popen(
                [str(executable_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )
            
            # Wait a bit for the app to start
            await asyncio.sleep(3)
            
            if self.tauri_process.poll() is not None:
                # Process ended, check for errors
                stdout, stderr = self.tauri_process.communicate()
                error_msg = stderr.decode() if stderr else "Unknown error"
                raise Exception(f"Pre-built executable failed: {error_msg}")
                
            logger.info("Pre-built desktop application launched successfully")
        else:
            # For production, run directly
            subprocess.run([str(executable_path)])
    
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
                logger.debug("Tauri configuration not found")
                return False
            
            if not (tauri_dir / "Cargo.toml").exists():
                logger.debug("Cargo.toml not found")
                return False
            
            # Check for pre-built executable first
            if self._has_prebuilt_executable():
                logger.info("Found pre-built desktop executable")
                return True
            
            # Check if Rust/Cargo is available for development build
            try:
                subprocess.run(["cargo", "--version"], 
                             check=True, capture_output=True)
                logger.info("Rust toolchain available for building desktop app")
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                logger.debug("Rust toolchain not available")
                return False
            
        except Exception as e:
            logger.debug(f"Desktop availability check failed: {e}")
            return False
    
    def _has_prebuilt_executable(self) -> bool:
        """Check if pre-built executable exists."""
        try:
            # First check in development build location
            tauri_dir = Path(__file__).parent.parent.parent / "src-tauri"
            target_dir = tauri_dir / "target" / "release"
            
            executable_name = self._get_executable_name()
            executable_path = target_dir / executable_name
            
            if executable_path.exists() and executable_path.is_file():
                logger.debug(f"Found development build: {executable_path}")
                return True
            
            # Check in package binaries directory
            package_binary = self._get_package_binary_path()
            if package_binary and package_binary.exists():
                logger.debug(f"Found package binary: {package_binary}")
                return True
            
            logger.debug("No pre-built executable found")
            return False
        except Exception as e:
            logger.debug(f"Error checking for pre-built executable: {e}")
            return False
    
    def _get_package_binary_path(self) -> Optional[Path]:
        """Get path to packaged binary for current platform."""
        try:
            import platform
            
            # Get current platform info
            current_platform = platform.system().lower()
            current_arch = platform.machine().lower()
            
            # Normalize architecture names
            if current_arch in ['amd64', 'x86_64']:
                current_arch = 'x86_64'
            elif current_arch in ['arm64', 'aarch64']:
                current_arch = 'arm64'
            
            # Look for binaries directory in package
            binaries_dir = Path(__file__).parent / "desktop_binaries"
            if not binaries_dir.exists():
                return None
            
            # Look for platform-specific executable
            executable_name = self._get_executable_name()
            binary_pattern = f"{executable_name}.{current_platform}-{current_arch}"
            
            binary_path = binaries_dir / binary_pattern
            if binary_path.exists():
                return binary_path
            
            # Fallback: look for any binary with the base name
            for binary_file in binaries_dir.glob(f"{executable_name}.*"):
                if current_platform in binary_file.name:
                    return binary_file
            
            return None
            
        except Exception as e:
            logger.debug(f"Error finding package binary: {e}")
            return None


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
        # Provide detailed error message and solutions
        tauri_dir = Path(__file__).parent.parent.parent / "src-tauri"
        
        error_msg = (
            "Desktop application not available.\n\n"
            "Solutions:\n"
            "1. 🌐 Use Web UI instead: mcp-sqlserver-filesystem test --web\n"
            "2. 🔧 Install Rust toolchain:\n"
            "   - Download and install Rust: https://rustup.rs/\n"
            "   - Install Tauri CLI: cargo install tauri-cli\n"
            "   - Then retry: mcp-sqlserver-filesystem test --desktop\n\n"
            "3. 📦 For developers - Build desktop app:\n"
            "   - python scripts/build_desktop.py install-deps\n"
            "   - python scripts/build_desktop.py build-desktop-release\n\n"
            "Note: The Web UI provides the same functionality without requiring Rust."
        )
        
        logger.error(error_msg)
        raise Exception(error_msg)
    
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