"""
Core functionality for vibe-pretty-print library.
"""

import json
import yaml
import xml.etree.ElementTree as ET
import os
from typing import Any, Dict, Optional
import requests
import colorama
from colorama import Fore, Back, Style

# Initialize colorama for cross-platform color support
colorama.init()


class VibePrettyPrintError(Exception):
    """Base exception for vibe-pretty-print errors."""
    pass


class ValidationError(VibePrettyPrintError):
    """Raised when input validation fails."""
    pass


class OpenAIError(VibePrettyPrintError):
    """Raised when OpenAI API calls fail."""
    pass


def _call_openai_api(api_key: str, text: str, format_type: str) -> str:
    """
    Call OpenAI API for formatting assistance.
    
    Args:
        api_key: OpenAI API key
        text: Text to format
        format_type: Type of format (json, xml, yaml, text)
    
    Returns:
        Formatted text from OpenAI
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""
    Please help format the following {format_type} content to be more readable and well-structured.
    
    Content:
    {text}
    
    Please return only the formatted content without any additional explanation.
    """
    
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 2000,
        "temperature": 0.3
    }
    
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()
    
    except requests.exceptions.RequestException as e:
        raise OpenAIError(f"OpenAI API call failed: {str(e)}")
    except (KeyError, IndexError) as e:
        raise OpenAIError("Invalid OpenAI API response format")


def _format_json(data: str, use_openai: bool = False, api_key: Optional[str] = None) -> str:
    """
    Format JSON data with validation and pretty printing.
    
    Args:
        data: JSON string to format
        use_openai: Whether to use OpenAI for enhanced formatting
        api_key: OpenAI API key (required if use_openai=True)
    
    Returns:
        Pretty-printed JSON string
    """
    try:
        # Try to parse and validate JSON
        parsed = json.loads(data)
        
        # Standard pretty printing
        formatted = json.dumps(parsed, indent=2, ensure_ascii=False, sort_keys=True)
        
        # If OpenAI enhancement is requested, use it
        if use_openai and api_key:
            try:
                enhanced = _call_openai_api(api_key, formatted, "json")
                return enhanced
            except OpenAIError:
                # Fall back to standard formatting if OpenAI fails
                pass
        
        return formatted
    
    except json.JSONDecodeError as e:
        raise ValidationError(f"Invalid JSON: {str(e)}")


def _format_yaml(data: str, use_openai: bool = False, api_key: Optional[str] = None) -> str:
    """
    Format YAML data with validation and pretty printing.
    
    Args:
        data: YAML string to format
        use_openai: Whether to use OpenAI for enhanced formatting
        api_key: OpenAI API key (required if use_openai=True)
    
    Returns:
        Pretty-printed YAML string
    """
    try:
        # Try to parse and validate YAML
        parsed = yaml.safe_load(data)
        
        # Standard pretty printing
        formatted = yaml.dump(parsed, default_flow_style=False, allow_unicode=True, indent=2)
        
        # If OpenAI enhancement is requested, use it
        if use_openai and api_key:
            try:
                enhanced = _call_openai_api(api_key, formatted, "yaml")
                return enhanced
            except OpenAIError:
                # Fall back to standard formatting if OpenAI fails
                pass
        
        return formatted
    
    except yaml.YAMLError as e:
        raise ValidationError(f"Invalid YAML: {str(e)}")


def _format_xml(data: str, use_openai: bool = False, api_key: Optional[str] = None) -> str:
    """
    Format XML data with validation and pretty printing.
    
    Args:
        data: XML string to format
        use_openai: Whether to use OpenAI for enhanced formatting
        api_key: OpenAI API key (required if use_openai=True)
    
    Returns:
        Pretty-printed XML string
    """
    try:
        # Try to parse and validate XML
        from xml.dom import minidom
        parsed = ET.fromstring(data)
        
        # Convert to string and pretty print
        xml_str = ET.tostring(parsed, encoding='unicode')
        dom = minidom.parseString(xml_str)
        formatted = dom.toprettyxml(indent="  ")
        
        # Remove extra newlines
        formatted = '\n'.join(line for line in formatted.split('\n') if line.strip())
        
        # If OpenAI enhancement is requested, use it
        if use_openai and api_key:
            try:
                enhanced = _call_openai_api(api_key, formatted, "xml")
                return enhanced
            except OpenAIError:
                # Fall back to standard formatting if OpenAI fails
                pass
        
        return formatted
    
    except ET.ParseError as e:
        raise ValidationError(f"Invalid XML: {str(e)}")


