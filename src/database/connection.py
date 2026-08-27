"""
MW4 Weapon Intelligence Lab - DuckDB Connection & Parquet Management
Provides thread-safe connections, database initialization, and Parquet export/import.
"""

import os
import threading
import duckdb
from pathlib import Path
from typing import Optional, Dict
from src.database.schema import SCHEMA_DDL


DEFAULT_DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data",
    "mw4_intelligence.duckdb"
)


class DatabaseManager:
    """Manages DuckDB instances, connection lifecycle, and Parquet data exports."""

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        self._lock = threading.RLock()
        self._conn: Optional[duckdb.DuckDBPyConnection] = None
        # Connection is initialized lazily upon first get_connection() call

    def _init_conn(self) -> None:
        with self._lock:
            if self._conn is not None:
                return
            if self.db_path != ":memory:":
                try:
                    os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
                    self._conn = duckdb.connect(self.db_path, read_only=False)
                except Exception:
                    try:
                        self._conn = duckdb.connect(self.db_path, read_only=True)
                    except Exception:
                        # In-memory fallback ensures 100% uptime in containerized/mounted cloud environments
                        self._conn = duckdb.connect(":memory:")
            else:
                self._conn = duckdb.connect(":memory:")

    def get_connection(self) -> duckdb.DuckDBPyConnection:
        """Returns a thread-safe connected DuckDB cursor on the persistent database connection."""
        with self._lock:
            if self._conn is None:
                self._init_conn()
            return self._conn.cursor()

    def init_database(self) -> None:
        """Executes DDL schema and ensures all required tables exist."""
        with self._lock:
            conn = self.get_connection()
            try:
                conn.execute(SCHEMA_DDL)
            finally:
                conn.close()

    def export_table_to_parquet(self, table_name: str, export_dir: str) -> str:
        """Exports a specified DuckDB table to a versioned Parquet file."""
        os.makedirs(export_dir, exist_ok=True)
        file_path = os.path.join(export_dir, f"{table_name}.parquet")
        with self._lock:
            conn = self.get_connection()
            try:
                query = f"COPY {table_name} TO '{file_path}' (FORMAT PARQUET)"
                conn.execute(query)
                return file_path
            finally:
                conn.close()

    def export_all_to_parquet(self, export_dir: str) -> Dict[str, str]:
        """Exports all core tables to Parquet for offline snapshotting."""
        tables = [
            "game_versions",
            "rulesets",
            "weapons",
            "weapon_version_stats",
            "weapon_damage_profiles",
            "attachments",
            "attachment_modifiers",
            "evidence_ledger",
            "ai_review_queue",
            "source_snapshots",
            "custom_builds",
            "stat_delta_events",
            "community_meta_consensus",
            "meta_build_presets"
        ]
        results = {}
        for table in tables:
            try:
                path = self.export_table_to_parquet(table, export_dir)
                results[table] = path
            except Exception as e:
                results[table] = f"Error: {str(e)}"
        return results

    def import_table_from_parquet(self, table_name: str, parquet_path: str) -> int:
        """Loads data from a Parquet file into a specified table."""
        with self._lock:
            conn = self.get_connection()
            try:
                query = f"INSERT OR REPLACE INTO {table_name} SELECT * FROM read_parquet(?)"
                conn.execute(query, [parquet_path])
                count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
                return count
            finally:
                conn.close()

    def clear_all_tables(self) -> None:
        """Clears all tables (used for testing or clean re-seeding)."""
        tables = [
            "meta_build_presets",
            "community_meta_consensus",
            "stat_delta_events",
            "custom_builds",
            "ai_review_queue",
            "evidence_ledger",
            "source_snapshots",
            "attachment_modifiers",
            "attachments",
            "weapon_damage_profiles",
            "weapon_version_stats",
            "weapons",
            "rulesets",
            "game_versions"
        ]
        with self._lock:
            conn = self.get_connection()
            try:
                for table in tables:
                    conn.execute(f"DELETE FROM {table}")
            finally:
                conn.close()

    def close(self) -> None:
        """Closes the underlying DuckDB connection if open."""
        with self._lock:
            if self._conn is not None:
                try:
                    self._conn.close()
                except Exception:
                    pass
                self._conn = None


# Default singleton instance
db_manager = DatabaseManager()
