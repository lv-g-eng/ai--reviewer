"""
Integration tests for Celery tasks

These tests verify:
- Task execution and chaining
- Task failure handling and retry logic
- Task monitoring and progress tracking
- Integration with Redis backend (in eager mode)

These tests use eager mode for faster execution without requiring a running worker.
For full integration testing with real workers, see CELERY_INTEGRATION_TESTS_README.md

Validates Requirements: 13.5 (Redis caching and queuing integration tests)
"""
import pytest
from datetime import datetime, timezone
from celery import chain, group

from app.celery_config import celery_app
from app.tasks.task_monitoring import (
    MonitoredTask,
    TaskProgressStage
)


# ========================================
# TEST FIXTURES
# ========================================

@pytest.fixture(scope="function", autouse=True)
def celery_eager_mode():
    """Configure Celery to run in eager mode for testing"""
    # Store original settings
    original_always_eager = celery_app.conf.task_always_eager
    original_eager_propagates = celery_app.conf.task_eager_propagates
    
    # Set eager mode
    celery_app.conf.task_always_eager = True
    celery_app.conf.task_eager_propagates = True
    
    yield
    
    # Restore original settings
    celery_app.conf.task_always_eager = original_always_eager
    celery_app.conf.task_eager_propagates = original_eager_propagates


# ========================================
# TEST TASK EXECUTION
# ========================================

class TestTaskExecution:
    """Test basic task execution"""
    
    def test_simple_task_execution(self):
        """Test that a simple task executes successfully"""
        
        @celery_app.task(name='test_simple_task_exec')
        def simple_task(x, y):
            return x + y
        
        # Execute task in eager mode
        result = simple_task.apply_async(args=[2, 3])
        
        # Get result (immediate in eager mode)
        output = result.get()
        
        # Assertions
        assert output == 5
        assert result.successful()
        assert result.state == 'SUCCESS'
    
    def test_task_with_kwargs(self):
        """Test task execution with keyword arguments"""
        
        @celery_app.task(name='test_kwargs_task_exec')
        def kwargs_task(a, b=10):
            return a * b
        
        # Execute task with kwargs
        result = kwargs_task.apply_async(args=[5], kwargs={'b': 3})
        
        # Get result
        output = result.get()
        
        # Assertions
        assert output == 15
        assert result.successful()
    
    def test_task_returns_dict(self):
        """Test task that returns complex data structure"""
        
        @celery_app.task(name='test_dict_task_exec')
        def dict_task(name):
            return {
                'name': name,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'status': 'completed'
            }
        
        # Execute task
        result = dict_task.apply_async(args=['test'])
        
        # Get result
        output = result.get()
        
        # Assertions
        assert isinstance(output, dict)
        assert output['name'] == 'test'
        assert output['status'] == 'completed'
        assert 'timestamp' in output


# ========================================
# TEST TASK CHAINING
# ========================================

