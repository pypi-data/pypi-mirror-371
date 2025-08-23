"""Connection manager for database connections."""

import asyncio
import logging
from typing import Dict, List, Optional, Set
from .types import ConnectionConfig, DatabaseType
from .database_factory import DatabaseFactory
from .databases.base import BaseDatabase


logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages database connections and connection pooling."""

    def __init__(self):
        """Initialize connection manager."""
        self._connections: Dict[str, BaseDatabase] = {}
        self._connection_configs: Dict[str, ConnectionConfig] = {}
        self._active_connections: Set[str] = set()
        self._lock = asyncio.Lock()

    async def add_connection(self, config: ConnectionConfig) -> bool:
        """Add a new database connection configuration."""
        async with self._lock:
            try:
                # Validate configuration
                if not config.name:
                    raise ValueError("Connection name is required")

                if config.name in self._connection_configs:
                    logger.warning(
                        f"Connection '{config.name}' already exists, updating..."
                    )

                # Test connection before adding
                test_db = await DatabaseFactory.create_database(config)
                connection_ok = await test_db.test_connection()
                await test_db.disconnect()

                if not connection_ok:
                    raise ConnectionError("Failed to establish test connection")

                # Store configuration
                self._connection_configs[config.name] = config

                # If there's an existing connection, close it
                if config.name in self._connections:
                    await self._disconnect_single(config.name)

                logger.info(
                    f"Added connection configuration: {config.name} ({config.type})"
                )
                return True

            except Exception as e:
                logger.error(f"Failed to add connection '{config.name}': {e}")
                return False

    async def remove_connection(self, name: str) -> bool:
        """Remove a database connection."""
        async with self._lock:
            try:
                if name not in self._connection_configs:
                    logger.warning(f"Connection '{name}' not found")
                    return False

                # Disconnect if active
                if name in self._connections:
                    await self._disconnect_single(name)

                # Remove configuration
                del self._connection_configs[name]
                self._active_connections.discard(name)

                logger.info(f"Removed connection: {name}")
                return True

            except Exception as e:
                logger.error(f"Failed to remove connection '{name}': {e}")
                return False

    async def get_connection(self, name: str) -> Optional[BaseDatabase]:
        """Get an active database connection."""
        async with self._lock:
            try:
                if name not in self._connection_configs:
                    logger.error(f"Connection '{name}' not configured")
                    return None

                # If connection exists and is active, return it
                if name in self._connections and self._connections[name].is_connected:
                    return self._connections[name]

                # Create new connection
                config = self._connection_configs[name]
                db = await DatabaseFactory.create_database(config)

                # Test connection
                if not await db.test_connection():
                    await db.disconnect()
                    raise ConnectionError(f"Connection test failed for '{name}'")

                self._connections[name] = db
                self._active_connections.add(name)

                logger.info(f"Established connection: {name}")
                return db

            except Exception as e:
                logger.error(f"Failed to get connection '{name}': {e}")
                return None

    async def test_connection(self, name: str) -> bool:
        """Test a specific connection."""
        try:
            db = await self.get_connection(name)
            if db:
                return await db.test_connection()
            return False
        except Exception as e:
            logger.error(f"Connection test failed for '{name}': {e}")
            return False

    async def test_all_connections(self) -> Dict[str, bool]:
        """Test all configured connections."""
        results = {}

        for name in self._connection_configs:
            results[name] = await self.test_connection(name)

        return results

    def list_connections(self) -> List[Dict[str, any]]:
        """List all configured connections."""
        connections = []

        for name, config in self._connection_configs.items():
            connections.append(
                {
                    "name": name,
                    "type": config.type,
                    "host": config.host,
                    "port": config.port,
                    "database": config.database,
                    "is_active": name in self._active_connections,
                    "is_connected": name in self._connections
                    and self._connections[name].is_connected,
                }
            )

        return connections

    def get_connection_config(self, name: str) -> Optional[ConnectionConfig]:
        """Get connection configuration."""
        return self._connection_configs.get(name)

    def get_supported_types(self) -> List[DatabaseType]:
        """Get list of supported database types."""
        return DatabaseFactory.get_supported_types()

    async def disconnect_all(self) -> None:
        """Disconnect all active connections."""
        async with self._lock:
            disconnect_tasks = []

            for name in list(self._connections.keys()):
                disconnect_tasks.append(self._disconnect_single(name))

            if disconnect_tasks:
                await asyncio.gather(*disconnect_tasks, return_exceptions=True)

            self._connections.clear()
            self._active_connections.clear()

            logger.info("Disconnected all connections")

    async def _disconnect_single(self, name: str) -> None:
        """Disconnect a single connection (internal method)."""
        try:
            if name in self._connections:
                db = self._connections[name]
                await db.disconnect()
                del self._connections[name]

            self._active_connections.discard(name)
            logger.info(f"Disconnected: {name}")

        except Exception as e:
            logger.error(f"Error disconnecting '{name}': {e}")

    async def reconnect(self, name: str) -> bool:
        """Reconnect a specific connection."""
        async with self._lock:
            try:
                if name not in self._connection_configs:
                    logger.error(f"Connection '{name}' not configured")
                    return False

                # Disconnect existing connection
                if name in self._connections:
                    await self._disconnect_single(name)

                # Reconnect
                db = await self.get_connection(name)
                return db is not None

            except Exception as e:
                logger.error(f"Failed to reconnect '{name}': {e}")
                return False

    async def cleanup(self) -> None:
        """Cleanup resources and disconnect all connections."""
        await self.disconnect_all()
        logger.info("Connection manager cleanup completed")

    def __repr__(self) -> str:
        """String representation."""
        return f"ConnectionManager(connections={len(self._connection_configs)}, active={len(self._active_connections)})"
