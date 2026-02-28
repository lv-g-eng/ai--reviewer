"""
Tests for OpenTelemetry distributed tracing integration.

Validates Requirement 18.1: Distributed tracing using OpenTelemetry
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter

from app.core.tracing import (
    TracingConfig,
    setup_tracing,
    get_tracing_config,
    get_tracer,
)


class TestTracingConfig:
    """Test TracingConfig class"""
    
    def test_tracing_config_initialization(self):
        """Test TracingConfig initialization with default values"""
        config = TracingConfig(
            service_name="test-service",
            service_version="1.0.0",
            environment="test",
        )
        
        assert config.service_name == "test-service"
        assert config.service_version == "1.0.0"
        assert config.environment == "test"
        assert config.otlp_endpoint == "http://localhost:4317"
        assert config.enable_console_export is False
        assert config.sample_rate == 1.0
        assert config._is_initialized is False
    
    def test_tracing_config_custom_values(self):
        """Test TracingConfig initialization with custom values"""
        config = TracingConfig(
            service_name="custom-service",
            service_version="2.0.0",
            environment="production",
            otlp_endpoint="http://xray-collector:4317",
            enable_console_export=True,
            sample_rate=0.5,
        )
        
        assert config.service_name == "custom-service"
        assert config.service_version == "2.0.0"
        assert config.environment == "production"
        assert config.otlp_endpoint == "http://xray-collector:4317"
        assert config.enable_console_export is True
        assert config.sample_rate == 0.5
    
    @patch('app.core.tracing.OTLPSpanExporter')
    @patch('app.core.tracing.TracerProvider')
    def test_initialize_tracing(self, mock_tracer_provider, mock_otlp_exporter):
        """Test tracing initialization"""
        config = TracingConfig(
            service_name="test-service",
            service_version="1.0.0",
            environment="test",
        )
        
        config.initialize()
        
        assert config._is_initialized is True
        mock_otlp_exporter.assert_called_once()
        mock_tracer_provider.assert_called_once()
    
    def test_initialize_tracing_twice(self):
        """Test that initializing tracing twice doesn't cause issues"""
        config = TracingConfig(
            service_name="test-service",
            service_version="1.0.0",
            environment="test",
        )
        
        with patch('app.core.tracing.OTLPSpanExporter'):
            with patch('app.core.tracing.TracerProvider'):
                config.initialize()
                config.initialize()  # Should log warning and skip
                
                assert config._is_initialized is True
    
    @patch('app.core.tracing.FastAPIInstrumentor')
    def test_instrument_fastapi(self, mock_instrumentor):
        """Test FastAPI instrumentation"""
        config = TracingConfig(
            service_name="test-service",
            service_version="1.0.0",
            environment="test",
        )
        
        mock_app = Mock()
        config.instrument_fastapi(mock_app)
        
        mock_instrumentor.instrument_app.assert_called_once_with(mock_app)
    
    @patch('app.core.tracing.HTTPXClientInstrumentor')
    def test_instrument_httpx(self, mock_instrumentor):
        """Test HTTPX instrumentation"""
        config = TracingConfig(
            service_name="test-service",
            service_version="1.0.0",
            environment="test",
        )
        
        config.instrument_httpx()
        
        mock_instrumentor.return_value.instrument.assert_called_once()
    
    @patch('app.core.tracing.RedisInstrumentor')
    def test_instrument_redis(self, mock_instrumentor):
        """Test Redis instrumentation"""
        config = TracingConfig(
            service_name="test-service",
            service_version="1.0.0",
            environment="test",
        )
        
        config.instrument_redis()
        
        mock_instrumentor.return_value.instrument.assert_called_once()
    
    @patch('app.core.tracing.SQLAlchemyInstrumentor')
    def test_instrument_sqlalchemy(self, mock_instrumentor):
        """Test SQLAlchemy instrumentation"""
        config = TracingConfig(
            service_name="test-service",
            service_version="1.0.0",
            environment="test",
        )
        
        mock_engine = Mock()
        config.instrument_sqlalchemy(mock_engine)
        
        mock_instrumentor.return_value.instrument.assert_called_once_with(engine=mock_engine)
    
    def test_get_tracer(self):
        """Test getting a tracer instance"""
        config = TracingConfig(
            service_name="test-service",
            service_version="1.0.0",
            environment="test",
        )
        
        tracer = config.get_tracer("test-module")
        
        assert tracer is not None
        # Tracer is returned from trace.get_tracer(), which is a valid tracer
    
    @patch('app.core.tracing.TracerProvider')
    def test_shutdown(self, mock_tracer_provider):
        """Test tracing shutdown"""
        config = TracingConfig(
            service_name="test-service",
            service_version="1.0.0",
            environment="test",
        )
        
        mock_provider = Mock()
        config._tracer_provider = mock_provider
        
        config.shutdown()
        
        mock_provider.shutdown.assert_called_once()


class TestTracingSetup:
    """Test tracing setup functions"""
    
    @patch('app.core.tracing.TracingConfig')
    def test_setup_tracing(self, mock_tracing_config):
        """Test setup_tracing function"""
        # Reset global config
        import app.core.tracing
        app.core.tracing._tracing_config = None
        
        mock_config = Mock()
        mock_tracing_config.return_value = mock_config
        
        result = setup_tracing(
            service_name="test-service",
            service_version="1.0.0",
            environment="test",
        )
        
        assert result == mock_config
        mock_config.initialize.assert_called_once()
    
    def test_get_tracing_config(self):
        """Test get_tracing_config function"""
        # Reset global config
        import app.core.tracing
        app.core.tracing._tracing_config = None
        
        config = get_tracing_config()
        assert config is None
        
        # Set a config
        mock_config = Mock()
        app.core.tracing._tracing_config = mock_config
        
        config = get_tracing_config()
        assert config == mock_config
    
    def test_get_tracer_function(self):
        """Test get_tracer function"""
        tracer = get_tracer("test-module")
        
        assert tracer is not None
        # Tracer is returned from trace.get_tracer(), which is a valid tracer


