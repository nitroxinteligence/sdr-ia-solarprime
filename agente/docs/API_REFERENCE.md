# API Reference - SDR Agent Tools

## Introdução

Este documento apresenta a documentação completa das 30 ferramentas (tools) do SDR Agent, organizadas por categoria. O SDR Agent utiliza o AGnO Framework para orquestrar essas ferramentas, permitindo que a agente Helen Vieira da SolarPrime execute ações complexas de vendas e qualificação via WhatsApp.

### Integração com AGnO Framework

O AGnO Framework permite que o agente:
- Execute ferramentas de forma assíncrona e paralela
- Gerencie o contexto entre chamadas de ferramentas
- Tome decisões inteligentes sobre qual ferramenta usar
- Monitore e registre o uso de cada ferramenta
- Trate erros de forma elegante com retry automático

### Como as Tools são Registradas

As ferramentas são registradas no agente através do Toolkit do AGnO:

```python
from agno.tools import Toolkit
from agente.tools import ALL_TOOLS

toolkit = Toolkit(
    show_tool_results=True,
    tools_to_stop_on=["create_meeting", "create_lead"],
    tools=ALL_TOOLS
)
```

### Padrões de Uso

Todas as ferramentas seguem padrões consistentes:
- Decoradas com `@tool` do AGnO Framework
- Retornam um dicionário com `success` indicando sucesso/falha
- Incluem tratamento de erros e logging detalhado
- São assíncronas (async/await)
- Incluem documentação inline para o agente

---

## 1. WhatsApp Tools (8 ferramentas)

Ferramentas para comunicação via WhatsApp através da Evolution API.

### 1.1 send_text_message

**Propósito**: Envia mensagens de texto via WhatsApp com simulação de digitação natural.

**Assinatura**:
```python
async def send_text_message(
    phone: str,
    text: str,
    delay: Optional[int] = None
) -> Dict[str, Any]
```

**Parâmetros**:
- `phone` (str, obrigatório): Número de telefone do destinatário no formato 5511999999999
- `text` (str, obrigatório): Texto da mensagem a ser enviada
- `delay` (int, opcional): Delay customizado em segundos. Se não fornecido, é calculado automaticamente baseado no tamanho do texto

**Retorno**:
```python
{
    "success": bool,           # Se a mensagem foi enviada com sucesso
    "message_id": str,         # ID da mensagem no WhatsApp (se sucesso)
    "error": str,              # Mensagem de erro (se falhou)
    "phone": str,              # Número formatado usado no envio
    "delay_applied": int       # Delay aplicado em segundos
}
```

**Exemplo de Uso**:
```python
# Envio simples
await send_text_message("5511999999999", "Olá! Como posso ajudar?")

# Com delay customizado
await send_text_message("5511999999999", "Mensagem importante", delay=5)
```

**Tratamento de Erros**:
- Valida formato do número de telefone
- Trata falhas de conexão com a API
- Registra todos os erros no log

**Ferramentas Relacionadas**:
- `type_simulation`: Simula digitação antes do envio
- `message_chunking`: Divide mensagens longas
- `message_buffer`: Agrupa múltiplas mensagens

**Notas**:
- O delay de digitação simula comportamento humano
- Mensagens muito longas devem usar `message_chunking` primeiro
- Respeita limites de rate da Evolution API

---

### 1.2 type_simulation

**Propósito**: Simula digitação ("typing...") no WhatsApp para parecer mais natural.

**Assinatura**:
```python
async def type_simulation(
    phone: str,
    duration: Optional[int] = None,
    message_preview: Optional[str] = None
) -> Dict[str, Any]
```

**Parâmetros**:
- `phone` (str, obrigatório): Número do destinatário
- `duration` (int, opcional): Duração da simulação em segundos (padrão: calculado automaticamente)
- `message_preview` (str, opcional): Prévia da mensagem para calcular duração apropriada

**Retorno**:
```python
{
    "success": bool,
    "duration": int,          # Duração aplicada
    "phone": str,
    "error": str             # Se houver erro
}
```

**Exemplo de Uso**:
```python
# Simular digitação antes de enviar mensagem
await type_simulation("5511999999999", message_preview="Deixe-me verificar isso para você...")
await send_text_message("5511999999999", "Deixe-me verificar isso para você...")
```

**Notas**:
- Aumenta naturalidade da conversa
- Duração baseada em velocidade de digitação humana (40-60 palavras/minuto)
- Usar antes de mensagens importantes ou longas

---

### 1.3 send_image_message

**Propósito**: Envia imagens via WhatsApp com legenda opcional.

**Assinatura**:
```python
async def send_image_message(
    phone: str,
    image_url: str,
    caption: Optional[str] = None,
    filename: Optional[str] = None
) -> Dict[str, Any]
```

**Parâmetros**:
- `phone` (str, obrigatório): Número do destinatário
- `image_url` (str, obrigatório): URL pública da imagem
- `caption` (str, opcional): Legenda da imagem
- `filename` (str, opcional): Nome do arquivo (padrão: "image.jpg")

**Retorno**:
```python
{
    "success": bool,
    "message_id": str,
    "media_id": str,         # ID da mídia no WhatsApp
    "phone": str,
    "error": str
}
```

**Exemplo de Uso**:
```python
# Enviar proposta visual
await send_image_message(
    "5511999999999",
    "https://example.com/proposta-solar.png",
    caption="Aqui está sua proposta de economia com energia solar!"
)
```

**Formatos Suportados**:
- JPEG, JPG, PNG, GIF, WEBP, BMP, TIFF

**Notas**:
- URL deve ser acessível publicamente
- Tamanho máximo: 5MB
- Imagens são comprimidas automaticamente pelo WhatsApp

---

### 1.4 send_document_message

**Propósito**: Envia documentos (PDF, DOC, etc.) via WhatsApp.

**Assinatura**:
```python
async def send_document_message(
    phone: str,
    document_url: str,
    filename: str,
    caption: Optional[str] = None
) -> Dict[str, Any]
```

**Parâmetros**:
- `phone` (str, obrigatório): Número do destinatário
- `document_url` (str, obrigatório): URL pública do documento
- `filename` (str, obrigatório): Nome do arquivo com extensão
- `caption` (str, opcional): Descrição do documento

