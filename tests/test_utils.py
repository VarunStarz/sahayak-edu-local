"""
Tests for utility functions
"""
import pytest
import asyncio
from datetime import datetime, timezone
from utils import (
    get_current_timestamp,
    safe_dict_get,
    retry_async,
    validate_input_type,
    sanitize_string
)


def test_get_current_timestamp():
    """Test timestamp generation"""
    timestamp = get_current_timestamp()
    assert isinstance(timestamp, datetime)
    assert timestamp.tzinfo == timezone.utc


def test_safe_dict_get():
    """Test safe dictionary access"""
    data = {"key1": "value1", "key2": None}
    
    assert safe_dict_get(data, "key1") == "value1"
    assert safe_dict_get(data, "key2") is None
    assert safe_dict_get(data, "missing") is None
    assert safe_dict_get(data, "missing", "default") == "default"


def test_retry_async_success():
    """Test retry function with successful call"""
    call_count = 0
    
    async def success_func():
        nonlocal call_count
        call_count += 1
        return "success"
    
    async def run_test():
        result = await retry_async(success_func)
        assert result == "success"
        assert call_count == 1
    
    asyncio.run(run_test())


def test_retry_async_failure():
    """Test retry function with eventual failure"""
    call_count = 0
    
    async def fail_func():
        nonlocal call_count
        call_count += 1
        raise ValueError("Test error")
    
    async def run_test():
        with pytest.raises(ValueError):
            await retry_async(fail_func, max_retries=2, delay=0.01)
        
        assert call_count == 3  # Initial call + 2 retries
    
    asyncio.run(run_test())


def test_validate_input_type():
    """Test input type validation"""
    assert validate_input_type("hello", "text") is True
    assert validate_input_type("", "text") is False
    assert validate_input_type("   ", "text") is False
    assert validate_input_type(123, "text") is False
    
    assert validate_input_type("audio_data", "voice") is True
    assert validate_input_type(None, "voice") is False
    
    assert validate_input_type("image_data", "image") is True
    assert validate_input_type(None, "image") is False
    
    assert validate_input_type("anything", "invalid") is False


def test_sanitize_string():
    """Test string sanitization"""
    assert sanitize_string("hello world") == "hello world"
    assert sanitize_string("  hello world  ") == "hello world"
    assert sanitize_string("hello\x00world") == "helloworld"
    assert sanitize_string("hello\nworld") == "hello\nworld"
    assert sanitize_string("a" * 1001, max_length=10) == "aaaaaaaaaa..."
    assert sanitize_string(123) == ""