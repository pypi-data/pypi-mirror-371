"""MCP Database Server implementation."""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Sequence
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import Tool, TextContent, CallToolResult, ListToolsResult
import mcp.server.stdio
import mcp.types as types

from .connection_manager import ConnectionManager
from .types import ConnectionConfig, DatabaseType, QueryParameters
from .databases.base import BaseDatabase, SQLDatabase, NoSQLDatabase


logger = logging.getLogger(__name__)


class DatabaseMCPServer:
    """MCP Server for database operations."""

    def __init__(self):
        """Initialize the MCP database server."""
        self.server = Server("mcp-database-server")
        self.connection_manager = ConnectionManager()
        self._setup_handlers()

    def _setup_handlers(self) -> None:
        """Set up MCP server handlers."""

        @self.server.list_tools()
        async def handle_list_tools() -> list[Tool]:
            """List available database tools."""
            return [
                Tool(
                    name="add_connection",
                    description="Add a new database connection configuration",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Connection name/identifier",
                            },
                            "type": {
                                "type": "string",
                                "enum": [t.value for t in DatabaseType],
                                "description": "Database type",
                            },
                            "host": {"type": "string", "description": "Database host"},
                            "port": {"type": "integer", "description": "Database port"},
                            "username": {"type": "string", "description": "Username"},
                            "password": {"type": "string", "description": "Password"},
                            "database": {
                                "type": "string",
                                "description": "Database name",
                            },
                            "schema": {
                                "type": "string",
                                "description": "Schema name (optional)",
                            },
                            "ssl": {
                                "type": "boolean",
                                "description": "Use SSL connection",
                                "default": False,
                            },
                            "options": {
                                "type": "object",
                                "description": "Additional connection options",
                                "default": {},
                            },
                        },
                        "required": ["name", "type"],
                    },
                ),
                Tool(
                    name="remove_connection",
                    description="Remove a database connection",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Connection name to remove",
                            }
                        },
                        "required": ["name"],
                    },
                ),
                Tool(
                    name="list_connections",
                    description="List all configured database connections",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "additionalProperties": False,
                    },
                ),
                Tool(
                    name="test_connection",
                    description="Test a database connection",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Connection name to test",
                            }
                        },
                        "required": ["name"],
                    },
                ),
                Tool(
                    name="execute_query",
                    description="Execute a SQL query or database command",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "connection_name": {
                                "type": "string",
                                "description": "Connection name to use",
                            },
                            "query": {
                                "type": "string",
                                "description": "SQL query or database command",
                            },
                            "parameters": {
                                "type": "object",
                                "description": "Query parameters",
                                "default": {},
                            },
                            "fetch": {
                                "type": "boolean",
                                "description": "Whether to fetch results",
                                "default": True,
                            },
                        },
                        "required": ["connection_name", "query"],
                    },
                ),
                Tool(
                    name="get_schema_info",
                    description="Get database schema information",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "connection_name": {
                                "type": "string",
                                "description": "Connection name to use",
                            },
                            "schema": {
                                "type": "string",
                                "description": "Schema name (optional)",
                            },
                        },
                        "required": ["connection_name"],
                    },
                ),
                Tool(
                    name="get_table_info",
                    description="Get detailed table information",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "connection_name": {
                                "type": "string",
                                "description": "Connection name to use",
                            },
                            "table_name": {
                                "type": "string",
                                "description": "Table name",
                            },
                            "schema": {
                                "type": "string",
                                "description": "Schema name (optional)",
                            },
                        },
                        "required": ["connection_name", "table_name"],
                    },
                ),
                Tool(
                    name="list_databases",
                    description="List available databases",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "connection_name": {
                                "type": "string",
                                "description": "Connection name to use",
                            }
                        },
                        "required": ["connection_name"],
                    },
                ),
                Tool(
                    name="list_tables",
                    description="List tables in a database/schema",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "connection_name": {
                                "type": "string",
                                "description": "Connection name to use",
                            },
                            "schema": {
                                "type": "string",
                                "description": "Schema name (optional)",
                            },
                        },
                        "required": ["connection_name"],
                    },
                ),
                Tool(
                    name="create_table",
                    description="Create a new table (SQL databases only)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "connection_name": {
                                "type": "string",
                                "description": "Connection name to use",
                            },
                            "table_name": {
                                "type": "string",
                                "description": "Table name",
                            },
                            "columns": {
                                "type": "object",
                                "description": "Column definitions (name: type)",
                            },
                            "schema": {
                                "type": "string",
                                "description": "Schema name (optional)",
                            },
                        },
                        "required": ["connection_name", "table_name", "columns"],
                    },
                ),
                Tool(
                    name="drop_table",
                    description="Drop a table (SQL databases only)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "connection_name": {
                                "type": "string",
                                "description": "Connection name to use",
                            },
                            "table_name": {
                                "type": "string",
                                "description": "Table name",
                            },
                            "schema": {
                                "type": "string",
                                "description": "Schema name (optional)",
                            },
                            "if_exists": {
                                "type": "boolean",
                                "description": "Only drop if exists",
                                "default": False,
                            },
                        },
                        "required": ["connection_name", "table_name"],
                    },
                ),
                Tool(
                    name="insert_data",
                    description="Insert data into a table",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "connection_name": {
                                "type": "string",
                                "description": "Connection name to use",
                            },
                            "table_name": {
                                "type": "string",
                                "description": "Table name",
                            },
                            "data": {
                                "type": ["object", "array"],
                                "description": "Data to insert (single object or array)",
                            },
                            "schema": {
                                "type": "string",
                                "description": "Schema name (optional)",
                            },
                        },
                        "required": ["connection_name", "table_name", "data"],
                    },
                ),
                Tool(
                    name="update_data",
                    description="Update data in a table (SQL databases only)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "connection_name": {
                                "type": "string",
                                "description": "Connection name to use",
                            },
                            "table_name": {
                                "type": "string",
                                "description": "Table name",
                            },
                            "data": {"type": "object", "description": "Data to update"},
                            "where_clause": {
                                "type": "string",
                                "description": "WHERE clause",
                            },
                            "parameters": {
                                "type": "object",
                                "description": "WHERE clause parameters",
                                "default": {},
                            },
                            "schema": {
                                "type": "string",
                                "description": "Schema name (optional)",
                            },
                        },
                        "required": [
                            "connection_name",
                            "table_name",
                            "data",
                            "where_clause",
                        ],
                    },
                ),
                Tool(
                    name="delete_data",
                    description="Delete data from a table",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "connection_name": {
                                "type": "string",
                                "description": "Connection name to use",
                            },
                            "table_name": {
                                "type": "string",
                                "description": "Table name",
                            },
                            "where_clause": {
                                "type": "string",
                                "description": "WHERE clause or filter",
                            },
                            "parameters": {
                                "type": "object",
                                "description": "WHERE clause parameters",
                                "default": {},
                            },
                            "schema": {
                                "type": "string",
                                "description": "Schema name (optional)",
                            },
                        },
                        "required": ["connection_name", "table_name", "where_clause"],
                    },
                ),
                Tool(
                    name="create_collection",
                    description="Create a collection (NoSQL databases only)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "connection_name": {
                                "type": "string",
                                "description": "Connection name to use",
                            },
                            "collection_name": {
                                "type": "string",
                                "description": "Collection name",
                            },
                            "options": {
                                "type": "object",
                                "description": "Collection options",
                                "default": {},
                            },
                        },
                        "required": ["connection_name", "collection_name"],
                    },
                ),
                Tool(
                    name="find_documents",
                    description="Find documents in a collection (NoSQL databases only)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "connection_name": {
                                "type": "string",
                                "description": "Connection name to use",
                            },
                            "collection_name": {
                                "type": "string",
                                "description": "Collection name",
                            },
                            "filter_query": {
                                "type": "object",
                                "description": "Filter query",
                                "default": {},
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Limit results",
                            },
                            "skip": {"type": "integer", "description": "Skip results"},
                            "sort": {
                                "type": "object",
                                "description": "Sort specification",
                            },
                        },
                        "required": ["connection_name", "collection_name"],
                    },
                ),
                Tool(
                    name="update_documents",
                    description="Update documents in a collection (NoSQL databases only)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "connection_name": {
                                "type": "string",
                                "description": "Connection name to use",
                            },
                            "collection_name": {
                                "type": "string",
                                "description": "Collection name",
                            },
                            "filter_query": {
                                "type": "object",
                                "description": "Filter query",
                            },
                            "update_data": {
                                "type": "object",
                                "description": "Update data",
                            },
                            "upsert": {
                                "type": "boolean",
                                "description": "Create if not exists",
                                "default": False,
                            },
                        },
                        "required": [
                            "connection_name",
                            "collection_name",
                            "filter_query",
                            "update_data",
                        ],
                    },
                ),
                Tool(
                    name="get_supported_types",
                    description="Get list of supported database types",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "additionalProperties": False,
                    },
                ),
            ]

        @self.server.call_tool()
        async def handle_call_tool(
            name: str, arguments: dict
        ) -> list[types.TextContent]:
            """Handle tool calls."""
            try:
                if name == "add_connection":
                    return await self._handle_add_connection(arguments)
                elif name == "remove_connection":
                    return await self._handle_remove_connection(arguments)
                elif name == "list_connections":
                    return await self._handle_list_connections(arguments)
                elif name == "test_connection":
                    return await self._handle_test_connection(arguments)
                elif name == "execute_query":
                    return await self._handle_execute_query(arguments)
                elif name == "get_schema_info":
                    return await self._handle_get_schema_info(arguments)
                elif name == "get_table_info":
                    return await self._handle_get_table_info(arguments)
                elif name == "list_databases":
                    return await self._handle_list_databases(arguments)
                elif name == "list_tables":
                    return await self._handle_list_tables(arguments)
                elif name == "create_table":
                    return await self._handle_create_table(arguments)
                elif name == "drop_table":
                    return await self._handle_drop_table(arguments)
                elif name == "insert_data":
                    return await self._handle_insert_data(arguments)
                elif name == "update_data":
                    return await self._handle_update_data(arguments)
                elif name == "delete_data":
                    return await self._handle_delete_data(arguments)
                elif name == "create_collection":
                    return await self._handle_create_collection(arguments)
                elif name == "find_documents":
                    return await self._handle_find_documents(arguments)
                elif name == "update_documents":
                    return await self._handle_update_documents(arguments)
                elif name == "get_supported_types":
                    return await self._handle_get_supported_types(arguments)
                else:
                    return [TextContent(type="text", text=f"Unknown tool: {name}")]

            except Exception as e:
                logger.error(f"Error handling tool {name}: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]

    # Tool handlers
    async def _handle_add_connection(self, args: dict) -> list[types.TextContent]:
        """Handle add_connection tool."""
        try:
            config = ConnectionConfig(**args)
            success = await self.connection_manager.add_connection(config)

            if success:
                return [
                    TextContent(
                        type="text",
                        text=f"Successfully added connection '{config.name}' ({config.type})",
                    )
                ]
            else:
                return [
                    TextContent(
                        type="text", text=f"Failed to add connection '{config.name}'"
                    )
                ]

        except Exception as e:
            return [TextContent(type="text", text=f"Error adding connection: {str(e)}")]

    async def _handle_remove_connection(self, args: dict) -> list[types.TextContent]:
        """Handle remove_connection tool."""
        name = args.get("name")
        success = await self.connection_manager.remove_connection(name)

        if success:
            return [
                TextContent(
                    type="text", text=f"Successfully removed connection '{name}'"
                )
            ]
        else:
            return [
                TextContent(type="text", text=f"Failed to remove connection '{name}'")
            ]

    async def _handle_list_connections(self, args: dict) -> list[types.TextContent]:
        """Handle list_connections tool."""
        connections = self.connection_manager.list_connections()

        if not connections:
            return [TextContent(type="text", text="No connections configured")]

        result = "Configured connections:\n\n"
        for conn in connections:
            status = "✓ Connected" if conn["is_connected"] else "○ Disconnected"
            result += f"• {conn['name']} ({conn['type']}) - {status}\n"
            result += f"  Host: {conn['host']}:{conn['port']}\n"
            result += f"  Database: {conn['database']}\n\n"

        return [TextContent(type="text", text=result)]

    async def _handle_test_connection(self, args: dict) -> list[types.TextContent]:
        """Handle test_connection tool."""
        name = args.get("name")
        success = await self.connection_manager.test_connection(name)

        if success:
            return [
                TextContent(type="text", text=f"Connection '{name}' test successful ✓")
            ]
        else:
            return [TextContent(type="text", text=f"Connection '{name}' test failed ✗")]

    async def _handle_execute_query(self, args: dict) -> list[types.TextContent]:
        """Handle execute_query tool."""
        connection_name = args.get("connection_name")
        query = args.get("query")
        parameters = args.get("parameters", {})
        fetch = args.get("fetch", True)

        db = await self.connection_manager.get_connection(connection_name)
        if not db:
            return [
                TextContent(
                    type="text", text=f"Connection '{connection_name}' not available"
                )
            ]

        result = await db.execute_query(query, parameters, fetch)

        if result.success:
            response = f"Query executed successfully\n"
            response += f"Execution time: {result.execution_time:.3f}s\n"

            if result.data:
                response += f"Results ({len(result.data)} rows):\n"
                response += json.dumps(result.data, indent=2, default=str)
            elif result.affected_rows is not None:
                response += f"Affected rows: {result.affected_rows}\n"

            return [TextContent(type="text", text=response)]
        else:
            return [TextContent(type="text", text=f"Query failed: {result.error}")]

    async def _handle_get_schema_info(self, args: dict) -> list[types.TextContent]:
        """Handle get_schema_info tool."""
        connection_name = args.get("connection_name")
        schema = args.get("schema")

        db = await self.connection_manager.get_connection(connection_name)
        if not db:
            return [
                TextContent(
                    type="text", text=f"Connection '{connection_name}' not available"
                )
            ]

        try:
            schema_info = await db.get_schema_info(schema)

            response = f"Schema information for '{connection_name}'"
            if schema:
                response += f" (schema: {schema})"
            response += ":\n\n"

            if schema_info.tables:
                response += f"Tables ({len(schema_info.tables)}):\n"
                for table in schema_info.tables:
                    response += f"  • {table}\n"
                response += "\n"

            if schema_info.views:
                response += f"Views ({len(schema_info.views)}):\n"
                for view in schema_info.views:
                    response += f"  • {view}\n"
                response += "\n"

            if schema_info.functions:
                response += f"Functions ({len(schema_info.functions)}):\n"
                for func in schema_info.functions:
                    response += f"  • {func}\n"
                response += "\n"

            if schema_info.procedures:
                response += f"Procedures ({len(schema_info.procedures)}):\n"
                for proc in schema_info.procedures:
                    response += f"  • {proc}\n"

            return [TextContent(type="text", text=response)]

        except Exception as e:
            return [
                TextContent(type="text", text=f"Error getting schema info: {str(e)}")
            ]

    async def _handle_get_table_info(self, args: dict) -> list[types.TextContent]:
        """Handle get_table_info tool."""
        connection_name = args.get("connection_name")
        table_name = args.get("table_name")
        schema = args.get("schema")

        db = await self.connection_manager.get_connection(connection_name)
        if not db:
            return [
                TextContent(
                    type="text", text=f"Connection '{connection_name}' not available"
                )
            ]

        try:
            table_info = await db.get_table_info(table_name, schema)

            response = f"Table information for '{table_name}'"
            if schema:
                response += f" (schema: {schema})"
            response += f":\n\n"

            if table_info.row_count is not None:
                response += f"Row count: {table_info.row_count:,}\n\n"

            if table_info.columns:
                response += f"Columns ({len(table_info.columns)}):\n"
                for col in table_info.columns:
                    col_name = col.get("column_name", "unknown")
                    col_type = col.get("data_type", "unknown")
                    nullable = col.get("is_nullable", "unknown")
                    response += f"  • {col_name} ({col_type}) - Nullable: {nullable}\n"
                response += "\n"

            if table_info.indexes:
                response += f"Indexes ({len(table_info.indexes)}):\n"
                for idx in table_info.indexes:
                    idx_name = idx.get("index_name", "unknown")
                    unique = idx.get("is_unique", False)
                    unique_str = "UNIQUE" if unique else "NON-UNIQUE"
                    response += f"  • {idx_name} ({unique_str})\n"
                response += "\n"

            return [TextContent(type="text", text=response)]

        except Exception as e:
            return [
                TextContent(type="text", text=f"Error getting table info: {str(e)}")
            ]

    async def _handle_list_databases(self, args: dict) -> list[types.TextContent]:
        """Handle list_databases tool."""
        connection_name = args.get("connection_name")

        db = await self.connection_manager.get_connection(connection_name)
        if not db:
            return [
                TextContent(
                    type="text", text=f"Connection '{connection_name}' not available"
                )
            ]

        try:
            databases = await db.list_databases()

            if not databases:
                return [TextContent(type="text", text="No databases found")]

            response = f"Databases in '{connection_name}' ({len(databases)}):\n\n"
            for db_name in databases:
                response += f"• {db_name}\n"

            return [TextContent(type="text", text=response)]

        except Exception as e:
            return [TextContent(type="text", text=f"Error listing databases: {str(e)}")]

    async def _handle_list_tables(self, args: dict) -> list[types.TextContent]:
        """Handle list_tables tool."""
        connection_name = args.get("connection_name")
        schema = args.get("schema")

        db = await self.connection_manager.get_connection(connection_name)
        if not db:
            return [
                TextContent(
                    type="text", text=f"Connection '{connection_name}' not available"
                )
            ]

        try:
            tables = await db.list_tables(schema)

            if not tables:
                return [TextContent(type="text", text="No tables found")]

            response = f"Tables in '{connection_name}'"
            if schema:
                response += f" (schema: {schema})"
            response += f" ({len(tables)}):\n\n"

            for table in tables:
                response += f"• {table}\n"

            return [TextContent(type="text", text=response)]

        except Exception as e:
            return [TextContent(type="text", text=f"Error listing tables: {str(e)}")]

    async def _handle_create_table(self, args: dict) -> list[types.TextContent]:
        """Handle create_table tool."""
        connection_name = args.get("connection_name")
        table_name = args.get("table_name")
        columns = args.get("columns", {})
        schema = args.get("schema")

        db = await self.connection_manager.get_connection(connection_name)
        if not db:
            return [
                TextContent(
                    type="text", text=f"Connection '{connection_name}' not available"
                )
            ]

        if not isinstance(db, SQLDatabase):
            return [
                TextContent(
                    type="text", text="create_table is only supported for SQL databases"
                )
            ]

        try:
            result = await db.create_table(table_name, columns, schema)

            if result.success:
                return [
                    TextContent(
                        type="text", text=f"Table '{table_name}' created successfully"
                    )
                ]
            else:
                return [
                    TextContent(
                        type="text", text=f"Failed to create table: {result.error}"
                    )
                ]

        except Exception as e:
            return [TextContent(type="text", text=f"Error creating table: {str(e)}")]

    async def _handle_drop_table(self, args: dict) -> list[types.TextContent]:
        """Handle drop_table tool."""
        connection_name = args.get("connection_name")
        table_name = args.get("table_name")
        schema = args.get("schema")
        if_exists = args.get("if_exists", False)

        db = await self.connection_manager.get_connection(connection_name)
        if not db:
            return [
                TextContent(
                    type="text", text=f"Connection '{connection_name}' not available"
                )
            ]

        if not isinstance(db, SQLDatabase):
            return [
                TextContent(
                    type="text", text="drop_table is only supported for SQL databases"
                )
            ]

        try:
            result = await db.drop_table(table_name, schema, if_exists)

            if result.success:
                return [
                    TextContent(
                        type="text", text=f"Table '{table_name}' dropped successfully"
                    )
                ]
            else:
                return [
                    TextContent(
                        type="text", text=f"Failed to drop table: {result.error}"
                    )
                ]

        except Exception as e:
            return [TextContent(type="text", text=f"Error dropping table: {str(e)}")]

    async def _handle_insert_data(self, args: dict) -> list[types.TextContent]:
        """Handle insert_data tool."""
        connection_name = args.get("connection_name")
        table_name = args.get("table_name")
        data = args.get("data")
        schema = args.get("schema")

        db = await self.connection_manager.get_connection(connection_name)
        if not db:
            return [
                TextContent(
                    type="text", text=f"Connection '{connection_name}' not available"
                )
            ]

        try:
            if isinstance(db, SQLDatabase):
                result = await db.insert_data(table_name, data, schema)
            elif isinstance(db, NoSQLDatabase):
                result = await db.insert_document(table_name, data)
            else:
                return [
                    TextContent(
                        type="text",
                        text="insert_data not supported for this database type",
                    )
                ]

            if result.success:
                return [
                    TextContent(
                        type="text",
                        text=f"Data inserted successfully. Affected rows: {result.affected_rows}",
                    )
                ]
            else:
                return [
                    TextContent(
                        type="text", text=f"Failed to insert data: {result.error}"
                    )
                ]

        except Exception as e:
            return [TextContent(type="text", text=f"Error inserting data: {str(e)}")]

    async def _handle_update_data(self, args: dict) -> list[types.TextContent]:
        """Handle update_data tool."""
        connection_name = args.get("connection_name")
        table_name = args.get("table_name")
        data = args.get("data")
        where_clause = args.get("where_clause")
        parameters = args.get("parameters", {})
        schema = args.get("schema")

        db = await self.connection_manager.get_connection(connection_name)
        if not db:
            return [
                TextContent(
                    type="text", text=f"Connection '{connection_name}' not available"
                )
            ]

        if not isinstance(db, SQLDatabase):
            return [
                TextContent(
                    type="text", text="update_data is only supported for SQL databases"
                )
            ]

        try:
            result = await db.update_data(
                table_name, data, where_clause, parameters, schema
            )

            if result.success:
                return [
                    TextContent(
                        type="text",
                        text=f"Data updated successfully. Affected rows: {result.affected_rows}",
                    )
                ]
            else:
                return [
                    TextContent(
                        type="text", text=f"Failed to update data: {result.error}"
                    )
                ]

        except Exception as e:
            return [TextContent(type="text", text=f"Error updating data: {str(e)}")]

    async def _handle_delete_data(self, args: dict) -> list[types.TextContent]:
        """Handle delete_data tool."""
        connection_name = args.get("connection_name")
        table_name = args.get("table_name")
        where_clause = args.get("where_clause")
        parameters = args.get("parameters", {})
        schema = args.get("schema")

        db = await self.connection_manager.get_connection(connection_name)
        if not db:
            return [
                TextContent(
                    type="text", text=f"Connection '{connection_name}' not available"
                )
            ]

        try:
            if isinstance(db, SQLDatabase):
                result = await db.delete_data(
                    table_name, where_clause, parameters, schema
                )
            elif isinstance(db, NoSQLDatabase):
                # For NoSQL, where_clause should be a filter query (dict)
                import json

                filter_query = (
                    json.loads(where_clause)
                    if isinstance(where_clause, str)
                    else where_clause
                )
                result = await db.delete_documents(table_name, filter_query)
            else:
                return [
                    TextContent(
                        type="text",
                        text="delete_data not supported for this database type",
                    )
                ]

            if result.success:
                return [
                    TextContent(
                        type="text",
                        text=f"Data deleted successfully. Affected rows: {result.affected_rows}",
                    )
                ]
            else:
                return [
                    TextContent(
                        type="text", text=f"Failed to delete data: {result.error}"
                    )
                ]

        except Exception as e:
            return [TextContent(type="text", text=f"Error deleting data: {str(e)}")]

    async def _handle_create_collection(self, args: dict) -> list[types.TextContent]:
        """Handle create_collection tool."""
        connection_name = args.get("connection_name")
        collection_name = args.get("collection_name")
        options = args.get("options", {})

        db = await self.connection_manager.get_connection(connection_name)
        if not db:
            return [
                TextContent(
                    type="text", text=f"Connection '{connection_name}' not available"
                )
            ]

        if not isinstance(db, NoSQLDatabase):
            return [
                TextContent(
                    type="text",
                    text="create_collection is only supported for NoSQL databases",
                )
            ]

        try:
            result = await db.create_collection(collection_name, **options)

            if result.success:
                return [
                    TextContent(
                        type="text",
                        text=f"Collection '{collection_name}' created successfully",
                    )
                ]
            else:
                return [
                    TextContent(
                        type="text", text=f"Failed to create collection: {result.error}"
                    )
                ]

        except Exception as e:
            return [
                TextContent(type="text", text=f"Error creating collection: {str(e)}")
            ]

    async def _handle_find_documents(self, args: dict) -> list[types.TextContent]:
        """Handle find_documents tool."""
        connection_name = args.get("connection_name")
        collection_name = args.get("collection_name")
        filter_query = args.get("filter_query", {})
        limit = args.get("limit")
        skip = args.get("skip")
        sort = args.get("sort")

        db = await self.connection_manager.get_connection(connection_name)
        if not db:
            return [
                TextContent(
                    type="text", text=f"Connection '{connection_name}' not available"
                )
            ]

        if not isinstance(db, NoSQLDatabase):
            return [
                TextContent(
                    type="text",
                    text="find_documents is only supported for NoSQL databases",
                )
            ]

        try:
            result = await db.find_documents(
                collection_name, filter_query, limit, skip, sort
            )

            if result.success:
                response = f"Found {result.affected_rows} document(s)\n"
                if result.data:
                    response += json.dumps(result.data, indent=2, default=str)
                return [TextContent(type="text", text=response)]
            else:
                return [
                    TextContent(
                        type="text", text=f"Failed to find documents: {result.error}"
                    )
                ]

        except Exception as e:
            return [TextContent(type="text", text=f"Error finding documents: {str(e)}")]

    async def _handle_update_documents(self, args: dict) -> list[types.TextContent]:
        """Handle update_documents tool."""
        connection_name = args.get("connection_name")
        collection_name = args.get("collection_name")
        filter_query = args.get("filter_query")
        update_data = args.get("update_data")
        upsert = args.get("upsert", False)

        db = await self.connection_manager.get_connection(connection_name)
        if not db:
            return [
                TextContent(
                    type="text", text=f"Connection '{connection_name}' not available"
                )
            ]

        if not isinstance(db, NoSQLDatabase):
            return [
                TextContent(
                    type="text",
                    text="update_documents is only supported for NoSQL databases",
                )
            ]

        try:
            result = await db.update_documents(
                collection_name, filter_query, update_data, upsert
            )

            if result.success:
                return [
                    TextContent(
                        type="text",
                        text=f"Documents updated successfully. Affected: {result.affected_rows}",
                    )
                ]
            else:
                return [
                    TextContent(
                        type="text", text=f"Failed to update documents: {result.error}"
                    )
                ]

        except Exception as e:
            return [
                TextContent(type="text", text=f"Error updating documents: {str(e)}")
            ]

    async def _handle_get_supported_types(self, args: dict) -> list[types.TextContent]:
        """Handle get_supported_types tool."""
        supported_types = self.connection_manager.get_supported_types()

        response = "Supported database types:\n\n"
        for db_type in supported_types:
            response += f"• {db_type.value}\n"

        return [TextContent(type="text", text=response)]

    async def run(self) -> None:
        """Run the MCP server."""
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="mcp-database-server",
                    server_version="0.1.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )

    async def cleanup(self) -> None:
        """Cleanup server resources."""
        await self.connection_manager.cleanup()


async def main():
    """Main entry point for the server."""
    logging.basicConfig(level=logging.INFO)

    server = DatabaseMCPServer()

    try:
        await server.run()
    finally:
        await server.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
