# Configuração de Variáveis de Ambiente - SDR IA SolarPrime

Este documento detalha todas as variáveis de ambiente necessárias para configurar e executar o agente SDR IA SolarPrime.

## 📋 Visão Geral

O sistema utiliza variáveis de ambiente para configurar integrações, comportamentos e parâmetros operacionais. Todas as variáveis devem ser definidas no arquivo `.env` na raiz do projeto.

## 🔧 Configuração Inicial

### 1. Criar arquivo .env
```bash
# Copiar template
cp .env.example .env

# Editar com suas configurações
nano .env
```

### 2. Configurar permissões
```bash
# Restringir acesso ao arquivo .env
chmod 600 .env

# Garantir propriedade correta
chown $USER:$USER .env
```

## 📦 Categorias de Variáveis

### 🌐 Configurações Básicas

| Variável | Descrição | Tipo | Padrão | Obrigatório |
|----------|-----------|------|---------|-------------|
| `API_PORT` | Porta onde a API será executada | Integer | `8000` | Sim |
| `ENVIRONMENT` | Ambiente de execução | String | `development` | Sim |
| `DEBUG` | Ativar modo debug | Boolean | `false` | Sim |
| `LOG_LEVEL` | Nível de log | String | `INFO` | Sim |
| `TZ` | Timezone do sistema | String | `America/Sao_Paulo` | Sim |

```env
# Exemplo de configuração básica
API_PORT=8000
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
TZ=America/Sao_Paulo
```

### 🤖 Google Gemini AI

| Variável | Descrição | Tipo | Exemplo | Obrigatório |
|----------|-----------|------|---------|-------------|
| `GEMINI_API_KEY` | Chave da API do Google Gemini | String | `AIza...` | Sim |

```env
# Configuração do Gemini
GEMINI_API_KEY="AIzaSyC_your_actual_api_key_here"
```

