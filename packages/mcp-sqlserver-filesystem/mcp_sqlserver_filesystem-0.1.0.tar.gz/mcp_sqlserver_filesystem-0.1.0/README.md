# MCP SQL Server Filesystem

🚀 **Enhanced MCP server** for SQL Server database and filesystem access with dual interface support.

## ✨ Features

- **Complete SQL Server Support** - Execute all SQL commands with enhanced connection parameters
- **Full Filesystem Access** - Read/write files with confirmation dialogs
- **Web UI Interface** - Real-time query results display
- **Smart Environment Detection** - Auto-adapts to SSH Remote, WSL, Local environments
- **Enhanced Connection Parameters** - Built-in support for `TrustServerCertificate=true`, `Encrypt=false`, `MultipleActiveResultSets=true`

## 🚀 Quick Start

### Simple Installation

```bash
# Install uv (if not already installed)
pip install uv

# Run directly with uvx
uvx mcp-sqlserver-filesystem@latest
```

### Alternative Installation

```bash
# Install from PyPI
pip install mcp-sqlserver-filesystem

# Or install from GitHub
pip install git+https://github.com/ppengit/mcp-sqlserver-filesystem.git
```

## 🔧 Augment Code Configuration

Add to your Augment Code MCP settings:

```json
{
  "mcpServers": {
    "mcp-sqlserver-filesystem": {
      "command": "uvx",
      "args": ["mcp-sqlserver-filesystem@latest"],
      "timeout": 600,
      "env": {
        "DB_SERVER": "localhost",
        "DB_DATABASE": "master",
        "DB_USE_WINDOWS_AUTH": "true",
        "DB_TRUST_SERVER_CERTIFICATE": "true",
        "DB_ENCRYPT": "false",
        "DB_MULTIPLE_ACTIVE_RESULT_SETS": "true"
      },
      "autoApprove": [
        "sql_query",
        "sql_execute",
        "list_tables",
        "get_table_schema",
        "read_file",
        "write_file",
        "list_directory"
      ]
    }
  }
}
```

## 🛠️ Available Tools

### Database Tools
- `sql_query` - Execute SQL queries with UI display
- `sql_execute` - Execute INSERT/UPDATE/DELETE operations
- `get_table_schema` - Get table structure information
- `list_tables` - List all database tables

### Filesystem Tools
- `read_file` - Read file contents
- `write_file` - Write file contents with confirmation
- `list_directory` - List directory contents

## 📝 Usage Examples

In Augment Code, try:

```
"Execute SQL query: SELECT TOP 10 * FROM Users"
"Show me the schema of the Users table"
"List all tables in the database"
"Read the file config.json"
"Write configuration to settings.json"
```

## 🔒 Configuration

Set environment variables or create `.env` file:

```env
# SQL Server Configuration
DB_SERVER=localhost
DB_DATABASE=master
DB_USE_WINDOWS_AUTH=true

# Enhanced Connection Parameters
DB_TRUST_SERVER_CERTIFICATE=true
DB_ENCRYPT=false
DB_MULTIPLE_ACTIVE_RESULT_SETS=true

# Web UI Configuration
MCP_WEB_HOST=127.0.0.1
MCP_WEB_PORT=8765
```

## 📋 Requirements

- Python 3.11+
- ODBC Driver for SQL Server
- Windows/macOS/Linux support

## 📄 License

MIT License - see [LICENSE](LICENSE) file.

---

**🎉 Enjoy powerful SQL Server and filesystem access in Augment Code!**
