#!/bin/bash
# Script to test running the server with uvx from local package

echo "Testing uvx with local package..."

# Change to the project directory
cd /home/hemang/Documents/GitHub/desktop-access-mcp-server

# Try to run with uvx using --from
echo "Trying uvx --from . desktop-access-mcp-server"
timeout 3 uvx --from . desktop-access-mcp-server