**Como obter**:
1. Acessar [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Criar ou selecionar projeto
3. Gerar API Key
4. Copiar e colar no .env

### 📅 Google Calendar

| Variável | Descrição | Tipo | Padrão | Obrigatório |
|----------|-----------|------|---------|-------------|
| `GOOGLE_USE_SERVICE_ACCOUNT` | Usar Service Account | Boolean | `true` | Sim |
| `GOOGLE_SERVICE_ACCOUNT_EMAIL` | Email da Service Account | String | - | Sim* |
| `GOOGLE_PRIVATE_KEY` | Chave privada da Service Account | String | - | Sim* |
| `GOOGLE_PROJECT_ID` | ID do projeto Google Cloud | String | - | Sim* |
| `GOOGLE_PRIVATE_KEY_ID` | ID da chave privada | String | - | Sim* |
| `GOOGLE_CLIENT_ID` | ID do cliente | String | - | Sim* |
| `GOOGLE_CALENDAR_ID` | ID do calendário | String | - | Sim |
| `GOOGLE_CALENDAR_OWNER_EMAIL` | Email do proprietário (opcional) | String | - | Não |
| `DISABLE_GOOGLE_CALENDAR` | Desabilitar integração | Boolean | `false` | Não |

*Obrigatório apenas se `GOOGLE_USE_SERVICE_ACCOUNT=true`

```env
# Configuração do Google Calendar (Service Account)
GOOGLE_USE_SERVICE_ACCOUNT=true
GOOGLE_SERVICE_ACCOUNT_EMAIL=sdr-agent@seu-projeto.iam.gserviceaccount.com
GOOGLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQ...\n-----END PRIVATE KEY-----\n"
GOOGLE_PROJECT_ID=seu-projeto-123456
GOOGLE_PRIVATE_KEY_ID=a1b2c3d4e5f6
GOOGLE_CLIENT_ID=123456789012345678901
GOOGLE_CALENDAR_ID=vendas@suaempresa.com.br
```

**Como configurar Service Account**:
1. Acessar [Google Cloud Console](https://console.cloud.google.com)
2. Criar novo projeto ou selecionar existente
3. Ativar Google Calendar API
4. Criar Service Account
5. Gerar chave JSON
6. Extrair valores do JSON para o .env
7. Compartilhar calendário com email da Service Account

### 💬 Evolution API (WhatsApp)

| Variável | Descrição | Tipo | Exemplo | Obrigatório |
|----------|-----------|------|---------|-------------|
| `EVOLUTION_API_URL` | URL da Evolution API | String | `https://api.evolution.com` | Sim |
| `EVOLUTION_API_KEY` | Chave de API | String | `B6D711FC...` | Sim |
| `EVOLUTION_INSTANCE_NAME` | Nome da instância | String | `sdr-agent` | Sim |

```env
# Configuração Evolution API
EVOLUTION_API_URL="https://evolution.suaempresa.com"
EVOLUTION_API_KEY="B6D711FCDE4D44E7936F2737593412C9"
EVOLUTION_INSTANCE_NAME="sdr-solarprime"
```

### 🗄️ Supabase (Banco de Dados)

| Variável | Descrição | Tipo | Exemplo | Obrigatório |
|----------|-----------|------|---------|-------------|
| `SUPABASE_URL` | URL do projeto Supabase | String | `https://xxx.supabase.co` | Sim |
| `SUPABASE_SERVICE_KEY` | Service Role Key | String | `eyJhbGc...` | Sim |

```env
# Configuração Supabase
SUPABASE_URL="https://abcdefghijk.supabase.co"
SUPABASE_SERVICE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Importante**: Use a Service Role Key, não a anon key!

### 🔴 Redis (Cache e Filas)

| Variável | Descrição | Tipo | Padrão | Obrigatório |
|----------|-----------|------|---------|-------------|
| `REDIS_URL` | URL completa do Redis | String | `redis://localhost:6379` | Sim |
| `REDIS_HOST` | Host do Redis (alternativo) | String | `localhost` | Não |
| `REDIS_PORT` | Porta do Redis (alternativo) | Integer | `6379` | Não |
| `REDIS_PASSWORD` | Senha do Redis (se aplicável) | String | - | Não |
| `REDIS_DB` | Número do banco Redis | Integer | `0` | Não |

```env
# Configuração Redis (local)
REDIS_URL="redis://localhost:6379/0"

# Configuração Redis (com senha)
REDIS_URL="redis://:senha_super_secreta@redis.suaempresa.com:6379/0"

# Configuração Redis (Docker)
REDIS_URL="redis://redis:6379/0"
```

### 💼 Kommo CRM

| Variável | Descrição | Tipo | Exemplo | Obrigatório |
|----------|-----------|------|---------|-------------|
| `KOMMO_SUBDOMAIN` | Subdomínio do Kommo | String | `suaempresa` | Sim |
| `KOMMO_ACCESS_TOKEN` | Token de acesso | String | `eyJ0eXAi...` | Sim |
| `KOMMO_REFRESH_TOKEN` | Token de refresh | String | `def50200...` | Sim |
| `KOMMO_PIPELINE_ID` | ID do pipeline | String | `1234567` | Sim |

```env
# Configuração Kommo CRM
KOMMO_SUBDOMAIN="solarprime"
KOMMO_ACCESS_TOKEN="eyJ0eXAiOiJKV1QiLCJhbGciOiJS..."
KOMMO_REFRESH_TOKEN="def502007c2f0b8a9c6b4..."
KOMMO_PIPELINE_ID="7654321"
```

### ⚙️ Configurações do Agente

#### Horário Comercial

| Variável | Descrição | Tipo | Padrão | Validação |
|----------|-----------|------|---------|-----------|
| `BUSINESS_HOURS_START` | Início expediente | Integer | `8` | 0-23 |
| `BUSINESS_HOURS_END` | Fim expediente | Integer | `18` | 0-23 |
| `BUSINESS_DAYS` | Dias úteis | String | `1,2,3,4,5` | 1-7* |

*1=Segunda, 2=Terça, ..., 7=Domingo

```env
# Horário comercial
BUSINESS_HOURS_START=8
BUSINESS_HOURS_END=18
BUSINESS_DAYS="1,2,3,4,5"  # Segunda a Sexta
```

#### Sistema de Follow-up

| Variável | Descrição | Tipo | Padrão | Validação |
|----------|-----------|------|---------|-----------|
| `FOLLOW_UP_ENABLED` | Ativar follow-ups | Boolean | `true` | - |
| `FOLLOW_UP_DELAY_HOURS` | Horas entre tentativas | Integer | `24` | 1-168 |
| `FOLLOW_UP_MAX_ATTEMPTS` | Máximo de tentativas | Integer | `3` | 1-10 |

```env
# Follow-up automático
FOLLOW_UP_ENABLED=true
FOLLOW_UP_DELAY_HOURS=24
FOLLOW_UP_MAX_ATTEMPTS=3
```

#### Comportamento da IA

| Variável | Descrição | Tipo | Padrão | Validação |
|----------|-----------|------|---------|-----------|
| `AI_RESPONSE_DELAY_SECONDS` | Delay simulando digitação | Integer | `2` | 0-10 |
| `AI_MAX_RETRIES` | Tentativas em caso de erro | Integer | `3` | 1-5 |
| `AI_TIMEOUT_SECONDS` | Timeout da API | Integer | `30` | 10-120 |

```env
# Comportamento da IA
AI_RESPONSE_DELAY_SECONDS=2
AI_MAX_RETRIES=3
AI_TIMEOUT_SECONDS=30
```

#### Sistema de Relatórios

| Variável | Descrição | Tipo | Padrão | Validação |
|----------|-----------|------|---------|-----------|
| `REPORT_ENABLED` | Ativar relatórios | Boolean | `true` | - |
| `REPORT_DAY_OF_WEEK` | Dia da semana | Integer | `1` | 0-6* |
| `REPORT_TIME` | Horário do envio | String | `09:00` | HH:MM |
| `REPORT_WHATSAPP_GROUP` | ID do grupo WhatsApp | String | - | - |

*0=Domingo, 1=Segunda, ..., 6=Sábado

```env
# Relatórios semanais
REPORT_ENABLED=true
REPORT_DAY_OF_WEEK=1  # Segunda-feira
REPORT_TIME="09:00"
REPORT_WHATSAPP_GROUP="5511999999999-1234567890@g.us"
```

### 🔐 Segurança

| Variável | Descrição | Tipo | Recomendação | Obrigatório |
|----------|-----------|------|--------------|-------------|
| `JWT_SECRET` | Chave secreta JWT | String | 32+ caracteres | Sim |
| `WEBHOOK_SIGNATURE_SECRET` | Segredo webhook Evolution | String | 32+ caracteres | Sim |
| `API_KEY` | Chave API interna | String | UUID v4 | Não |
| `ALLOWED_ORIGINS` | CORS origins permitidas | String | URLs separadas por vírgula | Não |

```env
# Segurança
JWT_SECRET="sua_chave_super_secreta_com_32_caracteres_ou_mais"
WEBHOOK_SIGNATURE_SECRET="outro_segredo_para_validar_webhooks"
API_KEY="550e8400-e29b-41d4-a716-446655440000"
ALLOWED_ORIGINS="https://app.suaempresa.com,https://admin.suaempresa.com"
```

**Gerar secrets seguros**:
```bash
# Gerar JWT_SECRET
openssl rand -hex 32

# Gerar WEBHOOK_SIGNATURE_SECRET
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Gerar API_KEY (UUID)
python -c "import uuid; print(str(uuid.uuid4()))"
```

## 📄 Arquivo .env Completo (Exemplo)

```env
# ===========================
# CONFIGURAÇÕES BÁSICAS
# ===========================
API_PORT=8000
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
TZ=America/Sao_Paulo

# ===========================
# GOOGLE GEMINI AI
# ===========================
GEMINI_API_KEY="AIzaSyC_sua_chave_api_aqui"

# ===========================
# GOOGLE CALENDAR
# ===========================
GOOGLE_USE_SERVICE_ACCOUNT=true
GOOGLE_SERVICE_ACCOUNT_EMAIL=sdr-agent@projeto-solar.iam.gserviceaccount.com
GOOGLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...\n-----END PRIVATE KEY-----\n"
GOOGLE_PROJECT_ID=projeto-solar-123456
GOOGLE_PRIVATE_KEY_ID=a1b2c3d4e5f6g7h8i9j0
GOOGLE_CLIENT_ID=123456789012345678901
GOOGLE_CALENDAR_ID=vendas@solarprime.com.br
DISABLE_GOOGLE_CALENDAR=false

# ===========================
# EVOLUTION API (WHATSAPP)
# ===========================
EVOLUTION_API_URL="https://evolution.solarprime.com.br"
EVOLUTION_API_KEY="B6D711FCDE4D44E7936F2737593412C9"
EVOLUTION_INSTANCE_NAME="sdr-solarprime-prod"

# ===========================
# SUPABASE
# ===========================
SUPABASE_URL="https://xyzabcdefghijk.supabase.co"
SUPABASE_SERVICE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh5emFiY2RlZmdoaWprIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTY5MDAwMDAwMCwiZXhwIjoxOTk5OTk5OTk5fQ.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# ===========================
# REDIS
# ===========================
REDIS_URL="redis://localhost:6379/0"

# ===========================
# KOMMO CRM
# ===========================
KOMMO_SUBDOMAIN="solarprime"
KOMMO_ACCESS_TOKEN="eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6IjA5YzNjNmY4ZjY2..."
KOMMO_REFRESH_TOKEN="def502007c2f0b8a9c6b4d3e9f8a7b6c5d4e3f2a1b0c9d8e7f6a5b4c3d2e1f0"
KOMMO_PIPELINE_ID="7654321"

# ===========================
# CONFIGURAÇÕES DO AGENTE
# ===========================

# Horário comercial
BUSINESS_HOURS_START=8
BUSINESS_HOURS_END=18
BUSINESS_DAYS="1,2,3,4,5"  # Segunda a Sexta

# Follow-up
FOLLOW_UP_ENABLED=true
FOLLOW_UP_DELAY_HOURS=24
FOLLOW_UP_MAX_ATTEMPTS=3

# Comportamento IA
AI_RESPONSE_DELAY_SECONDS=2
AI_MAX_RETRIES=3
AI_TIMEOUT_SECONDS=30

# Relatórios
REPORT_ENABLED=true
REPORT_DAY_OF_WEEK=1  # Segunda-feira
REPORT_TIME="09:00"
REPORT_WHATSAPP_GROUP="5585999999999-1234567890@g.us"

# ===========================
# SEGURANÇA
# ===========================
JWT_SECRET="sua_chave_super_secreta_de_pelo_menos_32_caracteres_aqui"
WEBHOOK_SIGNATURE_SECRET="outro_segredo_super_forte_para_validar_webhooks_evolution"
API_KEY="550e8400-e29b-41d4-a716-446655440000"
ALLOWED_ORIGINS="https://app.solarprime.com.br,https://admin.solarprime.com.br"

# ===========================
# DESENVOLVIMENTO
# ===========================

# Sentry (monitoramento de erros)
SENTRY_DSN=""  # Adicionar se usar Sentry

# Prometheus (métricas)
ENABLE_METRICS=true
METRICS_PORT=9090
```

## 🚀 Configurações por Ambiente

### Development
```env
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
REDIS_URL="redis://localhost:6379/0"
DISABLE_GOOGLE_CALENDAR=true  # Para testes sem calendário
```

### Staging
```env
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=INFO
REDIS_URL="redis://redis-staging.interno:6379/0"
REPORT_WHATSAPP_GROUP="5511999999999-staging@g.us"
```

### Production
```env
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING
REDIS_URL="redis://redis-prod.interno:6379/0"
SENTRY_DSN="https://xxxxx@sentry.io/yyyy"
```

## 🐳 Integração com Docker

### Docker Compose
No `docker-compose.yml`, as variáveis podem ser passadas de duas formas:

```yaml
services:
  sdr-api:
    environment:
      # Método 1: Valores diretos
      - ENVIRONMENT=production
      - DEBUG=false
      
      # Método 2: Do arquivo .env
      - REDIS_URL=${REDIS_URL}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    
    # Método 3: Arquivo .env completo
    env_file:
      - .env
```

### EasyPanel
No EasyPanel, adicione as variáveis através da interface:

1. Acessar configurações do app
2. Seção "Environment Variables"
3. Adicionar cada variável
4. Marcar como "Secret" para valores sensíveis
5. Deploy para aplicar mudanças

## 🔒 Boas Práticas de Segurança

### 1. Nunca commitar o .env
```bash
# Adicionar ao .gitignore
echo ".env" >> .gitignore
echo ".env.*" >> .gitignore
```

### 2. Usar secrets fortes
```bash
# Script para gerar secrets
#!/bin/bash
echo "JWT_SECRET=$(openssl rand -hex 32)"
echo "WEBHOOK_SIGNATURE_SECRET=$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
echo "API_KEY=$(python -c 'import uuid; print(str(uuid.uuid4()))')"
```

### 3. Rotacionar credenciais regularmente
- API Keys: A cada 90 dias
- Tokens JWT: A cada 30 dias
- Senhas de banco: A cada 180 dias

### 4. Usar variáveis específicas por ambiente
```bash
# Estrutura recomendada
.env.development
.env.staging  
.env.production
.env.example  # Template sem valores reais
```

### 5. Criptografar valores sensíveis
Para ambientes de produção, considere usar:
- AWS Secrets Manager
- Google Secret Manager
- HashiCorp Vault
- Kubernetes Secrets

## 🧪 Validação de Configuração

### Script de Validação
```python
#!/usr/bin/env python3
# validate_env.py

import os
import sys
from dotenv import load_dotenv

# Carregar .env
load_dotenv()

# Variáveis obrigatórias
required_vars = [
    'GEMINI_API_KEY',
    'EVOLUTION_API_URL',
    'EVOLUTION_API_KEY',
    'SUPABASE_URL',
    'SUPABASE_SERVICE_KEY',
    'REDIS_URL',
    'KOMMO_ACCESS_TOKEN',
    'JWT_SECRET'
]

# Validar
missing = []
for var in required_vars:
    if not os.getenv(var):
        missing.append(var)

if missing:
    print(f"❌ Variáveis faltando: {', '.join(missing)}")
    sys.exit(1)
else:
    print("✅ Todas as variáveis obrigatórias configuradas!")
```

### Executar validação
```bash
python validate_env.py
```

## 📚 Referências

- [12 Factor App - Config](https://12factor.net/config)
- [Google Cloud Service Accounts](https://cloud.google.com/iam/docs/service-accounts)
- [Supabase Environment Variables](https://supabase.com/docs/guides/getting-started/local-development#environment-variables)
- [Redis Configuration](https://redis.io/docs/manual/config/)
- [Kommo API Authentication](https://www.kommo.com/support/kb/authentication/)

---

**Última atualização**: Janeiro 2025