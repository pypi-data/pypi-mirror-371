"""Tests for main entry point."""

import pytest
from unittest.mock import patch
from keenmail_mcp.__main__ import main


class TestMain:
    """Test cases for main entry point."""
    
    @patch('keenmail_mcp.__main__.run_server')
    def test_main_success(self, mock_run_server):
        """Test successful main execution."""
        main()
        mock_run_server.assert_called_once()
    
    @patch('keenmail_mcp.__main__.run_server')
    def test_main_exception(self, mock_run_server):
        """Test main with exception."""
        mock_run_server.side_effect = Exception("Server error")
        
        with pytest.raises(SystemExit):
            main()