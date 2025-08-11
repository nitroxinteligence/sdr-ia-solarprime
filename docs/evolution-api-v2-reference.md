# Evolution API v2 - Referência Completa

## Visão Geral

A Evolution API v2 é uma plataforma open-source para integração com WhatsApp, oferecendo uma API completa para envio de mensagens, gerenciamento de instâncias e recebimento de eventos via webhooks.

### Características Principais
- Suporta WhatsApp Web (via Baileys) e WhatsApp Business API oficial
- Integração com múltiplas plataformas (Typebot, Chatwoot, Dify, OpenAI)
- Sistema de webhooks para eventos em tempo real
- Suporte para todos os tipos de mídia do WhatsApp
- Gerenciamento de múltiplas instâncias

## Autenticação

Todas as requisições devem incluir o header de autenticação:

```http
apikey: <sua-api-key>
Content-Type: application/json
```

## Base URL

```
https://{seu-servidor}/
```

## Endpoints Principais

### 1. Gerenciamento de Instância

#### Criar Instância
```http
POST /instance/create
```

**Request Body:**
```json
{
  "instanceName": "nome-da-instancia",
  "token": "token-da-instancia",
  "qrcode": true,
  "integration": "WEBWHOOKS",
  "webhook_url": "https://seu-webhook.com/webhook",
  "webhook_by_events": true,
  "webhook_base64": true
}
```

**Response (201):**
```json
{
  "instance": {
    "instanceName": "nome-da-instancia",
    "status": "created"
  },
  "qrcode": {
    "code": "string-do-qrcode"
  }
}
```

#### Conectar Instância
```http
GET /instance/connect/{instance}
```

**Response (200):**
```json
{
  "instance": "nome-da-instancia",
  "qrcode": "2@xxxxx...",
  "qrcode_url": "data:image/png;base64,..."
}
```

#### Estado da Conexão
```http
GET /instance/connectionState/{instance}
```

**Response (200):**
```json
{
  "instance": "nome-da-instancia",
  "state": "open" | "connecting" | "close"
}
```

#### Desconectar Instância
```http
DELETE /instance/logout/{instance}
```

**Response (200):**
```json
{
  "status": "success",
  "message": "Instance disconnected"
}
```

### 2. Envio de Mensagens

#### Enviar Texto
```http
POST /message/sendText/{instance}
```

**Request Body:**
```json
{
  "number": "5511999999999",
  "text": "Mensagem de texto",
  "delay": 1200,
  "linkPreview": true,
  "mentionsEveryOne": false,
  "mentioned": ["5511888888888"],
  "quoted": {
    "key": {
      "remoteJid": "5511999999999@s.whatsapp.net",
      "fromMe": false,
      "id": "message-id"
    }
  }
}
```

**Response (201):**
```json
{
  "key": {
    "remoteJid": "5511999999999@s.whatsapp.net",
    "fromMe": true,
    "id": "BAE5xxxx"
  },
  "message": {
    "extendedTextMessage": {
      "text": "Mensagem de texto"
    }
  },
  "messageTimestamp": "1678900000",
  "status": "PENDING"
}
```

#### Enviar Mídia (Imagem/Vídeo/Documento/Áudio)
```http
POST /message/sendMedia/{instance}
```

**Request Body:**
```json
{
  "number": "5511999999999",
  "mediatype": "image" | "video" | "document" | "audio",
  "media": "data:image/jpeg;base64,/9j/4AAQ...",
  "caption": "Legenda opcional",
  "fileName": "documento.pdf",
  "ptt": true
}
```

**Parâmetros de Mídia:**
- `mediatype`: Tipo da mídia
  - `image`: Imagens (JPEG, PNG)
  - `video`: Vídeos (MP4)
  - `document`: Documentos (PDF, DOC, etc)
  - `audio`: Áudios (MP3, OGG)
- `media`: Base64 da mídia com data URI
- `caption`: Legenda (para imagem/vídeo/documento)
- `fileName`: Nome do arquivo (obrigatório para documentos)
- `ptt`: Push-to-talk (true para nota de voz)

**Response (201):**
```json
{
  "key": {
    "remoteJid": "5511999999999@s.whatsapp.net",
    "fromMe": true,
    "id": "BAE5xxxx"
  },
  "message": {
    "imageMessage": {
      "url": "https://mmg.whatsapp.net/...",
      "mimetype": "image/jpeg",
      "caption": "Legenda opcional",
      "fileSha256": "...",
      "fileLength": "12345",
      "height": 1080,
      "width": 1920,
      "mediaKey": "...",
      "jpegThumbnail": "..."
    }
  },
  "messageTimestamp": "1678900000",
  "status": "PENDING"
}
```

