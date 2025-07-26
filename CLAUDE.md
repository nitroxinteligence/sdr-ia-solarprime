# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the **SDR IA SolarPrime** project - an intelligent sales agent for solar energy that automates lead qualification and meeting scheduling via WhatsApp. Built by Nitrox AI for Solarprime Boa Viagem, it uses AI to handle the entire sales process from initial contact to meeting scheduling.

## Tech Stack

- **Backend Framework**: FastAPI with Uvicorn
- **AI Framework**: AGnO Framework with Google Gemini 2.5 Pro
- **Database**: Supabase (PostgreSQL)
- **Queue/Cache**: Redis with Celery
- **WhatsApp Integration**: Evolution API
- **CRM Integration**: Kommo CRM
- **Infrastructure**: Hostinger VPS (Ubuntu 22.04) with Nginx

## Common Development Commands

### Running the Application
```bash
# Development server
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Production server
uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4

# Using Docker
docker-compose up -d
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=api --cov=services --cov-report=html

# Run specific test file
pytest tests/unit/test_ai_agent.py

# Run integration tests only
pytest tests/integration/
```

### Database Operations
```bash
# Run Supabase migrations
supabase migration up

# Create new migration
supabase migration new <migration_name>

# Reset database (development only)
supabase db reset
```

### Task Queue Management
```bash
# Start Celery worker
celery -A services.tasks worker --loglevel=info

# Start Celery beat (scheduler)
celery -A services.tasks beat --loglevel=info

# Monitor tasks
celery -A services.tasks flower
```

### Deployment
```bash
# Deploy to production
./scripts/deploy.sh

# Backup production data
./scripts/backup.sh

# Monitor system status
./scripts/monitoring.sh
```

## High-Level Architecture

### Core Flow
1. **WhatsApp Message Reception**: Evolution API sends webhook to `/webhook/whatsapp`
2. **Message Processing**: AI agent processes multimodal content (text, audio, images, PDFs)
3. **Lead Qualification**: Agent qualifies leads through conversational stages
4. **CRM Integration**: Kommo CRM updated in real-time with lead status
5. **Follow-up System**: Automated follow-ups based on configured rules
6. **Reporting**: Weekly reports sent to WhatsApp group

### Key Services

#### AI Agent Service (`services/ai_agent.py`)
- Manages conversation flow using AGnO Framework
- Integrates with Google Gemini 2.5 Pro for natural language processing
- Maintains conversation context and memory
- Handles qualification logic and scoring

#### WhatsApp Service (`services/whatsapp_service.py`)
- Interfaces with Evolution API
- Handles multimodal message processing
- Implements typing simulation for natural conversation
- Manages message delivery and status

#### Kommo Service (`services/kommo_service.py`)
- Creates and updates leads in CRM
- Manages pipeline stages based on qualification
- Handles meeting scheduling and calendar integration
- Syncs custom fields and tags

#### Task Service (`services/tasks.py`)
- Manages asynchronous operations with Celery
- Handles follow-up scheduling
- Processes report generation
- Manages retry logic for failed operations

### Qualification Pipeline

The system follows a structured qualification flow:
1. **Identification**: Capture lead name and create profile
2. **Solution Discovery**: Identify which of 5 solar solutions fits
3. **Value Assessment**: Analyze energy bill value (with OCR support)
4. **Competitive Analysis**: Check for existing discounts/competitors
5. **Meeting Scheduling**: Book meetings via Kommo integration

### Database Schema

Key tables in Supabase:
- `profiles`: Lead/customer data
- `conversations`: Chat sessions
- `messages`: Complete message history
- `leads`: Qualification and CRM data
- `follow_ups`: Scheduled follow-up tasks
- `reports`: Analytics and reporting data

### Security Considerations

- All sensitive data encrypted at rest
- SSL/TLS for all external communications
- JWT tokens for API authentication
- Webhook signature verification
- Rate limiting implemented
- LGPD compliance for Brazilian data protection

## Important Notes

1. **Environment Variables**: Copy `.env.example` to `.env` and fill in all required API keys
2. **Follow-up Timing**: Configurable via `AI_RESPONSE_DELAY_SECONDS` and business hours settings
3. **Report Schedule**: Weekly reports configurable via `REPORT_DAY_OF_WEEK` and `REPORT_TIME`
4. **Rate Limits**: Be aware of API rate limits for Gemini, Evolution API, and Kommo
5. **Error Handling**: All services implement retry logic with exponential backoff