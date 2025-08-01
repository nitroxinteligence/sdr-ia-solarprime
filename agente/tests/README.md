# SDR Agent - Test Suite Documentation

## Overview

This directory contains comprehensive tests for the SDR Agent system, ensuring reliability, performance, and correctness of all components. Includes both traditional mock-based tests and **REAL API integration tests** for complete validation.

## Test Structure

```
tests/
├── conftest.py                    # Pytest configuration and shared fixtures  
├── conftest_real.py              # Real API test fixtures and configurations
├── run_tests.py                  # Test runner script (mock-based tests)
├── run_real_tests.py             # Real API test runner script ⭐ NEW
├── enhanced_health_check.py      # Advanced health monitoring ⭐ NEW
├── setup_test_environment.py     # Test environment validation ⭐ NEW
├── cleanup_test_data.py          # Test data cleanup automation ⭐ NEW
├── pytest_real.ini               # Real test configuration ⭐ NEW
│
├── unit/                         # Unit tests for individual components (mock-based)
│   ├── whatsapp/        # WhatsApp tools tests (8 tools)
│   ├── kommo/           # Kommo CRM tools tests (6 tools)  
│   ├── calendar/        # Google Calendar tools tests (5 tools)
│   ├── database/        # Database tools tests (6 tools)
│   ├── media/           # Media processing tools tests (3 tools)
│   └── utility/         # Utility tools tests (2 tools)
│
├── real_integration/             # ⭐ REAL API Integration Tests
│   └── test_google_calendar_real.py  # Complete Google Calendar real tests
│
├── e2e_real/                     # ⭐ Real End-to-End Tests
├── performance_real/             # ⭐ Real Performance Testing
├── integration/                  # Integration tests (mock-based)
├── stress/                       # Stress tests for concurrent operations
├── validation/                   # Validation tests for business logic
└── performance/                  # Performance benchmark tests (mock-based)
```

## Running Tests

### Using the Test Runner Script

The easiest way to run tests is using the provided `run_tests.py` script:

```bash
# Run all unit tests
python agente/tests/run_tests.py unit

# Run specific category of unit tests
python agente/tests/run_tests.py unit --category whatsapp

# Run integration tests
python agente/tests/run_tests.py integration

# Run all test suites
python agente/tests/run_tests.py all

# Run with verbose output
python agente/tests/run_tests.py unit -v

# Generate coverage report
python agente/tests/run_tests.py coverage
```

### Using Pytest Directly

You can also run tests directly with pytest:

```bash
# Run all tests
pytest agente/tests/

# Run specific test file
pytest agente/tests/unit/whatsapp/test_send_text.py

# Run with coverage
pytest agente/tests/unit/ --cov=agente --cov-report=html

# Run specific test by name
pytest agente/tests/ -k "test_send_text_success"

# Run with markers
pytest agente/tests/ -m "integration"
```

## 🧪 REAL API Testing Framework ⭐ NEW

### Overview

In addition to traditional mock-based tests, we now have a comprehensive **REAL API testing framework** that validates functionality against actual APIs in isolated test environments. This addresses the critical gap where mock-based tests could pass while real integration was broken.

### Running Real API Tests

```bash
# ⚠️ IMPORTANT: Configure test environment first
export ENVIRONMENT=test
export GOOGLE_CALENDAR_ID=your-test-calendar-id
# ... other test credentials

# Validate test environment
python agente/tests/setup_test_environment.py

# Run Google Calendar real integration tests
python agente/tests/run_real_tests.py --google-calendar --verbose

# Run all real integration tests
python agente/tests/run_real_tests.py --integration

# Run performance tests against real APIs
python agente/tests/run_real_tests.py --performance --report

# Run specific real test
python agente/tests/run_real_tests.py --test test_service_account_authentication
```

### Advanced Health Monitoring

```bash
# Complete system health check
python agente/tests/enhanced_health_check.py --full

# Continuous monitoring (every 5 minutes)
python agente/tests/enhanced_health_check.py --monitor --interval 300

# Quick health check for CI/CD
python agente/tests/enhanced_health_check.py --ci --timeout 60

# Service-specific health check
python agente/tests/enhanced_health_check.py --service google-calendar
```

### Test Data Cleanup

```bash
# Check what would be cleaned (recommended first)
python agente/tests/cleanup_test_data.py --dry-run

# Execute real cleanup
python agente/tests/cleanup_test_data.py --confirm

# Clean data older than 7 days
python agente/tests/cleanup_test_data.py --older-than 7 --confirm
```

### Real API Test Coverage

#### ✅ Google Calendar API - FULLY IMPLEMENTED
- **Authentication & Authorization**: Service account validation, permissions checking
- **CRUD Operations**: Create/Read/Update/Delete events with real API calls
- **Thread Safety**: Concurrent operations, rate limiting validation (10 req/s)
- **Error Handling**: Invalid data, network failures, recovery scenarios  
- **Performance**: Response time benchmarks, reliability monitoring

#### ⏳ Pending Implementation
- **Kommo CRM**: Real lead management, pipeline operations
- **Evolution API**: WhatsApp messaging, media handling
- **Supabase**: Database operations, data consistency

### Safety Features

- 🛡️ **Environment Validation**: Automatic detection and blocking of production environments
- 🏷️ **Test Data Marking**: All test data clearly marked with `[TESTE]` prefixes
- 🧹 **Automatic Cleanup**: Test data automatically removed after execution
- 📊 **Monitoring**: Real-time performance and reliability metrics
- 🚨 **Alerting**: Proactive alerts for system degradation

## Test Categories

### Unit Tests (30 tools tested)