**Retorno**:
```python
{
    "success": bool,
    "message_id": str,
    "media_id": str,
    "filename": str,
    "phone": str,
    "error": str
}
```

**Exemplo de Uso**:
```python
# Enviar contrato
await send_document_message(
    "5511999999999",
    "https://example.com/contrato-solar.pdf",
    "Contrato_Energia_Solar_SolarPrime.pdf",
    caption="Segue o contrato para sua análise"
)
```

**Formatos Suportados**:
- PDF, DOC, DOCX, XLS, XLSX, PPT, PPTX, TXT, ZIP

**Notas**:
- Tamanho máximo: 100MB
- Nome do arquivo é importante para o destinatário

---

### 1.5 send_audio_message

**Propósito**: Envia mensagens de áudio/voz via WhatsApp.

**Assinatura**:
```python
async def send_audio_message(
    phone: str,
    audio_url: str,
    is_voice_note: bool = True,
    caption: Optional[str] = None
) -> Dict[str, Any]
```

**Parâmetros**:
- `phone` (str, obrigatório): Número do destinatário
- `audio_url` (str, obrigatório): URL do arquivo de áudio
- `is_voice_note` (bool, opcional): Se é nota de voz (padrão: True)
- `caption` (str, opcional): Legenda do áudio

**Retorno**:
```python
{
    "success": bool,
    "message_id": str,
    "media_id": str,
    "duration": int,         # Duração em segundos
    "phone": str,
    "error": str
}
```

**Exemplo de Uso**:
```python
# Enviar explicação em áudio
await send_audio_message(
    "5511999999999",
    "https://example.com/explicacao-solar.mp3",
    is_voice_note=True
)
```

**Formatos Suportados**:
- MP3, OGG, WAV, M4A, AAC

**Notas**:
- `is_voice_note=True` mostra como mensagem de voz
- Duração máxima recomendada: 5 minutos
- Áudios longos podem ser rejeitados

---

### 1.6 send_location_message

**Propósito**: Envia localização geográfica via WhatsApp.

**Assinatura**:
```python
async def send_location_message(
    phone: str,
    latitude: float,
    longitude: float,
    name: Optional[str] = None,
    address: Optional[str] = None
) -> Dict[str, Any]
```

**Parâmetros**:
- `phone` (str, obrigatório): Número do destinatário
- `latitude` (float, obrigatório): Latitude da localização
- `longitude` (float, obrigatório): Longitude da localização
- `name` (str, opcional): Nome do local
- `address` (str, opcional): Endereço completo

**Retorno**:
```python
{
    "success": bool,
    "message_id": str,
    "location": {
        "latitude": float,
        "longitude": float,
        "name": str,
        "address": str
    },
    "phone": str,
    "error": str
}
```

**Exemplo de Uso**:
```python
# Enviar localização do escritório
await send_location_message(
    "5511999999999",
    -8.05428,
    -34.8813,
    name="SolarPrime Boa Viagem",
    address="Av. Boa Viagem, 123 - Recife, PE"
)
```

**Notas**:
- Útil para reuniões presenciais
- Coordenadas devem ser válidas
- Integra com apps de mapas do destinatário

---

### 1.7 message_chunking

**Propósito**: Divide mensagens longas em chunks menores para melhor legibilidade.

**Assinatura**:
```python
async def message_chunking(
    text: str,
    max_chunk_size: int = 1000,
    preserve_paragraphs: bool = True,
    add_continuation: bool = True
) -> Dict[str, Any]
```

**Parâmetros**:
- `text` (str, obrigatório): Texto a ser dividido
- `max_chunk_size` (int, opcional): Tamanho máximo de cada chunk (padrão: 1000)
- `preserve_paragraphs` (bool, opcional): Preservar parágrafos inteiros (padrão: True)
- `add_continuation` (bool, opcional): Adicionar "..." entre chunks (padrão: True)

**Retorno**:
```python
{
    "success": bool,
    "chunks": List[str],     # Lista de chunks
    "chunk_count": int,      # Número de chunks
    "total_length": int,     # Tamanho total do texto
    "error": str
}
```

**Exemplo de Uso**:
```python
# Dividir explicação longa
result = await message_chunking(texto_longo, max_chunk_size=500)
for chunk in result["chunks"]:
    await send_text_message("5511999999999", chunk)
```

**Notas**:
- Evita quebrar palavras ou frases
- Preserva formatação quando possível
- Ideal para mensagens > 1000 caracteres

---

### 1.8 message_buffer

**Propósito**: Agrupa múltiplas mensagens pequenas antes de enviar.

**Assinatura**:
```python
async def message_buffer(
    phone: str,
    message: str,
    buffer_time: int = 3,
    max_buffer_size: int = 5,
    force_send: bool = False
) -> Dict[str, Any]
```

**Parâmetros**:
- `phone` (str, obrigatório): Número do destinatário
- `message` (str, obrigatório): Mensagem a adicionar ao buffer
- `buffer_time` (int, opcional): Tempo de espera em segundos (padrão: 3)
- `max_buffer_size` (int, opcional): Máximo de mensagens no buffer (padrão: 5)
- `force_send` (bool, opcional): Forçar envio imediato (padrão: False)

**Retorno**:
```python
{
    "success": bool,
    "buffered": bool,        # Se foi adicionado ao buffer
    "sent": bool,            # Se foi enviado
    "buffer_size": int,      # Tamanho atual do buffer
    "messages_sent": List[str],  # Mensagens enviadas
    "error": str
}
```

**Exemplo de Uso**:
```python
# Agrupar respostas curtas
await message_buffer("5511999999999", "✅ Nome recebido")
await message_buffer("5511999999999", "✅ Telefone validado")
await message_buffer("5511999999999", "✅ Endereço confirmado", force_send=True)
```

**Notas**:
- Reduz spam de notificações
- Melhora experiência do usuário
- Útil para confirmações e status updates

---

## 2. Kommo Tools (6 ferramentas)

Ferramentas para integração com o CRM Kommo.

### 2.1 create_kommo_lead

**Propósito**: Cria um novo lead no Kommo CRM.

**Assinatura**:
```python
async def create_kommo_lead(
    name: str,
    phone: str,
    email: Optional[str] = None,
    custom_fields: Optional[Dict[str, Any]] = None,
    tags: Optional[List[str]] = None,
    initial_stage: str = "NOVO_LEAD"
) -> Dict[str, Any]
```

