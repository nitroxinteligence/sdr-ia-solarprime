# Kommo CRM Tools Unit Tests

This directory contains comprehensive unit tests for all Kommo CRM integration tools used in the SDR Agent system.

## Test Coverage

### 1. Create Lead (`test_create_lead.py`)
Tests for creating new leads in Kommo CRM:
- ✅ Successful lead creation with all fields
- ✅ Duplicate lead detection
- ✅ Missing required fields validation
- ✅ Custom fields handling
- ✅ Initial stage setting
- ✅ Tag management
- ✅ API error handling (400, 401, 429)
- ✅ Unexpected error handling
- ✅ Qualification score scenarios

### 2. Update Lead (`test_update_lead.py`)
Tests for updating existing leads:
- ✅ Successful updates with various fields
- ✅ Lead not found handling
- ✅ No changes detection
- ✅ Custom fields updates
- ✅ Tag addition and removal
- ✅ Pipeline stage changes
- ✅ Edge cases (null values, empty strings)
- ✅ Data integrity preservation
- ✅ Rate limit handling

### 3. Add Note (`test_add_note.py`)
Tests for three note-related tools:

#### `add_kommo_note`
- ✅ Basic note addition with timestamp
- ✅ Empty text validation
- ✅ Lead existence verification
- ✅ API error handling

#### `add_qualification_note`
- ✅ Complete qualification data formatting
- ✅ Score-based emoji selection (high/medium/low)
- ✅ Partial data handling
- ✅ Special field formatting (currency, boolean, lists)

#### `add_interaction_log`
- ✅ Different interaction types (call, email, meeting, etc.)
- ✅ Sentiment tracking
- ✅ Custom emoji mapping
- ✅ Error handling

### 4. Schedule Activity (`test_schedule_activity.py`)
Tests for three scheduling tools:

#### `schedule_kommo_activity`
- ✅ Activity scheduling with various types
- ✅ Business hours adjustment
- ✅ Weekend skipping
- ✅ Date/time format validation
- ✅ Lead existence verification
- ✅ Note addition after scheduling

#### `schedule_follow_up`
- ✅ Next business day calculation
- ✅ Weekend skipping for follow-ups
- ✅ Custom day intervals

#### `schedule_meeting_reminder`
- ✅ Meeting reminder creation (1 hour before)
- ✅ Location and notes handling
- ✅ DateTime parsing

### 5. Update Stage (`test_update_stage.py`)
Tests for two stage-related tools:

#### `update_kommo_stage`
- ✅ Stage transitions through pipeline
- ✅ Stage name validation (key and value)
- ✅ Already in stage detection
- ✅ Special stage handling (QUALIFICADO, REUNIAO_AGENDADA, etc.)
- ✅ Note addition on stage change
- ✅ Pipeline validation

#### `get_lead_stage`
- ✅ Current stage retrieval
- ✅ Stage mapping to KOMMO_STAGES constants
- ✅ Unknown/custom stage handling
- ✅ Pipeline information retrieval

### 6. Search Lead (`test_search_lead.py`)
Tests for two search tools:

#### `search_kommo_lead`
- ✅ Search by name, phone, email
- ✅ Result processing and field extraction
- ✅ Custom fields handling
- ✅ Tag extraction
- ✅ Limit parameter
- ✅ No results handling

#### `search_lead_by_phone`
- ✅ Phone number search
- ✅ Various phone format support
- ✅ Not found scenarios
- ✅ Custom field extraction

## Running the Tests

### Run all Kommo tests:
```bash
pytest agente/tests/unit/kommo/ -v
```

### Run specific test file:
```bash
pytest agente/tests/unit/kommo/test_create_lead.py -v
```

### Run with coverage:
```bash
pytest agente/tests/unit/kommo/ --cov=agente.tools.kommo --cov-report=html
```

### Run specific test:
```bash
pytest agente/tests/unit/kommo/test_create_lead.py::TestCreateKommoLead::test_create_lead_success -v
```

## Test Dependencies

- `pytest` - Test framework
- `pytest-asyncio` - Async test support
- `freezegun` - Time mocking for scheduling tests
- `unittest.mock` - Mocking framework

## Mock Patterns

All tests follow consistent mocking patterns:

1. **Service Mocking**: Mock `get_kommo_service()` to return AsyncMock
2. **API Responses**: Mock service methods with realistic response data
3. **Error Scenarios**: Test both `KommoAPIError` and generic exceptions
4. **Data Validation**: Verify both input validation and output formatting

## Solar Prime Business Logic

The tests validate business-specific scenarios:

1. **Qualification Scores**: High (≥70), Medium (40-69), Low (<40)
2. **Pipeline Stages**: NOVO_LEAD → EM_NEGOCIACAO → EM_QUALIFICACAO → QUALIFICADO → REUNIAO_AGENDADA
3. **Business Hours**: 8:00-18:00, Monday-Friday
4. **Follow-up Rules**: Skip weekends, adjust to business hours
5. **Custom Fields**: Energy consumption, bill value, property type, etc.

## Common Test Fixtures

- `mock_kommo_service`: AsyncMock of KommoService
- `mock_lead`: Sample lead data structure
- `mock_pipelines`: Pipeline and status configuration
- `mock_current_lead`: Existing lead for update tests

## Error Scenarios Covered

- **404**: Lead not found
- **400**: Invalid request data
- **401**: Authentication failures
- **429**: Rate limiting
- **500**: Server errors
- **Connection errors**: Network issues
- **Timeout errors**: Slow responses

## Best Practices

1. **Isolation**: Each test is independent and doesn't affect others
2. **Clarity**: Test names clearly describe what is being tested
3. **Coverage**: Both happy path and error scenarios are tested
4. **Realism**: Mock data matches actual Kommo API responses
5. **Maintainability**: Fixtures reduce duplication and ease updates