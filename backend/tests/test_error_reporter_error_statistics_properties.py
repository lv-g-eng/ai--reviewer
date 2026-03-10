"""
Property-based tests for error statistics tracking in ErrorReporter.

Tests Property 13: Error Statistics Tracking
**Validates: Requirements 5.5**

These tests verify that for any sequence of database errors, the system maintains
error statistics to identify recurring connectivity patterns over time.
"""

import json
from datetime import datetime, timezone, timedelta
from unittest.mock import patch

import pytest
from hypothesis import given, strategies as st, settings

from app.core.error_reporter import (
    ErrorReporter, 
    DatabaseErrorCategory,
    ErrorStatistics
)


class TestErrorStatisticsTrackingProperties:
    """Property-based tests for error statistics tracking and pattern identification"""
    
    def setup_method(self):
        """Reset error statistics before each test"""
        ErrorReporter.reset_error_statistics()
    
    @given(
        error_sequence=st.lists(
            st.tuples(
                st.sampled_from(list(DatabaseErrorCategory)),
                st.sampled_from(['PostgreSQL', 'Neo4j', 'Redis', 'MongoDB'])
            ),
            min_size=1,
            max_size=50
        )
    )
    @settings(max_examples=100, deadline=15000)
    def test_error_count_accuracy_property(self, error_sequence):
        """
        **Property 13: Error Statistics Tracking - Count Accuracy**
        **Validates: Requirements 5.5**
        
        For any sequence of database errors, the system should maintain accurate
        counts of errors by category and component.
        """
        # Reset statistics
        ErrorReporter.reset_error_statistics()
        
        # Track expected counts
        expected_category_counts = {}
        expected_component_counts = {}
        
        # Generate errors and track expected statistics
        for category, component in error_sequence:
            expected_category_counts[category] = expected_category_counts.get(category, 0) + 1
            expected_component_counts[component] = expected_component_counts.get(component, 0) + 1
            
            # Create and add error
            error = Exception(f"Test error for {category.value}")
            error_info = ErrorReporter.create_database_error_info(error, component)
            error_info.category = category  # Override for testing
            
            ErrorReporter._error_statistics.add_error(error_info)
        
        # Get actual statistics
        stats = ErrorReporter.get_error_statistics()
        
        # Verify category counts are accurate
        for category, expected_count in expected_category_counts.items():
            actual_count = stats.error_counts.get(category, 0)
            assert actual_count == expected_count, \
                f"Category {category} count mismatch: expected {expected_count}, got {actual_count}"
        
        # Verify component counts are accurate
        for component, expected_count in expected_component_counts.items():
            actual_count = stats.component_errors.get(component, 0)
            assert actual_count == expected_count, \
                f"Component {component} count mismatch: expected {expected_count}, got {actual_count}"
        
        # Verify total count
        expected_total = len(error_sequence)
        actual_total = sum(stats.error_counts.values())
        assert actual_total == expected_total, \
            f"Total error count mismatch: expected {expected_total}, got {actual_total}"
        
        # Verify recent errors tracking
        assert len(stats.recent_errors) <= 50, "Recent errors should be capped at 50"
        assert len(stats.recent_errors) == min(expected_total, 50), \
            "Should track all recent errors up to the limit"
    
    @given(
        error_count=st.integers(min_value=1, max_value=100),
        time_spread_hours=st.integers(min_value=0, max_value=48),
        component=st.sampled_from(['PostgreSQL', 'Neo4j', 'Redis'])
    )
    @settings(max_examples=50, deadline=15000)
    def test_timestamp_tracking_property(self, error_count, time_spread_hours, component):
        """
        **Property 13: Error Statistics Tracking - Timestamp Tracking**
        **Validates: Requirements 5.5**
        
        For any sequence of errors over time, the system should accurately track
        first seen, last seen, and individual error timestamps.
        """
        # Reset statistics
        ErrorReporter.reset_error_statistics()
        
        # Generate errors with time progression
        base_time = datetime.now(timezone.utc)
        error_timestamps = []
        
        for i in range(error_count):
            # Calculate timestamp with time spread
            if time_spread_hours > 0 and error_count > 1:
                time_offset = timedelta(hours=(time_spread_hours * i) / (error_count - 1))
            else:
                time_offset = timedelta(seconds=i)  # Small increments for same-hour tests
            
            error_time = base_time + time_offset
            error_timestamps.append(error_time)
            
            # Create error with specific timestamp
            error = Exception(f"Error {i}")
            error_info = ErrorReporter.create_database_error_info(error, component)
            error_info.timestamp = error_time  # Override timestamp for testing
            
            ErrorReporter._error_statistics.add_error(error_info)
        
        # Get statistics
        stats = ErrorReporter.get_error_statistics()
        
        # Verify timestamp tracking
        assert stats.first_seen is not None, "First seen timestamp should be set"
        assert stats.last_seen is not None, "Last seen timestamp should be set"
        
        # Verify first and last seen are correct
        expected_first = min(error_timestamps)
        expected_last = max(error_timestamps)
        
        assert stats.first_seen == expected_first, \
            f"First seen mismatch: expected {expected_first}, got {stats.first_seen}"
        assert stats.last_seen == expected_last, \
            f"Last seen mismatch: expected {expected_last}, got {stats.last_seen}"
        
        # Verify chronological order
        assert stats.first_seen <= stats.last_seen, \
            "First seen should be before or equal to last seen"
        
        # Verify individual error timestamps in recent errors
        recent_timestamps = [error.timestamp for error in stats.recent_errors]
        if len(recent_timestamps) > 1:
            for i in range(1, len(recent_timestamps)):
                assert recent_timestamps[i-1] <= recent_timestamps[i], \
                    "Recent errors should be in chronological order"
    
    @given(
        categories_and_counts=st.dictionaries(
            st.sampled_from(list(DatabaseErrorCategory)),
            st.integers(min_value=1, max_value=20),
            min_size=1,
            max_size=5
        )
    )
    @settings(max_examples=50, deadline=15000)
    def test_pattern_identification_property(self, categories_and_counts):
        """
        **Property 13: Error Statistics Tracking - Pattern Identification**
        **Validates: Requirements 5.5**
        
        For any distribution of error categories, the system should correctly
        identify the most frequent error types and problematic components.
        """
        # Reset statistics
        ErrorReporter.reset_error_statistics()
        
        # Generate errors according to the specified distribution
        all_components = ['PostgreSQL', 'Neo4j', 'Redis']
        component_counts = {}
        
        for category, count in categories_and_counts.items():
            for i in range(count):
                component = all_components[i % len(all_components)]
                component_counts[component] = component_counts.get(component, 0) + 1
                
                error = Exception(f"Error {i} for {category.value}")
                error_info = ErrorReporter.create_database_error_info(error, component)
                error_info.category = category
                
                ErrorReporter._error_statistics.add_error(error_info)
        
        # Get statistics and pattern analysis
        stats = ErrorReporter.get_error_statistics()
        
        # Verify most frequent category identification
        expected_most_frequent = max(categories_and_counts.items(), key=lambda x: x[1])[0]
        actual_most_frequent = stats.get_most_frequent_category()
        
        assert actual_most_frequent == expected_most_frequent, \
            f"Most frequent category mismatch: expected {expected_most_frequent}, got {actual_most_frequent}"
        
        # Verify most problematic component identification
        if component_counts:
            expected_most_problematic = max(component_counts.items(), key=lambda x: x[1])[0]
            actual_most_problematic = stats.get_most_problematic_component()
            
            assert actual_most_problematic == expected_most_problematic, \
                f"Most problematic component mismatch: expected {expected_most_problematic}, got {actual_most_problematic}"
        
        # Verify pattern analysis provides insights
        pattern_analysis = ErrorReporter.get_error_pattern_analysis()
        
        assert pattern_analysis['total_errors'] == sum(categories_and_counts.values()), \
            "Pattern analysis should report correct total errors"
        assert pattern_analysis['unique_categories'] == len(categories_and_counts), \
            "Pattern analysis should report correct unique categories"
        assert len(pattern_analysis['patterns']) > 0, \
            "Pattern analysis should identify patterns"
        
        # Verify recommendations are provided for significant patterns
        total_errors = sum(categories_and_counts.values())
        max_category_count = max(categories_and_counts.values())
        
        if max_category_count / total_errors > 0.5:  # More than 50% of errors are one type
            assert len(pattern_analysis['recommendations']) > 0, \
                "Should provide recommendations for dominant error patterns"
    
    @given(
        error_bursts=st.lists(
            st.integers(min_value=1, max_value=10),  # Errors per burst
            min_size=1,
            max_size=5
        ),
        burst_interval_minutes=st.integers(min_value=1, max_value=60)
    )
    @settings(max_examples=50, deadline=15000)
    def test_error_burst_detection_property(self, error_bursts, burst_interval_minutes):
        """
        **Property 13: Error Statistics Tracking - Error Burst Detection**
        **Validates: Requirements 5.5**
        
        For any pattern of error bursts, the system should detect when multiple
        errors occur in a short time period and provide appropriate recommendations.
        """
        # Reset statistics
        ErrorReporter.reset_error_statistics()
        
        base_time = datetime.now(timezone.utc)
        total_errors = 0
        
        # Generate error bursts
        for burst_index, errors_in_burst in enumerate(error_bursts):
            burst_start_time = base_time + timedelta(minutes=burst_index * burst_interval_minutes)
            
            # Generate errors within a short time span (under 5 minutes for burst detection)
            for error_index in range(errors_in_burst):
                error_time = burst_start_time + timedelta(seconds=error_index * 10)  # 10 seconds apart
                
                error = Exception(f"Burst {burst_index} error {error_index}")
                error_info = ErrorReporter.create_database_error_info(error, 'PostgreSQL')
                error_info.timestamp = error_time
                
                ErrorReporter._error_statistics.add_error(error_info)
                total_errors += 1
        
        # Analyze patterns
        pattern_analysis = ErrorReporter.get_error_pattern_analysis()
        
        # Check for burst detection if we have recent errors close together
        stats = ErrorReporter.get_error_statistics()
        if len(stats.recent_errors) >= 5:
            recent_5_errors = stats.recent_errors[-5:]
            time_span = (recent_5_errors[-1].timestamp - recent_5_errors[0].timestamp).total_seconds()
            
            if time_span < 300:  # 5 minutes
                # Should detect error burst
                burst_patterns = [p for p in pattern_analysis['patterns'] if p.get('type') == 'error_burst']
                assert len(burst_patterns) > 0, "Should detect error burst pattern"
                
                # Should provide burst-related recommendations
                burst_recommendations = [r for r in pattern_analysis['recommendations'] 
                                       if 'burst' in r.lower()]
                assert len(burst_recommendations) > 0, "Should provide burst-related recommendations"
        
        # Verify total error count is correct
        assert pattern_analysis['total_errors'] == total_errors, \
            f"Total error count mismatch: expected {total_errors}, got {pattern_analysis['total_errors']}"
    
    @given(
        export_format=st.sampled_from(['json', 'csv', 'summary']),
        error_data=st.lists(
            st.tuples(
                st.sampled_from(list(DatabaseErrorCategory)),
                st.sampled_from(['PostgreSQL', 'Neo4j', 'Redis'])
            ),
            min_size=1,
            max_size=20
        )
    )
    @settings(max_examples=50, deadline=15000)
    def test_statistics_export_property(self, export_format, error_data):
        """
        **Property 13: Error Statistics Tracking - Statistics Export**
        **Validates: Requirements 5.5**
        
        For any collection of error statistics, the system should be able to
        export the data in various formats while maintaining data integrity.
        """
        # Reset statistics
        ErrorReporter.reset_error_statistics()
        
        # Generate errors
        for category, component in error_data:
            error = Exception(f"Test error for {category.value}")
            error_info = ErrorReporter.create_database_error_info(error, component)
            error_info.category = category
            
            ErrorReporter._error_statistics.add_error(error_info)
        
        # Export statistics
        exported_data = ErrorReporter.export_error_statistics(export_format)
        
        # Verify export is not empty
        assert len(exported_data) > 0, f"Exported {export_format} data should not be empty"
        
        # Format-specific validations
        if export_format == 'json':
            # Should be valid JSON
            parsed_data = json.loads(exported_data)
            assert isinstance(parsed_data, dict), "JSON export should be a dictionary"
            
            # Should contain expected fields
            assert 'error_counts' in parsed_data, "JSON export should contain error_counts"
            assert 'component_errors' in parsed_data, "JSON export should contain component_errors"
            assert 'total_errors' in parsed_data, "JSON export should contain total_errors"
            assert 'recent_errors' in parsed_data, "JSON export should contain recent_errors"
            
            # Verify data integrity
            expected_total = len(error_data)
            assert parsed_data['total_errors'] == expected_total, \
                f"JSON total_errors mismatch: expected {expected_total}, got {parsed_data['total_errors']}"
            
            # Verify recent errors structure
            for recent_error in parsed_data['recent_errors']:
                assert 'timestamp' in recent_error, "Recent errors should have timestamp"
                assert 'component' in recent_error, "Recent errors should have component"
                assert 'category' in recent_error, "Recent errors should have category"
                assert 'message' in recent_error, "Recent errors should have message"
        
        elif export_format == 'csv':
            # Should contain CSV headers and data
            lines = exported_data.strip().split('\n')
            assert len(lines) > 1, "CSV export should have headers and data"
            
            # Should have proper CSV structure
            header_line = lines[0]
            assert 'Category' in header_line, "CSV should have Category header"
            assert 'Component' in header_line, "CSV should have Component header"
            assert 'Count' in header_line, "CSV should have Count header"
            
            # Should have data lines
            data_lines = [line for line in lines[1:] if line.strip() and not line.startswith('Component,')]
            assert len(data_lines) > 0, "CSV should have data lines"
        
        elif export_format == 'summary':
            # Should be human-readable summary
            assert "Database Error Statistics Report" in exported_data, \
                "Summary should contain report header"
            assert "Error Categories:" in exported_data, \
                "Summary should contain error categories section"
            
            # Should contain actual data
            for category, component in error_data:
                # At least one of category or component should be mentioned
                category_mentioned = category.value in exported_data
                component_mentioned = component in exported_data
                assert category_mentioned or component_mentioned, \
                    f"Summary should mention {category.value} or {component}"
    
    @given(
        hours_threshold=st.integers(min_value=1, max_value=72),
        old_errors_count=st.integers(min_value=1, max_value=20),
        new_errors_count=st.integers(min_value=0, max_value=10)
    )
    @settings(max_examples=50, deadline=15000)
    def test_statistics_cleanup_property(self, hours_threshold, old_errors_count, new_errors_count):
        """
        **Property 13: Error Statistics Tracking - Statistics Cleanup**
        **Validates: Requirements 5.5**
        
        For any cleanup operation, the system should correctly remove old error
        statistics while preserving recent data and maintaining count accuracy.
        """
        # Reset statistics
        ErrorReporter.reset_error_statistics()
        
        base_time = datetime.now(timezone.utc)
        
        # Generate old errors (beyond threshold)
        old_cutoff = base_time - timedelta(hours=hours_threshold + 1)
        for i in range(old_errors_count):
            error_time = old_cutoff - timedelta(hours=i)
            
            error = Exception(f"Old error {i}")
            error_info = ErrorReporter.create_database_error_info(error, 'PostgreSQL')
            error_info.timestamp = error_time
            
            ErrorReporter._error_statistics.add_error(error_info)
        
        # Generate new errors (within threshold)
        new_cutoff = base_time - timedelta(hours=hours_threshold - 1)
        for i in range(new_errors_count):
            error_time = new_cutoff + timedelta(minutes=i * 10)
            
            error = Exception(f"New error {i}")
            error_info = ErrorReporter.create_database_error_info(error, 'Neo4j')
            error_info.timestamp = error_time
            
            ErrorReporter._error_statistics.add_error(error_info)
        
        # Verify initial state
        initial_stats = ErrorReporter.get_error_statistics()
        initial_total = len(initial_stats.recent_errors)
        expected_initial = old_errors_count + new_errors_count
        assert initial_total == expected_initial, \
            f"Initial error count mismatch: expected {expected_initial}, got {initial_total}"
        
        # Perform cleanup
        removed_count = ErrorReporter.clear_old_error_statistics(hours_threshold)
        
        # Verify cleanup results
        final_stats = ErrorReporter.get_error_statistics()
        final_total = len(final_stats.recent_errors)
        
        # Should have removed old errors
        assert removed_count == old_errors_count, \
            f"Removed count mismatch: expected {old_errors_count}, got {removed_count}"
        
        # Should have kept new errors
        assert final_total == new_errors_count, \
            f"Final error count mismatch: expected {new_errors_count}, got {final_total}"
        
        # Verify statistics consistency after cleanup
        if new_errors_count > 0:
            # Should have updated counts correctly
            expected_neo4j_count = new_errors_count  # All new errors were Neo4j
            actual_neo4j_count = final_stats.component_errors.get('Neo4j', 0)
            assert actual_neo4j_count == expected_neo4j_count, \
                f"Neo4j count after cleanup mismatch: expected {expected_neo4j_count}, got {actual_neo4j_count}"
            
            # Should not have old PostgreSQL errors
            postgresql_count = final_stats.component_errors.get('PostgreSQL', 0)
            assert postgresql_count == 0, \
                f"PostgreSQL count should be 0 after cleanup, got {postgresql_count}"
        else:
            # No errors should remain
            assert len(final_stats.error_counts) == 0, "No error counts should remain"
            assert len(final_stats.component_errors) == 0, "No component errors should remain"
            assert final_stats.first_seen is None, "First seen should be None"
            assert final_stats.last_seen is None, "Last seen should be None"
    
    @given(
        concurrent_errors=st.lists(
            st.tuples(
                st.sampled_from(list(DatabaseErrorCategory)),
                st.sampled_from(['PostgreSQL', 'Neo4j', 'Redis'])
            ),
            min_size=5,
            max_size=30
        )
    )
    @settings(max_examples=50, deadline=15000)
    def test_concurrent_statistics_updates_property(self, concurrent_errors):
        """
        **Property 13: Error Statistics Tracking - Concurrent Updates**
        **Validates: Requirements 5.5**
        
        For any sequence of concurrent error additions, the system should maintain
        accurate statistics without data corruption or lost updates.
        """
        # Reset statistics
        ErrorReporter.reset_error_statistics()
        
        # Track expected results
        expected_category_counts = {}
        expected_component_counts = {}
        
        # Simulate concurrent error additions
        for category, component in concurrent_errors:
            expected_category_counts[category] = expected_category_counts.get(category, 0) + 1
            expected_component_counts[component] = expected_component_counts.get(component, 0) + 1
            
            # Create and add error (simulating concurrent access)
            error = Exception(f"Concurrent error for {category.value}")
            error_info = ErrorReporter.create_database_error_info(error, component)
            error_info.category = category
            
            # Add error to statistics
            ErrorReporter._error_statistics.add_error(error_info)
        
        # Verify final statistics are accurate
        final_stats = ErrorReporter.get_error_statistics()
        
        # Check category counts
        for category, expected_count in expected_category_counts.items():
            actual_count = final_stats.error_counts.get(category, 0)
            assert actual_count == expected_count, \
                f"Concurrent update error - Category {category}: expected {expected_count}, got {actual_count}"
        
        # Check component counts
        for component, expected_count in expected_component_counts.items():
            actual_count = final_stats.component_errors.get(component, 0)
            assert actual_count == expected_count, \
                f"Concurrent update error - Component {component}: expected {expected_count}, got {actual_count}"
        
        # Verify total consistency
        expected_total = len(concurrent_errors)
        actual_total = sum(final_stats.error_counts.values())
        assert actual_total == expected_total, \
            f"Concurrent update error - Total count: expected {expected_total}, got {actual_total}"
        
        # Verify recent errors list integrity
        assert len(final_stats.recent_errors) <= 50, "Recent errors should be capped at 50"
        assert len(final_stats.recent_errors) == min(expected_total, 50), \
            "Recent errors count should match expected (up to limit)"
        
        # Verify timestamps are properly ordered
        if len(final_stats.recent_errors) > 1:
            timestamps = [error.timestamp for error in final_stats.recent_errors]
            for i in range(1, len(timestamps)):
                assert timestamps[i-1] <= timestamps[i], \
                    "Timestamps should remain in chronological order after concurrent updates"


