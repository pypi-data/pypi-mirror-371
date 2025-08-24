"""
Database plugins for Thoth SQL Database Manager.
"""

import logging

logger = logging.getLogger(__name__)

# Always available plugin (SQLite is built into Python)
from .sqlite import SQLitePlugin

__all__ = [
    "SQLitePlugin",
]

# Optional plugins - only import if dependencies are available
try:
    import psycopg2
    from .postgresql import PostgreSQLPlugin
    __all__.append("PostgreSQLPlugin")
    logger.debug("PostgreSQL plugin loaded successfully")
except ImportError:
    logger.debug("psycopg2 not installed, PostgreSQL plugin not available")
    PostgreSQLPlugin = None

try:
    import mariadb
    from .mariadb import MariaDBPlugin
    __all__.append("MariaDBPlugin")
    logger.debug("MariaDB plugin loaded successfully")
except ImportError:
    logger.debug("MariaDB connector not installed, MariaDB plugin not available")
    MariaDBPlugin = None

try:
    import pyodbc
    from .sqlserver import SQLServerPlugin
    __all__.append("SQLServerPlugin")
    logger.debug("SQL Server plugin loaded successfully")
except ImportError:
    logger.debug("pyodbc not installed, SQL Server plugin not available")
    SQLServerPlugin = None
