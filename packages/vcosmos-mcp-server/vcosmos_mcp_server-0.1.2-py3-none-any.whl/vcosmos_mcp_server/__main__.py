#!/usr/bin/env python3
"""
Entry point for running vcosmos_mcp_server as a module.

Usage: python -m vcosmos_mcp_server
       or: uvx vcosmos-mcp-server
"""

from .server import main as server_main
import asyncio

def main():
    """Entry point for console script"""
    asyncio.run(server_main())

if __name__ == "__main__":
    main()