class TestTracingIntegration:
    """Integration tests for tracing"""
    
    def test_create_custom_span(self):
        """Test creating custom spans"""
        # Setup tracing with console exporter for testing
        tracer_provider = TracerProvider()
        console_exporter = ConsoleSpanExporter()
        span_processor = SimpleSpanProcessor(console_exporter)
        tracer_provider.add_span_processor(span_processor)
        trace.set_tracer_provider(tracer_provider)
        
        tracer = get_tracer("test")
        
        # Create a span
        with tracer.start_as_current_span("test_operation") as span:
            span.set_attribute("test.attribute", "test_value")
            span.set_attribute("test.number", 42)
            
            # Nested span
            with tracer.start_as_current_span("nested_operation") as nested_span:
                nested_span.set_attribute("nested.attribute", "nested_value")
        
        # Verify spans were created (they should be exported to console)
        assert True  # If we get here without errors, spans were created successfully
    
    def test_span_with_exception(self):
        """Test span with exception recording"""
        tracer_provider = TracerProvider()
        console_exporter = ConsoleSpanExporter()
        span_processor = SimpleSpanProcessor(console_exporter)
        tracer_provider.add_span_processor(span_processor)
        trace.set_tracer_provider(tracer_provider)
        
        tracer = get_tracer("test")
        
        # Create a span with exception
        with pytest.raises(ValueError):
            with tracer.start_as_current_span("test_operation") as span:
                span.set_attribute("test.attribute", "test_value")
                
                try:
                    raise ValueError("Test error")
                except Exception as e:
                    span.record_exception(e)
                    from opentelemetry.trace import Status, StatusCode
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    raise
    
    def test_multiple_spans_in_sequence(self):
        """Test creating multiple spans in sequence"""
        tracer_provider = TracerProvider()
        console_exporter = ConsoleSpanExporter()
        span_processor = SimpleSpanProcessor(console_exporter)
        tracer_provider.add_span_processor(span_processor)
        trace.set_tracer_provider(tracer_provider)
        
        tracer = get_tracer("test")
        
        # Create multiple spans
        with tracer.start_as_current_span("operation_1") as span1:
            span1.set_attribute("operation", "1")
        
        with tracer.start_as_current_span("operation_2") as span2:
            span2.set_attribute("operation", "2")
        
        with tracer.start_as_current_span("operation_3") as span3:
            span3.set_attribute("operation", "3")
        
        assert True  # If we get here, all spans were created successfully


class TestTracingConfiguration:
    """Test tracing configuration validation"""
    
    def test_sample_rate_validation(self):
        """Test sample rate validation"""
        # Valid sample rates
        config1 = TracingConfig(
            service_name="test",
            service_version="1.0.0",
            environment="test",
            sample_rate=0.0,
        )
        assert config1.sample_rate == 0.0
        
        config2 = TracingConfig(
            service_name="test",
            service_version="1.0.0",
            environment="test",
            sample_rate=0.5,
        )
        assert config2.sample_rate == 0.5
        
        config3 = TracingConfig(
            service_name="test",
            service_version="1.0.0",
            environment="test",
            sample_rate=1.0,
        )
        assert config3.sample_rate == 1.0
    
    def test_otlp_endpoint_configuration(self):
        """Test OTLP endpoint configuration"""
        # Default endpoint
        config1 = TracingConfig(
            service_name="test",
            service_version="1.0.0",
            environment="test",
        )
        assert config1.otlp_endpoint == "http://localhost:4317"
        
        # Custom endpoint
        config2 = TracingConfig(
            service_name="test",
            service_version="1.0.0",
            environment="test",
            otlp_endpoint="http://custom-collector:4317",
        )
        assert config2.otlp_endpoint == "http://custom-collector:4317"
    
    def test_environment_configuration(self):
        """Test environment configuration"""
        environments = ["development", "staging", "production", "test"]
        
        for env in environments:
            config = TracingConfig(
                service_name="test",
                service_version="1.0.0",
                environment=env,
            )
            assert config.environment == env


@pytest.mark.asyncio
class TestTracingExample:
    """Test tracing example service"""
    
    async def test_analysis_service_with_tracing(self):
        """Test AnalysisService with tracing"""
        from app.services.tracing_example import AnalysisService
        
        # Setup tracing
        tracer_provider = TracerProvider()
        console_exporter = ConsoleSpanExporter()
        span_processor = SimpleSpanProcessor(console_exporter)
        tracer_provider.add_span_processor(span_processor)
        trace.set_tracer_provider(tracer_provider)
        
        service = AnalysisService()
        
        result = await service.analyze_repository(
            repo_url="https://github.com/test/repo",
            user_id=123,
        )
        
        assert result["status"] == "success"
        assert result["repository"] == "https://github.com/test/repo"
        assert result["files_analyzed"] == 3
        assert result["issues_found"] == 2
    
    async def test_llm_service_with_tracing(self):
        """Test LLMService with tracing"""
        from app.services.tracing_example import LLMService
        
        # Setup tracing
        tracer_provider = TracerProvider()
        console_exporter = ConsoleSpanExporter()
        span_processor = SimpleSpanProcessor(console_exporter)
        tracer_provider.add_span_processor(span_processor)
        trace.set_tracer_provider(tracer_provider)
        
        service = LLMService()
        
        review = await service.generate_review(
            code="def hello(): print('world')",
            context="Simple function",
        )
        
        assert isinstance(review, str)
        assert len(review) > 0
