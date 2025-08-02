# Guia de Configuração de Webhook para Produção - Evolution API

## Visão Geral

Este guia detalha como configurar adequadamente o webhook da Evolution API para produção, incluindo requisitos de segurança, SSL/TLS e URLs públicas.

## Requisitos para Webhook em Produção

### 1. URL Pública com HTTPS

**Obrigatório para produção:**
- URL deve ser HTTPS (não HTTP)
- Certificado SSL/TLS válido
- Porta suportada: 443, 80, 88 ou 8443
- Domínio público acessível

### 2. Opções de Exposição Pública

#### Opção 1: Ngrok (Desenvolvimento/Testes)
```bash
# Instalar ngrok
brew install ngrok  # macOS
# ou baixar de https://ngrok.com/download

# Autenticar (criar conta gratuita em ngrok.com)
ngrok authtoken YOUR_AUTH_TOKEN

# Expor aplicação local
ngrok http 8000

# Resultado exemplo:
# https://abc123.ngrok-free.app -> http://localhost:8000
```

**Prós:**
- Rápido para desenvolvimento
- SSL automático
- URL temporária gratuita

**Contras:**
- URL muda a cada reinício (plano gratuito)
- Não recomendado para produção real
- Limitações de requisições

#### Opção 2: Deploy em Cloud (Produção)

**Hostinger VPS com Nginx:**
```nginx
# /etc/nginx/sites-available/sdr-solarprime
server {
    listen 80;
    server_name api.seudominio.com.br;
    
    # Redirecionar para HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.seudominio.com.br;
    
    # Certificados SSL (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/api.seudominio.com.br/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.seudominio.com.br/privkey.pem;
    
    # Configurações SSL
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # Proxy para aplicação
    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
    
    # Endpoint específico para webhook
    location /webhook/whatsapp {
        proxy_pass http://localhost:8000/webhook/whatsapp;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeout maior para webhooks
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
}
```

**Obter certificado SSL gratuito:**
```bash
# Instalar Certbot
sudo apt update
sudo apt install certbot python3-certbot-nginx

# Obter certificado
sudo certbot --nginx -d api.seudominio.com.br

# Renovação automática
sudo certbot renew --dry-run
```

### 3. Configuração da Evolution API

Na interface do Evolution Manager (como mostrado na imagem):

1. **Ativar Webhook:**
   - Toggle "Enabled" = ON

2. **URL do Webhook:**
   ```
   https://api.seudominio.com.br/webhook/whatsapp
   ```

3. **Configurações Recomendadas:**
   - **Webhook by Events**: OFF (mais simples)
   - **Webhook Base64**: OFF (mais fácil de debugar)

4. **Eventos Essenciais:**
   - MESSAGES_UPSERT (novas mensagens)
   - MESSAGES_UPDATE (status de mensagens)
   - CONNECTION_UPDATE (status da conexão)
   - QRCODE_UPDATED (QR code atualizado)
   - PRESENCE_UPDATE (presença online/offline)

### 4. Atualização do .env para Produção

```env
# ============================================
# WEBHOOK CONFIGURATION - PRODUÇÃO
# ============================================
# Para desenvolvimento local com ngrok
# WEBHOOK_BASE_URL=https://abc123.ngrok-free.app

# Para produção
WEBHOOK_BASE_URL=https://api.seudominio.com.br

# Segurança adicional
WEBHOOK_SECRET=sua-chave-secreta-aqui
ALLOWED_WEBHOOK_IPS=ip-da-evolution-api
```

### 5. Validação de Segurança do Webhook

Adicione validação no endpoint:

```python
# api/routes/webhooks.py
from fastapi import Header, HTTPException
import hmac
import hashlib

async def validate_webhook_signature(
    signature: str = Header(None, alias="X-Webhook-Signature"),
    body: bytes = Body(...)
):
    """Valida assinatura do webhook"""
    if not signature:
        raise HTTPException(status_code=401, detail="Missing signature")
    
    secret = os.getenv("WEBHOOK_SECRET")
    expected_signature = hmac.new(
        secret.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(signature, expected_signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

@router.post("/webhook/whatsapp", dependencies=[Depends(validate_webhook_signature)])
async def whatsapp_webhook(request: Request):
    # Processar webhook
    pass
```

## Análise: Necessidade do Redis no Stack

### Cenário Atual
- **Evolution API**: Gerencia sessões WhatsApp
- **Supabase**: Banco de dados principal
- **Redis no Easypanel**: Cache disponível

### Análise de Necessidade

#### Quando Redis É Necessário:

1. **Alto Volume de Mensagens** (>1000/hora)
   - Cache de conversas ativas
   - Reduzir queries ao Supabase

2. **Múltiplas Instâncias da Aplicação**
   - Compartilhar estado entre servidores
   - Session management distribuído

3. **Rate Limiting Avançado**
   - Controle de taxa por usuário
   - Proteção contra spam

4. **Filas de Processamento**
   - Processar mensagens assíncronas
   - Retry de mensagens falhas

#### Quando Redis NÃO É Necessário:

1. **Volume Moderado** (<1000 mensagens/hora)
   - Supabase aguenta bem
   - Evolution API já mantém estado

2. **Aplicação Single Instance**
   - Estado em memória suficiente
   - Sem necessidade de distribuição

3. **Simplicidade Prioritária**
   - Menos componentes = menos falhas
   - Manutenção mais simples

### Recomendação para Seu Caso

**Começar SEM Redis:**
1. Evolution API já mantém estado das conversas
2. Supabase é suficiente para persistência
3. Menos complexidade inicial

**Migrar PARA Redis quando:**
- Volume crescer significativamente
- Precisar de múltiplas instâncias
- Performance se tornar gargalo

### Arquitetura Recomendada Inicial

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   WhatsApp      │────▶│  Evolution API   │────▶│   SDR Agent     │
│                 │     │   (Hostinger)    │     │   (FastAPI)     │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                           │
                                                           │
                                                   ┌───────▼────────┐
                                                   │   Supabase     │
                                                   │   (Database)   │
                                                   └────────────────┘
```

### Código de Fallback (Já Implementado)

O código já tem um fallback inteligente:
```python
# services/redis_fallback.py
# Usa Redis se disponível, senão usa cache em memória
```

Isso permite começar sem Redis e adicionar depois sem mudanças de código!

## Checklist de Deploy para Produção

- [ ] Domínio configurado apontando para servidor
- [ ] Certificado SSL instalado (Let's Encrypt)
- [ ] Nginx configurado como proxy reverso
- [ ] Firewall permitindo portas 80/443
- [ ] Webhook URL configurada na Evolution API
- [ ] Variáveis de ambiente atualizadas
- [ ] Logs configurados para monitoramento
- [ ] Backup automático configurado
- [ ] Monitoramento de uptime ativo

## Scripts de Deploy

### 1. Deploy Inicial
```bash
#!/bin/bash
# deploy.sh

# Atualizar código
git pull origin main

# Instalar dependências
pip install -r requirements.txt

# Aplicar migrações
alembic upgrade head

# Reiniciar serviços
sudo systemctl restart sdr-solarprime
sudo systemctl restart nginx

# Verificar status
sudo systemctl status sdr-solarprime
```

### 2. Configurar como Serviço
```ini
# /etc/systemd/system/sdr-solarprime.service
[Unit]
Description=SDR SolarPrime API
After=network.target

[Service]
Type=exec
User=ubuntu
WorkingDirectory=/home/ubuntu/sdr-solarprime
Environment="PATH=/home/ubuntu/.local/bin:/usr/bin"
ExecStart=/home/ubuntu/.local/bin/uvicorn api.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## Monitoramento

### 1. Health Check Endpoint
```python
# api/routes/health.py
@router.get("/health/full")
async def health_check_full():
    """Health check completo para monitoramento"""
    
    checks = {
        "api": "healthy",
        "timestamp": datetime.now().isoformat(),
        "evolution_api": "unknown",
        "database": "unknown",
        "webhook": "unknown"
    }
    
    # Verificar Evolution API
    try:
        async with evolution_client as client:
            status = await client.check_connection()
            checks["evolution_api"] = "healthy" if status.get("state") == "open" else "unhealthy"
    except:
        checks["evolution_api"] = "unhealthy"
    
    # Verificar Supabase
    try:
        # Fazer query simples
        checks["database"] = "healthy"
    except:
        checks["database"] = "unhealthy"
    
    # Status geral
    all_healthy = all(v == "healthy" for k, v in checks.items() if k not in ["timestamp", "webhook"])
    
    return JSONResponse(
        content=checks,
        status_code=200 if all_healthy else 503
    )
```

### 2. Configurar Uptime Monitor
- UptimeRobot: https://uptimerobot.com
- Pingdom: https://www.pingdom.com
- Ou usar o próprio monitor da Hostinger

## Conclusão

1. **Webhook em Produção**: Use HTTPS com certificado válido
2. **Redis**: Não necessário inicialmente, adicione conforme crescimento
3. **Arquitetura**: Mantenha simples, escale quando necessário
4. **Segurança**: Sempre valide webhooks e use HTTPS