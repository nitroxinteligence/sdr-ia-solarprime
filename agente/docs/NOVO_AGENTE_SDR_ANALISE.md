# 🚀 ANÁLISE COMPLETA: NOVO AGENTE SDR ULTRA ESCALÁVEL

# LEMBRE-SE: TODA A ESTRUTURA ANTIGA TEM MUITOS ERROS NO KOMMOCRM, ESTRUTURA DO AGNO E NO CALENDAR, ENTÃO ESSES SERVIÇOS EU PRECISO QUE VOCE IMPLEMENTE TUDO DO ZERO.

## 📋 SUMÁRIO EXECUTIVO

Este documento apresenta uma análise completa do sistema atual SDR IA SolarPrime e propõe uma nova arquitetura modular, simples e escalável para um agente SDR que:

- ✅ Atende leads via WhatsApp 
- ✅ Qualifica e agenda reuniões
- ✅ Integra com Kommo CRM e Google Calendar
- ✅ Processa imagens, áudios e documentos (PDF/DOCX)
- ✅ Usa AGnO Framework com Google Gemini 2.5 Pro

---

## 🎯 PERGUNTAS CRÍTICAS PARA DECISÃO

### 1. Arquitetura do Agente

Considerando que já temos um prompt super completo (500+ linhas), devemos:
- Opção A: Manter TUDO no prompt (fluxo, personalidade, objections, etc.) e criar tools apenas para ações externas?
- Opção B: Separar em módulos (prompt básico + tools inteligentes que gerenciam fluxo)?

**RESPOSTA**: Opção A. Eu acredito que muita coisa pode ser inserida no prompt.

### 2. Gestão de Estado e Contexto

O sistema atual usa Supabase para persistir contexto. Para o novo agente:
- Manter memória apenas no Supabase (como está)?
- Adicionar memória do AGnO Framework também?
- Qual estratégia para recuperar contexto de conversas antigas?

**RESPOSTA**: Manter memória no Supabase como está. O Agente deve recuperar as 100 últimas mensagens entre ele e o usuário.

### 3. Message Chunking e Timing

Vi que já existe lógica de chunking. Para melhorar:
- Qual o tamanho ideal de chunk que soa mais natural?
- Os delays atuais (3-8s) estão bons ou precisam ajuste?
- Deve variar timing baseado no horário/dia?

**RESPOSTA**: Não sei o tamanho ideal, você deve decidir. Sim, os delays estão viáveis, mas podemos aumentar para 15s. Você pode decidir sobre variar timing baseado no horário/dia.

### 4. Integração Kommo - Campos Críticos

No Kommo atual vejo campos customizados. Quais IDs exatos dos campos:
- field_id para Telefone? 
- field_id para Valor da Conta?
- pipeline_id e status_id corretos para cada estágio?

**RESPOSTA**: Todos os IDs e toda a estrutura é puxada do Long-Lived Token do Kommo CRM. As credenciais estão no arquivo .env

### 5. Horários de Agendamento

Para o Google Calendar:
- Quais calendários específicos verificar disponibilidade?
- Bloquear quais horários (almoço, fim de expediente)?
- Quanto tempo mínimo entre agendamentos?

**RESPOSTA**: Todas as credenciais do Calendar estão no arquivo .env. NÃO bloquear horários de almoço ou fim de expediente! 10min entre um agendamento e outro.

### 6. Follow-up Intelligence

O sistema tem follow-up de 30min e 24h. Dúvida:
- Deve parar após 2 tentativas ou continuar?
- Criar follow-ups diferentes para cada tipo de objeção?
- Follow-up especial para leads "quentes" que sumiram?

**RESPOSTA**: Se o lead não responder a primeira tentativa de 30min, e não responder a segunda tentativa de 24h, deve-se inserir no Kommo CRM como "NÃO INTERESSADO". Sim, deve-se ter um follow-up inteligente que deve analisar todo o contexto da conversa e agir de acordo com o contexto da conversa, não quero follow-ups genéricos, mas follow-ups que puxem o prompt do Agente + contexto da conversa. SIM, O AGENTE PRECISA ENTENDER O CONTEXTO E SER INTELIGENTE O SUFICIENTE PARA RESGATAR O LEAD QUENTE.

### 7. Decisão Técnica AGnO

Para otimizar performance:
- Usar reasoning=True sempre ou só em momentos complexos?
- Criar Toolkit com tools_to_stop_on para quais tools críticas?
- Storage e Memory do AGnO ou manter tudo no Supabase?

**RESPOSTA**: Reasoning somente em momentos complexos que necessita de mais raciocínio, reasoning sempre como true é desperdício de tempo e custos. Não sei sobre tools_to_stop_on. Mantenha tudo no Supabase.

### LEMBRE-SE:

NO KOMMO CRM DEVE FUNCIONAR DA SEGUINTE FORMA:

1. ASSIM QUE A IA RECEBER UM LEAD, DEVE ENVIAR PARA O KOMMO CRM E INSERIR NO CARD "NOVO LEAD"
2. DEPOIS QUE TIVER EM PROCESSO DE ATENDIMENTO VAI PARA "EM NEGOCIAÇÃO"
3. DEPOIS SE O LEAD SE INTERESSAR PELA SOLUÇÃO VAI PARA "EM QUALIFICAÇÃO"
4. SE QUALIFICADO VAI PARA O CARD "QUALIFICADO"
5. SE O LEAD QUISER AGENDAR E REALMENTE AGENDAR UMA REUNIÃO NO CALENDAR PARA "REUNIÃO AGENDADA"
6. SE O LEAD NÃO TIVER INTERESSE OU NÃO RESPONDER AOS FOLLOW-UPS E SUMIR, INSERIR NO CARD "NÃO INTERESSADO"

---

## 1. 📊 ANÁLISE DO SISTEMA ATUAL

### 1.1 Arquitetura Atual

O sistema atual funciona bem, mas apresenta problemas de organização e escalabilidade:

```
api/
├── main.py (FastAPI)
└── routes/webhooks.py → WhatsApp webhook

agents/
├── sdr_agent.py (1600+ linhas - MONOLÍTICO)
└── tools/ (apenas 3 tools)

services/
├── evolution_api.py
├── whatsapp_service.py
├── kommo_service.py (múltiplas versões)
└── google_calendar_service.py
```

### 1.2 Problemas Identificados

1. **Código Monolítico**: `sdr_agent.py` com 1600+ linhas fazendo tudo
2. **Múltiplas Versões**: Vários arquivos `_v2`, `_simple`, `_fixed`
3. **Acoplamento Forte**: Serviços muito dependentes entre si
4. **Tools Limitadas**: Apenas 3 tools customizadas (calendar, buffer, chunker)
5. **Complexidade Desnecessária**: Teams e workflows complexos não utilizados

### 1.3 Pontos Fortes (Infraestrutura 100% Funcional)

- ✅ **Webhook System**: Totalmente operacional recebendo eventos do WhatsApp
- ✅ **EasyPanel**: Deploy configurado e funcionando em produção
- ✅ **Evolution API**: Integração completa e estável com WhatsApp
- ✅ **FastAPI**: Servidor web rodando sem problemas
- ✅ **Nginx**: Proxy reverso configurado corretamente
- ✅ **SSL/HTTPS**: Certificados válidos e renovação automática
- ✅ **AGnO Framework**: Já integrado e funcionando
- ✅ **Google Gemini 2.5 Pro**: API funcionando perfeitamente
- ✅ **Kommo CRM**: Integração OAuth2 operacional
- ✅ **Google Calendar**: Agendamento funcionando
- ✅ **Supabase**: Banco de dados estável e performático
- ✅ **Redis/Celery**: Sistema de filas operacional

**IMPORTANTE**: Toda a infraestrutura está 100% funcional. O único problema é a complexidade excessiva do `sdr_agent.py` atual, que possui código monolítico e difícil manutenção. A proposta é simplificar APENAS o agente, mantendo toda infraestrutura existente.

---

## 2. 🔍 ANÁLISE DAS DOCUMENTAÇÕES E APIs

### 2.1 AGnO Framework (Detalhado)

**Definição**: Framework para criar agentes AI autônomos que operam com capacidade de tomada de decisão dinâmica.

