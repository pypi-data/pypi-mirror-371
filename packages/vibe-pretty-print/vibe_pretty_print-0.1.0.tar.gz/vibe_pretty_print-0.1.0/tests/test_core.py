"""
Tests for the vibe-pretty-print core functionality.
"""

import pytest
from unittest.mock import patch, Mock
import json
import yaml

from vibe_pprint.core import (
    vibe_pprint,
    ValidationError,
    OpenAIError,
    _format_json,
    _format_yaml,
    _format_xml,
    _format_text,
    _call_openai_api
)


class TestVibePPrint:
    """Test the main vibe_pprint function."""
    
    def test_json_formatting_valid(self):
        """Test JSON formatting with valid JSON."""
        json_text = '{"name": "John", "age": 30}'
        result = _format_json(json_text)
        expected = json.dumps({"name": "John", "age": 30}, indent=2, sort_keys=True)
        assert result == expected
    
    def test_json_formatting_invalid(self):
        """Test JSON formatting with invalid JSON."""
        invalid_json = '{"name": "John", "age":}'
        with pytest.raises(ValidationError):
            _format_json(invalid_json)
    
    def test_yaml_formatting_valid(self):
        """Test YAML formatting with valid YAML."""
        yaml_text = "name: John\nage: 30"
        result = _format_yaml(yaml_text)
        assert "name: John" in result
        assert "age: 30" in result
    
    def test_yaml_formatting_invalid(self):
        """Test YAML formatting with invalid YAML."""
        invalid_yaml = "name: John\n  age: 30"  # Invalid indentation
        with pytest.raises(ValidationError):
            _format_yaml(invalid_yaml)
    
    def test_xml_formatting_valid(self):
        """Test XML formatting with valid XML."""
        xml_text = "<person><name>John</name><age>30</age></person>"
        result = _format_xml(xml_text)
        assert "<person>" in result
        assert "<name>John</name>" in result
        assert "<age>30</age>" in result
    
    def test_xml_formatting_invalid(self):
        """Test XML formatting with invalid XML."""
        invalid_xml = "<person><name>John</age></name></person>"  # Mismatched tags
        with pytest.raises(ValidationError):
            _format_xml(invalid_xml)
    
    def test_text_formatting(self):
        """Test text formatting."""
        text = "Hello World! This is a test."
        result = _format_text(text)
        assert isinstance(result, str)
        assert "Hello World!" in result
    
    def test_main_function_json(self):
        """Test the main vibe_pprint function with JSON."""
        with patch('vibe_pprint.core._call_openai_api') as mock_openai:
            mock_openai.return_value = '{"formatted": "json"}'
            result = vibe_pprint("test-key", '{"test": "data"}', "json")
            assert result == '{"formatted": "json"}'
    
    def test_main_function_yaml(self):
        """Test the main vibe_pprint function with YAML."""
        with patch('vibe_pprint.core._call_openai_api') as mock_openai:
            mock_openai.return_value = "formatted: yaml"
            result = vibe_pprint("test-key", "test: data", "yaml")
            assert result == "formatted: yaml"
    
    def test_main_function_xml(self):
        """Test the main vibe_pprint function with XML."""
        with patch('vibe_pprint.core._call_openai_api') as mock_openai:
            mock_openai.return_value = "<formatted>xml</formatted>"
            result = vibe_pprint("test-key", "<test>data</test>", "xml")
            assert result == "<formatted>xml</formatted>"
    
    def test_main_function_text(self):
        """Test the main vibe_pprint function with text."""
        with patch('vibe_pprint.core._call_openai_api') as mock_openai:
            mock_openai.return_value = "formatted text"
            result = vibe_pprint("test-key", "test text", "text")
            assert result == "formatted text"
    
    def test_invalid_format_type(self):
        """Test with invalid format type."""
        with pytest.raises(ValueError, match="format_type must be one of"):
            vibe_pprint("test-key", "test", "invalid")
    
    def test_empty_api_key(self):
        """Test with empty API key."""
        with pytest.raises(ValueError, match="No API key found"):
            vibe_pprint("", "test", "json")
    
    def test_empty_text(self):
        """Test with empty text."""
        with pytest.raises(ValueError, match="text must be a non-empty string"):
            vibe_pprint("test-key", "", "json")
    
    def test_none_api_key(self):
        """Test with None API key."""
        with pytest.raises(ValueError, match="No API key found"):
            vibe_pprint(None, "test", "json")
    
    def test_none_text(self):
        """Test with None text."""
        with pytest.raises(ValueError, match="text must be a non-empty string"):
            vibe_pprint("test-key", None, "json")


