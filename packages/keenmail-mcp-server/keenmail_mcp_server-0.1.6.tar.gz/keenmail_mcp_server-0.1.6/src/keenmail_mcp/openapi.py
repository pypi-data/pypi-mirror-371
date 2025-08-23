"""OpenAPI specification for KeenMail API."""

OPENAPI_SPEC = {
    "openapi": "3.0.3",
    "info": {
        "title": "KeenMail API",
        "description": "API for sending template-based emails",
        "version": "1.0.0",
        "contact": {
            "email": "support@keenmail.com"
        }
    },
    "servers": [
        {
            "url": "https://app.keenmail.com/api/v1",
            "description": "Production server"
        }
    ],
    "paths": {
        "/emails/sendTemplate": {
            "post": {
                "summary": "Send template email",
                "description": "Send an email using a predefined template. Ensure recipients are properly configured as objects.",
                "operationId": "sendTemplateEmail",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/SendTemplateRequest"
                            },
                            "example": {
                                "templateId": "welcome_email",
                                "providerId": "ses_smtp_test",
                                "recipients": [
                                    {
                                        "from": "openhit@optimoz.com",
                                        "to": "openhit@optimoz.com",
                                        "cc": [
                                            "openhit@optimoz.com"
                                        ],
                                        "bcc": [
                                            "openhit@optimoz.com"
                                        ],
                                        "data": {
                                            "variableName": "string"
                                        }
                                    }
                                ]
                            }
                        }
                    }
                },
                "parameters": [
                    {
                        "name": "apiKey",
                        "in": "query",
                        "required": True,
                        "description": "API key for authentication",
                        "schema": {
                            "type": "string",
                            "example": "new1123"
                        }
                    },
                    {
                        "name": "secret",
                        "in": "query", 
                        "required": True,
                        "description": "Secret key for authentication",
                        "schema": {
                            "type": "string",
                            "example": "test"
                        }
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Email sent successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/SendTemplateResponse"
                                }
                            }
                        }
                    },
                    "400": {
                        "description": "Bad request - Invalid input data",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/ErrorResponse"
                                }
                            }
                        }
                    },
                    "401": {
                        "description": "Unauthorized - Invalid or missing apiKey/secret parameters",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/ErrorResponse"
                                }
                            }
                        }
                    },
                    "404": {
                        "description": "Template or provider not found",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/ErrorResponse"
                                }
                            }
                        }
                    },
                    "500": {
                        "description": "Internal server error",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/ErrorResponse"
                                }
                            }
                        }
                    }
                }
            }
        }
    },
    "components": {
        "schemas": {
            "SendTemplateRequest": {
                "type": "object",
                "required": [
                    "templateId",
                    "providerId",
                    "recipients"
                ],
                "properties": {
                    "templateId": {
                        "type": "string",
                        "description": "Unique identifier for the email template",
                        "example": "welcome_email"
                    },
                    "providerId": {
                        "type": "string",
                        "description": "Email provider configuration identifier",
                        "example": "ses_smtp_test"
                    },
                    "recipients": {
                        "type": "array",
                        "description": "List of email recipients with their configuration",
                        "minItems": 1,
                        "items": {
                            "$ref": "#/components/schemas/Recipient"
                        }
                    }
                }
            },
            "Recipient": {
                "type": "object",
                "required": [
                    "from",
                    "to"
                ],
                "properties": {
                    "from": {
                        "type": "string",
                        "format": "email",
                        "description": "Sender email address",
                        "example": "openhit@optimoz.com"
                    },
                    "to": {
                        "type": "string",
                        "format": "email",
                        "description": "Primary recipient email address",
                        "example": "openhit@optimoz.com"
                    },
                    "cc": {
                        "type": "array",
                        "description": "Carbon copy recipients",
                        "items": {
                            "type": "string",
                            "format": "email"
                        },
                        "example": [
                            "openhit@optimoz.com"
                        ]
                    },
                    "bcc": {
                        "type": "array",
                        "description": "Blind carbon copy recipients",
                        "items": {
                            "type": "string",
                            "format": "email"
                        },
                        "example": [
                            "openhit@optimoz.com"
                        ]
                    },
                    "data": {
                        "type": "object",
                        "description": "Dynamic data to populate template variables",
                        "additionalProperties": True,
                        "example": {
                            "variableName": "string",
                            "userName": "John Doe",
                            "companyName": "Example Corp"
                        }
                    }
                }
            },
            "SendTemplateResponse": {
                "type": "object",
                "properties": {
                    "success": {
                        "type": "boolean",
                        "description": "Indicates if the email was sent successfully",
                        "example": True
                    },
                    "messageId": {
                        "type": "string",
                        "description": "Unique identifier for the sent message",
                        "example": "msg_1234567890abcdef"
                    },
                    "status": {
                        "type": "string",
                        "description": "Status of the email sending operation",
                        "example": "sent"
                    },
                    "timestamp": {
                        "type": "string",
                        "format": "date-time",
                        "description": "When the email was processed",
                        "example": "2025-08-06T10:30:00Z"
                    }
                }
            },
            "ErrorResponse": {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "string",
                        "description": "Error message describing what went wrong",
                        "example": "Template not found"
                    },
                    "code": {
                        "type": "string",
                        "description": "Error code for programmatic handling",
                        "example": "TEMPLATE_NOT_FOUND"
                    },
                    "timestamp": {
                        "type": "string",
                        "format": "date-time",
                        "description": "When the error occurred",
                        "example": "2025-08-06T10:30:00Z"
                    }
                }
            }
        },
        "securitySchemes": {
            "QueryParamAuth": {
                "type": "apiKey",
                "in": "query",
                "name": "apiKey",
                "description": "API key passed as query parameter. Also requires 'secret' query parameter."
            }
        }
    },
    "security": []
}