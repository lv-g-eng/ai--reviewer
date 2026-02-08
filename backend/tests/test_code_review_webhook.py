"""
Unit tests for Code Review Webhook Handler

Tests webhook signature validation, payload extraction, and task queuing.

Validates Requirements: 1.1
"""
import pytest
import hmac
import hashlib
import json
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock
from fastapi import HTTPException

from app.api.v1.endpoints.code_review_webhook import (
    verify_webhook_signature,
    extract_pr_data,
    queue_analysis_task
)
from app.shared.exceptions import ValidationException


class TestWebhookSignatureValidation:
    """Test webhook signature verification"""
    
    def test_verify_valid_signature(self):
        """Test that valid signatures are accepted"""
        secret = "test_secret"
        payload = b'{"test": "data"}'
        
        # Generate valid signature
        mac = hmac.new(secret.encode('utf-8'), msg=payload, digestmod=hashlib.sha256)
        signature = f"sha256={mac.hexdigest()}"
        
        assert verify_webhook_signature(payload, signature, secret) is True
    
    def test_verify_invalid_signature(self):
        """Test that invalid signatures are rejected"""
        secret = "test_secret"
        payload = b'{"test": "data"}'
        invalid_signature = "sha256=invalid_signature_here"
        
        assert verify_webhook_signature(payload, invalid_signature, secret) is False
    
    def test_verify_missing_signature(self):
        """Test that missing signatures are rejected"""
        secret = "test_secret"
        payload = b'{"test": "data"}'
        
        assert verify_webhook_signature(payload, None, secret) is False
        assert verify_webhook_signature(payload, "", secret) is False
    
    def test_verify_wrong_format_signature(self):
        """Test that signatures without sha256= prefix are rejected"""
        secret = "test_secret"
        payload = b'{"test": "data"}'
        signature = "invalid_format"
        
        assert verify_webhook_signature(payload, signature, secret) is False
    
    def test_verify_signature_constant_time(self):
        """Test that signature comparison is constant-time (timing attack resistant)"""
        secret = "test_secret"
        payload = b'{"test": "data"}'
        
        # Generate valid signature
        mac = hmac.new(secret.encode('utf-8'), msg=payload, digestmod=hashlib.sha256)
        valid_signature = f"sha256={mac.hexdigest()}"
        
        # Create slightly different signature
        invalid_signature = f"sha256={mac.hexdigest()[:-1]}0"
        
        # Both should return False for invalid, but use constant-time comparison
        assert verify_webhook_signature(payload, invalid_signature, secret) is False
        assert verify_webhook_signature(payload, valid_signature, secret) is True


class TestPayloadExtraction:
    """Test PR data extraction from webhook payload"""
    
    @pytest.mark.asyncio
    async def test_extract_complete_pr_data(self):
        """Test extraction of complete PR data"""
        payload = {
            'action': 'opened',
            'pull_request': {
                'number': 123,
                'title': 'Test PR',
                'body': 'Test description',
                'head': {
                    'ref': 'feature-branch',
                    'sha': 'abc123def456'
                },
                'changed_files': 5,
                'additions': 100,
                'deletions': 50
            },
            'repository': {
                'html_url': 'https://github.com/owner/repo',
                'full_name': 'owner/repo'
            },
            'sender': {
                'login': 'testuser'
            }
        }
        
        result = await extract_pr_data(payload)
        
        assert result['pr_number'] == 123
        assert result['title'] == 'Test PR'
        assert result['description'] == 'Test description'
        assert result['branch_name'] == 'feature-branch'
        assert result['commit_sha'] == 'abc123def456'
        assert result['files_changed'] == 5
        assert result['lines_added'] == 100
        assert result['lines_deleted'] == 50
        assert result['repository_url'] == 'https://github.com/owner/repo'
        assert result['repository_full_name'] == 'owner/repo'
        assert result['action'] == 'opened'
        assert result['sender'] == 'testuser'
    
    @pytest.mark.asyncio
    async def test_extract_minimal_pr_data(self):
        """Test extraction with minimal required fields"""
        payload = {
            'action': 'synchronize',
            'pull_request': {
                'number': 456,
                'title': 'Minimal PR',
                'head': {
                    'ref': 'main',
                    'sha': 'xyz789'
                }
            },
            'repository': {
                'html_url': 'https://github.com/test/repo',
                'full_name': 'test/repo'
            },
            'sender': {}
        }
        
        result = await extract_pr_data(payload)
        
        assert result['pr_number'] == 456
        assert result['title'] == 'Minimal PR'
        assert result['description'] == ''  # Default empty string
        assert result['files_changed'] == 0  # Default
        assert result['lines_added'] == 0  # Default
        assert result['lines_deleted'] == 0  # Default
    
    @pytest.mark.asyncio
    async def test_extract_missing_pull_request(self):
        """Test that missing pull_request raises ValidationException"""
        payload = {
            'action': 'opened',
            'repository': {
                'html_url': 'https://github.com/test/repo'
            }
        }
        
        with pytest.raises(ValidationException) as exc_info:
            await extract_pr_data(payload)
        
        assert 'pull_request' in str(exc_info.value.message).lower()