class TestOpenAIIntegration:
    """Test OpenAI API integration."""
    
    @patch('requests.post')
    def test_openai_api_success(self, mock_post):
        """Test successful OpenAI API call."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "formatted content"}}]
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        result = _call_openai_api("test-key", "test text", "json")
        assert result == "formatted content"
    
    @patch('requests.post')
    def test_openai_api_http_error(self, mock_post):
        """Test OpenAI API call with HTTP error."""
        import requests
        mock_post.side_effect = requests.exceptions.RequestException("HTTP Error")
        
        with pytest.raises(OpenAIError, match="OpenAI API call failed"):
            _call_openai_api("test-key", "test text", "json")
    
    @patch('requests.post')
    def test_openai_api_invalid_response(self, mock_post):
        """Test OpenAI API call with invalid response format."""
        mock_response = Mock()
        mock_response.json.return_value = {"invalid": "format"}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        with pytest.raises(OpenAIError, match="Invalid OpenAI API response format"):
            _call_openai_api("test-key", "test text", "json")


class TestFallbackBehavior:
    """Test fallback behavior when OpenAI fails."""
    
    def test_openai_failure_fallback_json(self):
        """Test fallback to standard formatting when OpenAI fails for JSON."""
        with patch('vibe_pprint.core._call_openai_api', side_effect=OpenAIError("API Error")):
            json_text = '{"name": "John", "age": 30}'
            result = vibe_pprint("test-key", json_text, "json")
            expected = json.dumps({"name": "John", "age": 30}, indent=2, sort_keys=True)
            assert result == expected
    
    def test_openai_failure_fallback_yaml(self):
        """Test fallback to standard formatting when OpenAI fails for YAML."""
        with patch('vibe_pprint.core._call_openai_api', side_effect=OpenAIError("API Error")):
            yaml_text = "name: John\nage: 30"
            result = vibe_pprint("test-key", yaml_text, "yaml")
            assert "name: John" in result
            assert "age: 30" in result
    
    def test_openai_failure_fallback_xml(self):
        """Test fallback to standard formatting when OpenAI fails for XML."""
        with patch('vibe_pprint.core._call_openai_api', side_effect=OpenAIError("API Error")):
            xml_text = "<person><name>John</name><age>30</age></person>"
            result = vibe_pprint("test-key", xml_text, "xml")
            assert "<person>" in result
            assert "<name>John</name>" in result
    
    def test_openai_failure_fallback_text(self):
        """Test fallback to standard formatting when OpenAI fails for text."""
        with patch('vibe_pprint.core._call_openai_api', side_effect=OpenAIError("API Error")):
            text = "Hello World! This is a test."
            result = vibe_pprint("test-key", text, "text")
            assert isinstance(result, str)
            assert "Hello World!" in result


class TestAPIKeyResolution:
    """Test API key resolution functionality."""
    
    def test_api_key_from_function_parameter(self):
        """Test API key resolution from function parameter."""
        from vibe_pprint.core import _get_api_key
        result = _get_api_key("test-key")
        assert result == "test-key"
    
    def test_api_key_from_environment_variable(self):
        """Test API key resolution from environment variable."""
        from vibe_pprint.core import _get_api_key
        with patch.dict('os.environ', {'VIBE_PP_API_KEY': 'env-key'}):
            result = _get_api_key()
            assert result == "env-key"
    
    def test_api_key_preference_order(self):
        """Test API key resolution preference order."""
        from vibe_pprint.core import _get_api_key
        with patch.dict('os.environ', {'VIBE_PP_API_KEY': 'env-key'}):
            result = _get_api_key("function-key")
            assert result == "function-key"
    
    def test_api_key_no_key_found(self):
        """Test when no API key is found."""
        from vibe_pprint.core import _get_api_key
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="No API key found"):
                _get_api_key()


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_nested_json_formatting(self):
        """Test formatting of deeply nested JSON."""
        nested_json = {
            "level1": {
                "level2": {
                    "level3": {
                        "data": [1, 2, 3, {
                            "deep": "value"
                        }]
                    }
                }
            }
        }
        json_str = json.dumps(nested_json)
        result = _format_json(json_str)
        assert "level1" in result
        assert "level2" in result
        assert "level3" in result
        assert "deep" in result
    
    def test_large_yaml_formatting(self):
        """Test formatting of large YAML structures."""
        large_yaml = {
            "users": [
                {"id": i, "name": f"user_{i}", "active": i % 2 == 0}
                for i in range(100)
            ]
        }
        yaml_str = yaml.dump(large_yaml)
        result = _format_yaml(yaml_str)
        assert "users:" in result
        assert "user_0" in result
        assert "user_99" in result
    
    def test_special_characters_text(self):
        """Test formatting text with special characters."""
        special_text = "Special chars: àáâãäåæçèéêë ñ 中文 🚀"
        result = _format_text(special_text)
        assert isinstance(result, str)
        assert "Special chars:" in result
    
    def test_unicode_xml_formatting(self):
        """Test XML formatting with Unicode characters."""
        unicode_xml = "<person><name>José María</name><city>São Paulo</city></person>"
        result = _format_xml(unicode_xml)
        assert "José María" in result
        assert "São Paulo" in result