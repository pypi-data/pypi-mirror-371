#!/usr/bin/env python3
"""
Basic DOM Parser Example

This example demonstrates basic usage of the CeSail DOM Parser:
- Navigating to a webpage
- Analyzing the page structure
- Extracting interactive elements
- Taking screenshots
- Executing scroll actions
"""

import asyncio
import json
import os
from cesail import DOMParser, Action, ActionType

# Enable Playwright debug logging
os.environ["DEBUG"] = "pw:api"

async def basic_dom_parser_example():
    """Basic example showing DOM parsing and interaction capabilities."""
    print("🚀 Basic DOM Parser Example")
    print("=" * 50)
    
    async with DOMParser(headless=False) as parser:
        print("✅ Browser started successfully")
        
        # Navigate to Pinterest Ideas page
        print("\n🌐 Navigating to Pinterest Ideas...")
        action = Action(
            type=ActionType.NAVIGATE,
            metadata={"url": "https://www.pinterest.com/ideas/"}
        )
        await parser._action_executor.execute_action(action)
        print("✅ Navigation completed")
        
        # Take screenshot after navigation
        print("\n📸 Taking screenshot after navigation...")
        screenshot_path = "/tmp/01_after_navigation.png"
        await parser.take_screenshot(screenshot_path)
        print(f"✅ Screenshot saved: {screenshot_path}")
        print(f"   🔗 View: file://{screenshot_path}")

        # Analyze the page
        print("\n🔍 Analyzing page structure...")
        parsed_page = await parser.analyze_page()
        print("✅ Page analysis completed")
        
        # Take screenshot after analysis
        screenshot_path = "/tmp/02_after_analysis.png"
        await parser.take_screenshot(screenshot_path)
        print(f"✅ Screenshot saved: {screenshot_path}")
        print(f"   🔗 View: file://{screenshot_path}")
        
        # Print page analysis results
        print("\n📊 Page Analysis Results:")
        print(f"   URL: {parsed_page.metadata.url}")
        print(f"   Number of elements: {len(parsed_page.important_elements.elements)}")
        print(f"   Number of forms: {len(parsed_page.forms.forms)}")
        print(f"   Number of actions: {len(parsed_page.actions.actions)}")

        # Show available actions
        print("\n🎯 Available actions:")
        actions_json = parsed_page.to_json()["actions"]
        print(json.dumps(actions_json[:3], indent=2))  # Show first 3 actions
        if len(actions_json) > 3:
            print(f"   ... and {len(actions_json) - 3} more actions")

        # Test selector functionality
        print("\n🔧 Testing selector functionality:")
        try:
            selector = await parser.page_analyzer.get_selector_by_id("1")
            print(f"   Selector for element 1: {selector}")
        except Exception as e:
            print(f"   Could not get selector: {e}")

        # Perform multiple scroll actions
        print("\n📜 Performing scroll actions...")
        for i in range(3):  # Reduced from 7 to 3 for demo
            action = Action(
                type="scroll_down_viewport"
            )
            
            print(f"   Executing scroll action {i+1}/3...")
            result = await parser.execute_action(action, wait_for_idle=True)
            
            # Take screenshot after scroll
            screenshot_path = f"/tmp/{i+3:02d}_after_scroll_{i+1}.png"
            await parser.take_screenshot(screenshot_path)
            print(f"   ✅ Screenshot saved: {screenshot_path}")
            print(f"   🔗 View: file://{screenshot_path}")

            # Re-analyze page after scroll
            parsed_page = await parser.analyze_page()
            print(f"   📊 Elements after scroll {i+1}: {len(parsed_page.important_elements.elements)}")

        # Test base64 screenshot
        print("\n🖼️  Testing base64 screenshot...")
        try:
            screenshot = await parser.take_screenshot(
                filepath="/tmp/05_screenshot_base64.png",
                quality=None,
                format="png",
                full_page=False,
                return_base64=True
            )
            print(f"   ✅ Base64 screenshot length: {len(screenshot) if screenshot else 0}")
            print(f"   🔗 View: file:///tmp/05_screenshot_base64.png")
        except Exception as e:
            print(f"   ❌ Base64 screenshot failed: {e}")

        # Take final screenshot
        screenshot_path = "/tmp/06_final_state.png"
        await parser.take_screenshot(screenshot_path)
        print(f"✅ Final screenshot saved: {screenshot_path}")
        print(f"🔗 View: file://{screenshot_path}")
        
        print("\n🎉 Basic DOM parser example completed successfully!")
        print("\n📁 Screenshots saved to /tmp:")
        print("   - /tmp/01_after_navigation.png")
        print("   - /tmp/02_after_analysis.png")
        print("   - /tmp/03_after_scroll_1.png")
        print("   - /tmp/04_after_scroll_2.png")
        print("   - /tmp/05_after_scroll_3.png")
        print("   - /tmp/06_final_state.png")
        print("\n🔗 Quick links to view screenshots:")
        print("   file:///tmp/01_after_navigation.png")
        print("   file:///tmp/02_after_analysis.png")
        print("   file:///tmp/03_after_scroll_1.png")
        print("   file:///tmp/04_after_scroll_2.png")
        print("   file:///tmp/05_after_scroll_3.png")
        print("   file:///tmp/06_final_state.png")

if __name__ == "__main__":
    asyncio.run(basic_dom_parser_example())
