"""SQL Server database operations for MCP server."""

import logging
import re
from typing import Any, Dict, List, Optional, Tuple, Union
import pyodbc
from sqlalchemy import create_engine, text, MetaData, Table
from sqlalchemy.engine import Engine
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager

from .config import config

logger = logging.getLogger(__name__)


class SQLSecurityError(Exception):
    """Raised when a SQL query fails security checks."""
    pass


class DatabaseConnectionError(Exception):
    """Raised when database connection fails."""
    pass


class SQLServerManager:
    """Manages SQL Server connections and operations."""
    
    def __init__(self):
        self._engine: Optional[Engine] = None
        self._metadata: Optional[MetaData] = None
        self._initialize_engine()
    
    def _initialize_engine(self) -> None:
        """Initialize SQLAlchemy engine with connection pooling."""
        try:
            # Convert pyodbc connection string to SQLAlchemy format
            connection_string = config.database.connection_string
            sqlalchemy_url = f"mssql+pyodbc:///?odbc_connect={connection_string}"
            
            self._engine = create_engine(
                sqlalchemy_url,
                poolclass=QueuePool,
                pool_size=config.database.pool_size,
                max_overflow=config.database.max_overflow,
                pool_pre_ping=True,  # Validate connections before use
                pool_recycle=3600,   # Recycle connections every hour
                echo=config.server.debug,  # Log SQL queries in debug mode
            )
            
            self._metadata = MetaData()
            logger.info("Database engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database engine: {e}")
            raise DatabaseConnectionError(f"Database initialization failed: {e}")
    
    def _validate_sql_query(self, query: str) -> None:
        """Validate SQL query for security issues."""
        # Skip all validation if SQL protection is disabled (full access mode)
        if not config.security.enable_sql_injection_protection:
            logger.debug("SQL security validation skipped - full access mode enabled")
            return

        # Check query length
        if len(query) > config.security.max_query_length:
            raise SQLSecurityError(f"Query exceeds maximum length of {config.security.max_query_length}")

        # Convert to uppercase for keyword checking
        query_upper = query.upper()

        # Check for blocked keywords (only if any are configured)
        if config.security.blocked_sql_keywords:
            for keyword in config.security.blocked_sql_keywords:
                if re.search(r'\b' + re.escape(keyword) + r'\b', query_upper):
                    raise SQLSecurityError(f"Blocked SQL keyword detected: {keyword}")
        else:
            logger.debug("No blocked SQL keywords configured - allowing all SQL commands")

        # Skip injection pattern checks if no keywords are blocked (full access mode)
        if not config.security.blocked_sql_keywords:
            logger.debug("SQL injection pattern checks skipped - full access mode")
            return

        # Check for common SQL injection patterns (only when security is enabled)
        injection_patterns = [
            r";\s*(DROP|DELETE|UPDATE|INSERT|CREATE|ALTER|EXEC|EXECUTE)",
            r"UNION\s+SELECT",
            r"--\s*$",
            r"/\*.*\*/",
            r"'\s*(OR|AND)\s*'",
            r"'\s*=\s*'",
        ]

        for pattern in injection_patterns:
            if re.search(pattern, query_upper, re.MULTILINE):
                raise SQLSecurityError(f"Potential SQL injection detected: {pattern}")

        logger.debug("SQL query passed security validation")
    
    @contextmanager
    def get_connection(self):
        """Get a database connection with automatic cleanup."""
        if not self._engine:
            raise DatabaseConnectionError("Database engine not initialized")
        
        connection = None
        try:
            connection = self._engine.connect()
            yield connection
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            if connection:
                connection.rollback()
            raise
        finally:
            if connection:
                connection.close()
    
    def execute_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results."""
        self._validate_sql_query(query)
        
        if config.security.enable_query_logging:
            if config.security.log_sensitive_data:
                logger.info(f"Executing query: {query} with parameters: {parameters}")
            else:
                logger.info(f"Executing query: {query}")
        
        try:
            with self.get_connection() as conn:
                result = conn.execute(text(query), parameters or {})
                
                # Convert result to list of dictionaries
                columns = result.keys()
                rows = []
                for row in result:
                    row_dict = {}
                    for i, value in enumerate(row):
                        row_dict[columns[i]] = value
                    rows.append(row_dict)
                
                logger.info(f"Query executed successfully, returned {len(rows)} rows")
                return rows
                
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
    
    def execute_non_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> int:
        """Execute an INSERT, UPDATE, or DELETE query and return affected rows count."""
        self._validate_sql_query(query)
        
        if config.security.enable_query_logging:
            if config.security.log_sensitive_data:
                logger.info(f"Executing non-query: {query} with parameters: {parameters}")
            else:
                logger.info(f"Executing non-query: {query}")
        
        try:
            with self.get_connection() as conn:
                result = conn.execute(text(query), parameters or {})
                conn.commit()
                
                affected_rows = result.rowcount
                logger.info(f"Non-query executed successfully, affected {affected_rows} rows")
                return affected_rows
                
        except Exception as e:
            logger.error(f"Non-query execution failed: {e}")
            raise
    
    def get_table_schema(self, table_name: str, schema_name: str = "dbo") -> Dict[str, Any]:
        """Get table schema information."""
        query = """
        SELECT 
            c.COLUMN_NAME,
            c.DATA_TYPE,
            c.IS_NULLABLE,
            c.COLUMN_DEFAULT,
            c.CHARACTER_MAXIMUM_LENGTH,
            c.NUMERIC_PRECISION,
            c.NUMERIC_SCALE,
            CASE WHEN pk.COLUMN_NAME IS NOT NULL THEN 1 ELSE 0 END AS IS_PRIMARY_KEY
        FROM INFORMATION_SCHEMA.COLUMNS c
        LEFT JOIN (
            SELECT ku.TABLE_CATALOG, ku.TABLE_SCHEMA, ku.TABLE_NAME, ku.COLUMN_NAME
            FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS AS tc
            INNER JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE AS ku
                ON tc.CONSTRAINT_TYPE = 'PRIMARY KEY' 
                AND tc.CONSTRAINT_NAME = ku.CONSTRAINT_NAME
        ) pk ON c.TABLE_CATALOG = pk.TABLE_CATALOG
            AND c.TABLE_SCHEMA = pk.TABLE_SCHEMA
            AND c.TABLE_NAME = pk.TABLE_NAME
            AND c.COLUMN_NAME = pk.COLUMN_NAME
        WHERE c.TABLE_NAME = :table_name AND c.TABLE_SCHEMA = :schema_name
        ORDER BY c.ORDINAL_POSITION
        """
        
        try:
            results = self.execute_query(query, {
                'table_name': table_name,
                'schema_name': schema_name
            })
            
            return {
                'table_name': table_name,
                'schema_name': schema_name,
                'columns': results
            }
            
        except Exception as e:
            logger.error(f"Failed to get table schema for {schema_name}.{table_name}: {e}")
            raise
    
    def get_database_tables(self, schema_name: str = "dbo") -> List[str]:
        """Get list of tables in the database."""
        query = """
        SELECT TABLE_NAME 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_TYPE = 'BASE TABLE' AND TABLE_SCHEMA = :schema_name
        ORDER BY TABLE_NAME
        """
        
        try:
            results = self.execute_query(query, {'schema_name': schema_name})
            return [row['TABLE_NAME'] for row in results]
            
        except Exception as e:
            logger.error(f"Failed to get database tables: {e}")
            raise
    
    def test_connection(self) -> bool:
        """Test database connection."""
        try:
            with self.get_connection() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Database connection test successful")
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    def close(self) -> None:
        """Close database engine and all connections."""
        if self._engine:
            self._engine.dispose()
            self._engine = None
            logger.info("Database engine closed")


# Global database manager instance
db_manager = SQLServerManager()
