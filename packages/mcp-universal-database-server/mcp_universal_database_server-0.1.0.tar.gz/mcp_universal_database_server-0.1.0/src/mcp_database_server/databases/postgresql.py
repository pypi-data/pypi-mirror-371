"""PostgreSQL database driver."""

import asyncio
import time
from typing import Any, Dict, List, Optional, Union
import asyncpg
from asyncpg import Pool, Connection

from .base import SQLDatabase
from ..types import (
    ConnectionConfig,
    QueryResult,
    SchemaInfo,
    TableInfo,
    QueryParameters,
)


class PostgreSQLDatabase(SQLDatabase):
    """PostgreSQL database implementation."""

    def __init__(self, config: ConnectionConfig):
        """Initialize PostgreSQL connection."""
        super().__init__(config)
        self.pool: Optional[Pool] = None

    async def connect(self) -> None:
        """Establish PostgreSQL connection pool."""
        try:
            dsn = self._build_dsn()
            self.pool = await asyncpg.create_pool(
                dsn,
                min_size=1,
                max_size=self.config.pool_size,
                max_queries=50000,
                max_inactive_connection_lifetime=300.0,
                command_timeout=self.config.pool_timeout,
            )
            self.is_connected = True
        except Exception as e:
            raise ConnectionError(f"Failed to connect to PostgreSQL: {e}")

    async def disconnect(self) -> None:
        """Close PostgreSQL connection pool."""
        if self.pool:
            await self.pool.close()
            self.pool = None
        self.is_connected = False

    def _build_dsn(self) -> str:
        """Build PostgreSQL DSN."""
        dsn_parts = []

        if self.config.host:
            dsn_parts.append(f"host={self.config.host}")
        if self.config.port:
            dsn_parts.append(f"port={self.config.port}")
        if self.config.database:
            dsn_parts.append(f"database={self.config.database}")
        if self.config.username:
            dsn_parts.append(f"user={self.config.username}")
        if self.config.password:
            dsn_parts.append(f"password={self.config.password}")

        if self.config.ssl:
            dsn_parts.append("sslmode=require")

        return " ".join(dsn_parts)

    async def execute_query(
        self,
        query: str,
        parameters: Optional[QueryParameters] = None,
        fetch: bool = True,
    ) -> QueryResult:
        """Execute PostgreSQL query."""
        if not self.pool:
            raise ConnectionError("Database not connected")

        start_time = time.time()

        try:
            async with self.pool.acquire() as conn:
                if fetch:
                    if parameters:
                        rows = await conn.fetch(query, *parameters.values())
                    else:
                        rows = await conn.fetch(query)

                    data = [dict(row) for row in rows]

                    return QueryResult(
                        success=True,
                        data=data,
                        affected_rows=len(data),
                        execution_time=time.time() - start_time,
                    )
                else:
                    if parameters:
                        result = await conn.execute(query, *parameters.values())
                    else:
                        result = await conn.execute(query)

                    # Extract affected rows from result string like "UPDATE 5"
                    affected_rows = 0
                    if result and result.split():
                        try:
                            affected_rows = int(result.split()[-1])
                        except (ValueError, IndexError):
                            pass

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
                async with conn.transaction():
                    total_affected = 0
                    for params in parameters_list:
                        result = await conn.execute(query, *params.values())
                        if result and result.split():
                            try:
                                total_affected += int(result.split()[-1])
                            except (ValueError, IndexError):
                                pass

                    return QueryResult(
                        success=True,
                        affected_rows=total_affected,
                        execution_time=time.time() - start_time,
                    )

        except Exception as e:
            return QueryResult(
                success=False, error=str(e), execution_time=time.time() - start_time
            )

    async def get_schema_info(self, schema: Optional[str] = None) -> SchemaInfo:
        """Get PostgreSQL schema information."""
        schema = schema or "public"

        # Get tables
        tables_query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = $1 AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """
        tables_result = await self.execute_query(tables_query, {"schema": schema})
        tables = [row["table_name"] for row in (tables_result.data or [])]

        # Get views
        views_query = """
            SELECT table_name 
            FROM information_schema.views 
            WHERE table_schema = $1
            ORDER BY table_name
        """
        views_result = await self.execute_query(views_query, {"schema": schema})
        views = [row["table_name"] for row in (views_result.data or [])]

        # Get functions
        functions_query = """
            SELECT routine_name 
            FROM information_schema.routines 
            WHERE routine_schema = $1 AND routine_type = 'FUNCTION'
            ORDER BY routine_name
        """
        functions_result = await self.execute_query(functions_query, {"schema": schema})
        functions = [row["routine_name"] for row in (functions_result.data or [])]

        # Get procedures
        procedures_query = """
            SELECT routine_name 
            FROM information_schema.routines 
            WHERE routine_schema = $1 AND routine_type = 'PROCEDURE'
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
        """Get detailed PostgreSQL table information."""
        schema = schema or "public"

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
            WHERE table_schema = $1 AND table_name = $2
            ORDER BY ordinal_position
        """
        columns_result = await self.execute_query(
            columns_query, {"schema": schema, "table": table_name}
        )
        columns = columns_result.data or []

        # Get indexes
        indexes_query = """
            SELECT 
                i.indexname,
                i.indexdef,
                CASE WHEN i.indexname LIKE '%_pkey' THEN true ELSE false END as is_primary
            FROM pg_indexes i
            WHERE i.schemaname = $1 AND i.tablename = $2
        """
        indexes_result = await self.execute_query(
            indexes_query, {"schema": schema, "table": table_name}
        )
        indexes = indexes_result.data or []

        # Get row count estimate
        count_query = f'SELECT COUNT(*) as count FROM "{schema}"."{table_name}"'
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
        """List PostgreSQL databases."""
        query = "SELECT datname FROM pg_database WHERE datistemplate = false ORDER BY datname"
        result = await self.execute_query(query)
        return [row["datname"] for row in (result.data or [])]

    async def list_schemas(self, database: Optional[str] = None) -> List[str]:
        """List PostgreSQL schemas."""
        query = """
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
            ORDER BY schema_name
        """
        result = await self.execute_query(query)
        return [row["schema_name"] for row in (result.data or [])]

    async def list_tables(self, schema: Optional[str] = None) -> List[str]:
        """List PostgreSQL tables."""
        schema = schema or "public"
        query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = $1 AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """
        result = await self.execute_query(query, {"schema": schema})
        return [row["table_name"] for row in (result.data or [])]

    async def test_connection(self) -> bool:
        """Test PostgreSQL connection."""
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
        """Create PostgreSQL table."""
        schema = schema or "public"

        columns_def = ", ".join(
            [f'"{col}" {col_type}' for col, col_type in columns.items()]
        )
        query = f'CREATE TABLE "{schema}"."{table_name}" ({columns_def})'

        return await self.execute_query(query, fetch=False)

    async def drop_table(
        self, table_name: str, schema: Optional[str] = None, if_exists: bool = False
    ) -> QueryResult:
        """Drop PostgreSQL table."""
        schema = schema or "public"

        if_exists_clause = "IF EXISTS" if if_exists else ""
        query = f'DROP TABLE {if_exists_clause} "{schema}"."{table_name}"'

        return await self.execute_query(query, fetch=False)

    async def insert_data(
        self,
        table_name: str,
        data: Union[Dict[str, Any], List[Dict[str, Any]]],
        schema: Optional[str] = None,
    ) -> QueryResult:
        """Insert data into PostgreSQL table."""
        schema = schema or "public"

        if isinstance(data, dict):
            data = [data]

        if not data:
            return QueryResult(success=True, affected_rows=0)

        # Build INSERT query
        columns = list(data[0].keys())
        columns_str = ", ".join([f'"{col}"' for col in columns])
        placeholders = ", ".join([f"${i+1}" for i in range(len(columns))])

        query = f'INSERT INTO "{schema}"."{table_name}" ({columns_str}) VALUES ({placeholders})'

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
        """Update data in PostgreSQL table."""
        schema = schema or "public"

        set_clauses = []
        param_counter = 1
        update_params = {}

        for col, value in data.items():
            set_clauses.append(f'"{col}" = ${param_counter}')
            update_params[str(param_counter)] = value
            param_counter += 1

        # Add where parameters
        if parameters:
            for key, value in parameters.items():
                update_params[str(param_counter)] = value
                # Replace named parameters in where clause with positional
                where_clause = where_clause.replace(f":{key}", f"${param_counter}")
                param_counter += 1

        set_clause = ", ".join(set_clauses)
        query = (
            f'UPDATE "{schema}"."{table_name}" SET {set_clause} WHERE {where_clause}'
        )

        return await self.execute_query(query, update_params, fetch=False)

    async def delete_data(
        self,
        table_name: str,
        where_clause: str,
        parameters: Optional[QueryParameters] = None,
        schema: Optional[str] = None,
    ) -> QueryResult:
        """Delete data from PostgreSQL table."""
        schema = schema or "public"

        delete_params = {}
        if parameters:
            param_counter = 1
            for key, value in parameters.items():
                delete_params[str(param_counter)] = value
                # Replace named parameters with positional
                where_clause = where_clause.replace(f":{key}", f"${param_counter}")
                param_counter += 1

        query = f'DELETE FROM "{schema}"."{table_name}" WHERE {where_clause}'

        return await self.execute_query(query, delete_params, fetch=False)
