# 📅 Google Calendar - Guia Completo de Configuração e Uso

## 📋 Índice
1. [Visão Geral](#visão-geral)
2. [Arquitetura do Sistema](#arquitetura-do-sistema)
3. [Configuração Inicial](#configuração-inicial)
4. [Fluxo de Funcionamento](#fluxo-de-funcionamento)
5. [Teste e Validação](#teste-e-validação)
6. [Troubleshooting](#troubleshooting)
7. [Melhorias Implementadas](#melhorias-implementadas)

## 🎯 Visão Geral

O sistema de Google Calendar do SDR IA SolarPrime permite agendamento automático de reuniões através do WhatsApp, integrando-se perfeitamente com o fluxo de vendas.

### Recursos Principais
- ✅ Agendamento automático de reuniões
- ✅ Verificação de disponibilidade
- ✅ Criação de links do Google Meet
- ✅ Reagendamento e cancelamento
- ✅ Lembretes automáticos
- ✅ Sincronização com Supabase

## 🏗️ Arquitetura do Sistema

```
Usuário WhatsApp
        ↓
AGENTIC SDR (agentic_sdr.py)
        ↓
[Detecta intenção de agendamento]
        ↓
SDR Team (sdr_team.py)
        ↓
CalendarAgent (calendar.py)
        ↓
GoogleCalendarClient (google_calendar.py)
        ↓
Google Calendar API v3
```

### Componentes Principais

#### 1. **AGENTIC SDR** (`app/agents/agentic_sdr.py`)
- Detecta palavras-chave de agendamento
- Calcula score de complexidade
- Delega ao SDR Team quando necessário

#### 2. **SDR Team** (`app/teams/sdr_team.py`)
- Coordena agentes especializados
- Ativa CalendarAgent para agendamento
- Gerencia contexto e histórico

#### 3. **CalendarAgent** (`app/teams/agents/calendar.py`)
- Tools para agendamento
- Validação de horário comercial
- Integração com banco de dados

#### 4. **GoogleCalendarClient** (`app/integrations/google_calendar.py`)
- Autenticação via Service Account
- Rate limiting e retry logic
- Operações CRUD de eventos

## ⚙️ Configuração Inicial

### 1. Configurar Google Cloud Console

1. Acesse [Google Cloud Console](https://console.cloud.google.com)
2. Crie ou selecione um projeto
3. Ative a **Google Calendar API**
4. Crie uma **Service Account**:
   ```
   IAM & Admin → Service Accounts → Create Service Account
   ```
5. Gere uma chave privada (JSON)
6. Conceda permissões ao Service Account no calendário:
   - Abra Google Calendar
   - Configurações → Adicionar pessoas
   - Adicione o email do Service Account com permissão "Fazer alterações em eventos"

### 2. Configurar Variáveis de Ambiente

Adicione ao arquivo `.env`:

```env
# Flags de Habilitação (OBRIGATÓRIO)
ENABLE_CALENDAR_AGENT=true
ENABLE_CALENDAR_INTEGRATION=true
ENABLE_SDR_TEAM=true

# Google Calendar
GOOGLE_USE_SERVICE_ACCOUNT=true
GOOGLE_SERVICE_ACCOUNT_EMAIL=seu-service-account@projeto.iam.gserviceaccount.com
GOOGLE_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n
GOOGLE_PROJECT_ID=seu-projeto-id
GOOGLE_PRIVATE_KEY_ID=id-da-chave-privada
GOOGLE_CLIENT_ID=client-id-numerico
GOOGLE_CALENDAR_ID=email-do-calendario@gmail.com
DISABLE_GOOGLE_CALENDAR=false
```

### 3. Estrutura de Banco de Dados

Execute o SQL para criar a tabela:

```sql
CREATE TABLE calendar_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lead_id TEXT NOT NULL,
    google_event_id TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE NOT NULL,
    location TEXT,
    description TEXT,
    event_type TEXT,
    status TEXT DEFAULT 'scheduled',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## 🔄 Fluxo de Funcionamento

### 1. Detecção de Intenção

O sistema detecta automaticamente quando o usuário quer agendar:

**Palavras-chave detectadas:**
- agendar, reunião, marcar, horário
- disponibilidade, agenda, calendário
- encontro, meeting, apresentação
- reagendar, remarcar, cancelar reunião
- data, dia, semana que vem, amanhã
- manhã, tarde, noite, às, horas

### 2. Processo de Agendamento

```python
# Fluxo simplificado
1. Usuário: "Quero agendar uma reunião"
2. AGENTIC SDR detecta intenção (score >= 0.7)
3. Delega ao SDR Team com CalendarAgent
4. CalendarAgent coleta informações:
   - Data e horário desejado
   - Duração da reunião
   - Participantes (emails)
5. Verifica disponibilidade
6. Cria evento no Google Calendar
7. Retorna confirmação com link do Meet
```

### 3. Exemplo de Conversa

```
Cliente: "Gostaria de agendar uma reunião para amanhã"
Helen: "Claro! Tenho alguns horários disponíveis amanhã:
        - 09:00
        - 14:00 
        - 16:00
        Qual horário seria melhor para você?"
Cliente: "14h seria perfeito"
Helen: "Ótimo! Preciso do seu email para enviar o convite"
Cliente: "cliente@empresa.com"
Helen: "✅ Reunião agendada para amanhã às 14:00!
        📅 Duração: 30 minutos
        📹 Link do Meet: [será enviado por email]
        Você receberá um lembrete 30 minutos antes."
```

## 🧪 Teste e Validação

### Executar Script de Teste

```bash
# Tornar executável
chmod +x test_google_calendar.py

# Executar testes
python test_google_calendar.py
```

### Testes Realizados

1. ✅ **Verificação de Configurações**
2. ✅ **Autenticação com Google**
3. ✅ **Listagem de Eventos**
4. ✅ **Criação de Evento**
5. ✅ **Verificação de Disponibilidade**
6. ✅ **Exclusão de Evento**
7. ✅ **CalendarAgent Tools**

### Verificar Logs

```bash
# Ver logs em tempo real
docker logs -f sdr-api

# Filtrar logs de calendário
docker logs sdr-api | grep "📅"
```

## 🔧 Troubleshooting

### Problema: CalendarAgent não é ativado

**Sintomas:**
- Mensagens sobre agendamento não são processadas
- CalendarAgent aparece como desabilitado nos logs

**Soluções:**
1. Verificar flags no `.env`:
   ```env
   ENABLE_CALENDAR_AGENT=true
   ENABLE_CALENDAR_INTEGRATION=true
   ENABLE_SDR_TEAM=true
   ```

2. Reiniciar o serviço:
   ```bash
   docker-compose restart sdr-api
   ```

### Problema: Erro de autenticação

**Sintomas:**
- "403 Forbidden" nos logs
- "Service Account não tem permissão"

**Soluções:**
1. Verificar se Service Account tem permissão no calendário
2. Confirmar que a chave privada está correta no `.env`
3. Verificar se a API está habilitada no Google Cloud

### Problema: Eventos não são criados

**Sintomas:**
- Confirmação de agendamento mas evento não aparece

**Soluções:**
1. Verificar `GOOGLE_CALENDAR_ID` no `.env`
2. Testar com script: `python test_google_calendar.py`
3. Verificar quota da API no Google Cloud Console

## 🚀 Melhorias Implementadas

### 1. Detecção Aprimorada
- ✅ Mais palavras-chave para detecção
- ✅ Score aumentado (0.4 → 0.8) para garantir ativação
- ✅ Logs detalhados para debug

### 2. Configurações Adicionadas
- ✅ Flags de habilitação no `.env`
- ✅ Validação de configurações no startup

### 3. Debug Melhorado
- ✅ Logs em cada etapa do processo
- ✅ Script de teste completo
- ✅ Mensagens de erro detalhadas

### 4. Rate Limiting Robusto
- ✅ Exponential backoff com jitter
- ✅ Quota management para Service Account
- ✅ Até 5 tentativas com delays progressivos

## 📊 Métricas e Monitoramento

### KPIs Importantes
- Taxa de agendamento bem-sucedido
- Tempo médio de resposta
- Conflitos de horário evitados
- Taxa de reagendamento

### Logs para Monitorar
```bash
# Agendamentos criados
grep "✅ Evento criado" logs/

# Erros de calendário
grep "❌ Erro ao criar evento" logs/

# CalendarAgent ativações
grep "📅 CALENDÁRIO DETECTADO" logs/
```

## 🔐 Segurança

### Boas Práticas
1. **Nunca commitar credenciais** - Use `.env` e `.gitignore`
2. **Rotação de chaves** - Renove Service Account keys periodicamente
3. **Princípio do menor privilégio** - Service Account só com permissões necessárias
4. **Logs seguros** - Não logar informações sensíveis

## 📚 Referências

- [Google Calendar API v3 Documentation](https://developers.google.com/calendar/api/v3/reference)
- [Service Account Setup Guide](https://developers.google.com/identity/protocols/oauth2/service-account)
- [Python Client Library](https://github.com/googleapis/google-api-python-client)
- [Rate Limiting Best Practices](https://cloud.google.com/apis/design/rate_limiting)

---

**Última atualização:** Agosto 2025
**Versão:** 2.0
**Autor:** SDR IA Team