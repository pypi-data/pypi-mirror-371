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
            to: str,
            from_email: str = None,
            cc: list = None,
            bcc: list = None,
            data: dict = None,
            providerId: str = None
        ):
            """
            Send an email using a KeenMail template.
            
            Args:
                templateId: The ID of the email template (e.g., "awsdemofollowupemail")
                to: Recipient email address (e.g., "renesa@optimoz.com")
                from_email: Sender email address (optional, uses default if not provided)
                cc: List of CC email addresses (optional)
                bcc: List of BCC email addresses (optional)
                data: Template variables as key-value pairs (optional)
                providerId: Email provider ID (optional, uses default if not provided)
            
            Example:
                templateId="awsdemofollowupemail",
                to="renesa@optimoz.com",
                from_email="mcp@optimoz.com",
                data={"userName": "Renesa", "companyName": "Optimoz"}
            """
            # Add auth params to the request
            auth_params = config.get_auth_params()
            
            # Get default template data from config
            template_defaults = config.get_default_template_data()
            recipient_defaults = config.get_default_recipient_data()
            
            # Build recipient object
            recipient = {
                "to": to,
                "cc": cc or [],
                "bcc": bcc or [],
                "data": data or {}
            }
            
            # Set from email - use provided, then config default, then fail
            if from_email:
                recipient["from"] = from_email
            elif recipient_defaults.get("from"):
                recipient["from"] = recipient_defaults["from"]
            else:
                raise ValueError("from_email is required. Either provide it as a parameter or set KEENMAIL_FROM_EMAIL environment variable.")
            
            # Build request data
            request_data = {
                "templateId": templateId,
                "recipients": [recipient],
                **template_defaults
            }
            
            # Use provided providerId or default
            if providerId:
                request_data["providerId"] = providerId
            elif not request_data.get("providerId"):
                raise ValueError("providerId is required. Either provide it as a parameter or set KEENMAIL_PROVIDER_ID environment variable.")
            
            # Log the request for debugging
            logger.info(f"Sending email with template: {templateId}")
            logger.info(f"Using provider: {request_data.get('providerId')}")
            logger.info(f"From: {recipient['from']} -> To: {recipient['to']}")
            if recipient['cc']:
                logger.info(f"CC: {recipient['cc']}")
            if recipient['bcc']:
                logger.info(f"BCC: {recipient['bcc']}")
            
            # Log the complete request payload for debugging
            import json
            logger.info(f"Complete request payload: {json.dumps(request_data, indent=2)}")
            
            # Make the authenticated request directly
            import httpx
            async with httpx.AsyncClient() as auth_client:
                url = f"{config.base_url}/emails/sendTemplate"
                params = auth_params
                
                try:
                    response = await auth_client.post(
                        url,
                        params=params,
                        json=request_data,
                        headers={"Content-Type": "application/json"}
                    )
                    response.raise_for_status()
                    return response.json()
                except httpx.HTTPStatusError as e:
                    # Enhanced error reporting
                    logger.error(f"HTTP {e.response.status_code} error: {e.response.text}")
                    raise ValueError(f"KeenMail API error ({e.response.status_code}): {e.response.text}")
                except Exception as e:
                    logger.error(f"Request failed: {str(e)}")
                    raise ValueError(f"Failed to send email: {str(e)}")
        
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