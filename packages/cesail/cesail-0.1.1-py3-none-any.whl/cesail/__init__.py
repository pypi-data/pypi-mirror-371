"""
CeSail - A comprehensive web automation and DOM parsing platform with AI-powered agents.

This package provides:
- DOM Parser: JavaScript-based DOM analysis and element extraction
- MCP Server: FastMCP server for web automation APIs
- Simple Agent: AI-powered web automation agent
"""

__version__ = "0.1.1"
__author__ = "CeSail Contributors"
__email__ = "ajjayawardane@gmail.com"

# Import main components for easy access
try:
    from dom_parser.src.dom_parser import DOMParser
    from dom_parser.src.py.types import Action, ActionType
except ImportError:
    # Handle case where dom_parser is not available
    pass

__all__ = [
    "DOMParser",
    "Action", 
    "ActionType",
    "__version__",
    "__author__",
    "__email__"
]
