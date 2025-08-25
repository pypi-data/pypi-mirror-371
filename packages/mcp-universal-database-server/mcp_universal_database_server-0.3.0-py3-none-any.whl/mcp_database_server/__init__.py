"""MCP Database Server - Universal database connection and operations server."""

__version__ = "0.1.0"
__author__ = "Adarsh Bhayani"
__email__ = "your.email@example.com"

from .server import DatabaseMCPServer
from .connection_manager import ConnectionManager
from .database_factory import DatabaseFactory

__all__ = [
    "DatabaseMCPServer",
    "ConnectionManager",
    "DatabaseFactory",
]
