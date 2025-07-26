# 🚀 Guia de Deploy para Produção - SDR IA SolarPrime

## 📋 Visão Geral

Este guia detalha como fazer o deploy do webhook do agente SDR em produção, resolvendo o problema de "localhost não acessível" pela Evolution API.

## 🎯 Arquitetura de Produção Recomendada

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   WhatsApp      │────▶│  Evolution API   │────▶│  Webhook Server │
│   (Cliente)     │     │  (Easypanel)     │     │  (Railway/VPS)  │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                           │
                                                           ▼
                                                   ┌───────────────┐
                                                   │   Supabase    │
                                                   │  (Database)   │
                                                   └───────────────┘
```

## 🔧 Opções de Deploy

### Opção 1: Railway (Recomendado para FastAPI)

#### Vantagens:
- Deploy automático via GitHub
- SSL/HTTPS gratuito
- Fácil configuração de variáveis de ambiente
- Suporte nativo para FastAPI
- Preço baseado em uso

#### Passo a Passo:

1. **Prepare o projeto para Railway:**

```bash
# Crie um arquivo railway.json na raiz
echo '{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn api.main:app --host 0.0.0.0 --port $PORT"
  }
}' > railway.json

# Crie um runtime.txt
echo "python-3.11" > runtime.txt
```

2. **Crie um Procfile:**
```bash
echo "web: uvicorn api.main:app --host 0.0.0.0 --port $PORT" > Procfile
```

3. **Deploy no Railway:**
   - Acesse [railway.app](https://railway.app)
   - Crie um novo projeto
   - Conecte seu GitHub
   - Selecione o repositório
   - Configure as variáveis de ambiente
   - Railway criará automaticamente uma URL pública

4. **Configure o webhook na Evolution API:**
```python
webhook_url = "https://seu-app.railway.app/webhook/whatsapp"
```

### Opção 2: Render.com (Alternativa Gratuita)

#### Vantagens:
- Tier gratuito disponível
- Deploy automático do GitHub
- SSL incluído
- Boa performance

#### Configuração:

1. **Crie render.yaml:**
```yaml
services:
  - type: web
    name: sdr-ia-solarprime
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "uvicorn api.main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: PYTHON_VERSION
        value: 3.11
```

2. **Deploy:**
   - Faça push para GitHub
   - Conecte no Render.com
   - Configure variáveis de ambiente
   - URL será: `https://sdr-ia-solarprime.onrender.com`

### Opção 3: VPS com Nginx (Produção Robusta)

#### Vantagens:
- Controle total
- Melhor performance
- Custo fixo mensal

#### Setup Completo:

1. **Configure o servidor Ubuntu:**
```bash
# Atualize o sistema
sudo apt update && sudo apt upgrade -y

# Instale dependências
sudo apt install python3.11 python3.11-venv python3-pip nginx certbot python3-certbot-nginx -y

# Clone o projeto
git clone https://github.com/seu-usuario/sdr-ia-solarprime.git
cd sdr-ia-solarprime

# Crie ambiente virtual
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **Configure systemd service:**
```bash
sudo nano /etc/systemd/system/sdr-ia.service
```

```ini
[Unit]
Description=SDR IA SolarPrime API
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/sdr-ia-solarprime
Environment="PATH=/home/ubuntu/sdr-ia-solarprime/venv/bin"
ExecStart=/home/ubuntu/sdr-ia-solarprime/venv/bin/uvicorn api.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

3. **Configure Nginx:**
```nginx
server {
    listen 80;
    server_name api.seudominio.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

4. **Configure SSL:**
```bash
sudo certbot --nginx -d api.seudominio.com
```

5. **Inicie o serviço:**
```bash
sudo systemctl enable sdr-ia
sudo systemctl start sdr-ia
```

### Opção 4: Docker + Cloud Run (Escalável)

1. **Crie Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

2. **Deploy no Google Cloud Run:**
```bash
# Build e push da imagem
gcloud builds submit --tag gcr.io/SEU-PROJETO/sdr-ia

# Deploy
gcloud run deploy sdr-ia \
  --image gcr.io/SEU-PROJETO/sdr-ia \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## 🔐 Segurança em Produção

