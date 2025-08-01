# Database Tools Unit Tests

This directory contains comprehensive unit tests for all database tools in the SDR Agent system.

## Test Coverage

### 1. `test_get_lead.py`
Tests for retrieving lead information from the database:
- Get lead by ID (UUID)
- Get lead by phone number
- Include qualification data
- Include follow-up data
- Handle not found scenarios
- Validate input parameters
- Handle database errors gracefully
- Phone number formatting
- Concurrent access handling

### 2. `test_update_lead.py`
Tests for updating existing lead information:
- Update by lead ID or phone
- Update basic lead fields (name, email, etc.)
- Update qualification data (solutions, urgency, objections)
- Stage transitions (QUALIFYING → QUALIFIED)
- Property type updates
- Bill value and consumption updates
- Partial updates
- Data type conversion
- Handle validation errors
- Concurrent update handling

### 3. `test_save_message.py`
Tests for saving conversation messages:
- Save text messages
- Save messages with media (image, audio, video, document)
- Support different roles (user, assistant, system)
- WhatsApp message ID tracking
- Update conversation message counter
- Handle invalid conversation IDs
- Media type validation
- Long message truncation in response
- Concurrent message saves

### 4. `test_update_conversation.py`
Tests for updating conversation sessions:
- Update session ID
- Update conversation stage
- Update sentiment (positivo, neutro, negativo)
- End conversation with duration calculation
- Update session state data
- Handle invalid sentiment values
- No-op when no updates needed
- Concurrent update handling

### 5. `test_schedule_followup.py`
Tests for scheduling intelligent follow-ups:
- Schedule by lead ID or phone
- Different follow-up types (reminder, check_in, reengagement, etc.)
- Custom vs auto-generated messages
- Time scheduling (minutes, hours, specific datetime)
- First vs second attempt logic
- Business rule validation (not interested leads)
- Default timing based on attempt number
- Context passing for personalization
- Business hours consideration

### 6. `test_create_lead.py`
Tests for creating new leads:
- Create with minimal data (phone only)
- Create with full data (all fields)
- Property type enum conversion
- Data type conversion (string to float/int)
- Handle invalid property types
- Validation of required fields
- Special characters in names
- Solar-specific fields (bill value, consumption)
- Concurrent creation handling

## Common Test Patterns

### Fixtures
- `mock_lead_repository`: Mocked lead repository with async methods
- `mock_conversation_repository`: Mocked conversation repository
- `mock_message_repository`: Mocked message repository
- `mock_followup_repository`: Mocked follow-up repository
- `sample_lead`: Pre-configured lead object for testing
- `sample_conversation`: Pre-configured conversation object
- `sample_message`: Pre-configured message object
- `sample_followup`: Pre-configured follow-up object

### Test Structure
Each test file follows a consistent structure:
1. Import necessary modules and types
2. Define fixtures for mocked repositories and sample data
3. Group tests in a class (e.g., `TestGetLead`)
4. Test success scenarios first
5. Test error scenarios
6. Test edge cases and validation
7. Test concurrent operations
8. Verify tool export

### Mocking Strategy
- Use `AsyncMock` for repository methods
- Patch repository getter functions
- Verify method calls with correct parameters
- Test both success and failure scenarios
- Ensure errors in optional operations don't fail the main operation

### Solar Prime Specific Tests
- Lead qualification stages and scoring
- Energy bill value validation (R$)
- Energy consumption in kWh
- Solution type mappings
- Follow-up rules based on lead stage
- Business hours for follow-ups
- Portuguese language messages
- Brazilian phone number formatting

## Running the Tests

```bash
# Run all database tool tests
pytest agente/tests/unit/database/

# Run a specific test file
pytest agente/tests/unit/database/test_get_lead.py

# Run with coverage
pytest --cov=agente.tools.database agente/tests/unit/database/

# Run a specific test
pytest agente/tests/unit/database/test_get_lead.py::TestGetLead::test_get_lead_by_id_success
```

## Key Test Scenarios

### Data Integrity
- UUID validation for IDs
- Phone number formatting consistency
- Enum value handling
- Data type conversions
- Required vs optional fields

### Error Handling
- Database connection failures
- Invalid input validation
- Not found scenarios
- Partial operation failures
- Graceful degradation

### Business Logic
- Lead interest validation
- Stage transition rules
- Follow-up scheduling logic
- Qualification scoring
- Message ordering

### Performance
- Concurrent operation handling
- Transaction rollback scenarios
- Efficient data retrieval
- Proper pagination support