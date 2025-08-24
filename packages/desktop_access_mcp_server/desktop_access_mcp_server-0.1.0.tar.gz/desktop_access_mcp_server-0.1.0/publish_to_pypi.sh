#!/bin/bash
# Script to clean, build, and publish the package to PyPI

echo "Publishing desktop-access-mcp-server to PyPI"

# Change to the project directory
cd /home/hemang/Documents/GitHub/desktop-access-mcp-server

# Clean up all previous build artifacts
echo "Cleaning up previous build artifacts..."
rm -rf build/
rm -rf dist/
rm -rf *.egg-info/
rm -rf desktop_access_mcp_server.egg-info/

# Also clean up any Python cache files
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true

echo "Build artifacts cleaned successfully!"

# Make sure we have the latest build tools
echo "Ensuring build tools are up to date..."
pip install --upgrade build twine setuptools wheel

# Build the package fresh
echo "Building the package..."
python -m build

# Check if build was successful
if [ ! -d "dist" ] || [ -z "$(ls -A dist)" ]; then
    echo "ERROR: Build failed - no distribution files found in dist/"
    exit 1
fi

echo "Build completed successfully!"
echo "Generated files:"
ls -la dist/

# Upload to PyPI
echo "Uploading to PyPI..."
twine upload dist/*

echo "Package published successfully!"
echo "You can now install it with: pip install desktop-access-mcp-server"