#### Enviar Reação
```http
POST /message/sendReaction/{instance}
```

**Request Body:**
```json
{
  "key": {
    "remoteJid": "5511999999999@s.whatsapp.net",
    "fromMe": false,
    "id": "message-id"
  },
  "reaction": "👍"
}
```

**Response (201):**
```json
{
  "key": {
    "remoteJid": "5511999999999@s.whatsapp.net",
    "fromMe": true,
    "id": "BAE5xxxx"
  },
  "message": {
    "reactionMessage": {
      "key": {...},
      "text": "👍"
    }
  },
  "messageTimestamp": "1678900000",
  "status": "PENDING"
}
```

### 3. Gerenciamento de Chats

#### Obter Chats
```http
GET /chat/findChats/{instance}
```

**Response (200):**
```json
[
  {
    "id": "5511999999999@s.whatsapp.net",
    "name": "Nome do Contato",
    "unreadCount": 5,
    "lastMessage": {
      "key": {...},
      "message": {...}
    }
  }
]
```

#### Obter Mensagens
```http
POST /chat/findMessages/{instance}
```

**Request Body:**
```json
{
  "where": {
    "remoteJid": "5511999999999@s.whatsapp.net"
  },
  "limit": 20
}
```

**Response (200):**
```json
[
  {
    "key": {
      "remoteJid": "5511999999999@s.whatsapp.net",
      "fromMe": false,
      "id": "message-id"
    },
    "message": {
      "conversation": "Texto da mensagem"
    },
    "messageTimestamp": "1678900000"
  }
]
```

#### Marcar como Lida
```http
POST /chat/markMessageAsRead/{instance}
```

**Request Body:**
```json
{
  "read_messages": [
    {
      "remoteJid": "5511999999999@s.whatsapp.net",
      "id": "message-id"
    }
  ]
}
```

#### Atualizar Presença (Digitando)
```http
POST /chat/updatePresence/{instance}
```

**Request Body:**
```json
{
  "number": "5511999999999",
  "delay": 3000,
  "state": "composing" | "paused" | "recording"
}
```

#### Obter Base64 de Mídia
```http
POST /chat/getBase64FromMediaMessage/{instance}
```

**Request Body:**
```json
{
  "message": {
    "key": {
      "id": "message-id"
    }
  },
  "convertToMp4": true
}
```

**Response (200):**
```json
{
  "base64": "/9j/4AAQSkZJRg...",
  "mimetype": "image/jpeg"
}
```

### 4. Perfil e Contatos

#### Obter Foto de Perfil
```http
POST /chat/fetchProfilePictureUrl/{instance}
```

**Request Body:**
```json
{
  "number": "5511999999999"
}
```

**Response (200):**
```json
{
  "wuid": "5511999999999@s.whatsapp.net",
  "profilePictureUrl": "https://pps.whatsapp.net/v/t61.24694-24/..."
}
```

#### Obter Perfil
```http
POST /chat/fetchProfile/{instance}
```

**Request Body:**
```json
{
  "number": "5511999999999"
}
```

**Response (200):**
```json
{
  "wuid": "5511999999999@s.whatsapp.net",
  "name": "Nome do Contato",
  "status": "Status do WhatsApp",
  "picture": "url-da-foto"
}
```

#### Obter Perfil Business
```http
POST /chat/fetchBusinessProfile/{instance}
```

**Request Body:**
```json
{
  "number": "5511999999999"
}
```

**Response (200):**
```json
{
  "wuid": "5511999999999@s.whatsapp.net",
  "business": {
    "name": "Nome da Empresa",
    "description": "Descrição",
    "category": "Categoria",
    "email": "email@empresa.com",
    "website": ["https://empresa.com"],
    "address": "Endereço"
  }
}
```

#### Verificar se Número Existe
```http
POST /chat/checkNumber/{instance}
```

**Request Body:**
```json
{
  "number": "5511999999999"
}
```

**Response (200):**
```json
{
  "exists": true,
  "jid": "5511999999999@s.whatsapp.net"
}
```

### 5. Grupos

#### Obter Informações do Grupo
```http
GET /group/findGroupInfos/{instance}?groupJid={groupJid}
```