**Parâmetros**:
- `name` (str, obrigatório): Nome completo do lead
- `phone` (str, obrigatório): Telefone do lead
- `email` (str, opcional): Email do lead
- `custom_fields` (dict, opcional): Campos customizados {field_id: value}
- `tags` (list, opcional): Lista de tags para o lead
- `initial_stage` (str, opcional): Estágio inicial no pipeline

**Retorno**:
```python
{
    "success": bool,
    "lead_id": int,          # ID do lead no Kommo
    "lead": {
        "id": int,
        "name": str,
        "phone": str,
        "email": str,
        "status_id": int,
        "pipeline_id": int,
        "created_at": int,
        "tags": List[str]
    },
    "message": str,
    "already_exists": bool,   # Se lead já existia
    "error": str
}
```

**Exemplo de Uso**:
```python
# Criar lead com tags
await create_kommo_lead(
    name="João Silva",
    phone="5511999999999",
    email="joao@email.com",
    tags=["WhatsApp", "Interesse Alto", "Recife"],
    initial_stage="EM_NEGOCIACAO"
)
```

**Estágios Disponíveis**:
- `NOVO_LEAD`: Novo lead (padrão)
- `EM_NEGOCIACAO`: Em negociação
- `EM_QUALIFICACAO`: Em qualificação
- `QUALIFICADO`: Qualificado
- `REUNIAO_AGENDADA`: Reunião agendada
- `NAO_INTERESSADO`: Não interessado

**Notas**:
- Verifica duplicidade por telefone
- Tags são criadas automaticamente se não existirem
- Integra com pipeline de vendas configurado

---

### 2.2 update_kommo_lead

**Propósito**: Atualiza informações de um lead existente no Kommo.

**Assinatura**:
```python
async def update_kommo_lead(
    lead_id: int,
    name: Optional[str] = None,
    custom_fields: Optional[Dict[str, Any]] = None,
    responsible_user_id: Optional[int] = None,
    tags_to_add: Optional[List[str]] = None,
    tags_to_remove: Optional[List[str]] = None
) -> Dict[str, Any]
```

**Parâmetros**:
- `lead_id` (int, obrigatório): ID do lead no Kommo
- `name` (str, opcional): Novo nome do lead
- `custom_fields` (dict, opcional): Campos para atualizar
- `responsible_user_id` (int, opcional): ID do usuário responsável
- `tags_to_add` (list, opcional): Tags para adicionar
- `tags_to_remove` (list, opcional): Tags para remover

**Retorno**:
```python
{
    "success": bool,
    "lead_id": int,
    "updated_fields": List[str],  # Campos atualizados
    "lead": dict,                  # Dados atualizados
    "error": str
}
```

**Exemplo de Uso**:
```python
# Atualizar lead com valor da conta
await update_kommo_lead(
    lead_id=12345,
    custom_fields={
        "conta_luz_valor": 450.00,
        "consumo_kwh": 320,
        "tem_desconto": False
    },
    tags_to_add=["Conta Alta", "Potencial Bom"]
)
```

**Campos Customizados Comuns**:
- `conta_luz_valor`: Valor da conta de luz
- `consumo_kwh`: Consumo em kWh
- `tipo_imovel`: Tipo de imóvel
- `tem_desconto`: Se já tem desconto
- `economia_estimada`: Economia estimada

**Notas**:
- Mantém histórico de alterações
- Dispara webhooks de atualização
- Atualiza modificação timestamp

---

### 2.3 add_kommo_note

**Propósito**: Adiciona uma nota/comentário ao lead no Kommo.

**Assinatura**:
```python
async def add_kommo_note(
    lead_id: int,
    text: str,
    note_type: str = "common",
    created_by: Optional[int] = None
) -> Dict[str, Any]
```

**Parâmetros**:
- `lead_id` (int, obrigatório): ID do lead
- `text` (str, obrigatório): Texto da nota
- `note_type` (str, opcional): Tipo da nota (padrão: "common")
- `created_by` (int, opcional): ID do usuário criador

**Retorno**:
```python
{
    "success": bool,
    "note_id": int,          # ID da nota criada
    "lead_id": int,
    "created_at": int,       # Timestamp
    "error": str
}
```

**Exemplo de Uso**:
```python
# Adicionar nota de qualificação
await add_kommo_note(
    lead_id=12345,
    text="Lead qualificado via WhatsApp. Conta de luz: R$ 450. Interesse em economia de 95%. Agendou reunião para segunda-feira.",
    note_type="common"
)
```

**Tipos de Nota**:
- `common`: Nota comum (padrão)
- `call_in`: Ligação recebida
- `call_out`: Ligação realizada
- `service_message`: Mensagem do sistema

**Notas**:
- Aparece na timeline do lead
- Suporta formatação básica
- Útil para histórico de interações

---

### 2.4 schedule_kommo_activity

**Propósito**: Agenda uma atividade/tarefa para um lead no Kommo.

**Assinatura**:
```python
async def schedule_kommo_activity(
    lead_id: int,
    text: str,
    complete_till: datetime,
    task_type: int = 1,
    responsible_user_id: Optional[int] = None
) -> Dict[str, Any]
```

**Parâmetros**:
- `lead_id` (int, obrigatório): ID do lead
- `text` (str, obrigatório): Descrição da atividade
- `complete_till` (datetime, obrigatório): Data/hora limite
- `task_type` (int, opcional): Tipo da tarefa (padrão: 1)
- `responsible_user_id` (int, opcional): ID do responsável

**Retorno**:
```python
{
    "success": bool,
    "task_id": int,          # ID da tarefa criada
    "lead_id": int,
    "complete_till": str,    # ISO format
    "responsible_user": int,
    "error": str
}
```

**Exemplo de Uso**:
```python
from datetime import datetime, timedelta

# Agendar follow-up
tomorrow = datetime.now() + timedelta(days=1)
await schedule_kommo_activity(
    lead_id=12345,
    text="Follow-up: Verificar se recebeu proposta",
    complete_till=tomorrow,
    task_type=1
)
```

**Tipos de Tarefa**:
- `1`: Ligação
- `2`: Reunião
- `3`: Email

