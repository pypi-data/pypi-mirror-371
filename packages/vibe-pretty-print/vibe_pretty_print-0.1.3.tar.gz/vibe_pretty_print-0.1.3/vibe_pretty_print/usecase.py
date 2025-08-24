"""
Use case module - Core business logic
"""
from .model import FormatRequest, FormatResult, ValidationError, OpenAIError
from .infra import Validator, StandardFormatter, OpenAIFormatter

class FormatUseCase:
    """Core business logic for formatting"""
    
    def __init__(self, context):
        self.context = context
        self.validator = Validator()
        self.formatter = StandardFormatter()
        self.openai_formatter = OpenAIFormatter(context)
    
    def execute(self, request: FormatRequest) -> FormatResult:
        """Execute formatting use case"""
        # Validate input
        self.validator.validate(request)
        
        # Get API key
        api_key = request.api_key or self.context.env_api_key
        
        # Try OpenAI if API key available
        if api_key:
            try:
                return self.openai_formatter.format(request, api_key)
            except OpenAIError as e:
                # Fallback to standard formatting
                print(f"⚠️  OpenAI failed, using fallback: {e}")
        
        # Standard formatting
        return self.formatter.format(request)