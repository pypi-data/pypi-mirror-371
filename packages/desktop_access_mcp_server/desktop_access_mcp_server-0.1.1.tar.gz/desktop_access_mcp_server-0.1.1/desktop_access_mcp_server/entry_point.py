#!/usr/bin/env python3
"""Entry point for the Desktop Access MCP Server."""

import asyncio
import sys
import os

# Add the package to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from desktop_access_mcp_server.__main__ import main

def run_server():
    """Run the server."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass  # Server stopped by user
    except Exception as e:
        print(f"Server error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    run_server()