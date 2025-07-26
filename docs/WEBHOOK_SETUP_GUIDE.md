# Guia Completo de Configuração do Webhook - Evolution API

## 📋 Índice
1. [Visão Geral](#visão-geral)
2. [Pré-requisitos](#pré-requisitos)
3. [Configuração Rápida](#configuração-rápida)
4. [Configuração Detalhada](#configuração-detalhada)
5. [Segurança](#segurança)
6. [Troubleshooting](#troubleshooting)
7. [Melhores Práticas](#melhores-práticas)

## 🎯 Visão Geral

O webhook é o canal de comunicação entre a Evolution API e sua aplicação SDR. Sempre que algo acontece no WhatsApp (nova mensagem, mudança de status, etc.), a Evolution API envia uma notificação HTTP para seu webhook.

### Fluxo de Dados
```
WhatsApp → Evolution API → Webhook (sua aplicação) → Processamento → Resposta
```

## ⚡ Configuração Rápida

### 1. Use o Script Automatizado

```bash
cd /path/to/sdr-solarprime
python scripts/configure-webhook.py
```

O script irá:
- ✅ Verificar conexão com Evolution API
- ✅ Mostrar configuração atual
- ✅ Solicitar URL do webhook
- ✅ Permitir seleção de eventos
- ✅ Configurar e testar o webhook

### 2. Configuração Manual via API

```python
import asyncio
from services.evolution_api import EvolutionAPIClient

async def setup_webhook():
    async with EvolutionAPIClient() as client:
        result = await client.create_webhook(
            webhook_url="https://api.seudominio.com.br/webhook/whatsapp",
            events=[
                "MESSAGES_UPSERT",
                "MESSAGES_UPDATE", 
                "CONNECTION_UPDATE",
                "QRCODE_UPDATED"
            ]
        )
        print("Webhook configurado:", result)

asyncio.run(setup_webhook())
```

## 🔧 Configuração Detalhada

### Estrutura do Webhook

```json
{
  "webhook": {
    "enabled": true,
    "url": "https://api.seudominio.com.br/webhook/whatsapp",
    "webhookByEvents": false,
    "webhookBase64": false,
    "events": [
      "MESSAGES_UPSERT",
      "MESSAGES_UPDATE",
      "CONNECTION_UPDATE",
      "QRCODE_UPDATED",
      "PRESENCE_UPDATE",
      "SEND_MESSAGE"
    ]
  }
}
```

### Eventos Disponíveis

#### 📱 Eventos Essenciais (Recomendados)
- **MESSAGES_UPSERT** - Nova mensagem recebida
- **MESSAGES_UPDATE** - Status de mensagem atualizado (enviada, entregue, lida)
- **CONNECTION_UPDATE** - Mudança no status da conexão
- **QRCODE_UPDATED** - QR Code atualizado (para reconexão)
- **SEND_MESSAGE** - Confirmação de mensagem enviada

#### 📊 Eventos Complementares
- **PRESENCE_UPDATE** - Cliente online/offline/digitando
- **CONTACTS_UPSERT** - Novo contato ou atualização
- **CHATS_UPSERT** - Novo chat iniciado
- **GROUPS_UPSERT** - Adicionado a grupo
- **CALL** - Chamada recebida

#### 🔧 Eventos Avançados
- **APPLICATION_STARTUP** - Aplicação iniciada
- **MESSAGES_SET** - Sincronização inicial de mensagens
- **MESSAGES_DELETE** - Mensagem deletada
- **LABELS_EDIT** - Etiquetas modificadas
- **TYPEBOT_START** - Integração com Typebot

### URLs por Ambiente

#### Desenvolvimento
```bash
# Com ngrok
ngrok http 8000
# URL gerada: https://abc123.ngrok-free.app/webhook/whatsapp

# Local (apenas para testes)
http://localhost:8000/webhook/whatsapp
```

#### Produção
```bash
# HTTPS obrigatório
https://api.seudominio.com.br/webhook/whatsapp
```

## 🔒 Segurança

### 1. Validação de IP

Configure no `.env`:
```env
# IPs permitidos (separe por vírgula)
ALLOWED_WEBHOOK_IPS=ip-evolution-api,outro-ip

# Ou deixe vazio para permitir todos
ALLOWED_WEBHOOK_IPS=
```

### 2. Assinatura HMAC

Configure no `.env`:
```env
# Ative validação de assinatura
WEBHOOK_VALIDATE_SIGNATURE=true

# Configure um secret forte
WEBHOOK_SECRET=sua-chave-secreta-super-segura-aqui
```

### 3. Headers de Segurança

O webhook valida automaticamente:
- `X-Hub-Signature-256` - Assinatura HMAC SHA256
- `X-Webhook-Signature` - Assinatura alternativa
- `Content-Type` - Deve ser `application/json`

### 4. Rate Limiting

Configure no nginx:
```nginx
# /etc/nginx/sites-available/sdr-solarprime
limit_req_zone $binary_remote_addr zone=webhook_limit:10m rate=30r/s;

location /webhook/ {
    limit_req zone=webhook_limit burst=50 nodelay;
    # ... resto da configuração
}
```

## 🔍 Troubleshooting

### Webhook Não Está Recebendo Mensagens

1. **Verifique a URL**
   ```bash
   curl -X POST https://sua-url/webhook/test
   ```

2. **Verifique os logs da Evolution API**
   ```bash
   docker logs evolution-api
   ```

3. **Verifique o status do webhook**
   ```bash
   curl http://localhost:8000/webhook/status
   ```

### Erro 403 Forbidden

- Verifique `ALLOWED_WEBHOOK_IPS` no `.env`
- Confirme o IP da Evolution API

### Erro 401 Unauthorized

- Verifique `WEBHOOK_SECRET` no `.env`
- Confirme que Evolution API está enviando assinatura

### Timeout nos Webhooks

- Aumente timeout no nginx:
  ```nginx
  proxy_read_timeout 300s;
  ```
- Processe mensagens em background (já implementado)

### Mensagens Duplicadas

- Evolution API pode reenviar se não receber 200 OK
- Sempre retorne 200 OK rapidamente
- Implemente idempotência baseada em `message.key.id`

## 📚 Melhores Práticas

### 1. Responda Rapidamente
```python
# ✅ Bom - processa em background
@router.post("/webhook/whatsapp")
async def webhook(background_tasks: BackgroundTasks):
    background_tasks.add_task(process_message, payload)
    return {"status": "ok"}  # Responde imediatamente

# ❌ Ruim - processa sincrono
@router.post("/webhook/whatsapp")
async def webhook():
    await process_message(payload)  # Demora muito
    return {"status": "ok"}
```

### 2. Sempre Retorne 200 OK
```python
try:
    # Processar webhook
    pass
except Exception as e:
    logger.error(f"Erro: {e}")
    # Ainda retorna 200 para evitar reenvios
    return {"status": "error"}, 200
```

### 3. Log Estruturado
```python
logger.info("Webhook recebido", extra={
    "event": event_type,
    "instance": instance,
    "message_id": message_id,
    "from": sender
})
```

### 4. Monitore a Saúde
```python
# Endpoint de monitoramento
@router.get("/webhook/health")
async def webhook_health():
    return {
        "status": "healthy",
        "last_webhook": last_webhook_time,
        "webhooks_today": webhook_count,
        "error_rate": error_percentage
    }
```

### 5. Configure Alertas
```python
# Alerta se não receber webhooks
if time_since_last_webhook > 300:  # 5 minutos
    send_alert("Nenhum webhook recebido há 5 minutos")
```

## 🚀 Exemplo Completo de Implementação

```python
# api/routes/webhooks.py
from fastapi import APIRouter, BackgroundTasks, Request
from datetime import datetime
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Métricas
webhook_metrics = {
    "total": 0,
    "errors": 0,
    "last_received": None
}

@router.post("/webhook/whatsapp")
async def whatsapp_webhook(
    request: Request,
    background_tasks: BackgroundTasks
):
    """Recebe webhooks da Evolution API"""
    
    # Atualizar métricas
    webhook_metrics["total"] += 1
    webhook_metrics["last_received"] = datetime.now()
    
    try:
        # Parse payload
        payload = await request.json()
        event_type = payload.get("event", "UNKNOWN")
        
        # Log estruturado
        logger.info("Webhook recebido", extra={
            "event": event_type,
            "instance": payload.get("instance"),
            "timestamp": datetime.now().isoformat()
        })
        
        # Processar em background
        if event_type == "MESSAGES_UPSERT":
            background_tasks.add_task(
                process_new_message,
                payload.get("data", {})
            )
        elif event_type == "CONNECTION_UPDATE":
            background_tasks.add_task(
                handle_connection_update,
                payload.get("data", {})
            )
        
        # Responder rapidamente
        return {
            "status": "ok",
            "event": event_type,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        webhook_metrics["errors"] += 1
        logger.error(f"Erro no webhook: {e}", exc_info=True)
        
        # Ainda retorna 200
        return {
            "status": "error",
            "message": "Internal error"
        }

async def process_new_message(data: dict):
    """Processa nova mensagem em background"""
    try:
        # Extrair informações
        message = data.get("message", {})
        key = data.get("key", {})
        
        # Processar com AI
        from services.ai_agent import ai_agent
        await ai_agent.process_message(
            phone=key.get("remoteJid"),
            message=message.get("conversation"),
            message_id=key.get("id")
        )
    except Exception as e:
        logger.error(f"Erro ao processar mensagem: {e}")
```

## 📊 Monitoramento com Grafana

Crie um dashboard para monitorar:
- Taxa de webhooks por minuto
- Tempo de resposta
- Taxa de erro
- Eventos por tipo
- Status da conexão

Query Prometheus exemplo:
```promql
# Taxa de webhooks
rate(webhook_total[5m])

# Taxa de erro
rate(webhook_errors[5m]) / rate(webhook_total[5m])

# Latência
histogram_quantile(0.95, webhook_duration_seconds)
```

## 🔄 Atualização e Manutenção

### Atualizar Configuração
```bash
# Via script
python scripts/configure-webhook.py

# Via API
curl -X POST https://evolution-api/webhook/set/instance \
  -H "apikey: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "webhook": {
      "enabled": true,
      "url": "https://nova-url.com/webhook/whatsapp"
    }
  }'
```

### Verificar Configuração Atual
```bash
curl https://evolution-api/webhook/find/instance \
  -H "apikey: YOUR_KEY"
```

### Desabilitar Temporariamente
```bash
curl -X POST https://evolution-api/webhook/set/instance \
  -H "apikey: YOUR_KEY" \
  -d '{"webhook": {"enabled": false}}'
```

## 📝 Checklist de Produção

- [ ] URL HTTPS com certificado válido
- [ ] Webhook configurado com eventos essenciais
- [ ] Validação de segurança ativada
- [ ] Rate limiting configurado
- [ ] Logs estruturados implementados
- [ ] Monitoramento ativo
- [ ] Alertas configurados
- [ ] Backup da configuração
- [ ] Documentação atualizada
- [ ] Testes de carga realizados