**Componentes Principais:**
1. **Agent**: Programas AI que operam autonomamente
   - Tomada de decisão dinâmica
   - Suporte a conversações multi-turno
   - Gerenciamento de estado e memória

2. **Tools**: Funções com decorator @tool para interações externas
   - 80+ toolkits pré-construídos
   - Suporte para tools customizadas
   - Controle de execução (show_result, stop_after_tool_call)

3. **Reasoning**: Três abordagens disponíveis
   - **Reasoning Models**: Modelos especializados (OpenAI o-series, Claude 3.7)
   - **Reasoning Tools**: Tool dedicada "think" para raciocínio estruturado
   - **Reasoning Agents**: Sistema multi-agente com chain-of-thought

4. **Multimodal**: Suporte completo para múltiplos tipos de mídia
   - **Inputs**: Texto, imagem, áudio, vídeo (Gemini)
   - **Outputs**: Texto, imagem (DALL-E), áudio
   - **Document Readers**: PDF, DOCX, imagens de PDF

**Implementação Avançada:**
```python
from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools import tool

# Tool customizada com controle avançado
@tool(show_result=True, stop_after_tool_call=False)
async def process_whatsapp_message(phone: str, message: str) -> dict:
    """Processa mensagem do WhatsApp com contexto"""
    # Implementação
    return {"status": "processed", "response": "..."}

agent = Agent(
    name="SDR Agent",
    model=Gemini(id="gemini-2.5-pro"),
    tools=[process_whatsapp_message, ...],
    reasoning=True,  # Ativa raciocínio avançado
    instructions="Você é um SDR especialista...",
    # Configurações avançadas
    storage=True,  # Mantém histórico de conversas
    memory=True,   # Aprende preferências do usuário
    knowledge=True # Acesso a conhecimento específico do domínio
)
```

**Workflows**: Sistema determinístico para processos multi-agente
- Implementação em Python puro
- Gerenciamento de estado built-in
- Cache de resultados intermediários
- Suporte para processos paralelos

### 2.2 Evolution API v2 (Recursos Completos)

**Recursos de Mensagens:**
- **Texto**: Envio com formatação (negrito, itálico)
- **Mídia**: Vídeo, imagem, documento, áudio
- **Áudio**: Narração de áudio
- **Localização**: Compartilhamento de localização
- **Contatos**: Compartilhamento de contatos
- **Reactions**: Reações em mensagens
- **Link Preview**: Pré-visualização de links 🆕
- **Reply**: Respostas em thread 🆕
- **Mentions**: Menções individuais/grupo 🆕
- **Polls**: Enquetes 🆕
- **Status**: Stories/Status updates 🆕
- **Stickers**: Envio de figurinhas 🆕
- **List Messages**: Mensagens em lista

**Recursos de Perfil:**
- Atualizar nome
- Atualizar foto de perfil
- Atualizar status

**Recursos de Grupo:**
- Criar grupos
- Atualizar foto do grupo
- Atualizar nome/descrição
- Gerenciar participantes
- Recuperar informações do grupo

**Sistema de Webhooks:**
```json
{
  "enabled": true,
  "url": "https://seu-dominio.com/webhook",
  "webhook_by_events": true,  // URLs específicas por evento
  "events": [
    "QRCODE_UPDATED",
    "MESSAGES_UPSERT",
    "CONNECTION_UPDATE",
    "SEND_MESSAGE",
    "MESSAGES_UPDATE",
    "MESSAGES_DELETE",
    "GROUPS_UPSERT",
    "GROUP_UPDATE",
    "GROUP_PARTICIPANTS_UPDATE",
    "PRESENCE_UPDATE",
    "CONTACTS_UPSERT",
    "CONTACTS_UPDATE",
    "CHATS_UPSERT",
    "CHATS_UPDATE",
    "CHATS_DELETE",
    "CALL"
  ]
}
```

**Endpoints Essenciais:**
- `POST /message/sendText/{instance}` - Enviar texto
- `POST /message/sendMedia/{instance}` - Enviar mídia
- `POST /message/sendAudio/{instance}` - Enviar áudio
- `POST /message/sendPoll/{instance}` - Criar enquete
- `POST /message/sendList/{instance}` - Enviar lista
- `POST /message/sendReaction/{instance}` - Reagir a mensagem
- `GET /chat/fetchMessages/{instance}` - Buscar mensagens
- `GET /chat/fetchProfilePicUrl/{instance}` - Foto do perfil
- `POST /webhook/set/{instance}` - Configurar webhook
- `GET /webhook/get/{instance}` - Obter configuração webhook

**Integração com Redis**: Suporte para cache e gerenciamento de sessões

### 2.3 Kommo CRM (API Completa)

**Autenticação OAuth 2.0:**
- **Integration ID & Secret Key**: Obtidos no painel de desenvolvedor
- **Authorization Flow**: Modal, Widget webhook, ou Redirect URI
- **Access Token**: Validade 24 horas
- **Refresh Token**: Validade 3 meses (renovação automática)

**Fluxo de Autorização:**
```javascript
// 1. Obter código de autorização
function auth() {
  popup = window.open(
    'https://www.kommo.com/oauth?client_id=XXX&state=XXX&mode=post_message',
    'Allow Access',
    'width=750, height=580'
  );
}

// 2. Trocar código por tokens
POST /oauth2/access_token
{
  "client_id": "xxx",
  "client_secret": "xxx",
  "grant_type": "authorization_code",
  "code": "xxx",
  "redirect_uri": "xxx"
}
```

**Entidades Principais (20 tipos):**
1. **Account**: Configurações da conta
2. **Leads**: Gestão completa de leads
3. **Pipelines/Stages**: Funis customizáveis
4. **Contacts**: Base de contatos
5. **Users/Roles**: Gestão de usuários
6. **Tags**: Sistema de etiquetas
7. **Custom Fields**: Campos personalizados
8. **Tasks**: Tarefas e follow-ups
9. **Templates**: Templates de mensagens
10. **Webhooks**: Eventos em tempo real
11. **Companies**: Gestão de empresas
12. **Conversations**: Histórico de conversas
13. **Notes**: Anotações em entidades
14. **Calls**: Registro de ligações
15. **Events**: Eventos do calendário
16. **Sources**: Origem dos leads
17. **Incoming Leads**: Leads não processados
18. **Salesbot**: Automação de vendas
19. **Widgets**: Integrações visuais
20. **Lists**: Listas segmentadas

**Webhooks Disponíveis:**
- Lead criado/atualizado/deletado
- Contato criado/atualizado
- Task criada/completada
- Pipeline stage mudou
- Nota adicionada
- Eventos customizados

**Endpoints Essenciais:**
- `GET /api/v4/leads` - Listar leads
- `POST /api/v4/leads` - Criar lead
- `PATCH /api/v4/leads/{id}` - Atualizar lead
- `POST /api/v4/leads/{id}/notes` - Adicionar nota
- `POST /api/v4/tasks` - Criar tarefa
- `GET /api/v4/account` - Info da conta
- `POST /api/v4/webhooks` - Configurar webhook
- `GET /api/v4/users` - Listar usuários
- `GET /api/v4/pipelines` - Listar pipelines

**Rate Limits e Boas Práticas:**
- Implementar retry com backoff exponencial
- Armazenar tokens de forma segura
- Renovar tokens antes da expiração
- Usar webhooks para dados em tempo real

### 2.4 Google Calendar API v3 (Atualizado 2025)

**Visão Geral:**
- API RESTful completa para gerenciamento de calendários
- Suporte para OAuth2 e Service Account
- Integração nativa com Google Meet
- API Base URL: `https://www.googleapis.com/calendar/v3`

**Autenticação (Service Account Recomendado):**
```python
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Service Account (melhor para automação)
credentials = service_account.Credentials.from_service_account_file(
    'service-account-key.json',
    scopes=['https://www.googleapis.com/auth/calendar']
)

# Criar cliente do Calendar
service = build('calendar', 'v3', credentials=credentials)
```

**Recursos Principais:**

1. **Events Resource** - Gerenciamento de eventos
   - `events.insert()` - Criar evento
   - `events.update()` - Atualizar evento
   - `events.patch()` - Atualização parcial
   - `events.delete()` - Deletar evento
   - `events.get()` - Obter evento específico
   - `events.list()` - Listar eventos
   - `events.quickAdd()` - Criar evento com texto natural
   - `events.move()` - Mover evento entre calendários
   - `events.watch()` - Monitorar mudanças (webhooks)

