# MCP SQL Server Filesystem

🚀 **Enhanced MCP server** for SQL Server database and filesystem access with **dual interface support** (Web UI and Desktop Application).

## ✨ Key Features

- 🗄️ **Complete SQL Server Support** - Execute all SQL commands with detailed operation tracking
- 📁 **Full Filesystem Access** - Read/write files with advanced security controls  
- 🌐 **Web UI Interface** - Real-time query results display with modern responsive design
- 🖥️ **Desktop Application** - Cross-platform native desktop app with intelligent fallback to Web UI
- 📊 **Detailed Operation Tracking** - INSERT/UPDATE/DELETE operations show affected records
- 🔐 **Enhanced Security** - Comprehensive access controls and validation

## 🚀 Quick Start

### Zero-Installation Usage (Recommended)

```bash
# Install uv (if not already installed)
pip install uv

# Run directly - no need to clone repository or install Rust!
uvx mcp-sqlserver-filesystem@latest
```

### Testing Interfaces

```bash
# Test Web UI
uvx mcp-sqlserver-filesystem@latest --test-web

# Test Desktop Application (auto-fallback to Web UI)
uvx mcp-sqlserver-filesystem@latest --test-desktop
```

## 📋 System Requirements

1. **Python 3.11+**
2. **ODBC Driver for SQL Server** ⭐ **Required!**
3. **uv** (for package execution)

### Install ODBC Driver (Windows)

```bash
# Method 1: winget (recommended)
winget install Microsoft.ODBCDriverforSQLServer

# Method 2: Chocolatey  
choco install sqlserver-odbcdriver
```

## 🔧 Configuration

### Complete Setup (Database + Filesystem)

```json
{
  "mcpServers": {
    "mcp-sqlserver-filesystem": {
      "command": "uvx",
      "args": ["mcp-sqlserver-filesystem@latest"], 
      "timeout": 600,
      "env": {
        "DB_SERVER": "localhost",
        "DB_DATABASE": "your_database",
        "DB_USE_WINDOWS_AUTH": "true",
        "FS_ALLOWED_PATHS": "C:\\Users\\YourName\\Documents,D:\\Projects", 
        "FS_ALLOWED_EXTENSIONS": ".txt,.md,.py,.json,.sql,.csv",
        "FS_IGNORE_FILE_LOCKS": "true"
      },
      "autoApprove": [
        "sql_query", "list_tables", "get_table_schema",
        "read_file", "write_file", "list_directory"
      ]
    }
  }
}
```

### SQL Server Authentication

```json
{
  "mcpServers": {
    "mcp-sqlserver-filesystem": {
      "command": "uvx",
      "args": ["mcp-sqlserver-filesystem@latest"],
      "timeout": 600,
      "env": {
        "DB_SERVER": "your-server", 
        "DB_DATABASE": "your_database",
        "DB_USE_WINDOWS_AUTH": "false",
        "DB_USERNAME": "sa",
        "DB_PASSWORD": "your_password",
        "FS_ALLOWED_PATHS": "*",
        "FS_ALLOWED_EXTENSIONS": "*.*"
      },
      "autoApprove": [
        "sql_query", "list_tables", "get_table_schema",
        "read_file", "write_file", "list_directory"
      ]
    }
  }
}
```

## 🛠️ Key Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_SERVER` | SQL Server hostname | `localhost` |
| `DB_DATABASE` | Database name | `master` |
| `DB_USE_WINDOWS_AUTH` | Use Windows Authentication | `true` |
| `DB_USERNAME` | SQL Server username | - |
| `DB_PASSWORD` | SQL Server password | - |
| `FS_ALLOWED_PATHS` | Allowed filesystem paths | `[]` (empty = allow all) |
| `FS_ALLOWED_EXTENSIONS` | Allowed file extensions | `[]` (empty = allow all) |
| `FS_IGNORE_FILE_LOCKS` | Ignore file locks | `true` |

## 📚 Available Tools

### Database Operations
- `sql_query` - Execute SQL with detailed results
- `list_tables` - List all database tables  
- `get_table_schema` - Get table structure

### Filesystem Operations
- `read_file` - Read file contents
- `write_file` - Write file contents  
- `list_directory` - List directory contents

## 🎯 Usage Examples

### SQL Operations with Detailed Tracking
```python
# Shows affected records for DML operations
result = sql_query("INSERT INTO users (name) VALUES ('John')")
result = sql_query("UPDATE users SET status = 'active' WHERE id = 1") 
result = sql_query("DELETE FROM users WHERE status = 'inactive')")
```

### Filesystem Operations  
```python
content = read_file("C:/Projects/config.json")
write_file("C:/Projects/output.txt", "Hello World!")
files = list_directory("C:/Projects")
```

## 🚨 Troubleshooting

1. **ODBC Driver Issues**: Install Microsoft ODBC Driver for SQL Server
2. **Connection Timeout**: Increase `DB_CONNECTION_TIMEOUT`  
3. **Desktop App**: Automatically falls back to Web UI
4. **File Access**: Enable `FS_IGNORE_FILE_LOCKS`

## 📖 Links

- **GitHub**: [mcp-sqlserver-filesystem](https://github.com/ppengit/mcp-sqlserver-filesystem)
- **PyPI**: [mcp-sqlserver-filesystem](https://pypi.org/project/mcp-sqlserver-filesystem/)
- **Issues**: [GitHub Issues](https://github.com/ppengit/mcp-sqlserver-filesystem/issues)

## License

MIT License - **PJ** ([peng.it@qq.com](mailto:peng.it@qq.com))