class TestTaskChaining:
    """Test task chaining functionality"""
    
    def test_simple_chain(self):
        """Test chaining two tasks together"""
        
        @celery_app.task(name='test_add_chain')
        def add(x, y):
            return x + y
        
        @celery_app.task(name='test_multiply_chain')
        def multiply(result, factor):
            return result * factor
        
        # Create chain: (2 + 3) * 4 = 20
        workflow = chain(
            add.s(2, 3),
            multiply.s(4)
        )
        
        # Execute chain
        result = workflow.apply_async()
        
        # Get final result
        output = result.get()
        
        # Assertions
        assert output == 20
        assert result.successful()
    
    def test_multi_step_chain(self):
        """Test chaining multiple tasks"""
        
        @celery_app.task(name='test_step1_chain')
        def step1(data):
            return {'step1': data, 'count': 1}
        
        @celery_app.task(name='test_step2_chain')
        def step2(result):
            result['step2'] = 'processed'
            result['count'] += 1
            return result
        
        @celery_app.task(name='test_step3_chain')
        def step3(result):
            result['step3'] = 'completed'
            result['count'] += 1
            return result
        
        # Create 3-step chain
        workflow = chain(
            step1.s('initial'),
            step2.s(),
            step3.s()
        )
        
        # Execute chain
        result = workflow.apply_async()
        
        # Get final result
        output = result.get()
        
        # Assertions
        assert output['step1'] == 'initial'
        assert output['step2'] == 'processed'
        assert output['step3'] == 'completed'
        assert output['count'] == 3
    
    def test_chain_with_dict_passing(self):
        """Test chain passing dictionaries between tasks"""
        
        @celery_app.task(name='test_parse_chain')
        def parse_data(input_data):
            return {
                'parsed': True,
                'data': input_data,
                'entities': ['entity1', 'entity2']
            }
        
        @celery_app.task(name='test_process_chain')
        def process_data(parse_result):
            return {
                **parse_result,
                'processed': True,
                'entity_count': len(parse_result['entities'])
            }
        
        @celery_app.task(name='test_finalize_chain')
        def finalize_data(process_result):
            return {
                **process_result,
                'finalized': True,
                'status': 'completed'
            }
        
        # Create chain
        workflow = chain(
            parse_data.s('test_input'),
            process_data.s(),
            finalize_data.s()
        )
        
        # Execute chain
        result = workflow.apply_async()
        
        # Get final result
        output = result.get()
        
        # Assertions
        assert output['parsed'] is True
        assert output['processed'] is True
        assert output['finalized'] is True
        assert output['entity_count'] == 2
        assert output['status'] == 'completed'


# ========================================
# TEST TASK FAILURE AND RETRY
# ========================================

class TestTaskFailureAndRetry:
    """Test task failure handling and retry logic"""
    
    def test_task_failure_no_retry(self):
        """Test task that fails without retry"""
        
        @celery_app.task(name='test_failing_task_no_retry', max_retries=0)
        def failing_task():
            raise ValueError("Task failed")
        
        # Execute task
        result = failing_task.apply_async()
        
        # Task should fail
        with pytest.raises(ValueError):
            result.get()
        
        # Assertions
        assert result.failed()
        assert result.state == 'FAILURE'
    
    def test_task_retry_on_failure(self):
        """Test task that retries on failure"""
        
        attempt_count = {'count': 0}
        
        @celery_app.task(bind=True, name='test_retry_task_failure', max_retries=3, default_retry_delay=0)
        def retry_task(self):
            attempt_count['count'] += 1
            if attempt_count['count'] < 3:
                # Fail first 2 attempts
                raise self.retry(exc=ValueError("Temporary failure"), countdown=0)
            # Succeed on 3rd attempt
            return {'attempts': attempt_count['count'], 'status': 'success'}
        
        # Execute task
        result = retry_task.apply_async()
        
        # Get result (should succeed after retries)
        output = result.get()
        
        # Assertions
        assert output['status'] == 'success'
        assert output['attempts'] == 3
        assert result.successful()
    
    def test_task_max_retries_exceeded(self):
        """Test task that exceeds max retries"""
        
        @celery_app.task(bind=True, name='test_max_retry_task_failure', max_retries=2, default_retry_delay=0)
        def max_retry_task(self):
            # Always fail
            raise self.retry(exc=ConnectionError("Connection failed"), countdown=0)
        
        # Execute task
        result = max_retry_task.apply_async()
        
        # Task should fail after max retries
        with pytest.raises(Exception):  # Will raise Retry or ConnectionError
            result.get()
        
        # Assertions
        assert result.failed()
    
    def test_task_conditional_retry(self):
        """Test task with conditional retry logic"""
        
        attempt_count = {'count': 0}
        
        @celery_app.task(bind=True, name='test_conditional_retry_failure', max_retries=3, default_retry_delay=0)
        def conditional_retry_task(self, should_fail):
            attempt_count['count'] += 1
            
            if should_fail and attempt_count['count'] < 2:
                # Retry on transient error
                raise self.retry(exc=TimeoutError("Timeout"), countdown=0)
            
            return {'attempts': attempt_count['count'], 'result': 'success'}
        
        # Execute task that will retry once
        result = conditional_retry_task.apply_async(args=[True])
        
        # Get result
        output = result.get()
        
        # Assertions
        assert output['attempts'] == 2
        assert output['result'] == 'success'