2. **Calendars Resource** - Gerenciamento de calendários
   - `calendars.insert()` - Criar calendário
   - `calendars.update()` - Atualizar calendário
   - `calendars.patch()` - Atualização parcial
   - `calendars.delete()` - Deletar calendário
   - `calendars.get()` - Obter detalhes
   - `calendars.clear()` - Limpar eventos

3. **FreeBusy Resource** - Disponibilidade
   - `freebusy.query()` - Verificar disponibilidade

**Exemplo: Criar Evento com Google Meet:**
```python
event = {
    'summary': 'Reunião Solar - João Silva',
    'location': 'Online via Google Meet',
    'description': 'Apresentação da proposta de energia solar',
    'start': {
        'dateTime': '2025-02-01T10:00:00-03:00',
        'timeZone': 'America/Sao_Paulo',
    },
    'end': {
        'dateTime': '2025-02-01T11:00:00-03:00',
        'timeZone': 'America/Sao_Paulo',
    },
    'attendees': [
        {'email': 'cliente@example.com'},
        {'email': 'vendedor@solarprime.com'},
    ],
    'conferenceData': {
        'createRequest': {
            'requestId': 'unique-request-id',
            'conferenceSolutionKey': {'type': 'hangoutsMeet'}
        }
    },
    'reminders': {
        'useDefault': False,
        'overrides': [
            {'method': 'email', 'minutes': 24 * 60},
            {'method': 'popup', 'minutes': 30},
        ],
    },
    'sendNotifications': True,
    'sendUpdates': 'all'
}

# Criar evento com conferência
event = service.events().insert(
    calendarId='primary',
    body=event,
    conferenceDataVersion=1
).execute()

# Retorna link do Meet: event['conferenceData']['entryPoints'][0]['uri']
```

**Exemplo: Verificar Disponibilidade:**
```python
# Verificar disponibilidade para múltiplos calendários
body = {
    "timeMin": "2025-02-01T09:00:00-03:00",
    "timeMax": "2025-02-01T18:00:00-03:00",
    "timeZone": "America/Sao_Paulo",
    "items": [
        {"id": "vendedor1@solarprime.com"},
        {"id": "vendedor2@solarprime.com"}
    ]
}

freebusy = service.freebusy().query(body=body).execute()

# Processar slots ocupados
for calendar_id, calendar_info in freebusy['calendars'].items():
    busy_slots = calendar_info.get('busy', [])
    for slot in busy_slots:
        print(f"{calendar_id} ocupado: {slot['start']} até {slot['end']}")
```

**Recursos Avançados Implementados:**
- **Eventos Recorrentes**: Suporte completo com RRULE
- **Working Locations**: Gerenciar locais de trabalho (novo 2025)
- **Birthday Events**: Acesso a eventos de aniversário do Google Contacts
- **Event Types**: Filtrar por tipo (working location, out-of-office, focus time)
- **Attachments**: Adicionar anexos aos eventos
- **Extended Properties**: Metadados customizados
- **Color Coding**: 11 cores disponíveis para categorização

**Rate Limits e Quotas:**
- 1.000.000 requests/dia (quota padrão)
- 500 requests/100 segundos por usuário
- Implementar exponential backoff para retry

**Boas Práticas:**
- Usar campos parciais para otimizar respostas
- Implementar sincronização incremental com syncToken
- Cachear resultados de freebusy
- Usar batch requests para múltiplas operações
- Sempre especificar timezone explicitamente

### 2.5 Supabase (PostgreSQL)

**Banco de Dados Principal:**
- PostgreSQL hospedado no Supabase
- Row Level Security (RLS) habilitado
- Triggers automáticos para updated_at
- Views otimizadas para consultas

**Tabelas Principais:**
1. **leads** - Informações dos leads
   - phone_number (único)
   - name, email, document
   - bill_value, consumption_kwh
   - current_stage, qualification_score
   - kommo_lead_id (integração CRM)

2. **conversations** - Sessões de conversa
   - lead_id (FK para leads)
   - session_id (único)
   - total_messages, sentiment
   - is_active

3. **messages** - Histórico de mensagens
   - conversation_id (FK)
   - role (user/assistant/system)
   - content, media_type, media_url
   - whatsapp_message_id

4. **lead_qualifications** - Dados de qualificação
   - lead_id (FK)
   - has_own_property, decision_maker
   - urgency_level, objections
   - extracted_data (JSONB)

5. **follow_ups** - Agendamento de follow-ups
   - lead_id (FK)
   - scheduled_at, type
   - status (pending/executed/failed)
   - message, result

6. **analytics** - Eventos e métricas
   - lead_id (FK)
   - event_type, event_data
   - session_id, ip_address

---

## 3. 🏗️ PROPOSTA DE ARQUITETURA - SIMPLES E MODULAR

### PRINCÍPIO FUNDAMENTAL: Prompt > Código

**IMPORTANTE**: Antes de criar qualquer código Python, sempre considere se a lógica pode ser implementada no prompt. O AGnO Framework é extremamente capaz de seguir instruções complexas em linguagem natural.

**Exemplos do que colocar NO PROMPT ao invés de código:**
- Fluxos de conversação e transições entre estágios
- Regras de quando chamar cada tool
- Validações de dados e formatos
- Lógica de qualificação de leads
- Critérios para agendamento
- Tratamento de objeções
- Personalização de mensagens

**Exemplos de instruções no prompt:**
```
Quando o lead demonstrar interesse em agendar uma reunião:
1. Primeiro, chame a tool 'check_calendar_availability' para verificar horários
2. Apresente até 3 opções de horários disponíveis
3. Após confirmação, chame 'create_calendar_meeting' com os dados
4. Em seguida, atualize o lead no Kommo usando 'update_lead_stage'
```

Isso reduz drasticamente a complexidade do código Python e torna o sistema mais flexível.

### 3.1 Estrutura de Pastas

```
agente/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── agent.py          # Agente principal SDR
│   ├── config.py         # Configurações centralizadas
│   └── types.py          # Types e interfaces
│
├── tools/
│   ├── __init__.py
│   ├── whatsapp.py       # Tools do WhatsApp/Evolution
│   ├── kommo.py          # Tools do Kommo CRM
│   ├── calendar.py       # Tools do Google Calendar
│   ├── media.py          # Tools de processamento multimodal
│   └── database.py       # Tools do Supabase
│
├── services/
│   ├── __init__.py
│   ├── evolution.py      # Cliente Evolution API simplificado
│   ├── kommo.py          # Cliente Kommo simplificado
│   ├── calendar.py       # Cliente Calendar simplificado
│   └── supabase.py       # Cliente Supabase simplificado
│
├── prompts/
│   ├── __init__.py
│   ├── system.py         # Prompt principal do sistema
│   └── stages.py         # Prompts por estágio de qualificação
│
├── repositories/
│   ├── __init__.py
│   ├── lead.py           # Repository para leads
│   ├── conversation.py   # Repository para conversas
│   └── message.py        # Repository para mensagens
│
└── utils/
    ├── __init__.py
    ├── formatters.py     # Formatação de mensagens
    └── validators.py     # Validações
```

### 3.2 Fluxo Simplificado

```python
# 1. Webhook recebe mensagem (JÁ FUNCIONA)
POST /webhook/whatsapp → 

# 2. Processar com NOVO agente (ÚNICA MUDANÇA)
agent = SDRAgent()  # Substitui o sdr_agent.py atual
response = await agent.process(message)

# 3. Enviar resposta (JÁ FUNCIONA)
await whatsapp_tool.send_message(response)
```

**NOTA**: Apenas o passo 2 muda. Todo o resto (webhook, Evolution API, envio de mensagens) continua funcionando exatamente como está hoje.

### 3.3 Agente Principal (SIMPLES)

