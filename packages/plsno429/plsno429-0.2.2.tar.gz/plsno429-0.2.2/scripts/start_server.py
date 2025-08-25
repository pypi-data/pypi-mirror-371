#!/usr/bin/env python3
"""Uvicorn server startup script that uses application settings.

This script reads configuration from environment variables and .env files
through the application's settings system and starts the uvicorn server
with the appropriate parameters.
"""

import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_path))

import uvicorn  # noqa: E402

from plsno429.api.settings import get_settings  # noqa: E402


def main() -> None:
    """Start the uvicorn server with settings-based configuration."""
    # Load application settings
    settings = get_settings()

    # Start uvicorn server with settings
    uvicorn.run(
        'plsno429.app:create_app',
        factory=True,
        host=settings.api_host,
        port=settings.api_port,
        workers=settings.max_workers,
        log_level=settings.log_level.lower(),
        reload=False,  # Disable reload in production
        access_log=True,
    )


if __name__ == '__main__':
    main()
