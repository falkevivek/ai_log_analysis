"""
Database Initialisation Script
================================
Standalone script that initialises the database and runs Alembic migrations.

Usage:
    python scripts/init_db.py

Run this after setting up your .env file and before starting the application
for the first time.

Note: This script uses the sync SQLAlchemy engine (psycopg2) because Alembic
does not support asyncpg.
"""

from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path

# Ensure the project root is on sys.path so imports resolve correctly.
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config.settings import get_settings
from app.core.logging import configure_logging
from app.database.session import close_db, init_db

configure_logging()
logger = logging.getLogger("ai_analysis_engine.scripts.init_db")


async def main() -> None:
    """Verify database connectivity and report readiness."""
    settings = get_settings()

    logger.info("Starting database initialisation...")
    logger.info("Target: %s@%s:%d/%s",
                settings.database.user,
                settings.database.host,
                settings.database.port,
                settings.database.name)

    try:
        await init_db()
        logger.info("✓ Database connection verified successfully.")
        logger.info("Database is ready to accept connections.")
    except Exception as exc:
        logger.error("✗ Database initialisation failed: %s", exc)
        sys.exit(1)
    finally:
        await close_db()


if __name__ == "__main__":
    asyncio.run(main())