**Notas**:
- Cria lembretes para vendedores
- Aparece no calendário do Kommo
- Notifica responsável

---

### 2.5 update_kommo_stage

**Propósito**: Move o lead para outro estágio do pipeline.

**Assinatura**:
```python
async def update_kommo_stage(
    lead_id: int,
    stage: str,
    loss_reason_id: Optional[int] = None,
    closed_at: Optional[datetime] = None
) -> Dict[str, Any]
```

**Parâmetros**:
- `lead_id` (int, obrigatório): ID do lead
- `stage` (str, obrigatório): Novo estágio
- `loss_reason_id` (int, opcional): ID do motivo de perda
- `closed_at` (datetime, opcional): Data de fechamento

**Retorno**:
```python
{
    "success": bool,
    "lead_id": int,
    "old_stage": str,        # Estágio anterior
    "new_stage": str,        # Novo estágio
    "pipeline_id": int,
    "error": str
}
```

**Exemplo de Uso**:
```python
# Mover para qualificado
await update_kommo_stage(
    lead_id=12345,
    stage="QUALIFICADO"
)

# Marcar como perdido
await update_kommo_stage(
    lead_id=12345,
    stage="NAO_INTERESSADO",
    loss_reason_id=1
)
```

**Notas**:
- Dispara automações do pipeline
- Registra histórico de movimentação
- Atualiza métricas do funil

---

### 2.6 search_kommo_lead

**Propósito**: Busca leads no Kommo por diversos critérios.

**Assinatura**:
```python
async def search_kommo_lead(
    query: Optional[str] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    limit: int = 10,
    with_contacts: bool = True
) -> Dict[str, Any]
```

**Parâmetros**:
- `query` (str, opcional): Termo de busca geral
- `phone` (str, opcional): Buscar por telefone
- `email` (str, opcional): Buscar por email
- `limit` (int, opcional): Limite de resultados (padrão: 10)
- `with_contacts` (bool, opcional): Incluir contatos (padrão: True)

**Retorno**:
```python
{
    "success": bool,
    "count": int,            # Número de resultados
    "leads": List[{
        "id": int,
        "name": str,
        "status_id": int,
        "pipeline_id": int,
        "price": int,
        "created_at": int,
        "updated_at": int,
        "contacts": List[dict]
    }],
    "error": str
}
```

**Exemplo de Uso**:
```python
# Buscar por telefone
result = await search_kommo_lead(
    phone="5511999999999",
    with_contacts=True
)

if result["count"] > 0:
    lead = result["leads"][0]
    print(f"Lead encontrado: {lead['name']}")
```

**Notas**:
- Busca é case-insensitive
- Retorna máximo 250 resultados
- Ordena por relevância

---

## 3. Calendar Tools (5 ferramentas)

Ferramentas para gerenciamento de agenda e reuniões via Google Calendar.

### 3.1 check_calendar_availability

**Propósito**: Verifica disponibilidade no calendário para agendamento.

**Assinatura**:
```python
async def check_availability(
    date: str,
    duration_minutes: int = 60,
    timezone: str = "America/Sao_Paulo",
    check_days_ahead: int = 1
) -> Dict[str, Any]
```

**Parâmetros**:
- `date` (str, obrigatório): Data inicial (formato: YYYY-MM-DD)
- `duration_minutes` (int, opcional): Duração da reunião (padrão: 60)
- `timezone` (str, opcional): Timezone (padrão: America/Sao_Paulo)
- `check_days_ahead` (int, opcional): Dias à frente para verificar (padrão: 1)

**Retorno**:
```python
{
    "success": bool,
    "available_slots": List[{
        "date": str,         # YYYY-MM-DD
        "start_time": str,   # HH:MM
        "end_time": str,     # HH:MM
        "duration_minutes": int,
        "timezone": str,
        "iso_start": str,    # ISO format
        "iso_end": str       # ISO format
    }],
    "total_slots": int,
    "business_hours": dict,
    "query_period": dict,
    "error": str
}
```

**Exemplo de Uso**:
```python
# Verificar agenda para amanhã
from datetime import date, timedelta

tomorrow = (date.today() + timedelta(days=1)).isoformat()
result = await check_availability(
    date=tomorrow,
    duration_minutes=45,
    check_days_ahead=3
)

# Apresentar opções ao cliente
for slot in result["available_slots"][:3]:
    print(f"📅 {slot['date']} às {slot['start_time']}")
```

**Horário Comercial**:
- Segunda-Sexta: 08:00 - 18:00
- Sábado: 08:00 - 13:00
- Domingo: Fechado

**Notas**:
- Usa FreeBusy API do Google
- Considera eventos existentes
- Respeita horário comercial configurado

---

### 3.2 create_meeting

**Propósito**: Cria uma reunião no Google Calendar.

**Assinatura**:
```python
async def create_meeting(
    title: str,
    start_time: datetime,
    duration_minutes: int = 60,
    attendees: List[str] = None,
    description: Optional[str] = None,
    location: Optional[str] = None,
    send_notifications: bool = True,
    meeting_link: bool = True
) -> Dict[str, Any]
```

**Parâmetros**:
- `title` (str, obrigatório): Título da reunião
- `start_time` (datetime, obrigatório): Início da reunião
- `duration_minutes` (int, opcional): Duração em minutos (padrão: 60)
- `attendees` (list, opcional): Lista de emails dos participantes
- `description` (str, opcional): Descrição/agenda da reunião
- `location` (str, opcional): Local ou endereço
- `send_notifications` (bool, opcional): Enviar convites (padrão: True)
- `meeting_link` (bool, opcional): Criar Google Meet (padrão: True)

**Retorno**:
```python
{
    "success": bool,
    "event_id": str,         # ID do evento no Calendar
    "event_link": str,       # Link para o evento
    "meet_link": str,        # Link do Google Meet
    "start": str,            # ISO format
    "end": str,              # ISO format
    "attendees": List[str],
    "error": str
}
```

**Exemplo de Uso**:
```python
from datetime import datetime, timedelta

# Agendar para amanhã às 14h
start = datetime.now() + timedelta(days=1, hours=14)

result = await create_meeting(
    title="Apresentação Sistema Solar - João Silva",
    start_time=start,
    duration_minutes=45,
    attendees=["joao@email.com"],
    description="Apresentação da proposta de energia solar com economia de até 95%",
    location="Online via Google Meet",
    meeting_link=True
)

print(f"Reunião criada! Link: {result['meet_link']}")
```

