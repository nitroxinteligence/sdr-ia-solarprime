# SDR IA Solar Prime v0.2 - AGNO Teams Framework

Sistema inteligente de vendas para energia solar implementado com **AGNO Teams Framework**.

## 🏗️ Arquitetura

### Team Mode: COORDINATE

O sistema utiliza o modo **COORDINATE** do AGNO Teams, onde:
- **Helen SDR Master** atua como Team Leader
- Analisa requisições e delega para agentes especializados
- Sintetiza respostas dos agentes em uma resposta unificada

### 👥 Agentes Especializados

1. **QualificationAgent** 🎯
   - Qualificação de leads com score de 0-100
   - Classificação: HOT/WARM/COLD/UNQUALIFIED
   - Análise de critérios e potencial de conversão

2. **CalendarAgent** 📅
   - Integração com Google Calendar
   - Agendamento com rate limiting (5 req/s)
   - Verificação de disponibilidade
   - Sugestão de melhores horários

3. **FollowUpAgent** 🔄
   - Campanhas de nurturing personalizadas
   - Estratégias baseadas em temperatura do lead
   - Mensagens personalizadas e timing otimizado

4. **KnowledgeAgent** 📚
   - RAG (Retrieval-Augmented Generation)
   - Busca vetorial em base de conhecimento
   - Gestão de documentos e FAQs

5. **CRMAgent** 🏢
   - Integração com Kommo CRM
   - Sincronização automática de leads e deals
   - Pipeline: NOVO LEAD → EM NEGOCIAÇÃO → EM QUALIFICAÇÃO → QUALIFICADO → REUNIÃO AGENDADA → REUNIÃO FINALIZADA → NÃO INTERESSADO

6. **BillAnalyzerAgent** 📊
   - OCR de contas de energia
   - Cálculo de economia (20% garantida)
   - Dimensionamento de sistema solar
   - Geração de propostas personalizadas

## 🚀 Instalação

### Pré-requisitos

- Python 3.11+
- Redis
- PostgreSQL (via Supabase)
- Google Calendar API
- Evolution API (WhatsApp)
- Kommo CRM

### Setup

1. Clone o repositório:
```bash
git clone <repo>
cd "SDR IA SolarPrime v0.2"
```

2. Instale dependências:
```bash
pip install -r requirements.txt
```

3. Configure variáveis de ambiente:
```bash
cp .env.example .env
# Edite .env com suas credenciais
```

4. Execute as migrações do banco:
```bash
python -m app.migrations.run
```

5. Inicie o servidor:
```bash
python main.py
```

## 📡 API Endpoints

### Teams API

#### Status do Team
```http
GET /teams/status
```

#### Qualificar Lead
```http
POST /teams/qualify-lead
{
  "lead_id": "string",
  "force_requalification": false
}
```

#### Agendar Reunião
```http
POST /teams/schedule-meeting
{
  "lead_id": "string",
  "date": "DD/MM/YYYY",
  "time": "HH:MM",
  "duration_minutes": 30,
  "meeting_type": "presentation"
}
```

#### Analisar Conta de Luz
```http
POST /teams/analyze-bill
{
  "lead_id": "string",
  "image_base64": "string",
  "generate_proposal": true
}
```

#### Criar Campanha de Nurturing
```http
POST /teams/create-campaign
{
  "lead_id": "string",
  "campaign_type": "standard",
  "duration_days": 7
}
```

### Webhooks

#### Evolution API Webhook
```http
POST /webhooks/evolution
```
Recebe eventos do WhatsApp via Evolution API.

## 🔧 Configuração

### Variáveis de Ambiente

```env
# API
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false

# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=xxx

# Redis
REDIS_URL=redis://localhost:6379

# Evolution API
EVOLUTION_API_URL=http://localhost:8080
EVOLUTION_INSTANCE=xxx
EVOLUTION_API_KEY=xxx

# Google Calendar
GOOGLE_CALENDAR_CREDENTIALS=xxx

# Kommo CRM
KOMMO_BASE_URL=https://xxx.kommo.com
KOMMO_SUBDOMAIN=xxx
KOMMO_PIPELINE_ID=xxx
KOMMO_LONG_LIVED_TOKEN=xxx

# OpenAI/Anthropic
OPENAI_API_KEY=xxx
ANTHROPIC_API_KEY=xxx
```

## 📊 Banco de Dados

### Tabelas Principais

- `leads` - Informações dos leads
- `leads_qualifications` - Qualificações dos leads
- `conversations` - Conversas do WhatsApp
- `messages` - Mensagens trocadas
- `calendar_events` - Reuniões agendadas
- `follow_ups` - Follow-ups agendados
- `knowledge_base` - Base de conhecimento
- `embeddings` - Embeddings para RAG
- `proposals` - Propostas geradas
- `crm_mappings` - Mapeamento com Kommo CRM

## 🎯 Fluxo de Operação

1. **Recepção de Mensagem**
   - Webhook recebe mensagem do WhatsApp
   - Sistema identifica ou cria lead

2. **Processamento pelo Team**
   - Helen SDR Master analisa a mensagem
   - Delega para agentes especializados conforme necessário
   - Sintetiza resposta unificada

3. **Ações dos Agentes**
   - QualificationAgent avalia potencial
   - CalendarAgent agenda reuniões
   - FollowUpAgent mantém engajamento
   - KnowledgeAgent responde dúvidas
   - CRMAgent sincroniza dados
   - BillAnalyzerAgent analisa contas

4. **Resposta ao Lead**
   - Mensagem personalizada via WhatsApp
   - Ações automatizadas (agendamento, follow-up, etc.)

## 🔍 Monitoramento

### Métricas Disponíveis

```http
GET /teams/metrics
```

Retorna:
- Total de leads
- Taxa de qualificação
- Mensagens processadas hoje
- Conversas ativas
- Reuniões agendadas

### Health Check

```http
GET /health
```

Verifica status de:
- Redis
- Supabase
- Team SDR
- Serviços externos

## 🚦 Rate Limiting

- **Google Calendar**: 5 requisições/segundo
- **WhatsApp**: 10 mensagens/minuto por lead
- **Kommo CRM**: Configurável

## 🔒 Segurança

- Autenticação via API Keys
- Rate limiting por IP e por lead
- Validação de webhooks
- Sanitização de inputs
- Logs auditáveis

## 📝 Logs

Logs são salvos em `logs/app.log` com rotação diária e retenção de 7 dias.

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Proprietário - Solar Prime © 2024

## 👨‍💻 Desenvolvido com

- **AGNO Teams Framework** - Multi-agent orchestration
- **FastAPI** - Web framework
- **Supabase** - Database and auth
- **Redis** - Caching and rate limiting
- **Evolution API** - WhatsApp integration
- **Google Calendar API** - Meeting scheduling
- **Kommo CRM** - Customer relationship management