"""Command-line interface for MCP Database Server."""

import asyncio
import json
import sys
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table
from rich import print as rprint

from .server import DatabaseMCPServer
from .types import ConnectionConfig, DatabaseType


app = typer.Typer(help="MCP Database Server - Universal database connection server")
console = Console()

# Connection configuration file path
CONNECTIONS_FILE = Path.home() / ".mcp_database_connections.json"


def load_connections():
    """Load saved connections from file."""
    if not CONNECTIONS_FILE.exists():
        return {}

    try:
        with open(CONNECTIONS_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        console.print(f"❌ Error loading connections: {e}", style="bold red")
        return {}


def save_connections(connections):
    """Save connections to file."""
    try:
        with open(CONNECTIONS_FILE, "w") as f:
            json.dump(connections, f, indent=2)
        return True
    except Exception as e:
        console.print(f"❌ Error saving connections: {e}", style="bold red")
        return False


@app.command()
def serve():
    """Start the MCP Database Server."""
    console.print("🚀 Starting MCP Database Server...", style="bold green")

    try:
        asyncio.run(DatabaseMCPServer().run())
    except KeyboardInterrupt:
        console.print("\n👋 Server stopped", style="bold yellow")
    except Exception as e:
        console.print(f"❌ Server error: {e}", style="bold red")
        sys.exit(1)


@app.command()
def add_connection(
    name: str = typer.Argument(..., help="Connection name/identifier"),
    db_type: DatabaseType = typer.Option(..., "--type", help="Database type"),
    host: str = typer.Option("localhost", help="Database host"),
    port: Optional[int] = typer.Option(None, help="Database port"),
    username: Optional[str] = typer.Option(None, help="Username"),
    password: Optional[str] = typer.Option(None, help="Password"),
    database: Optional[str] = typer.Option(None, help="Database name"),
    schema: Optional[str] = typer.Option(None, help="Schema name"),
    ssl: bool = typer.Option(True, help="Use SSL connection"),
    no_ssl: bool = typer.Option(False, "--no-ssl", help="Disable SSL connection"),
):
    """Add a new database connection configuration."""

    # Handle SSL flag
    use_ssl = ssl and not no_ssl

    # Load existing connections
    connections = load_connections()

    # Check if connection already exists
    if name in connections:
        if not typer.confirm(f"Connection '{name}' already exists. Overwrite?"):
            console.print("❌ Operation cancelled", style="bold yellow")
            return

    # Create connection config
    connection_data = {
        "type": db_type.value,
        "host": host,
        "username": username,
        "database": database,
        "ssl": use_ssl,
    }

    # Add optional fields
    if port:
        connection_data["port"] = port
    if password:
        connection_data["password"] = password
    if schema:
        connection_data["schema"] = schema

    # Save connection
    connections[name] = connection_data

    if save_connections(connections):
        console.print(f"✅ Connection '{name}' saved successfully!", style="bold green")
        console.print(f"📁 Saved to: {CONNECTIONS_FILE}", style="dim")
    else:
        console.print(f"❌ Failed to save connection '{name}'", style="bold red")


@app.command()
def list_connections():
    """List all saved database connections."""
    connections = load_connections()

    if not connections:
        console.print("📭 No saved connections found", style="bold yellow")
        console.print(f"💡 Use 'add-connection' to save a connection", style="dim")
        return

    table = Table(title="Saved Database Connections")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Type", style="magenta")
    table.add_column("Host", style="green")
    table.add_column("Port", style="blue")
    table.add_column("Database", style="yellow")
    table.add_column("Username", style="red")
    table.add_column("SSL", style="white")

    for name, config in connections.items():
        table.add_row(
            name,
            config.get("type", "unknown"),
            config.get("host", "N/A"),
            str(config.get("port", "default")),
            config.get("database", "N/A"),
            config.get("username", "N/A"),
            "✅" if config.get("ssl", False) else "❌",
        )

    console.print(table)


@app.command()
def remove_connection(
    name: str = typer.Argument(..., help="Connection name to remove")
):
    """Remove a saved database connection."""
    connections = load_connections()

    if name not in connections:
        console.print(f"❌ Connection '{name}' not found", style="bold red")
        return

    if typer.confirm(f"Are you sure you want to remove connection '{name}'?"):
        del connections[name]
        if save_connections(connections):
            console.print(
                f"✅ Connection '{name}' removed successfully!", style="bold green"
            )
        else:
            console.print(f"❌ Failed to remove connection '{name}'", style="bold red")
    else:
        console.print("❌ Operation cancelled", style="bold yellow")


@app.command()
def test_connection(
    name: str = typer.Argument(..., help="Connection name or identifier"),
    db_type: Optional[DatabaseType] = typer.Option(
        None, "--type", help="Database type (required if not using saved connection)"
    ),
    host: str = typer.Option("localhost", help="Database host"),
    port: Optional[int] = typer.Option(None, help="Database port"),
    username: Optional[str] = typer.Option(None, help="Username"),
    password: Optional[str] = typer.Option(None, help="Password"),
    database: Optional[str] = typer.Option(None, help="Database name"),
    ssl: bool = typer.Option(False, help="Use SSL connection"),
):
    """Test a database connection (saved or new)."""

    async def _test():
        from .database_factory import DatabaseFactory

        # Try to load saved connection first
        connections = load_connections()

        if name in connections:
            # Use saved connection
            saved_config = connections[name]
            console.print(f"🔍 Testing saved connection '{name}'...", style="bold blue")

            config = ConnectionConfig(
                name=name,
                type=DatabaseType(saved_config["type"]),
                host=saved_config.get("host", "localhost"),
                port=saved_config.get("port"),
                username=saved_config.get("username"),
                password=saved_config.get("password"),
                database=saved_config.get("database"),
                ssl=saved_config.get("ssl", False),
            )
        else:
            # Use provided parameters
            if not db_type:
                console.print(
                    "❌ Database type is required when not using a saved connection",
                    style="bold red",
                )
                console.print(
                    "💡 Use --type option or save the connection first with 'add-connection'",
                    style="dim",
                )
                sys.exit(1)

            console.print(
                f"🔍 Testing new connection to {db_type.value} database...",
                style="bold blue",
            )

            config = ConnectionConfig(
                name=name,
                type=db_type,
                host=host,
                port=port,
                username=username,
                password=password,
                database=database,
                ssl=ssl,
            )

        console.print(
            f"🔍 Testing connection to {config.type} database...",
            style="bold blue",
        )

        try:
            db = await DatabaseFactory.create_database(config)
            success = await db.test_connection()
            await db.disconnect()

            if success:
                console.print("✅ Connection test successful!", style="bold green")
                return True
            else:
                console.print("❌ Connection test failed!", style="bold red")
                return False

        except Exception as e:
            console.print(f"❌ Connection error: {e}", style="bold red")
            return False

    success = asyncio.run(_test())
    sys.exit(0 if success else 1)


@app.command()
def list_supported():
    """List supported database types."""
    from .database_factory import DatabaseFactory

    supported_types = DatabaseFactory.get_supported_types()

    console.print("🗃️  Supported Database Types:", style="bold blue")
    console.print()

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Database Type", style="cyan")
    table.add_column("Description", style="green")

    type_descriptions = {
        DatabaseType.POSTGRESQL: "PostgreSQL - Advanced open-source relational database",
        DatabaseType.MYSQL: "MySQL - Popular open-source relational database",
        DatabaseType.SQLITE: "SQLite - Lightweight file-based SQL database",
        DatabaseType.MONGODB: "MongoDB - Document-oriented NoSQL database",
        DatabaseType.REDIS: "Redis - In-memory key-value store",
        DatabaseType.MSSQL: "Microsoft SQL Server - Enterprise relational database",
        DatabaseType.ORACLE: "Oracle Database - Enterprise relational database",
        DatabaseType.CASSANDRA: "Apache Cassandra - Distributed NoSQL database",
        DatabaseType.FIRESTORE: "Google Firestore - Cloud document database",
        DatabaseType.DYNAMODB: "Amazon DynamoDB - Cloud NoSQL database",
        DatabaseType.COSMOSDB: "Azure Cosmos DB - Multi-model cloud database",
    }

    for db_type in supported_types:
        description = type_descriptions.get(db_type, "Database type")
        table.add_row(db_type.value, description)

    console.print(table)


@app.command()
def generate_config(
    output: str = typer.Option("mcp_database_config.json", help="Output file path"),
    host: str = typer.Option("localhost", help="Default host"),
    port: int = typer.Option(5432, help="Default port"),
):
    """Generate a sample configuration file."""

    config = {
        "mcpServers": {
            "mcp-database-server": {
                "command": "mcp-database-server",
                "args": ["serve"],
                "env": {"MCP_DATABASE_LOG_LEVEL": "INFO"},
            }
        },
        "connections": {
            "example_postgresql": {
                "name": "example_postgresql",
                "type": "postgresql",
                "host": host,
                "port": port,
                "username": "your_username",
                "password": "your_password",
                "database": "your_database",
                "ssl": False,
            },
            "example_mongodb": {
                "name": "example_mongodb",
                "type": "mongodb",
                "host": host,
                "port": 27017,
                "username": "your_username",
                "password": "your_password",
                "database": "your_database",
                "ssl": False,
            },
            "example_sqlite": {
                "name": "example_sqlite",
                "type": "sqlite",
                "database": "/path/to/your/database.db",
            },
        },
    }

    try:
        with open(output, "w") as f:
            json.dump(config, f, indent=2)

        console.print(f"✅ Generated configuration file: {output}", style="bold green")
        console.print(
            "📝 Edit the file to add your actual database credentials", style="yellow"
        )

    except Exception as e:
        console.print(f"❌ Failed to generate config: {e}", style="bold red")
        sys.exit(1)


@app.command()
def version():
    """Show version information."""
    from . import __version__

    console.print(f"🔧 MCP Database Server v{__version__}", style="bold blue")
    console.print("Universal database connection server for MCP", style="dim")


def main():
    """Main CLI entry point."""
    app()


if __name__ == "__main__":
    main()
