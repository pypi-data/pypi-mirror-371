"""
Runner module - Main entry point and interface
"""
from typing import Optional
from .ctx import Context
from .model import FormatRequest
from .usecase import FormatUseCase

class VibePPrintRunner:
    """Main runner class"""
    
    def __init__(self):
        self.context = Context()
        self.use_case = FormatUseCase(self.context)
    
    def run(self, text: str, format_type: str = "text", api_key: Optional[str] = None) -> str:
        """Main entry point"""
        request = FormatRequest(text, format_type, api_key)
        result = self.use_case.execute(request)
        return result.content

def vibe_pprint(text: str, format_type: str = "text", api_key: Optional[str] = None) -> str:
    """
    Format text using AI-enhanced or standard formatting
    
    Args:
        text: Content to format (JSON, XML, YAML, or plain text)
        format_type: "json", "xml", "yaml", or "text"
        api_key: OpenAI API key (optional, uses VIBE_PP_API_KEY env var)
    
    Returns:
        Formatted text string
    
    Raises:
        ValidationError: If input validation fails
        OpenAIError: If OpenAI API fails
    """
    runner = VibePPrintRunner()
    return runner.run(text, format_type, api_key)