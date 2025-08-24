﻿﻿﻿﻿# MCP SQL Server Filesystem

🚀 **Enhanced MCP server** for SQL Server database and filesystem access with **dual interface support** (Web UI and Desktop Application).

*Read this in other languages: [English](#english) | [中文](#中文)*

---

## English

### ✨ Features

- 🗄️ **Complete SQL Server Support** - Execute all SQL commands with enhanced connection parameters
- 📁 **Full Filesystem Access** - Read/write files with confirmation dialogs  
- 🌐 **Web UI Interface** - Real-time query results display with modern responsive design
- 🖥️ **Desktop Application** - Cross-platform native desktop app based on Tauri framework
- 🔍 **Smart Environment Detection** - Auto-adapts to SSH Remote, WSL, Local environments
- 🔐 **Enhanced Connection Parameters** - Built-in support for `TrustServerCertificate=true`, `Encrypt=false`, `MultipleActiveResultSets=true`
- ⚡ **Dual Interface Architecture** - Choose between Web UI and native desktop experience
- 🎨 **Modern UI Design** - Responsive design with dark/light theme support
- 🔄 **Real-time Communication** - WebSocket-based live updates

### 🚀 Quick Start

#### 📦 Simple Installation

```bash
# Install uv (if not already installed)
pip install uv

# Run directly (no need to clone repository)
uvx mcp-sqlserver-filesystem@latest
```

#### 🧪 Testing Both Interfaces

```bash
# Test Web UI (browser-based interface)
uvx mcp-sqlserver-filesystem@latest --test-web

# Test Desktop Application (native app)
uvx mcp-sqlserver-filesystem@latest --test-desktop

# Alternative syntax
uvx mcp-sqlserver-filesystem@latest test --web
uvx mcp-sqlserver-filesystem@latest test --desktop
```

### 🖥️ Desktop Application

#### Features
- **Cross-platform Support**: Windows (.exe, .msi), macOS (.dmg, .app), Linux (.deb, .AppImage)
- **Native Performance**: Built with Tauri framework (Rust + Web Technologies)
- **Modern Interface**: Responsive design with tabbed navigation
- **Real-time Updates**: WebSocket communication with backend
- **Local Settings**: Persistent configuration storage
- **System Integration**: Native notifications and file dialogs

#### Requirements for Desktop App
1. **Rust** (for building): Install from https://rustup.rs/
2. **Tauri CLI**: `cargo install tauri-cli`

#### Desktop Development
```bash
# Clone repository for desktop development
git clone https://github.com/ppengit/mcp-sqlserver-filesystem.git
cd mcp-sqlserver-filesystem

# Install dependencies
python scripts/build_desktop.py install-deps

# Run in development mode
python scripts/build_desktop.py dev-desktop

# Build release version
python scripts/build_desktop.py build-desktop-release

# Package for distribution
python scripts/build_desktop.py package
```

### 📋 System Requirements

**All platforms:**
1. **Python 3.11+**
2. **ODBC Driver for SQL Server** ⭐ **Critical!**

**Windows users:**
```bash
# Check Python version
python --version

# Check ODBC drivers
python -c "import pyodbc; print([d for d in pyodbc.drivers() if 'SQL Server' in d])"

# Install ODBC Driver (choose one method):
# Method 1: winget (recommended)
winget install Microsoft.ODBCDriverforSQLServer

# Method 2: Chocolatey
choco install sqlserver-odbcdriver
```

**Download links:**
- [ODBC Driver 18](https://go.microsoft.com/fwlink/?linkid=2249006) (latest)
- [ODBC Driver 17](https://go.microsoft.com/fwlink/?linkid=2249005) (stable)
- [All versions](https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)

### 🔧 Augment Code Configuration

#### Option 1: Windows Authentication (Recommended)

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
        "DB_MULTIPLE_ACTIVE_RESULT_SETS": "true",
        "MCP_DESKTOP_MODE": "false"
      },
      "autoApprove": [
        "sql_query", "sql_execute", "list_tables", "get_table_schema",
        "read_file", "write_file", "list_directory"
      ]
    }
  }
}
```

#### Option 2: SQL Server Authentication

```json
{
  "mcpServers": {
    "mcp-sqlserver-filesystem": {
      "command": "uvx",
      "args": ["mcp-sqlserver-filesystem@latest"],
      "timeout": 600,
      "env": {
        "DB_SERVER": "your-sql-server",
        "DB_DATABASE": "your-database",
        "DB_USE_WINDOWS_AUTH": "false",
        "DB_USERNAME": "your-username",
        "DB_PASSWORD": "your-password",
        "DB_TRUST_SERVER_CERTIFICATE": "true",
        "DB_ENCRYPT": "false",
        "DB_MULTIPLE_ACTIVE_RESULT_SETS": "true"
      },
      "autoApprove": [
        "sql_query", "sql_execute", "list_tables", "get_table_schema",
        "read_file", "write_file", "list_directory"
      ]
    }
  }
}
```

#### Option 3: Desktop Application Mode

```json
{
  "mcpServers": {
    "mcp-sqlserver-filesystem": {
      "command": "uvx",
      "args": ["mcp-sqlserver-filesystem@latest"],
      "timeout": 600,
      "env": {
        "MCP_DESKTOP_MODE": "true",
        "MCP_WEB_HOST": "127.0.0.1",
        "MCP_WEB_PORT": "8765",
        "DB_SERVER": "localhost",
        "DB_DATABASE": "master",
        "DB_USE_WINDOWS_AUTH": "true"
      },
      "autoApprove": ["interactive_feedback"]
    }
  }
}
```

#### Option 4: Restricted Filesystem Access (Recommended for Production)

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
        "FS_ALLOWED_PATHS": "C:\\Users\\YourName\\Documents,C:\\Projects",
        "FS_BLOCKED_PATHS": "C:\\Windows,C:\\System32",
        "FS_ALLOWED_EXTENSIONS": ".txt,.json,.xml,.csv,.log,.md,.py,.js",
        "FS_ENABLE_DELETE": "false"
      },
      "autoApprove": [
        "sql_query", "list_tables", "get_table_schema",
        "read_file", "list_directory"
      ]
    }
  }
}
```