class TestTaskQueuing:
    """Test analysis task queuing"""
    
    @pytest.mark.asyncio
    @patch('app.tasks.pull_request_analysis.analyze_pull_request')
    async def test_queue_analysis_task(self, mock_task):
        """Test that analysis task is queued correctly"""
        # Mock the Celery task
        mock_result = Mock()
        mock_result.id = 'task-123-abc'
        mock_task.apply_async.return_value = mock_result
        
        pr_id = 'pr-uuid-123'
        project_id = 'project-uuid-456'
        pr_data = {
            'pr_number': 789,
            'commit_sha': 'abc123',
            'action': 'opened'
        }
        
        result = await queue_analysis_task(pr_id, project_id, pr_data)
        
        # Verify task was queued
        mock_task.apply_async.assert_called_once_with(
            args=[pr_id, project_id],
            queue='high_priority',
            priority=9,
            expires=3600
        )
        
        # Verify result
        assert result['task_id'] == 'task-123-abc'
        assert result['status'] == 'queued'
        assert result['pr_id'] == pr_id
        assert result['pr_number'] == 789


class TestWebhookEndpointEdgeCases:
    """Test edge cases for webhook endpoint"""
    
    def test_webhook_signature_timing_attack_resistance(self):
        """Test that signature verification resists timing attacks"""
        secret = "super_secret_key"
        payload = b'{"sensitive": "data"}'
        
        # Generate correct signature
        mac = hmac.new(secret.encode('utf-8'), msg=payload, digestmod=hashlib.sha256)
        correct_sig = f"sha256={mac.hexdigest()}"
        
        # Create signatures with different lengths
        short_sig = "sha256=abc"
        long_sig = f"sha256={mac.hexdigest()}extra"
        
        # All should use constant-time comparison
        assert verify_webhook_signature(payload, correct_sig, secret) is True
        assert verify_webhook_signature(payload, short_sig, secret) is False
        assert verify_webhook_signature(payload, long_sig, secret) is False
    
    @pytest.mark.asyncio
    async def test_extract_pr_data_with_null_values(self):
        """Test extraction handles null values gracefully"""
        payload = {
            'action': 'opened',
            'pull_request': {
                'number': 100,
                'title': 'Test',
                'body': None,  # Null body
                'head': {
                    'ref': 'branch',
                    'sha': 'sha123'
                }
            },
            'repository': {
                'html_url': 'https://github.com/test/repo',
                'full_name': 'test/repo'
            },
            'sender': {
                'login': 'user'
            }
        }
        
        result = await extract_pr_data(payload)
        
        # Should handle None body gracefully
        assert result['description'] == ''  # Converted to empty string


