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
    
    def get_auth_params(self) -> dict:
        """Get authentication parameters for API requests."""
        return {
            "apiKey": self.api_key,
            "secret": self.secret
        }