### 🛡️ Filesystem Security Configuration

The filesystem access system provides flexible security controls to restrict file access to specific directories.

#### Access Modes

1. **Full Access Mode** (Default - ⚠️ Use with caution)
   - `FS_ALLOWED_PATHS=` (empty) or `FS_ALLOWED_PATHS=*`
   - Allows access to all disk files and directories
   - Suitable for trusted local development only

2. **Restricted Access Mode** (Recommended for production)
   - `FS_ALLOWED_PATHS=C:\Users\YourName\Documents,D:\Projects`
   - Only allows access to specified directories and their subdirectories
   - More secure for shared or production environments

#### Configuration Variables

| Variable | Description | Example |
|----------|-------------|----------|
| `FS_ALLOWED_PATHS` | Comma-separated list of allowed directories | `C:\Users\John\Documents,D:\Projects` |
| `FS_BLOCKED_PATHS` | Comma-separated list of blocked directories (higher priority) | `C:\Windows,C:\System32` |
| `FS_ALLOWED_EXTENSIONS` | Comma-separated list of allowed file extensions | `.txt,.json,.py,.md` |
| `FS_BLOCKED_EXTENSIONS` | Comma-separated list of blocked file extensions | `.exe,.dll,.sys` |
| `FS_MAX_FILE_SIZE` | Maximum file size in bytes | `104857600` (100MB) |
| `FS_ENABLE_WRITE` | Enable file write operations | `true` or `false` |
| `FS_ENABLE_DELETE` | Enable file delete operations | `true` or `false` |

#### Security Examples

**Conservative Security (Recommended)**:
```env
FS_ALLOWED_PATHS=C:\Users\YourName\Documents,C:\Users\YourName\Projects
FS_BLOCKED_PATHS=C:\Windows,C:\ProgramData
FS_ALLOWED_EXTENSIONS=.txt,.json,.xml,.csv,.log,.md,.py,.js,.html,.css
FS_ENABLE_WRITE=true
FS_ENABLE_DELETE=false
FS_MAX_FILE_SIZE=10485760  # 10MB
```

**Development Environment**:
```env
FS_ALLOWED_PATHS=C:\Development,C:\Temp
FS_BLOCKED_PATHS=C:\Windows,C:\System32
FS_ALLOWED_EXTENSIONS=  # Allow all extensions
FS_ENABLE_WRITE=true
FS_ENABLE_DELETE=true
FS_MAX_FILE_SIZE=104857600  # 100MB
```

