"""Redis database driver."""

import time
import json
from typing import Any, Dict, List, Optional, Union
import redis.asyncio as redis

from .base import NoSQLDatabase
from ..types import (
    ConnectionConfig,
    QueryResult,
    SchemaInfo,
    TableInfo,
    QueryParameters,
)


class RedisDatabase(NoSQLDatabase):
    """Redis database implementation."""

    def __init__(self, config: ConnectionConfig):
        """Initialize Redis connection."""
        super().__init__(config)
        self.client: Optional[redis.Redis] = None

    async def connect(self) -> None:
        """Establish Redis connection."""
        try:
            self.client = redis.Redis(
                host=self.config.host or "localhost",
                port=self.config.port or 6379,
                password=self.config.password,
                db=int(self.config.database) if self.config.database else 0,
                decode_responses=True,
                max_connections=self.config.pool_size,
                socket_timeout=self.config.pool_timeout,
                socket_connect_timeout=self.config.pool_timeout,
                ssl=self.config.ssl,
                ssl_cert_reqs=None if not self.config.ssl else "required",
            )

            # Test connection
            await self.client.ping()
            self.is_connected = True
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Redis: {e}")

    async def disconnect(self) -> None:
        """Close Redis connection."""
        if self.client:
            await self.client.aclose()
            self.client = None
        self.is_connected = False

    async def execute_query(
        self,
        query: str,
        parameters: Optional[QueryParameters] = None,
        fetch: bool = True,
    ) -> QueryResult:
        """Execute Redis command."""
        if not self.client:
            raise ConnectionError("Database not connected")

        start_time = time.time()

        try:
            # Parse Redis command
            parts = query.strip().split()
            if not parts:
                raise ValueError("Empty command")

            command = parts[0].upper()
            args = parts[1:]

            # Replace parameters in args if provided
            if parameters:
                for i, arg in enumerate(args):
                    for key, value in parameters.items():
                        if f":{key}" in arg:
                            args[i] = arg.replace(f":{key}", str(value))

            # Execute command
            result = await self.client.execute_command(command, *args)

            # Format result based on command type
            data = None
            affected_rows = 0

            if fetch and result is not None:
                if isinstance(result, (list, tuple)):
                    data = [
                        {"index": i, "value": item} for i, item in enumerate(result)
                    ]
                    affected_rows = len(result)
                else:
                    data = [{"result": result}]
                    affected_rows = 1
            elif not fetch:
                affected_rows = 1 if result else 0

            return QueryResult(
                success=True,
                data=data,
                affected_rows=affected_rows,
                execution_time=time.time() - start_time,
                metadata={"command": command, "raw_result": result},
            )
        except Exception as e:
            return QueryResult(
                success=False, error=str(e), execution_time=time.time() - start_time
            )

    async def execute_many(
        self, query: str, parameters_list: List[QueryParameters]
    ) -> QueryResult:
        """Execute Redis command multiple times with different parameters."""
        if not self.client:
            raise ConnectionError("Database not connected")

        start_time = time.time()

        try:
            results = []
            total_affected = 0

            async with self.client.pipeline() as pipe:
                for params in parameters_list:
                    # Parse and substitute parameters
                    parts = query.strip().split()
                    command = parts[0].upper()
                    args = parts[1:]

                    for i, arg in enumerate(args):
                        for key, value in params.items():
                            if f":{key}" in arg:
                                args[i] = arg.replace(f":{key}", str(value))

                    pipe.execute_command(command, *args)

                pipeline_results = await pipe.execute()

                for result in pipeline_results:
                    results.append(result)
                    total_affected += 1 if result else 0

            return QueryResult(
                success=True,
                affected_rows=total_affected,
                execution_time=time.time() - start_time,
                metadata={"results": results},
            )
        except Exception as e:
            return QueryResult(
                success=False, error=str(e), execution_time=time.time() - start_time
            )

    async def get_schema_info(self, schema: Optional[str] = None) -> SchemaInfo:
        """Get Redis database information."""
        if not self.client:
            return SchemaInfo()

        try:
            # Get database info
            info = await self.client.info("keyspace")

            # Redis doesn't have traditional tables, but we can show key patterns
            keys = await self.client.keys("*")

            # Group keys by pattern (prefix before first colon)
            patterns = set()
            for key in keys[:100]:  # Limit to first 100 keys for performance
                if ":" in key:
                    patterns.add(key.split(":")[0])
                else:
                    patterns.add("_no_pattern")

            return SchemaInfo(tables=list(patterns))
        except Exception:
            return SchemaInfo()

    async def get_table_info(
        self, table_name: str, schema: Optional[str] = None
    ) -> TableInfo:
        """Get Redis key pattern information."""
        if not self.client:
            raise ConnectionError("Database not connected")

        try:
            # Find keys matching the pattern
            if table_name == "_no_pattern":
                pattern = "*"
                # Get keys without colons
                all_keys = await self.client.keys(pattern)
                keys = [k for k in all_keys if ":" not in k]
            else:
                pattern = f"{table_name}:*"
                keys = await self.client.keys(pattern)

            # Sample some keys to understand structure
            sample_keys = keys[:10]
            key_types = {}

            for key in sample_keys:
                key_type = await self.client.type(key)
                if key_type not in key_types:
                    key_types[key_type] = 0
                key_types[key_type] += 1

            # Create column info based on key types
            columns = []
            for key_type, count in key_types.items():
                columns.append(
                    {
                        "column_name": f"{key_type}_keys",
                        "data_type": key_type,
                        "count": count,
                    }
                )

            return TableInfo(
                name=table_name,
                columns=columns,
                indexes=[],
                constraints=[],
                row_count=len(keys),
            )
        except Exception as e:
            raise ConnectionError(f"Failed to get key pattern info: {e}")

    async def list_databases(self) -> List[str]:
        """List Redis databases (0-15 by default)."""
        # Redis typically has databases 0-15
        return [str(i) for i in range(16)]

    async def list_schemas(self, database: Optional[str] = None) -> List[str]:
        """List Redis databases (same as list_databases)."""
        return await self.list_databases()

    async def list_tables(self, schema: Optional[str] = None) -> List[str]:
        """List Redis key patterns."""
        if not self.client:
            raise ConnectionError("Database not connected")

        try:
            keys = await self.client.keys("*")
            patterns = set()

            for key in keys[:100]:  # Limit for performance
                if ":" in key:
                    patterns.add(key.split(":")[0])
                else:
                    patterns.add("_no_pattern")

            return list(patterns)
        except Exception:
            return []

    async def test_connection(self) -> bool:
        """Test Redis connection."""
        try:
            if self.client:
                await self.client.ping()
                return True
            return False
        except Exception:
            return False

    # NoSQL-specific methods (adapted for Redis)
    async def create_collection(self, collection_name: str, **kwargs) -> QueryResult:
        """Create Redis key pattern (not applicable, always succeeds)."""
        return QueryResult(
            success=True,
            execution_time=0.0,
            metadata={
                "message": f"Redis doesn't require explicit collection creation. Pattern '{collection_name}' ready to use."
            },
        )

    async def drop_collection(self, collection_name: str) -> QueryResult:
        """Drop all keys matching Redis pattern."""
        if not self.client:
            raise ConnectionError("Database not connected")

        start_time = time.time()

        try:
            pattern = (
                f"{collection_name}:*" if collection_name != "_no_pattern" else "*"
            )
            keys = await self.client.keys(pattern)

            if collection_name == "_no_pattern":
                # Filter keys without colons
                keys = [k for k in keys if ":" not in k]

            deleted_count = 0
            if keys:
                deleted_count = await self.client.delete(*keys)

            return QueryResult(
                success=True,
                affected_rows=deleted_count,
                execution_time=time.time() - start_time,
                metadata={"deleted_keys": deleted_count},
            )
        except Exception as e:
            return QueryResult(
                success=False, error=str(e), execution_time=time.time() - start_time
            )

    async def insert_document(
        self,
        collection_name: str,
        document: Union[Dict[str, Any], List[Dict[str, Any]]],
    ) -> QueryResult:
        """Insert data into Redis (as JSON strings)."""
        if not self.client:
            raise ConnectionError("Database not connected")

        start_time = time.time()

        try:
            if isinstance(document, dict):
                documents = [document]
            else:
                documents = document

            inserted_count = 0

            async with self.client.pipeline() as pipe:
                for i, doc in enumerate(documents):
                    key = f"{collection_name}:{doc.get('id', i)}"
                    value = json.dumps(doc)
                    pipe.set(key, value)
                    inserted_count += 1

                await pipe.execute()

            return QueryResult(
                success=True,
                affected_rows=inserted_count,
                execution_time=time.time() - start_time,
                metadata={"inserted_count": inserted_count},
            )
        except Exception as e:
            return QueryResult(
                success=False, error=str(e), execution_time=time.time() - start_time
            )

    async def find_documents(
        self,
        collection_name: str,
        filter_query: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        skip: Optional[int] = None,
        sort: Optional[Dict[str, int]] = None,
    ) -> QueryResult:
        """Find documents in Redis collection."""
        if not self.client:
            raise ConnectionError("Database not connected")

        start_time = time.time()

        try:
            pattern = f"{collection_name}:*"
            keys = await self.client.keys(pattern)

            documents = []
            processed = 0

            for key in keys:
                if skip and processed < skip:
                    processed += 1
                    continue

                if limit and len(documents) >= limit:
                    break

                value = await self.client.get(key)
                if value:
                    try:
                        doc = json.loads(value)

                        # Apply simple filter (basic equality check)
                        if filter_query:
                            match = True
                            for field, expected in filter_query.items():
                                if field not in doc or doc[field] != expected:
                                    match = False
                                    break
                            if not match:
                                continue

                        doc["_key"] = key
                        documents.append(doc)
                    except json.JSONDecodeError:
                        # If not JSON, treat as string value
                        documents.append({"_key": key, "value": value})

                processed += 1

            return QueryResult(
                success=True,
                data=documents,
                affected_rows=len(documents),
                execution_time=time.time() - start_time,
            )
        except Exception as e:
            return QueryResult(
                success=False, error=str(e), execution_time=time.time() - start_time
            )

    async def update_documents(
        self,
        collection_name: str,
        filter_query: Dict[str, Any],
        update_data: Dict[str, Any],
        upsert: bool = False,
    ) -> QueryResult:
        """Update documents in Redis collection."""
        if not self.client:
            raise ConnectionError("Database not connected")

        start_time = time.time()

        try:
            pattern = f"{collection_name}:*"
            keys = await self.client.keys(pattern)

            updated_count = 0

            for key in keys:
                value = await self.client.get(key)
                if value:
                    try:
                        doc = json.loads(value)

                        # Check if document matches filter
                        match = True
                        for field, expected in filter_query.items():
                            if field not in doc or doc[field] != expected:
                                match = False
                                break

                        if match:
                            # Update document
                            doc.update(update_data)
                            await self.client.set(key, json.dumps(doc))
                            updated_count += 1
                    except json.JSONDecodeError:
                        continue

            return QueryResult(
                success=True,
                affected_rows=updated_count,
                execution_time=time.time() - start_time,
                metadata={"updated_count": updated_count},
            )
        except Exception as e:
            return QueryResult(
                success=False, error=str(e), execution_time=time.time() - start_time
            )

    async def delete_documents(
        self, collection_name: str, filter_query: Dict[str, Any]
    ) -> QueryResult:
        """Delete documents from Redis collection."""
        if not self.client:
            raise ConnectionError("Database not connected")

        start_time = time.time()

        try:
            pattern = f"{collection_name}:*"
            keys = await self.client.keys(pattern)

            keys_to_delete = []

            for key in keys:
                value = await self.client.get(key)
                if value:
                    try:
                        doc = json.loads(value)

                        # Check if document matches filter
                        match = True
                        for field, expected in filter_query.items():
                            if field not in doc or doc[field] != expected:
                                match = False
                                break

                        if match:
                            keys_to_delete.append(key)
                    except json.JSONDecodeError:
                        continue

            deleted_count = 0
            if keys_to_delete:
                deleted_count = await self.client.delete(*keys_to_delete)

            return QueryResult(
                success=True,
                affected_rows=deleted_count,
                execution_time=time.time() - start_time,
                metadata={"deleted_count": deleted_count},
            )
        except Exception as e:
            return QueryResult(
                success=False, error=str(e), execution_time=time.time() - start_time
            )
