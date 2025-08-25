"""DSN (Data Source Name) parser for various database types."""

import re
from typing import Dict, Optional, Tuple
from urllib.parse import parse_qs, urlparse

from .types import ConnectionConfig, DatabaseType


class DSNParser:
    """Parser for database DSN strings."""

    # DSN format patterns for different databases
    DSN_PATTERNS = {
        "postgresql": r"^postgres(?:ql)?://",
        "mysql": r"^mysql://",
        "sqlite": r"^sqlite://",
        "mongodb": r"^mongodb(?:\+srv)?://",
        "redis": r"^redis://",
        "mssql": r"^(?:sqlserver|mssql)://",
    }

    @classmethod
    def parse_dsn(
        cls, dsn: str, connection_name: str = "dsn-connection"
    ) -> ConnectionConfig:
        """
        Parse a DSN string and return a ConnectionConfig.

        Supported formats:
        - PostgreSQL: postgresql://user:pass@host:port/dbname?param=value
        - MySQL: mysql://user:pass@host:port/dbname?param=value
        - SQLite: sqlite:///path/to/database.db or sqlite:///:memory:
        - MongoDB: mongodb://user:pass@host:port/dbname?param=value
        - Redis: redis://user:pass@host:port/db?param=value
        - SQL Server: sqlserver://user:pass@host:port/dbname?param=value
        """
        if not dsn:
            raise ValueError("DSN string cannot be empty")

        # Determine database type from DSN
        db_type = cls._detect_database_type(dsn)

        if db_type == DatabaseType.SQLITE:
            return cls._parse_sqlite_dsn(dsn, connection_name)
        else:
            return cls._parse_standard_dsn(dsn, connection_name, db_type)

    @classmethod
    def _detect_database_type(cls, dsn: str) -> DatabaseType:
        """Detect database type from DSN string."""
        dsn_lower = dsn.lower()

        for db_name, pattern in cls.DSN_PATTERNS.items():
            if re.match(pattern, dsn_lower):
                if db_name == "postgresql":
                    return DatabaseType.POSTGRESQL
                elif db_name == "mysql":
                    return DatabaseType.MYSQL
                elif db_name == "sqlite":
                    return DatabaseType.SQLITE
                elif db_name == "mongodb":
                    return DatabaseType.MONGODB
                elif db_name == "redis":
                    return DatabaseType.REDIS
                elif db_name == "mssql":
                    return DatabaseType.MSSQL

        raise ValueError(f"Unsupported or unrecognized DSN format: {dsn}")

    @classmethod
    def _parse_sqlite_dsn(cls, dsn: str, connection_name: str) -> ConnectionConfig:
        """Parse SQLite DSN string."""
        parsed = urlparse(dsn)

        # SQLite path can be absolute or relative
        database_path = parsed.path
        if database_path.startswith("/"):
            database_path = database_path[
                1:
            ]  # Remove leading slash for Windows compatibility

        return ConnectionConfig(
            name=connection_name,
            type=DatabaseType.SQLITE,
            host="",  # SQLite doesn't use host
            port=None,
            username=None,
            password=None,
            database=database_path,
            ssl=False,
        )

    @classmethod
    def _parse_standard_dsn(
        cls, dsn: str, connection_name: str, db_type: DatabaseType
    ) -> ConnectionConfig:
        """Parse standard DSN format for network databases."""
        parsed = urlparse(dsn)

        # Extract basic connection info
        host = parsed.hostname or "localhost"
        port = parsed.port
        username = parsed.username
        password = parsed.password
        database = parsed.path.lstrip("/") if parsed.path else None

        # Parse query parameters
        query_params = parse_qs(parsed.query)

        # Handle SSL settings
        ssl = True  # Default to SSL
        if "sslmode" in query_params:
            ssl_mode = query_params["sslmode"][0].lower()
            ssl = ssl_mode not in ["disable", "false", "off", "no"]
        elif "ssl" in query_params:
            ssl_value = query_params["ssl"][0].lower()
            ssl = ssl_value in ["true", "on", "yes", "1"]

        # Handle schema
        schema = query_params.get("schema", [None])[0]

        # Set default ports if not specified
        if port is None:
            default_ports = {
                DatabaseType.POSTGRESQL: 5432,
                DatabaseType.MYSQL: 3306,
                DatabaseType.MONGODB: 27017,
                DatabaseType.REDIS: 6379,
                DatabaseType.MSSQL: 1433,
            }
            port = default_ports.get(db_type)

        return ConnectionConfig(
            name=connection_name,
            type=db_type,
            host=host,
            port=port,
            username=username,
            password=password,
            database=database,
            schema_name=schema,
            ssl=ssl,
            options=cls._extract_additional_options(query_params),
        )

    @classmethod
    def _extract_additional_options(cls, query_params: Dict) -> Dict[str, str]:
        """Extract additional options from query parameters."""
        # Skip common parameters that are handled separately
        skip_params = {"sslmode", "ssl", "schema"}

        options = {}
        for key, values in query_params.items():
            if key not in skip_params and values:
                options[key] = values[0]  # Take first value

        return options

    @classmethod
    def validate_dsn(cls, dsn: str) -> Tuple[bool, Optional[str]]:
        """
        Validate a DSN string.

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            cls.parse_dsn(dsn)
            return True, None
        except Exception as e:
            return False, str(e)

    @classmethod
    def get_supported_schemes(cls) -> list[str]:
        """Get list of supported DSN schemes."""
        return [
            "postgresql://",
            "postgres://",
            "mysql://",
            "sqlite://",
            "mongodb://",
            "mongodb+srv://",
            "redis://",
            "sqlserver://",
            "mssql://",
        ]


def parse_dsn_from_env(
    env_var: str, connection_name: str = None
) -> Optional[ConnectionConfig]:
    """
    Parse DSN from environment variable.

    Args:
        env_var: Environment variable name containing DSN
        connection_name: Name for the connection (defaults to env_var name)

    Returns:
        ConnectionConfig if DSN found and valid, None otherwise
    """
    import os

    dsn = os.getenv(env_var)
    if not dsn:
        return None

    if connection_name is None:
        connection_name = env_var.lower().replace("_", "-")

    try:
        return DSNParser.parse_dsn(dsn, connection_name)
    except Exception:
        return None
