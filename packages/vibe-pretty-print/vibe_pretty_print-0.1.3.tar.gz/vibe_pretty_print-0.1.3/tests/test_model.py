"""
Tests for model module
"""
import pytest
from vibe_pretty_print.model import FormatRequest, FormatResult, ValidationError, OpenAIError

class TestFormatRequest:
    def test_format_request_creation(self):
        request = FormatRequest("test text", "json", "api-key")
        assert request.text == "test text"
        assert request.format_type == "json"
        assert request.api_key == "api-key"

    def test_format_request_optional_api_key(self):
        request = FormatRequest("test", "yaml")
        assert request.text == "test"
        assert request.format_type == "yaml"
        assert request.api_key is None

class TestFormatResult:
    def test_format_result_creation(self):
        result = FormatResult("formatted", "json")
        assert result.content == "formatted"
        assert result.format_type == "json"
        assert result.source == "standard"

    def test_format_result_with_source(self):
        result = FormatResult("formatted", "xml", "openai")
        assert result.source == "openai"

class TestExceptions:
    def test_validation_error(self):
        with pytest.raises(ValidationError) as exc_info:
            raise ValidationError("test error")
        assert str(exc_info.value) == "test error"

    def test_openai_error(self):
        with pytest.raises(OpenAIError) as exc_info:
            raise OpenAIError("test error")
        assert str(exc_info.value) == "test error"