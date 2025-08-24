"""Configuration management for MCP SQL Server Filesystem server."""

import os
from pathlib import Path
from typing import Dict, List, Optional, Set
from pydantic import BaseModel, Field, validator
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class DatabaseConfig(BaseModel):
    """SQL Server database configuration."""

    server: str = Field(..., description="SQL Server hostname or IP address")
    database: str = Field(..., description="Database name")
    username: Optional[str] = Field(None, description="Username for SQL Server authentication")
    password: Optional[str] = Field(None, description="Password for SQL Server authentication")
    use_windows_auth: bool = Field(True, description="Use Windows Authentication")
    port: int = Field(1433, description="SQL Server port")
    driver: str = Field("ODBC Driver 17 for SQL Server", description="ODBC driver name")
    connection_timeout: int = Field(30, description="Connection timeout in seconds")
    command_timeout: int = Field(30, description="Command timeout in seconds")
    pool_size: int = Field(5, description="Connection pool size")
    max_overflow: int = Field(10, description="Maximum overflow connections")

    # 新增的连接参数
    trust_server_certificate: bool = Field(True, description="Trust server certificate (TrustServerCertificate)")
    encrypt: bool = Field(False, description="Enable encryption (Encrypt)")
    multiple_active_result_sets: bool = Field(True, description="Enable multiple active result sets (MultipleActiveResultSets)")
    application_name: str = Field("MCP-SQLServer-Filesystem", description="Application name for connection tracking")
    
    @validator('port')
    def validate_port(cls, v):
        if not 1 <= v <= 65535:
            raise ValueError('Port must be between 1 and 65535')
        return v
    
    @property
    def connection_string(self) -> str:
        """Generate SQL Server connection string with enhanced parameters."""
        # 基础连接参数
        base_params = [
            f"DRIVER={{{self.driver}}}",
            f"SERVER={self.server},{self.port}",
            f"DATABASE={self.database}",
            f"Connection Timeout={self.connection_timeout}",
        ]

        # 认证参数
        if self.use_windows_auth:
            base_params.append("Trusted_Connection=yes")
        else:
            base_params.extend([
                f"UID={self.username}",
                f"PWD={self.password}",
            ])

        # 增强的连接参数
        enhanced_params = [
            f"TrustServerCertificate={'yes' if self.trust_server_certificate else 'no'}",
            f"Encrypt={'yes' if self.encrypt else 'no'}",
            f"MultipleActiveResultSets={'yes' if self.multiple_active_result_sets else 'no'}",
            f"Application Name={self.application_name}",
        ]

        # 合并所有参数
        all_params = base_params + enhanced_params
        return ";".join(all_params) + ";"


class FilesystemConfig(BaseModel):
    """Filesystem access configuration."""

    allowed_paths: List[str] = Field(default_factory=list, description="List of allowed base paths (empty = allow all)")
    blocked_paths: List[str] = Field(default_factory=list, description="List of blocked paths (empty = block none)")
    max_file_size: int = Field(1024 * 1024 * 1024, description="Maximum file size in bytes (1GB - increased for full access)")
    allowed_extensions: Set[str] = Field(default_factory=set, description="Allowed file extensions (empty = allow all)")
    blocked_extensions: Set[str] = Field(
        default_factory=set,
        description="Blocked file extensions (empty = block none - full access)"
    )
    enable_write: bool = Field(True, description="Enable write operations")
    enable_delete: bool = Field(True, description="Enable delete operations (enabled for full access)")
    
    @validator('allowed_paths', 'blocked_paths')
    def validate_paths(cls, v):
        """Validate and normalize paths."""
        normalized_paths = []
        for path in v:
            try:
                normalized_path = str(Path(path).resolve())
                normalized_paths.append(normalized_path)
            except Exception as e:
                raise ValueError(f"Invalid path '{path}': {e}")
        return normalized_paths
    
    @validator('max_file_size')
    def validate_file_size(cls, v):
        if v <= 0:
            raise ValueError('Max file size must be positive')
        return v


class SecurityConfig(BaseModel):
    """Security configuration."""

    enable_sql_injection_protection: bool = Field(False, description="Enable SQL injection protection (disabled for full access)")
    allowed_sql_keywords: Set[str] = Field(
        default_factory=set,
        description="Allowed SQL keywords (empty = allow all)"
    )
    blocked_sql_keywords: Set[str] = Field(
        default_factory=set,
        description="Blocked SQL keywords (empty = allow all)"
    )
    max_query_length: int = Field(100000, description="Maximum SQL query length (increased for complex queries)")
    enable_query_logging: bool = Field(True, description="Enable query logging")
    log_sensitive_data: bool = Field(True, description="Log sensitive data for debugging (enabled for full access)")