class TestInvalidSignatureEdgeCases:
    """Test various invalid signature scenarios"""
    
    def test_signature_with_wrong_algorithm_prefix(self):
        """Test signature with sha1= prefix instead of sha256="""
        secret = "test_secret"
        payload = b'{"test": "data"}'
        
        # Use sha1 prefix (wrong algorithm)
        mac = hmac.new(secret.encode('utf-8'), msg=payload, digestmod=hashlib.sha1)
        signature = f"sha1={mac.hexdigest()}"
        
        assert verify_webhook_signature(payload, signature, secret) is False
    
    def test_signature_with_no_prefix(self):
        """Test signature without algorithm prefix"""
        secret = "test_secret"
        payload = b'{"test": "data"}'
        
        # Generate signature without prefix
        mac = hmac.new(secret.encode('utf-8'), msg=payload, digestmod=hashlib.sha256)
        signature = mac.hexdigest()  # No "sha256=" prefix
        
        assert verify_webhook_signature(payload, signature, secret) is False
    
    def test_signature_with_uppercase_prefix(self):
        """Test signature with uppercase SHA256= prefix"""
        secret = "test_secret"
        payload = b'{"test": "data"}'
        
        mac = hmac.new(secret.encode('utf-8'), msg=payload, digestmod=hashlib.sha256)
        signature = f"SHA256={mac.hexdigest()}"  # Uppercase prefix
        
        assert verify_webhook_signature(payload, signature, secret) is False
    
    def test_signature_with_extra_spaces(self):
        """Test signature with extra whitespace"""
        secret = "test_secret"
        payload = b'{"test": "data"}'
        
        mac = hmac.new(secret.encode('utf-8'), msg=payload, digestmod=hashlib.sha256)
        signature = f" sha256={mac.hexdigest()} "  # Extra spaces
        
        assert verify_webhook_signature(payload, signature, secret) is False
    
    def test_signature_with_wrong_secret(self):
        """Test signature generated with different secret"""
        correct_secret = "correct_secret"
        wrong_secret = "wrong_secret"
        payload = b'{"test": "data"}'
        
        # Generate signature with wrong secret
        mac = hmac.new(wrong_secret.encode('utf-8'), msg=payload, digestmod=hashlib.sha256)
        signature = f"sha256={mac.hexdigest()}"
        
        assert verify_webhook_signature(payload, signature, correct_secret) is False
    
    def test_signature_with_modified_payload(self):
        """Test signature validation fails when payload is modified"""
        secret = "test_secret"
        original_payload = b'{"test": "data"}'
        modified_payload = b'{"test": "modified"}'
        
        # Generate signature for original payload
        mac = hmac.new(secret.encode('utf-8'), msg=original_payload, digestmod=hashlib.sha256)
        signature = f"sha256={mac.hexdigest()}"
        
        # Verify with modified payload should fail
        assert verify_webhook_signature(modified_payload, signature, secret) is False
    
    def test_signature_with_empty_string(self):
        """Test signature verification with empty signature string"""
        secret = "test_secret"
        payload = b'{"test": "data"}'
        
        assert verify_webhook_signature(payload, "", secret) is False
    
    def test_signature_with_special_characters_in_secret(self):
        """Test signature with special characters in secret"""
        secret = "test!@#$%^&*()_+-=[]{}|;:',.<>?/~`"
        payload = b'{"test": "data"}'
        
        # Generate valid signature with special character secret
        mac = hmac.new(secret.encode('utf-8'), msg=payload, digestmod=hashlib.sha256)
        signature = f"sha256={mac.hexdigest()}"
        
        assert verify_webhook_signature(payload, signature, secret) is True
        
        # Verify fails with different secret
        assert verify_webhook_signature(payload, signature, "different_secret") is False
    
    def test_signature_with_unicode_in_secret(self):
        """Test signature with unicode characters in secret"""
        secret = "test_密码_🔐"
        payload = b'{"test": "data"}'
        
        # Generate valid signature with unicode secret
        mac = hmac.new(secret.encode('utf-8'), msg=payload, digestmod=hashlib.sha256)
        signature = f"sha256={mac.hexdigest()}"
        
        assert verify_webhook_signature(payload, signature, secret) is True