**Notas**:
- Cria evento no calendário principal
- Google Meet link automático
- Envia convites por email
- Suporta recorrência (feature futura)

---

### 3.3 update_meeting

**Propósito**: Atualiza uma reunião existente no calendário.

**Assinatura**:
```python
async def update_meeting(
    event_id: str,
    title: Optional[str] = None,
    start_time: Optional[datetime] = None,
    duration_minutes: Optional[int] = None,
    description: Optional[str] = None,
    location: Optional[str] = None,
    attendees: Optional[List[str]] = None,
    send_updates: str = "all"
) -> Dict[str, Any]
```

**Parâmetros**:
- `event_id` (str, obrigatório): ID do evento no Calendar
- `title` (str, opcional): Novo título
- `start_time` (datetime, opcional): Novo horário de início
- `duration_minutes` (int, opcional): Nova duração
- `description` (str, opcional): Nova descrição
- `location` (str, opcional): Novo local
- `attendees` (list, opcional): Nova lista de participantes
- `send_updates` (str, opcional): "all", "externalOnly", "none"

**Retorno**:
```python
{
    "success": bool,
    "event_id": str,
    "updated_fields": List[str],
    "event": dict,           # Dados atualizados
    "error": str
}
```

**Exemplo de Uso**:
```python
# Reagendar reunião
new_time = datetime.now() + timedelta(days=2, hours=15)

await update_meeting(
    event_id="abc123xyz",
    start_time=new_time,
    send_updates="all"
)
```

**Notas**:
- Notifica participantes das mudanças
- Mantém histórico de alterações
- Preserva Google Meet link

---

### 3.4 cancel_meeting

**Propósito**: Cancela uma reunião agendada.

**Assinatura**:
```python
async def cancel_meeting(
    event_id: str,
    send_notifications: bool = True,
    cancellation_reason: Optional[str] = None
) -> Dict[str, Any]
```

**Parâmetros**:
- `event_id` (str, obrigatório): ID do evento
- `send_notifications` (bool, opcional): Notificar participantes (padrão: True)
- `cancellation_reason` (str, opcional): Motivo do cancelamento

**Retorno**:
```python
{
    "success": bool,
    "event_id": str,
    "cancelled_at": str,     # ISO format
    "notified_count": int,   # Participantes notificados
    "error": str
}
```

**Exemplo de Uso**:
```python
# Cancelar com motivo
await cancel_meeting(
    event_id="abc123xyz",
    cancellation_reason="Cliente solicitou reagendamento",
    send_notifications=True
)
```

**Notas**:
- Remove do calendário de todos
- Envia email de cancelamento
- Registra no histórico do lead

---

### 3.5 send_calendar_invite

**Propósito**: Envia convite de calendário via email.

**Assinatura**:
```python
async def send_calendar_invite(
    event_id: str,
    additional_attendees: List[str],
    custom_message: Optional[str] = None,
    send_copy_to_organizer: bool = False
) -> Dict[str, Any]
```

**Parâmetros**:
- `event_id` (str, obrigatório): ID do evento
- `additional_attendees` (list, obrigatório): Novos emails para convidar
- `custom_message` (str, opcional): Mensagem personalizada
- `send_copy_to_organizer` (bool, opcional): Cópia para organizador

**Retorno**:
```python
{
    "success": bool,
    "event_id": str,
    "invites_sent": int,
    "attendees": List[str],
    "error": str
}
```

**Exemplo de Uso**:
```python
# Convidar pessoas adicionais
await send_calendar_invite(
    event_id="abc123xyz",
    additional_attendees=["gerente@empresa.com"],
    custom_message="Adicionando o gerente conforme solicitado"
)
```

**Notas**:
- Não duplica convites existentes
- Atualiza lista de participantes
- Mantém RSVP status

---

## 4. Database Tools (6 ferramentas)

Ferramentas para gerenciamento de dados no Supabase.

### 4.1 get_lead_data

**Propósito**: Busca dados de um lead no banco de dados.

**Assinatura**:
```python
async def get_lead(
    lead_id: Optional[str] = None,
    phone: Optional[str] = None,
    include_qualification: bool = False,
    include_follow_ups: bool = False
) -> Dict[str, Any]
```

**Parâmetros**:
- `lead_id` (str, opcional): UUID do lead
- `phone` (str, opcional): Número de telefone
- `include_qualification` (bool, opcional): Incluir dados de qualificação
- `include_follow_ups` (bool, opcional): Incluir follow-ups pendentes

**Retorno**:
```python
{
    "success": bool,
    "lead_id": str,
    "data": {
        "name": str,
        "phone": str,
        "email": str,
        "document": str,
        "property_type": str,
        "address": str,
        "bill_value": float,
        "consumption_kwh": int,
        "stage": str,
        "qualification_score": int,
        "interested": bool,
        "kommo_lead_id": int,
        "created_at": str,
        "updated_at": str
    },
    "qualification": dict,    # Se solicitado
    "follow_ups": List[dict], # Se solicitado
    "error": str
}
```

**Exemplo de Uso**:
```python
# Buscar lead completo
lead = await get_lead(
    phone="5511999999999",
    include_qualification=True,
    include_follow_ups=True
)

if lead["success"]:
    print(f"Lead: {lead['data']['name']}")
    print(f"Score: {lead['data']['qualification_score']}")
```

**Notas**:
- Busca por ID ou telefone
- Inclui dados relacionados opcionalmente
- Formata telefone automaticamente

---

### 4.2 update_lead_data

**Propósito**: Atualiza informações de um lead existente.

**Assinatura**:
```python
async def update_lead(
    lead_id: str,
    name: Optional[str] = None,
    email: Optional[str] = None,
    document: Optional[str] = None,
    property_type: Optional[str] = None,
    address: Optional[str] = None,
    bill_value: Optional[float] = None,
    consumption_kwh: Optional[int] = None,
    current_stage: Optional[str] = None,
    qualification_score: Optional[int] = None,
    interested: Optional[bool] = None,
    kommo_lead_id: Optional[int] = None,
    qualification_data: Optional[Dict] = None
) -> Dict[str, Any]
```

