"""
Test database optimization functionality
"""

import pytest
from unittest.mock import AsyncMock
from app.database.optimizations import DatabaseOptimizer, db_optimizer

@pytest.fixture
def mock_db_session():
    """Mock database session"""
    session = AsyncMock()
    return session

@pytest.fixture
def optimizer():
    """Database optimizer instance"""
    return DatabaseOptimizer()

class TestDatabaseOptimizer:
    """Test database optimization functionality"""
    
    @pytest.mark.asyncio
    async def test_optimizer_initialization(self, optimizer):
        """Test optimizer initializes correctly"""
        assert optimizer.query_cache == {}
        assert optimizer.slow_query_threshold == 0.1
        assert optimizer.index_recommendations == []
    
    @pytest.mark.asyncio
    async def test_analyze_query_performance_error_handling(self, optimizer, mock_db_session):
        """Test query performance analysis handles errors gracefully"""
        # Mock database error
        mock_db_session.execute.side_effect = Exception("Database connection failed")
        
        result = await optimizer.analyze_query_performance(mock_db_session)
        
        assert "error" in result
        assert "Database connection failed" in result["error"]
    
    @pytest.mark.asyncio
    async def test_create_recommended_indexes_error_handling(self, optimizer, mock_db_session):
        """Test index creation handles errors gracefully"""
        # Mock database error
        mock_db_session.execute.side_effect = Exception("Permission denied")
        mock_db_session.rollback = AsyncMock()
        
        result = await optimizer.create_recommended_indexes(mock_db_session)
        
        assert len(result) == 1
        assert "Index creation failed" in result[0]
        mock_db_session.rollback.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_vacuum_and_analyze_success(self, optimizer, mock_db_session):
        """Test vacuum and analyze operations"""
        mock_db_session.execute = AsyncMock()
        
        tables = ['projects', 'reviews']
        result = await optimizer.vacuum_and_analyze(mock_db_session, tables)
        
        assert len(result) == 2
        assert all("Successfully vacuumed and analyzed" in r for r in result)
        assert mock_db_session.execute.call_count == 2
    
    @pytest.mark.asyncio
    async def test_vacuum_and_analyze_partial_failure(self, optimizer, mock_db_session):
        """Test vacuum and analyze with partial failures"""
        # First call succeeds, second fails
        mock_db_session.execute.side_effect = [None, Exception("Table not found")]
        
        tables = ['projects', 'invalid_table']
        result = await optimizer.vacuum_and_analyze(mock_db_session, tables)
        
        assert len(result) == 2
        assert "Successfully vacuumed and analyzed projects" in result[0]
        assert "Failed to vacuum invalid_table" in result[1]

class TestOptimizationUtilities:
    """Test optimization utility functions"""
    
    def test_global_optimizer_instance(self):
        """Test global optimizer instance exists"""
        assert db_optimizer is not None
        assert isinstance(db_optimizer, DatabaseOptimizer)
    
    @pytest.mark.asyncio
    async def test_performance_monitoring_integration(self):
        """Test integration with performance monitoring"""
        # This would test the actual integration in a real environment
        # For now, just verify the structure exists
        assert hasattr(db_optimizer, 'query_cache')
        assert hasattr(db_optimizer, 'slow_query_threshold')

if __name__ == "__main__":
    pytest.main([__file__, "-v"])