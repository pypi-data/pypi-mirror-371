#!/usr/bin/env python3
"""Entry point for the Desktop Access MCP Server CLI."""

import asyncio
import sys
import os

# Add the package to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from desktop_access_mcp_server.cli import main

def run_cli():
    """Run the CLI."""
    try:
        result = asyncio.run(main())
        sys.exit(result)
    except KeyboardInterrupt:
        pass  # CLI stopped by user
    except Exception as e:
        print(f"CLI error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    run_cli()