```python
# agente/core/agent.py
from agno.agent import Agent
from agno.models.google import Gemini

class SDRAgent:
    def __init__(self):
        # Carregar prompt do sistema que contém TODA a lógica
        with open('docs/SYSTEM-PROMPT.md', 'r') as f:
            system_prompt = f.read()
        
        # Adicionar instruções sobre quando chamar cada tool
        tool_instructions = """
        
        ## INSTRUÇÕES PARA USO DE TOOLS
        
        ### Agendamento de Reuniões:
        Quando o lead aceitar agendar uma reunião:
        1. Use 'check_calendar_availability' para buscar horários
        2. Apresente opções disponíveis
        3. Após confirmação, use 'create_calendar_meeting'
        4. Atualize o Kommo com 'update_lead_stage' para 'meeting_scheduled'
        
        ### Processamento de Contas de Luz:
        Quando receber uma imagem:
        1. Use 'analyze_image' com prompt específico para contas
        2. Extraia valor e consumo
        3. Salve com 'update_lead_data'
        
        ### Qualificação:
        Durante a conversa, sempre que obtiver informações relevantes:
        1. Use 'update_lead_data' para salvar no banco
        2. Se lead qualificado, use 'create_kommo_lead'
        """
        
        self.agent = Agent(
            name="Helen Vieira - SDR SolarPrime",
            model=Gemini(id="gemini-2.5-pro"),
            tools=[
                # WhatsApp Tools
                send_whatsapp_message,
                send_whatsapp_media,
                mark_as_read,
                
                # Kommo Tools
                create_lead,
                update_lead_stage,
                add_note,
                schedule_task,
                
                # Calendar Tools
                check_availability,
                create_meeting,
                
                # Media Tools
                analyze_image,
                process_pdf,
                transcribe_audio,
                
                # Database Tools
                save_lead,
                get_lead,
                update_lead_data,
                save_message,
                get_conversation_history
            ],
            reasoning=True,
            instructions=system_prompt + tool_instructions
        )
    
    async def process(self, message: Dict) -> str:
        # Processar mensagem com contexto
        return await self.agent.run(message)
```

---

## 4. 🛠️ TOOLS ESPECÍFICAS

### 4.1 WhatsApp Tools

```python
@tool
async def send_whatsapp_message(
    phone: str, 
    message: str,
    typing_time: int = 5
) -> Dict:
    """Envia mensagem via WhatsApp com simulação de digitação"""
    
@tool
async def send_whatsapp_media(
    phone: str,
    media_url: str,
    caption: str = ""
) -> Dict:
    """Envia mídia (imagem/documento) via WhatsApp"""

@tool
async def mark_as_read(
    phone: str,
    message_id: str
) -> bool:
    """Marca mensagem como lida"""

@tool
async def chunk_message(
    agent,
    message: str,
    join_probability: float = 0.6,
    max_chunk_words: int = 30,
    min_chunk_words: int = 3,
    max_chars_per_chunk: int = 1200
) -> Dict:
    """
    Divide mensagem em chunks naturais para envio sequencial
    
    Cria conversação mais natural dividindo mensagens longas
    em pedaços menores, simulando digitação humana.
    
    Args:
        agent: Instância do agente AGnO
        message: Mensagem completa para dividir
        join_probability: Probabilidade de juntar sentenças (0.0-1.0)
        max_chunk_words: Máximo de palavras por chunk
        min_chunk_words: Mínimo de palavras por chunk
        max_chars_per_chunk: Máximo de caracteres (WhatsApp: 1600)
    
    Returns:
        - chunks: Lista de chunks de mensagem
        - delays: Lista de delays em ms para cada chunk
        - total_reading_time: Tempo total estimado de leitura
        - chunk_count: Número de chunks gerados
    """

@tool
async def process_buffered_messages(
    agent,
    messages: List[Dict[str, Any]]
) -> Dict:
    """
    Processa múltiplas mensagens rápidas como contexto único
    
    Quando usuário envia várias mensagens rapidamente,
    consolida tudo em um contexto único antes de responder.
    
    Args:
        agent: Instância do agente AGnO
        messages: Lista de mensagens com estrutura:
            [{
                "content": "texto",
                "type": "text|image|audio|document",
                "timestamp": "ISO datetime",
                "media_data": {...} (opcional)
            }]
    
    Returns:
        - consolidated_content: Texto unificado
        - message_count: Total de mensagens
        - detected_intents: ['interesse', 'dúvida', 'urgência']
        - requires_immediate_response: Se precisa resposta urgente
        - time_span_seconds: Tempo entre primeira e última msg
        - media_messages: Lista de mensagens com mídia
    """
```

### 4.2 Kommo Tools

```python
@tool
async def create_lead(
    name: str,
    phone: str,
    source: str = "WhatsApp"
) -> Dict:
    """Cria lead no Kommo CRM"""

@tool
async def update_lead_stage(
    lead_id: int,
    stage: str
) -> Dict:
    """Move lead no pipeline"""

@tool
async def schedule_task(
    lead_id: int,
    task: str,
    due_date: str
) -> Dict:
    """Cria tarefa de follow-up"""
```

### 4.3 Calendar Tools (Google Calendar API v3)

```python
@tool
async def check_calendar_availability(
    agent,
    date: str,
    duration_minutes: int = 60,
    calendar_ids: List[str] = None,
    working_hours: Dict = None
) -> List[Dict]:
    """Verifica disponibilidade usando FreeBusy API
    
    Args:
        agent: Instância do agente AGnO
        date: Data para verificar (YYYY-MM-DD)
        duration_minutes: Duração da reunião em minutos
        calendar_ids: Lista de calendários para verificar
        working_hours: {"start": "09:00", "end": "18:00"}
    
    Returns:
        Lista de slots disponíveis com horários em ISO format
    """

@tool
async def create_calendar_meeting(
    agent,
    title: str,
    description: str,
    start_datetime: str,
    end_datetime: str,
    attendee_emails: List[str],
    location: str = "Online via Google Meet",
    create_meet_link: bool = True,
    send_notifications: bool = True,
    reminder_minutes: List[int] = [1440, 30]  # 24h e 30min
) -> Dict:
    """Cria reunião com Google Meet integrado
    
    Args:
        agent: Instância do agente AGnO
        title: Título da reunião
        description: Descrição/agenda detalhada
        start_datetime: Início (ISO: 2025-02-01T10:00:00-03:00)
        end_datetime: Fim (ISO: 2025-02-01T11:00:00-03:00)
        attendee_emails: Lista de participantes
        location: Local ou "Online via Google Meet"
        create_meet_link: Se deve criar link do Google Meet
        send_notifications: Se deve enviar convites
        reminder_minutes: Lista de lembretes em minutos
    
    Returns:
        Dict com:
        - id: ID do evento
        - htmlLink: Link para o evento no Calendar
        - hangoutLink: Link do Google Meet
        - status: Status do evento
    """

@tool
async def update_calendar_event(
    agent,
    event_id: str,
    updates: Dict,
    send_updates: str = "all"
) -> Dict:
    """Atualiza evento existente (patch update)
    
    Args:
        agent: Instância do agente AGnO
        event_id: ID do evento no Google Calendar
        updates: Campos para atualizar (apenas os modificados)
        send_updates: "all", "externalOnly" ou "none"
    
    Returns:
        Evento atualizado
    """

@tool
async def cancel_calendar_event(
    agent,
    event_id: str,
    send_cancellation: bool = True,
    cancellation_reason: str = None
) -> Dict:
    """Cancela evento e notifica participantes
    
    Args:
        agent: Instância do agente AGnO
        event_id: ID do evento
        send_cancellation: Se deve notificar participantes
        cancellation_reason: Motivo do cancelamento
    
    Returns:
        Confirmação do cancelamento
    """

@tool
async def quick_add_event(
    agent,
    text: str,
    calendar_id: str = "primary"
) -> Dict:
    """Cria evento usando linguagem natural
    
    Args:
        agent: Instância do agente AGnO
        text: Ex: "Reunião com João amanhã às 15h por 1 hora"
        calendar_id: ID do calendário
    
    Returns:
        Evento criado
    """
```

### 4.4 Media Tools

```python
@tool
async def analyze_image(
    image_url: str,
    prompt: str = "Analise esta conta de luz"
) -> Dict:
    """Analisa imagem com Gemini Vision"""

@tool
async def process_pdf(
    pdf_url: str
) -> str:
    """Extrai texto de PDF"""

@tool
async def transcribe_audio(
    audio_url: str
) -> str:
    """Transcreve áudio para texto"""
```

### 4.5 Database Tools (Supabase)