**Full Access (Use with extreme caution)**:
```env
FS_ALLOWED_PATHS=*  # or leave empty
FS_BLOCKED_PATHS=
FS_ALLOWED_EXTENSIONS=
FS_ENABLE_WRITE=true
FS_ENABLE_DELETE=true
FS_MAX_FILE_SIZE=1073741824  # 1GB
```

### 🛠️ Available Tools

#### Database Tools
- `sql_query` - Execute SQL queries with UI display
- `sql_execute` - Execute INSERT/UPDATE/DELETE operations
- `get_table_schema` - Get table structure information
- `list_tables` - List all database tables

#### Filesystem Tools
- `read_file` - Read file contents
- `write_file` - Write file contents with confirmation
- `list_directory` - List directory contents

### 📝 Usage Examples

In Augment Code, try:

```
"Execute SQL query: SELECT TOP 10 * FROM Users"
"Show me the schema of the Users table"
"List all tables in the database"
"Read the file config.json"
"Write configuration to settings.json"
"Launch desktop interface for database management"
```

### 🎯 Interface Comparison

| Feature | Web UI | Desktop App |
|---------|--------|-------------|
| **Platform** | Any browser | Windows/macOS/Linux |
| **Installation** | None | Rust + Tauri CLI |
| **Performance** | Good | Excellent (Native) |
| **Offline Use** | No | Yes |
| **File Dialogs** | Basic | Native |
| **Notifications** | Browser | System |
| **Best for** | Remote/WSL | Local Development |

---

## 中文

### ✨ 功能特性

- 🗄️ **完整的SQL Server支持** - 执行所有SQL命令，增强连接参数
- 📁 **完整的文件系统访问** - 带确认对话框的文件读写功能
- 🌐 **Web UI界面** - 实时查询结果显示，现代响应式设计
- 🖥️ **桌面应用程序** - 基于Tauri框架的跨平台原生桌面应用
- 🔍 **智能环境检测** - 自动适配SSH远程、WSL、本地环境
- 🔐 **增强连接参数** - 内置支持`TrustServerCertificate=true`等参数
- ⚡ **双界面架构** - 可选择Web UI或原生桌面体验
- 🎨 **现代UI设计** - 响应式设计，支持深色/浅色主题
- 🔄 **实时通信** - 基于WebSocket的实时更新

### 🚀 快速开始

#### 📦 简单安装

```bash
# 安装 uv (如果还没安装)
pip install uv

# 直接运行 (无需克隆仓库)
uvx mcp-sqlserver-filesystem@latest
```

#### 🧪 测试两种界面

```bash
# 测试 Web UI (浏览器界面)
uvx mcp-sqlserver-filesystem@latest --test-web

# 测试桌面应用 (原生应用)
uvx mcp-sqlserver-filesystem@latest --test-desktop

# 或者使用替代语法
uvx mcp-sqlserver-filesystem@latest test --web
uvx mcp-sqlserver-filesystem@latest test --desktop
```

### 🖥️ 桌面应用程序

#### 功能特性
- **跨平台支持**: Windows (.exe, .msi), macOS (.dmg, .app), Linux (.deb, .AppImage)
- **原生性能**: 使用Tauri框架构建 (Rust + Web技术)
- **现代界面**: 响应式设计，标签页导航
- **实时更新**: 与后端WebSocket通信
- **本地设置**: 持久化配置存储
- **系统集成**: 原生通知和文件对话框

#### 桌面应用要求
1. **Rust** (用于构建): 从 https://rustup.rs/ 安装
2. **Tauri CLI**: `cargo install tauri-cli`

#### 桌面开发
```bash
# 克隆仓库进行桌面开发
git clone https://github.com/ppengit/mcp-sqlserver-filesystem.git
cd mcp-sqlserver-filesystem

# 安装依赖
python scripts/build_desktop.py install-deps

# 开发模式运行
python scripts/build_desktop.py dev-desktop

# 构建发布版本
python scripts/build_desktop.py build-desktop-release

# 打包分发
python scripts/build_desktop.py package
```

### 📋 系统要求

**所有平台:**
1. **Python 3.11+**
2. **ODBC Driver for SQL Server** ⭐ **必需!**

**Windows 用户:**
```bash
# 检查Python版本
python --version

# 检查ODBC驱动
python -c "import pyodbc; print([d for d in pyodbc.drivers() if 'SQL Server' in d])"

# 安装ODBC驱动 (选择一种方法):
# 方法1: winget (推荐)
winget install Microsoft.ODBCDriverforSQLServer

# 方法2: Chocolatey
choco install sqlserver-odbcdriver
```

