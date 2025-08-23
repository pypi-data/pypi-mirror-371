"""Tests for configuration management."""

import os
import pytest
from unittest.mock import patch
from keenmail_mcp.config import KeenMailConfig


class TestKeenMailConfig:
    """Test cases for KeenMailConfig."""
    
    def test_config_with_env_vars(self):
        """Test configuration loading with environment variables."""
        with patch.dict(os.environ, {
            'KEENMAIL_API_KEY': 'test_api_key',
            'KEENMAIL_SECRET': 'test_secret',
            'KEENMAIL_BASE_URL': 'https://test.keenmail.com/api/v1',
            'KEENMAIL_PROVIDER_ID': 'test_provider',
            'KEENMAIL_FROM_EMAIL': 'test@example.com'
        }):
            config = KeenMailConfig()
            assert config.api_key == 'test_api_key'
            assert config.secret == 'test_secret'
            assert config.base_url == 'https://test.keenmail.com/api/v1'
            assert config.provider_id == 'test_provider'
            assert config.from_email == 'test@example.com'
    
    def test_config_with_defaults(self):
        """Test configuration with default values."""
        with patch.dict(os.environ, {
            'KEENMAIL_API_KEY': 'test_api_key',
            'KEENMAIL_SECRET': 'test_secret',
            'KEENMAIL_PROVIDER_ID': 'test_provider',
            'KEENMAIL_FROM_EMAIL': 'test@example.com'
        }):
            config = KeenMailConfig()
            assert config.base_url == 'https://app.keenmail.com/api/v1'
    
    def test_missing_api_key_raises_error(self):
        """Test that missing API key raises ValueError."""
        with patch.dict(os.environ, {'KEENMAIL_SECRET': 'test_secret'}, clear=True):
            with pytest.raises(ValueError, match="KEENMAIL_API_KEY environment variable is required"):
                KeenMailConfig()
    
    def test_missing_secret_raises_error(self):
        """Test that missing secret raises ValueError."""
        with patch.dict(os.environ, {'KEENMAIL_API_KEY': 'test_key'}, clear=True):
            with pytest.raises(ValueError, match="KEENMAIL_SECRET environment variable is required"):
                KeenMailConfig()
    
    def test_missing_provider_id_raises_error(self):
        """Test that missing provider ID raises ValueError."""
        with patch.dict(os.environ, {
            'KEENMAIL_API_KEY': 'test_key',
            'KEENMAIL_SECRET': 'test_secret',
            'KEENMAIL_FROM_EMAIL': 'test@example.com'
        }, clear=True):
            with pytest.raises(ValueError, match="KEENMAIL_PROVIDER_ID environment variable is required"):
                KeenMailConfig()
    
    def test_missing_from_email_raises_error(self):
        """Test that missing from email raises ValueError."""
        with patch.dict(os.environ, {
            'KEENMAIL_API_KEY': 'test_key',
            'KEENMAIL_SECRET': 'test_secret',
            'KEENMAIL_PROVIDER_ID': 'test_provider'
        }, clear=True):
            with pytest.raises(ValueError, match="KEENMAIL_FROM_EMAIL environment variable is required"):
                KeenMailConfig()
    
    def test_invalid_base_url_raises_error(self):
        """Test that invalid base URL raises ValueError."""
        with patch.dict(os.environ, {
            'KEENMAIL_API_KEY': 'test_key',
            'KEENMAIL_SECRET': 'test_secret',
            'KEENMAIL_PROVIDER_ID': 'test_provider',
            'KEENMAIL_FROM_EMAIL': 'test@example.com',
            'KEENMAIL_BASE_URL': 'invalid_url'
        }):
            with pytest.raises(ValueError, match="Base URL must start with http:// or https://"):
                KeenMailConfig()
    
    def test_get_auth_params(self):
        """Test auth parameters generation."""
        with patch.dict(os.environ, {
            'KEENMAIL_API_KEY': 'test_key',
            'KEENMAIL_SECRET': 'test_secret',
            'KEENMAIL_PROVIDER_ID': 'test_provider',
            'KEENMAIL_FROM_EMAIL': 'test@example.com'
        }):
            config = KeenMailConfig()
            auth_params = config.get_auth_params()
            
            assert auth_params == {
                'apiKey': 'test_key',
                'secret': 'test_secret'
            }
    
    def test_base_url_trailing_slash_removed(self):
        """Test that trailing slash is removed from base URL."""
        with patch.dict(os.environ, {
            'KEENMAIL_API_KEY': 'test_key',
            'KEENMAIL_SECRET': 'test_secret',
            'KEENMAIL_PROVIDER_ID': 'test_provider',
            'KEENMAIL_FROM_EMAIL': 'test@example.com',
            'KEENMAIL_BASE_URL': 'https://test.keenmail.com/api/v1/'
        }):
            config = KeenMailConfig()
            assert config.base_url == 'https://test.keenmail.com/api/v1'
    
    def test_invalid_from_email_raises_error(self):
        """Test that invalid from email raises ValueError."""
        with patch.dict(os.environ, {
            'KEENMAIL_API_KEY': 'test_key',
            'KEENMAIL_SECRET': 'test_secret',
            'KEENMAIL_PROVIDER_ID': 'test_provider',
            'KEENMAIL_FROM_EMAIL': 'invalid_email'
        }):
            with pytest.raises(ValueError, match="From email must be a valid email address"):
                KeenMailConfig()
    
    def test_get_default_recipient_data(self):
        """Test default recipient data generation."""
        with patch.dict(os.environ, {
            'KEENMAIL_API_KEY': 'test_key',
            'KEENMAIL_SECRET': 'test_secret',
            'KEENMAIL_PROVIDER_ID': 'test_provider',
            'KEENMAIL_FROM_EMAIL': 'test@example.com'
        }):
            config = KeenMailConfig()
            recipient_data = config.get_default_recipient_data()
            
            assert recipient_data == {'from': 'test@example.com'}
    
    def test_get_default_template_data(self):
        """Test default template data generation."""
        with patch.dict(os.environ, {
            'KEENMAIL_API_KEY': 'test_key',
            'KEENMAIL_SECRET': 'test_secret',
            'KEENMAIL_PROVIDER_ID': 'amazonaws',
            'KEENMAIL_FROM_EMAIL': 'test@example.com'
        }):
            config = KeenMailConfig()
            template_data = config.get_default_template_data()
            
            assert template_data == {'providerId': 'amazonaws'}
    
    def test_default_data_with_required_fields(self):
        """Test that defaults include required values."""
        with patch.dict(os.environ, {
            'KEENMAIL_API_KEY': 'test_key',
            'KEENMAIL_SECRET': 'test_secret',
            'KEENMAIL_PROVIDER_ID': 'test_provider',
            'KEENMAIL_FROM_EMAIL': 'test@example.com'
        }):
            config = KeenMailConfig()
            
            assert config.get_default_recipient_data() == {'from': 'test@example.com'}
            assert config.get_default_template_data() == {'providerId': 'test_provider'}