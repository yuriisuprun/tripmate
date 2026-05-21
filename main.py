#!/usr/bin/env python3
"""Entry point for the repo-assistant-mcp server."""

from __future__ import annotations

import asyncio
import sys

from app.server import main


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped.")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)
