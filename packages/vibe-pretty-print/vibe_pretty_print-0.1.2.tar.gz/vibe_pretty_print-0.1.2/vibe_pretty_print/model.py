"""
Model module - Data models and domain entities
"""
from typing import Optional

class ValidationError(Exception):
    """Raised when input validation fails"""
    pass

class OpenAIError(Exception):
    """Raised when OpenAI API fails"""
    pass

class FormatResult:
    """Model for formatting results"""
    def __init__(self, content: str, format_type: str, source: str = "standard"):
        self.content = content
        self.format_type = format_type
        self.source = source  # "standard" or "openai"

class FormatRequest:
    """Model for formatting requests"""
    def __init__(self, text: str, format_type: str, api_key: Optional[str] = None):
        self.text = text
        self.format_type = format_type
        self.api_key = api_key