"""MCP Server for SQL Server and Filesystem Access."""

import asyncio
import logging
import sys
from typing import Any, Dict, List, Optional, Sequence
import json

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel,
)

from .config import config
from .database import db_manager, SQLSecurityError, DatabaseConnectionError
from .filesystem import fs_manager, FilesystemSecurityError, FilesystemOperationError

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.server.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        *([logging.FileHandler(config.server.log_file)] if config.server.log_file else [])
    ]
)

logger = logging.getLogger(__name__)

# Create MCP server instance
server = Server("mcp-sqlserver-filesystem")


@server.list_resources()
async def handle_list_resources() -> List[Resource]:
    """List available resources."""
    resources = [
        Resource(
            uri="config://database",
            name="Database Configuration",
            description="Current database configuration settings",
            mimeType="application/json",
        ),
        Resource(
            uri="config://filesystem",
            name="Filesystem Configuration", 
            description="Current filesystem configuration settings",
            mimeType="application/json",
        ),
        Resource(
            uri="status://database",
            name="Database Status",
            description="Current database connection status",
            mimeType="application/json",
        ),
    ]
    
    return resources


@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read a specific resource."""
    if uri == "config://database":
        return json.dumps({
            "server": config.database.server,
            "database": config.database.database,
            "port": config.database.port,
            "use_windows_auth": config.database.use_windows_auth,
            "connection_timeout": config.database.connection_timeout,
            "command_timeout": config.database.command_timeout,
            "pool_size": config.database.pool_size,
        }, indent=2)
    
    elif uri == "config://filesystem":
        return json.dumps({
            "allowed_paths": config.filesystem.allowed_paths,
            "blocked_paths": config.filesystem.blocked_paths,
            "max_file_size": config.filesystem.max_file_size,
            "allowed_extensions": list(config.filesystem.allowed_extensions),
            "blocked_extensions": list(config.filesystem.blocked_extensions),
            "enable_write": config.filesystem.enable_write,
            "enable_delete": config.filesystem.enable_delete,
        }, indent=2)
    
    elif uri == "status://database":
        try:
            is_connected = db_manager.test_connection()
            return json.dumps({
                "connected": is_connected,
                "status": "Connected" if is_connected else "Disconnected",
                "timestamp": asyncio.get_event_loop().time(),
            }, indent=2)
        except Exception as e:
            return json.dumps({
                "connected": False,
                "status": f"Error: {str(e)}",
                "timestamp": asyncio.get_event_loop().time(),
            }, indent=2)
    
    else:
        raise ValueError(f"Unknown resource: {uri}")


@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available tools."""
    tools = [
        # Database tools
        Tool(
            name="sql_query",
            description="Execute SQL SELECT query and display results in UI window",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "SQL SELECT query to execute"
                    },
                    "parameters": {
                        "type": "object",
                        "description": "Query parameters (optional)",
                        "additionalProperties": True
                    },
                    "show_ui": {
                        "type": "boolean",
                        "description": "Show results in UI window",
                        "default": True
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="sql_execute",
            description="Execute SQL INSERT/UPDATE/DELETE query",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "SQL query to execute"
                    },
                    "parameters": {
                        "type": "object",
                        "description": "Query parameters (optional)",
                        "additionalProperties": True
                    },
                    "confirm_ui": {
                        "type": "boolean",
                        "description": "Show confirmation dialog in UI",
                        "default": True
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_table_schema",
            description="Get table schema information and display in UI",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Name of the table"
                    },
                    "schema_name": {
                        "type": "string",
                        "description": "Schema name (default: dbo)",
                        "default": "dbo"
                    },
                    "show_ui": {
                        "type": "boolean",
                        "description": "Show schema in UI window",
                        "default": True
                    }
                },
                "required": ["table_name"]
            }
        ),
        Tool(
            name="list_tables",
            description="List all tables in database and display in UI",
            inputSchema={
                "type": "object",
                "properties": {
                    "schema_name": {
                        "type": "string",
                        "description": "Schema name (default: dbo)",
                        "default": "dbo"
                    },
                    "show_ui": {
                        "type": "boolean",
                        "description": "Show tables in UI window",
                        "default": True
                    }
                }
            }
        ),
        
        # Filesystem tools
        Tool(
            name="read_file",
            description="Read file content and optionally display in UI",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to read"
                    },
                    "encoding": {
                        "type": "string",
                        "description": "File encoding (default: utf-8)",
                        "default": "utf-8"
                    },
                    "show_ui": {
                        "type": "boolean",
                        "description": "Show content in UI window",
                        "default": False
                    }
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="write_file",
            description="Write content to file with optional UI confirmation",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to write"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write to file"
                    },
                    "encoding": {
                        "type": "string",
                        "description": "File encoding (default: utf-8)",
                        "default": "utf-8"
                    },
                    "create_dirs": {
                        "type": "boolean",
                        "description": "Create parent directories if needed",
                        "default": True
                    },
                    "confirm_ui": {
                        "type": "boolean",
                        "description": "Show confirmation dialog in UI",
                        "default": True
                    }
                },
                "required": ["file_path", "content"]
            }
        ),
        Tool(
            name="list_directory",
            description="List directory contents and display in UI",
            inputSchema={
                "type": "object",
                "properties": {
                    "dir_path": {
                        "type": "string",
                        "description": "Path to the directory to list"
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": "List recursively",
                        "default": False
                    },
                    "show_ui": {
                        "type": "boolean",
                        "description": "Show directory listing in UI window",
                        "default": True
                    }
                },
                "required": ["dir_path"]
            }
        ),
    ]
    
    return tools


