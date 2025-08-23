"""Microsoft SQL Server database driver."""

import time
from typing import Any, Dict, List, Optional, Union
import aioodbc

from .base import SQLDatabase
from ..types import (
    ConnectionConfig,
    QueryResult,
    SchemaInfo,
    TableInfo,
    QueryParameters,
)


class MSSQLDatabase(SQLDatabase):
    """Microsoft SQL Server database implementation."""

    def __init__(self, config: ConnectionConfig):
        """Initialize SQL Server connection."""
        super().__init__(config)
        self.pool: Optional[aioodbc.Pool] = None

    async def connect(self) -> None:
        """Establish SQL Server connection pool."""
        try:
            dsn = self._build_dsn()
            self.pool = await aioodbc.create_pool(
                dsn=dsn,
                minsize=1,
                maxsize=self.config.pool_size,
                timeout=self.config.pool_timeout,
            )
            self.is_connected = True
        except Exception as e:
            raise ConnectionError(f"Failed to connect to SQL Server: {e}")

    async def disconnect(self) -> None:
        """Close SQL Server connection pool."""
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
            self.pool = None
        self.is_connected = False

    def _build_dsn(self) -> str:
        """Build SQL Server DSN."""
        # Build ODBC connection string
        dsn_parts = []

        # Driver - try to use the most recent available
        dsn_parts.append("DRIVER={ODBC Driver 18 for SQL Server}")

        if self.config.host:
            if self.config.port:
                dsn_parts.append(f"SERVER={self.config.host},{self.config.port}")
            else:
                dsn_parts.append(f"SERVER={self.config.host}")

        if self.config.database:
            dsn_parts.append(f"DATABASE={self.config.database}")

        if self.config.username:
            dsn_parts.append(f"UID={self.config.username}")

        if self.config.password:
            dsn_parts.append(f"PWD={self.config.password}")

        # SSL/Encryption settings
        if self.config.ssl:
            dsn_parts.append("Encrypt=yes")
            dsn_parts.append("TrustServerCertificate=no")
        else:
            dsn_parts.append("Encrypt=no")

        # Additional options
        dsn_parts.append("Connection Timeout=30")

        # Add any additional options
        for key, value in self.config.options.items():
            dsn_parts.append(f"{key}={value}")

        return ";".join(dsn_parts)

    async def execute_query(
        self,
        query: str,
        parameters: Optional[QueryParameters] = None,
        fetch: bool = True,
    ) -> QueryResult:
        """Execute SQL Server query."""
        if not self.pool:
            raise ConnectionError("Database not connected")

        start_time = time.time()

        try:
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    if parameters:
                        # Convert named parameters to positional for SQL Server
                        param_values = list(parameters.values())
                        await cursor.execute(query, param_values)
                    else:
                        await cursor.execute(query)

                    if fetch:
                        rows = await cursor.fetchall()

                        # Get column names
                        columns = (
                            [desc[0] for desc in cursor.description]
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
                        affected_rows = cursor.rowcount
                        await conn.commit()

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
        if not self.pool:
            raise ConnectionError("Database not connected")

        start_time = time.time()

        try:
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    param_values_list = [
                        list(params.values()) for params in parameters_list
                    ]
                    await cursor.executemany(query, param_values_list)
                    await conn.commit()

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
        """Get SQL Server schema information."""
        schema = schema or "dbo"

        # Get tables
        tables_query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = ? AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """
        tables_result = await self.execute_query(tables_query, {"schema": schema})
        tables = [row["table_name"] for row in (tables_result.data or [])]

        # Get views
        views_query = """
            SELECT table_name 
            FROM information_schema.views 
            WHERE table_schema = ?
            ORDER BY table_name
        """
        views_result = await self.execute_query(views_query, {"schema": schema})
        views = [row["table_name"] for row in (views_result.data or [])]

        # Get functions
        functions_query = """
            SELECT routine_name 
            FROM information_schema.routines 
            WHERE routine_schema = ? AND routine_type = 'FUNCTION'
            ORDER BY routine_name
        """
        functions_result = await self.execute_query(functions_query, {"schema": schema})
        functions = [row["routine_name"] for row in (functions_result.data or [])]

        # Get procedures
        procedures_query = """
            SELECT routine_name 
            FROM information_schema.routines 
            WHERE routine_schema = ? AND routine_type = 'PROCEDURE'
            ORDER BY routine_name
        """
        procedures_result = await self.execute_query(
            procedures_query, {"schema": schema}
        )
        procedures = [row["routine_name"] for row in (procedures_result.data or [])]

        return SchemaInfo(
            tables=tables, views=views, functions=functions, procedures=procedures
        )

    async def get_table_info(
        self, table_name: str, schema: Optional[str] = None
    ) -> TableInfo:
        """Get detailed SQL Server table information."""
        schema = schema or "dbo"

        # Get columns
        columns_query = """
            SELECT 
                column_name,
                data_type,
                is_nullable,
                column_default,
                character_maximum_length,
                numeric_precision,
                numeric_scale
            FROM information_schema.columns 
            WHERE table_schema = ? AND table_name = ?
            ORDER BY ordinal_position
        """
        columns_result = await self.execute_query(
            columns_query, {"schema": schema, "table": table_name}
        )
        columns = columns_result.data or []

        # Get indexes
        indexes_query = """
            SELECT 
                i.name as index_name,
                i.is_unique,
                i.is_primary_key,
                c.name as column_name
            FROM sys.indexes i
            INNER JOIN sys.index_columns ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id
            INNER JOIN sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id
            INNER JOIN sys.tables t ON i.object_id = t.object_id
            INNER JOIN sys.schemas s ON t.schema_id = s.schema_id
            WHERE s.name = ? AND t.name = ?
            ORDER BY i.name, ic.key_ordinal
        """
        indexes_result = await self.execute_query(
            indexes_query, {"schema": schema, "table": table_name}
        )

        # Group indexes
        indexes_dict = {}
        for idx in indexes_result.data or []:
            idx_name = idx["index_name"]
            if idx_name not in indexes_dict:
                indexes_dict[idx_name] = {
                    "index_name": idx_name,
                    "is_unique": bool(idx["is_unique"]),
                    "is_primary": bool(idx["is_primary_key"]),
                    "columns": [],
                }
            indexes_dict[idx_name]["columns"].append(idx["column_name"])

        indexes = list(indexes_dict.values())

        # Get row count estimate
        count_query = f"SELECT COUNT(*) as count FROM [{schema}].[{table_name}]"
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
        """List SQL Server databases."""
        query = """
            SELECT name 
            FROM sys.databases 
            WHERE name NOT IN ('master', 'tempdb', 'model', 'msdb')
            ORDER BY name
        """
        result = await self.execute_query(query)
        return [row["name"] for row in (result.data or [])]

    async def list_schemas(self, database: Optional[str] = None) -> List[str]:
        """List SQL Server schemas."""
        query = """
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name NOT IN ('information_schema', 'sys', 'db_owner', 'db_accessadmin', 'db_securityadmin', 'db_ddladmin', 'db_backupoperator', 'db_datareader', 'db_datawriter', 'db_denydatareader', 'db_denydatawriter')
            ORDER BY schema_name
        """
        result = await self.execute_query(query)
        return [row["schema_name"] for row in (result.data or [])]

    async def list_tables(self, schema: Optional[str] = None) -> List[str]:
        """List SQL Server tables."""
        schema = schema or "dbo"
        query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = ? AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """
        result = await self.execute_query(query, {"schema": schema})
        return [row["table_name"] for row in (result.data or [])]

    async def test_connection(self) -> bool:
        """Test SQL Server connection."""
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
        """Create SQL Server table."""
        schema = schema or "dbo"

        columns_def = ", ".join(
            [f"[{col}] {col_type}" for col, col_type in columns.items()]
        )
        query = f"CREATE TABLE [{schema}].[{table_name}] ({columns_def})"

        return await self.execute_query(query, fetch=False)

    async def drop_table(
        self, table_name: str, schema: Optional[str] = None, if_exists: bool = False
    ) -> QueryResult:
        """Drop SQL Server table."""
        schema = schema or "dbo"

        if if_exists:
            query = f"IF OBJECT_ID('[{schema}].[{table_name}]', 'U') IS NOT NULL DROP TABLE [{schema}].[{table_name}]"
        else:
            query = f"DROP TABLE [{schema}].[{table_name}]"

        return await self.execute_query(query, fetch=False)

    async def insert_data(
        self,
        table_name: str,
        data: Union[Dict[str, Any], List[Dict[str, Any]]],
        schema: Optional[str] = None,
    ) -> QueryResult:
        """Insert data into SQL Server table."""
        schema = schema or "dbo"

        if isinstance(data, dict):
            data = [data]

        if not data:
            return QueryResult(success=True, affected_rows=0)

        # Build INSERT query
        columns = list(data[0].keys())
        columns_str = ", ".join([f"[{col}]" for col in columns])
        placeholders = ", ".join(["?" for _ in columns])

        query = f"INSERT INTO [{schema}].[{table_name}] ({columns_str}) VALUES ({placeholders})"

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
        """Update data in SQL Server table."""
        schema = schema or "dbo"

        set_clauses = [f"[{col}] = ?" for col in data.keys()]
        set_clause = ", ".join(set_clauses)

        query = (
            f"UPDATE [{schema}].[{table_name}] SET {set_clause} WHERE {where_clause}"
        )

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
        """Delete data from SQL Server table."""
        schema = schema or "dbo"

        query = f"DELETE FROM [{schema}].[{table_name}] WHERE {where_clause}"

        return await self.execute_query(query, parameters, fetch=False)
