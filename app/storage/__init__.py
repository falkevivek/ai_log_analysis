"""
Storage Package Entrypoint
===========================
Exposes abstract storage interfaces and concrete implementations.
"""

from __future__ import annotations

from app.storage.base import StorageInterface
from app.storage.memory import InMemoryStore

__all__ = [
    "StorageInterface",
    "InMemoryStore",
]
