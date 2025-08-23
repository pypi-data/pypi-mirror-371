"""Command-line interface for MCP Database Server."""

import asyncio
import json
import sys
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table
from rich import print as rprint

from .server import DatabaseMCPServer
from .types import ConnectionConfig, DatabaseType


app = typer.Typer(help="MCP Database Server - Universal database connection server")
console = Console()


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
def test_connection(
    name: str = typer.Argument(..., help="Connection name"),
    db_type: DatabaseType = typer.Option(..., "--type", help="Database type"),
    host: str = typer.Option("localhost", help="Database host"),
    port: Optional[int] = typer.Option(None, help="Database port"),
    username: Optional[str] = typer.Option(None, help="Username"),
    password: Optional[str] = typer.Option(None, help="Password"),
    database: Optional[str] = typer.Option(None, help="Database name"),
    ssl: bool = typer.Option(False, help="Use SSL connection"),
):
    """Test a database connection."""

    async def _test():
        from .database_factory import DatabaseFactory

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
            f"🔍 Testing connection to {db_type.value} database...", style="bold blue"
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
