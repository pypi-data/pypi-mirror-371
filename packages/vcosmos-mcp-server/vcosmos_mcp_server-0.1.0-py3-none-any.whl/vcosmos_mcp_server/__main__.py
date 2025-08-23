#!/usr/bin/env python3
"""
Entry point for running vcosmos_mcp_server as a module.

Usage: python -m vcosmos_mcp_server
"""

from .server import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())