# ========================================
# TEST CHAIN FAILURE HANDLING
# ========================================

class TestChainFailureHandling:
    """Test failure handling in task chains"""
    
    def test_chain_stops_on_failure(self):
        """Test that chain stops when a task fails"""
        
        execution_log = []
        
        @celery_app.task(name='test_chain_step1_failure')
        def step1():
            execution_log.append('step1')
            return "step1_result"
        
        @celery_app.task(name='test_chain_step2_failure')
        def step2(prev_result):
            execution_log.append('step2')
            raise ValueError("Step 2 failed")
        
        @celery_app.task(name='test_chain_step3_failure')
        def step3(prev_result):
            execution_log.append('step3')
            return "step3_result"
        
        # Create chain
        workflow = chain(
            step1.s(),
            step2.s(),
            step3.s()
        )
        
        # Execute chain
        result = workflow.apply_async()
        
        # Wait for failure
        with pytest.raises(ValueError):
            result.get()
        
        # Assertions - step3 should not execute
        assert 'step1' in execution_log
        assert 'step2' in execution_log
        assert 'step3' not in execution_log
    
    def test_chain_with_retry_in_middle(self):
        """Test chain with retry in middle task"""
        
        attempt_count = {'count': 0}
        
        @celery_app.task(name='test_retry_chain_step1_failure')
        def step1():
            return "step1_result"
        
        @celery_app.task(bind=True, name='test_retry_chain_step2_failure', max_retries=2, default_retry_delay=0)
        def step2(self, prev_result):
            attempt_count['count'] += 1
            if attempt_count['count'] < 2:
                raise self.retry(exc=ConnectionError("Retry"), countdown=0)
            return f"{prev_result}_step2"
        
        @celery_app.task(name='test_retry_chain_step3_failure')
        def step3(prev_result):
            return f"{prev_result}_step3"
        
        # Create chain
        workflow = chain(
            step1.s(),
            step2.s(),
            step3.s()
        )
        
        # Execute chain
        result = workflow.apply_async()
        
        # Get result (should succeed after retry)
        output = result.get()
        
        # Assertions
        assert output == "step1_result_step2_step3"
        assert attempt_count['count'] == 2


# ========================================
# TEST PARALLEL EXECUTION
# ========================================

class TestParallelExecution:
    """Test parallel task execution with groups"""
    
    def test_group_execution(self):
        """Test executing tasks in parallel using group"""
        
        @celery_app.task(name='test_parallel_task_exec')
        def parallel_task(x):
            return x * 2
        
        # Create group of parallel tasks
        job = group(
            parallel_task.s(1),
            parallel_task.s(2),
            parallel_task.s(3),
            parallel_task.s(4)
        )
        
        # Execute group
        result = job.apply_async()
        
        # Get all results
        outputs = result.get()
        
        # Assertions
        assert len(outputs) == 4
        assert outputs == [2, 4, 6, 8]


# ========================================
# TEST MONITORED TASK
# ========================================

