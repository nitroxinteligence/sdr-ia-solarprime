# Guia de Instalação - SDR IA SolarPrime

Este guia fornece instruções detalhadas para instalar e configurar o agente SDR IA SolarPrime em diferentes ambientes.

## 📋 Requisitos do Sistema

### Sistema Operacional
- **Recomendado**: Ubuntu 22.04 LTS
- **Alternativas**: Ubuntu 20.04 LTS, Debian 11+
- **Mínimo de RAM**: 4GB (8GB recomendado para produção)
- **Espaço em Disco**: 20GB mínimo
- **CPU**: 2 cores (4 cores recomendado para produção)

### Software Necessário
- **Python**: 3.11+ (obrigatório)
- **Docker**: 24.0+ (para deploy containerizado)
- **Docker Compose**: 2.20+ (para orquestração)
- **Redis**: 7.0+ (para cache e filas)
- **PostgreSQL**: 15+ (via Supabase)
- **Nginx**: 1.18+ (para proxy reverso)
- **Git**: 2.25+

## 🚀 Instalação Rápida (Docker)

### 1. Clonar o Repositório
```bash
git clone https://github.com/sua-empresa/sdr-ia-solarprime.git
cd sdr-ia-solarprime
```

### 2. Configurar Variáveis de Ambiente
```bash
cp .env.example .env
nano .env  # Editar com suas credenciais
```

### 3. Build e Execução com Docker
```bash
# Build da imagem
docker build -t sdr-agent:latest .

# Executar com Docker Compose
docker-compose up -d

# Verificar logs
docker-compose logs -f sdr-api
```

## 🛠️ Instalação Manual (Desenvolvimento)

### 1. Preparar o Sistema
```bash
# Atualizar pacotes do sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependências do sistema
sudo apt install -y \
    python3.11 \
    python3.11-venv \
    python3.11-dev \
    python3-pip \
    libpq-dev \
    libmagic1 \
    libmagic-dev \
    poppler-utils \
    ffmpeg \
    libsndfile1 \
    redis-server \
    nginx \
    certbot \
    python3-certbot-nginx \
    curl \
    git
```

### 2. Configurar Python e Ambiente Virtual
```bash
# Criar ambiente virtual
python3.11 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate

# Atualizar pip
pip install --upgrade pip setuptools wheel
```

### 3. Instalar Dependências Python
```bash
# Instalar dependências do projeto
pip install -r requirements.txt

# Verificar instalação
python -c "import agno; print(f'AGnO Framework v{agno.__version__}')"
```

### 4. Configurar Redis
```bash
# Habilitar e iniciar Redis
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Verificar status
sudo systemctl status redis-server

# Testar conexão
redis-cli ping  # Deve retornar PONG
```

