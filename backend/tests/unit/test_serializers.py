"""
Unit tests for serializers utility
"""
import pytest
from datetime import datetime, date
from decimal import Decimal
from uuid import UUID
from app.utils.serializers import (
    serialize_json,
    deserialize_json,
    serialize_pickle,
    deserialize_pickle,
    compress_json,
    decompress_json,
    EnhancedJSONEncoder
)


class TestSerializers:
    """Test suite for serialization utilities"""
    
    def test_serialize_simple_dict(self):
        """Test serializing simple dictionary"""
        data = {'key': 'value', 'number': 42}
        result = serialize_json(data)
        assert isinstance(result, str)
        assert 'key' in result
        assert 'value' in result
    
    def test_deserialize_simple_dict(self):
        """Test deserializing simple dictionary"""
        json_str = '{"key": "value", "number": 42}'
        result = deserialize_json(json_str)
        assert result == {'key': 'value', 'number': 42}
    
    def test_serialize_datetime(self):
        """Test serializing datetime objects"""
        data = {'timestamp': datetime(2024, 1, 15, 10, 30, 0)}
        result = serialize_json(data)
        assert '2024-01-15T10:30:00' in result
    
    def test_serialize_date(self):
        """Test serializing date objects"""
        data = {'date': date(2024, 1, 15)}
        result = serialize_json(data)
        assert '2024-01-15' in result
    
    def test_serialize_decimal(self):
        """Test serializing Decimal objects"""
        data = {'price': Decimal('19.99')}
        result = serialize_json(data)
        deserialized = deserialize_json(result)
        assert deserialized['price'] == 19.99
    
    def test_serialize_uuid(self):
        """Test serializing UUID objects"""
        test_uuid = UUID('12345678-1234-5678-1234-567812345678')
        data = {'id': test_uuid}
        result = serialize_json(data)
        assert '12345678-1234-5678-1234-567812345678' in result
    
    def test_serialize_bytes(self):
        """Test serializing bytes objects"""
        data = {'data': b'hello'}
        result = serialize_json(data)
        deserialized = deserialize_json(result)
        assert deserialized['data'] == 'hello'
    
    def test_serialize_custom_object(self):
        """Test serializing custom objects with __dict__"""
        class CustomObject:
            def __init__(self):
                self.name = 'test'
                self.value = 123
        
        obj = CustomObject()
        result = serialize_json(obj)
        deserialized = deserialize_json(result)
        assert deserialized['name'] == 'test'
        assert deserialized['value'] == 123
    
    def test_serialize_nested_structure(self):
        """Test serializing nested data structures"""
        data = {
            'user': {
                'id': UUID('12345678-1234-5678-1234-567812345678'),
                'created_at': datetime(2024, 1, 15),
                'balance': Decimal('100.50')
            },
            'items': [1, 2, 3]
        }
        result = serialize_json(data)
        deserialized = deserialize_json(result)
        assert deserialized['user']['balance'] == 100.50
        assert deserialized['items'] == [1, 2, 3]
    
    def test_deserialize_invalid_json(self):
        """Test deserializing invalid JSON raises error"""
        with pytest.raises(ValueError, match="Cannot deserialize JSON"):
            deserialize_json("invalid json {")
    
    def test_serialize_pickle_simple_object(self):
        """Test pickle serialization of simple object"""
        data = {'key': 'value', 'list': [1, 2, 3]}
        serialized = serialize_pickle(data)
        assert isinstance(serialized, bytes)
        deserialized = deserialize_pickle(serialized)
        assert deserialized == data
    
    def test_serialize_pickle_complex_object(self):
        """Test pickle serialization of complex Python object"""
        # Use a simple dict instead of local class (local classes can't be pickled)
        data = {
            'data': [1, 2, 3],
            'nested': {'key': 'value'},
            'tuple': (1, 2, 3)
        }
        
        serialized = serialize_pickle(data)
        deserialized = deserialize_pickle(serialized)
        assert deserialized == data
    
    def test_deserialize_pickle_invalid_data(self):
        """Test deserializing invalid pickle data raises error"""
        with pytest.raises(ValueError, match="Cannot deserialize pickle data"):
            deserialize_pickle(b'invalid pickle data')
    
    def test_compress_decompress_json(self):
        """Test compressing and decompressing JSON data"""
        data = {'key': 'value' * 100, 'numbers': list(range(100))}
        compressed = compress_json(data)
        assert isinstance(compressed, bytes)
        assert len(compressed) < len(serialize_json(data))
        
        decompressed = decompress_json(compressed)
        assert decompressed == data
    
    def test_compress_json_reduces_size(self):
        """Test that compression actually reduces data size"""
        large_data = {'data': 'x' * 1000}
        json_str = serialize_json(large_data)
        compressed = compress_json(large_data)
        
        assert len(compressed) < len(json_str.encode('utf-8'))
    
    def test_roundtrip_json_serialization(self):
        """Test complete roundtrip of JSON serialization"""
        original = {
            'string': 'test',
            'number': 42,
            'float': 3.14,
            'bool': True,
            'null': None,
            'list': [1, 2, 3],
            'nested': {'key': 'value'}
        }
        serialized = serialize_json(original)
        deserialized = deserialize_json(serialized)
        assert deserialized == original
    
    def test_serialize_empty_dict(self):
        """Test serializing empty dictionary"""
        result = serialize_json({})
        assert result == '{}'
    
    def test_serialize_empty_list(self):
        """Test serializing empty list"""
        result = serialize_json([])
        assert result == '[]'
    
    def test_enhanced_json_encoder_handles_all_types(self):
        """Test EnhancedJSONEncoder handles all supported types"""
        import json
        
        data = {
            'datetime': datetime(2024, 1, 15, 10, 30),
            'date': date(2024, 1, 15),
            'decimal': Decimal('19.99'),
            'uuid': UUID('12345678-1234-5678-1234-567812345678'),
            'bytes': b'test'
        }
        
        result = json.dumps(data, cls=EnhancedJSONEncoder)
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert '2024-01-15' in parsed['datetime']
        assert parsed['decimal'] == 19.99