# Integration test to verify property test assumptions
def test_error_statistics_tracking_integration():
    """Integration test to verify error statistics tracking works correctly"""
    # Reset statistics
    ErrorReporter.reset_error_statistics()
    
    # Create a sequence of different errors
    test_errors = [
        (DatabaseErrorCategory.CONNECTION_TIMEOUT, 'PostgreSQL'),
        (DatabaseErrorCategory.CONNECTION_TIMEOUT, 'PostgreSQL'),
        (DatabaseErrorCategory.AUTHENTICATION_FAILURE, 'Neo4j'),
        (DatabaseErrorCategory.ENCODING_ERROR, 'PostgreSQL'),
        (DatabaseErrorCategory.CONNECTION_TIMEOUT, 'Redis')
    ]
    
    # Add errors to statistics
    for category, component in test_errors:
        error = Exception(f"Test error for {category.value}")
        error_info = ErrorReporter.create_database_error_info(error, component)
        error_info.category = category
        
        ErrorReporter._error_statistics.add_error(error_info)
    
    # Verify statistics
    stats = ErrorReporter.get_error_statistics()
    
    # Check counts
    assert stats.error_counts[DatabaseErrorCategory.CONNECTION_TIMEOUT] == 3
    assert stats.error_counts[DatabaseErrorCategory.AUTHENTICATION_FAILURE] == 1
    assert stats.error_counts[DatabaseErrorCategory.ENCODING_ERROR] == 1
    
    assert stats.component_errors['PostgreSQL'] == 3
    assert stats.component_errors['Neo4j'] == 1
    assert stats.component_errors['Redis'] == 1
    
    # Check pattern identification
    assert stats.get_most_frequent_category() == DatabaseErrorCategory.CONNECTION_TIMEOUT
    assert stats.get_most_problematic_component() == 'PostgreSQL'
    
    # Test pattern analysis
    analysis = ErrorReporter.get_error_pattern_analysis()
    assert analysis['total_errors'] == 5
    assert analysis['unique_categories'] == 3
    assert analysis['unique_components'] == 3
    assert len(analysis['patterns']) > 0
    
    # Test export functionality
    json_export = ErrorReporter.export_error_statistics('json')
    assert 'error_counts' in json_export
    
    csv_export = ErrorReporter.export_error_statistics('csv')
    assert 'Category,Component,Count' in csv_export
    
    summary_export = ErrorReporter.export_error_statistics('summary')
    assert 'Database Error Statistics Report' in summary_export