```python
@tool
async def save_lead(
    phone: str,
    name: str = None,
    email: str = None,
    bill_value: float = None
) -> Dict:
    """Salva ou atualiza lead no Supabase"""

@tool
async def get_lead(
    phone: str
) -> Dict:
    """Busca lead pelo telefone"""

@tool
async def update_lead_data(
    phone: str,
    stage: str = None,
    qualification_score: int = None,
    **kwargs
) -> Dict:
    """Atualiza dados do lead"""

@tool
async def save_message(
    phone: str,
    content: str,
    role: str,
    media_type: str = None
) -> Dict:
    """Salva mensagem no histórico"""

@tool
async def get_conversation_history(
    phone: str,
    limit: int = 10
) -> List[Dict]:
    """Busca histórico de conversas"""

@tool
async def schedule_followup(
    lead_id: str,
    scheduled_at: str,
    message: str,
    type: str = "reminder"
) -> Dict:
    """Agenda follow-up no banco"""
```

### 4.6 Funcionalidades de Conversação Natural

#### Message Chunking (Divisão Natural de Mensagens)

O sistema divide mensagens longas em pedaços menores para criar uma conversação mais natural:

**Características:**
- Simula digitação humana com delays realistas (5-8s dependendo do tamanho da mensagem)
- Preserva pontuação e formatação correta
- Evita quebras inadequadas (não quebra em vírgulas, pode quebrar apenas quando um texto finalizar ou em uma pontuaçao, o ideal é quando um texto finalizar pois soa mais natural, quebrar mensagens somente em pontuaçoes deixa muito robotico.)
- Detecta quebras naturais (parágrafos, listas)
- Ajusta estratégia baseada no contexto (inicial, técnico, perguntas)

#### Simulação de Digitação Proporcional

**IMPORTANTE**: A simulação de digitação deve ser **proporcional ao tamanho da mensagem**:

- **Mensagem pequena** (até ~10 palavras): 2-4 segundos de digitação
- **Mensagem média** (10-30 palavras): 4-6 segundos de digitação
- **Mensagem grande** (30+ palavras): 6-8 segundos de digitação

Esta simulação torna a conversa mais natural e humana, dando tempo para o lead ler e processar a informação antes da próxima mensagem.

**Exemplo de uso:**
```python
# Mensagem longa
response = "João, analisei sua conta de luz e identifiquei que você paga R$ 850 por mês. Com nossa solução solar, você pode economizar até 95% desse valor. Vamos agendar uma visita?"

# Sistema divide em:
# Chunk 1: "João, analisei sua conta de luz e identifiquei que você paga R$ 850 por mês"
# Chunk 2: "Com nossa solução solar, você pode economizar até 95% desse valor!!!!"
# Chunk 3: "Vamos agendar uma visita?"
```

#### Message Buffering (Processamento de Múltiplas Mensagens)

Quando usuário envia várias mensagens rapidamente, o sistema consolida antes de responder:

**Características:**
- Detecta mensagens fragmentadas (múltiplas em <5s)
- Consolida contexto completo antes de processar
- Identifica intenções principais (interesse, dúvida, urgência)
- Evita respostas parciais ou fora de contexto

**Exemplo de uso:**
```python
# Usuário envia rapidamente:
# Msg 1: "oi"
# Msg 2: "quero saber sobre energia solar"
# Msg 3: "minha conta vem 800 reais"
# Msg 4: "tem desconto?"

# Sistema consolida em:
# "oi. quero saber sobre energia solar. minha conta vem 800 reais. tem desconto?"
# E responde uma vez só com contexto completo
```

---

## 5. ✅ CHECKLIST DE IMPLEMENTAÇÃO

### Fase 1: Estrutura Base (1-2 dias) ✅
- [X] Criar estrutura de pastas conforme proposto
- [X] Configurar `__init__.py` em todos os módulos
- [X] Criar `config.py` com todas as configurações do .env
- [X] Definir types em `types.py` (Lead, Message, Conversation, etc.)
- [X] Configurar logging estruturado com Loguru
- [X] Configurar conexão com Supabase
- [X] Criar tabela `agent_sessions` para estado do AGnO
- [X] Configurar variáveis de ambiente do .env
- [X] Criar utils/formatters.py com utilitários de formatação
- [X] Criar utils/validators.py com validadores de entrada
- [X] Criar agent.py com skeleton do SDRAgent

### Fase 2: Services Simplificados (2-3 dias) ✅
- [X] Implementar Evolution API client v2 (do zero)
  - [X] Implementar webhook by events
  - [X] Adicionar suporte para send_text, send_media, send_reaction
  - [X] Simulação de digitação proporcional (2-15s)
  - [X] Retry logic com exponential backoff
- [X] Implementar Kommo service (do zero)
  - [X] Usar Long-Lived Token do .env
  - [X] Implementar mapeamento automático de campos
  - [X] Adicionar lógica de pipeline stages
  - [X] Cache de pipelines e custom fields
- [X] Implementar Calendar service (do zero)
  - [X] Usar Service Account do .env
  - [X] Implementar FreeBusy API
  - [X] Adicionar criação de Google Meet
  - [X] Configurar timezone America/Sao_Paulo
- [X] Criar Supabase service simplificado
  - [X] Manter estrutura de tabelas existente
  - [X] Adicionar métodos para recuperar 100 últimas mensagens
  - [X] CRUD completo com type safety

### Fase 3: Repositories (1-2 dias) ✅
- [X] Implementar LeadRepository
  - [X] CRUD completo para tabela leads
  - [X] Métodos de busca por telefone
  - [X] Atualização de estágios com validação
  - [X] Cálculo de score de qualificação
  - [X] Sincronização com Kommo CRM
- [X] Implementar ConversationRepository
  - [X] Gerenciamento de sessões com timeout de 30min
  - [X] Histórico de conversas formatado
  - [X] Recuperar 100 últimas mensagens
  - [X] Cache de conversas ativas
- [X] Implementar MessageRepository
  - [X] Salvar mensagens com media
  - [X] Buscar por conversation_id
  - [X] Suporte para multimodal
  - [X] Tracking de chunks de mensagem
  - [X] Busca full-text
- [X] Implementar FollowUpRepository
  - [X] Agendar follow-ups inteligentes
  - [X] Marcar como executado/falhou
  - [X] Follow-ups com contexto personalizado
  - [X] Regras de negócio (30min → 24h → desistir)
  - [X] Respeito ao horário comercial
- [X] Criar métodos de consulta otimizados
- [ ] Testar operações CRUD

### Fase 4: Tools AGnO (3-4 dias) ✅
- [X] Implementar WhatsApp tools (8 tools)
  - [X] send_text_message (com delay proporcional)
  - [X] send_audio_message
  - [X] send_image_message  
  - [X] send_document_message
  - [X] send_location_message
  - [X] type_simulation (simulação de digitação)
  - [X] message_chunking (delays até 15s, quebra em frases completas)
  - [X] message_buffer (consolidar múltiplas mensagens)
- [X] Implementar Kommo tools (6 tools)
  - [X] search_kommo_lead (buscar por telefone/email)
  - [X] create_kommo_lead (inserir em "NOVO LEAD")
  - [X] update_kommo_lead (atualizar dados do lead)
  - [X] update_kommo_stage (seguir fluxo de estágios)
  - [X] add_kommo_note (adicionar notas/comentários)
  - [X] schedule_kommo_activity (agendar atividades)
- [X] Implementar Calendar tools (5 tools)
  - [X] check_availability (sem bloquear almoço)
  - [X] create_meeting (10min entre agendamentos)
  - [X] update_meeting (atualizar reunião)
  - [X] cancel_meeting (cancelar reunião)
  - [X] send_calendar_invite (enviar convite via WhatsApp)
- [X] Implementar Media tools (3 tools)
  - [X] process_image (preparar para Gemini Vision)
  - [X] process_audio (preparar para transcrição)
  - [X] process_document (análise de PDFs/contas de luz)
- [X] Implementar Database tools (6 tools)
  - [X] create_lead (criar lead no Supabase)
  - [X] update_lead (atualizar dados do lead)
  - [X] get_lead (buscar lead por telefone/ID)
  - [X] save_message (salvar mensagem com multimodal)
  - [X] update_conversation (atualizar sessão)
  - [X] schedule_followup (inteligente com contexto)
