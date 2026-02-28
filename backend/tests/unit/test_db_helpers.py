"""
Unit tests for database helper utilities.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.utils.db_helpers import (
    get_or_404_async,
    get_or_404_sync,
    get_by_field_async,
    get_by_field_sync,
    check_unique_field_sync,
    check_unique_field_async
)


class MockModel:
    """Mock SQLAlchemy model for testing."""
    __name__ = "MockModel"
    id = None
    name = None


class TestGetOr404Sync:
    """Tests for get_or_404_sync function."""
    
    def test_get_or_404_sync_found(self):
        """Test successful retrieval."""
        # Setup
        db = MagicMock(spec=Session)
        mock_entity = MockModel()
        mock_entity.id = "123"
        
        db.query.return_value.filter.return_value.first.return_value = mock_entity
        
        # Execute
        result = get_or_404_sync(db, MockModel, "123")
        
        # Assert
        assert result == mock_entity
        db.query.assert_called_once_with(MockModel)
    
    def test_get_or_404_sync_not_found(self):
        """Test 404 error when entity not found."""
        # Setup
        db = MagicMock(spec=Session)
        db.query.return_value.filter.return_value.first.return_value = None
        
        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            get_or_404_sync(db, MockModel, "123")
        
        assert exc_info.value.status_code == 404
        assert "MockModel not found" in exc_info.value.detail
    
    def test_get_or_404_sync_custom_error_message(self):
        """Test custom error message."""
        # Setup
        db = MagicMock(spec=Session)
        db.query.return_value.filter.return_value.first.return_value = None
        
        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            get_or_404_sync(db, MockModel, "123", error_message="Custom error")
        
        assert exc_info.value.detail == "Custom error"


class TestGetOr404Async:
    """Tests for get_or_404_async function."""
    
    @pytest.mark.asyncio
    async def test_get_or_404_async_found(self):
        """Test successful retrieval (async)."""
        # Setup
        db = AsyncMock(spec=AsyncSession)
        mock_entity = MockModel()
        mock_entity.id = UUID("123e4567-e89b-12d3-a456-426614174000")
        
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_entity
        db.execute.return_value = mock_result
        
        # Execute
        result = await get_or_404_async(
            db, MockModel, "123e4567-e89b-12d3-a456-426614174000"
        )
        
        # Assert
        assert result == mock_entity
        db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_or_404_async_not_found(self):
        """Test 404 error when entity not found (async)."""
        # Setup
        db = AsyncMock(spec=AsyncSession)
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None
        db.execute.return_value = mock_result
        
        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            await get_or_404_async(
                db, MockModel, "123e4567-e89b-12d3-a456-426614174000"
            )
        
        assert exc_info.value.status_code == 404
    
    @pytest.mark.asyncio
    async def test_get_or_404_async_invalid_uuid(self):
        """Test 400 error for invalid UUID format."""
        # Setup
        db = AsyncMock(spec=AsyncSession)
        
        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            await get_or_404_async(db, MockModel, "invalid-uuid")
        
        assert exc_info.value.status_code == 400
        assert "Invalid" in exc_info.value.detail


class TestGetByFieldSync:
    """Tests for get_by_field_sync function."""
    
    def test_get_by_field_sync_found(self):
        """Test successful retrieval by field."""
        # Setup
        db = MagicMock(spec=Session)
        mock_entity = MockModel()
        mock_entity.name = "test"
        
        db.query.return_value.filter.return_value.first.return_value = mock_entity
        
        # Execute
        result = get_by_field_sync(db, MockModel, "name", "test")
        
        # Assert
        assert result == mock_entity
    
    def test_get_by_field_sync_not_found_no_error(self):
        """Test returns None when not found and error_if_not_found=False."""
        # Setup
        db = MagicMock(spec=Session)
        db.query.return_value.filter.return_value.first.return_value = None
        
        # Execute
        result = get_by_field_sync(db, MockModel, "name", "test", error_if_not_found=False)
        
        # Assert
        assert result is None
    
    def test_get_by_field_sync_not_found_with_error(self):
        """Test raises 404 when not found and error_if_not_found=True."""
        # Setup
        db = MagicMock(spec=Session)
        db.query.return_value.filter.return_value.first.return_value = None
        
        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            get_by_field_sync(db, MockModel, "name", "test", error_if_not_found=True)
        
        assert exc_info.value.status_code == 404


class TestCheckUniqueFieldSync:
    """Tests for check_unique_field_sync function."""
    
    def test_check_unique_field_sync_unique(self):
        """Test passes when field value is unique."""
        # Setup
        db = MagicMock(spec=Session)
        db.query.return_value.filter.return_value.first.return_value = None
        
        # Execute (should not raise)
        check_unique_field_sync(db, MockModel, "name", "unique_value")
    
    def test_check_unique_field_sync_not_unique(self):
        """Test raises 400 when field value already exists."""
        # Setup
        db = MagicMock(spec=Session)
        mock_entity = MockModel()
        db.query.return_value.filter.return_value.first.return_value = mock_entity
        
        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            check_unique_field_sync(db, MockModel, "name", "existing_value")
        
        assert exc_info.value.status_code == 400
        assert "already exists" in exc_info.value.detail
    
    def test_check_unique_field_sync_custom_error(self):
        """Test custom error message."""
        # Setup
        db = MagicMock(spec=Session)
        mock_entity = MockModel()
        db.query.return_value.filter.return_value.first.return_value = mock_entity
        
        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            check_unique_field_sync(
                db, MockModel, "name", "existing_value",
                error_message="Custom uniqueness error"
            )
        
        assert exc_info.value.detail == "Custom uniqueness error"


class TestCheckUniqueFieldAsync:
    """Tests for check_unique_field_async function."""
    
    @pytest.mark.asyncio
    async def test_check_unique_field_async_unique(self):
        """Test passes when field value is unique (async)."""
        # Setup
        db = AsyncMock(spec=AsyncSession)
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None
        db.execute.return_value = mock_result
        
        # Execute (should not raise)
        await check_unique_field_async(db, MockModel, "name", "unique_value")
    
    @pytest.mark.asyncio
    async def test_check_unique_field_async_not_unique(self):
        """Test raises 400 when field value already exists (async)."""
        # Setup
        db = AsyncMock(spec=AsyncSession)
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = MockModel()
        db.execute.return_value = mock_result
        
        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            await check_unique_field_async(db, MockModel, "name", "existing_value")
        
        assert exc_info.value.status_code == 400
