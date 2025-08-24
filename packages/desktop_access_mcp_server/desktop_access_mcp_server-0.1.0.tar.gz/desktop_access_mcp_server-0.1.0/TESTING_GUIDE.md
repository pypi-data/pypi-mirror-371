# Screenshot Testing Guide

This guide explains how to use the comprehensive screenshot testing system to evaluate and debug the multi-monitor screenshot functionality.

## Directory Structure

```
test_screenshots/
├── Timestamp_TestName_Monitor_WidthxHeight.png/jpeg
├── Timestamp_TestName_Monitor_WidthxHeight_metadata.json
└── test_summary_Timestamp.txt
```

## Naming Convention

Each screenshot filename contains detailed information:
- **Timestamp**: YYYYMMDD_HHMMSS format
- **TestName**: Descriptive name of the test
- **Monitor**: M0 for combined, M1+ for individual monitors
- **WidthxHeight**: Resolution of the screenshot

Example: `20250823_223836_Combined_All_Monitors_M0_2446x1920.png`

## Types of Tests

1. **Combined Screenshots**: Captures all monitors as one image
2. **Individual Monitor Screenshots**: Captures each monitor separately
3. **Different Formats**: PNG and JPEG formats with various quality settings

## How to Review Screenshots

1. **Check the Summary**: Look at the `test_summary_*.txt` file for overall results
2. **Review Individual Images**: Open screenshots in order of timestamp
3. **Compare Metadata**: Check JSON metadata files for technical details
4. **Verify Accuracy**: Ensure each screenshot matches the expected monitor layout

## Expected Results for Your Setup

Based on your monitor configuration:
- **Laptop Display (eDP-1)**: Positioned at (0, 876) with resolution 1366x768
- **HDMI Display (HDMI-1)**: Positioned at (1366, 0) with resolution 1080x1920
- **Combined Image**: Should be 2446x1920 representing the extended desktop

## Debugging Tips

1. **Check Monitor Layout**: Verify the detected monitor positions match your actual setup
2. **Compare Individual vs Combined**: Ensure individual screenshots are correctly positioned in the combined image
3. **Verify Dimensions**: Each screenshot should match the expected resolution
4. **Look for Artifacts**: Check for black bars, misalignment, or missing content

## Running Tests

```bash
# Run all tests
python run_screenshot_tests.py

# Review results
python review_screenshots.py
```

## Interpreting Results

- **✅ Good**: Combined screenshot shows both monitors correctly positioned
- **⚠ Acceptable**: Minor alignment issues that don't affect usability
- **✗ Bad**: Missing monitors, severe misalignment, or completely wrong content