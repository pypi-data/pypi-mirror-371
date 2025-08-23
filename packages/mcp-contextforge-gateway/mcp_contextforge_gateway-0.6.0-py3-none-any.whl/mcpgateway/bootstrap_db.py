# -*- coding: utf-8 -*-
"""Location: ./mcpgateway/bootstrap_db.py
Copyright 2025
SPDX-License-Identifier: Apache-2.0
Authors: Madhav Kandukuri

Database bootstrap/upgrade entry-point for MCP Gateway.
The script:

1. Creates a synchronous SQLAlchemy ``Engine`` from ``settings.database_url``.
2. Looks for an *alembic.ini* two levels up from this file to drive migrations.
3. If the database is still empty (no ``gateways`` table), it:
   - builds the base schema with ``Base.metadata.create_all()``
   - stamps the migration head so Alembic knows it is up-to-date
4. Otherwise, it applies any outstanding Alembic revisions.
5. Logs a **"Database ready"** message on success.

It is intended to be invoked via ``python3 -m mcpgateway.bootstrap_db`` or
directly with ``python3 mcpgateway/bootstrap_db.py``.

Examples:
    >>> from mcpgateway.bootstrap_db import logging_service, logger
    >>> logging_service is not None
    True
    >>> logger is not None
    True
    >>> hasattr(logger, 'info')
    True
    >>> from mcpgateway.bootstrap_db import Base
    >>> hasattr(Base, 'metadata')
    True
"""

# Standard
import asyncio
from importlib.resources import files

# Third-Party
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect

# First-Party
from mcpgateway.config import settings
from mcpgateway.db import Base
from mcpgateway.services.logging_service import LoggingService

# Initialize logging service first
logging_service = LoggingService()
logger = logging_service.get_logger(__name__)


async def main() -> None:
    """
    Bootstrap or upgrade the database schema, then log readiness.

    Runs `create_all()` + `alembic stamp head` on an empty DB, otherwise just
    executes `alembic upgrade head`, leaving application data intact.

    Args:
        None
    """
    engine = create_engine(settings.database_url)
    ini_path = files("mcpgateway").joinpath("alembic.ini")
    cfg = Config(str(ini_path))  # path in container
    cfg.attributes["configure_logger"] = True

    with engine.begin() as conn:
        cfg.attributes["connection"] = conn
        cfg.set_main_option("sqlalchemy.url", settings.database_url)

        insp = inspect(conn)

        if "gateways" not in insp.get_table_names():
            logger.info("Empty DB detected - creating baseline schema")
            Base.metadata.create_all(bind=conn)
            command.stamp(cfg, "head")
        else:
            command.upgrade(cfg, "head")

    logger.info("Database ready")


if __name__ == "__main__":
    asyncio.run(main())