@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls."""
    try:
        if name == "sql_query":
            return await handle_sql_query(arguments)
        elif name == "sql_execute":
            return await handle_sql_execute(arguments)
        elif name == "get_table_schema":
            return await handle_get_table_schema(arguments)
        elif name == "list_tables":
            return await handle_list_tables(arguments)
        elif name == "read_file":
            return await handle_read_file(arguments)
        elif name == "write_file":
            return await handle_write_file(arguments)
        elif name == "list_directory":
            return await handle_list_directory(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    except Exception as e:
        logger.error(f"Tool {name} failed: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


# Tool handler functions
async def handle_sql_query(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle SQL query execution."""
    query = arguments.get("query", "")
    parameters = arguments.get("parameters", {})
    show_ui = arguments.get("show_ui", True)

    try:
        results = db_manager.execute_query(query, parameters)

        # Format results for display
        if not results:
            response_text = "Query executed successfully. No results returned."
        else:
            # Create a formatted table
            if len(results) == 1:
                response_text = f"Query returned 1 row:\n\n"
            else:
                response_text = f"Query returned {len(results)} rows:\n\n"

            # Add column headers
            if results:
                headers = list(results[0].keys())
                response_text += " | ".join(headers) + "\n"
                response_text += "-" * (len(" | ".join(headers))) + "\n"

                # Add data rows (limit to first 100 rows for display)
                display_results = results[:100]
                for row in display_results:
                    row_values = [str(row.get(header, "")) for header in headers]
                    response_text += " | ".join(row_values) + "\n"

                if len(results) > 100:
                    response_text += f"\n... and {len(results) - 100} more rows"

        # Show in UI if requested
        if show_ui:
            try:
                await show_query_results_in_ui(query, results)
            except Exception as ui_error:
                logger.warning(f"Failed to show results in UI: {ui_error}")
                response_text += f"\n\nNote: Could not display in UI window: {ui_error}"

        return [TextContent(type="text", text=response_text)]

    except Exception as e:
        error_msg = f"SQL query failed: {str(e)}"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]


async def handle_sql_execute(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle SQL execution (INSERT, UPDATE, DELETE)."""
    query = arguments.get("query", "")
    parameters = arguments.get("parameters", {})
    confirm = arguments.get("confirm", False)

    try:
        # Check if confirmation is required for dangerous operations
        dangerous_keywords = ["DELETE", "DROP", "TRUNCATE", "ALTER"]
        query_upper = query.upper().strip()

        is_dangerous = any(keyword in query_upper for keyword in dangerous_keywords)

        if is_dangerous and not confirm:
            return [TextContent(
                type="text",
                text=f"This operation requires confirmation. Please add 'confirm': true to execute: {query}"
            )]

        affected_rows = db_manager.execute_non_query(query, parameters)

        response_text = f"SQL executed successfully. {affected_rows} rows affected."

        return [TextContent(type="text", text=response_text)]

    except Exception as e:
        error_msg = f"SQL execution failed: {str(e)}"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]


async def handle_get_table_schema(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle table schema retrieval."""
    table_name = arguments.get("table_name", "")
    schema_name = arguments.get("schema_name", "dbo")
    show_ui = arguments.get("show_ui", True)

    try:
        schema_info = db_manager.get_table_schema(table_name, schema_name)

        if not schema_info:
            response_text = f"Table '{schema_name}.{table_name}' not found or has no columns."
        else:
            response_text = f"Schema for table '{schema_name}.{table_name}':\n\n"
            response_text += "Column Name | Data Type | Nullable | Default | Key\n"
            response_text += "-" * 50 + "\n"

            for col in schema_info:
                nullable = "YES" if col.get("is_nullable", True) else "NO"
                default = col.get("column_default", "") or ""
                key_type = ""
                if col.get("is_primary_key"):
                    key_type = "PK"
                elif col.get("is_foreign_key"):
                    key_type = "FK"

                response_text += f"{col['column_name']} | {col['data_type']} | {nullable} | {default} | {key_type}\n"

        # Show in UI if requested
        if show_ui:
            try:
                await show_table_schema_in_ui(table_name, schema_name, schema_info)
            except Exception as ui_error:
                logger.warning(f"Failed to show schema in UI: {ui_error}")
                response_text += f"\n\nNote: Could not display in UI window: {ui_error}"

        return [TextContent(type="text", text=response_text)]

    except Exception as e:
        error_msg = f"Failed to get table schema: {str(e)}"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]


