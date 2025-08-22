# src/canonmap/connectors/mysql_connector/connector.py

import logging
import re
import time
from contextlib import contextmanager
from typing import Any, List, Optional

from mysql.connector.pooling import MySQLConnectionPool

from canonmap.connectors.mysql_connector.config import MySQLConfig


logger = logging.getLogger(__name__)


class MySQLConnector:
    """Manages a MySQL connection pool and provides connection contexts."""

    def __init__(self, config: MySQLConfig):
        self.config = config
        self._pool: Optional[MySQLConnectionPool] = None
        # Provide an instance logger used by utils for optional logging
        self.logger = logger

    def initialize_pool(self) -> None:
        if self._pool is None:
            self._pool = MySQLConnectionPool(**self.config.to_pool_dict())

    def get_pool(self) -> MySQLConnectionPool:
        if self._pool is None:
            self.initialize_pool()
        return self._pool

    @contextmanager
    def get_connection(self):
        conn = self.get_pool().get_connection()
        try:
            yield conn
        finally:
            conn.close()

    @contextmanager
    def transaction(self):
        """Begin a transaction: commit on success, rollback on exception."""
        conn = self.get_pool().get_connection()
        conn.autocommit = False
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def close_pool(self):
        """Close all pooled connections."""
        if self._pool is None:
            return
        logger.info("Pool cleanup completed")
        self._pool = None

    def execute_query(self, query: str, params: Optional[List[Any]] = None, allow_writes: bool = False, limit: Optional[int] = 1000) -> Any:
        query_upper = query.strip().upper()
        if not allow_writes and not query_upper.startswith("SELECT"):
            raise ValueError("Writes are disallowed; set allow_writes=True to proceed.")

        # Prepare SQL and params for execution, applying LIMIT policy for SELECTs when requested
        sql_query = query
        final_params: List[Any] = list(params) if isinstance(params, list) else ([] if params is None else list(params))
        if not allow_writes and limit is not None:
            # Only manipulate SELECT statements
            limit_pattern = re.compile(r"LIMIT\s+(\d+)\s*;?\s*$", re.IGNORECASE)
            match = limit_pattern.search(sql_query)
            if match:
                existing_limit = int(match.group(1))
                if limit < existing_limit:
                    sql_query = limit_pattern.sub("LIMIT %s", sql_query.rstrip())
                    final_params.append(limit)
                    logger.info("Replacing existing LIMIT %d with stricter LIMIT %d", existing_limit, limit)
                else:
                    logger.info("Respecting existing LIMIT %d (<= requested %d)", existing_limit, limit)
            else:
                # Append a parameterized LIMIT
                sql_query = sql_query.rstrip().rstrip(";") + " LIMIT %s"
                final_params.append(limit)
                logger.info("Appending LIMIT %d to query", limit)

        start = time.time()
        with self.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(sql_query, final_params)
                if cursor.with_rows:
                    data = cursor.fetchall()
                else:
                    conn.commit()
                    data = {"affected_rows": cursor.rowcount}
                duration = time.time() - start
                logger.info("Query executed in %.4f sec", duration)
                return {"data": data, "error": None, "final_sql": sql_query}
            except Exception as e:
                # For write operations, preserve exception semantics for upstream retry logic
                if allow_writes:
                    # Attach context for logging, then re-raise
                    logger.exception("Write query failed: %s", e)
                    raise
                # For read operations, return a structured error without raising
                logger.exception("Read query failed: %s", e)
                return {"data": None, "error": str(e), "final_sql": sql_query}
            finally:
                cursor.close()