**Parâmetros**:
- `lead_id` (str, obrigatório): UUID do lead
- Todos os outros campos são opcionais para atualização

**Retorno**:
```python
{
    "success": bool,
    "lead_id": str,
    "updated_fields": List[str],
    "data": dict,            # Dados atualizados
    "qualification_updated": bool,
    "error": str
}
```

**Exemplo de Uso**:
```python
# Atualizar após receber conta de luz
await update_lead(
    lead_id="uuid-aqui",
    bill_value=485.90,
    consumption_kwh=420,
    property_type="CASA",
    qualification_score=85,
    qualification_data={
        "has_own_property": True,
        "decision_maker": True,
        "urgency_level": "ALTA"
    }
)
```

**Tipos de Propriedade**:
- `CASA`: Casa
- `APARTAMENTO`: Apartamento
- `COMERCIO`: Comércio
- `INDUSTRIA`: Indústria
- `RURAL`: Rural

**Notas**:
- Atualiza timestamp automaticamente
- Valida tipos de dados
- Mantém histórico de alterações

---

### 4.3 save_message

**Propósito**: Salva mensagens da conversa no histórico.

**Assinatura**:
```python
async def save_message(
    conversation_id: str,
    phone: str,
    message: str,
    role: str = "user",
    media_url: Optional[str] = None,
    media_type: Optional[str] = None,
    metadata: Optional[Dict] = None
) -> Dict[str, Any]
```

**Parâmetros**:
- `conversation_id` (str, obrigatório): UUID da conversa
- `phone` (str, obrigatório): Número do remetente
- `message` (str, obrigatório): Conteúdo da mensagem
- `role` (str, opcional): "user" ou "assistant" (padrão: "user")
- `media_url` (str, opcional): URL de mídia anexada
- `media_type` (str, opcional): Tipo de mídia
- `metadata` (dict, opcional): Metadados adicionais

**Retorno**:
```python
{
    "success": bool,
    "message_id": str,       # UUID da mensagem
    "conversation_id": str,
    "created_at": str,       # ISO format
    "error": str
}
```

**Exemplo de Uso**:
```python
# Salvar mensagem com imagem
await save_message(
    conversation_id="conv-uuid",
    phone="5511999999999",
    message="Segue foto da minha conta de luz",
    role="user",
    media_url="https://example.com/conta.jpg",
    media_type="image",
    metadata={
        "extracted_value": 485.90,
        "extracted_kwh": 420
    }
)
```

**Notas**:
- Mantém ordem cronológica
- Suporta mídia e metadados
- Usado para contexto do agente

---

### 4.4 update_conversation_session

**Propósito**: Atualiza dados da sessão de conversa.

**Assinatura**:
```python
async def update_conversation(
    conversation_id: str,
    lead_id: Optional[str] = None,
    status: Optional[str] = None,
    last_activity: Optional[datetime] = None,
    metadata: Optional[Dict] = None,
    increment_message_count: bool = False
) -> Dict[str, Any]
```

**Parâmetros**:
- `conversation_id` (str, obrigatório): UUID da conversa
- `lead_id` (str, opcional): Associar a um lead
- `status` (str, opcional): Status da conversa
- `last_activity` (datetime, opcional): Última atividade
- `metadata` (dict, opcional): Metadados da sessão
- `increment_message_count` (bool, opcional): Incrementar contador

**Retorno**:
```python
{
    "success": bool,
    "conversation_id": str,
    "updated_fields": List[str],
    "message_count": int,
    "error": str
}
```

**Status de Conversa**:
- `active`: Em andamento
- `completed`: Concluída
- `abandoned`: Abandonada
- `scheduled`: Agendada

**Exemplo de Uso**:
```python
# Marcar conversa como concluída
await update_conversation(
    conversation_id="conv-uuid",
    status="completed",
    metadata={
        "outcome": "meeting_scheduled",
        "qualification_score": 85
    }
)
```

**Notas**:
- Atualiza last_activity automaticamente
- Incrementa contadores atomicamente
- Útil para analytics

---

### 4.5 schedule_followup

**Propósito**: Agenda um follow-up automático para o lead.

**Assinatura**:
```python
async def schedule_followup(
    lead_id: str,
    scheduled_at: datetime,
    message: str,
    type: str = "WHATSAPP",
    attempt_number: int = 1,
    metadata: Optional[Dict] = None
) -> Dict[str, Any]
```

**Parâmetros**:
- `lead_id` (str, obrigatório): UUID do lead
- `scheduled_at` (datetime, obrigatório): Quando executar
- `message` (str, obrigatório): Mensagem do follow-up
- `type` (str, opcional): Tipo do follow-up (padrão: "WHATSAPP")
- `attempt_number` (int, opcional): Número da tentativa
- `metadata` (dict, opcional): Dados adicionais

**Retorno**:
```python
{
    "success": bool,
    "followup_id": str,      # UUID do follow-up
    "lead_id": str,
    "scheduled_at": str,     # ISO format
    "status": str,
    "error": str
}
```

**Exemplo de Uso**:
```python
from datetime import datetime, timedelta

# Agendar para 30 minutos
followup_time = datetime.now() + timedelta(minutes=30)

await schedule_followup(
    lead_id="lead-uuid",
    scheduled_at=followup_time,
    message="Oi! Vi que você demonstrou interesse em economizar na conta de luz. Ainda posso ajudar? 😊",
    type="WHATSAPP",
    attempt_number=1,
    metadata={
        "reason": "no_response",
        "last_stage": "qualification"
    }
)
```

**Tipos de Follow-up**:
- `WHATSAPP`: Mensagem WhatsApp
- `EMAIL`: Email automático
- `TASK`: Tarefa para vendedor

**Notas**:
- Executado por worker Celery
- Máximo 3 tentativas por padrão
- Respeita horário comercial

---

### 4.6 create_new_lead

**Propósito**: Cria um novo lead no banco de dados.

**Assinatura**:
```python
async def create_lead(
    name: str,
    phone: str,
    email: Optional[str] = None,
    document: Optional[str] = None,
    property_type: Optional[str] = None,
    address: Optional[str] = None,
    source: str = "WHATSAPP",
    initial_message: Optional[str] = None
) -> Dict[str, Any]
```