def _format_text(data: str, use_openai: bool = False, api_key: Optional[str] = None) -> str:
    """
    Format plain text with color highlighting.
    
    Args:
        data: Text to format
        use_openai: Whether to use OpenAI for enhanced formatting
        api_key: OpenAI API key (required if use_openai=True)
    
    Returns:
        Color-formatted text string
    """
    if use_openai and api_key:
        try:
            enhanced = _call_openai_api(api_key, data, "text")
            return enhanced
        except OpenAIError:
            # Fall back to standard formatting if OpenAI fails
            pass
    
    # Simple color formatting - highlight different elements
    lines = data.split('\n')
    formatted_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Color code comments (lines starting with #)
        if line.startswith('#'):
            formatted_lines.append(f"{Fore.GREEN}{line}{Style.RESET_ALL}")
        # Color code URLs
        elif 'http' in line.lower():
            parts = line.split()
            colored_parts = []
            for part in parts:
                if part.startswith('http'):
                    colored_parts.append(f"{Fore.BLUE}{part}{Style.RESET_ALL}")
                else:
                    colored_parts.append(part)
            formatted_lines.append(' '.join(colored_parts))
        # Color code numbers
        elif any(c.isdigit() for c in line):
            import re
            colored_line = re.sub(r'(\d+)', f"{Fore.YELLOW}\\1{Style.RESET_ALL}", line)
            formatted_lines.append(colored_line)
        else:
            formatted_lines.append(line)
    
    return '\n'.join(formatted_lines)


def _get_api_key(api_key: Optional[str] = None) -> str:
    """
    Get API key from multiple sources in order of preference:
    1. Function parameter
    2. Environment variable VIBE_PP_API_KEY
    3. Hardcoded fallback
    
    Args:
        api_key: Optional API key from function parameter
        
    Returns:
        str: API key to use
        
    Raises:
        ValueError: If no API key is found
    """
    # 1. Check function parameter first
    if api_key and isinstance(api_key, str) and api_key.strip():
        return api_key.strip()
    
    # 2. Check environment variable
    env_key = os.getenv("VIBE_PP_API_KEY")
    if env_key and env_key.strip():
        return env_key.strip()
    
    # 3. Check hardcoded fallback (for testing purposes)
    hardcoded_key = ""  # Leave empty - users should provide their own key
    if hardcoded_key and hardcoded_key.strip():
        return hardcoded_key.strip()
    
    raise ValueError(
        "No API key found. Please provide an API key via:\n"
        "1. Function parameter: vibe_pprint('your-key', text, 'json')\n"
        "2. Environment variable: export VIBE_PP_API_KEY='your-key'\n"
        "3. Update the hardcoded key in the source code"
    )


def vibe_pprint(api_key: Optional[str] = None, text: str = "", format_type: str = "text") -> str:
    """
    Main interface for vibe-pretty-print library.
    
    Args:
        api_key: OpenAI API key for enhanced formatting
        text: Text content to format (JSON, XML, YAML, or plain text)
        format_type: Type of content - "json", "xml", "yaml", or "text"
    
    Returns:
        Pretty-printed/formatted string
    
    Raises:
        ValidationError: If the input format is invalid
        OpenAIError: If OpenAI API calls fail
        ValueError: If format_type is invalid
    
    Examples:
        >>> from vibe_pprint import vibe_pprint
        >>> vibe_pprint("your-api-key", '{"name": "John", "age": 30}', "json")
        '{
  "age": 30,
  "name": "John"
}'
    """
    format_type = format_type.lower().strip()
    
    if format_type not in ["json", "xml", "yaml", "text"]:
        raise ValueError("format_type must be one of: json, xml, yaml, text")
    
    # Get API key using the new resolution function
    resolved_api_key = _get_api_key(api_key)
    
    if not text or not isinstance(text, str):
        raise ValueError("text must be a non-empty string")
    
    formatters = {
        "json": _format_json,
        "xml": _format_xml,
        "yaml": _format_yaml,
        "text": _format_text
    }
    
    formatter = formatters[format_type]
    
    try:
        # Always attempt to use OpenAI for enhanced formatting
        return formatter(text, use_openai=True, api_key=resolved_api_key)
    except (ValidationError, OpenAIError):
        # Fall back to standard formatting without OpenAI
        return formatter(text, use_openai=False, api_key=None)