- [X] Implementar Utility tools (2 tools)
  - [X] validate_phone (validar telefone brasileiro)
  - [X] format_currency (formatar valores em Reais)
- [X] Todas as tools com decorator @tool do AGnO
- [X] Tratamento de erros e logging com loguru

### Fase 5: Agente Principal (2-3 dias) ✅
- [X] Implementar SDRAgent com AGnO
  - [X] Configurar Gemini 2.0 Flash Exp
  - [X] Criar Toolkit com tools_to_stop_on
  - [X] Reasoning=False por padrão (ativar só quando complexo)
  - [X] Desabilitar storage e memory do AGnO
- [X] Configurar prompts por estágio
  - [X] Carregar prompt principal do arquivo
  - [X] Adicionar instruções de uso de tools
  - [X] Implementar lógica no prompt (não em código)
- [X] Implementar fluxo de qualificação
  - [X] QualificationFlow com estágios do Kommo CRM
  - [X] Lógica de transição estruturada
- [X] Adicionar contexto com Supabase
  - [X] ContextManager recupera 100 últimas mensagens
  - [X] SessionManager mantém estado das conversas
- [X] Implementar follow-ups inteligentes
  - [X] 30min primeira tentativa
  - [X] 24h segunda tentativa
  - [X] Marcar "NÃO INTERESSADO" após 2 falhas
  - [X] Follow-ups personalizados por objeção
- [X] Implementar MessageProcessor com humanização
- [X] Implementar HelenHumanizer com simulação realista

### Fase 6: Integração com Infraestrutura Existente (2-3 dias) ✅
- [X] Criar main.py para integração com FastAPI
- [X] Conectar com webhook existente (compatível com Evolution API v2)
- [X] Manter todas as configurações atuais de Evolution API
- [X] Reutilizar formatadores de mensagem existentes
- [X] Manter sistema de logs e monitoramento atual (Sentry integrado)
- [X] Configurar simulação de digitação proporcional (HelenHumanizer)
- [X] Implementar message buffering (MessageProcessor)
- [X] Deploy no EasyPanel (Dockerfile atualizado)
- [X] Testar fluxo completo E2E
  - [X] Recepção de mensagem (test_complete_flow.py)
  - [X] Processamento multimodal (test_complete_flow.py)
  - [X] Qualificação (test_qualification_stages.py)
  - [X] Agendamento (test_complete_flow.py)
  - [X] Follow-ups (test_complete_flow.py)
- [X] Criar script de migração (migrate_to_modular.py)

### Fase 7: Testes e Validação ✅ (2-3 dias)
- [x] Criar testes unitários para cada tool
- [x] Testar integração com APIs externas
- [x] Validar fluxo de qualificação completo
- [x] Testar agendamento com Google Calendar
- [x] Validar follow-ups automáticos
- [x] Testar processamento de mídia
- [x] Stress test com múltiplas conversas
- [x] Validar rate limiting
- [x] Testar migração de dados existentes

### Fase 8: Documentação e Entrega (1-2 dias)
- [ ] Documentar arquitetura final
- [ ] Criar guia de instalação
- [ ] Documentar variáveis de ambiente
- [ ] Criar exemplos de uso
- [ ] Documentar APIs e tools
- [ ] Preparar scripts de migração
- [ ] Criar plano de rollback
- [ ] Treinar equipe

**IMPORTANTE**: Esta implementação mantém toda infraestrutura existente funcionando. Apenas substituímos o `sdr_agent.py` monolítico pelo novo `SDRAgent()` modular.

---

## 5.1 🔧 DETALHES TÉCNICOS DE IMPLEMENTAÇÃO

### Configuração do Agente AGnO

```python
from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools import tool, Toolkit
from agno.document_reader import PDFReader, DOCXReader

class SDRAgent:
    def __init__(self):
        # Configurar modelo com capacidades multimodais
        model = Gemini(
            id="gemini-2.5-pro",
            api_key=os.getenv("GOOGLE_API_KEY")
        )
        
        # Criar toolkit personalizado
        sdr_toolkit = Toolkit(
            show_tool_results=True,
            tools_to_stop_on=["create_calendar_meeting", "create_kommo_lead"]
        )
        
        # Adicionar todas as tools ao toolkit
        sdr_toolkit.add_tools([
            send_whatsapp_message,
            chunk_message,
            process_buffered_messages,
            create_kommo_lead,
            check_calendar_availability,
            analyze_image,
            # ... outras tools
        ])
        
        # Criar agente com configurações avançadas
        self.agent = Agent(
            name="Helen Vieira - SDR SolarPrime",
            model=model,
            toolkit=sdr_toolkit,
            reasoning=True,  # Ativa chain of thought
            storage=True,    # Persistência de conversas
            memory=True,     # Memória de preferências
            instructions=self._get_system_prompt(),
            # Configurações adicionais
            debug=True,
            log_level="INFO"
        )
```

### Integração com Evolution API v2

```python
# services/evolution.py
class EvolutionService:
    def __init__(self):
        self.base_url = os.getenv("EVOLUTION_API_URL")
        self.instance = os.getenv("EVOLUTION_INSTANCE")
        self.api_key = os.getenv("EVOLUTION_API_KEY")
        
    async def send_text(self, phone: str, message: str, options: Dict = None):
        """Envia mensagem de texto com opções avançadas"""
        endpoint = f"/message/sendText/{self.instance}"
        
        payload = {
            "number": phone,
            "text": message,
            "delay": options.get("delay", 1000),
            "linkPreview": options.get("link_preview", True),
            "mentionsEveryOne": options.get("mention_all", False)
        }
        
        return await self._make_request("POST", endpoint, payload)
    
    async def configure_webhook(self, events: List[str]):
        """Configura webhook com eventos específicos"""
        endpoint = f"/webhook/set/{self.instance}"
        
        payload = {
            "enabled": True,
            "url": os.getenv("WEBHOOK_URL"),
            "webhook_by_events": True,
            "events": events
        }
        
        return await self._make_request("POST", endpoint, payload)
```

### Integração com Kommo CRM (OAuth2)

```python
# services/kommo.py
class KommoService:
    def __init__(self):
        self.base_url = "https://your-domain.kommo.com"
        self.client_id = os.getenv("KOMMO_CLIENT_ID")
        self.client_secret = os.getenv("KOMMO_CLIENT_SECRET")
        self.access_token = None
        self.refresh_token = None
        
    async def refresh_access_token(self):
        """Renova token de acesso usando refresh token"""
        endpoint = "/oauth2/access_token"
        
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "redirect_uri": os.getenv("KOMMO_REDIRECT_URI")
        }
        
        response = await self._make_request("POST", endpoint, payload)
        self.access_token = response["access_token"]
        self.refresh_token = response["refresh_token"]
        
        # Salvar tokens no banco
        await self._save_tokens()
        
    async def create_lead_with_details(self, data: Dict):
        """Cria lead com campos customizados e tags"""
        endpoint = "/api/v4/leads"
        
        payload = {
            "name": data["name"],
            "price": data.get("price", 0),
            "status_id": data.get("status_id"),
            "pipeline_id": data.get("pipeline_id"),
            "custom_fields_values": [
                {
                    "field_id": 123456,  # Campo telefone
                    "values": [{"value": data["phone"]}]
                },
                {
                    "field_id": 123457,  # Campo origem
                    "values": [{"value": "WhatsApp"}]
                }
            ],
            "_embedded": {
                "tags": [{"name": tag} for tag in data.get("tags", [])]
            }
        }
        
        return await self._make_authorized_request("POST", endpoint, [payload])
```

### Processamento Multimodal com AGnO

