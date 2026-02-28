"""
Tests for Graceful Shutdown Service

Tests graceful shutdown handling including:
- Signal handling (SIGTERM, SIGINT)
- Shutdown callback execution
- Database connection cleanup
- Timeout handling

Validates Requirements: 12.10
"""

import pytest
import asyncio
import signal
from unittest.mock import AsyncMock, MagicMock, patch, call
from datetime import datetime

from app.services.graceful_shutdown import (
    GracefulShutdownHandler,
    get_shutdown_handler,
    setup_graceful_shutdown,
)


@pytest.fixture
def shutdown_handler():
    """Create a shutdown handler instance for testing"""
    return GracefulShutdownHandler(shutdown_timeout=5)


@pytest.fixture
def mock_database_close_functions():
    """Mock database close functions"""
    with patch('app.services.graceful_shutdown.close_postgres') as mock_postgres, \
         patch('app.services.graceful_shutdown.close_neo4j') as mock_neo4j, \
         patch('app.services.graceful_shutdown.close_redis') as mock_redis:
        
        # Make them async
        mock_postgres.return_value = asyncio.Future()
        mock_postgres.return_value.set_result(None)
        
        mock_neo4j.return_value = asyncio.Future()
        mock_neo4j.return_value.set_result(None)
        
        mock_redis.return_value = asyncio.Future()
        mock_redis.return_value.set_result(None)
        
        yield {
            'postgres': mock_postgres,
            'neo4j': mock_neo4j,
            'redis': mock_redis,
        }


