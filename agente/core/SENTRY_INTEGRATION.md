# Sentry Integration for SDR Agent

This document describes the Sentry integration for error tracking, performance monitoring, and custom event tracking in the SDR Agent.

## Overview

The SDR Agent integrates with Sentry to provide:
- **Error Tracking**: Automatic capture of exceptions with context
- **Performance Monitoring**: Track API endpoints and agent operations
- **Custom Events**: Monitor qualification stages, tool usage, and agent lifecycle
- **Breadcrumbs**: Detailed trail of events leading to errors

## Configuration

### Environment Variables

Add the following to your `.env` file:

```env
# Sentry DSN from your project settings
SENTRY_DSN=https://YOUR_KEY@o123456.ingest.sentry.io/PROJECT_ID

# Performance monitoring (0.0 to 1.0)
SENTRY_TRACES_SAMPLE_RATE=0.1  # 10% of transactions

# Profiling (0.0 to 1.0)
SENTRY_PROFILES_SAMPLE_RATE=0.1  # 10% of transactions

# Environment
ENVIRONMENT=production  # or development, staging
```

### Setup

Sentry is automatically initialized when the agent starts. No additional setup required.

## Features

### 1. Error Tracking

All exceptions are automatically captured with context:

```python
try:
    # Your code
except Exception as e:
    capture_agent_error(
        e,
        context={
            "phone": phone,
            "operation": "qualification",
            "stage": current_stage
        }
    )
```

### 2. Performance Monitoring

#### API Endpoints
All FastAPI endpoints are automatically monitored:
- Request/response times
- Error rates
- Throughput

#### Agent Operations
The `process_message` method is wrapped with performance monitoring:
- Message processing time
- Qualification stage transitions
- Tool execution metrics

### 3. Custom Events

#### Qualification Stage Monitoring
```python
monitor_qualification_stage(
    phone="5511999999999",
    stage="collecting_name",
    success=True,
    duration_ms=1500
)
```

#### Tool Usage Monitoring
All tools can be monitored with the `@monitor_tool` decorator:
```python
@tool(show_result=True)
@monitor_tool("whatsapp.send_message")
async def send_text_message(...):
    ...
```

### 4. Breadcrumbs

Breadcrumbs provide a trail of events:
```python
add_breadcrumb(
    message="Processing message",
    category="agent",
    level="info",
    data={"phone": "5511****", "stage": "qualification"}
)
```

## Privacy and Security

### Data Redaction
Sensitive data is automatically redacted:
- Phone numbers are partially masked (e.g., "5511****")
- Personal information (CPF, RG, email) is removed
- API keys and tokens are redacted

### PII (Personally Identifiable Information)
- `send_default_pii` is set to `False`
- User IDs are hashed phone numbers
- No full phone numbers or names are sent

## Monitoring Dashboard

### Key Metrics to Monitor

1. **Error Rate**
   - Track spikes in errors
   - Monitor error types and frequencies
   - Set alerts for critical errors

2. **Performance**
   - Message processing time (target: <3s)
   - Tool execution time
   - API response times

3. **Qualification Funnel**
   - Stage transition success rates
   - Drop-off points
   - Average time per stage

4. **Tool Usage**
   - Most used tools
   - Tool failure rates
   - Performance by tool type

### Recommended Alerts

1. **High Error Rate**: >5% error rate in 5 minutes
2. **Slow Processing**: Message processing >5 seconds
3. **Tool Failures**: Any tool with >10% failure rate
4. **Qualification Drops**: >50% drop rate at any stage

## Custom Integration Points

### Adding Monitoring to New Tools

```python
from agente.core.tool_monitoring import monitor_tool

@tool(show_result=True)
@monitor_tool("category.tool_name")
async def your_new_tool(...):
    ...
```

### Capturing Custom Events

```python
from agente.core.monitoring import capture_agent_event

capture_agent_event(
    "Custom Event Name",
    "event_category",
    {
        "key": "value",
        "metric": 123
    },
    level="info"  # or "warning", "error"
)
```

### Adding Context to Errors

```python
from agente.core.monitoring import capture_agent_error

try:
    # Your code
except Exception as e:
    capture_agent_error(
        e,
        context={
            "custom_field": "value",
            "user_action": "scheduling_meeting",
            "additional_info": {...}
        }
    )
```

## Best Practices

1. **Use Appropriate Sampling Rates**
   - Production: 0.1 (10%) for both traces and profiles
   - Development: 1.0 (100%) for debugging
   - Adjust based on volume and costs

2. **Add Meaningful Context**
   - Include relevant business context in errors
   - Use descriptive event names and categories
   - Add breadcrumbs for complex operations

3. **Monitor Business Metrics**
   - Track qualification success rates
   - Monitor tool usage patterns
   - Measure response times by stage

4. **Set Up Alerts**
   - Configure alerts for critical errors
   - Monitor performance degradation
   - Track business metric anomalies

## Troubleshooting

### Sentry Not Capturing Events

1. Check if `SENTRY_DSN` is set correctly
2. Verify environment is not filtering events
3. Check Sentry project rate limits
4. Look for initialization errors in logs

### Missing Context

1. Ensure `capture_agent_error` is used instead of generic logging
2. Add breadcrumbs before critical operations
3. Use `set_user_context` for user-specific errors

### Performance Issues

1. Reduce sampling rates if needed
2. Disable profiling in production if causing overhead
3. Review custom event volume