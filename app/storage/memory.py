"""
In-Memory Storage
=================
Thread-safe, dictionary-backed store used as the data layer for Freeze Point 1.

PostgreSQL Migration Path
--------------------------
When PostgreSQL is introduced, create ``app/storage/postgres.py`` that exposes
the same ``Store`` interface (``save``, ``get``, ``list``, ``delete``, ``clear``).
Then update the single import in ``app/main.py``:

    # Before
    from app.storage.memory import InMemoryStore as Store

    # After
    from app.storage.postgres import PostgresStore as Store

No other file changes are required. Route handlers always access storage via
``request.app.state.store`` — they are completely decoupled from the backend.

Interface Contract
------------------
Every collection is a named namespace (e.g. "incidents", "logs").
Records are plain dicts. ``save()`` assigns a UUID ``id`` field if absent.
"""

from __future__ import annotations

import uuid
from collections import defaultdict
from datetime import datetime, timezone
from threading import Lock
from typing import Any


from app.storage.base import StorageInterface


class InMemoryStore(StorageInterface):
    """
    Thread-safe in-memory key-value store organised by collection.

    Implements StorageInterface. Designed to mirror the interface a future
    PostgreSQL repository will expose, so swapping the backend requires
    no changes to route handlers.
    """

    def __init__(self) -> None:
        # { collection_name: { record_id: record_dict } }
        self._data: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
        self._lock = Lock()

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def save(self, collection: str, record: dict[str, Any]) -> dict[str, Any]:
        """
        Insert or update a record in the given collection.

        If the record does not have an ``id`` field, one is generated.
        ``created_at`` is set on first insert; ``updated_at`` is always refreshed.

        Parameters
        ----------
        collection:
            Logical namespace, e.g. ``"incidents"`` or ``"logs"``.
        record:
            Plain dict representing the record.

        Returns
        -------
        dict
            The stored record including generated ``id`` and timestamps.
        """
        with self._lock:
            now = datetime.now(tz=timezone.utc).isoformat()
            record = dict(record)  # avoid mutating the caller's dict

            if "id" not in record or not record["id"]:
                record["id"] = str(uuid.uuid4())

            existing = self._data[collection].get(record["id"])
            record["created_at"] = existing["created_at"] if existing else now
            record["updated_at"] = now

            self._data[collection][record["id"]] = record
            return dict(record)

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def get(self, collection: str, record_id: str) -> dict[str, Any] | None:
        """
        Retrieve a single record by ID.

        Returns ``None`` if the record does not exist.
        """
        with self._lock:
            record = self._data[collection].get(record_id)
            return dict(record) if record else None

    def list(self, collection: str) -> list[dict[str, Any]]:
        """
        Return all records in a collection, ordered by ``created_at`` ascending.
        """
        with self._lock:
            records = list(self._data[collection].values())
            return sorted(records, key=lambda r: r.get("created_at", ""))

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    def delete(self, collection: str, record_id: str) -> bool:
        """
        Remove a record by ID.

        Returns ``True`` if the record existed and was deleted, ``False`` otherwise.
        """
        with self._lock:
            if record_id in self._data[collection]:
                del self._data[collection][record_id]
                return True
            return False

    def clear(self, collection: str) -> None:
        """Remove all records from a collection. Useful for development resets."""
        with self._lock:
            self._data[collection].clear()

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def count(self, collection: str) -> int:
        """Return the number of records in a collection."""
        with self._lock:
            return len(self._data[collection])

    def collections(self) -> list[str]:
        """Return the names of all non-empty collections."""
        with self._lock:
            return [name for name, records in self._data.items() if records]

    def stats(self) -> dict[str, int]:
        """Return record counts per collection. Used by the health endpoint."""
        with self._lock:
            return {name: len(records) for name, records in self._data.items()}