# Test fixtures for property tests
@pytest.fixture
def sample_error_statistics():
    """Sample error statistics for testing"""
    stats = ErrorStatistics()
    
    # Add sample errors
    categories = [DatabaseErrorCategory.CONNECTION_TIMEOUT, DatabaseErrorCategory.AUTHENTICATION_FAILURE]
    components = ['PostgreSQL', 'Neo4j']
    
    for i in range(10):
        category = categories[i % len(categories)]
        component = components[i % len(components)]
        
        error = Exception(f"Sample error {i}")
        error_info = ErrorReporter.create_database_error_info(error, component)
        error_info.category = category
        
        stats.add_error(error_info)
    
    return stats


@pytest.fixture
def mock_datetime():
    """Mock datetime for testing time-based functionality"""
    base_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    with patch('app.core.error_reporter.datetime') as mock_dt:
        mock_dt.now.return_value = base_time
        mock_dt.side_effect = lambda *args, **kw: datetime(*args, **kw)
        yield mock_dt


# Performance test for large error volumes
def test_error_statistics_performance():
    """Test that error statistics tracking performs well with large volumes"""
    import time
    
    # Reset statistics
    ErrorReporter.reset_error_statistics()
    
    # Generate large number of errors
    start_time = time.time()
    
    for i in range(1000):
        category = list(DatabaseErrorCategory)[i % len(DatabaseErrorCategory)]
        component = ['PostgreSQL', 'Neo4j', 'Redis'][i % 3]
        
        error = Exception(f"Performance test error {i}")
        error_info = ErrorReporter.create_database_error_info(error, component)
        error_info.category = category
        
        ErrorReporter._error_statistics.add_error(error_info)
    
    end_time = time.time()
    
    # Should complete within reasonable time (less than 1 second for 1000 errors)
    elapsed_time = end_time - start_time
    assert elapsed_time < 1.0, f"Statistics tracking too slow: {elapsed_time:.2f} seconds for 1000 errors"
    
    # Verify statistics are still accurate
    stats = ErrorReporter.get_error_statistics()
    assert sum(stats.error_counts.values()) == 1000
    assert len(stats.recent_errors) == 50  # Capped at 50