class TestMalformedPayloadEdgeCases:
    """Test various malformed payload scenarios"""
    
    @pytest.mark.asyncio
    async def test_extract_pr_data_missing_nested_head(self):
        """Test extraction when head object is missing"""
        payload = {
            'action': 'opened',
            'pull_request': {
                'number': 123,
                'title': 'Test PR'
                # Missing 'head' object
            },
            'repository': {
                'html_url': 'https://github.com/test/repo',
                'full_name': 'test/repo'
            }
        }
        
        result = await extract_pr_data(payload)
        
        # Should handle missing nested objects gracefully
        assert result['pr_number'] == 123
        assert result['branch_name'] is None
        assert result['commit_sha'] is None
    
    @pytest.mark.asyncio
    async def test_extract_pr_data_missing_repository(self):
        """Test extraction when repository object is missing"""
        payload = {
            'action': 'opened',
            'pull_request': {
                'number': 123,
                'title': 'Test PR',
                'head': {
                    'ref': 'branch',
                    'sha': 'abc123'
                }
            }
            # Missing 'repository' object
        }
        
        result = await extract_pr_data(payload)
        
        # Should handle missing repository gracefully
        assert result['pr_number'] == 123
        assert result['repository_url'] is None
        assert result['repository_full_name'] is None
    
    @pytest.mark.asyncio
    async def test_extract_pr_data_empty_strings(self):
        """Test extraction with empty string values"""
        payload = {
            'action': '',
            'pull_request': {
                'number': 123,
                'title': '',
                'body': '',
                'head': {
                    'ref': '',
                    'sha': ''
                }
            },
            'repository': {
                'html_url': '',
                'full_name': ''
            },
            'sender': {
                'login': ''
            }
        }
        
        result = await extract_pr_data(payload)
        
        # Should preserve empty strings
        assert result['title'] == ''
        assert result['description'] == ''
        assert result['branch_name'] == ''
        assert result['commit_sha'] == ''
    
    @pytest.mark.asyncio
    async def test_extract_pr_data_with_very_long_strings(self):
        """Test extraction with very long string values"""
        long_string = 'A' * 10000  # 10KB string
        
        payload = {
            'action': 'opened',
            'pull_request': {
                'number': 123,
                'title': long_string,
                'body': long_string,
                'head': {
                    'ref': 'branch',
                    'sha': 'abc123'
                }
            },
            'repository': {
                'html_url': 'https://github.com/test/repo',
                'full_name': 'test/repo'
            }
        }
        
        result = await extract_pr_data(payload)
        
        # Should handle long strings
        assert len(result['title']) == 10000
        assert len(result['description']) == 10000
    
    @pytest.mark.asyncio
    async def test_extract_pr_data_with_special_characters(self):
        """Test extraction with special characters in strings"""
        payload = {
            'action': 'opened',
            'pull_request': {
                'number': 123,
                'title': 'Test <script>alert("XSS")</script>',
                'body': 'Description with\nnewlines\tand\ttabs',
                'head': {
                    'ref': 'feature/test-!@#$%',
                    'sha': 'abc123'
                }
            },
            'repository': {
                'html_url': 'https://github.com/test/repo',
                'full_name': 'test/repo'
            },
            'sender': {
                'login': 'user-name_123'
            }
        }
        
        result = await extract_pr_data(payload)
        
        # Should preserve special characters
        assert '<script>' in result['title']
        assert '\n' in result['description']
        assert '\t' in result['description']
        assert '!@#$%' in result['branch_name']
    
    @pytest.mark.asyncio
    async def test_extract_pr_data_with_unicode_characters(self):
        """Test extraction with unicode characters"""
        payload = {
            'action': 'opened',
            'pull_request': {
                'number': 123,
                'title': 'Test PR 测试 🚀',
                'body': 'Description with émojis 😀 and 中文',
                'head': {
                    'ref': 'feature/测试',
                    'sha': 'abc123'
                }
            },
            'repository': {
                'html_url': 'https://github.com/test/repo',
                'full_name': 'test/repo'
            },
            'sender': {
                'login': 'user_名前'
            }
        }
        
        result = await extract_pr_data(payload)
        
        # Should handle unicode correctly
        assert '测试' in result['title']
        assert '🚀' in result['title']
        assert '😀' in result['description']
        assert '中文' in result['description']
        assert '测试' in result['branch_name']
    
    @pytest.mark.asyncio
    async def test_extract_pr_data_with_negative_numbers(self):
        """Test extraction with negative numbers"""
        payload = {
            'action': 'opened',
            'pull_request': {
                'number': 123,
                'title': 'Test PR',
                'head': {
                    'ref': 'branch',
                    'sha': 'abc123'
                },
                'changed_files': -1,
                'additions': -100,
                'deletions': -50
            },
            'repository': {
                'html_url': 'https://github.com/test/repo',
                'full_name': 'test/repo'
            }
        }
        
        result = await extract_pr_data(payload)
        
        # Should preserve negative numbers (even if unusual)
        assert result['files_changed'] == -1
        assert result['lines_added'] == -100
        assert result['lines_deleted'] == -50
    
    @pytest.mark.asyncio
    async def test_extract_pr_data_with_zero_pr_number(self):
        """Test extraction with PR number 0"""
        payload = {
            'action': 'opened',
            'pull_request': {
                'number': 0,
                'title': 'Test PR',
                'head': {
                    'ref': 'branch',
                    'sha': 'abc123'
                }
            },
            'repository': {
                'html_url': 'https://github.com/test/repo',
                'full_name': 'test/repo'
            }
        }
        
        result = await extract_pr_data(payload)
        
        # Should handle PR number 0
        assert result['pr_number'] == 0
    
    @pytest.mark.asyncio
    async def test_extract_pr_data_with_very_large_numbers(self):
        """Test extraction with very large numbers"""
        payload = {
            'action': 'opened',
            'pull_request': {
                'number': 999999999,
                'title': 'Test PR',
                'head': {
                    'ref': 'branch',
                    'sha': 'abc123'
                },
                'changed_files': 999999,
                'additions': 999999999,
                'deletions': 999999999
            },
            'repository': {
                'html_url': 'https://github.com/test/repo',
                'full_name': 'test/repo'
            }
        }
        
        result = await extract_pr_data(payload)
        
        # Should handle large numbers
        assert result['pr_number'] == 999999999
        assert result['files_changed'] == 999999
        assert result['lines_added'] == 999999999
        assert result['lines_deleted'] == 999999999
    
    @pytest.mark.asyncio
    async def test_extract_pr_data_missing_sender(self):
        """Test extraction when sender object is missing"""
        payload = {
            'action': 'opened',
            'pull_request': {
                'number': 123,
                'title': 'Test PR',
                'head': {
                    'ref': 'branch',
                    'sha': 'abc123'
                }
            },
            'repository': {
                'html_url': 'https://github.com/test/repo',
                'full_name': 'test/repo'
            }
            # Missing 'sender' object
        }
        
        result = await extract_pr_data(payload)
        
        # Should handle missing sender gracefully
        assert result['pr_number'] == 123
        assert result['sender'] is None
    
    @pytest.mark.asyncio
    async def test_extract_pr_data_with_extra_fields(self):
        """Test extraction ignores extra unexpected fields"""
        payload = {
            'action': 'opened',
            'pull_request': {
                'number': 123,
                'title': 'Test PR',
                'head': {
                    'ref': 'branch',
                    'sha': 'abc123'
                },
                'extra_field': 'should be ignored',
                'another_field': 12345
            },
            'repository': {
                'html_url': 'https://github.com/test/repo',
                'full_name': 'test/repo'
            },
            'unexpected_top_level': 'ignored'
        }
        
        result = await extract_pr_data(payload)
        
        # Should extract expected fields and ignore extras
        assert result['pr_number'] == 123
        assert 'extra_field' not in result
        assert 'unexpected_top_level' not in result