**Parâmetros**:
- `name` (str, obrigatório): Nome completo
- `phone` (str, obrigatório): Telefone principal
- `email` (str, opcional): Email do lead
- `document` (str, opcional): CPF/CNPJ
- `property_type` (str, opcional): Tipo de imóvel
- `address` (str, opcional): Endereço completo
- `source` (str, opcional): Origem do lead (padrão: "WHATSAPP")
- `initial_message` (str, opcional): Primeira mensagem

**Retorno**:
```python
{
    "success": bool,
    "lead_id": str,          # UUID do lead criado
    "conversation_id": str,  # UUID da conversa criada
    "data": dict,            # Dados do lead
    "error": str
}
```

**Exemplo de Uso**:
```python
# Criar lead do WhatsApp
result = await create_lead(
    name="Maria Santos",
    phone="5511888888888",
    source="WHATSAPP",
    initial_message="Olá, vi o anúncio sobre energia solar"
)

print(f"Lead criado: {result['lead_id']}")
```

**Sources Disponíveis**:
- `WHATSAPP`: WhatsApp (padrão)
- `WEBSITE`: Site
- `INSTAGRAM`: Instagram
- `FACEBOOK`: Facebook
- `INDICACAO`: Indicação

**Notas**:
- Cria conversa automaticamente
- Verifica duplicidade por telefone
- Inicializa com stage "NOVO"

---

## 5. Media Tools (3 ferramentas)

Ferramentas para processamento de mídia recebida via WhatsApp.

### 5.1 process_image

**Propósito**: Processa imagens para análise pelo Gemini 2.5 Pro.

**Assinatura**:
```python
async def process_image(
    media_url: str,
    context: Optional[str] = None,
    extract_text: bool = True
) -> Dict[str, Any]
```

**Parâmetros**:
- `media_url` (str, obrigatório): URL da imagem
- `context` (str, opcional): Contexto da imagem
- `extract_text` (bool, opcional): Extrair texto via OCR (padrão: True)

**Retorno**:
```python
{
    "success": bool,
    "type": str,             # "image"
    "image_type": str,       # Tipo detectado
    "format": str,           # jpg, png, etc.
    "file_name": str,
    "media_url": str,
    "ready_for_gemini": bool,
    "context": str,
    "analysis_hints": List[str],
    "metadata": dict,
    "special_instructions": dict,  # Se conta de luz
    "error": str
}
```

**Exemplo de Uso**:
```python
# Processar conta de luz
result = await process_image(
    media_url="https://example.com/conta-luz.jpg",
    context="conta de luz",
    extract_text=True
)

# Resultado inclui hints para análise
print(result["analysis_hints"])
# ["Extrair valor da conta", "Identificar consumo em kWh", ...]
```

**Tipos de Imagem Detectados**:
- `conta_energia`: Conta de luz/energia
- `local_instalacao`: Local para instalação
- `documento`: Documentos pessoais
- `generic`: Outros tipos

**Formatos Suportados**:
- JPEG, JPG, PNG, GIF, WEBP, BMP, TIFF

**Notas**:
- Prepara imagem para análise multimodal
- Detecta tipo automaticamente pelo contexto
- Fornece hints específicos por tipo

---

### 5.2 process_document

**Propósito**: Processa documentos PDF e outros formatos.

**Assinatura**:
```python
async def process_document(
    media_url: str,
    document_type: Optional[str] = None,
    extract_data: bool = True,
    page_limit: int = 10
) -> Dict[str, Any]
```

**Parâmetros**:
- `media_url` (str, obrigatório): URL do documento
- `document_type` (str, opcional): Tipo do documento
- `extract_data` (bool, opcional): Extrair dados (padrão: True)
- `page_limit` (int, opcional): Limite de páginas (padrão: 10)

**Retorno**:
```python
{
    "success": bool,
    "type": str,             # "document"
    "document_type": str,    # Tipo detectado
    "format": str,           # pdf, doc, etc.
    "file_name": str,
    "media_url": str,
    "page_count": int,       # Número de páginas
    "size_mb": float,        # Tamanho em MB
    "analysis_hints": List[str],
    "metadata": dict,
    "error": str
}
```

**Exemplo de Uso**:
```python
# Processar proposta em PDF
result = await process_document(
    media_url="https://example.com/proposta-concorrente.pdf",
    document_type="proposta",
    extract_data=True
)

if result["success"]:
    print(f"Documento com {result['page_count']} páginas")
```

**Tipos de Documento**:
- `conta_energia`: Faturas de energia
- `proposta`: Propostas comerciais
- `contrato`: Contratos
- `identidade`: Documentos pessoais

**Formatos Suportados**:
- PDF, DOC, DOCX, XLS, XLSX, PPT, PPTX, TXT

**Notas**:
- Limite de 100MB por arquivo
- Extração depende do formato
- PDFs com OCR quando necessário

---

### 5.3 process_audio

**Propósito**: Processa áudios para transcrição e análise.

**Assinatura**:
```python
async def process_audio(
    media_url: str,
    language: str = "pt-BR",
    identify_speaker: bool = False,
    enhance_quality: bool = True
) -> Dict[str, Any]
```

**Parâmetros**:
- `media_url` (str, obrigatório): URL do áudio
- `language` (str, opcional): Idioma para transcrição (padrão: pt-BR)
- `identify_speaker` (bool, opcional): Identificar falante (padrão: False)
- `enhance_quality` (bool, opcional): Melhorar qualidade (padrão: True)

**Retorno**:
```python
{
    "success": bool,
    "type": str,             # "audio"
    "format": str,           # mp3, ogg, etc.
    "duration_seconds": int,
    "file_name": str,
    "media_url": str,
    "ready_for_transcription": bool,
    "language": str,
    "quality_info": {
        "bitrate": int,
        "sample_rate": int,
        "channels": int
    },
    "metadata": dict,
    "error": str
}
```

**Exemplo de Uso**:
```python
# Processar mensagem de voz
result = await process_audio(
    media_url="https://example.com/audio-cliente.ogg",
    language="pt-BR",
    enhance_quality=True
)

print(f"Áudio de {result['duration_seconds']} segundos")
```

**Formatos Suportados**:
- MP3, OGG, WAV, M4A, AAC, OPUS

**Notas**:
- Preparação para transcrição via Gemini
- Melhoria de qualidade automática
- Suporta áudios até 5 minutos

