# MCP Database Server

🚀 **Universal Database Connector for AI Assistants**

Connect to ANY database (SQL Server, PostgreSQL, MySQL, MongoDB, Redis, SQLite) through your AI assistant with just a simple configuration!

A universal MCP (Model Context Protocol) server that provides seamless connections to multiple database types. This server enables AI assistants like Claude to interact with your databases through a unified interface.

## 📦 Quick Install

```bash
# Install with uv (recommended)
uv add mcp-universal-database-server

# Or install with pip
pip install mcp-universal-database-server
```

## 🔧 Simple Setup

Add this to your `~/.cursor/mcp.json` or `.vscode/settings.json`:

```json
{
  "mcpServers": {
    "mcp-database-server": {
      "command": "mcp-universal-database-server",
      "args": ["serve"]
    }
  }
}
```

**That's it!** Your AI assistant can now connect to any database. Just ask: *"Connect to my SQL Server database"*

## 🚀 Features

- **Universal Database Support**: Connect to PostgreSQL, MySQL, SQLite, MongoDB, Redis, and more
- **MCP Integration**: Seamless integration with VSCode, Cursor, and other MCP-compatible tools
- **Secure Connections**: Support for SSL/TLS and connection pooling
- **Rich Operations**: Full CRUD operations, schema management, and query execution
- **Type Safety**: Built with Python type hints and Pydantic models
- **Easy Installation**: Install via `uv` package manager

## 📦 Supported Databases

### SQL Databases
- **PostgreSQL** - Advanced open-source relational database
- **MySQL** - Popular open-source relational database  
- **SQLite** - Lightweight file-based SQL database
- **Microsoft SQL Server** *(planned)*
- **Oracle Database** *(planned)*

### NoSQL Databases
- **MongoDB** - Document-oriented database
- **Redis** - In-memory key-value store
- **Apache Cassandra** *(planned)*

### Cloud Databases
- **Google Firestore** *(planned)*
- **Amazon DynamoDB** *(planned)*
- **Azure Cosmos DB** *(planned)*

## 🛠️ Installation

### Using uv (Recommended)

```bash
# Install from PyPI (once published)
uv add mcp-database-server

# Or install from source
uv add git+https://github.com/yourusername/mcp-database-server.git
```

### Using pip

```bash
pip install mcp-database-server
```

## 🔧 Configuration

### 1. Generate Configuration

```bash
mcp-database-server generate-config --output mcp_config.json
```

### 2. Configure VSCode/Cursor

Add to your MCP settings file (`.vscode/settings.json` or Cursor equivalent):

```json
{
  "mcp.servers": {
    "mcp-database-server": {
      "command": "mcp-database-server",
      "args": ["serve"]
    }
  }
}
```

### 3. Add Database Connections

Use the MCP tools in your AI assistant to add connections:

```
Add a PostgreSQL connection:
- Name: my_postgres
- Type: postgresql
- Host: localhost
- Port: 5432
- Username: myuser
- Password: mypassword
- Database: mydatabase
```

## 🚀 Usage

### Starting the Server

```bash
# Start MCP server (typically called by your editor)
mcp-database-server serve

# Test a connection
mcp-database-server test-connection \
  --type postgresql \
  --host localhost \
  --port 5432 \
  my_postgres

# List supported database types
mcp-database-server list-supported
```

### Available MCP Tools

Once configured, you can use these tools through your AI assistant:

#### Connection Management
- `add_connection` - Add a new database connection
- `remove_connection` - Remove a database connection
- `list_connections` - List all configured connections
- `test_connection` - Test a specific connection

#### Schema Operations
- `get_schema_info` - Get database schema information
- `get_table_info` - Get detailed table information
- `list_databases` - List available databases
- `list_tables` - List tables in a database/schema

#### Data Operations
- `execute_query` - Execute SQL queries or database commands
- `insert_data` - Insert data into tables/collections
- `update_data` - Update data in tables (SQL databases)
- `delete_data` - Delete data from tables/collections

#### Table Management (SQL)
- `create_table` - Create new tables
- `drop_table` - Drop tables

#### Collection Management (NoSQL)
- `create_collection` - Create new collections
- `find_documents` - Find documents in collections
- `update_documents` - Update documents in collections

## 📝 Examples

### Example 1: PostgreSQL Connection

```python
# Through MCP tools in your AI assistant:
# 1. Add connection
add_connection(
    name="my_postgres",
    type="postgresql",
    host="localhost",
    port=5432,
    username="myuser",
    password="mypassword",
    database="mydb"
)

# 2. Execute query
execute_query(
    connection_name="my_postgres",
    query="SELECT * FROM users WHERE active = $1",
    parameters={"active": true}
)
```

### Example 2: MongoDB Connection

```python
# 1. Add MongoDB connection
add_connection(
    name="my_mongo",
    type="mongodb",
    host="localhost",
    port=27017,
    username="myuser",
    password="mypassword",
    database="mydb"
)

# 2. Find documents
find_documents(
    connection_name="my_mongo",
    collection_name="users",
    filter_query={"status": "active"},
    limit=10
)
```

### Example 3: SQLite Connection

```python
# 1. Add SQLite connection
add_connection(
    name="my_sqlite",
    type="sqlite",
    database="/path/to/database.db"
)

# 2. Get schema info
get_schema_info(connection_name="my_sqlite")
```

## 🔒 Security

- **Connection Security**: All connections support SSL/TLS encryption
- **Credential Management**: Passwords are handled securely and not logged
- **Connection Pooling**: Efficient connection management with automatic cleanup
- **Input Validation**: All inputs are validated using Pydantic models

## 🧪 Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/yourusername/mcp-database-server.git
cd mcp-database-server

# Install with uv
uv sync --dev

# Run tests
uv run pytest

# Format code
uv run black src/
uv run ruff check src/
```

### Project Structure

```
mcp-database-server/
├── src/mcp_database_server/
│   ├── __init__.py
│   ├── server.py              # Main MCP server
│   ├── connection_manager.py  # Connection management
│   ├── database_factory.py    # Database factory
│   ├── types.py              # Type definitions
│   ├── cli.py                # CLI interface
│   └── databases/            # Database drivers
│       ├── base.py           # Base classes
│       ├── postgresql.py     # PostgreSQL driver
│       ├── mysql.py          # MySQL driver
│       ├── sqlite.py         # SQLite driver
│       ├── mongodb.py        # MongoDB driver
│       └── redis.py          # Redis driver
├── tests/                    # Test files
├── pyproject.toml           # Project configuration
└── README.md
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Adding New Database Support

1. Create a new driver in `src/mcp_database_server/databases/`
2. Inherit from `SQLDatabase` or `NoSQLDatabase` base class
3. Implement all required methods
4. Register the driver in `database_factory.py`
5. Add appropriate dependencies to `pyproject.toml`
6. Write tests for the new driver

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/mcp-database-server/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/mcp-database-server/discussions)
- **Documentation**: [GitHub Wiki](https://github.com/yourusername/mcp-database-server/wiki)

## 🙏 Acknowledgments

- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) for the protocol specification
- All the amazing database driver maintainers
- The Python async ecosystem

---

Made with ❤️ for the AI and database communities