```python
# tools/media.py
from agno.document_reader import PDFReader, DOCXReader, PDFImageReader

@tool(show_result=True)
async def analyze_energy_bill(agent, image_url: str) -> Dict:
    """Analisa conta de energia e extrai dados estruturados"""
    
    # Usar capacidade multimodal do Gemini
    prompt = """
    Analise esta conta de energia e extraia:
    1. Nome do titular
    2. Endereço completo
    3. Número da instalação/cliente
    4. Valor total da fatura
    5. Consumo em kWh
    6. Histórico de consumo (se disponível)
    7. Vencimento
    
    Retorne os dados em formato JSON estruturado.
    """
    
    # Gemini processa imagem diretamente
    result = await agent.run_with_image(
        prompt=prompt,
        image_url=image_url
    )
    
    # Parsear resultado e validar
    try:
        data = json.loads(result)
        return {
            "success": True,
            "data": data,
            "confidence": 0.95
        }
    except:
        return {
            "success": False,
            "raw_text": result,
            "error": "Não foi possível extrair dados estruturados"
        }

@tool
async def process_pdf_document(agent, pdf_url: str) -> Dict:
    """Processa PDF usando AGnO PDFReader"""
    
    # Usar PDFReader do AGnO
    pdf_reader = PDFReader(pdf=pdf_url)
    
    # Extrair texto
    text_content = await pdf_reader.read()
    
    # Se PDF tem imagens (conta escaneada)
    if pdf_reader.has_images:
        pdf_image_reader = PDFImageReader(pdf=pdf_url)
        images = await pdf_image_reader.extract_images()
        
        # Analisar cada imagem
        for idx, image in enumerate(images):
            analysis = await analyze_energy_bill(agent, image)
            if analysis["success"]:
                return analysis
    
    # Tentar extrair dados do texto
    return {
        "text": text_content,
        "type": "pdf",
        "pages": pdf_reader.page_count
    }
```

---

## 6. 📅 ETAPAS DETALHADAS DE IMPLEMENTAÇÃO

### Semana 1: Base e Services

**Dia 1-2: Estrutura**
```bash
# Criar estrutura
mkdir -p agente/{core,tools,services,prompts,utils}

# Configurar projeto
touch agente/core/{__init__.py,agent.py,config.py,types.py}
```

**Dia 3-5: Services**
- Copiar apenas o necessário dos services atuais
- Remover complexidade e duplicação
- Unificar interfaces

### Semana 2: Tools e Agente

**Dia 6-8: Tools**
- Implementar tools com @tool decorator
- Documentar cada tool
- Criar testes unitários

**Dia 9-10: Agente**
- Implementar SDRAgent
- Configurar AGnO corretamente
- Testar multimodal

### Semana 3: Integração

**Dia 11-12: Conexão**
- Integrar com FastAPI
- Migrar webhook handler
- Testar ponta a ponta

**Dia 13-15: Ajustes**
- Performance tuning
- Correções de bugs
- Documentação

---

## 7. 🎯 BENEFÍCIOS DA NOVA ARQUITETURA

### Simplicidade
- UM agente principal (sem Teams complexos)
- Tools bem definidas e isoladas
- Services limpos e diretos
- Fácil de entender e manter

### Modularidade
- Cada tool é independente
- Services plugáveis
- Fácil adicionar/remover funcionalidades
- Testável isoladamente

### Escalabilidade
- Adicionar novas tools sem modificar core
- Deploy de mudanças específicas
- Monitoramento por componente
- Cache e otimizações pontuais

### Performance
- Menos overhead (sem Teams)
- Tools executam diretamente
- Reasoning otimizado
- Respostas mais rápidas

---

## 8. 🔒 CONSIDERAÇÕES FINAIS

### Segurança
- Todas as credenciais em variáveis de ambiente
- Validação de inputs
- Rate limiting mantido
- Logs sem dados sensíveis

### Manutenção
- Código limpo e documentado
- Testes para cada componente
- CI/CD simplificado
- Monitoramento de erros

### Evolução
- Fácil adicionar novos canais (Instagram, etc)
- Suporte para novos tipos de mídia
- Integração com mais CRMs
- IA cada vez mais inteligente

---

## 9. 🚀 CONCLUSÃO

Esta proposta oferece uma arquitetura:

✅ **SIMPLES**: Sem complexidade desnecessária
✅ **MODULAR**: Componentes independentes
✅ **ESCALÁVEL**: Cresce conforme necessidade
✅ **EFICIENTE**: Performance otimizada
✅ **MANUTENÍVEL**: Fácil de entender e modificar

O novo agente SDR será capaz de:
- Atender múltiplas conversas simultaneamente
- Qualificar leads com inteligência
- Agendar reuniões automaticamente
- Processar qualquer tipo de mídia
- Integrar com sistemas externos

Tudo isso mantendo a simplicidade e eficiência que o negócio precisa.

---

## 10. 📝 OBSERVAÇÕES IMPORTANTES

### Sobre a Infraestrutura Existente

1. **Webhook Evolution API**: Já está configurado e funcionando perfeitamente
2. **EasyPanel**: Deploy já configurado, apenas fazer build da nova imagem
3. **Variáveis de Ambiente**: Todas já configuradas no .env
4. **SSL/HTTPS**: Certificados válidos com renovação automática
5. **Redis**: Já configurado para cache e filas
6. **Supabase**: Banco de dados com todas as tabelas criadas

### Sobre as Integrações

1. **Evolution API v2**: 
   - Suporta todos recursos novos (polls, reactions, status)
   - Webhook by events já pode ser ativado
   - Redis opcional mas recomendado para performance

2. **Kommo CRM**:
   - OAuth2 tokens devem ser renovados a cada 24h
   - Usar refresh token antes da expiração
   - Webhooks disponíveis para sincronização em tempo real

3. **Google Calendar**:
   - Service Account é melhor para automação
   - Timezone handling já implementado
   - Google Meet links automáticos

4. **AGnO Framework**:
   - Reasoning ativado melhora qualidade das respostas
   - Multimodal nativo com Gemini 2.5 Pro
   - Tools com @tool decorator são simples de criar
   - Toolkit permite controle fino sobre execução

### Pontos de Atenção

1. **Performance**: 
   - Usar chunking para mensagens longas
   - Buffer para múltiplas mensagens rápidas
   - Cache de tokens OAuth2

2. **Segurança**:
   - Nunca logar tokens ou senhas
   - Validar todos inputs do usuário
   - Rate limiting já implementado

3. **Manutenção**:
   - Logs estruturados com Loguru
   - Monitoramento com Sentry (já configurado)
   - Testes automatizados essenciais

### Migração do Sistema Atual

1. **Fase 1**: Criar novo agente em paralelo
2. **Fase 2**: Testar com números de teste
3. **Fase 3**: Migração gradual (10% → 50% → 100%)
4. **Fase 4**: Desativar agente antigo

### Contatos para Dúvidas

- **Evolution API**: Documentação em doc.evolution-api.com
- **Kommo**: developers.kommo.com
- **AGnO**: docs.agno.com
- **Supabase**: supabase.com/docs

---

## 11. 📊 ESTRUTURA DE DADOS COMPLETA DO SUPABASE

### Análise das Tabelas Existentes

Com base na análise dos scripts SQL, aqui está a estrutura completa das tabelas:

### 11.1 Tabela: `profiles`
```sql
- id: UUID PRIMARY KEY
- phone: VARCHAR(50) UNIQUE NOT NULL
- whatsapp_name: VARCHAR(255)
- whatsapp_push_name: VARCHAR(255)
- first_interaction_at: TIMESTAMP WITH TIME ZONE
- last_interaction_at: TIMESTAMP WITH TIME ZONE
- total_messages: INTEGER DEFAULT 0
- created_at/updated_at: TIMESTAMP WITH TIME ZONE
```

### 11.2 Tabela: `leads`
```sql
- id: UUID PRIMARY KEY
- phone_number: VARCHAR(20) UNIQUE NOT NULL
- name: VARCHAR(100)
- email: VARCHAR(100)
- document: VARCHAR(20) -- CPF/CNPJ
- property_type: VARCHAR(20) -- casa/apartamento/comercial/rural
- address: TEXT
- bill_value: DECIMAL(10,2)
- consumption_kwh: INTEGER
- current_stage: VARCHAR(50) DEFAULT 'INITIAL_CONTACT'
- qualification_score: INTEGER (0-100)
- interested: BOOLEAN DEFAULT true
- kommo_lead_id: VARCHAR(50)
- created_at/updated_at: TIMESTAMP WITH TIME ZONE
```

### 11.3 Tabela: `conversations`
```sql
- id: UUID PRIMARY KEY
- lead_id: UUID REFERENCES leads(id)
- session_id: VARCHAR(100) UNIQUE NOT NULL
- started_at: TIMESTAMP WITH TIME ZONE
- ended_at: TIMESTAMP WITH TIME ZONE
- total_messages: INTEGER DEFAULT 0
- current_stage: VARCHAR(50)
- sentiment: VARCHAR(20) -- positivo/neutro/negativo
- is_active: BOOLEAN DEFAULT true
- created_at/updated_at: TIMESTAMP WITH TIME ZONE
```