**Query Parameters:**
- `groupJid`: ID do grupo (ex: 120363295648424210@g.us)

**Response (200):**
```json
{
  "id": "120363295648424210@g.us",
  "subject": "Nome do Grupo",
  "owner": "5511999999999@s.whatsapp.net",
  "description": "Descrição do grupo",
  "participants": [
    {
      "id": "5511999999999@s.whatsapp.net",
      "admin": "superadmin" | "admin" | null
    }
  ],
  "creation": 1678900000,
  "size": 256
}
```

#### Enviar Mensagem para Grupo
```http
POST /message/sendText/{instance}
```

**Request Body:**
```json
{
  "number": "120363295648424210@g.us",
  "text": "Mensagem para o grupo",
  "mentionsEveryOne": true,
  "mentioned": ["5511999999999@s.whatsapp.net"]
}
```

### 6. Webhooks

#### Configurar Webhook
```http
POST /webhook/set/{instance}
```

**Request Body:**
```json
{
  "enabled": true,
  "url": "https://seu-servidor.com/webhook",
  "webhookByEvents": true,
  "webhookBase64": true,
  "events": [
    "APPLICATION_STARTUP",
    "QRCODE_UPDATED",
    "CONNECTION_UPDATE",
    "MESSAGES_SET",
    "MESSAGES_UPSERT",
    "MESSAGES_UPDATE",
    "MESSAGES_DELETE",
    "SEND_MESSAGE",
    "CONTACTS_SET",
    "CONTACTS_UPSERT",
    "CONTACTS_UPDATE",
    "PRESENCE_UPDATE",
    "CHATS_SET",
    "CHATS_UPSERT",
    "CHATS_UPDATE",
    "CHATS_DELETE",
    "GROUPS_UPSERT",
    "GROUPS_UPDATE",
    "GROUP_PARTICIPANTS_UPDATE",
    "NEW_JWT_TOKEN"
  ]
}
```

**Response (201):**
```json
{
  "enabled": true,
  "url": "https://seu-servidor.com/webhook",
  "events": [...],
  "webhook_by_events": true
}
```

#### Obter Configuração do Webhook
```http
GET /webhook/find/{instance}
```

**Response (200):**
```json
{
  "enabled": true,
  "url": "https://seu-servidor.com/webhook",
  "events": [...]
}
```

## Eventos de Webhook

### Estrutura Base do Evento
```json
{
  "event": "MESSAGES_UPSERT",
  "instance": "nome-da-instancia",
  "data": {
    // Dados específicos do evento
  },
  "apikey": "sua-api-key",
  "date_time": "2024-01-01T12:00:00.000Z",
  "sender": "Evolution API",
  "server_url": "https://seu-servidor.com"
}
```

### Principais Eventos

#### MESSAGES_UPSERT
Recebimento de nova mensagem:
```json
{
  "event": "MESSAGES_UPSERT",
  "data": {
    "key": {
      "remoteJid": "5511999999999@s.whatsapp.net",
      "fromMe": false,
      "id": "message-id"
    },
    "message": {
      "conversation": "Texto da mensagem",
      "messageContextInfo": {...}
    },
    "messageTimestamp": "1678900000",
    "pushName": "Nome do Contato"
  }
}
```

#### CONNECTION_UPDATE
Mudança no status da conexão:
```json
{
  "event": "CONNECTION_UPDATE",
  "data": {
    "state": "open" | "connecting" | "close"
  }
}
```

#### QRCODE_UPDATED
Novo QR Code gerado:
```json
{
  "event": "QRCODE_UPDATED",
  "data": {
    "qrcode": {
      "code": "2@xxxx...",
      "base64": "data:image/png;base64,..."
    }
  }
}
```

## Recursos Disponíveis

### Mensagens
- ✅ Envio de texto com formatação (negrito, itálico, tachado, código)
- ✅ Emojis
- ✅ Envio de mídia (imagem, vídeo, documento, áudio)
- ✅ Notas de voz
- ✅ Localização
- ✅ Contatos
- ✅ Stickers
- ✅ Reações
- ✅ Link preview
- ✅ Responder mensagens
- ✅ Mencionar contatos
- ✅ Enquetes (polls)
- ✅ Status/Stories
- ❌ Botões (descontinuado)

### Perfil
- ✅ Atualizar nome
- ✅ Atualizar foto
- ✅ Atualizar status

