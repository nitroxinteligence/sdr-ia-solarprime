# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Running the Application
```bash
# Development mode
python main.py

# Production mode with uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000

# Using Docker
docker-compose up -d

# Production deployment (EasyPanel)
cd prod && docker-compose -f docker-compose.production.yml up -d
```

### Testing and Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/
pytest tests/test_multimodal_complete.py -v  # Specific test

# Setup NLTK data (required for smart text splitting)
python setup_nltk.py

# Test qualification flow
python test_qualification_flow.py
```

### Database Setup
```bash
# Apply Supabase migrations (run SQL files in order)
# Execute in Supabase SQL editor:
# 1. sqls/tabela-*.sql files (create tables)
# 2. sqls/fix_*.sql files (apply fixes)
# 3. sqls/migration_*.sql files (apply migrations)
```

## High-Level Architecture

### System Overview
SDR IA SolarPrime is an AI-powered sales development system for solar energy, built with:
- **AGnO Framework** (v1.7.6) - Multi-agent AI orchestration
- **FastAPI** - Webhook and API endpoints
- **Supabase** - PostgreSQL with pgvector for memory and persistence
- **Evolution API** - WhatsApp integration
- **Redis** - Message buffering and caching

### Core Components

1. **AgenticSDR** (`app/agents/agentic_sdr.py`)
   - Main conversational agent with ultra-humanized personality
   - Multimodal processing (images, audio, documents)
   - Context analysis and emotional state tracking
   - Decision engine for team agent activation

2. **SDR Team** (`app/teams/sdr_team.py`)
   - Coordinates specialized agents:
     - **CalendarAgent** - Google Calendar meeting scheduling
     - **CRMAgent** - Kommo CRM integration
     - **FollowUpAgent** - Lead nurturing and reengagement

3. **Message Flow Architecture**
   ```
   WhatsApp → Evolution API → Webhook → Message Buffer → AgenticSDR → Team Agents → Response
   ```

4. **Key Services**
   - **Message Buffer** - Groups rapid messages (configurable timeout)
   - **Message Splitter** - Smart message chunking for WhatsApp limits
   - **Typing Controller** - Simulates human typing patterns
   - **FollowUp Executor** - Automated follow-up scheduling

### Configuration Management
All behavior controlled via environment variables in `.env`:
- Agent enablement flags (`ENABLE_*_AGENT`)
- Timing controls (`TYPING_DURATION_*`, `RESPONSE_DELAY_*`)
- AI model selection (`PRIMARY_AI_MODEL`, `FALLBACK_AI_MODEL`)
- Feature toggles (`ENABLE_MULTIMODAL_ANALYSIS`, etc.)

## Key Implementation Details

### Agent Creation Pattern
```python
# AgenticSDR uses singleton pattern
agent = await get_agentic_agent()  # Returns cached instance

# Pre-warming on startup prevents cold starts
# See main.py lines 100-116
```

### Supabase Integration
- Tables created via SQL scripts in `/sqls/`
- pgvector for semantic search and memory
- Emotional state persistence for continuity
- Lead qualification scoring and tracking

### Multimodal Processing
- Images: OCR with Tesseract, visual analysis with Gemini
- Audio: Transcription with SpeechRecognition
- Documents: PDF/DOCX parsing with specialized libraries
- All media decrypted from Evolution API format

### Error Handling
- Gemini API retry with exponential backoff
- Fallback to OpenAI when Gemini fails
- Redis connection optional (in-memory fallback)
- Comprehensive logging with emoji categories

## Important Files and Locations

- **Main entry**: `main.py`
- **Agent logic**: `app/agents/agentic_sdr.py`
- **Team coordination**: `app/teams/sdr_team.py`
- **Webhook handler**: `app/api/webhooks.py`
- **Configuration**: `app/config.py`
- **Database schemas**: `sqls/tabela-*.sql`
- **Production config**: `prod/docker-compose.production.yml`

## Development Tips

### When Adding Features
1. Check existing agent capabilities in `agentic_sdr.py`
2. Review team agent implementations in `app/teams/agents/`
3. Consider configuration flags in `config.py`
4. Update relevant SQL migrations if database changes needed

### When Debugging
- Enable debug mode: `DEBUG=true` in `.env`
- Check emoji-categorized logs for quick issue identification
- Review `logs/app.log` for detailed traces
- Use `test_multimodal_complete.py` for comprehensive testing

### Performance Considerations
- AgenticSDR pre-warms on startup (3 retry attempts)
- Message buffer groups rapid messages (default 2s timeout)
- Smart text splitting prevents message truncation
- Redis caching reduces API calls

## External Dependencies

### Required Services
- **Supabase**: Database and vector storage
- **Evolution API**: WhatsApp messaging
- **Google API**: Gemini AI model
- **OpenAI API**: Fallback AI model (optional)
- **Redis**: Caching (optional but recommended)

### Optional Integrations
- **Google Calendar**: Meeting scheduling
- **Kommo CRM**: Lead management
- **Tesseract OCR**: Image text extraction