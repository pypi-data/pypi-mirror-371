"""Base database interface."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from ..types import (
    ConnectionConfig,
    QueryResult,
    SchemaInfo,
    TableInfo,
    QueryParameters,
)


class BaseDatabase(ABC):
    """Abstract base class for database connections."""

    def __init__(self, config: ConnectionConfig):
        """Initialize database connection."""
        self.config = config
        self.connection = None
        self.is_connected = False

    @abstractmethod
    async def connect(self) -> None:
        """Establish database connection."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Close database connection."""
        pass

    @abstractmethod
    async def execute_query(
        self,
        query: str,
        parameters: Optional[QueryParameters] = None,
        fetch: bool = True,
    ) -> QueryResult:
        """Execute a query and return results."""
        pass

    @abstractmethod
    async def execute_many(
        self, query: str, parameters_list: List[QueryParameters]
    ) -> QueryResult:
        """Execute a query multiple times with different parameters."""
        pass

    @abstractmethod
    async def get_schema_info(self, schema: Optional[str] = None) -> SchemaInfo:
        """Get database schema information."""
        pass

    @abstractmethod
    async def get_table_info(
        self, table_name: str, schema: Optional[str] = None
    ) -> TableInfo:
        """Get detailed table information."""
        pass

    @abstractmethod
    async def list_databases(self) -> List[str]:
        """List available databases."""
        pass

    @abstractmethod
    async def list_schemas(self, database: Optional[str] = None) -> List[str]:
        """List available schemas."""
        pass

    @abstractmethod
    async def list_tables(self, schema: Optional[str] = None) -> List[str]:
        """List tables in schema/database."""
        pass

    @abstractmethod
    async def test_connection(self) -> bool:
        """Test database connection."""
        pass

    # Common utility methods
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()

    def __repr__(self) -> str:
        """String representation."""
        return f"{self.__class__.__name__}(name='{self.config.name}', type='{self.config.type}')"


class SQLDatabase(BaseDatabase):
    """Base class for SQL databases."""

    @abstractmethod
    async def create_table(
        self,
        table_name: str,
        columns: Dict[str, str],
        schema: Optional[str] = None,
        **kwargs,
    ) -> QueryResult:
        """Create a new table."""
        pass

    @abstractmethod
    async def drop_table(
        self, table_name: str, schema: Optional[str] = None, if_exists: bool = False
    ) -> QueryResult:
        """Drop a table."""
        pass

    @abstractmethod
    async def insert_data(
        self,
        table_name: str,
        data: Union[Dict[str, Any], List[Dict[str, Any]]],
        schema: Optional[str] = None,
    ) -> QueryResult:
        """Insert data into table."""
        pass

    @abstractmethod
    async def update_data(
        self,
        table_name: str,
        data: Dict[str, Any],
        where_clause: str,
        parameters: Optional[QueryParameters] = None,
        schema: Optional[str] = None,
    ) -> QueryResult:
        """Update data in table."""
        pass

    @abstractmethod
    async def delete_data(
        self,
        table_name: str,
        where_clause: str,
        parameters: Optional[QueryParameters] = None,
        schema: Optional[str] = None,
    ) -> QueryResult:
        """Delete data from table."""
        pass


class NoSQLDatabase(BaseDatabase):
    """Base class for NoSQL databases."""

    @abstractmethod
    async def create_collection(self, collection_name: str, **kwargs) -> QueryResult:
        """Create a new collection."""
        pass

    @abstractmethod
    async def drop_collection(self, collection_name: str) -> QueryResult:
        """Drop a collection."""
        pass

    @abstractmethod
    async def insert_document(
        self,
        collection_name: str,
        document: Union[Dict[str, Any], List[Dict[str, Any]]],
    ) -> QueryResult:
        """Insert document(s) into collection."""
        pass

    @abstractmethod
    async def find_documents(
        self,
        collection_name: str,
        filter_query: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        skip: Optional[int] = None,
        sort: Optional[Dict[str, int]] = None,
    ) -> QueryResult:
        """Find documents in collection."""
        pass

    @abstractmethod
    async def update_documents(
        self,
        collection_name: str,
        filter_query: Dict[str, Any],
        update_data: Dict[str, Any],
        upsert: bool = False,
    ) -> QueryResult:
        """Update documents in collection."""
        pass

    @abstractmethod
    async def delete_documents(
        self, collection_name: str, filter_query: Dict[str, Any]
    ) -> QueryResult:
        """Delete documents from collection."""
        pass