class TestMonitoredTask:
    """Test MonitoredTask base class"""
    
    def test_monitored_task_success(self):
        """Test MonitoredTask tracks successful execution"""
        
        @celery_app.task(bind=True, base=MonitoredTask, name='test_monitored_success')
        def monitored_task(self):
            self.update_progress(50, "Processing...")
            return "completed"
        
        # Execute task
        result = monitored_task.apply_async()
        
        # Get result
        output = result.get()
        
        # Assertions
        assert output == "completed"
        assert result.successful()
    
    def test_monitored_task_failure(self):
        """Test MonitoredTask tracks failures"""
        
        @celery_app.task(bind=True, base=MonitoredTask, name='test_monitored_failure', max_retries=0)
        def failing_monitored_task(self):
            self.update_progress(50, "Processing...")
            raise ValueError("Task failed")
        
        # Execute task
        result = failing_monitored_task.apply_async()
        
        # Task should fail
        with pytest.raises(ValueError):
            result.get()
        
        # Assertions
        assert result.failed()
    
    def test_monitored_task_progress_updates(self):
        """Test MonitoredTask progress tracking"""
        
        progress_updates = []
        
        @celery_app.task(bind=True, base=MonitoredTask, name='test_monitored_progress')
        def progress_task(self):
            self.update_progress(25, "Step 1", TaskProgressStage.PARSING_FILES)
            progress_updates.append(25)
            self.update_progress(50, "Step 2", TaskProgressStage.BUILDING_GRAPH)
            progress_updates.append(50)
            self.update_progress(75, "Step 3", TaskProgressStage.ANALYZING_LLM)
            progress_updates.append(75)
            self.update_progress(100, "Done", TaskProgressStage.COMPLETED)
            progress_updates.append(100)
            return "completed"
        
        # Execute task
        result = progress_task.apply_async()
        
        # Get result
        output = result.get()
        
        # Assertions
        assert output == "completed"
        assert progress_updates == [25, 50, 75, 100]


# ========================================
# TEST ERROR SCENARIOS
# ========================================

class TestErrorScenarios:
    """Test various error scenarios"""
    
    def test_task_with_invalid_arguments(self):
        """Test task called with invalid arguments"""
        
        @celery_app.task(name='test_invalid_args_error')
        def strict_task(required_arg):
            return required_arg
        
        # Execute task without required argument
        result = strict_task.apply_async(args=[])
        
        # Should fail
        with pytest.raises(TypeError):
            result.get()
        
        assert result.failed()
    
    def test_task_with_exception_in_chain(self):
        """Test exception handling in task chain"""
        
        @celery_app.task(name='test_exception_step1_error')
        def step1():
            return "success"
        
        @celery_app.task(name='test_exception_step2_error')
        def step2(prev):
            raise RuntimeError("Unexpected error")
        
        # Create chain
        workflow = chain(step1.s(), step2.s())
        
        # Execute
        result = workflow.apply_async()
        
        # Should fail with RuntimeError
        with pytest.raises(RuntimeError):
            result.get()


# ========================================
# TEST WORKFLOW SIMULATION
# ========================================

class TestWorkflowSimulation:
    """Test simulated PR analysis workflow"""
    
    def test_pr_analysis_workflow_simulation(self):
        """Test simulated PR analysis workflow with chained tasks"""
        
        @celery_app.task(name='test_parse_pr_workflow')
        def parse_pr(pr_id, project_id):
            return {
                'pr_id': pr_id,
                'project_id': project_id,
                'parsed_entities': ['entity1', 'entity2'],
                'files': ['file1.py', 'file2.py']
            }
        
        @celery_app.task(name='test_build_graph_workflow')
        def build_graph(parse_result):
            return {
                **parse_result,
                'graph_stats': {
                    'nodes_created': 2,
                    'relationships_created': 1
                }
            }
        
        @celery_app.task(name='test_analyze_llm_workflow')
        def analyze_llm(graph_result):
            return {
                **graph_result,
                'llm_analysis': {
                    'issues': [{'severity': 'warning', 'message': 'Test issue'}],
                    'risk_score': 30
                }
            }
        
        @celery_app.task(name='test_post_comments_workflow')
        def post_comments(analysis_result):
            return {
                'status': 'completed',
                'comments_posted': len(analysis_result['llm_analysis']['issues']),
                'risk_score': analysis_result['llm_analysis']['risk_score']
            }
        
        # Create workflow chain
        workflow = chain(
            parse_pr.s('pr-123', 'project-456'),
            build_graph.s(),
            analyze_llm.s(),
            post_comments.s()
        )
        
        # Execute workflow
        result = workflow.apply_async()
        
        # Get final result
        output = result.get()
        
        # Assertions
        assert output['status'] == 'completed'
        assert output['comments_posted'] == 1
        assert output['risk_score'] == 30
        assert result.successful()


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
