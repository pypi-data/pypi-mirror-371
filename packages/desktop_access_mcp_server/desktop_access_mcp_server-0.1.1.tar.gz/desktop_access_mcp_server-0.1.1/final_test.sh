#!/bin/bash
# Final test script to verify the package works correctly

echo "=== Desktop Access MCP Server - Final Verification ==="

# Test 1: Check if the package is installed
echo "Test 1: Checking if package is installed..."
if python -c "import desktop_access_mcp_server" 2>/dev/null; then
    echo "✓ Package is installed and importable"
else
    echo "✗ Package is not installed or not importable"
    exit 1
fi

# Test 2: Check if the server command is available
echo "Test 2: Checking if server command is available..."
if command -v desktop-access-mcp-server &>/dev/null; then
    echo "✓ Server command is available"
else
    echo "✗ Server command is not available"
    exit 1
fi

# Test 3: Check if the CLI command is available
echo "Test 3: Checking if CLI command is available..."
if command -v desktop-cli &>/dev/null; then
    echo "✓ CLI command is available"
else
    echo "✗ CLI command is not available"
    exit 1
fi

# Test 4: Test the server starts (with timeout)
echo "Test 4: Testing if server starts correctly..."
if timeout 3 desktop-access-mcp-server 2>/dev/null; then
    echo "✓ Server starts correctly"
else
    # Check if it's the expected behavior (server starts but times out)
    if [[ $? -eq 124 ]]; then
        echo "✓ Server starts correctly (timed out as expected)"
    else
        echo "✗ Server failed to start"
        exit 1
    fi
fi

# Test 5: Test the CLI help
echo "Test 5: Testing CLI help..."
if timeout 3 desktop-cli --help 2>/dev/null; then
    echo "✓ CLI help works correctly"
else
    echo "✗ CLI help failed"
    exit 1
fi

echo ""
echo "=== All tests passed! Package is ready for use ==="
echo ""
echo "To use the package:"
echo "1. For direct usage: desktop-access-mcp-server"
echo "2. For CLI usage: desktop-cli"
echo "3. For MCP client configuration, see MCP_SERVER_CONFIG.md"