**下载链接:**
- [ODBC Driver 18](https://go.microsoft.com/fwlink/?linkid=2249006) (最新版)
- [ODBC Driver 17](https://go.microsoft.com/fwlink/?linkid=2249005) (稳定版)
- [所有版本](https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)

### 🔧 Augment Code 配置

#### 选项1: Windows认证 (推荐)

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
        "DB_MULTIPLE_ACTIVE_RESULT_SETS": "true",
        "MCP_DESKTOP_MODE": "false"
      },
      "autoApprove": [
        "sql_query", "sql_execute", "list_tables", "get_table_schema",
        "read_file", "write_file", "list_directory"
      ]
    }
  }
}
```

#### 选项2: SQL Server认证

```json
{
  "mcpServers": {
    "mcp-sqlserver-filesystem": {
      "command": "uvx",
      "args": ["mcp-sqlserver-filesystem@latest"],
      "timeout": 600,
      "env": {
        "DB_SERVER": "your-sql-server",
        "DB_DATABASE": "your-database",
        "DB_USE_WINDOWS_AUTH": "false",
        "DB_USERNAME": "your-username",
        "DB_PASSWORD": "your-password",
        "DB_TRUST_SERVER_CERTIFICATE": "true",
        "DB_ENCRYPT": "false",
        "DB_MULTIPLE_ACTIVE_RESULT_SETS": "true"
      },
      "autoApprove": [
        "sql_query", "sql_execute", "list_tables", "get_table_schema",
        "read_file", "write_file", "list_directory"
      ]
    }
  }
}
```

#### 选项3: 桌面应用模式

```json
{
  "mcpServers": {
    "mcp-sqlserver-filesystem": {
      "command": "uvx",
      "args": ["mcp-sqlserver-filesystem@latest"],
      "timeout": 600,
      "env": {
        "MCP_DESKTOP_MODE": "true",
        "MCP_WEB_HOST": "127.0.0.1",
        "MCP_WEB_PORT": "8765",
        "DB_SERVER": "localhost",
        "DB_DATABASE": "master",
        "DB_USE_WINDOWS_AUTH": "true"
      },
      "autoApprove": ["interactive_feedback"]
    }
  }
}
```

### 🛡️ 文件系统安全配置

文件系统访问系统提供灵活的安全控制，可以限制文件访问仅限于特定目录。

#### 访问模式

1. **完全访问模式** (默认 - ⚠️ 请谨慎使用)
   - `FS_ALLOWED_PATHS=` (空白) 或 `FS_ALLOWED_PATHS=*`
   - 允许访问所有磁盘文件和目录
   - 仅适用于可信的本地开发环境

2. **限制访问模式** (推荐用于生产环境)
   - `FS_ALLOWED_PATHS=C:\\Users\\YourName\\Documents,D:\\Projects`
   - 仅允许访问指定目录及其子目录
   - 对共享或生产环境更加安全

#### 配置变量

| 变量 | 说明 | 示例 |
|------|------|------|
| `FS_ALLOWED_PATHS` | 逗号分隔的允许目录列表 | `C:\\Users\\John\\Documents,D:\\Projects` |
| `FS_BLOCKED_PATHS` | 逗号分隔的禁止目录列表(优先级更高) | `C:\\Windows,C:\\System32` |
| `FS_ALLOWED_EXTENSIONS` | 逗号分隔的允许文件扩展名列表 | `.txt,.json,.py,.md` |
| `FS_BLOCKED_EXTENSIONS` | 逗号分隔的禁止文件扩展名列表 | `.exe,.dll,.sys` |
| `FS_MAX_FILE_SIZE` | 最大文件大小(字节) | `104857600` (100MB) |
| `FS_ENABLE_WRITE` | 启用文件写入操作 | `true` 或 `false` |
| `FS_ENABLE_DELETE` | 启用文件删除操作 | `true` 或 `false` |

#### 安全配置示例

**保守安全配置(推荐)**:
```env
FS_ALLOWED_PATHS=C:\\Users\\YourName\\Documents,C:\\Users\\YourName\\Projects
FS_BLOCKED_PATHS=C:\\Windows,C:\\ProgramData
FS_ALLOWED_EXTENSIONS=.txt,.json,.xml,.csv,.log,.md,.py,.js,.html,.css
FS_ENABLE_WRITE=true
FS_ENABLE_DELETE=false
FS_MAX_FILE_SIZE=10485760  # 10MB
```

**开发环境配置**:
```env
FS_ALLOWED_PATHS=C:\\Development,C:\\Temp
FS_BLOCKED_PATHS=C:\\Windows,C:\\System32
FS_ALLOWED_EXTENSIONS=  # 允许所有扩展名
FS_ENABLE_WRITE=true
FS_ENABLE_DELETE=true
FS_MAX_FILE_SIZE=104857600  # 100MB
```

**完全访问(请极其谨慎使用)**:
```env
FS_ALLOWED_PATHS=*  # 或留空
FS_BLOCKED_PATHS=
FS_ALLOWED_EXTENSIONS=
FS_ENABLE_WRITE=true
FS_ENABLE_DELETE=true
FS_MAX_FILE_SIZE=1073741824  # 1GB
```

### 🛠️ 可用工具

#### 数据库工具
- `sql_query` - 执行SQL查询并显示UI
- `sql_execute` - 执行INSERT/UPDATE/DELETE操作
- `get_table_schema` - 获取表结构信息
- `list_tables` - 列出所有数据库表

#### 文件系统工具
- `read_file` - 读取文件内容
- `write_file` - 写入文件内容(带确认)
- `list_directory` - 列出目录内容

### 📝 使用示例

在 Augment Code 中尝试:

```
"执行SQL查询: SELECT TOP 10 * FROM Users"
"显示Users表的结构"
"列出数据库中的所有表"
"读取config.json文件"
"将配置写入settings.json"
"启动桌面界面进行数据库管理"
```

### 🎯 界面对比

| 功能 | Web UI | 桌面应用 |
|------|--------|----------|
| **平台** | 任何浏览器 | Windows/macOS/Linux |
| **安装** | 无需安装 | Rust + Tauri CLI |
| **性能** | 良好 | 优秀 (原生) |
| **离线使用** | 否 | 是 |
| **文件对话框** | 基础 | 原生 |
| **通知** | 浏览器 | 系统 |
| **最适合** | 远程/WSL | 本地开发 |

---

## 📦 版本信息

**当前版本**: v0.1.4

### 🆕 v0.1.4 新功能
- ✅ **增强文件系统安全** - 支持环境变量配置允许访问的文件夹
- ✅ **通配符支持** - 使用 `*` 或留空启用完全访问模式
- ✅ **路径访问控制** - 可配置允许和禁止访问的目录
- ✅ **扩展名过滤** - 支持按文件扩展名控制访问
- ✅ **详细配置日志** - 启动时显示完整的安全配置信息
- ✅ **生产安全模式** - 推荐的安全配置示例

### 🔄 升级说明
- 从v0.1.2升级: 新增桌面应用功能，向后兼容
- 从v0.1.1升级: 增强UI设计和稳定性改进

## 🏗️ 技术架构

### 后端架构
- **Python 3.11+** - MCP服务器核心
- **FastAPI** - Web API框架
- **WebSocket** - 实时通信
- **pyodbc** - SQL Server连接

### 前端架构
- **Web UI**: HTML5 + CSS3 + JavaScript
- **Desktop**: Tauri (Rust) + Web Technologies
- **通信**: WebSocket + Tauri IPC

### 构建工具
- **Python**: uv, pip, setuptools
- **Rust**: Cargo, Tauri CLI
- **跨平台**: Makefile, batch scripts, Python scripts

## 🤝 贡献

欢迎提交Issues和Pull Requests!

### 开发环境设置
```bash
# 克隆项目
git clone https://github.com/ppengit/mcp-sqlserver-filesystem.git
cd mcp-sqlserver-filesystem

# 安装Python依赖
uv sync

# 安装Rust和Tauri (桌面开发)
python scripts/build_desktop.py install-deps

# 运行测试
uv run python -m pytest
```

## 👨‍💻 作者

由 **PJ** 创建 - 增强型MCP服务器，用于SQL Server和文件系统访问。

- GitHub: [ppengit](https://github.com/ppengit)
- Email: peng.it@qq.com

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件。

---

**🎉 在Augment Code中享受强大的SQL Server和文件系统访问功能！**

*Made with ❤️ by PJ*
