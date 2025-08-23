"""KeenMail MCP Server - MCP server for KeenMail API integration."""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .server import create_server
from .config import KeenMailConfig

__all__ = ["create_server", "KeenMailConfig", "__version__"]