### 5. Configurar Banco de Dados (Supabase)
1. Criar conta em [Supabase](https://supabase.com)
2. Criar novo projeto
3. Copiar URL e Service Key para o .env
4. Executar migrations (se disponíveis):
```bash
# Instalar Supabase CLI
npm install -g supabase

# Fazer login
supabase login

# Link com projeto
supabase link --project-ref your-project-ref

# Executar migrations
supabase db push
```

## 🐳 Deploy com EasyPanel

### 1. Preparar Projeto para EasyPanel
```bash
# Criar arquivo docker-compose específico para EasyPanel
cp docker-compose.yml docker-compose.easypanel.yml
```

### 2. Configurar no EasyPanel

1. **Criar Novo Projeto**:
   - Acessar painel EasyPanel
   - Clicar em "New App"
   - Selecionar "Docker Compose"

2. **Configurar Repositório**:
   ```yaml
   Git Repository: https://github.com/sua-empresa/sdr-ia-solarprime.git
   Branch: main
   Build Path: /
   Docker Compose File: docker-compose.easypanel.yml
   ```

3. **Configurar Variáveis de Ambiente**:
   - Adicionar todas as variáveis do .env no painel
   - Marcar variáveis sensíveis como "Secret"

4. **Configurar Domínio**:
   ```
   Domain: api.seudominio.com.br
   Port: 8000
   HTTPS: Enable (Let's Encrypt)
   ```

5. **Deploy**:
   - Clicar em "Deploy"
   - Monitorar logs em tempo real

## 🔧 Configuração do Nginx

### 1. Configurar Proxy Reverso
```nginx
# /etc/nginx/sites-available/sdr-agent
server {
    listen 80;
    server_name api.seudominio.com.br;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.seudominio.com.br;
    
    # SSL configurado pelo Certbot
    ssl_certificate /etc/letsencrypt/live/api.seudominio.com.br/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.seudominio.com.br/privkey.pem;
    
    # Configurações de segurança SSL
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # Logs
    access_log /var/log/nginx/sdr-agent.access.log;
    error_log /var/log/nginx/sdr-agent.error.log;
    
    # Tamanho máximo de upload (para PDFs e imagens)
    client_max_body_size 25M;
    
    # Timeouts para operações longas
    proxy_read_timeout 300s;
    proxy_connect_timeout 75s;
    proxy_send_timeout 300s;
    
    # Headers de segurança
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Webhook Evolution API
    location /webhook/whatsapp {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Não fazer buffer para webhooks
        proxy_buffering off;
        proxy_request_buffering off;
    }
    
    # API principal
    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 2. Ativar Configuração
```bash
# Criar link simbólico
sudo ln -s /etc/nginx/sites-available/sdr-agent /etc/nginx/sites-enabled/

# Testar configuração
sudo nginx -t

# Recarregar Nginx
sudo systemctl reload nginx
```

### 3. Configurar SSL com Let's Encrypt
```bash
# Obter certificado SSL
sudo certbot --nginx -d api.seudominio.com.br

# Renovação automática (já configurada pelo certbot)
sudo certbot renew --dry-run
```

## 🔄 Configuração de Serviços (systemd)

### 1. Criar Serviço da API
```ini
# /etc/systemd/system/sdr-agent.service
[Unit]
Description=SDR IA SolarPrime Agent
After=network.target redis.service
Requires=redis.service

[Service]
Type=exec
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/sdr-ia-solarprime
Environment="PATH=/home/ubuntu/sdr-ia-solarprime/venv/bin"
ExecStart=/home/ubuntu/sdr-ia-solarprime/venv/bin/uvicorn agente.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10
StandardOutput=append:/var/log/sdr-agent/api.log
StandardError=append:/var/log/sdr-agent/error.log

# Limites de recursos
LimitNOFILE=65536
LimitNPROC=4096

[Install]
WantedBy=multi-user.target
```

### 2. Criar Serviço do Celery Worker
```ini
# /etc/systemd/system/sdr-agent-worker.service
[Unit]
Description=SDR Agent Celery Worker
After=network.target redis.service
Requires=redis.service

[Service]
Type=exec
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/sdr-ia-solarprime
Environment="PATH=/home/ubuntu/sdr-ia-solarprime/venv/bin"
ExecStart=/home/ubuntu/sdr-ia-solarprime/venv/bin/celery -A services.tasks worker --loglevel=info
Restart=always
RestartSec=10
StandardOutput=append:/var/log/sdr-agent/worker.log
StandardError=append:/var/log/sdr-agent/worker-error.log

[Install]
WantedBy=multi-user.target
```

### 3. Criar Serviço do Celery Beat
```ini
# /etc/systemd/system/sdr-agent-beat.service
[Unit]
Description=SDR Agent Celery Beat
After=network.target redis.service
Requires=redis.service

[Service]
Type=exec
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/sdr-ia-solarprime
Environment="PATH=/home/ubuntu/sdr-ia-solarprime/venv/bin"
ExecStart=/home/ubuntu/sdr-ia-solarprime/venv/bin/celery -A services.tasks beat --loglevel=info
Restart=always
RestartSec=10
StandardOutput=append:/var/log/sdr-agent/beat.log
StandardError=append:/var/log/sdr-agent/beat-error.log

[Install]
WantedBy=multi-user.target
```

### 4. Ativar e Iniciar Serviços
```bash
# Criar diretório de logs
sudo mkdir -p /var/log/sdr-agent
sudo chown ubuntu:ubuntu /var/log/sdr-agent

# Recarregar daemon
sudo systemctl daemon-reload

# Habilitar serviços
sudo systemctl enable sdr-agent sdr-agent-worker sdr-agent-beat

# Iniciar serviços
sudo systemctl start sdr-agent sdr-agent-worker sdr-agent-beat

# Verificar status
sudo systemctl status sdr-agent
sudo systemctl status sdr-agent-worker
sudo systemctl status sdr-agent-beat
```

## 🔍 Troubleshooting

### Problemas Comuns

#### 1. Erro de Conexão com Redis
```bash
# Verificar se Redis está rodando
sudo systemctl status redis-server

# Testar conexão
redis-cli ping

# Verificar logs
sudo journalctl -u redis-server -n 50
```

#### 2. Erro de Permissão no Docker
```bash
# Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER

# Fazer logout e login novamente
exit
```

#### 3. Porta 8000 já em uso
```bash
# Encontrar processo usando a porta
sudo lsof -i :8000

# Matar processo (substituir PID)
sudo kill -9 <PID>
```

#### 4. Erro de SSL/TLS
```bash
# Renovar certificado manualmente
sudo certbot renew --force-renewal

# Verificar certificado
sudo openssl x509 -in /etc/letsencrypt/live/api.seudominio.com.br/cert.pem -text -noout
```

#### 5. Webhook não recebendo mensagens
```bash
# Verificar logs do Nginx
sudo tail -f /var/log/nginx/sdr-agent.error.log

# Verificar se API está acessível
curl -X POST https://api.seudominio.com.br/webhook/whatsapp \
  -H "Content-Type: application/json" \
  -d '{"test": true}'
```

### Logs e Monitoramento

#### Localização dos Logs
- **API**: `/var/log/sdr-agent/api.log`
- **Worker**: `/var/log/sdr-agent/worker.log`
- **Beat**: `/var/log/sdr-agent/beat.log`
- **Nginx**: `/var/log/nginx/sdr-agent.*.log`
- **Docker**: `docker-compose logs -f [service]`

#### Comandos Úteis
```bash
# Logs em tempo real da API
sudo journalctl -u sdr-agent -f

# Logs do Worker
sudo journalctl -u sdr-agent-worker -f

# Monitorar todos os serviços
sudo journalctl -u sdr-agent* -f

# Verificar consumo de recursos
htop
docker stats
```

## 🔐 Segurança Pós-Instalação

### 1. Configurar Firewall
```bash
# Instalar UFW
sudo apt install ufw

# Configurar regras básicas
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Permitir SSH, HTTP e HTTPS
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https

# Habilitar firewall
sudo ufw enable
```

### 2. Configurar Fail2ban
```bash
# Instalar fail2ban
sudo apt install fail2ban

# Criar configuração para API
sudo nano /etc/fail2ban/jail.local
```

```ini
[sdr-api]
enabled = true
port = http,https
filter = sdr-api
logpath = /var/log/sdr-agent/api.log
maxretry = 5
bantime = 3600
```

### 3. Rotação de Logs
```bash
# Criar configuração logrotate
sudo nano /etc/logrotate.d/sdr-agent
```

```
/var/log/sdr-agent/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 ubuntu ubuntu
    sharedscripts
    postrotate
        systemctl reload sdr-agent >/dev/null 2>&1 || true
    endscript
}
```

## 📞 Suporte

Para problemas durante a instalação:
1. Verificar logs detalhados
2. Consultar documentação da API em `/docs`
3. Contatar equipe de desenvolvimento
4. Abrir issue no repositório

---

**Última atualização**: Janeiro 2025