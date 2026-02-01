"""
Example test file to ensure pytest is working correctly
"""

import pytest
import asyncio


def test_basic_math():
    """Test basic math operations"""
    assert 2 + 2 == 4
    assert 10 - 5 == 5
    assert 3 * 4 == 12


def test_string_operations():
    """Test string operations"""
    test_string = "Hello World"
    assert test_string.lower() == "hello world"
    assert test_string.upper() == "HELLO WORLD"
    assert len(test_string) == 11


@pytest.mark.asyncio
async def test_async_operation():
    """Test async operations"""
    async def async_function():
        await asyncio.sleep(0.01)
        return "async result"
    
    result = await async_function()
    assert result == "async result"


def test_list_operations():
    """Test list operations"""
    test_list = [1, 2, 3, 4, 5]
    assert len(test_list) == 5
    assert test_list[0] == 1
    assert test_list[-1] == 5
    assert sum(test_list) == 15


def test_dictionary_operations():
    """Test dictionary operations"""
    test_dict = {"key1": "value1", "key2": "value2"}
    assert test_dict["key1"] == "value1"
    assert "key2" in test_dict
    assert len(test_dict) == 2


class TestExampleClass:
    """Example test class"""
    
    def test_class_method(self):
        """Test class method"""
        assert True
    
    def test_setup_and_teardown(self):
        """Test with setup and teardown"""
        # Setup
        data = {"test": True}
        
        # Test
        assert data["test"] is True
        
        # Teardown (automatic with pytest)
        pass