class TestGracefulShutdownHandler:
    """Tests for GracefulShutdownHandler"""
    
    def test_initialization(self, shutdown_handler):
        """Test shutdown handler initializes correctly"""
        assert shutdown_handler.shutdown_timeout == 5
        assert shutdown_handler.is_shutting_down is False
        assert len(shutdown_handler.shutdown_callbacks) == 0
    
    def test_register_shutdown_callback(self, shutdown_handler):
        """Test registering shutdown callbacks"""
        async def callback1():
            pass
        
        async def callback2():
            pass
        
        shutdown_handler.register_shutdown_callback(callback1)
        shutdown_handler.register_shutdown_callback(callback2)
        
        assert len(shutdown_handler.shutdown_callbacks) == 2
        assert callback1 in shutdown_handler.shutdown_callbacks
        assert callback2 in shutdown_handler.shutdown_callbacks
    
    def test_setup_signal_handlers(self, shutdown_handler):
        """Test signal handlers are registered"""
        with patch('signal.signal') as mock_signal:
            shutdown_handler.setup_signal_handlers()
            
            # Verify SIGTERM and SIGINT handlers were registered
            calls = mock_signal.call_args_list
            assert len(calls) == 2
            
            # Check SIGTERM
            assert calls[0][0][0] == signal.SIGTERM
            
            # Check SIGINT
            assert calls[1][0][0] == signal.SIGINT
    
    @pytest.mark.asyncio
    async def test_perform_shutdown_executes_callbacks(self, shutdown_handler):
        """Test shutdown executes all registered callbacks"""
        callback1_executed = False
        callback2_executed = False
        
        async def callback1():
            nonlocal callback1_executed
            callback1_executed = True
        
        async def callback2():
            nonlocal callback2_executed
            callback2_executed = True
        
        shutdown_handler.register_shutdown_callback(callback1)
        shutdown_handler.register_shutdown_callback(callback2)
        
        # Mock database close functions
        with patch.object(shutdown_handler, '_close_database_connections', new_callable=AsyncMock):
            await shutdown_handler._perform_shutdown()
        
        assert callback1_executed is True
        assert callback2_executed is True
        assert shutdown_handler._shutdown_event.is_set()
    
    @pytest.mark.asyncio
    async def test_perform_shutdown_handles_callback_errors(self, shutdown_handler):
        """Test shutdown continues even if callbacks fail"""
        callback1_executed = False
        callback2_executed = False
        
        async def callback1():
            nonlocal callback1_executed
            callback1_executed = True
            raise Exception("Callback 1 failed")
        
        async def callback2():
            nonlocal callback2_executed
            callback2_executed = True
        
        shutdown_handler.register_shutdown_callback(callback1)
        shutdown_handler.register_shutdown_callback(callback2)
        
        # Mock database close functions
        with patch.object(shutdown_handler, '_close_database_connections', new_callable=AsyncMock):
            await shutdown_handler._perform_shutdown()
        
        # Both callbacks should have been attempted
        assert callback1_executed is True
        assert callback2_executed is True
        assert shutdown_handler._shutdown_event.is_set()
    
    @pytest.mark.asyncio
    async def test_perform_shutdown_handles_callback_timeout(self, shutdown_handler):
        """Test shutdown handles callback timeouts"""
        callback1_executed = False
        callback2_executed = False
        
        async def callback1():
            nonlocal callback1_executed
            callback1_executed = True
            # Simulate long-running callback
            await asyncio.sleep(10)
        
        async def callback2():
            nonlocal callback2_executed
            callback2_executed = True
        
        shutdown_handler.register_shutdown_callback(callback1)
        shutdown_handler.register_shutdown_callback(callback2)
        
        # Mock database close functions
        with patch.object(shutdown_handler, '_close_database_connections', new_callable=AsyncMock):
            await shutdown_handler._perform_shutdown()
        
        # Callback 1 should have been attempted (but timed out)
        assert callback1_executed is True
        # Callback 2 should still execute
        assert callback2_executed is True
        assert shutdown_handler._shutdown_event.is_set()
    
    @pytest.mark.asyncio
    async def test_close_database_connections(self, shutdown_handler):
        """Test database connections are closed"""
        with patch('app.database.postgresql.close_postgres', new_callable=AsyncMock) as mock_postgres, \
             patch('app.database.neo4j_db.close_neo4j', new_callable=AsyncMock) as mock_neo4j, \
             patch('app.database.redis_db.close_redis', new_callable=AsyncMock) as mock_redis:
            
            await shutdown_handler._close_database_connections()
            
            # Verify all close functions were called
            mock_postgres.assert_called_once()
            mock_neo4j.assert_called_once()
            mock_redis.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_close_database_connections_handles_errors(self, shutdown_handler):
        """Test database connection cleanup handles errors gracefully"""
        with patch('app.database.postgresql.close_postgres', new_callable=AsyncMock) as mock_postgres, \
             patch('app.database.neo4j_db.close_neo4j', new_callable=AsyncMock) as mock_neo4j, \
             patch('app.database.redis_db.close_redis', new_callable=AsyncMock) as mock_redis:
            
            # Make PostgreSQL close fail
            mock_postgres.side_effect = Exception("PostgreSQL close failed")
            
            # Should not raise exception
            await shutdown_handler._close_database_connections()
            
            # All close functions should have been attempted
            mock_postgres.assert_called_once()
            mock_neo4j.assert_called_once()
            mock_redis.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_safe_close_success(self, shutdown_handler):
        """Test safe_close successfully closes connection"""
        mock_close = AsyncMock()
        
        await shutdown_handler._safe_close(mock_close, "TestDB")
        
        mock_close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_safe_close_handles_error(self, shutdown_handler):
        """Test safe_close handles errors gracefully"""
        mock_close = AsyncMock()
        mock_close.side_effect = Exception("Close failed")
        
        # Should not raise exception
        await shutdown_handler._safe_close(mock_close, "TestDB")
        
        mock_close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_wait_for_shutdown(self, shutdown_handler):
        """Test wait_for_shutdown blocks until shutdown completes"""
        # Start shutdown in background
        async def trigger_shutdown():
            await asyncio.sleep(0.1)
            shutdown_handler._shutdown_event.set()
        
        asyncio.create_task(trigger_shutdown())
        
        # Wait for shutdown
        await shutdown_handler.wait_for_shutdown()
        
        assert shutdown_handler._shutdown_event.is_set()
    
    def test_is_shutdown_in_progress(self, shutdown_handler):
        """Test is_shutdown_in_progress returns correct status"""
        assert shutdown_handler.is_shutdown_in_progress() is False
        
        shutdown_handler.is_shutting_down = True
        
        assert shutdown_handler.is_shutdown_in_progress() is True


