"""KeenMail MCP Server - MCP server for KeenMail API integration."""

__version__ = "0.1.3"
__author__ = "Renesa Patel"
__email__ = "renesa@optimoz.com"

from .server import create_server
from .config import KeenMailConfig

__all__ = ["create_server", "KeenMailConfig", "__version__"]