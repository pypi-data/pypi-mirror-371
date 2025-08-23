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
        
        # Override the sendTemplateEmail tool with our authenticated version
        @mcp.tool()
        async def sendTemplateEmail(
            templateId: str,
            recipients: list,
            providerId: str = None
        ):
            """Send an email using a KeenMail template with authentication."""
            # Add auth params to the request
            auth_params = config.get_auth_params()
            
            # Get default template data from config
            template_defaults = config.get_default_template_data()
            recipient_defaults = config.get_default_recipient_data()
            
            # Build request data
            request_data = {
                "templateId": templateId,
                "recipients": recipients,
                **template_defaults
            }
            
            # Use provided providerId or default
            if providerId:
                request_data["providerId"] = providerId
            
            # Apply recipient defaults to each recipient if not already set
            for recipient in request_data["recipients"]:
                for key, value in recipient_defaults.items():
                    if key not in recipient or not recipient[key]:
                        recipient[key] = value
            
            # Log the request for debugging
            logger.info(f"Sending email with template: {templateId}")
            logger.info(f"Using provider: {request_data.get('providerId', 'default')}")
            if config.from_email:
                logger.info(f"Default from email: {config.from_email}")
            
            # Make the authenticated request directly
            import httpx
            async with httpx.AsyncClient() as auth_client:
                url = f"{config.base_url}/emails/sendTemplate"
                params = auth_params
                
                response = await auth_client.post(
                    url,
                    params=params,
                    json=request_data,
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                return response.json()
        
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