# MCP SQL Server Filesystem

🚀 **Enhanced MCP server** for SQL Server database and filesystem access with dual interface support.

*Read this in other languages: [中文](README_zh.md)*

## ✨ Features

- **Complete SQL Server Support** - Execute all SQL commands with enhanced connection parameters
- **Full Filesystem Access** - Read/write files with confirmation dialogs  
- **Web UI Interface** - Real-time query results display
- **Desktop Application** - Cross-platform native desktop app (v0.1.1 new feature)
- **Smart Environment Detection** - Auto-adapts to SSH Remote, WSL, Local environments
- **Enhanced Connection Parameters** - Built-in support for `TrustServerCertificate=true`, `Encrypt=false`, `MultipleActiveResultSets=true`

## 🚀 Quick Start

### 📦 Simple Installation

```bash
# Install uv (if not already installed)
pip install uv

# Run directly (no need to clone repository)
uvx mcp-sqlserver-filesystem@latest
```

### 🧪 Installation & Testing

```bash
# Test Web UI
uvx mcp-sqlserver-filesystem@latest --test-web

# Test desktop application (v0.1.1 new feature)
uvx mcp-sqlserver-filesystem@latest --test-desktop

# Or use traditional way
uvx mcp-sqlserver-filesystem@latest test --web
uvx mcp-sqlserver-filesystem@latest test --desktop
```

### 📋 System Requirements

**Windows 11 users please ensure you have:**

1. **Python 3.11+** 
   ```bash
   python --version  # Check version
   # If not installed: winget install Python.Python.3.12
   ```

2. **ODBC Driver for SQL Server** ⭐ **Important!**
   ```bash
   # Check drivers: python -c "import pyodbc; print([d for d in pyodbc.drivers() if 'SQL Server' in d])"
   # If none: winget install Microsoft.ODBCDriverforSQLServer
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

## 🔒 Configuration Options

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

## 🆕 v0.1.1 New Features

- ✅ **Desktop Application Support** - Cross-platform native desktop app
- ✅ **Quick Test Commands** - `--test-web` and `--test-desktop`
- ✅ **Enhanced Connection Parameters** - Full SQL Server connection options support
- ✅ **Full Access Mode** - Default allow all SQL commands and file operations

## 📋 System Requirements

- Python 3.11+
- ODBC Driver for SQL Server
- Windows/macOS/Linux support

## 🤝 Contributing

Issues and Pull Requests are welcome!

## 📄 License

MIT License - see [LICENSE](LICENSE) file.

---

**🎉 Enjoy powerful SQL Server and filesystem access in Augment Code!**
