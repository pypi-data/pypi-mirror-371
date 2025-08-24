"""
Database adapters for Thoth SQL Database Manager.
"""

import logging

logger = logging.getLogger(__name__)

# Always available adapter (SQLite is built into Python)
from .sqlite import SQLiteAdapter

__all__ = [
    "SQLiteAdapter",
]

# Optional adapters - only import if dependencies are available
try:
    import psycopg2
    from .postgresql import PostgreSQLAdapter
    __all__.append("PostgreSQLAdapter")
except ImportError:
    logger.debug("psycopg2 not installed, PostgreSQLAdapter not available")
    PostgreSQLAdapter = None

try:
    import mariadb
    from .mariadb import MariaDBAdapter
    __all__.append("MariaDBAdapter")
except ImportError:
    logger.debug("MariaDB connector not installed, MariaDBAdapter not available")
    MariaDBAdapter = None

try:
    import pyodbc
    from .sqlserver import SQLServerAdapter
    __all__.append("SQLServerAdapter")
except ImportError:
    logger.debug("pyodbc not installed, SQLServerAdapter not available")
    SQLServerAdapter = None
