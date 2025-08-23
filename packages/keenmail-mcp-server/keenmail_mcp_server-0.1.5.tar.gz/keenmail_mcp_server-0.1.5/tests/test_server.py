"""Tests for server implementation."""

import os
import pytest
from unittest.mock import patch, MagicMock
from keenmail_mcp.server import create_server, setup_logging


class TestServer:
    """Test cases for server functionality."""
    
    @patch('keenmail_mcp.server.KeenMailConfig')
    @patch('keenmail_mcp.server.FastMCP')
    @patch('keenmail_mcp.server.httpx.AsyncClient')
    def test_create_server_success(self, mock_client, mock_fastmcp, mock_config):
        """Test successful server creation."""
        # Mock configuration
        mock_config_instance = MagicMock()
        mock_config_instance.base_url = 'https://test.keenmail.com/api/v1'
        mock_config_instance.get_auth_params.return_value = {'apiKey': 'test', 'secret': 'test'}
        mock_config.return_value = mock_config_instance
        
        # Mock FastMCP
        mock_server = MagicMock()
        mock_fastmcp.from_openapi.return_value = mock_server
        
        # Call function
        result = create_server()
        
        # Assertions
        mock_config.assert_called_once()
        mock_client.assert_called_once()
        mock_fastmcp.from_openapi.assert_called_once()
        assert result == mock_server
    
    @patch('keenmail_mcp.server.KeenMailConfig')
    def test_create_server_config_error(self, mock_config):
        """Test server creation with configuration error."""
        mock_config.side_effect = ValueError("Config error")
        
        with pytest.raises(SystemExit):
            create_server()
    
    @patch('keenmail_mcp.server.KeenMailConfig')
    @patch('keenmail_mcp.server.FastMCP')
    @patch('keenmail_mcp.server.httpx.AsyncClient')
    def test_create_server_fastmcp_error(self, mock_client, mock_fastmcp, mock_config):
        """Test server creation with FastMCP error."""
        # Mock configuration
        mock_config_instance = MagicMock()
        mock_config.return_value = mock_config_instance
        
        # Mock FastMCP to raise error
        mock_fastmcp.from_openapi.side_effect = Exception("FastMCP error")
        
        with pytest.raises(SystemExit):
            create_server()
    
    def test_setup_logging(self):
        """Test logging setup."""
        logger = setup_logging()
        
        assert logger is not None
        assert logger.name == 'keenmail_mcp.server'