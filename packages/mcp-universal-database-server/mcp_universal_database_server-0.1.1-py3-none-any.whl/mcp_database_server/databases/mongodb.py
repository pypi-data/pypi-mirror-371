"""MongoDB database driver."""

import time
from typing import Any, Dict, List, Optional, Union
from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorDatabase,
    AsyncIOMotorCollection,
)

from .base import NoSQLDatabase
from ..types import (
    ConnectionConfig,
    QueryResult,
    SchemaInfo,
    TableInfo,
    QueryParameters,
)


class MongoDatabase(NoSQLDatabase):
    """MongoDB database implementation."""

    def __init__(self, config: ConnectionConfig):
        """Initialize MongoDB connection."""
        super().__init__(config)
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None

    async def connect(self) -> None:
        """Establish MongoDB connection."""
        try:
            # Build MongoDB URI
            uri = self._build_uri()
            self.client = AsyncIOMotorClient(
                uri,
                maxPoolSize=self.config.pool_size,
                minPoolSize=1,
                maxIdleTimeMS=30000,
                serverSelectionTimeoutMS=self.config.pool_timeout * 1000,
            )

            # Test connection
            await self.client.admin.command("ping")

            if self.config.database:
                self.database = self.client[self.config.database]

            self.is_connected = True
        except Exception as e:
            raise ConnectionError(f"Failed to connect to MongoDB: {e}")

    async def disconnect(self) -> None:
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            self.client = None
            self.database = None
        self.is_connected = False

    def _build_uri(self) -> str:
        """Build MongoDB connection URI."""
        if self.config.options.get("connection_string"):
            return self.config.options["connection_string"]

        # Build URI from components
        uri_parts = ["mongodb://"]

        if self.config.username and self.config.password:
            uri_parts.append(f"{self.config.username}:{self.config.password}@")

        host = self.config.host or "localhost"
        port = self.config.port or 27017
        uri_parts.append(f"{host}:{port}")

        if self.config.database:
            uri_parts.append(f"/{self.config.database}")

        # Add SSL options
        options = []
        if self.config.ssl:
            options.append("ssl=true")

        # Add additional options
        for key, value in self.config.options.items():
            if key != "connection_string":
                options.append(f"{key}={value}")

        if options:
            uri_parts.append("?" + "&".join(options))

        return "".join(uri_parts)

    async def execute_query(
        self,
        query: str,
        parameters: Optional[QueryParameters] = None,
        fetch: bool = True,
    ) -> QueryResult:
        """Execute MongoDB operation (not applicable for raw queries)."""
        return QueryResult(
            success=False,
            error="Raw query execution not supported for MongoDB. Use specific operations.",
        )

    async def execute_many(
        self, query: str, parameters_list: List[QueryParameters]
    ) -> QueryResult:
        """Execute multiple operations (not applicable for raw queries)."""
        return QueryResult(
            success=False,
            error="Raw query execution not supported for MongoDB. Use specific operations.",
        )

    async def get_schema_info(self, schema: Optional[str] = None) -> SchemaInfo:
        """Get MongoDB database information."""
        if not self.database:
            return SchemaInfo()

        try:
            collections = await self.database.list_collection_names()
            return SchemaInfo(tables=collections)
        except Exception as e:
            return SchemaInfo()

    async def get_table_info(
        self, table_name: str, schema: Optional[str] = None
    ) -> TableInfo:
        """Get MongoDB collection information."""
        if not self.database:
            raise ConnectionError("Database not connected")

        try:
            collection = self.database[table_name]

            # Get collection stats
            stats = await self.database.command("collStats", table_name)

            # Get indexes
            indexes = []
            async for index in collection.list_indexes():
                indexes.append(
                    {
                        "index_name": index.get("name", ""),
                        "keys": index.get("key", {}),
                        "unique": index.get("unique", False),
                    }
                )

            # Sample documents to infer schema
            sample_docs = []
            async for doc in collection.find().limit(10):
                sample_docs.append(doc)

            # Infer columns from sample documents
            columns = []
            if sample_docs:
                all_keys = set()
                for doc in sample_docs:
                    all_keys.update(doc.keys())

                for key in sorted(all_keys):
                    # Determine data type from samples
                    data_types = set()
                    for doc in sample_docs:
                        if key in doc:
                            data_types.add(type(doc[key]).__name__)

                    columns.append(
                        {
                            "column_name": key,
                            "data_type": "/".join(sorted(data_types)),
                            "is_nullable": "YES",  # MongoDB is schema-less
                        }
                    )

            return TableInfo(
                name=table_name,
                columns=columns,
                indexes=indexes,
                constraints=[],
                row_count=stats.get("count", 0),
            )

        except Exception as e:
            raise ConnectionError(f"Failed to get collection info: {e}")

    async def list_databases(self) -> List[str]:
        """List MongoDB databases."""
        if not self.client:
            raise ConnectionError("Database not connected")

        try:
            db_list = await self.client.list_database_names()
            # Filter out system databases
            system_dbs = {"admin", "config", "local"}
            return [db for db in db_list if db not in system_dbs]
        except Exception:
            return []

    async def list_schemas(self, database: Optional[str] = None) -> List[str]:
        """List MongoDB databases (same as list_databases)."""
        return await self.list_databases()

    async def list_tables(self, schema: Optional[str] = None) -> List[str]:
        """List MongoDB collections."""
        if not self.database:
            raise ConnectionError("Database not connected")

        try:
            return await self.database.list_collection_names()
        except Exception:
            return []

    async def test_connection(self) -> bool:
        """Test MongoDB connection."""
        try:
            if self.client:
                await self.client.admin.command("ping")
                return True
            return False
        except Exception:
            return False

    # NoSQL-specific methods
    async def create_collection(self, collection_name: str, **kwargs) -> QueryResult:
        """Create MongoDB collection."""
        if not self.database:
            raise ConnectionError("Database not connected")

        start_time = time.time()

        try:
            await self.database.create_collection(collection_name, **kwargs)

            return QueryResult(
                success=True,
                execution_time=time.time() - start_time,
                metadata={"collection_created": collection_name},
            )
        except Exception as e:
            return QueryResult(
                success=False, error=str(e), execution_time=time.time() - start_time
            )

    async def drop_collection(self, collection_name: str) -> QueryResult:
        """Drop MongoDB collection."""
        if not self.database:
            raise ConnectionError("Database not connected")

        start_time = time.time()

        try:
            await self.database.drop_collection(collection_name)

            return QueryResult(
                success=True,
                execution_time=time.time() - start_time,
                metadata={"collection_dropped": collection_name},
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
        """Insert document(s) into MongoDB collection."""
        if not self.database:
            raise ConnectionError("Database not connected")

        start_time = time.time()

        try:
            collection = self.database[collection_name]

            if isinstance(document, dict):
                result = await collection.insert_one(document)
                return QueryResult(
                    success=True,
                    affected_rows=1,
                    execution_time=time.time() - start_time,
                    metadata={"inserted_id": str(result.inserted_id)},
                )
            else:
                result = await collection.insert_many(document)
                return QueryResult(
                    success=True,
                    affected_rows=len(result.inserted_ids),
                    execution_time=time.time() - start_time,
                    metadata={"inserted_ids": [str(id) for id in result.inserted_ids]},
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
        """Find documents in MongoDB collection."""
        if not self.database:
            raise ConnectionError("Database not connected")

        start_time = time.time()

        try:
            collection = self.database[collection_name]

            cursor = collection.find(filter_query or {})

            if skip:
                cursor = cursor.skip(skip)
            if limit:
                cursor = cursor.limit(limit)
            if sort:
                sort_list = [(field, direction) for field, direction in sort.items()]
                cursor = cursor.sort(sort_list)

            documents = []
            async for doc in cursor:
                # Convert ObjectId to string for JSON serialization
                if "_id" in doc:
                    doc["_id"] = str(doc["_id"])
                documents.append(doc)

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
        """Update documents in MongoDB collection."""
        if not self.database:
            raise ConnectionError("Database not connected")

        start_time = time.time()

        try:
            collection = self.database[collection_name]

            result = await collection.update_many(
                filter_query, update_data, upsert=upsert
            )

            return QueryResult(
                success=True,
                affected_rows=result.modified_count,
                execution_time=time.time() - start_time,
                metadata={
                    "matched_count": result.matched_count,
                    "modified_count": result.modified_count,
                    "upserted_id": (
                        str(result.upserted_id) if result.upserted_id else None
                    ),
                },
            )
        except Exception as e:
            return QueryResult(
                success=False, error=str(e), execution_time=time.time() - start_time
            )

    async def delete_documents(
        self, collection_name: str, filter_query: Dict[str, Any]
    ) -> QueryResult:
        """Delete documents from MongoDB collection."""
        if not self.database:
            raise ConnectionError("Database not connected")

        start_time = time.time()

        try:
            collection = self.database[collection_name]

            result = await collection.delete_many(filter_query)

            return QueryResult(
                success=True,
                affected_rows=result.deleted_count,
                execution_time=time.time() - start_time,
                metadata={"deleted_count": result.deleted_count},
            )
        except Exception as e:
            return QueryResult(
                success=False, error=str(e), execution_time=time.time() - start_time
            )