async def handle_list_tables(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle database tables listing."""
    schema_name = arguments.get("schema_name", "dbo")
    show_ui = arguments.get("show_ui", True)

    try:
        tables = db_manager.get_database_tables(schema_name)

        if not tables:
            response_text = f"No tables found in schema '{schema_name}'."
        else:
            response_text = f"Tables in schema '{schema_name}' ({len(tables)} found):\n\n"
            for i, table in enumerate(tables, 1):
                response_text += f"{i}. {table}\n"

        # Show in UI if requested
        if show_ui:
            try:
                await show_tables_list_in_ui(schema_name, tables)
            except Exception as ui_error:
                logger.warning(f"Failed to show tables in UI: {ui_error}")
                response_text += f"\n\nNote: Could not display in UI window: {ui_error}"

        return [TextContent(type="text", text=response_text)]

    except Exception as e:
        error_msg = f"Failed to list tables: {str(e)}"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]


async def handle_read_file(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle file reading."""
    file_path = arguments.get("file_path", "")
    encoding = arguments.get("encoding", "utf-8")
    show_ui = arguments.get("show_ui", False)

    try:
        content = fs_manager.read_file(file_path, encoding)

        # Limit content display for very large files
        if len(content) > 10000:
            preview_content = content[:10000] + f"\n\n... (file truncated, showing first 10000 characters of {len(content)} total)"
            response_text = f"File content from '{file_path}':\n\n{preview_content}"
        else:
            response_text = f"File content from '{file_path}':\n\n{content}"

        # Show in UI if requested
        if show_ui:
            try:
                await show_file_content_in_ui(file_path, content)
            except Exception as ui_error:
                logger.warning(f"Failed to show file content in UI: {ui_error}")
                response_text += f"\n\nNote: Could not display in UI window: {ui_error}"

        return [TextContent(type="text", text=response_text)]

    except Exception as e:
        error_msg = f"Failed to read file: {str(e)}"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]


async def handle_write_file(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle file writing."""
    file_path = arguments.get("file_path", "")
    content = arguments.get("content", "")
    encoding = arguments.get("encoding", "utf-8")
    create_dirs = arguments.get("create_dirs", True)
    confirm = arguments.get("confirm", False)

    try:
        # Check if confirmation is required for overwriting existing files
        from pathlib import Path
        path = Path(file_path)

        if path.exists() and not confirm:
            return [TextContent(
                type="text",
                text=f"File '{file_path}' already exists. Please add 'confirm': true to overwrite."
            )]

        # Show confirmation dialog in UI if available
        if not confirm:
            try:
                confirmed = await show_file_write_confirmation_ui(file_path, len(content))
                if not confirmed:
                    return [TextContent(type="text", text="File write operation cancelled by user.")]
            except Exception as ui_error:
                logger.warning(f"Failed to show confirmation dialog: {ui_error}")
                # Continue without UI confirmation

        fs_manager.write_file(file_path, content, encoding, create_dirs)

        response_text = f"File written successfully: '{file_path}' ({len(content)} characters)"

        return [TextContent(type="text", text=response_text)]

    except Exception as e:
        error_msg = f"Failed to write file: {str(e)}"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]


async def handle_list_directory(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle directory listing."""
    dir_path = arguments.get("dir_path", "")
    recursive = arguments.get("recursive", False)
    show_ui = arguments.get("show_ui", True)

    try:
        items = fs_manager.list_directory(dir_path, recursive)

        if not items:
            response_text = f"Directory '{dir_path}' is empty or no accessible items found."
        else:
            response_text = f"Directory listing for '{dir_path}' ({len(items)} items):\n\n"
            response_text += "Type | Name | Size | Modified\n"
            response_text += "-" * 50 + "\n"

            for item in items:
                item_type = "DIR" if item.get("is_directory") else "FILE"
                name = item.get("name", "")
                size = item.get("size", 0) if not item.get("is_directory") else ""
                modified = item.get("modified", "")

                response_text += f"{item_type} | {name} | {size} | {modified}\n"

        # Show in UI if requested
        if show_ui:
            try:
                await show_directory_listing_in_ui(dir_path, items, recursive)
            except Exception as ui_error:
                logger.warning(f"Failed to show directory listing in UI: {ui_error}")
                response_text += f"\n\nNote: Could not display in UI window: {ui_error}"

        return [TextContent(type="text", text=response_text)]

    except Exception as e:
        error_msg = f"Failed to list directory: {str(e)}"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]


