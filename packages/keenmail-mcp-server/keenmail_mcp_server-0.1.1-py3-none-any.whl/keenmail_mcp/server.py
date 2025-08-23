"""KeenMail MCP Server implementation."""

import httpx
import logging
import sys
from fastmcp import FastMCP
from .config import KeenMailConfig
from .openapi import OPENAPI_SPEC


def setup_logging():
    """Configure logging to stderr for MCP compatibility."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stderr
    )
    return logging.getLogger(__name__)


def create_server() -> FastMCP:
    """Create and configure the KeenMail MCP server."""
    logger = setup_logging()
    
    try:
        # Load and validate configuration
        config = KeenMailConfig()
        logger.info("Configuration loaded successfully")
    except Exception as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    
    # Create HTTP client with authentication
    client = httpx.AsyncClient(
        base_url=config.base_url,
        headers={
            "Content-Type": "application/json"
        }
    )
    
    # Create MCP server from OpenAPI spec
    try:
        mcp = FastMCP.from_openapi(
            openapi_spec=OPENAPI_SPEC,
            client=client,
            name="KeenMail Server"
        )
        
        # Get the generated tool and wrap it with authentication
        original_tool = None
        for tool_name, tool_func in mcp._tools.items():
            if tool_name == "sendTemplateEmail":
                original_tool = tool_func
                break
        
        if original_tool:
            async def sendTemplateEmail_with_auth(**kwargs):
                """Wrapper that adds authentication to the sendTemplateEmail call."""
                # Add auth params to the request
                auth_params = config.get_auth_params()
                
                # The original function expects these as part of the request
                # We need to inject them into the httpx call
                import httpx
                
                # Make the authenticated request directly
                async with httpx.AsyncClient() as auth_client:
                    url = f"{config.base_url}/emails/sendTemplate"
                    params = auth_params
                    
                    response = await auth_client.post(
                        url,
                        params=params,
                        json=kwargs,
                        headers={"Content-Type": "application/json"}
                    )
                    response.raise_for_status()
                    return response.json()
            
            # Replace the tool with our authenticated version
            mcp._tools["sendTemplateEmail"] = sendTemplateEmail_with_auth
        
        logger.info("KeenMail MCP Server created successfully")
        return mcp
    except Exception as e:
        logger.error(f"Failed to create MCP server: {e}")
        sys.exit(1)


def run_server():
    """Run the KeenMail MCP server with STDIO transport."""
    logger = setup_logging()
    logger.info("Starting KeenMail MCP Server with STDIO transport...")
    
    server = create_server()
    
    try:
        # Run with STDIO transport for UVX compatibility
        server.run(transport="stdio")
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)