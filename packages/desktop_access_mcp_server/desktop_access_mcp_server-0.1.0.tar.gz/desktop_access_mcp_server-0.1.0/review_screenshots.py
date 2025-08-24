#!/usr/bin/env python3
"""
Screenshot review script.
This script helps review the captured screenshots and provides detailed information about each one.
"""

import os
import json
from PIL import Image
import sys

def review_screenshots(test_dir="test_screenshots"):
    """Review all captured screenshots with detailed information."""
    if not os.path.exists(test_dir):
        print(f"Test directory '{test_dir}' not found.")
        return
    
    # Get all files in the test directory
    files = sorted(os.listdir(test_dir))
    
    # Separate images, metadata, and summary files
    images = [f for f in files if f.endswith(('.png', '.jpeg', '.jpg')) and not f.endswith('_metadata.json')]
    metadata_files = [f for f in files if f.endswith('_metadata.json')]
    summary_files = [f for f in files if f.startswith('test_summary_') and f.endswith('.txt')]
    
    print("Screenshot Review")
    print("=" * 50)
    print(f"Found {len(images)} screenshots, {len(metadata_files)} metadata files, and {len(summary_files)} summary files.\\n")
    
    # Display summary if available
    if summary_files:
        print("Test Summary:")
        print("-" * 20)
        with open(os.path.join(test_dir, summary_files[0]), 'r') as f:
            print(f.read())
        print("\\n")
    
    # Display each screenshot with details
    print("Detailed Screenshot Information:")
    print("-" * 35)
    
    for image_file in images:
        print(f"\\n\\U0001F4F7 {image_file}")
        
        # Try to get metadata
        metadata_file = image_file.rsplit('.', 1)[0] + '_metadata.json'
        if metadata_file in files:
            try:
                with open(os.path.join(test_dir, metadata_file), 'r') as f:
                    metadata = json.load(f)
                
                # Display metadata
                print(f"   Test: {metadata.get('test_name', 'Unknown')}")
                print(f"   Size: {metadata['result']['size']['width']}x{metadata['result']['size']['height']}")
                print(f"   Format: {metadata['result']['format'].upper()}")
                print(f"   Monitor: {metadata['result'].get('monitor', 'Unknown')}")
                print(f"   Timestamp: {metadata.get('timestamp', 'Unknown')}")
                
                # Try to get actual image dimensions
                try:
                    img_path = os.path.join(test_dir, image_file)
                    with Image.open(img_path) as img:
                        print(f"   Actual Size: {img.width}x{img.height}")
                        print(f"   Mode: {img.mode}")
                except Exception as e:
                    print(f"   Error getting image info: {e}")
                    
            except Exception as e:
                print(f"   Error reading metadata: {e}")
        else:
            print("   No metadata available")
    
    print("\\n" + "=" * 50)
    print("Review complete. Check the images in the test_screenshots directory.")

if __name__ == "__main__":
    review_screenshots()
