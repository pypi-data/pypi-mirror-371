"""Configuration management for KeenMail MCP Server."""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator


class KeenMailConfig(BaseSettings):
    """Configuration for KeenMail MCP Server."""
    
    api_key: Optional[str] = None
    secret: Optional[str] = None
    base_url: str = "https://app.keenmail.com/api/v1"
    provider_id: Optional[str] = None
    from_email: Optional[str] = None
    
    model_config = {"env_prefix": "KEENMAIL_", "case_sensitive": False}
        
    @field_validator("api_key")
    @classmethod
    def validate_api_key(cls, v):
        if not v:
            raise ValueError(
                "KEENMAIL_API_KEY environment variable is required. "
                "Please set your KeenMail API key."
            )
        return v
    
    @field_validator("secret") 
    @classmethod
    def validate_secret(cls, v):
        if not v:
            raise ValueError(
                "KEENMAIL_SECRET environment variable is required. "
                "Please set your KeenMail secret key."
            )
        return v
    
    @field_validator("base_url")
    @classmethod
    def validate_base_url(cls, v):
        if not v.startswith(("http://", "https://")):
            raise ValueError("Base URL must start with http:// or https://")
        return v.rstrip("/")
    
    
    @field_validator("provider_id")
    @classmethod
    def validate_provider_id(cls, v):
        if not v:
            raise ValueError(
                "KEENMAIL_PROVIDER_ID environment variable is required. "
                "Please set your email provider ID (e.g., 'amazonaws', 'ses_smtp_test')."
            )
        return v
    
    @field_validator("from_email")
    @classmethod
    def validate_from_email(cls, v):
        if not v:
            raise ValueError(
                "KEENMAIL_FROM_EMAIL environment variable is required. "
                "Please set your default sender email address."
            )
        if "@" not in v:
            raise ValueError("From email must be a valid email address")
        return v
    
    def get_auth_params(self) -> dict:
        """Get authentication parameters for API requests."""
        return {
            "apiKey": self.api_key,
            "secret": self.secret
        }
    
    def get_default_recipient_data(self) -> dict:
        """Get default recipient data from configuration."""
        data = {}
        if self.from_email:
            data["from"] = self.from_email
        return data
    
    def get_default_template_data(self) -> dict:
        """Get default template data from configuration."""
        data = {}
        if self.provider_id:
            data["providerId"] = self.provider_id
        return data