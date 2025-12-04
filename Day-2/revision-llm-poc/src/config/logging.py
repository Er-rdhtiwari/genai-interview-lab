from __future__ import annotations

"""
Logging configuration helpers.

Provides a setup_logging() function that configures the root logger based on
the current Settings (log level, format, etc.).
"""

import logging

from config.settings import Settings, get_settings


def setup_logging(settings: Settings | None = None) -> None:
    """
    Configure the root logger for the application.

    This should typically be called once at startup (e.g., in app.main).
    """
    if settings is None:
        settings = get_settings()

    # Convert string log level to numeric (INFO, DEBUG, etc.)
    level = getattr(logging, settings.log_level.upper(), logging.INFO)

    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    )

    logging.getLogger(__name__).info(
        "Logging initialized with level=%s (APP_ENV=%s)",
        settings.log_level,
        settings.app_env,
    )