# UI interaction functions (will be implemented with Web UI)
async def show_query_results_in_ui(query: str, results: List[Dict[str, Any]]) -> None:
    """Show SQL query results in UI window."""
    try:
        # Import Web UI manager
        from .web.main import get_web_ui_manager

        manager = get_web_ui_manager()
        if manager and manager.is_running():
            await manager.show_query_results(query, results)
        else:
            logger.debug("Web UI not available for showing query results")
    except ImportError:
        logger.debug("Web UI module not available")
    except Exception as e:
        logger.warning(f"Failed to show query results in UI: {e}")


async def show_table_schema_in_ui(table_name: str, schema_name: str, schema_info: List[Dict[str, Any]]) -> None:
    """Show table schema in UI window."""
    try:
        from .web.main import get_web_ui_manager

        manager = get_web_ui_manager()
        if manager and manager.is_running():
            await manager.show_table_schema(table_name, schema_name, schema_info)
        else:
            logger.debug("Web UI not available for showing table schema")
    except ImportError:
        logger.debug("Web UI module not available")
    except Exception as e:
        logger.warning(f"Failed to show table schema in UI: {e}")


async def show_tables_list_in_ui(schema_name: str, tables: List[str]) -> None:
    """Show tables list in UI window."""
    try:
        from .web.main import get_web_ui_manager

        manager = get_web_ui_manager()
        if manager and manager.is_running():
            await manager.show_tables_list(schema_name, tables)
        else:
            logger.debug("Web UI not available for showing tables list")
    except ImportError:
        logger.debug("Web UI module not available")
    except Exception as e:
        logger.warning(f"Failed to show tables list in UI: {e}")


async def show_file_content_in_ui(file_path: str, content: str) -> None:
    """Show file content in UI window."""
    try:
        from .web.main import get_web_ui_manager

        manager = get_web_ui_manager()
        if manager and manager.is_running():
            await manager.show_file_content(file_path, content)
        else:
            logger.debug("Web UI not available for showing file content")
    except ImportError:
        logger.debug("Web UI module not available")
    except Exception as e:
        logger.warning(f"Failed to show file content in UI: {e}")


async def show_file_write_confirmation_ui(file_path: str, content_length: int) -> bool:
    """Show file write confirmation dialog in UI."""
    try:
        from .web.main import get_web_ui_manager

        manager = get_web_ui_manager()
        if manager and manager.is_running():
            return await manager.show_file_write_confirmation(file_path, content_length)
        else:
            logger.debug("Web UI not available for file write confirmation")
            return True  # Default to allow if UI not available
    except ImportError:
        logger.debug("Web UI module not available")
        return True
    except Exception as e:
        logger.warning(f"Failed to show file write confirmation in UI: {e}")
        return True


async def show_directory_listing_in_ui(dir_path: str, items: List[Dict[str, Any]], recursive: bool) -> None:
    """Show directory listing in UI window."""
    try:
        from .web.main import get_web_ui_manager

        manager = get_web_ui_manager()
        if manager and manager.is_running():
            await manager.show_directory_listing(dir_path, items, recursive)
        else:
            logger.debug("Web UI not available for showing directory listing")
    except ImportError:
        logger.debug("Web UI module not available")
    except Exception as e:
        logger.warning(f"Failed to show directory listing in UI: {e}")


async def main():
    """Main entry point for the MCP server."""
    logger.info("Starting MCP SQL Server Filesystem server...")

    # Initialize Web UI manager if available
    try:
        from .web.main import get_web_ui_manager
        ui_manager = get_web_ui_manager()
        logger.info("Web UI manager initialized")
    except ImportError:
        logger.info("Web UI not available - running in console mode only")
    except Exception as e:
        logger.warning(f"Failed to initialize Web UI: {e}")

    # Test database connection on startup
    try:
        if db_manager.test_connection():
            logger.info("Database connection test successful")
        else:
            logger.warning("Database connection test failed")
    except Exception as e:
        logger.error(f"Database connection test error: {e}")

    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="mcp-sqlserver-filesystem",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities={}
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
