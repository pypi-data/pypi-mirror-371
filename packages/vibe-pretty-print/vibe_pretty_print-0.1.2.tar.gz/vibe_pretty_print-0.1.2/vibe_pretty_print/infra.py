"""
Infrastructure module - External services and implementations
"""
import json
import xml.etree.ElementTree as ET
import yaml
import requests
from .model import FormatRequest, FormatResult, ValidationError, OpenAIError
from .ctx import Context

class Validator:
    """Input validation logic"""
    
    def validate(self, request: FormatRequest):
        """Validate the formatting request"""
        if not request.text or not isinstance(request.text, str):
            raise ValidationError("Text must be a non-empty string")
        
        valid_formats = ["json", "xml", "yaml", "text"]
        if request.format_type not in valid_formats:
            raise ValidationError(f"format_type must be one of: {', '.join(valid_formats)}")
        
        # Format-specific validation
        getattr(self, f"_validate_{request.format_type}")(request.text)
    
    def _validate_json(self, text: str):
        try:
            json.loads(text)
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON: {e}")
    
    def _validate_xml(self, text: str):
        try:
            ET.fromstring(text)
        except ET.ParseError as e:
            raise ValidationError(f"Invalid XML: {e}")
    
    def _validate_yaml(self, text: str):
        try:
            yaml.safe_load(text)
        except yaml.YAMLError as e:
            raise ValidationError(f"Invalid YAML: {e}")
    
    def _validate_text(self, text: str):
        pass  # Text has no validation

class StandardFormatter:
    """Standard formatting without OpenAI"""
    
    def format(self, request: FormatRequest) -> FormatResult:
        """Format using standard methods"""
        method = getattr(self, f"_format_{request.format_type}")
        content = method(request.text)
        return FormatResult(content, request.format_type, "standard")
    
    def _format_json(self, text: str) -> str:
        return json.dumps(json.loads(text), indent=2, sort_keys=True)
    
    def _format_xml(self, text: str) -> str:
        # Basic XML formatting
        root = ET.fromstring(text)
        return self._prettify_xml(root)
    
    def _format_yaml(self, text: str) -> str:
        data = yaml.safe_load(text)
        return yaml.dump(data, default_flow_style=False, indent=2)
    
    def _format_text(self, text: str) -> str:
        return text.strip()
    
    def _prettify_xml(self, elem, level=0) -> str:
        indent = "  " * level
        if len(elem) == 0:
            return f"{indent}<{elem.tag}>{elem.text or ''}</{elem.tag}>"
        
        lines = [f"{indent}<{elem.tag}>"]
        for child in elem:
            lines.append(self._prettify_xml(child, level + 1))
        lines.append(f"{indent}</{elem.tag}>")
        return "\n".join(lines)

class OpenAIFormatter:
    """OpenAI-powered formatting"""
    
    def __init__(self, context: Context):
        self.context = context
    
    def format(self, request: FormatRequest, api_key: str) -> FormatResult:
        """Format using OpenAI API"""
        prompt = self._build_prompt(request.format_type)
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.context.model,
            "messages": [
                {"role": "system", "content": "You are a formatting expert. Format the given content perfectly."},
                {"role": "user", "content": f"{prompt}\n\n{request.text}"}
            ],
            "max_tokens": self.context.max_tokens,
            "temperature": self.context.temperature
        }
        
        response = requests.post(self.context.openai_url, headers=headers, json=payload)
        
        if response.status_code != 200:
            raise OpenAIError(f"OpenAI API error: {response.status_code} {response.text}")
        
        data = response.json()
        if not data.get("choices"):
            raise OpenAIError("No response choices from OpenAI")
        
        content = data["choices"][0]["message"]["content"].strip()
        return FormatResult(content, request.format_type, "openai")
    
    def _build_prompt(self, format_type: str) -> str:
        prompts = {
            "json": "Format this JSON for readability with proper indentation and sorting. Only return the formatted JSON:",
            "xml": "Format this XML with proper indentation and structure. Only return the formatted XML:",
            "yaml": "Format this YAML with consistent indentation and structure. Only return the formatted YAML:",
            "text": "Format this text for better readability with proper spacing and structure. Only return the formatted text:"
        }
        return prompts.get(format_type, prompts["text"])