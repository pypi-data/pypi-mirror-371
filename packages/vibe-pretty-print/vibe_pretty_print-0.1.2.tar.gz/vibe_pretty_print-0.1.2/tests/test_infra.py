"""
Tests for infrastructure module
"""
import pytest
from vibe_pretty_print.model import FormatRequest, ValidationError
from vibe_pretty_print.infra import Validator, StandardFormatter

class TestValidator:
    def test_validate_valid_json(self):
        validator = Validator()
        request = FormatRequest('{"key": "value"}', "json")
        validator.validate(request)  # Should not raise

    def test_validate_invalid_json(self):
        validator = Validator()
        request = FormatRequest('{"invalid": json}', "json")
        with pytest.raises(ValidationError):
            validator.validate(request)

    def test_validate_valid_xml(self):
        validator = Validator()
        request = FormatRequest('<root><item>test</item></root>', "xml")
        validator.validate(request)  # Should not raise

    def test_validate_invalid_xml(self):
        validator = Validator()
        request = FormatRequest('<invalid>', "xml")
        with pytest.raises(ValidationError):
            validator.validate(request)

    def test_validate_valid_yaml(self):
        validator = Validator()
        request = FormatRequest('key: value\nlist:\n  - item1\n  - item2', "yaml")
        validator.validate(request)  # Should not raise

    def test_validate_invalid_yaml(self):
        validator = Validator()
        request = FormatRequest('invalid: yaml: syntax', "yaml")
        with pytest.raises(ValidationError):
            validator.validate(request)

    def test_validate_empty_text(self):
        validator = Validator()
        request = FormatRequest('', "text")
        with pytest.raises(ValidationError):
            validator.validate(request)

    def test_validate_invalid_format_type(self):
        validator = Validator()
        request = FormatRequest('test', "invalid")
        with pytest.raises(ValidationError):
            validator.validate(request)

class TestStandardFormatter:
    def test_format_json(self):
        formatter = StandardFormatter()
        request = FormatRequest('{"b":2,"a":1}', "json")
        result = formatter.format(request)
        
        assert result.format_type == "json"
        assert result.source == "standard"
        assert '"a"' in result.content
        assert '"b"' in result.content

    def test_format_yaml(self):
        formatter = StandardFormatter()
        request = FormatRequest('key: value\nlist:\n  - item1', "yaml")
        result = formatter.format(request)
        
        assert result.format_type == "yaml"
        assert result.source == "standard"
        assert 'key: value' in result.content

    def test_format_text(self):
        formatter = StandardFormatter()
        request = FormatRequest('  hello world  ', "text")
        result = formatter.format(request)
        
        assert result.format_type == "text"
        assert result.source == "standard"
        assert result.content == "hello world"

    def test_format_xml(self):
        formatter = StandardFormatter()
        request = FormatRequest('<root><item>test</item></root>', "xml")
        result = formatter.format(request)
        
        assert result.format_type == "xml"
        assert result.source == "standard"
        assert 'root' in result.content