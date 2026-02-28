# Feature Flags System

This module provides a flexible feature flag system for gradual rollout, A/B testing, and feature management.

## Features

- **Boolean Flags**: Simple on/off switches
- **Percentage Rollouts**: Gradually roll out features to a percentage of users
- **User-Specific Flags**: Enable features for specific users
- **Environment-Specific Flags**: Enable features only in certain environments
- **Dynamic Updates**: Change flags without restarting the application
- **Environment Variable Override**: Override flags via environment variables

## Quick Start

### Check if Feature is Enabled

```python
from app.core.feature_flags import is_feature_enabled

# Simple boolean check
if is_feature_enabled("github_integration"):
    # Use GitHub integration
    process_github_webhook(payload)

# With user ID for percentage-based rollout
if is_feature_enabled("realtime_updates", user_id=current_user.id):
    # Enable real-time updates for this user
    enable_websocket_connection()

# With environment check
if is_feature_enabled("distributed_tracing", environment="production"):
    # Enable tracing in production
    setup_jaeger_tracing()
```

### Use Decorator

```python
from app.core.feature_flags import require_feature

@require_feature("github_integration")
def handle_github_webhook(payload):
    """This function only runs if github_integration is enabled."""
    # Process webhook
    pass
```

## Available Feature Flags

### Core Features

| Flag Name | Default | Description |
|-----------|---------|-------------|
| `github_integration` | ✓ | GitHub webhook integration and PR analysis |
| `llm_analysis` | ✓ | LLM-powered code analysis |
| `architecture_analysis` | ✓ | Architecture drift detection and circular dependency analysis |
| `compliance_check` | ✓ | ISO/IEC 25010 compliance verification |
| `audit_logging` | ✓ | Comprehensive audit logging |

### Performance Features

| Flag Name | Default | Description |
|-----------|---------|-------------|
| `redis_caching` | ✓ | Redis caching for API responses |
| `query_optimization` | ✓ | Database query optimization |

### Experimental Features

| Flag Name | Default | Rollout | Description |
|-----------|---------|---------|-------------|
| `realtime_updates` | ✗ | 10% | WebSocket real-time updates |
| `advanced_llm_features` | ✗ | 25% | Advanced LLM features (fine-tuning, custom prompts) |
| `graph_visualization_v2` | ✗ | 0% | New graph visualization engine |

### Security Features

| Flag Name | Default | Description |
|-----------|---------|-------------|
| `rate_limiting` | ✓ | API rate limiting |
| `mfa_authentication` | ✗ | Multi-factor authentication |

### Monitoring Features

| Flag Name | Default | Description |
|-----------|---------|-------------|
| `detailed_metrics` | ✓ | Detailed performance metrics collection |
| `distributed_tracing` | ✗ | Distributed tracing with Jaeger (staging/production only) |

## Flag Strategies

### 1. Boolean Strategy

Simple on/off switch:

```python
flags.register_flag(
    "new_feature",
    enabled=True,
    description="Enable new feature",
    strategy=FeatureFlagStrategy.BOOLEAN
)

# Check
if is_feature_enabled("new_feature"):
    use_new_feature()
```

### 2. Percentage Strategy

Gradually roll out to a percentage of users:

```python
flags.register_flag(
    "beta_feature",
    enabled=True,
    description="Beta feature for 25% of users",
    strategy=FeatureFlagStrategy.PERCENTAGE,
    config={"percentage": 25}
)

# Check (requires user_id)
if is_feature_enabled("beta_feature", user_id=user.id):
    use_beta_feature()
```

**How it works:**
- Uses consistent hashing based on user_id and flag_name
- Same user always gets same result
- Percentage can be adjusted dynamically

### 3. User List Strategy

Enable for specific users:

```python
flags.register_flag(
    "vip_feature",
    enabled=True,
    description="Feature for VIP users only",
    strategy=FeatureFlagStrategy.USER_LIST,
    config={"users": ["user123", "user456"]}
)

# Check
if is_feature_enabled("vip_feature", user_id=user.id):
    use_vip_feature()
```

### 4. Environment Strategy

Enable only in specific environments:

```python
flags.register_flag(
    "debug_mode",
    enabled=True,
    description="Debug mode for development",
    strategy=FeatureFlagStrategy.ENVIRONMENT,
    config={"environments": ["development", "staging"]}
)

# Check
if is_feature_enabled("debug_mode", environment="development"):
    enable_debug_logging()
```

## Managing Flags

### Get Feature Flag Manager

```python
from app.core.feature_flags import get_feature_flags

flags = get_feature_flags()
```

### Enable/Disable Flags

```python
# Enable a flag
flags.enable_flag("new_feature")

# Disable a flag
flags.disable_flag("old_feature")
```

### Adjust Percentage Rollout

```python
# Start with 10%
flags.set_percentage("beta_feature", 10)

# Increase to 25%
flags.set_percentage("beta_feature", 25)

# Increase to 50%
flags.set_percentage("beta_feature", 50)

# Full rollout
flags.set_percentage("beta_feature", 100)
```

### Manage User Lists

```python
# Add user to flag
flags.add_user_to_flag("vip_feature", "user789")

# Remove user from flag
flags.remove_user_from_flag("vip_feature", "user123")
```

### Get All Flags

```python
# Get all flags and their state
all_flags = flags.get_all_flags()
for name, info in all_flags.items():
    print(f"{name}: {info}")

# Get only enabled flags
enabled = flags.get_enabled_flags()
print(f"Enabled flags: {enabled}")
```