class TestGlobalShutdownHandler:
    """Tests for global shutdown handler functions"""
    
    def test_get_shutdown_handler_creates_instance(self):
        """Test get_shutdown_handler creates a singleton instance"""
        # Reset global instance
        import app.services.graceful_shutdown as module
        module._shutdown_handler = None
        
        handler1 = get_shutdown_handler()
        handler2 = get_shutdown_handler()
        
        assert handler1 is handler2
        assert isinstance(handler1, GracefulShutdownHandler)
    
    def test_setup_graceful_shutdown(self):
        """Test setup_graceful_shutdown initializes and registers handlers"""
        # Reset global instance
        import app.services.graceful_shutdown as module
        module._shutdown_handler = None
        
        with patch('signal.signal') as mock_signal:
            handler = setup_graceful_shutdown(shutdown_timeout=10)
            
            assert isinstance(handler, GracefulShutdownHandler)
            assert handler.shutdown_timeout == 10
            
            # Verify signal handlers were registered
            assert mock_signal.call_count == 2


class TestShutdownIntegration:
    """Integration tests for graceful shutdown"""
    
    @pytest.mark.asyncio
    async def test_full_shutdown_sequence(self):
        """Test complete shutdown sequence"""
        handler = GracefulShutdownHandler(shutdown_timeout=5)
        
        # Track execution order
        execution_order = []
        
        async def callback1():
            execution_order.append('callback1')
        
        async def callback2():
            execution_order.append('callback2')
        
        handler.register_shutdown_callback(callback1)
        handler.register_shutdown_callback(callback2)
        
        # Mock database close functions
        with patch('app.database.postgresql.close_postgres', new_callable=AsyncMock) as mock_postgres, \
             patch('app.database.neo4j_db.close_neo4j', new_callable=AsyncMock) as mock_neo4j, \
             patch('app.database.redis_db.close_redis', new_callable=AsyncMock) as mock_redis:
            
            await handler._perform_shutdown()
            
            # Verify execution order
            assert execution_order == ['callback1', 'callback2']
            
            # Verify database connections were closed
            mock_postgres.assert_called_once()
            mock_neo4j.assert_called_once()
            mock_redis.assert_called_once()
            
            # Verify shutdown completed
            assert handler._shutdown_event.is_set()
    
    @pytest.mark.asyncio
    async def test_shutdown_with_mixed_success_and_failure(self):
        """Test shutdown handles mix of successful and failed operations"""
        handler = GracefulShutdownHandler(shutdown_timeout=5)
        
        # Track execution
        successful_callback_executed = False
        failed_callback_executed = False
        
        async def successful_callback():
            nonlocal successful_callback_executed
            successful_callback_executed = True
        
        async def failed_callback():
            nonlocal failed_callback_executed
            failed_callback_executed = True
            raise Exception("Callback failed")
        
        handler.register_shutdown_callback(successful_callback)
        handler.register_shutdown_callback(failed_callback)
        
        # Mock database close functions with one failure
        with patch('app.database.postgresql.close_postgres', new_callable=AsyncMock) as mock_postgres, \
             patch('app.database.neo4j_db.close_neo4j', new_callable=AsyncMock) as mock_neo4j, \
             patch('app.database.redis_db.close_redis', new_callable=AsyncMock) as mock_redis:
            
            # Make Neo4j close fail
            mock_neo4j.side_effect = Exception("Neo4j close failed")
            
            await handler._perform_shutdown()
            
            # Verify all callbacks were attempted
            assert successful_callback_executed is True
            assert failed_callback_executed is True
            
            # Verify all database close attempts were made
            mock_postgres.assert_called_once()
            mock_neo4j.assert_called_once()
            mock_redis.assert_called_once()
            
            # Verify shutdown completed despite failures
            assert handler._shutdown_event.is_set()
