"""Filesystem operations for MCP server."""

import logging
import os
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import aiofiles
import asyncio
from datetime import datetime

from .config import config

logger = logging.getLogger(__name__)


class FilesystemSecurityError(Exception):
    """Raised when a filesystem operation fails security checks."""
    pass


class FilesystemOperationError(Exception):
    """Raised when a filesystem operation fails."""
    pass


class FilesystemManager:
    """Manages filesystem operations with security controls."""
    
    def __init__(self):
        self._validate_configuration()
    
    def _validate_configuration(self) -> None:
        """Validate filesystem configuration."""
        # Ensure allowed paths exist and are accessible
        for path_str in config.filesystem.allowed_paths:
            path = Path(path_str)
            if not path.exists():
                logger.warning(f"Allowed path does not exist: {path}")
            elif not path.is_dir():
                logger.warning(f"Allowed path is not a directory: {path}")
    
    def _is_path_allowed(self, file_path: Union[str, Path]) -> bool:
        """Check if a path is allowed based on configuration."""
        file_path = Path(file_path).resolve()

        # Check if path is in blocked paths (only if any are configured)
        if config.filesystem.blocked_paths:
            for blocked_path_str in config.filesystem.blocked_paths:
                blocked_path = Path(blocked_path_str).resolve()
                try:
                    file_path.relative_to(blocked_path)
                    logger.debug(f"Path blocked: {file_path} is under {blocked_path}")
                    return False  # Path is under a blocked directory
                except ValueError:
                    continue  # Path is not under this blocked directory

        # If no allowed paths specified, allow all (full access mode)
        if not config.filesystem.allowed_paths:
            logger.debug(f"Path allowed: {file_path} (full access mode - no restrictions)")
            return True

        # Check if path is under any allowed path
        for allowed_path_str in config.filesystem.allowed_paths:
            allowed_path = Path(allowed_path_str).resolve()
            try:
                file_path.relative_to(allowed_path)
                logger.debug(f"Path allowed: {file_path} is under {allowed_path}")
                return True  # Path is under an allowed directory
            except ValueError:
                continue  # Path is not under this allowed directory

        logger.debug(f"Path not allowed: {file_path} is not under any allowed directory")
        return False  # Path is not under any allowed directory
    
    def _is_extension_allowed(self, file_path: Union[str, Path]) -> bool:
        """Check if file extension is allowed."""
        file_path = Path(file_path)
        extension = file_path.suffix.lower()

        # Check blocked extensions (only if any are configured)
        if config.filesystem.blocked_extensions and extension in config.filesystem.blocked_extensions:
            logger.debug(f"Extension blocked: {extension}")
            return False

        # If allowed extensions specified, check if extension is in the list
        if config.filesystem.allowed_extensions:
            allowed = extension in config.filesystem.allowed_extensions
            logger.debug(f"Extension {'allowed' if allowed else 'not allowed'}: {extension}")
            return allowed

        # No restrictions configured - allow all extensions (full access mode)
        logger.debug(f"Extension allowed: {extension} (full access mode - no restrictions)")
        return True
    
    def _validate_file_operation(self, file_path: Union[str, Path], operation: str) -> None:
        """Validate file operation for security."""
        file_path = Path(file_path)
        
        # Check if path is allowed
        if not self._is_path_allowed(file_path):
            raise FilesystemSecurityError(f"Path not allowed: {file_path}")
        
        # Check file extension
        if not self._is_extension_allowed(file_path):
            raise FilesystemSecurityError(f"File extension not allowed: {file_path.suffix}")
        
        # Check write operations
        if operation in ['write', 'create', 'move', 'copy'] and not config.filesystem.enable_write:
            raise FilesystemSecurityError("Write operations are disabled")
        
        # Check delete operations
        if operation == 'delete' and not config.filesystem.enable_delete:
            raise FilesystemSecurityError("Delete operations are disabled")
        
        logger.debug(f"File operation validated: {operation} on {file_path}")
    
    def read_file(self, file_path: Union[str, Path], encoding: str = 'utf-8') -> str:
        """Read file content."""
        file_path = Path(file_path)
        self._validate_file_operation(file_path, 'read')
        
        try:
            if not file_path.exists():
                raise FilesystemOperationError(f"File does not exist: {file_path}")
            
            if not file_path.is_file():
                raise FilesystemOperationError(f"Path is not a file: {file_path}")
            
            # Check file size
            file_size = file_path.stat().st_size
            if file_size > config.filesystem.max_file_size:
                raise FilesystemOperationError(
                    f"File too large: {file_size} bytes (max: {config.filesystem.max_file_size})"
                )
            
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            
            logger.info(f"File read successfully: {file_path} ({file_size} bytes)")
            return content
            
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            raise FilesystemOperationError(f"Failed to read file: {e}")
    
    def write_file(self, file_path: Union[str, Path], content: str, encoding: str = 'utf-8', create_dirs: bool = True) -> None:
        """Write content to file."""
        file_path = Path(file_path)
        self._validate_file_operation(file_path, 'write')
        
        try:
            # Check content size
            content_size = len(content.encode(encoding))
            if content_size > config.filesystem.max_file_size:
                raise FilesystemOperationError(
                    f"Content too large: {content_size} bytes (max: {config.filesystem.max_file_size})"
                )
            
            # Create parent directories if needed
            if create_dirs:
                file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(content)
            
            logger.info(f"File written successfully: {file_path} ({content_size} bytes)")
            
        except Exception as e:
            logger.error(f"Failed to write file {file_path}: {e}")
            raise FilesystemOperationError(f"Failed to write file: {e}")
    
    def list_directory(self, dir_path: Union[str, Path], recursive: bool = False) -> List[Dict[str, Any]]:
        """List directory contents."""
        dir_path = Path(dir_path)
        self._validate_file_operation(dir_path, 'read')
        
        try:
            if not dir_path.exists():
                raise FilesystemOperationError(f"Directory does not exist: {dir_path}")
            
            if not dir_path.is_dir():
                raise FilesystemOperationError(f"Path is not a directory: {dir_path}")
            
            items = []
            
            if recursive:
                for item in dir_path.rglob('*'):
                    if self._is_path_allowed(item):
                        items.append(self._get_file_info(item))
            else:
                for item in dir_path.iterdir():
                    if self._is_path_allowed(item):
                        items.append(self._get_file_info(item))
            
            logger.info(f"Directory listed successfully: {dir_path} ({len(items)} items)")
            return items
            
        except Exception as e:
            logger.error(f"Failed to list directory {dir_path}: {e}")
            raise FilesystemOperationError(f"Failed to list directory: {e}")
    
    def _get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """Get file information."""
        try:
            stat = file_path.stat()
            return {
                'name': file_path.name,
                'path': str(file_path),
                'type': 'directory' if file_path.is_dir() else 'file',
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'extension': file_path.suffix.lower() if file_path.is_file() else None,
            }
        except Exception as e:
            logger.warning(f"Failed to get file info for {file_path}: {e}")
            return {
                'name': file_path.name,
                'path': str(file_path),
                'type': 'unknown',
                'error': str(e)
            }
    
    def create_directory(self, dir_path: Union[str, Path], parents: bool = True) -> None:
        """Create directory."""
        dir_path = Path(dir_path)
        self._validate_file_operation(dir_path, 'create')
        
        try:
            dir_path.mkdir(parents=parents, exist_ok=True)
            logger.info(f"Directory created successfully: {dir_path}")
            
        except Exception as e:
            logger.error(f"Failed to create directory {dir_path}: {e}")
            raise FilesystemOperationError(f"Failed to create directory: {e}")
    
    def delete_file(self, file_path: Union[str, Path]) -> None:
        """Delete file."""
        file_path = Path(file_path)
        self._validate_file_operation(file_path, 'delete')
        
        try:
            if not file_path.exists():
                raise FilesystemOperationError(f"File does not exist: {file_path}")
            
            if file_path.is_file():
                file_path.unlink()
                logger.info(f"File deleted successfully: {file_path}")
            else:
                raise FilesystemOperationError(f"Path is not a file: {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to delete file {file_path}: {e}")
            raise FilesystemOperationError(f"Failed to delete file: {e}")


# Global filesystem manager instance
fs_manager = FilesystemManager()