## Environment Variable Override

Override any flag via environment variables:

```bash
# Format: FEATURE_FLAG_{FLAG_NAME}=true/false
export FEATURE_FLAG_GITHUB_INTEGRATION=true
export FEATURE_FLAG_REALTIME_UPDATES=false

# Legacy format (also supported)
export ENABLE_GITHUB_INTEGRATION=true
export ENABLE_LLM_ANALYSIS=false
```

## API Endpoints

### Get All Flags

```http
GET /api/v1/admin/feature-flags
```

Response:
```json
{
  "github_integration": {
    "enabled": true,
    "description": "GitHub webhook integration",
    "strategy": "boolean",
    "config": {}
  },
  "realtime_updates": {
    "enabled": true,
    "description": "WebSocket real-time updates",
    "strategy": "percentage",
    "config": {"percentage": 10}
  }
}
```

### Enable/Disable Flag

```http
POST /api/v1/admin/feature-flags/{flag_name}/enable
POST /api/v1/admin/feature-flags/{flag_name}/disable
```

### Update Percentage

```http
PUT /api/v1/admin/feature-flags/{flag_name}/percentage
Content-Type: application/json

{
  "percentage": 50
}
```

## Best Practices

### 1. Start Small

Begin with a small percentage and gradually increase:

```python
# Week 1: 5%
flags.set_percentage("new_feature", 5)

# Week 2: 10%
flags.set_percentage("new_feature", 10)

# Week 3: 25%
flags.set_percentage("new_feature", 25)

# Week 4: 50%
flags.set_percentage("new_feature", 50)

# Week 5: 100%
flags.set_percentage("new_feature", 100)
```

### 2. Monitor Metrics

Track metrics for flagged features:

```python
if is_feature_enabled("new_feature", user_id=user.id):
    with metrics.timer("new_feature.execution_time"):
        result = use_new_feature()
    metrics.increment("new_feature.usage")
```

### 3. Clean Up Old Flags

Remove flags after full rollout:

```python
# After feature is fully rolled out and stable
# 1. Remove flag checks from code
# 2. Remove flag registration
# 3. Deploy
```

### 4. Document Flags

Always provide clear descriptions:

```python
flags.register_flag(
    "complex_feature",
    enabled=False,
    description="Complex feature that does X, Y, and Z. "
                "Requires database migration v123. "
                "See JIRA-456 for details.",
    strategy=FeatureFlagStrategy.PERCENTAGE,
    config={"percentage": 0}
)
```

### 5. Test Both States

Always test with flag enabled AND disabled:

```python
def test_feature_enabled():
    flags = get_feature_flags()
    flags.enable_flag("new_feature")
    result = my_function()
    assert result == expected_with_feature

def test_feature_disabled():
    flags = get_feature_flags()
    flags.disable_flag("new_feature")
    result = my_function()
    assert result == expected_without_feature
```

## Gradual Rollout Example

Complete example of rolling out a new feature:

```python
# 1. Register flag (disabled initially)
flags.register_flag(
    "new_dashboard",
    enabled=False,
    description="New dashboard UI with improved performance",
    strategy=FeatureFlagStrategy.PERCENTAGE,
    config={"percentage": 0}
)

# 2. Deploy code with flag checks
@app.get("/dashboard")
def get_dashboard(user_id: str):
    if is_feature_enabled("new_dashboard", user_id=user_id):
        return render_new_dashboard()
    else:
        return render_old_dashboard()

# 3. Enable for internal testing (specific users)
flags.add_user_to_flag("new_dashboard", "internal_user_1")
flags.add_user_to_flag("new_dashboard", "internal_user_2")

# 4. Start percentage rollout
flags.enable_flag("new_dashboard")
flags.set_percentage("new_dashboard", 5)  # 5% of users

# 5. Monitor metrics and errors
# If issues found, reduce percentage or disable
flags.set_percentage("new_dashboard", 0)

# 6. Gradually increase
flags.set_percentage("new_dashboard", 10)
flags.set_percentage("new_dashboard", 25)
flags.set_percentage("new_dashboard", 50)
flags.set_percentage("new_dashboard", 100)

# 7. After stable, remove flag and old code
# Remove flag checks, keep only new dashboard
```

## Troubleshooting

### Flag Not Working

```python
# Check if flag exists
flags = get_feature_flags()
all_flags = flags.get_all_flags()
if "my_flag" not in all_flags:
    print("Flag not registered")

# Check flag state
flag_info = all_flags["my_flag"]
print(f"Enabled: {flag_info['enabled']}")
print(f"Strategy: {flag_info['strategy']}")
print(f"Config: {flag_info['config']}")
```

### Percentage Not Working

```python
# Ensure user_id is provided
if is_feature_enabled("beta_feature", user_id=user.id):
    # Will work
    pass

if is_feature_enabled("beta_feature"):
    # Won't work - user_id required for percentage strategy
    pass
```

### Environment Override Not Working

```bash
# Check environment variable is set
echo $FEATURE_FLAG_MY_FEATURE

# Ensure correct format (uppercase, underscores)
export FEATURE_FLAG_MY_FEATURE=true  # Correct
export feature_flag_my_feature=true  # Wrong
```

## Related Documentation

- [Configuration Management](./config.py)
- [Environment Variables](.env.example)
- [API Documentation](../api/README.md)

## Validates Requirements

- **Requirement 14.7**: Implement feature flags for gradual rollout
- **Requirement 14.1**: Externalize all configuration
- **Requirement 14.5**: Implement configuration hot-reload
