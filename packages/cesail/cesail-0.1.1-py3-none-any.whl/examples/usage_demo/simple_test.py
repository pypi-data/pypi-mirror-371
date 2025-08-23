#!/usr/bin/env python3
print("Testing CeSail package installation...")

try:
    from dom_parser.src.dom_parser import DOMParser
    print("✅ DOMParser imported successfully")
    
    from dom_parser.src.py.types import Action, ActionType
    print("✅ Action and ActionType imported successfully")
    
    import mcp
    print("✅ MCP package imported successfully")
    
    import simple_agent
    print("✅ Simple Agent package imported successfully")
    
    print("🎉 All imports successful!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
