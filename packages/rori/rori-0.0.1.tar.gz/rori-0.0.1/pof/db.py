import json
import sqlite3
from pathlib import Path
from typing import Optional

from pof import config
from pof.models import PofDbEntry


class PofDb:
    """SQLite database manager for port forward entries."""

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize database connection."""
        if db_path is None:
            db_path = config.POF_DIR / "pof.db"

        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """Initialize database tables."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pofs (
                    hid INTEGER PRIMARY KEY,
                    port_from INTEGER NOT NULL,
                    port_to INTEGER NOT NULL,
                    type TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT,
                    UNIQUE(hid)
                )
            """)
            conn.commit()

    def add(self, entry: PofDbEntry) -> int:
        """Add a new port forward entry."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                INSERT OR REPLACE INTO pofs
                (hid, port_from, port_to, type, metadata)
                VALUES (?, ?, ?, ?, ?)""",
                (
                    entry.hid,
                    entry.port_from,
                    entry.port_to,
                    entry.type_,
                    json.dumps(entry.metadata),
                ),
            )

            entry_id = cursor.lastrowid
            conn.commit()
            return entry_id or 0

    def get(self, pof_id: int) -> Optional[PofDbEntry]:
        """Get a specific port forward entry by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            query = "SELECT * FROM pofs WHERE hid = ?"
            cursor = conn.execute(query, (pof_id,))

            row = cursor.fetchone()
            if row:
                return self._row_to_entry(row)

    def get_all_entries(self) -> list[PofDbEntry]:
        """Get all port forward entries."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM port_forwards ORDER BY created_at DESC
            """)

            return [self._row_to_entry(row) for row in cursor.fetchall()]

    def get_entries_by_status(self, status: str) -> list[PofDbEntry]:
        """Get entries filtered by status."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """
                SELECT * FROM port_forwards WHERE status = ? ORDER BY created_at DESC
            """,
                (status,),
            )

            return [self._row_to_entry(row) for row in cursor.fetchall()]

    def get_entries_by_type(self, entry_type: str) -> list[PofDbEntry]:
        """Get entries filtered by type."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """
                SELECT * FROM port_forwards WHERE type = ? ORDER BY created_at DESC
            """,
                (entry_type,),
            )

            return [self._row_to_entry(row) for row in cursor.fetchall()]

    def update(self, entry: PofDbEntry) -> bool:
        """Update an existing port forward entry."""
        if entry.id_ is None:
            return False

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                UPDATE port_forwards SET
                    name = ?, port_from = ?, port_to = ?, status = ?, type = ?,
                    uptime = ?, namespace = ?, resource_name = ?, context = ?,
                    local_address = ?, command = ?, pid = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """,
                (
                    entry.name,
                    entry.port_from,
                    entry.port_to,
                    entry.status,
                    entry.type_,
                    entry.id_,
                ),
            )

            conn.commit()
            return cursor.rowcount > 0

    def delete(self, pof_id: int) -> bool:
        """Delete a port forward entry."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                DELETE FROM pofs WHERE hid = ?
            """,
                (pof_id,),
            )

            conn.commit()
            return cursor.rowcount > 0

    def update_status(
        self, entry_id: int, status: str, pid: Optional[int] = None
    ) -> bool:
        """Update the status of a port forward entry."""
        with sqlite3.connect(self.db_path) as conn:
            if pid is not None:
                cursor = conn.execute(
                    """
                    UPDATE port_forwards SET status = ?, pid = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """,
                    (status, pid, entry_id),
                )
            else:
                cursor = conn.execute(
                    """
                    UPDATE port_forwards SET status = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """,
                    (status, entry_id),
                )

            conn.commit()
            return cursor.rowcount > 0

    def cleanup_inactive_entries(self) -> int:
        """Remove old inactive entries (older than 30 days)."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                DELETE FROM port_forwards 
                WHERE status = 'inactive' 
                AND created_at < datetime('now', '-30 days')
            """)

            conn.commit()
            return cursor.rowcount

    def get_stats(self) -> dict:
        """Get database statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active,
                    SUM(CASE WHEN status = 'inactive' THEN 1 ELSE 0 END) as inactive,
                    COUNT(DISTINCT type) as types
                FROM port_forwards
            """)

            row = cursor.fetchone()
            return {
                "total": row[0],
                "active": row[1],
                "inactive": row[2],
                "types": row[3],
            }

    def _row_to_entry(self, row) -> PofDbEntry:
        """Convert database row to PortForwardEntry."""
        return PofDbEntry(
            hid=row["hid"],
            port_from=row["port_from"],
            port_to=row["port_to"],
            type_=row["type"],
            created_at=row["created_at"],
            metadata=json.loads(row["metadata"]),
        )
