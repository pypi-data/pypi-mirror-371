"""Type definitions for MCP Database Server."""

from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


class DatabaseType(str, Enum):
    """Supported database types."""

    # SQL Databases
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"
    MSSQL = "mssql"
    ORACLE = "oracle"

    # NoSQL Databases
    MONGODB = "mongodb"
    REDIS = "redis"
    CASSANDRA = "cassandra"

    # Cloud Databases
    FIRESTORE = "firestore"
    DYNAMODB = "dynamodb"
    COSMOSDB = "cosmosdb"


class ConnectionConfig(BaseModel):
    """Database connection configuration."""

    name: str = Field(..., description="Connection name/identifier")
    type: DatabaseType = Field(..., description="Database type")
    host: Optional[str] = Field(None, description="Database host")
    port: Optional[int] = Field(None, description="Database port")
    username: Optional[str] = Field(None, description="Username")
    password: Optional[str] = Field(None, description="Password")
    database: Optional[str] = Field(None, description="Database name")
    schema_name: Optional[str] = Field(
        None, description="Schema name (for SQL databases)", alias="schema"
    )

    # Connection options
    ssl: bool = Field(False, description="Use SSL connection")
    ssl_cert: Optional[str] = Field(None, description="SSL certificate path")
    ssl_key: Optional[str] = Field(None, description="SSL key path")
    ssl_ca: Optional[str] = Field(None, description="SSL CA path")

    # Connection pooling
    pool_size: int = Field(10, description="Connection pool size")
    max_overflow: int = Field(20, description="Maximum pool overflow")
    pool_timeout: int = Field(30, description="Pool timeout in seconds")

    # Additional options (for cloud databases, special configurations)
    options: Dict[str, Any] = Field(
        default_factory=dict, description="Additional connection options"
    )

    model_config = {"use_enum_values": True}


class QueryResult(BaseModel):
    """Query execution result."""

    success: bool = Field(..., description="Whether query was successful")
    data: Optional[List[Dict[str, Any]]] = Field(None, description="Query result data")
    affected_rows: Optional[int] = Field(None, description="Number of affected rows")
    error: Optional[str] = Field(None, description="Error message if failed")
    execution_time: Optional[float] = Field(
        None, description="Execution time in seconds"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class SchemaInfo(BaseModel):
    """Database schema information."""

    tables: List[str] = Field(default_factory=list, description="List of tables")
    views: List[str] = Field(default_factory=list, description="List of views")
    procedures: List[str] = Field(
        default_factory=list, description="List of stored procedures"
    )
    functions: List[str] = Field(default_factory=list, description="List of functions")


class TableInfo(BaseModel):
    """Table information."""

    name: str = Field(..., description="Table name")
    columns: List[Dict[str, Any]] = Field(
        default_factory=list, description="Column information"
    )
    indexes: List[Dict[str, Any]] = Field(
        default_factory=list, description="Index information"
    )
    constraints: List[Dict[str, Any]] = Field(
        default_factory=list, description="Constraint information"
    )
    row_count: Optional[int] = Field(None, description="Approximate row count")


class DatabaseOperation(BaseModel):
    """Database operation request."""

    connection_name: str = Field(..., description="Connection name to use")
    operation: str = Field(..., description="Operation type")
    parameters: Dict[str, Any] = Field(
        default_factory=dict, description="Operation parameters"
    )
    timeout: Optional[int] = Field(30, description="Operation timeout in seconds")


# Common parameter types
DatabaseValue = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]
QueryParameters = Dict[str, DatabaseValue]
