"""
Storage and Repository Abstractions
===================================
Defines the abstract interface (contract) for the platform's data layer.

Architecture Rationale
-----------------------
Following the Dependency Inversion Principle (D), the high-level business logic
(engines, routers) depends on the abstract `StorageInterface` rather than
concrete implementations (like in-memory dictionary or SQLAlchemy sessions).

All operations are defined as asynchronous (`async def`) so that when the
storage backend is migrated to PostgreSQL (using SQLAlchemy + `asyncpg`), the
route controllers and downstream logic do not need to change their syntax.
"""

from __future__ import annotations

from typing import Any, Protocol


class StorageInterface(Protocol):
    """
    Abstract interface defining data storage contract.

    Acts as a generic repository abstraction for collections of documents
    (such as raw logs, events, timeline events, and incident diagnostic reports).
    """

    async def save(self, collection: str, record: dict[str, Any]) -> dict[str, Any]:
        """
        Insert or update a record in the collection.

        Parameters
        ----------
        collection:
            Logical database table/collection name (e.g. 'incidents', 'logs').
        record:
            Data payload to store.

        Returns
        -------
        dict
            The persisted record containing generated ID and timestamps.
        """
        ...

    async def get(self, collection: str, record_id: str) -> dict[str, Any] | None:
        """
        Retrieve a single record from a collection by ID.

        Returns None if the record does not exist.
        """
        ...

    async def list(self, collection: str) -> list[dict[str, Any]]:
        """
        List all records in a collection, ordered by creation time ascending.
        """
        ...

    async def delete(self, collection: str, record_id: str) -> bool:
        """
        Delete a record by ID. Returns True if deleted, False otherwise.
        """
        ...

    async def clear(self, collection: str) -> None:
        """
        Clear all records in a collection (primarily for testing/development resets).
        """
        ...

    async def count(self, collection: str) -> int:
        """
        Return the total number of records in a collection.
        """
        ...

    async def collections(self) -> list[str]:
        """
        Return names of all active collections containing records.
        """
        ...

    async def stats(self) -> dict[str, int]:
        """
        Return health stats and record counts per collection.
        """
        ...