class ServerConfig(BaseModel):
    """MCP server configuration."""
    
    name: str = Field("mcp-sqlserver-filesystem", description="Server name")
    version: str = Field("0.1.0", description="Server version")
    debug: bool = Field(False, description="Enable debug mode")
    log_level: str = Field("INFO", description="Logging level")
    log_file: Optional[str] = Field(None, description="Log file path")
    
    @validator('log_level')
    def validate_log_level(cls, v):
        valid_levels = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}
        if v.upper() not in valid_levels:
            raise ValueError(f'Log level must be one of: {valid_levels}')
        return v.upper()


class Config(BaseModel):
    """Main configuration class."""
    
    database: DatabaseConfig
    filesystem: FilesystemConfig = Field(default_factory=FilesystemConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    server: ServerConfig = Field(default_factory=ServerConfig)
    
    @classmethod
    def from_env(cls) -> 'Config':
        """Create configuration from environment variables."""
        # Database configuration
        db_config = DatabaseConfig(
            server=os.getenv('DB_SERVER', 'localhost'),
            database=os.getenv('DB_DATABASE', 'master'),
            username=os.getenv('DB_USERNAME'),
            password=os.getenv('DB_PASSWORD'),
            use_windows_auth=os.getenv('DB_USE_WINDOWS_AUTH', 'true').lower() == 'true',
            port=int(os.getenv('DB_PORT', '1433')),
            driver=os.getenv('DB_DRIVER', 'ODBC Driver 17 for SQL Server'),
            connection_timeout=int(os.getenv('DB_CONNECTION_TIMEOUT', '30')),
            command_timeout=int(os.getenv('DB_COMMAND_TIMEOUT', '30')),
            pool_size=int(os.getenv('DB_POOL_SIZE', '5')),
            max_overflow=int(os.getenv('DB_MAX_OVERFLOW', '10')),

            # 新增的连接参数
            trust_server_certificate=os.getenv('DB_TRUST_SERVER_CERTIFICATE', 'true').lower() == 'true',
            encrypt=os.getenv('DB_ENCRYPT', 'false').lower() == 'true',
            multiple_active_result_sets=os.getenv('DB_MULTIPLE_ACTIVE_RESULT_SETS', 'true').lower() == 'true',
            application_name=os.getenv('DB_APPLICATION_NAME', 'MCP-SQLServer-Filesystem'),
        )
        
        # Filesystem configuration
        allowed_paths = os.getenv('FS_ALLOWED_PATHS', '').split(',') if os.getenv('FS_ALLOWED_PATHS') else []
        blocked_paths = os.getenv('FS_BLOCKED_PATHS', '').split(',') if os.getenv('FS_BLOCKED_PATHS') else []
        allowed_extensions = set(os.getenv('FS_ALLOWED_EXTENSIONS', '').split(',')) if os.getenv('FS_ALLOWED_EXTENSIONS') else set()
        
        fs_config = FilesystemConfig(
            allowed_paths=[p.strip() for p in allowed_paths if p.strip()],
            blocked_paths=[p.strip() for p in blocked_paths if p.strip()],
            max_file_size=int(os.getenv('FS_MAX_FILE_SIZE', str(1024 * 1024 * 1024))),  # 1GB default for full access
            allowed_extensions=allowed_extensions,
            enable_write=os.getenv('FS_ENABLE_WRITE', 'true').lower() == 'true',
            enable_delete=os.getenv('FS_ENABLE_DELETE', 'true').lower() == 'true',  # Enabled by default for full access
        )
        
        # Security configuration - defaults to full access
        security_config = SecurityConfig(
            enable_sql_injection_protection=os.getenv('SEC_ENABLE_SQL_PROTECTION', 'false').lower() == 'true',
            max_query_length=int(os.getenv('SEC_MAX_QUERY_LENGTH', '100000')),
            enable_query_logging=os.getenv('SEC_ENABLE_QUERY_LOGGING', 'true').lower() == 'true',
            log_sensitive_data=os.getenv('SEC_LOG_SENSITIVE_DATA', 'true').lower() == 'true',
        )
        
        # Server configuration
        server_config = ServerConfig(
            debug=os.getenv('SERVER_DEBUG', 'false').lower() == 'true',
            log_level=os.getenv('SERVER_LOG_LEVEL', 'INFO'),
            log_file=os.getenv('SERVER_LOG_FILE'),
        )
        
        return cls(
            database=db_config,
            filesystem=fs_config,
            security=security_config,
            server=server_config,
        )


# Global configuration instance
config = Config.from_env()
