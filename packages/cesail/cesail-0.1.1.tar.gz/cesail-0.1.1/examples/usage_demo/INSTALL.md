# CeSail Installation and Usage Guide

This guide shows how to install and use the CeSail package from PyPI, including testing the installation and running example scripts.

## Quick Installation

1. **Install CeSail from PyPI**:
   ```bash
   pip install cesail
   ```

2. **Install Playwright browsers** (required for web automation):
   ```bash
   playwright install
   ```

3. **Test the installation**:
   ```bash
   python test_installation.py
   ```

## Installation Test

The `test_installation.py` script verifies that all components are properly installed:

```bash
python test_installation.py
```

**Expected output**:
```
🚀 CeSail Installation Test
========================================
🧪 Testing CeSail package installation...
✅ Successfully imported cesail package
   Version: 0.1.0
   Author: CeSail Contributors
✅ Successfully imported DOMParser, Action, and ActionType
✅ ActionType.CLICK is available
✅ ActionType.TYPE is available
✅ ActionType.NAVIGATE is available
✅ ActionType.SCROLL_DOWN_VIEWPORT is available

🎉 All import tests passed!

📦 Package Information:
========================================
Package Name: cesail
Version: 0.1.0
Author: CeSail Contributors
Email: ajjayawardane@gmail.com

✅ Installation test completed successfully!
💡 You can now use CeSail in your projects!
```

## Running Examples

After successful installation, you can run the example scripts:

### Basic DOM Parser Example
```bash
python basic_dom_parser.py
```

This comprehensive example demonstrates:
- 🌐 **Navigation**: Opens browser and navigates to Pinterest Ideas
- 📸 **Screenshots**: Takes multiple screenshots saved to `/tmp/`
- 🔍 **Page Analysis**: Analyzes page structure and extracts elements
- 📜 **Scroll Actions**: Performs multiple scroll operations
- 🖼️ **Base64 Screenshots**: Tests different screenshot formats
- 📊 **Element Extraction**: Shows available actions and elements

**Screenshots created**:
- `/tmp/01_after_navigation.png`
- `/tmp/02_after_analysis.png`
- `/tmp/03_after_scroll_1.png`
- `/tmp/04_after_scroll_2.png`
- `/tmp/05_after_scroll_3.png`
- `/tmp/06_final_state.png`

### Complete Automation Example
```bash
python complete_automation.py
```

This advanced example showcases:
- 🔄 **Multiple Actions**: Navigation, clicking, typing, scrolling
- 📸 **Screenshot Management**: Various screenshot options
- 🎯 **Element Finding**: Locating specific elements on pages
- 📊 **Detailed Analysis**: Comprehensive page structure analysis

## Using CeSail in Your Own Projects

### Basic Usage
```python
import asyncio
from cesail import DOMParser, Action, ActionType

async def my_automation():
    async with DOMParser(headless=False) as parser:
        # Navigate to a website
        action = Action(
            type=ActionType.NAVIGATE,
            metadata={"url": "https://example.com"}
        )
        await parser._action_executor.execute_action(action)
        
        # Analyze the page
        parsed_page = await parser.analyze_page()
        print(f"Found {len(parsed_page.important_elements.elements)} elements")
        
        # Take a screenshot
        await parser.take_screenshot("my_screenshot.png")

# Run the automation
asyncio.run(my_automation())
```

### Key Components

- **DOMParser**: Main class for web automation
- **Action**: Represents actions like navigation, clicking, typing
- **ActionType**: Enum of available action types
- **ParsedPage**: Result of page analysis with elements, forms, and actions

## Prerequisites

- **Python**: 3.9 or higher
- **Playwright**: Browser automation engine
- **Operating System**: macOS, Linux, or Windows

## Troubleshooting

### Import Errors
If you get `ModuleNotFoundError: No module named 'cesail'`:
1. Verify installation: `pip list | grep cesail`
2. Check virtual environment: `which python`
3. Try reinstalling: `pip install --upgrade cesail`

### Browser Errors
If you get browser-related errors:
1. Install Playwright browsers: `playwright install`
2. Check permissions for browser access
3. Try running with `headless=False` for debugging

### Screenshot Errors
If screenshots fail:
1. Ensure write permissions to target directory
2. Check available disk space
3. Verify file paths are valid

## Package Information

- **Package Name**: `cesail`
- **PyPI URL**: https://pypi.org/project/cesail/
- **Version**: 0.1.0
- **Author**: CeSail Contributors
- **Email**: ajjayawardane@gmail.com
- **License**: MIT
- **Documentation**: See main README.md for detailed API reference

## What's Included

The CeSail package includes:
- **DOM Parser**: JavaScript-based DOM analysis and element extraction
- **MCP Server**: FastMCP server for web automation APIs
- **Simple Agent**: AI-powered web automation agent
- **Python Bindings**: Full Python API for all functionality

## Next Steps

After successful installation:
1. Run the examples to see CeSail in action
2. Check the main README.md for detailed API documentation
3. Explore the source code structure for advanced usage
4. Join the community for support and contributions

## Support

For issues and questions:
- Check the troubleshooting section above
- Review the main project README.md
- Open an issue on the project repository
- Contact: ajjayawardane@gmail.com