### Grupos
- ✅ Criar grupos
- ✅ Atualizar foto do grupo
- ✅ Atualizar nome do grupo
- ✅ Atualizar descrição
- ✅ Listar grupos
- ✅ Gerenciar participantes

## Códigos de Status

### Respostas de Sucesso
- `200 OK`: Requisição bem-sucedida
- `201 Created`: Recurso criado com sucesso

### Erros Comuns
- `400 Bad Request`: Parâmetros inválidos
- `401 Unauthorized`: API key inválida
- `404 Not Found`: Instância ou recurso não encontrado
- `409 Conflict`: Conflito (ex: instância já existe)
- `429 Too Many Requests`: Limite de requisições excedido
- `500 Internal Server Error`: Erro no servidor

## Boas Práticas

### Formatação de Números
- Sempre incluir código do país (55 para Brasil)
- Formato: `5511999999999` (sem +, espaços ou caracteres especiais)
- Para grupos, usar formato: `120363295648424210@g.us`

### Delays e Rate Limiting
- Implementar delay entre mensagens (mínimo 1200ms)
- Respeitar limites da API
- Implementar retry com backoff exponencial

### Segurança
- Nunca expor API key no frontend
- Validar todos os webhooks recebidos
- Implementar autenticação adicional nos webhooks

### Performance
- Usar webhook_by_events para reduzir tráfego
- Implementar cache para dados de perfil
- Processar webhooks de forma assíncrona

## Integrações Suportadas

- **Typebot**: Construção de bots conversacionais
- **Chatwoot**: Atendimento ao cliente
- **Dify**: Integração com IA e múltiplos agentes
- **OpenAI**: Capacidades de IA e conversão áudio-texto
- **RabbitMQ/Amazon SQS**: Filas de mensagens
- **WebSocket**: Eventos em tempo real
- **Amazon S3/Minio**: Armazenamento de mídia

## Requisitos do Sistema

### Redis (Opcional mas Recomendado)
- Usado para cache e gerenciamento de sessões
- Melhora significativamente a performance
- Permite múltiplas instâncias do servidor

### Ambiente
- Node.js 18+
- MongoDB ou PostgreSQL
- SSL/TLS para webhooks
- Mínimo 2GB RAM
- 2 vCPUs recomendado

## Exemplos de Implementação

### Cliente Python
```python
import httpx
import asyncio

class EvolutionAPI:
    def __init__(self, base_url, instance, api_key):
        self.base_url = base_url
        self.instance = instance
        self.headers = {
            "apikey": api_key,
            "Content-Type": "application/json"
        }
    
    async def send_text(self, phone, message):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/message/sendText/{self.instance}",
                headers=self.headers,
                json={
                    "number": phone,
                    "text": message
                }
            )
            return response.json()
```

### Webhook Handler
```python
from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/webhook")
async def webhook_handler(request: Request):
    data = await request.json()
    
    event_type = data.get("event")
    
    if event_type == "MESSAGES_UPSERT":
        message_data = data.get("data", {})
        # Processar nova mensagem
        
    elif event_type == "CONNECTION_UPDATE":
        state = data.get("data", {}).get("state")
        # Processar mudança de conexão
    
    return {"status": "ok"}
```

## Troubleshooting

### Problemas Comuns

1. **QR Code não aparece**
   - Verificar se a instância foi criada corretamente
   - Verificar logs do servidor

2. **Mensagens não são enviadas**
   - Verificar status da conexão
   - Verificar formato do número
   - Verificar se o número existe no WhatsApp

3. **Webhooks não são recebidos**
   - Verificar URL do webhook
   - Verificar SSL/TLS
   - Verificar firewall

4. **Mídia não é enviada**
   - Verificar tamanho do arquivo (máx 16MB)
   - Verificar formato base64
   - Verificar mimetype

## Links Úteis

- Documentação Oficial: https://doc.evolution-api.com/v2/pt/
- GitHub: https://github.com/EvolutionAPI/evolution-api
- Comunidade: https://evolution-api.com
- Swagger/OpenAPI: https://seu-servidor.com/docs

## Changelog

### v2.0.0
- Nova arquitetura baseada em TypeScript
- Suporte para WhatsApp Business API oficial
- Melhorias de performance
- Novo sistema de webhooks

### Recursos Futuros
- Suporte para Instagram
- Suporte para Messenger
- Integração com mais plataformas de IA