---

## 6. Utility Tools (2 ferramentas)

Ferramentas utilitárias para validação e formatação.

### 6.1 format_currency

**Propósito**: Formata valores monetários no padrão brasileiro.

**Assinatura**:
```python
async def format_currency(
    value: Union[str, float, int],
    validate: bool = True,
    include_cents: bool = True
) -> Dict[str, Any]
```

**Parâmetros**:
- `value` (str/float/int, obrigatório): Valor a formatar
- `validate` (bool, opcional): Validar para conta de luz (padrão: True)
- `include_cents` (bool, opcional): Incluir centavos (padrão: True)

**Retorno**:
```python
{
    "success": bool,
    "original": str,         # Valor original
    "formatted": str,        # Valor formatado
    "numeric_value": float,  # Valor numérico
    "is_valid_bill": bool,   # Se validate=True
    "validation_message": str,  # Se inválido
    "error": str
}
```

**Exemplo de Uso**:
```python
# Formatar valor de conta
result = await format_currency("485.90", validate=True)
print(result["formatted"])  # "R$ 485,90"

# Extrair de texto
result = await extract_currency_from_text(
    "Minha conta veio 485,90 esse mês"
)
print(result["values"][0]["formatted"])  # "R$ 485,90"
```

**Validação de Conta**:
- Mínimo: R$ 50,00
- Máximo: R$ 10.000,00
- Aviso se fora dos limites

**Notas**:
- Aceita vários formatos de entrada
- Extrai valores de texto
- Valida faixa para energia residencial

---

### 6.2 validate_phone

**Propósito**: Valida e formata números de telefone brasileiros.

**Assinatura**:
```python
async def validate_phone(
    phone: str,
    accept_landline: bool = False,
    region: Optional[str] = None
) -> Dict[str, Any]
```

**Parâmetros**:
- `phone` (str, obrigatório): Número para validar
- `accept_landline` (bool, opcional): Aceitar fixo (padrão: False)
- `region` (str, opcional): Filtrar por DDD/região

**Retorno**:
```python
{
    "success": bool,
    "is_valid": bool,
    "formatted": str,        # Formato internacional
    "national": str,         # Formato nacional
    "whatsapp": str,         # Formato WhatsApp
    "type": str,             # "mobile" ou "landline"
    "carrier": str,          # Operadora detectada
    "region": str,           # Estado/região
    "error": str
}
```

**Exemplo de Uso**:
```python
# Validar celular
result = await validate_phone("(11) 98888-9999")

if result["is_valid"]:
    print(f"WhatsApp: {result['whatsapp']}")  # "5511988889999"
    print(f"Região: {result['region']}")      # "SP"
```

**Detecção de Operadora**:
- Vivo, Claro, TIM, Oi
- Baseado no prefixo
- Pode estar desatualizado com portabilidade

**Formatos Aceitos**:
- (11) 98888-9999
- 11988889999
- +5511988889999
- 11 9 8888-9999

**Notas**:
- Remove caracteres especiais
- Adiciona código do país
- Valida quantidade de dígitos

---

## Melhores Práticas

### 1. Tratamento de Erros
Sempre verifique o campo `success` antes de usar os dados:

```python
result = await send_text_message(phone, message)
if not result["success"]:
    logger.error(f"Erro ao enviar: {result['error']}")
    # Implementar retry ou alternativa
```

### 2. Uso de Context
Forneça contexto relevante para ferramentas de processamento:

```python
# Bom
await process_image(url, context="conta de luz do mês atual")

# Ruim
await process_image(url)
```

### 3. Encadeamento de Tools
Use ferramentas em sequência lógica:

```python
# 1. Simular digitação
await type_simulation(phone, message_preview=text)

# 2. Dividir mensagem se necessário
if len(text) > 1000:
    chunks = await message_chunking(text)
    for chunk in chunks["chunks"]:
        await send_text_message(phone, chunk)
else:
    await send_text_message(phone, text)
```

### 4. Validação de Dados
Sempre valide dados antes de salvar:

```python
# Validar telefone
phone_result = await validate_phone(raw_phone)
if phone_result["is_valid"]:
    # Validar valor
    value_result = await format_currency(raw_value)
    if value_result["is_valid_bill"]:
        # Salvar no banco
        await update_lead(lead_id, 
            phone=phone_result["formatted"],
            bill_value=value_result["numeric_value"]
        )
```

### 5. Gestão de Estado
Mantenha o estado atualizado em tempo real:

```python
# Atualizar banco local
await update_lead(lead_id, current_stage="EM_QUALIFICACAO")

# Sincronizar com Kommo
await update_kommo_stage(kommo_id, "EM_QUALIFICACAO")

# Adicionar nota
await add_kommo_note(kommo_id, "Lead avançou para qualificação via WhatsApp")
```

### 6. Performance
Use ferramentas de buffer para múltiplas operações:

```python
# Para múltiplas confirmações
await message_buffer(phone, "✓ Nome registrado")
await message_buffer(phone, "✓ Telefone validado")
await message_buffer(phone, "✓ Email confirmado", force_send=True)
```

### 7. Monitoramento
Todas as ferramentas incluem logging automático:

```python
# Logs são gerados automaticamente
# 2024-01-10 14:30:15 | INFO | Enviando mensagem de texto via WhatsApp
# 2024-01-10 14:30:16 | SUCCESS | Mensagem enviada: ID=3EB0C767D097E9ECFE8A
```

## Considerações de Performance

### Limites de Rate
- **WhatsApp**: 80 msgs/min por número
- **Kommo**: 7 requests/segundo
- **Google Calendar**: 500 requests/100 segundos

### Timeouts Recomendados
- **WhatsApp**: 30 segundos
- **Kommo**: 10 segundos
- **Calendar**: 10 segundos
- **Database**: 5 segundos

### Caching
- Disponibilidade de calendário: 5 minutos
- Dados do Kommo: 1 minuto
- Dados do lead: 30 segundos

## Conclusão

As 30 ferramentas do SDR Agent fornecem uma base completa para automação de vendas via WhatsApp. O design modular permite fácil manutenção e extensão, enquanto a integração com AGnO Framework garante execução confiável e inteligente.

Para dúvidas ou suporte, consulte a equipe de desenvolvimento ou a documentação do AGnO Framework.