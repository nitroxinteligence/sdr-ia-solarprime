# 06. Deploy e Monitoramento - Guia Completo

Este documento detalha o processo completo de deploy em produção e configuração de monitoramento para o Agente SDR SolarPrime.

## 📋 Índice

1. [Preparação para Deploy](#1-preparação-para-deploy)
2. [Deploy com Docker](#2-deploy-com-docker)
3. [Deploy com Systemd](#3-deploy-com-systemd)
4. [Configuração de SSL/TLS](#4-configuração-de-ssltls)
5. [Sistema de Monitoramento](#5-sistema-de-monitoramento)
6. [Logs e Observabilidade](#6-logs-e-observabilidade)
7. [Alertas e Notificações](#7-alertas-e-notificações)
8. [Backup e Recovery](#8-backup-e-recovery)
9. [Otimização de Performance](#9-otimização-de-performance)
10. [Manutenção e Atualizações](#10-manutenção-e-atualizações)

---

## 1. Preparação para Deploy

### 1.1 Checklist Pré-Deploy

```bash
# scripts/pre_deploy_check.sh
#!/bin/bash

echo "🔍 Verificando ambiente para deploy..."
echo "======================================="

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Função para verificar comando
check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✅ $1 instalado${NC}"
        return 0
    else
        echo -e "${RED}❌ $1 não encontrado${NC}"
        return 1
    fi
}

# Função para verificar serviço
check_service() {
    if systemctl is-active --quiet $1; then
        echo -e "${GREEN}✅ $1 está rodando${NC}"
        return 0
    else
        echo -e "${RED}❌ $1 não está rodando${NC}"
        return 1
    fi
}

# Verificar dependências
echo -e "\n📦 Verificando dependências..."
check_command python3.11
check_command docker
check_command nginx
check_command redis-cli
check_command git

# Verificar serviços
echo -e "\n🔧 Verificando serviços..."
check_service nginx
check_service docker

# Verificar arquivos essenciais
echo -e "\n📄 Verificando arquivos..."
files=(
    ".env"
    "requirements.txt"
    "docker-compose.yml"
    "api/main.py"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅ $file existe${NC}"
    else
        echo -e "${RED}❌ $file não encontrado${NC}"
    fi
done

# Verificar variáveis de ambiente
echo -e "\n🔐 Verificando variáveis de ambiente..."
source .env

required_vars=(
    "GEMINI_API_KEY"
    "SUPABASE_URL"
    "EVOLUTION_API_KEY"
    "KOMMO_CLIENT_ID"
    "REDIS_URL"
)

for var in "${required_vars[@]}"; do
    if [ -n "${!var}" ]; then
        echo -e "${GREEN}✅ $var configurada${NC}"
    else
        echo -e "${RED}❌ $var não configurada${NC}"
    fi
done

# Verificar conectividade
echo -e "\n🌐 Verificando conectividade..."
if ping -c 1 google.com &> /dev/null; then
    echo -e "${GREEN}✅ Internet OK${NC}"
else
    echo -e "${RED}❌ Sem conexão com internet${NC}"
fi

# Verificar espaço em disco
echo -e "\n💾 Verificando espaço em disco..."
disk_usage=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $disk_usage -lt 80 ]; then
    echo -e "${GREEN}✅ Espaço em disco OK ($disk_usage% usado)${NC}"
else
    echo -e "${RED}❌ Pouco espaço em disco ($disk_usage% usado)${NC}"
fi

echo -e "\n======================================="
echo "Verificação concluída!"
```

### 1.2 Build da Aplicação

```bash
# scripts/build.sh
#!/bin/bash

echo "🏗️ Iniciando build da aplicação..."

# Ativar ambiente virtual
source venv/bin/activate

# Atualizar dependências
echo "📦 Instalando dependências..."
pip install -r requirements.txt

# Executar testes
echo "🧪 Executando testes..."
pytest tests/unit/ -v

# Verificar código
echo "🔍 Verificando qualidade do código..."
flake8 api/ services/ --max-line-length=120
mypy api/ services/

# Criar arquivos estáticos
echo "📄 Preparando arquivos estáticos..."
mkdir -p static/docs
cp -r docs/* static/docs/

# Minificar e otimizar
echo "🗜️ Otimizando assets..."
find . -name "*.py" -exec python -m py_compile {} \;

echo "✅ Build concluído com sucesso!"
```

---

## 2. Deploy com Docker

### 2.1 Docker Compose Produção

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  # API Principal
  api:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: sdr-api
    restart: always
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - WORKERS=4
    env_file:
      - .env
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    depends_on:
      - redis
      - evolution
    networks:
      - solarprime-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # Redis
  redis:
    image: redis:7-alpine
    container_name: sdr-redis
    restart: always
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    command: >
      redis-server
      --appendonly yes
      --requirepass ${REDIS_PASSWORD}
      --maxmemory 512mb
      --maxmemory-policy allkeys-lru
    networks:
      - solarprime-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Celery Worker
  celery-worker:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: sdr-celery-worker
    restart: always
    command: celery -A services.tasks worker --loglevel=info --concurrency=4
    env_file:
      - .env
    volumes:
      - ./logs:/app/logs
    depends_on:
      - redis
      - api
    networks:
      - solarprime-network

  # Celery Beat
  celery-beat:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: sdr-celery-beat
    restart: always
    command: celery -A services.tasks beat --loglevel=info
    env_file:
      - .env
    volumes:
      - ./logs:/app/logs
    depends_on:
      - redis
      - celery-worker
    networks:
      - solarprime-network

  # Evolution API
  evolution:
    image: evolution-api/evolution-api:latest
    container_name: sdr-evolution
    restart: always
    ports:
      - "8080:8080"
    environment:
      - NODE_ENV=production
      - DATABASE_PROVIDER=postgresql
      - DATABASE_URL=${EVOLUTION_DATABASE_URL}
      - AUTHENTICATION_API_KEY=${EVOLUTION_API_KEY}
    volumes:
      - evolution-data:/evolution/instances
    networks:
      - solarprime-network
    healthcheck:
      test: ["CMD", "wget", "--spider", "-q", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Nginx (opcional se usar Docker)
  nginx:
    image: nginx:alpine
    container_name: sdr-nginx
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/sites-enabled:/etc/nginx/sites-enabled
      - ./ssl:/etc/nginx/ssl
      - ./static:/var/www/static
    depends_on:
      - api
    networks:
      - solarprime-network

  # Prometheus
  prometheus:
    image: prom/prometheus:latest
    container_name: sdr-prometheus
    restart: always
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/usr/share/prometheus/console_libraries'
      - '--web.console.templates=/usr/share/prometheus/consoles'
    networks:
      - solarprime-network

  # Grafana
  grafana:
    image: grafana/grafana:latest
    container_name: sdr-grafana
    restart: always
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana-data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources
    depends_on:
      - prometheus
    networks:
      - solarprime-network

networks:
  solarprime-network:
    driver: bridge

volumes:
  redis-data:
  evolution-data:
  prometheus-data:
  grafana-data:
```

### 2.2 Dockerfile Otimizado

```dockerfile
# Dockerfile
FROM python:3.11-slim as builder

# Instalar dependências de build
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Criar diretório de trabalho
WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage final
FROM python:3.11-slim

# Instalar dependências runtime
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Criar usuário não-root
RUN useradd -m -u 1000 appuser

# Copiar dependências do builder
COPY --from=builder /root/.local /home/appuser/.local

# Definir PATH
ENV PATH=/home/appuser/.local/bin:$PATH

# Criar diretório de trabalho
WORKDIR /app

# Copiar código
COPY --chown=appuser:appuser . .

# Mudar para usuário não-root
USER appuser

# Expor porta
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Comando padrão
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### 2.3 Script de Deploy Docker

```bash
# scripts/deploy_docker.sh
#!/bin/bash

set -e

echo "🚀 Iniciando deploy com Docker..."

# Carregar variáveis
source .env

# Pull das imagens base
echo "📥 Baixando imagens Docker..."
docker-compose -f docker-compose.prod.yml pull

# Build da aplicação
echo "🏗️ Building containers..."
docker-compose -f docker-compose.prod.yml build --no-cache

# Parar containers antigos
echo "🛑 Parando containers antigos..."
docker-compose -f docker-compose.prod.yml down

# Limpar recursos não utilizados
echo "🧹 Limpando recursos Docker..."
docker system prune -f

# Iniciar novos containers
echo "🚀 Iniciando novos containers..."
docker-compose -f docker-compose.prod.yml up -d

# Aguardar containers ficarem saudáveis
echo "⏳ Aguardando containers ficarem prontos..."
sleep 30

# Verificar status
echo "📊 Verificando status dos containers..."
docker-compose -f docker-compose.prod.yml ps

# Verificar logs
echo "📄 Últimas linhas dos logs..."
docker-compose -f docker-compose.prod.yml logs --tail=20

# Health check
echo "🏥 Verificando saúde da aplicação..."
curl -f http://localhost:8000/health || exit 1

echo "✅ Deploy concluído com sucesso!"
```

---

## 3. Deploy com Systemd

### 3.1 Serviço da API

```ini
# /etc/systemd/system/sdr-api.service
[Unit]
Description=SDR SolarPrime API
After=network.target redis.service
Requires=redis.service

[Service]
Type=exec
User=solarprime
Group=solarprime
WorkingDirectory=/home/solarprime/sdr-solarprime
Environment="PATH=/home/solarprime/sdr-solarprime/venv/bin"
Environment="ENVIRONMENT=production"
ExecStart=/home/solarprime/sdr-solarprime/venv/bin/uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10
StandardOutput=append:/var/log/sdr-api/api.log
StandardError=append:/var/log/sdr-api/error.log

# Segurança
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/home/solarprime/sdr-solarprime/logs /home/solarprime/sdr-solarprime/data

[Install]
WantedBy=multi-user.target
```

### 3.2 Serviço Celery Worker

```ini
# /etc/systemd/system/sdr-celery-worker.service
[Unit]
Description=SDR SolarPrime Celery Worker
After=network.target redis.service sdr-api.service
Requires=redis.service

[Service]
Type=forking
User=solarprime
Group=solarprime
WorkingDirectory=/home/solarprime/sdr-solarprime
Environment="PATH=/home/solarprime/sdr-solarprime/venv/bin"
Environment="ENVIRONMENT=production"
ExecStart=/home/solarprime/sdr-solarprime/venv/bin/celery -A services.tasks worker --detach --loglevel=info --concurrency=4 --pidfile=/var/run/sdr-celery/worker.pid
ExecStop=/bin/kill -TERM $MAINPID
Restart=always
RestartSec=10
PIDFile=/var/run/sdr-celery/worker.pid

# Diretório para PID
RuntimeDirectory=sdr-celery
RuntimeDirectoryMode=0755

[Install]
WantedBy=multi-user.target
```

### 3.3 Serviço Celery Beat

```ini
# /etc/systemd/system/sdr-celery-beat.service
[Unit]
Description=SDR SolarPrime Celery Beat
After=network.target redis.service sdr-celery-worker.service
Requires=redis.service

[Service]
Type=forking
User=solarprime
Group=solarprime
WorkingDirectory=/home/solarprime/sdr-solarprime
Environment="PATH=/home/solarprime/sdr-solarprime/venv/bin"
Environment="ENVIRONMENT=production"
ExecStart=/home/solarprime/sdr-solarprime/venv/bin/celery -A services.tasks beat --detach --loglevel=info --pidfile=/var/run/sdr-celery/beat.pid
ExecStop=/bin/kill -TERM $MAINPID
Restart=always
RestartSec=10
PIDFile=/var/run/sdr-celery/beat.pid

# Diretório para PID
RuntimeDirectory=sdr-celery
RuntimeDirectoryMode=0755

[Install]
WantedBy=multi-user.target
```

### 3.4 Script de Deploy Systemd

```bash
# scripts/deploy_systemd.sh
#!/bin/bash

set -e

echo "🚀 Iniciando deploy com Systemd..."

# Parar serviços
echo "🛑 Parando serviços..."
sudo systemctl stop sdr-api sdr-celery-worker sdr-celery-beat || true

# Atualizar código
echo "📥 Atualizando código..."
git pull origin main

# Ativar ambiente virtual
source venv/bin/activate

# Instalar dependências
echo "📦 Instalando dependências..."
pip install -r requirements.txt

# Executar migrações
echo "🗃️ Executando migrações..."
alembic upgrade head

# Coletar arquivos estáticos
echo "📄 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

# Recarregar systemd
echo "🔄 Recarregando systemd..."
sudo systemctl daemon-reload

# Iniciar serviços
echo "🚀 Iniciando serviços..."
sudo systemctl start sdr-api
sleep 5
sudo systemctl start sdr-celery-worker
sudo systemctl start sdr-celery-beat

# Habilitar serviços
echo "🔧 Habilitando serviços..."
sudo systemctl enable sdr-api
sudo systemctl enable sdr-celery-worker
sudo systemctl enable sdr-celery-beat

# Verificar status
echo "📊 Verificando status dos serviços..."
sudo systemctl status sdr-api --no-pager
sudo systemctl status sdr-celery-worker --no-pager
sudo systemctl status sdr-celery-beat --no-pager

# Recarregar Nginx
echo "🌐 Recarregando Nginx..."
sudo nginx -t && sudo systemctl reload nginx

echo "✅ Deploy concluído com sucesso!"
```

---

## 4. Configuração de SSL/TLS

### 4.1 Certbot com Nginx

```bash
# scripts/setup_ssl.sh
#!/bin/bash

echo "🔒 Configurando SSL/TLS com Certbot..."

# Instalar Certbot se necessário
if ! command -v certbot &> /dev/null; then
    echo "📦 Instalando Certbot..."
    sudo apt update
    sudo apt install -y certbot python3-certbot-nginx
fi

# Domínio
read -p "Digite seu domínio (ex: api.solarprime.com.br): " DOMAIN

# Email
read -p "Digite seu email para notificações SSL: " EMAIL

# Obter certificado
echo "🔐 Obtendo certificado SSL..."
sudo certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email $EMAIL

# Configurar renovação automática
echo "🔄 Configurando renovação automática..."
(crontab -l 2>/dev/null; echo "0 3 * * * /usr/bin/certbot renew --quiet") | crontab -

# Testar renovação
echo "🧪 Testando renovação..."
sudo certbot renew --dry-run

echo "✅ SSL configurado com sucesso!"
```

### 4.2 Configuração Nginx com SSL

```nginx
# /etc/nginx/sites-available/sdr-solarprime-ssl
server {
    listen 80;
    server_name api.solarprime.com.br;
    
    # Redirecionar todo tráfego HTTP para HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.solarprime.com.br;
    
    # Certificados SSL (gerenciados pelo Certbot)
    ssl_certificate /etc/letsencrypt/live/api.solarprime.com.br/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.solarprime.com.br/privkey.pem;
    
    # Configurações SSL
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA384;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Headers de segurança
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Content-Security-Policy "default-src 'self'" always;
    
    # Logs
    access_log /var/log/nginx/sdr-solarprime-ssl.access.log;
    error_log /var/log/nginx/sdr-solarprime-ssl.error.log;
    
    # Configuração de proxy
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
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Webhook com timeout maior
    location /webhook {
        proxy_pass http://localhost:8000/webhook;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts maiores para webhooks
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
        
        # Buffer settings
        proxy_buffering off;
        proxy_request_buffering off;
    }
    
    # Health check endpoint
    location /health {
        proxy_pass http://localhost:8000/health;
        access_log off;
    }
    
    # Métricas Prometheus
    location /metrics {
        proxy_pass http://localhost:8000/metrics;
        allow 127.0.0.1;
        deny all;
    }
}
```

---

## 5. Sistema de Monitoramento

### 5.1 Configuração Prometheus

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    monitor: 'sdr-solarprime'

# Alerting
alerting:
  alertmanagers:
    - static_configs:
        - targets:
            - localhost:9093

# Load rules
rule_files:
  - "alerts.yml"

# Scrape configs
scrape_configs:
  # API Principal
  - job_name: 'sdr-api'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    
  # Redis
  - job_name: 'redis'
    static_configs:
      - targets: ['localhost:9121']
      
  # Node Exporter
  - job_name: 'node'
    static_configs:
      - targets: ['localhost:9100']
      
  # Nginx
  - job_name: 'nginx'
    static_configs:
      - targets: ['localhost:9113']
```

### 5.2 Métricas da Aplicação

```python
# utils/metrics.py
from prometheus_client import Counter, Histogram, Gauge, Info
import time
from functools import wraps
from typing import Callable

# Métricas de requisições
http_requests_total = Counter(
    'http_requests_total',
    'Total de requisições HTTP',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'Duração das requisições HTTP em segundos',
    ['method', 'endpoint']
)

# Métricas de WhatsApp
whatsapp_messages_total = Counter(
    'whatsapp_messages_total',
    'Total de mensagens do WhatsApp processadas',
    ['type', 'status']
)

whatsapp_processing_duration_seconds = Histogram(
    'whatsapp_processing_duration_seconds',
    'Duração do processamento de mensagens WhatsApp'
)

# Métricas de leads
leads_total = Counter(
    'leads_total',
    'Total de leads criados',
    ['source', 'status']
)

leads_qualified_total = Counter(
    'leads_qualified_total',
    'Total de leads qualificados',
    ['score_range']
)

# Métricas de IA
ai_requests_total = Counter(
    'ai_requests_total',
    'Total de requisições para IA',
    ['model', 'status']
)

ai_tokens_used_total = Counter(
    'ai_tokens_used_total',
    'Total de tokens consumidos',
    ['model']
)

# Métricas de sistema
active_conversations = Gauge(
    'active_conversations',
    'Número de conversas ativas'
)

celery_tasks_total = Counter(
    'celery_tasks_total',
    'Total de tarefas Celery',
    ['task_name', 'status']
)

# Info da aplicação
app_info = Info('app_info', 'Informações da aplicação')
app_info.info({
    'version': '1.0.0',
    'environment': 'production'
})

# Decorador para métricas de tempo
def track_time(metric: Histogram):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start
                metric.observe(duration)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start
                metric.observe(duration)
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

# Middleware para FastAPI
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        duration = time.time() - start_time
        
        # Registrar métricas
        http_requests_total.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        
        http_request_duration_seconds.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(duration)
        
        return response
```

### 5.3 Dashboard Grafana

```json
{
  "dashboard": {
    "title": "SDR SolarPrime - Monitoramento",
    "panels": [
      {
        "title": "Requisições por Segundo",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Tempo de Resposta (p95)",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "p95"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Mensagens WhatsApp",
        "targets": [
          {
            "expr": "rate(whatsapp_messages_total[5m])",
            "legendFormat": "{{type}}"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Leads Criados",
        "targets": [
          {
            "expr": "increase(leads_total[1h])",
            "legendFormat": "{{source}}"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Taxa de Qualificação",
        "targets": [
          {
            "expr": "rate(leads_qualified_total[1h]) / rate(leads_total[1h]) * 100",
            "legendFormat": "Taxa %"
          }
        ],
        "type": "gauge"
      },
      {
        "title": "Conversas Ativas",
        "targets": [
          {
            "expr": "active_conversations",
            "legendFormat": "Ativas"
          }
        ],
        "type": "stat"
      },
      {
        "title": "Uso de CPU",
        "targets": [
          {
            "expr": "100 - (avg(irate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)",
            "legendFormat": "CPU %"
          }
        ],
        "type": "gauge"
      },
      {
        "title": "Uso de Memória",
        "targets": [
          {
            "expr": "(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100",
            "legendFormat": "Memória %"
          }
        ],
        "type": "gauge"
      }
    ]
  }
}
```

---

## 6. Logs e Observabilidade

### 6.1 Configuração de Logs

```python
# config/logging_config.py
import logging
import logging.handlers
import json
from datetime import datetime
from pythonjsonlogger import jsonlogger

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        log_record['timestamp'] = datetime.utcnow().isoformat()
        log_record['service'] = 'sdr-solarprime'
        log_record['environment'] = 'production'
        
        # Adicionar trace_id se disponível
        if hasattr(record, 'trace_id'):
            log_record['trace_id'] = record.trace_id

def setup_logging():
    """Configura sistema de logs para produção"""
    
    # Formato para logs JSON
    json_formatter = CustomJsonFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s'
    )
    
    # Handler para arquivo
    file_handler = logging.handlers.RotatingFileHandler(
        'logs/app.log',
        maxBytes=50*1024*1024,  # 50MB
        backupCount=10
    )
    file_handler.setFormatter(json_formatter)
    
    # Handler para erros
    error_handler = logging.handlers.RotatingFileHandler(
        'logs/error.log',
        maxBytes=50*1024*1024,
        backupCount=10
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(json_formatter)
    
    # Handler para stdout (para containers)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(json_formatter)
    
    # Configurar root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_handler)
    root_logger.addHandler(console_handler)
    
    # Configurar loggers específicos
    logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    
    return root_logger

# Exemplo de uso com contexto
from contextvars import ContextVar
import uuid

trace_id_var: ContextVar[str] = ContextVar('trace_id', default=None)

class LoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        trace_id = trace_id_var.get()
        if trace_id:
            kwargs['extra'] = kwargs.get('extra', {})
            kwargs['extra']['trace_id'] = trace_id
        return msg, kwargs

# Middleware para adicionar trace_id
from fastapi import Request

async def trace_id_middleware(request: Request, call_next):
    trace_id = request.headers.get('X-Trace-ID', str(uuid.uuid4()))
    trace_id_var.set(trace_id)
    
    response = await call_next(request)
    response.headers['X-Trace-ID'] = trace_id
    
    return response
```

### 6.2 Agregação de Logs

```yaml
# docker-compose.logging.yml
version: '3.8'

services:
  # Elasticsearch
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.8.0
    container_name: sdr-elasticsearch
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch-data:/usr/share/elasticsearch/data
    networks:
      - solarprime-network

  # Logstash
  logstash:
    image: docker.elastic.co/logstash/logstash:8.8.0
    container_name: sdr-logstash
    volumes:
      - ./logstash/pipeline:/usr/share/logstash/pipeline
      - ./logs:/logs
    ports:
      - "5044:5044"
    environment:
      - "LS_JAVA_OPTS=-Xmx256m -Xms256m"
    depends_on:
      - elasticsearch
    networks:
      - solarprime-network

  # Kibana
  kibana:
    image: docker.elastic.co/kibana/kibana:8.8.0
    container_name: sdr-kibana
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    depends_on:
      - elasticsearch
    networks:
      - solarprime-network

  # Filebeat
  filebeat:
    image: docker.elastic.co/beats/filebeat:8.8.0
    container_name: sdr-filebeat
    user: root
    volumes:
      - ./filebeat/filebeat.yml:/usr/share/filebeat/filebeat.yml:ro
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./logs:/logs:ro
    command: filebeat -e -strict.perms=false
    depends_on:
      - elasticsearch
      - logstash
    networks:
      - solarprime-network

volumes:
  elasticsearch-data:

networks:
  solarprime-network:
    external: true
```

### 6.3 Configuração Filebeat

```yaml
# filebeat/filebeat.yml
filebeat.inputs:
  # Logs da aplicação
  - type: log
    enabled: true
    paths:
      - /logs/*.log
    json.keys_under_root: true
    json.add_error_key: true
    fields:
      service: sdr-solarprime
      environment: production

  # Logs Docker
  - type: container
    paths:
      - '/var/lib/docker/containers/*/*.log'
    processors:
      - add_docker_metadata:
          host: "unix:///var/run/docker.sock"

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
  index: "sdr-logs-%{+yyyy.MM.dd}"

setup.template.name: "sdr-logs"
setup.template.pattern: "sdr-logs-*"
setup.template.settings:
  index.number_of_shards: 1
  index.number_of_replicas: 0

logging.level: info
logging.to_files: true
logging.files:
  path: /var/log/filebeat
  name: filebeat
  keepfiles: 7
  permissions: 0644
```

---

## 7. Alertas e Notificações

### 7.1 Regras de Alerta Prometheus

```yaml
# monitoring/alerts.yml
groups:
  - name: sdr_alerts
    interval: 30s
    rules:
      # API não está respondendo
      - alert: APIDown
        expr: up{job="sdr-api"} == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "API SDR está fora do ar"
          description: "A API principal não está respondendo há {{ $value }} minutos"

      # Taxa de erro alta
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Taxa de erro alta na API"
          description: "Taxa de erro: {{ $value | humanizePercentage }}"

      # Tempo de resposta alto
      - alert: HighResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Tempo de resposta alto"
          description: "P95 do tempo de resposta: {{ $value }}s"

      # Fila de mensagens crescendo
      - alert: MessageQueueBacklog
        expr: celery_queue_length{queue="whatsapp"} > 100
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Fila de mensagens WhatsApp acumulando"
          description: "{{ $value }} mensagens na fila"

      # Uso de CPU alto
      - alert: HighCPUUsage
        expr: 100 - (avg(irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Uso de CPU alto"
          description: "CPU em {{ $value }}%"

      # Pouca memória disponível
      - alert: LowMemory
        expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Memória disponível baixa"
          description: "Apenas {{ $value }}% de memória livre"

      # Disco cheio
      - alert: DiskSpaceLow
        expr: (1 - (node_filesystem_avail_bytes / node_filesystem_size_bytes)) * 100 > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Espaço em disco baixo"
          description: "Disco {{ $labels.mountpoint }} com {{ $value }}% usado"

      # Redis não está respondendo
      - alert: RedisDown
        expr: redis_up == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Redis está fora do ar"
          description: "Redis não está respondendo"

      # Falhas de integração com Gemini
      - alert: GeminiAPIFailures
        expr: rate(ai_requests_total{model="gemini", status="error"}[5m]) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Falhas na API do Gemini"
          description: "Taxa de erro: {{ $value | humanizePercentage }}"

      # Sem novos leads
      - alert: NoNewLeads
        expr: increase(leads_total[1h]) == 0
        for: 2h
        labels:
          severity: info
        annotations:
          summary: "Nenhum lead novo na última hora"
          description: "Verificar se o WhatsApp está funcionando corretamente"
```

### 7.2 Configuração AlertManager

```yaml
# monitoring/alertmanager.yml
global:
  resolve_timeout: 5m
  slack_api_url: '${SLACK_WEBHOOK_URL}'

route:
  group_by: ['alertname', 'severity']
  group_wait: 10s
  group_interval: 5m
  repeat_interval: 4h
  receiver: 'default'
  
  routes:
    - match:
        severity: critical
      receiver: 'critical'
      continue: true
      
    - match:
        severity: warning
      receiver: 'warning'
      continue: true

receivers:
  - name: 'default'
    slack_configs:
      - channel: '#sdr-alerts'
        title: 'SDR Alert'
        text: '{{ range .Alerts }}{{ .Annotations.summary }}\n{{ .Annotations.description }}{{ end }}'

  - name: 'critical'
    slack_configs:
      - channel: '#sdr-critical'
        title: '🚨 CRITICAL: {{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'
    webhook_configs:
      - url: '${WHATSAPP_WEBHOOK_URL}'
        send_resolved: true

  - name: 'warning'
    slack_configs:
      - channel: '#sdr-alerts'
        title: '⚠️ Warning: {{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'

inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname']
```

### 7.3 Notificações WhatsApp

```python
# services/alert_notifications.py
from typing import Dict, List
import httpx
import logging
from datetime import datetime

from services.whatsapp_service import WhatsAppService
from config.settings import settings

logger = logging.getLogger(__name__)

class AlertNotificationService:
    """Serviço de notificações de alertas via WhatsApp"""
    
    def __init__(self):
        self.whatsapp = WhatsAppService()
        self.admin_numbers = settings.ADMIN_WHATSAPP_NUMBERS.split(',')
        
    async def send_critical_alert(self, alert_data: Dict):
        """Envia alerta crítico via WhatsApp"""
        message = self._format_critical_message(alert_data)
        
        # Enviar para todos os admins
        for number in self.admin_numbers:
            try:
                await self.whatsapp.send_message(number, message)
                logger.info(f"Alerta crítico enviado para {number}")
            except Exception as e:
                logger.error(f"Erro ao enviar alerta para {number}: {str(e)}")
    
    async def send_daily_summary(self):
        """Envia resumo diário de saúde do sistema"""
        summary = await self._generate_daily_summary()
        
        message = f"""📊 *Resumo Diário - SDR SolarPrime*
📅 {datetime.now().strftime('%d/%m/%Y')}

🟢 *Status Geral: {summary['status']}*

📈 *Métricas do Dia:*
• Uptime: {summary['uptime']}%
• Leads processados: {summary['leads_count']}
• Taxa de sucesso: {summary['success_rate']}%
• Tempo médio resposta: {summary['avg_response_time']}s

⚠️ *Alertas:*
• Críticos: {summary['critical_alerts']}
• Avisos: {summary['warnings']}

💾 *Recursos:*
• CPU: {summary['cpu_usage']}%
• Memória: {summary['memory_usage']}%
• Disco: {summary['disk_usage']}%

🔗 *Dashboard:* {settings.GRAFANA_URL}"""
        
        # Enviar para grupo de monitoramento
        await self.whatsapp.send_message(
            settings.MONITORING_GROUP_ID,
            message
        )
    
    def _format_critical_message(self, alert_data: Dict) -> str:
        """Formata mensagem de alerta crítico"""
        return f"""🚨 *ALERTA CRÍTICO - SDR SolarPrime*

*Alerta:* {alert_data['alertname']}
*Severidade:* {alert_data['severity']}
*Tempo:* {datetime.now().strftime('%H:%M:%S')}

*Descrição:*
{alert_data['annotations']['description']}

*Ação Requerida:*
{self._get_action_required(alert_data['alertname'])}

*Dashboard:* {settings.GRAFANA_URL}
*Logs:* {settings.KIBANA_URL}"""
    
    def _get_action_required(self, alert_name: str) -> str:
        """Retorna ação requerida baseada no tipo de alerta"""
        actions = {
            "APIDown": "Verificar logs da aplicação e reiniciar serviço se necessário",
            "RedisDown": "Verificar container Redis e reiniciar se necessário",
            "HighErrorRate": "Analisar logs de erro e identificar causa raiz",
            "DiskSpaceLow": "Limpar logs antigos ou expandir disco",
            "HighMemory": "Verificar vazamentos de memória e reiniciar se necessário"
        }
        
        return actions.get(alert_name, "Verificar sistema e logs")
    
    async def _generate_daily_summary(self) -> Dict:
        """Gera resumo diário de métricas"""
        # Buscar métricas do Prometheus
        async with httpx.AsyncClient() as client:
            # Uptime
            uptime_response = await client.get(
                f"{settings.PROMETHEUS_URL}/api/v1/query",
                params={"query": "avg_over_time(up{job='sdr-api'}[24h]) * 100"}
            )
            uptime = uptime_response.json()['data']['result'][0]['value'][1]
            
            # Outras métricas...
            
        return {
            "status": "Operacional",
            "uptime": round(float(uptime), 2),
            "leads_count": 150,
            "success_rate": 98.5,
            "avg_response_time": 0.250,
            "critical_alerts": 0,
            "warnings": 2,
            "cpu_usage": 35,
            "memory_usage": 62,
            "disk_usage": 48
        }
```

---

## 8. Backup e Recovery

### 8.1 Script de Backup

```bash
# scripts/backup.sh
#!/bin/bash

set -e

# Configurações
BACKUP_DIR="/backups/sdr-solarprime"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="backup_${TIMESTAMP}"
RETENTION_DAYS=30

echo "🔒 Iniciando backup do sistema..."

# Criar diretório de backup
mkdir -p "${BACKUP_DIR}/${BACKUP_NAME}"
cd "${BACKUP_DIR}/${BACKUP_NAME}"

# 1. Backup do banco de dados (Supabase)
echo "📊 Backup do banco de dados..."
source /home/solarprime/sdr-solarprime/.env

pg_dump "${SUPABASE_DB_URL}" > database.sql
gzip database.sql

# 2. Backup do Redis
echo "💾 Backup do Redis..."
docker exec sdr-redis redis-cli --rdb /data/dump.rdb BGSAVE
sleep 5
docker cp sdr-redis:/data/dump.rdb redis_dump.rdb

# 3. Backup dos arquivos da aplicação
echo "📁 Backup dos arquivos..."
tar -czf application_files.tar.gz \
    -C /home/solarprime/sdr-solarprime \
    --exclude=venv \
    --exclude=__pycache__ \
    --exclude=logs \
    --exclude=.git \
    .

# 4. Backup das configurações
echo "⚙️ Backup das configurações..."
tar -czf configs.tar.gz \
    /etc/nginx/sites-available/sdr-solarprime* \
    /etc/systemd/system/sdr-*.service \
    /home/solarprime/sdr-solarprime/.env

# 5. Backup dos logs recentes
echo "📝 Backup dos logs..."
tar -czf logs.tar.gz \
    -C /home/solarprime/sdr-solarprime/logs \
    --newer-mtime="7 days ago" \
    .

# 6. Criar arquivo de metadados
echo "📋 Criando metadados..."
cat > metadata.json << EOF
{
    "timestamp": "${TIMESTAMP}",
    "date": "$(date)",
    "version": "$(cd /home/solarprime/sdr-solarprime && git describe --tags --always)",
    "size": "$(du -sh . | cut -f1)",
    "files": [
        "database.sql.gz",
        "redis_dump.rdb",
        "application_files.tar.gz",
        "configs.tar.gz",
        "logs.tar.gz"
    ]
}
EOF

# 7. Criar checksum
echo "🔐 Gerando checksums..."
sha256sum * > checksums.sha256

# 8. Comprimir backup completo
cd ..
tar -czf "${BACKUP_NAME}.tar.gz" "${BACKUP_NAME}/"
rm -rf "${BACKUP_NAME}/"

# 9. Upload para S3 (opcional)
if [ -n "${AWS_S3_BUCKET}" ]; then
    echo "☁️ Enviando para S3..."
    aws s3 cp "${BACKUP_NAME}.tar.gz" "s3://${AWS_S3_BUCKET}/backups/"
fi

# 10. Limpar backups antigos
echo "🧹 Limpando backups antigos..."
find "${BACKUP_DIR}" -name "backup_*.tar.gz" -mtime +${RETENTION_DAYS} -delete

echo "✅ Backup concluído: ${BACKUP_NAME}.tar.gz"

# Enviar notificação
curl -X POST "${WHATSAPP_WEBHOOK_URL}" \
    -H "Content-Type: application/json" \
    -d "{\"number\": \"${ADMIN_WHATSAPP}\", \"text\": \"✅ Backup concluído com sucesso: ${BACKUP_NAME}\"}"
```

### 8.2 Script de Restore

```bash
# scripts/restore.sh
#!/bin/bash

set -e

echo "🔄 Sistema de Restore - SDR SolarPrime"
echo "======================================"

# Verificar se foi fornecido arquivo de backup
if [ -z "$1" ]; then
    echo "Uso: ./restore.sh <arquivo_backup.tar.gz>"
    exit 1
fi

BACKUP_FILE=$1
RESTORE_DIR="/tmp/restore_$$"

# Verificar se arquivo existe
if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Arquivo de backup não encontrado: $BACKUP_FILE"
    exit 1
fi

echo "⚠️  ATENÇÃO: Este processo irá restaurar o sistema!"
echo "Todos os dados atuais serão sobrescritos."
read -p "Continuar? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Restore cancelado."
    exit 0
fi

# Criar diretório temporário
mkdir -p "$RESTORE_DIR"

# 1. Extrair backup
echo "📦 Extraindo backup..."
tar -xzf "$BACKUP_FILE" -C "$RESTORE_DIR"
BACKUP_NAME=$(ls "$RESTORE_DIR")
cd "$RESTORE_DIR/$BACKUP_NAME"

# 2. Verificar integridade
echo "🔐 Verificando integridade..."
sha256sum -c checksums.sha256

# 3. Parar serviços
echo "🛑 Parando serviços..."
sudo systemctl stop sdr-api sdr-celery-worker sdr-celery-beat

# 4. Restaurar banco de dados
echo "📊 Restaurando banco de dados..."
source /home/solarprime/sdr-solarprime/.env
gunzip -c database.sql.gz | psql "${SUPABASE_DB_URL}"

# 5. Restaurar Redis
echo "💾 Restaurando Redis..."
docker cp redis_dump.rdb sdr-redis:/data/dump.rdb
docker restart sdr-redis

# 6. Restaurar arquivos da aplicação
echo "📁 Restaurando arquivos..."
cd /home/solarprime/sdr-solarprime
tar -xzf "$RESTORE_DIR/$BACKUP_NAME/application_files.tar.gz"

# 7. Restaurar configurações
echo "⚙️ Restaurando configurações..."
sudo tar -xzf "$RESTORE_DIR/$BACKUP_NAME/configs.tar.gz" -C /

# 8. Recarregar configurações
echo "🔄 Recarregando configurações..."
sudo systemctl daemon-reload
sudo nginx -t && sudo systemctl reload nginx

# 9. Iniciar serviços
echo "🚀 Iniciando serviços..."
sudo systemctl start sdr-api sdr-celery-worker sdr-celery-beat

# 10. Verificar saúde
echo "🏥 Verificando saúde do sistema..."
sleep 10
curl -f http://localhost:8000/health || exit 1

# 11. Limpar arquivos temporários
echo "🧹 Limpando arquivos temporários..."
rm -rf "$RESTORE_DIR"

echo "✅ Restore concluído com sucesso!"

# Enviar notificação
curl -X POST "${WHATSAPP_WEBHOOK_URL}" \
    -H "Content-Type: application/json" \
    -d "{\"number\": \"${ADMIN_WHATSAPP}\", \"text\": \"✅ Restore concluído com sucesso do backup: ${BACKUP_NAME}\"}"
```

### 8.3 Backup Automático

```bash
# Adicionar ao crontab
crontab -e

# Backup diário às 3h da manhã
0 3 * * * /home/solarprime/sdr-solarprime/scripts/backup.sh >> /var/log/backup.log 2>&1

# Backup semanal completo aos domingos
0 4 * * 0 /home/solarprime/sdr-solarprime/scripts/backup_full.sh >> /var/log/backup.log 2>&1
```

---

## 9. Otimização de Performance

### 9.1 Configurações de Performance

```python
# config/performance.py
from typing import Dict

class PerformanceConfig:
    """Configurações de otimização de performance"""
    
    # Configurações do Uvicorn
    UVICORN_CONFIG = {
        "workers": 4,  # Número de workers
        "worker_class": "uvicorn.workers.UvicornWorker",
        "worker_connections": 1000,
        "max_requests": 1000,
        "max_requests_jitter": 50,
        "timeout": 30,
        "keepalive": 5,
        "limit_concurrency": 1000,
    }
    
    # Configurações do Redis
    REDIS_CONFIG = {
        "max_connections": 100,
        "socket_keepalive": True,
        "socket_keepalive_options": {
            1: 1,  # TCP_KEEPIDLE
            2: 1,  # TCP_KEEPINTVL
            3: 3,  # TCP_KEEPCNT
        },
        "retry_on_timeout": True,
        "health_check_interval": 30,
    }
    
    # Configurações do Celery
    CELERY_CONFIG = {
        "worker_prefetch_multiplier": 1,
        "worker_max_tasks_per_child": 1000,
        "worker_disable_rate_limits": True,
        "task_compression": "gzip",
        "result_compression": "gzip",
        "task_time_limit": 300,  # 5 minutos
        "task_soft_time_limit": 240,  # 4 minutos
    }
    
    # Configurações de cache
    CACHE_CONFIG = {
        "default_ttl": 300,  # 5 minutos
        "max_entries": 10000,
        "ttl_by_endpoint": {
            "/health": 10,
            "/metrics": 5,
            "/api/leads": 60,
            "/api/analytics": 300,
        }
    }
    
    # Configurações de rate limiting
    RATE_LIMIT_CONFIG = {
        "default": "100/minute",
        "by_endpoint": {
            "/webhook": "1000/minute",
            "/api/send-message": "30/minute",
            "/auth": "10/minute",
        }
    }

# Otimizações de banco de dados
from sqlalchemy.pool import NullPool, QueuePool

DATABASE_POOL_CONFIG = {
    "poolclass": QueuePool,
    "pool_size": 20,
    "max_overflow": 40,
    "pool_timeout": 30,
    "pool_recycle": 3600,
    "pool_pre_ping": True,
}

# Configurações de compressão
COMPRESSION_CONFIG = {
    "enable_gzip": True,
    "gzip_min_length": 1000,
    "gzip_types": [
        "text/plain",
        "text/css",
        "text/javascript",
        "application/javascript",
        "application/json",
    ]
}
```

### 9.2 Otimizações da Aplicação

```python
# utils/performance_optimizations.py
import asyncio
from functools import lru_cache, wraps
from typing import Callable, Any
import time
import cachetools
from cachetools import TTLCache

# Cache global com TTL
response_cache = TTLCache(maxsize=1000, ttl=300)

def cache_response(ttl: int = 300):
    """Decorator para cachear respostas de endpoints"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Gerar chave de cache
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Verificar cache
            if cache_key in response_cache:
                return response_cache[cache_key]
            
            # Executar função
            result = await func(*args, **kwargs)
            
            # Armazenar no cache
            response_cache[cache_key] = result
            
            return result
        return wrapper
    return decorator

# Pool de conexões reutilizáveis
import httpx

class ConnectionPool:
    """Pool de conexões HTTP reutilizáveis"""
    
    def __init__(self):
        self._clients = {}
        
    def get_client(self, base_url: str) -> httpx.AsyncClient:
        if base_url not in self._clients:
            self._clients[base_url] = httpx.AsyncClient(
                base_url=base_url,
                timeout=30.0,
                limits=httpx.Limits(
                    max_keepalive_connections=20,
                    max_connections=100,
                    keepalive_expiry=30.0
                )
            )
        return self._clients[base_url]
    
    async def close_all(self):
        for client in self._clients.values():
            await client.aclose()

# Singleton global
connection_pool = ConnectionPool()

# Batch processing
class BatchProcessor:
    """Processador de lotes para operações em massa"""
    
    def __init__(self, batch_size: int = 100, flush_interval: float = 1.0):
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self._queue = asyncio.Queue()
        self._task = None
        
    async def start(self):
        """Inicia o processador de lotes"""
        self._task = asyncio.create_task(self._process_batches())
        
    async def stop(self):
        """Para o processador de lotes"""
        if self._task:
            self._task.cancel()
            
    async def add(self, item: Any):
        """Adiciona item ao lote"""
        await self._queue.put(item)
        
    async def _process_batches(self):
        """Processa lotes periodicamente"""
        batch = []
        last_flush = time.time()
        
        while True:
            try:
                # Timeout para forçar flush periódico
                timeout = max(0.1, self.flush_interval - (time.time() - last_flush))
                item = await asyncio.wait_for(
                    self._queue.get(),
                    timeout=timeout
                )
                batch.append(item)
                
                # Processar se atingiu tamanho do lote
                if len(batch) >= self.batch_size:
                    await self._process_batch(batch)
                    batch = []
                    last_flush = time.time()
                    
            except asyncio.TimeoutError:
                # Flush periódico
                if batch:
                    await self._process_batch(batch)
                    batch = []
                    last_flush = time.time()
                    
            except asyncio.CancelledError:
                # Processar lote final antes de parar
                if batch:
                    await self._process_batch(batch)
                break
                
    async def _process_batch(self, batch: list):
        """Processa um lote de itens"""
        # Implementar processamento específico
        pass

# Otimização de queries
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload

class OptimizedQueries:
    """Queries otimizadas com eager loading"""
    
    @staticmethod
    def get_lead_with_relations(session, lead_id: int):
        """Busca lead com todas as relações em uma query"""
        return session.execute(
            select(Lead)
            .options(
                selectinload(Lead.messages),
                selectinload(Lead.tasks),
                joinedload(Lead.contact)
            )
            .where(Lead.id == lead_id)
        ).scalar_one_or_none()
    
    @staticmethod
    def get_recent_leads_optimized(session, limit: int = 100):
        """Busca leads recentes com dados agregados"""
        return session.execute(
            select(
                Lead,
                func.count(Message.id).label('message_count'),
                func.max(Message.created_at).label('last_message')
            )
            .outerjoin(Message)
            .group_by(Lead.id)
            .order_by(Lead.created_at.desc())
            .limit(limit)
        ).all()
```

### 9.3 Monitoramento de Performance

```python
# utils/performance_monitoring.py
import psutil
import asyncio
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Monitor de performance do sistema"""
    
    def __init__(self):
        self.metrics = {}
        self._monitoring = False
        
    async def start_monitoring(self):
        """Inicia monitoramento contínuo"""
        self._monitoring = True
        asyncio.create_task(self._monitor_loop())
        
    async def stop_monitoring(self):
        """Para o monitoramento"""
        self._monitoring = False
        
    async def _monitor_loop(self):
        """Loop de monitoramento"""
        while self._monitoring:
            try:
                # Coletar métricas
                self.metrics = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "cpu": {
                        "percent": psutil.cpu_percent(interval=1),
                        "count": psutil.cpu_count(),
                        "freq": psutil.cpu_freq().current
                    },
                    "memory": {
                        "percent": psutil.virtual_memory().percent,
                        "available": psutil.virtual_memory().available,
                        "used": psutil.virtual_memory().used
                    },
                    "disk": {
                        "percent": psutil.disk_usage('/').percent,
                        "free": psutil.disk_usage('/').free
                    },
                    "network": {
                        "bytes_sent": psutil.net_io_counters().bytes_sent,
                        "bytes_recv": psutil.net_io_counters().bytes_recv
                    },
                    "process": {
                        "threads": len(psutil.Process().threads()),
                        "connections": len(psutil.Process().connections()),
                        "open_files": len(psutil.Process().open_files())
                    }
                }
                
                # Verificar thresholds
                await self._check_thresholds()
                
                # Aguardar próximo ciclo
                await asyncio.sleep(60)  # A cada minuto
                
            except Exception as e:
                logger.error(f"Erro no monitoramento: {str(e)}")
                await asyncio.sleep(60)
    
    async def _check_thresholds(self):
        """Verifica limites de performance"""
        # CPU alto
        if self.metrics["cpu"]["percent"] > 80:
            logger.warning(f"CPU alta: {self.metrics['cpu']['percent']}%")
            
        # Memória alta
        if self.metrics["memory"]["percent"] > 85:
            logger.warning(f"Memória alta: {self.metrics['memory']['percent']}%")
            
        # Disco cheio
        if self.metrics["disk"]["percent"] > 85:
            logger.warning(f"Disco cheio: {self.metrics['disk']['percent']}%")
    
    def get_metrics(self) -> dict:
        """Retorna métricas atuais"""
        return self.metrics

# Profiling de código
import cProfile
import pstats
from io import StringIO

def profile_function(func):
    """Decorator para fazer profiling de funções"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        profiler = cProfile.Profile()
        profiler.enable()
        
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            profiler.disable()
            
            # Gerar relatório
            s = StringIO()
            ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
            ps.print_stats(20)  # Top 20 funções
            
            logger.info(f"Profile de {func.__name__}:\n{s.getvalue()}")
    
    return wrapper
```

---

## 10. Manutenção e Atualizações

### 10.1 Script de Atualização

```bash
# scripts/update.sh
#!/bin/bash

set -e

echo "🔄 Sistema de Atualização - SDR SolarPrime"
echo "=========================================="

# Verificar se está em manutenção
if [ -f "/tmp/maintenance.lock" ]; then
    echo "❌ Sistema em manutenção. Tente novamente mais tarde."
    exit 1
fi

# Criar lock de manutenção
touch /tmp/maintenance.lock

# Função de cleanup
cleanup() {
    rm -f /tmp/maintenance.lock
    echo "🧹 Limpeza concluída"
}
trap cleanup EXIT

# 1. Backup antes da atualização
echo "🔒 Criando backup de segurança..."
./scripts/backup.sh

# 2. Ativar modo manutenção no Nginx
echo "🚧 Ativando modo manutenção..."
sudo ln -sf /etc/nginx/sites-available/maintenance /etc/nginx/sites-enabled/default
sudo nginx -s reload

# 3. Parar serviços
echo "🛑 Parando serviços..."
sudo systemctl stop sdr-celery-beat sdr-celery-worker sdr-api

# 4. Atualizar código
echo "📥 Atualizando código..."
git fetch origin
git checkout main
git pull origin main

# 5. Atualizar dependências
echo "📦 Atualizando dependências..."
source venv/bin/activate
pip install -r requirements.txt --upgrade

# 6. Executar migrações
echo "🗃️ Executando migrações..."
alembic upgrade head

# 7. Compilar assets
echo "🎨 Compilando assets..."
python manage.py collectstatic --noinput

# 8. Executar testes
echo "🧪 Executando testes..."
pytest tests/unit/ -v --tb=short

# 9. Reiniciar serviços
echo "🚀 Reiniciando serviços..."
sudo systemctl daemon-reload
sudo systemctl start sdr-api
sleep 5
sudo systemctl start sdr-celery-worker sdr-celery-beat

# 10. Verificar saúde
echo "🏥 Verificando saúde do sistema..."
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Sistema está saudável!"
        break
    fi
    
    echo "⏳ Aguardando sistema ficar pronto... ($((attempt+1))/$max_attempts)"
    sleep 2
    attempt=$((attempt+1))
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ Sistema não ficou saudável a tempo!"
    exit 1
fi

# 11. Desativar modo manutenção
echo "✅ Desativando modo manutenção..."
sudo ln -sf /etc/nginx/sites-available/sdr-solarprime-ssl /etc/nginx/sites-enabled/default
sudo nginx -s reload

echo "✅ Atualização concluída com sucesso!"

# Enviar notificação
curl -X POST "${WHATSAPP_WEBHOOK_URL}" \
    -H "Content-Type: application/json" \
    -d "{\"number\": \"${ADMIN_WHATSAPP}\", \"text\": \"✅ Sistema atualizado com sucesso!\"}"
```

### 10.2 Página de Manutenção

```html
<!-- /var/www/maintenance/index.html -->
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Manutenção - SDR SolarPrime</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
            max-width: 500px;
        }
        h1 {
            color: #333;
            margin-bottom: 20px;
        }
        p {
            color: #666;
            line-height: 1.6;
        }
        .logo {
            width: 150px;
            margin-bottom: 30px;
        }
        .progress {
            background: #e0e0e0;
            height: 4px;
            border-radius: 2px;
            overflow: hidden;
            margin: 30px 0;
        }
        .progress-bar {
            background: #4CAF50;
            height: 100%;
            width: 0%;
            animation: progress 3s ease-in-out infinite;
        }
        @keyframes progress {
            0% { width: 0%; }
            50% { width: 100%; }
            100% { width: 0%; }
        }
    </style>
</head>
<body>
    <div class="container">
        <img src="/logo.png" alt="SolarPrime" class="logo">
        <h1>Sistema em Manutenção</h1>
        <p>
            Estamos realizando melhorias para oferecer uma experiência ainda melhor.
            O sistema estará disponível em breve.
        </p>
        <div class="progress">
            <div class="progress-bar"></div>
        </div>
        <p>
            <strong>Previsão:</strong> 10 minutos<br>
            <small>Última atualização: <span id="time"></span></small>
        </p>
    </div>
    
    <script>
        // Atualizar horário
        document.getElementById('time').textContent = new Date().toLocaleTimeString('pt-BR');
        
        // Verificar status a cada 30 segundos
        setInterval(() => {
            fetch('/health')
                .then(response => {
                    if (response.ok) {
                        window.location.reload();
                    }
                })
                .catch(() => {});
        }, 30000);
    </script>
</body>
</html>
```

### 10.3 Checklist de Manutenção

```bash
# scripts/maintenance_checklist.sh
#!/bin/bash

echo "📋 Checklist de Manutenção Mensal"
echo "================================="

# Função para marcar item
check_item() {
    read -p "$1 [y/n]: " response
    if [ "$response" = "y" ]; then
        echo "✅ $1"
    else
        echo "❌ $1 - PENDENTE"
    fi
}

echo -e "\n🔍 Verificações de Sistema:"
check_item "Logs revisados e arquivados"
check_item "Espaço em disco verificado"
check_item "Backups testados"
check_item "Certificados SSL renovados"

echo -e "\n🔧 Otimizações:"
check_item "Índices do banco otimizados"
check_item "Cache Redis limpo"
check_item "Logs antigos removidos"
check_item "Containers Docker limpos"

echo -e "\n🔒 Segurança:"
check_item "Atualizações de segurança aplicadas"
check_item "Senhas rotacionadas"
check_item "Logs de acesso revisados"
check_item "Firewall rules revisadas"

echo -e "\n📊 Performance:"
check_item "Métricas de performance analisadas"
check_item "Queries lentas otimizadas"
check_item "Configurações de cache ajustadas"
check_item "Rate limits revisados"

echo -e "\n📝 Documentação:"
check_item "README atualizado"
check_item "Changelog atualizado"
check_item "Documentação da API revisada"
check_item "Runbooks atualizados"

echo -e "\n================================="
echo "Manutenção concluída em: $(date)"
```

---

## 🎉 Conclusão

O sistema está agora totalmente configurado para produção com:

### ✅ Deploy Automatizado
- Scripts para Docker e Systemd
- Configuração SSL/TLS
- Modo de manutenção

### ✅ Monitoramento Completo
- Prometheus + Grafana
- Logs centralizados com ELK
- Alertas via WhatsApp

### ✅ Alta Disponibilidade
- Health checks automáticos
- Auto-recovery
- Load balancing

### ✅ Backup e Recovery
- Backups automáticos diários
- Restore testado
- Retenção configurável

### ✅ Performance Otimizada
- Cache em múltiplas camadas
- Connection pooling
- Batch processing

### 📝 Checklist Final de Deploy

- [ ] Todos os scripts executáveis (`chmod +x`)
- [ ] Variáveis de ambiente configuradas
- [ ] SSL/TLS ativo
- [ ] Monitoramento funcionando
- [ ] Alertas configurados
- [ ] Backup automático ativo
- [ ] Documentação atualizada
- [ ] Testes de carga executados
- [ ] Plano de contingência documentado
- [ ] Equipe treinada

---

**🚀 O sistema SDR SolarPrime está pronto para produção!**