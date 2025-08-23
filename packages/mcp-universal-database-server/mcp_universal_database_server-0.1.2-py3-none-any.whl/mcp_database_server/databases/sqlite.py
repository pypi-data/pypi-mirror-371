"""SQLite database driver."""

import time
import aiosqlite
from typing import Any, Dict, List, Optional, Union

from .base import SQLDatabase
from ..types import (
    ConnectionConfig,
    QueryResult,
    SchemaInfo,
    TableInfo,
    QueryParameters,
)


class SQLiteDatabase(SQLDatabase):
    """SQLite database implementation."""

    def __init__(self, config: ConnectionConfig):
        """Initialize SQLite connection."""
        super().__init__(config)
        self.connection: Optional[aiosqlite.Connection] = None

    async def connect(self) -> None:
        """Establish SQLite connection."""
        try:
            # For SQLite, the database parameter is the file path
            db_path = self.config.database or ":memory:"
            self.connection = await aiosqlite.connect(db_path)
            # Enable foreign keys
            await self.connection.execute("PRAGMA foreign_keys = ON")
            await self.connection.commit()
            self.is_connected = True
        except Exception as e:
            raise ConnectionError(f"Failed to connect to SQLite: {e}")

    async def disconnect(self) -> None:
        """Close SQLite connection."""
        if self.connection:
            await self.connection.close()
            self.connection = None
        self.is_connected = False

    async def execute_query(
        self,
        query: str,
        parameters: Optional[QueryParameters] = None,
        fetch: bool = True,
    ) -> QueryResult:
        """Execute SQLite query."""
        if not self.connection:
            raise ConnectionError("Database not connected")

        start_time = time.time()

        try:
            if parameters:
                # Convert named parameters to positional for SQLite
                param_values = list(parameters.values())
                cursor = await self.connection.execute(query, param_values)
            else:
                cursor = await self.connection.execute(query)

            if fetch:
                rows = await cursor.fetchall()
                # Get column names
                columns = (
                    [description[0] for description in cursor.description]
                    if cursor.description
                    else []
                )

                # Convert rows to dictionaries
                data = [dict(zip(columns, row)) for row in rows]

                return QueryResult(
                    success=True,
                    data=data,
                    affected_rows=len(data),
                    execution_time=time.time() - start_time,
                )
            else:
                await self.connection.commit()
                affected_rows = cursor.rowcount

                return QueryResult(
                    success=True,
                    affected_rows=affected_rows,
                    execution_time=time.time() - start_time,
                )

        except Exception as e:
            return QueryResult(
                success=False, error=str(e), execution_time=time.time() - start_time
            )

    async def execute_many(
        self, query: str, parameters_list: List[QueryParameters]
    ) -> QueryResult:
        """Execute query multiple times with different parameters."""
        if not self.connection:
            raise ConnectionError("Database not connected")

        start_time = time.time()

        try:
            param_values_list = [list(params.values()) for params in parameters_list]
            cursor = await self.connection.executemany(query, param_values_list)
            await self.connection.commit()

            return QueryResult(
                success=True,
                affected_rows=cursor.rowcount,
                execution_time=time.time() - start_time,
            )

        except Exception as e:
            return QueryResult(
                success=False, error=str(e), execution_time=time.time() - start_time
            )

    async def get_schema_info(self, schema: Optional[str] = None) -> SchemaInfo:
        """Get SQLite schema information."""
        # Get tables
        tables_query = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        tables_result = await self.execute_query(tables_query)
        tables = [row["name"] for row in (tables_result.data or [])]

        # Get views
        views_query = "SELECT name FROM sqlite_master WHERE type='view' ORDER BY name"
        views_result = await self.execute_query(views_query)
        views = [row["name"] for row in (views_result.data or [])]

        return SchemaInfo(
            tables=tables,
            views=views,
            functions=[],  # SQLite doesn't have stored functions like PostgreSQL
            procedures=[],  # SQLite doesn't have stored procedures
        )

    async def get_table_info(
        self, table_name: str, schema: Optional[str] = None
    ) -> TableInfo:
        """Get detailed SQLite table information."""
        # Get columns
        columns_query = f"PRAGMA table_info({table_name})"
        columns_result = await self.execute_query(columns_query)

        columns = []
        for col in columns_result.data or []:
            columns.append(
                {
                    "column_name": col["name"],
                    "data_type": col["type"],
                    "is_nullable": "YES" if not col["notnull"] else "NO",
                    "column_default": col["dflt_value"],
                    "is_primary_key": bool(col["pk"]),
                }
            )

        # Get indexes
        indexes_query = f"PRAGMA index_list({table_name})"
        indexes_result = await self.execute_query(indexes_query)

        indexes = []
        for idx in indexes_result.data or []:
            # Get index info
            index_info_query = f"PRAGMA index_info({idx['name']})"
            index_info_result = await self.execute_query(index_info_query)

            indexes.append(
                {
                    "index_name": idx["name"],
                    "is_unique": bool(idx["unique"]),
                    "columns": [
                        info["name"] for info in (index_info_result.data or [])
                    ],
                }
            )

        # Get row count
        count_query = f"SELECT COUNT(*) as count FROM {table_name}"
        count_result = await self.execute_query(count_query)
        row_count = count_result.data[0]["count"] if count_result.data else 0

        return TableInfo(
            name=table_name,
            columns=columns,
            indexes=indexes,
            constraints=[],  # TODO: Implement constraints query
            row_count=row_count,
        )

    async def list_databases(self) -> List[str]:
        """List SQLite databases (always returns current database)."""
        return [self.config.database or ":memory:"]

    async def list_schemas(self, database: Optional[str] = None) -> List[str]:
        """List SQLite schemas (always returns 'main')."""
        return ["main"]

    async def list_tables(self, schema: Optional[str] = None) -> List[str]:
        """List SQLite tables."""
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        result = await self.execute_query(query)
        return [row["name"] for row in (result.data or [])]

    async def test_connection(self) -> bool:
        """Test SQLite connection."""
        try:
            result = await self.execute_query("SELECT 1 as test")
            return result.success and result.data and result.data[0]["test"] == 1
        except Exception:
            return False

    # SQL-specific methods
    async def create_table(
        self,
        table_name: str,
        columns: Dict[str, str],
        schema: Optional[str] = None,
        **kwargs,
    ) -> QueryResult:
        """Create SQLite table."""
        columns_def = ", ".join(
            [f"{col} {col_type}" for col, col_type in columns.items()]
        )
        query = f"CREATE TABLE {table_name} ({columns_def})"

        return await self.execute_query(query, fetch=False)

    async def drop_table(
        self, table_name: str, schema: Optional[str] = None, if_exists: bool = False
    ) -> QueryResult:
        """Drop SQLite table."""
        if_exists_clause = "IF EXISTS" if if_exists else ""
        query = f"DROP TABLE {if_exists_clause} {table_name}"

        return await self.execute_query(query, fetch=False)

    async def insert_data(
        self,
        table_name: str,
        data: Union[Dict[str, Any], List[Dict[str, Any]]],
        schema: Optional[str] = None,
    ) -> QueryResult:
        """Insert data into SQLite table."""
        if isinstance(data, dict):
            data = [data]

        if not data:
            return QueryResult(success=True, affected_rows=0)

        # Build INSERT query
        columns = list(data[0].keys())
        columns_str = ", ".join(columns)
        placeholders = ", ".join(["?" for _ in columns])

        query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"

        if len(data) == 1:
            params = {str(i): data[0][col] for i, col in enumerate(columns)}
            return await self.execute_query(query, params, fetch=False)
        else:
            params_list = [
                {str(i): row[col] for i, col in enumerate(columns)} for row in data
            ]
            return await self.execute_many(query, params_list)

    async def update_data(
        self,
        table_name: str,
        data: Dict[str, Any],
        where_clause: str,
        parameters: Optional[QueryParameters] = None,
        schema: Optional[str] = None,
    ) -> QueryResult:
        """Update data in SQLite table."""
        set_clauses = [f"{col} = ?" for col in data.keys()]
        set_clause = ", ".join(set_clauses)

        query = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"

        # Combine update data and where parameters
        all_params = {}
        param_counter = 0

        for value in data.values():
            all_params[str(param_counter)] = value
            param_counter += 1

        if parameters:
            for value in parameters.values():
                all_params[str(param_counter)] = value
                param_counter += 1

        return await self.execute_query(query, all_params, fetch=False)

    async def delete_data(
        self,
        table_name: str,
        where_clause: str,
        parameters: Optional[QueryParameters] = None,
        schema: Optional[str] = None,
    ) -> QueryResult:
        """Delete data from SQLite table."""
        query = f"DELETE FROM {table_name} WHERE {where_clause}"

        return await self.execute_query(query, parameters, fetch=False)
