#!/usr/bin/env python3
import asyncio
import sys
import os

# Add the package to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from desktop_access_mcp_server.__main__ import main

print("Testing direct call to main function")
print(f"main function: {main}")
print(f"main function type: {type(main)}")

try:
    # Try to run the function directly
    result = main()
    print(f"Result: {result}")
    print(f"Result type: {type(result)}")
except Exception as e:
    print(f"Error calling main directly: {e}")

try:
    # Try with asyncio.run
    print("Trying with asyncio.run")
    result = asyncio.run(main())
    print(f"Result: {result}")
except Exception as e:
    print(f"Error with asyncio.run: {e}")