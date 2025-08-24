"""
Context module - Application configuration and context
"""
import os

class Context:
    """Application context holding configuration"""
    def __init__(self):
        self.env_api_key = os.getenv("VIBE_PP_API_KEY", "")
        self.openai_url = "https://api.openai.com/v1/chat/completions"
        self.model = "gpt-3.5-turbo"
        self.max_tokens = 2000
        self.temperature = 0.1