### 11.4 Tabela: `messages`
```sql
- id: UUID PRIMARY KEY
- conversation_id: UUID REFERENCES conversations(id)
- whatsapp_message_id: VARCHAR(100)
- role: VARCHAR(20) -- user/assistant/system
- content: TEXT NOT NULL
- media_type: VARCHAR(20) -- image/audio/video/document
- media_url: TEXT
- media_data: JSONB
- created_at: TIMESTAMP WITH TIME ZONE
```

### 11.5 Tabela: `lead_qualifications`
```sql
- id: UUID PRIMARY KEY
- lead_id: UUID REFERENCES leads(id)
- has_own_property: BOOLEAN
- decision_maker: BOOLEAN
- urgency_level: VARCHAR(20) -- alta/media/baixa
- objections: JSONB DEFAULT '[]'
- solutions_presented: JSONB DEFAULT '[]'
- extracted_data: JSONB DEFAULT '{}'
- qualification_date: TIMESTAMP WITH TIME ZONE
- created_at/updated_at: TIMESTAMP WITH TIME ZONE
```

### 11.6 Tabela: `follow_ups`
```sql
- id: UUID PRIMARY KEY
- lead_id: UUID REFERENCES leads(id)
- scheduled_at: TIMESTAMP WITH TIME ZONE NOT NULL
- type: VARCHAR(50) -- reminder/check_in/reengagement/nurture
- message: TEXT NOT NULL
- status: VARCHAR(20) -- pending/executed/failed/cancelled
- executed_at: TIMESTAMP WITH TIME ZONE
- result: JSONB
- created_at/updated_at: TIMESTAMP WITH TIME ZONE
```

### 11.7 Tabela: `analytics`
```sql
- id: UUID PRIMARY KEY
- lead_id: UUID REFERENCES leads(id)
- event_type: VARCHAR(50) NOT NULL
- event_data: JSONB DEFAULT '{}'
- session_id: VARCHAR(100)
- user_agent: VARCHAR(255)
- ip_address: VARCHAR(45)
- created_at: TIMESTAMP WITH TIME ZONE
```

### 11.8 Tabela: `knowledge_base`
```sql
- id: UUID PRIMARY KEY
- category: VARCHAR(100) NOT NULL
- question: TEXT NOT NULL
- answer: TEXT NOT NULL
- keywords: TEXT[]
- metadata: JSONB DEFAULT '{}'
- embedding: vector(1536) -- Para busca semântica
- created_at/updated_at: TIMESTAMP WITH TIME ZONE
```

### 11.9 Tabela: `agent_sessions`
```sql
- id: UUID PRIMARY KEY
- session_id: VARCHAR(255) UNIQUE NOT NULL
- phone_number: VARCHAR(50) NOT NULL
- state: JSONB NOT NULL DEFAULT '{}'
- created_at/updated_at: TIMESTAMP WITH TIME ZONE
- last_interaction: TIMESTAMP WITH TIME ZONE
```

### 11.10 Tabela: `embeddings` (AGnO PgVector)
```sql
- id: TEXT PRIMARY KEY
- content: TEXT
- meta_data: JSONB
- embedding: vector(1536)
- created_at: TIMESTAMP WITH TIME ZONE
```

---

## 12. 🔧 CONFIGURAÇÃO DO KOMMO CRM

### Campos Customizados Identificados

Com base na análise do `kommo_service.py`, os campos customizados mapeados automaticamente são:

1. **whatsapp_number**: Número do WhatsApp
2. **energy_bill_value**: Valor da conta de energia
3. **qualification_score**: Score de qualificação
4. **solution_type**: Tipo de solução (select)
5. **lead_source**: Origem do lead
6. **first_message**: Primeira mensagem
7. **conversation_id**: ID da conversa
8. **google_calendar_link**: Link do Google Calendar
9. **meeting_status**: Status da reunião

### Pipeline e Estágios

O sistema mapeia automaticamente os estágios baseado em palavras-chave:
- **new**: novo, inicial, primeiro
- **in_qualification**: qualifica, analisa, avalia
- **qualified**: qualificado (sem "não")
- **meeting_scheduled**: reuni, agend, meeting
- **in_negotiation**: negocia, proposta, orçamento
- **won**: ganho, fechado, vendido
- **lost**: perdido, cancelado
- **not_interested**: não interessado, desistiu

### Autenticação

- Usa **Long-Lived Token** (não precisa renovar)
- Token configurado em `KOMMO_LONG_LIVED_TOKEN`
- Subdomain configurado no .env

---

## 13. 🎯 RESPOSTAS ÀS PERGUNTAS CRÍTICAS

Com base na análise completa do codebase:

### 1. **Arquitetura do Agente**
**Resposta**: Opção A (Manter TUDO no prompt) é a melhor escolha. O prompt atual já tem 500+ linhas extremamente detalhadas com fluxos, personalidade, objections handling. As tools devem ser apenas para ações externas (WhatsApp, Kommo, Calendar, Supabase).

**IMPORTANTE**: Muita lógica pode ser inserida diretamente no prompt ao invés de criar código Python complexo. Por exemplo:
- Quando for agendar uma reunião, inserir uma instrução no prompt para chamar a tool de calendar
- Fluxos de decisão podem ser descritos no prompt em linguagem natural
- Validações e regras de negócio podem estar no prompt
- O prompt pode conter instruções para chamar tools específicas em momentos determinados

Isso mantém o código Python simples e move a complexidade para o prompt, onde é mais fácil de ajustar.

### 2. **Gestão de Estado e Contexto**
**Resposta**: Usar Supabase como está + tabela `agent_sessions` para estado do AGnO. O sistema já tem `conversations` e `messages` para histórico completo. O agente deve recuperar as **100 últimas mensagens** entre ele e o usuário para manter contexto adequado.

### 3. **Message Chunking e Timing**
**Resposta**: Já existe lógica implementada. Aumentar delays para até **15 segundos** para mensagens muito grandes. Chunks devem quebrar preferencialmente no final de frases completas, não em vírgulas. O timing pode variar baseado no horário/dia conforme a decisão do desenvolvedor.

### 4. **Integração Kommo - Campos Críticos**
**Resposta**: O sistema faz mapeamento automático! Não precisamos dos IDs exatos. O `kommo_service.py` já tem lógica para descobrir campos por nome. **Todos os IDs e toda a estrutura é puxada automaticamente do Long-Lived Token do Kommo CRM** (credenciais no arquivo .env).

### 5. **Horários de Agendamento**
**Resposta**: Horário comercial 8h-18h (configurado). O sistema já tem slots padrão: 09:00, 10:00, 11:00, 14:00, 15:00, 16:00, 17:00. **Todas as credenciais do Google Calendar estão no arquivo .env**. Não bloquear horários de almoço ou fim de expediente. **Mínimo de 10 minutos entre agendamentos**.

### 6. **Follow-up Intelligence**
**Resposta**: Sistema atual: 30min + 24h. Se o lead não responder à primeira tentativa de 30min e não responder à segunda tentativa de 24h, deve-se inserir no Kommo CRM como **"NÃO INTERESSADO"**.

**Follow-ups Inteligentes**: Criar follow-ups diferentes para cada tipo de objeção. O follow-up deve analisar todo o contexto da conversa e agir de acordo - não queremos follow-ups genéricos, mas follow-ups que puxem o prompt do Agente + contexto da conversa.

**Follow-up para Leads Quentes**: SIM! O agente precisa entender o contexto e ser inteligente o suficiente para resgatar leads quentes que sumiram, com abordagem personalizada baseada no histórico.

### 7. **Decisão Técnica AGnO**
**Resposta**: 
- `reasoning=True` **somente em momentos complexos** que necessitam de mais raciocínio. Reasoning sempre como true é desperdício de tempo e custos
- `tools_to_stop_on`: ["create_calendar_meeting", "create_kommo_lead"] (manter como sugerido)
- Usar Supabase para tudo - manter toda a persistência no Supabase, não usar Storage e Memory do AGnO