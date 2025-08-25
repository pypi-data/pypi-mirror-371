# MCP SQL Server Filesystem

一个简洁高效的 MCP (Model Context Protocol) 服务器，提供 SQL Server 数据库访问和文件系统操作功能。

## ✨ 主要特性

### 🗄️ 数据库功能
- **SQL 查询执行** - 支持 SELECT 查询
- **SQL 命令执行** - 支持 INSERT/UPDATE/DELETE 操作
- **表结构查询** - 获取表的详细结构信息和字段描述
- **表列表** - 列出数据库中的所有表

### 📁 文件系统功能
- **文件读取** - 读取文件内容
- **文件写入** - 写入内容到文件
- **目录列表** - 列出目录内容

### 🔒 安全特性
- SQL 注入防护
- 文件系统访问控制
- 环境变量配置
- 权限验证

## 🚀 快速开始

### 📦 零安装使用（推荐）

```bash
# 安装 uv（如果尚未安装）
pip install uv

# 直接运行 - 无需克隆仓库！
uvx mcp-sqlserver-filesystem@latest
```

### 🔧 配置

在你的 MCP 客户端（如 Claude Desktop、AugmentCode）中添加以下配置：

```json
{
  "mcpServers": {
    "mcp-sqlserver-filesystem": {
      "command": "uvx",
      "args": ["mcp-sqlserver-filesystem@latest"],
      "env": {
        "DB_SERVER": "localhost",
        "DB_DATABASE": "your_database",
        "DB_USERNAME": "your_username",
        "DB_PASSWORD": "your_password",
        "DB_USE_WINDOWS_AUTH": "false",
        "DB_TRUST_SERVER_CERTIFICATE": "true",
        "DB_ENCRYPT": "false",
        "FS_ALLOWED_PATHS": "*",
        "FS_ALLOWED_EXTENSIONS": "*.*",
        "FS_IGNORE_FILE_LOCKS": "true"
      }
    }
  }
}
```

## 🛠️ 可用工具

### 数据库工具

- `sql_query` - 执行 SQL SELECT 查询
- `sql_execute` - 执行 SQL INSERT/UPDATE/DELETE 命令
- `list_tables` - 列出数据库中的所有表
- `get_table_schema` - 获取表的结构信息

### 文件系统工具

- `read_file` - 读取文件内容
- `write_file` - 写入文件内容
- `list_directory` - 列出目录内容

## 📋 环境变量

### 数据库配置
- `DB_SERVER` - SQL Server 服务器地址
- `DB_DATABASE` - 数据库名称
- `DB_USERNAME` - 用户名
- `DB_PASSWORD` - 密码
- `DB_USE_WINDOWS_AUTH` - 是否使用 Windows 身份验证
- `DB_TRUST_SERVER_CERTIFICATE` - 是否信任服务器证书
- `DB_ENCRYPT` - 是否加密连接

### 文件系统配置
- `FS_ALLOWED_PATHS` - 允许访问的路径（`*` 表示所有路径）
- `FS_ALLOWED_EXTENSIONS` - 允许的文件扩展名（`*.*` 表示所有文件）
- `FS_IGNORE_FILE_LOCKS` - 是否忽略文件锁

## 🔧 开发

### 本地开发

```bash
# 克隆仓库
git clone https://github.com/ppengit/mcp-sqlserver-filesystem.git
cd mcp-sqlserver-filesystem

# 安装依赖
uv sync

# 运行服务器
uv run python -m mcp_sqlserver_filesystem server
```

### 测试

```bash
# 运行测试
uv run pytest

# 运行特定测试
uv run pytest tests/test_database.py
```

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件。

## 🤝 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

## 📞 支持

- GitHub Issues: [https://github.com/ppengit/mcp-sqlserver-filesystem/issues](https://github.com/ppengit/mcp-sqlserver-filesystem/issues)
- 文档: [https://github.com/ppengit/mcp-sqlserver-filesystem/wiki](https://github.com/ppengit/mcp-sqlserver-filesystem/wiki)

## 🔄 更新日志

### v1.0.0
- 🎉 首个稳定版本发布
- ✨ 完整的 SQL Server 数据库支持
- 📁 全面的文件系统操作
- 🔒 增强的安全特性
- 📝 改进的错误处理和日志记录
- 🚀 简化的架构，移除了复杂的UI组件，专注于核心功能

---

**注意**: 此版本专注于核心功能的稳定性和可靠性，移除了之前版本中的UI组件以简化架构和提高性能。
