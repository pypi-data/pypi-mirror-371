"""MySQL database driver."""

import time
from typing import Any, Dict, List, Optional, Union
import aiomysql

from .base import SQLDatabase
from ..types import (
    ConnectionConfig,
    QueryResult,
    SchemaInfo,
    TableInfo,
    QueryParameters,
)


class MySQLDatabase(SQLDatabase):
    """MySQL database implementation."""

    def __init__(self, config: ConnectionConfig):
        """Initialize MySQL connection."""
        super().__init__(config)
        self.pool: Optional[aiomysql.Pool] = None

    async def connect(self) -> None:
        """Establish MySQL connection pool."""
        try:
            self.pool = await aiomysql.create_pool(
                host=self.config.host or "localhost",
                port=self.config.port or 3306,
                user=self.config.username,
                password=self.config.password,
                db=self.config.database,
                minsize=1,
                maxsize=self.config.pool_size,
                pool_recycle=3600,
                autocommit=False,
            )
            self.is_connected = True
        except Exception as e:
            raise ConnectionError(f"Failed to connect to MySQL: {e}")

    async def disconnect(self) -> None:
        """Close MySQL connection pool."""
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
            self.pool = None
        self.is_connected = False

    async def execute_query(
        self,
        query: str,
        parameters: Optional[QueryParameters] = None,
        fetch: bool = True,
    ) -> QueryResult:
        """Execute MySQL query."""
        if not self.pool:
            raise ConnectionError("Database not connected")

        start_time = time.time()

        try:
            async with self.pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    if parameters:
                        # Convert named parameters to positional for MySQL
                        param_values = list(parameters.values())
                        await cursor.execute(query, param_values)
                    else:
                        await cursor.execute(query)

                    if fetch:
                        rows = await cursor.fetchall()
                        data = [dict(row) for row in rows]

                        return QueryResult(
                            success=True,
                            data=data,
                            affected_rows=len(data),
                            execution_time=time.time() - start_time,
                        )
                    else:
                        await conn.commit()
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
        """Get MySQL schema information."""
        database = schema or self.config.database

        # Get tables
        tables_query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = %s AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """
        tables_result = await self.execute_query(tables_query, {"database": database})
        tables = [row["table_name"] for row in (tables_result.data or [])]

        # Get views
        views_query = """
            SELECT table_name 
            FROM information_schema.views 
            WHERE table_schema = %s
            ORDER BY table_name
        """
        views_result = await self.execute_query(views_query, {"database": database})
        views = [row["table_name"] for row in (views_result.data or [])]

        # Get functions
        functions_query = """
            SELECT routine_name 
            FROM information_schema.routines 
            WHERE routine_schema = %s AND routine_type = 'FUNCTION'
            ORDER BY routine_name
        """
        functions_result = await self.execute_query(
            functions_query, {"database": database}
        )
        functions = [row["routine_name"] for row in (functions_result.data or [])]

        # Get procedures
        procedures_query = """
            SELECT routine_name 
            FROM information_schema.routines 
            WHERE routine_schema = %s AND routine_type = 'PROCEDURE'
            ORDER BY routine_name
        """
        procedures_result = await self.execute_query(
            procedures_query, {"database": database}
        )
        procedures = [row["routine_name"] for row in (procedures_result.data or [])]

        return SchemaInfo(
            tables=tables, views=views, functions=functions, procedures=procedures
        )

    async def get_table_info(
        self, table_name: str, schema: Optional[str] = None
    ) -> TableInfo:
        """Get detailed MySQL table information."""
        database = schema or self.config.database

        # Get columns
        columns_query = """
            SELECT 
                column_name,
                data_type,
                is_nullable,
                column_default,
                character_maximum_length,
                numeric_precision,
                numeric_scale,
                column_key
            FROM information_schema.columns 
            WHERE table_schema = %s AND table_name = %s
            ORDER BY ordinal_position
        """
        columns_result = await self.execute_query(
            columns_query, {"database": database, "table": table_name}
        )
        columns = columns_result.data or []

        # Get indexes
        indexes_query = """
            SELECT 
                index_name,
                column_name,
                non_unique,
                seq_in_index
            FROM information_schema.statistics 
            WHERE table_schema = %s AND table_name = %s
            ORDER BY index_name, seq_in_index
        """
        indexes_result = await self.execute_query(
            indexes_query, {"database": database, "table": table_name}
        )

        # Group indexes
        indexes_dict = {}
        for idx in indexes_result.data or []:
            idx_name = idx["index_name"]
            if idx_name not in indexes_dict:
                indexes_dict[idx_name] = {
                    "index_name": idx_name,
                    "is_unique": not bool(idx["non_unique"]),
                    "columns": [],
                }
            indexes_dict[idx_name]["columns"].append(idx["column_name"])

        indexes = list(indexes_dict.values())

        # Get row count estimate
        count_query = f"SELECT COUNT(*) as count FROM `{database}`.`{table_name}`"
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
        """List MySQL databases."""
        query = "SHOW DATABASES"
        result = await self.execute_query(query)

        # Filter out system databases
        system_dbs = {"information_schema", "mysql", "performance_schema", "sys"}
        databases = []

        for row in result.data or []:
            db_name = row.get("Database") or row.get("database")
            if db_name and db_name not in system_dbs:
                databases.append(db_name)

        return sorted(databases)

    async def list_schemas(self, database: Optional[str] = None) -> List[str]:
        """List MySQL schemas (same as databases in MySQL)."""
        return await self.list_databases()

    async def list_tables(self, schema: Optional[str] = None) -> List[str]:
        """List MySQL tables."""
        database = schema or self.config.database
        query = f"SHOW TABLES FROM `{database}`"
        result = await self.execute_query(query)

        tables = []
        for row in result.data or []:
            # The key name varies depending on MySQL version
            table_name = None
            for key in row.keys():
                if key.startswith("Tables_in_"):
                    table_name = row[key]
                    break

            if table_name:
                tables.append(table_name)

        return sorted(tables)

    async def test_connection(self) -> bool:
        """Test MySQL connection."""
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
        """Create MySQL table."""
        database = schema or self.config.database

        columns_def = ", ".join(
            [f"`{col}` {col_type}" for col, col_type in columns.items()]
        )
        query = f"CREATE TABLE `{database}`.`{table_name}` ({columns_def})"

        return await self.execute_query(query, fetch=False)

    async def drop_table(
        self, table_name: str, schema: Optional[str] = None, if_exists: bool = False
    ) -> QueryResult:
        """Drop MySQL table."""
        database = schema or self.config.database

        if_exists_clause = "IF EXISTS" if if_exists else ""
        query = f"DROP TABLE {if_exists_clause} `{database}`.`{table_name}`"

        return await self.execute_query(query, fetch=False)

    async def insert_data(
        self,
        table_name: str,
        data: Union[Dict[str, Any], List[Dict[str, Any]]],
        schema: Optional[str] = None,
    ) -> QueryResult:
        """Insert data into MySQL table."""
        database = schema or self.config.database

        if isinstance(data, dict):
            data = [data]

        if not data:
            return QueryResult(success=True, affected_rows=0)

        # Build INSERT query
        columns = list(data[0].keys())
        columns_str = ", ".join([f"`{col}`" for col in columns])
        placeholders = ", ".join(["%s" for _ in columns])

        query = f"INSERT INTO `{database}`.`{table_name}` ({columns_str}) VALUES ({placeholders})"

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
        """Update data in MySQL table."""
        database = schema or self.config.database

        set_clauses = [f"`{col}` = %s" for col in data.keys()]
        set_clause = ", ".join(set_clauses)

        query = (
            f"UPDATE `{database}`.`{table_name}` SET {set_clause} WHERE {where_clause}"
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
        """Delete data from MySQL table."""
        database = schema or self.config.database

        query = f"DELETE FROM `{database}`.`{table_name}` WHERE {where_clause}"

        return await self.execute_query(query, parameters, fetch=False)
