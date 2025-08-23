"""Entry point for KeenMail MCP Server - UVX compatible."""

import sys
from .server import run_server


def main():
    """Main entry point for the KeenMail MCP Server."""
    try:
        run_server()
    except Exception as e:
        print(f"Error starting KeenMail MCP Server: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()