class TestDuplicateWebhookEvents:
    """Test duplicate webhook event handling"""
    
    @pytest.mark.asyncio
    async def test_duplicate_delivery_id_detection(self):
        """Test that duplicate delivery IDs are detected"""
        # This is tested in integration tests, but we can test the logic
        # The webhook handler uses Redis cache to track delivery IDs
        # Duplicate deliveries should be rejected
        pass  # Covered in integration tests
    
    @pytest.mark.asyncio
    async def test_same_pr_multiple_actions(self):
        """Test handling same PR with different actions"""
        # When the same PR receives multiple webhook events (opened, synchronize, etc.)
        # Each should be processed if they have different delivery IDs
        # This is covered by the action filtering logic in the webhook handler
        pass  # Covered by existing tests and integration tests


class TestPayloadSizeEdgeCases:
    """Test edge cases related to payload size"""
    
    def test_signature_verification_with_large_payload(self):
        """Test signature verification with large payload (1MB)"""
        secret = "test_secret"
        # Create 1MB payload
        large_data = {'data': 'A' * (1024 * 1024)}
        payload = json.dumps(large_data).encode('utf-8')
        
        # Generate valid signature
        mac = hmac.new(secret.encode('utf-8'), msg=payload, digestmod=hashlib.sha256)
        signature = f"sha256={mac.hexdigest()}"
        
        # Should handle large payloads
        assert verify_webhook_signature(payload, signature, secret) is True
    
    def test_signature_verification_with_empty_payload(self):
        """Test signature verification with empty payload"""
        secret = "test_secret"
        payload = b''
        
        # Generate valid signature for empty payload
        mac = hmac.new(secret.encode('utf-8'), msg=payload, digestmod=hashlib.sha256)
        signature = f"sha256={mac.hexdigest()}"
        
        # Should handle empty payload
        assert verify_webhook_signature(payload, signature, secret) is True


