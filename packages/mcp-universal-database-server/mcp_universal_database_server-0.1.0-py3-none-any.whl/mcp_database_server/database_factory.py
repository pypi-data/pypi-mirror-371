"""Database factory for creating database connections."""

import asyncio
from typing import Dict, Type, Optional
from .types import DatabaseType, ConnectionConfig
from .databases.base import BaseDatabase
from .databases.postgresql import PostgreSQLDatabase
from .databases.mysql import MySQLDatabase
from .databases.sqlite import SQLiteDatabase
from .databases.mongodb import MongoDatabase
from .databases.redis import RedisDatabase
from .databases.mssql import MSSQLDatabase


class DatabaseFactory:
    """Factory for creating database connections."""

    _drivers: Dict[DatabaseType, Type[BaseDatabase]] = {
        DatabaseType.POSTGRESQL: PostgreSQLDatabase,
        DatabaseType.MYSQL: MySQLDatabase,
        DatabaseType.SQLITE: SQLiteDatabase,
        DatabaseType.MONGODB: MongoDatabase,
        DatabaseType.REDIS: RedisDatabase,
        DatabaseType.MSSQL: MSSQLDatabase,
    }

    @classmethod
    def register_driver(
        cls, db_type: DatabaseType, driver_class: Type[BaseDatabase]
    ) -> None:
        """Register a new database driver."""
        cls._drivers[db_type] = driver_class

    @classmethod
    def get_supported_types(cls) -> list[DatabaseType]:
        """Get list of supported database types."""
        return list(cls._drivers.keys())

    @classmethod
    async def create_database(cls, config: ConnectionConfig) -> BaseDatabase:
        """Create a database connection instance."""
        if config.type not in cls._drivers:
            raise ValueError(f"Unsupported database type: {config.type}")

        driver_class = cls._drivers[config.type]
        database = driver_class(config)

        # Initialize the connection
        await database.connect()

        return database

    @classmethod
    def is_supported(cls, db_type: DatabaseType) -> bool:
        """Check if a database type is supported."""
        return db_type in cls._drivers
