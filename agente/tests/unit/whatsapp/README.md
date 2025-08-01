# WhatsApp Tools Unit Tests

This directory contains comprehensive unit tests for all WhatsApp tools in the SDR Agent system.

## Test Coverage

### 1. `test_send_text_message.py`
Tests for sending text messages via WhatsApp:
- ✅ Successful message sending with automatic delay calculation
- ✅ Custom delay specification
- ✅ Empty response handling
- ✅ Exception handling
- ✅ Invalid phone number format
- ✅ Empty text messages
- ✅ Very long text messages
- ✅ Special characters and emojis
- ✅ Missing message ID handling

### 2. `test_type_simulation.py`
Tests for typing indicator simulation:
- ✅ Successful typing simulation with message sending
- ✅ Typing simulation without sending
- ✅ Custom delay handling
- ✅ Minimum and maximum delay boundaries
- ✅ Send failure after typing
- ✅ Exception handling during simulation
- ✅ Empty text handling
- ✅ Multiline text support
- ✅ Sleep interruption handling

### 3. `test_send_image_message.py`
Tests for sending images:
- ✅ Successful image sending
- ✅ Images with captions
- ✅ Invalid URL validation
- ✅ Various image extensions (.jpg, .png, .gif, etc.)
- ✅ Empty response handling
- ✅ Exception handling
- ✅ HTTP URL support
- ✅ Long captions
- ✅ Special characters in captions

### 4. `test_send_document_message.py`
Tests for sending documents:
- ✅ Successful document sending
- ✅ Documents with caption and filename
- ✅ Filename-only handling
- ✅ Various document types (.pdf, .doc, .xlsx, etc.)
- ✅ Invalid URL validation
- ✅ Empty response handling
- ✅ Exception handling
- ✅ Case-insensitive extension detection
- ✅ URLs with query parameters

### 5. `test_send_audio_message.py`
Tests for sending audio files:
- ✅ Successful audio sending
- ✅ Audio with captions
- ✅ Invalid URL validation
- ✅ Various audio formats (.mp3, .ogg, .opus, etc.)
- ✅ Empty response handling
- ✅ Exception handling
- ✅ HTTP URL support
- ✅ Long captions
- ✅ URLs with query parameters

### 6. `test_send_location_message.py`
Tests for sending location coordinates:
- ✅ Successful location sending
- ✅ Locations with name and address
- ✅ Name-only and address-only handling
- ✅ Coordinate validation (latitude: -90 to 90, longitude: -180 to 180)
- ✅ Boundary value testing
- ✅ Empty response handling
- ✅ Exception handling
- ✅ Special characters in location names
- ✅ High precision coordinate handling

### 7. `test_message_buffer.py`
Tests for message buffering and consolidation:
- ✅ Single message buffering
- ✅ Force send functionality
- ✅ Automatic send on buffer size limit
- ✅ Timeout-triggered sending
- ✅ Send failure handling
- ✅ Exception handling
- ✅ Buffer clearing
- ✅ Buffer status retrieval
- ✅ Concurrent access handling
- ✅ Auto-send enable/disable

### 8. `test_message_chunking.py`
Tests for splitting long messages:
- ✅ Short text handling (no chunking needed)
- ✅ Long text with sentence boundary preference
- ✅ Chunking without sentence preference
- ✅ Custom delay settings
- ✅ Empty text validation
- ✅ Minimum chunk size enforcement
- ✅ Multiple paragraph handling
- ✅ Proportional delay calculation
- ✅ Statistics calculation
- ✅ Unicode and emoji support

## Running the Tests

### Run all WhatsApp tool tests:
```bash
pytest agente/tests/unit/whatsapp/ -v
```

### Run tests for a specific tool:
```bash
pytest agente/tests/unit/whatsapp/test_send_text_message.py -v
```

### Run with coverage report:
```bash
pytest agente/tests/unit/whatsapp/ --cov=agente.tools.whatsapp --cov-report=html
```

### Run the test summary:
```bash
python agente/tests/unit/whatsapp/test_all_whatsapp_tools.py
```

## Test Structure

All tests follow a consistent pattern:
1. **Arrange**: Set up test data and mock dependencies
2. **Act**: Execute the tool function
3. **Assert**: Verify the results and side effects

## Mocking Strategy

- Uses `mock_evolution_service` fixture from `conftest.py`
- Patches the `get_evolution_service` function to inject mocks
- Mocks Evolution API responses for predictable testing
- Tests both success and failure scenarios

## Coverage Goals

- Target: >90% code coverage for all tools
- Focus on:
  - Happy path scenarios
  - Error conditions
  - Edge cases
  - Boundary values
  - Concurrent access (where applicable)
  - Async behavior

## Adding New Tests

When adding a new WhatsApp tool:
1. Create a test file named `test_[tool_name].py`
2. Import the tool function and necessary fixtures
3. Test all parameters and return values
4. Include error handling tests
5. Add edge case tests
6. Update this README with the new test coverage