### 1. **Validação de Webhook:**
```python
# Em api/routes/webhooks.py
from fastapi import Header, HTTPException
import hmac
import hashlib

async def validate_webhook(
    signature: str = Header(None, alias="X-Evolution-Signature")
):
    """Valida assinatura do webhook"""
    if not signature:
        raise HTTPException(status_code=401, detail="Missing signature")
    
    # Implemente validação HMAC aqui
    expected_signature = hmac.new(
        WEBHOOK_SECRET.encode(),
        request_body,
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(signature, expected_signature):
        raise HTTPException(status_code=401, detail="Invalid signature")
```

### 2. **Rate Limiting Aprimorado:**
```python
# Já implementado em middleware/rate_limiter.py
# Configure limites específicos para produção:
RATE_LIMIT_WEBHOOK=100  # Requisições por minuto
RATE_LIMIT_BURST=20     # Burst permitido
```

### 3. **Monitoramento:**
```python
# Adicione logging estruturado
import structlog

logger = structlog.get_logger()

@app.post("/webhook/whatsapp")
async def webhook(request: Request):
    logger.info("webhook_received", 
                instance=instance_name,
                event_type=event_type,
                timestamp=datetime.utcnow())
```

## 📊 Monitoramento e Observabilidade

### 1. **Health Check Endpoint:**
```python
@app.get("/health/detailed")
async def health_detailed():
    return {
        "status": "healthy",
        "version": APP_VERSION,
        "database": await check_database_health(),
        "evolution_api": await check_evolution_health(),
        "gemini_api": await check_gemini_health(),
        "uptime": get_uptime(),
        "memory_usage": get_memory_usage()
    }
```

### 2. **Métricas com Prometheus:**
```python
from prometheus_client import Counter, Histogram, generate_latest

webhook_counter = Counter('webhook_requests_total', 'Total webhook requests')
response_time = Histogram('webhook_response_time', 'Response time in seconds')

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

## 🚀 Script de Deploy Automático

```bash
#!/bin/bash
# deploy.sh

echo "🚀 Iniciando deploy do SDR IA SolarPrime..."

# Variáveis
DEPLOY_ENV=${1:-production}
WEBHOOK_URL=""

# Escolha plataforma
echo "Escolha a plataforma de deploy:"
echo "1. Railway"
echo "2. Render"
echo "3. VPS com Nginx"
echo "4. Google Cloud Run"
read -p "Opção: " platform

case $platform in
    1)
        echo "📦 Preparando para Railway..."
        railway up
        WEBHOOK_URL=$(railway domain)
        ;;
    2)
        echo "📦 Preparando para Render..."
        git push render main
        WEBHOOK_URL="https://sdr-ia.onrender.com"
        ;;
    3)
        echo "📦 Deploy em VPS..."
        read -p "Digite o IP do servidor: " server_ip
        ssh ubuntu@$server_ip "cd sdr-ia-solarprime && git pull && systemctl restart sdr-ia"
        WEBHOOK_URL="https://api.seudominio.com"
        ;;
    4)
        echo "📦 Deploy no Cloud Run..."
        gcloud run deploy sdr-ia --source .
        WEBHOOK_URL=$(gcloud run services describe sdr-ia --format='value(status.url)')
        ;;
esac

echo "✅ Deploy concluído!"
echo "🔗 Webhook URL: $WEBHOOK_URL/webhook/whatsapp"
echo ""
echo "📝 Próximos passos:"
echo "1. Configure o webhook na Evolution API"
echo "2. Teste enviando uma mensagem"
echo "3. Monitor logs em tempo real"
```

## ✅ Checklist de Produção

- [ ] Variáveis de ambiente configuradas
- [ ] SSL/HTTPS habilitado
- [ ] Rate limiting configurado
- [ ] Logs estruturados
- [ ] Health checks implementados
- [ ] Backup de dados configurado
- [ ] Monitoramento ativo
- [ ] Webhook validation
- [ ] Error handling robusto
- [ ] Auto-scaling configurado (se aplicável)

## 🆘 Troubleshooting

### Webhook não recebe mensagens:
1. Verifique se a URL é acessível publicamente
2. Confirme que Evolution API está configurada corretamente
3. Teste com `curl` diretamente
4. Verifique logs de ambos os lados

### Performance issues:
1. Implemente cache Redis
2. Use connection pooling
3. Otimize queries do banco
4. Configure auto-scaling

### Segurança:
1. Sempre valide webhooks
2. Use HTTPS
3. Implemente rate limiting
4. Monitore tentativas suspeitas

## 🎯 Conclusão

Com este guia, você pode fazer deploy do SDR IA SolarPrime em produção de forma segura e escalável. Escolha a opção que melhor se adequa às suas necessidades e orçamento.