#### WhatsApp Tools (8 tools)
- `send_text` - Text message sending with typing simulation
- `send_typing` - Typing indicator management
- `send_media` - Image, document, and audio sending
- `send_list` - Interactive list messages
- `send_buttons` - Interactive button messages
- `download_media` - Media file downloading
- `get_instance_status` - Evolution API status checking
- `check_whatsapp_connection` - WhatsApp connection validation

#### Kommo CRM Tools (6 tools)
- `create_lead` - Lead creation with custom fields
- `update_lead` - Lead updates and stage transitions
- `add_note` - Note addition with timestamps
- `create_task` - Task creation and scheduling
- `get_pipelines` - Pipeline and stage retrieval
- `get_calendar_link` - Calendar booking link generation

#### Google Calendar Tools (5 tools)
- `check_availability` - Available slot checking with business hours
- `create_event` - Meeting creation with Google Meet
- `update_event` - Event rescheduling
- `delete_event` - Event cancellation
- `get_events` - Event listing and filtering

#### Database Tools (6 tools)
- `get_lead_info` - Lead data retrieval
- `update_lead_info` - Lead information updates
- `save_conversation` - Conversation persistence
- `get_conversation_history` - Message history retrieval
- `create_follow_up` - Follow-up task scheduling
- `complete_follow_up` - Follow-up completion tracking

#### Media Tools (3 tools)
- `analyze_image` - AI-powered image analysis (energy bills)
- `extract_pdf_info` - PDF text extraction
- `transcribe_audio` - Audio to text transcription

#### Utility Tools (2 tools)
- `calculate_score` - Lead qualification scoring
- `check_business_hours` - Business hours validation

### Integration Tests

Tests for external API integrations:
- **Evolution API**: WhatsApp messaging, media handling, webhooks
- **Kommo CRM**: Lead management, custom fields, webhooks
- **Google Calendar**: Event management, availability checking

### Stress Tests

Concurrent operation testing:
- Multiple simultaneous conversations (50-100)
- Rapid message processing
- Session isolation
- Memory usage stability
- Resource cleanup

### Validation Tests

Business logic validation:
- Helen Vieira personality consistency
- Typing simulation realism
- Message humanization
- Natural conversation flow
- Brazilian Portuguese localization

### Performance Benchmarks

Performance metrics testing:
- Single message response time (<3s)
- Throughput (>5 messages/second)
- Response time percentiles (P50, P95, P99)
- Memory usage per session (<1MB)
- API call efficiency
- Scaling with concurrent sessions

## Test Configuration

### Environment Variables

Create a `.env.test` file for test configuration:

```env
ENVIRONMENT=test
DEBUG=true
LOG_LEVEL=DEBUG

# Mock service URLs
SUPABASE_URL=https://test.supabase.co
SUPABASE_KEY=test-key
EVOLUTION_API_URL=http://localhost:8080
EVOLUTION_API_KEY=test-api-key
EVOLUTION_INSTANCE=test-instance
KOMMO_SUBDOMAIN=test
KOMMO_LONG_LIVED_TOKEN=test-token
GOOGLE_API_KEY=test-google-key
```

### Pytest Configuration

The `conftest.py` file provides:
- Shared fixtures for all tests
- Mock services configuration
- Async test support
- Test utilities

## Writing New Tests

### Test Structure

```python
import pytest
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_feature_success(mock_service):
    """Test successful feature execution."""
    # Arrange
    mock_service.method.return_value = {"success": True}
    
    # Act
    result = await feature_function()
    
    # Assert
    assert result["success"] is True
    mock_service.method.assert_called_once()
```

### Best Practices

1. **Use descriptive test names**: `test_send_text_with_emoji_success`
2. **Follow AAA pattern**: Arrange, Act, Assert
3. **Test both success and failure cases**
4. **Use fixtures for common setup**
5. **Mock external dependencies**
6. **Test edge cases and boundaries**
7. **Keep tests isolated and independent**

## Coverage Goals

- **Unit Tests**: >90% coverage for all tools
- **Integration Tests**: All external API endpoints
- **Critical Paths**: 100% coverage for qualification flow
- **Error Handling**: All error scenarios tested

## Continuous Integration

Tests are run automatically on:
- Pull requests
- Commits to main branch
- Nightly builds

### CI Commands

```yaml
# GitHub Actions example
- name: Run tests
  run: |
    pip install -r requirements.txt
    python agente/tests/run_tests.py all --continue-on-failure
    
- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

## Debugging Tests

### Running single test with debugging

```bash
# With pytest
pytest -s -vv agente/tests/unit/whatsapp/test_send_text.py::test_send_text_success

# With pdb
pytest --pdb agente/tests/unit/whatsapp/test_send_text.py

# With logging
pytest --log-cli-level=DEBUG agente/tests/
```

### Common Issues

1. **Import errors**: Ensure project root is in PYTHONPATH
2. **Async warnings**: Use `pytest-asyncio` markers
3. **Mock issues**: Check mock method names match actual methods
4. **Timeout errors**: Increase timeout for slow operations

## Performance Testing

### Running benchmarks

```bash
# Run all benchmarks
python agente/tests/run_tests.py performance

# Run specific benchmark
pytest agente/tests/performance/test_benchmarks.py::test_throughput_messages_per_second -s
```

### Interpreting results

- **Response Time**: Should be <3s for single messages
- **Throughput**: Should handle >5 messages/second
- **Memory**: Should use <1MB per active session
- **API Efficiency**: Minimize redundant calls

## Contributing

When adding new tests:

1. Follow existing patterns and structure
2. Add appropriate markers (`@pytest.mark.unit`, etc.)
3. Update this documentation
4. Ensure tests pass locally before submitting
5. Include both positive and negative test cases
6. Document any special setup requirements