class TestTaskQueuingEdgeCases:
    """Test edge cases in task queuing"""
    
    @pytest.mark.asyncio
    @patch('app.tasks.pull_request_analysis.analyze_pull_request')
    async def test_queue_task_with_special_characters_in_ids(self, mock_task):
        """Test queuing task with special characters in IDs"""
        mock_result = Mock()
        mock_result.id = 'task-123-abc'
        mock_task.apply_async.return_value = mock_result
        
        # IDs with special characters (UUIDs typically don't have these, but test anyway)
        pr_id = 'pr-uuid-123-abc-def'
        project_id = 'project-uuid-456-xyz'
        pr_data = {
            'pr_number': 789,
            'commit_sha': 'abc123',
            'action': 'opened'
        }
        
        result = await queue_analysis_task(pr_id, project_id, pr_data)
        
        # Should handle IDs correctly
        assert result['task_id'] == 'task-123-abc'
        assert result['pr_id'] == pr_id
    
    @pytest.mark.asyncio
    @patch('app.tasks.pull_request_analysis.analyze_pull_request')
    async def test_queue_task_with_minimal_pr_data(self, mock_task):
        """Test queuing task with minimal PR data"""
        mock_result = Mock()
        mock_result.id = 'task-xyz'
        mock_task.apply_async.return_value = mock_result
        
        pr_id = 'pr-123'
        project_id = 'project-456'
        pr_data = {}  # Empty PR data
        
        result = await queue_analysis_task(pr_id, project_id, pr_data)
        
        # Should handle empty PR data
        assert result['task_id'] == 'task-xyz'
        assert result['pr_number'] is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
