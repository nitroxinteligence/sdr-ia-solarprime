# 01. Setup do Ambiente - Guia Completo

Este documento fornece instruções detalhadas para configurar o ambiente de desenvolvimento e produção do Agente SDR SolarPrime na VPS Hostinger.

## 📋 Índice

1. [Preparação da VPS](#1-preparação-da-vps)
2. [Instalação das Dependências Base](#2-instalação-das-dependências-base)
3. [Configuração do Python](#3-configuração-do-python)
4. [Instalação do Docker](#4-instalação-do-docker)
5. [Setup do Redis](#5-setup-do-redis)
6. [Configuração do Nginx](#6-configuração-do-nginx)
7. [Segurança e Firewall](#7-segurança-e-firewall)
8. [Estrutura do Projeto](#8-estrutura-do-projeto)
9. [Variáveis de Ambiente](#9-variáveis-de-ambiente)
10. [Validação do Setup](#10-validação-do-setup)

---

## 1. Preparação da VPS

### 1.1 Acesso Inicial

```bash
# Conecte-se à sua VPS via SSH
ssh root@seu_ip_vps

# Atualize o sistema
apt update && apt upgrade -y

# Configure o timezone para São Paulo
timedatectl set-timezone America/Sao_Paulo
```

### 1.2 Criar Usuário Non-Root

```bash
# Criar novo usuário
adduser solarprime

# Adicionar ao grupo sudo
usermod -aG sudo solarprime

# Configurar SSH para o novo usuário
su - solarprime
mkdir ~/.ssh
chmod 700 ~/.ssh

# Copie sua chave SSH pública
# No seu computador local:
ssh-copy-id solarprime@seu_ip_vps
```

### 1.3 Configurar Hostname

```bash
# Definir hostname
sudo hostnamectl set-hostname sdr-solarprime

# Editar /etc/hosts
sudo nano /etc/hosts
# Adicione:
# 127.0.0.1 sdr-solarprime
```

---

## 2. Instalação das Dependências Base

### 2.1 Pacotes Essenciais

```bash
# Instalar pacotes essenciais
sudo apt install -y \
    build-essential \
    curl \
    wget \
    git \
    vim \
    htop \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release \
    net-tools \
    ufw \
    fail2ban
```

### 2.2 Ferramentas de Desenvolvimento

```bash
# Instalar ferramentas de desenvolvimento
sudo apt install -y \
    gcc \
    g++ \
    make \
    libssl-dev \
    libffi-dev \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev
```

---

## 3. Configuração do Python

### 3.1 Instalar Python 3.11

```bash
# Adicionar repositório deadsnakes
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update

# Instalar Python 3.11
sudo apt install -y python3.11 python3.11-venv python3.11-dev

# Instalar pip
curl https://bootstrap.pypa.io/get-pip.py | sudo python3.11

# Verificar instalação
python3.11 --version
pip3.11 --version
```

### 3.2 Configurar Python como Padrão

```bash
# Criar links simbólicos
sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1
sudo update-alternatives --install /usr/bin/pip pip /usr/bin/pip3.11 1

# Configurar como padrão
sudo update-alternatives --config python
# Selecione python3.11
```

### 3.3 Criar Ambiente Virtual

```bash
# Criar diretório do projeto
cd ~
mkdir sdr-solarprime
cd sdr-solarprime

# Criar ambiente virtual
python -m venv venv

# Ativar ambiente
source venv/bin/activate

# Atualizar pip
pip install --upgrade pip setuptools wheel
```

---

## 4. Instalação do Docker

### 4.1 Instalar Docker

```bash
# Adicionar chave GPG oficial do Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Adicionar repositório
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Instalar Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER

# Reiniciar sessão para aplicar mudanças
exit
# Reconecte via SSH
```

### 4.2 Verificar Docker

```bash
# Verificar instalação
docker --version
docker compose version

# Testar Docker
docker run hello-world
```

---

## 5. Setup do Redis

### 5.1 Instalar Redis via Docker

```bash
# Criar diretório para Redis
mkdir -p ~/sdr-solarprime/redis
cd ~/sdr-solarprime/redis

# Criar docker-compose.yml
cat > docker-compose.yml << EOF
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    container_name: redis-solarprime
    restart: always
    ports:
      - "6379:6379"
    volumes:
      - ./data:/data
    command: redis-server --appendonly yes --requirepass "sua_senha_redis_aqui"
    networks:
      - solarprime-network

networks:
  solarprime-network:
    driver: bridge
EOF

# Iniciar Redis
docker compose up -d

# Verificar status
docker ps
docker logs redis-solarprime
```

### 5.2 Testar Conexão Redis

```bash
# Instalar redis-cli
sudo apt install -y redis-tools

# Testar conexão
redis-cli -h localhost -p 6379 -a "sua_senha_redis_aqui" ping
# Deve retornar: PONG
```

---

## 6. Configuração do Nginx

### 6.1 Instalar Nginx

```bash
# Instalar Nginx
sudo apt install -y nginx

# Verificar status
sudo systemctl status nginx
```

### 6.2 Configurar Nginx para a Aplicação

```bash
# Criar configuração
sudo nano /etc/nginx/sites-available/sdr-solarprime

# Adicionar configuração:
```

```nginx
server {
    listen 80;
    server_name seu_dominio.com.br;
    
    # Redirecionar para HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name seu_dominio.com.br;
    
    # SSL será configurado com Certbot
    
    # Logs
    access_log /var/log/nginx/sdr-solarprime.access.log;
    error_log /var/log/nginx/sdr-solarprime.error.log;
    
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
    
    # Webhook endpoint com timeout maior
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
}
```

### 6.3 Ativar Site

```bash
# Criar link simbólico
sudo ln -s /etc/nginx/sites-available/sdr-solarprime /etc/nginx/sites-enabled/

# Testar configuração
sudo nginx -t

# Recarregar Nginx
sudo systemctl reload nginx
```

### 6.4 Instalar SSL com Certbot

```bash
# Instalar Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obter certificado SSL
sudo certbot --nginx -d seu_dominio.com.br

# Configurar renovação automática
sudo systemctl enable certbot.timer
```

---

## 7. Segurança e Firewall

### 7.1 Configurar UFW (Firewall)

```bash
# Configurar regras básicas
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Permitir SSH (ajuste a porta se necessário)
sudo ufw allow 22/tcp

# Permitir HTTP e HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Permitir Redis apenas localhost
# Redis já está protegido por binding apenas em localhost

# Ativar firewall
sudo ufw enable

# Verificar status
sudo ufw status verbose
```

### 7.2 Configurar Fail2ban

```bash
# Criar configuração para SSH
sudo nano /etc/fail2ban/jail.local

# Adicionar:
```

```ini
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
port = 22
filter = sshd
logpath = /var/log/auth.log
maxretry = 3

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
port = http,https
logpath = /var/log/nginx/error.log

[nginx-noscript]
enabled = true
port = http,https
filter = nginx-noscript
logpath = /var/log/nginx/access.log
maxretry = 6

[nginx-badbots]
enabled = true
port = http,https
filter = nginx-badbots
logpath = /var/log/nginx/access.log
maxretry = 2

[nginx-noproxy]
enabled = true
port = http,https
filter = nginx-noproxy
logpath = /var/log/nginx/access.log
maxretry = 2
```

```bash
# Reiniciar Fail2ban
sudo systemctl restart fail2ban
sudo systemctl enable fail2ban

# Verificar status
sudo fail2ban-client status
```

### 7.3 Segurança Adicional

```bash
# Desabilitar login root via SSH
sudo nano /etc/ssh/sshd_config
# Altere: PermitRootLogin no

# Reiniciar SSH
sudo systemctl restart sshd

# Configurar atualizações automáticas de segurança
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure --priority=low unattended-upgrades
```

---

## 8. Estrutura do Projeto

### 8.1 Criar Estrutura de Diretórios

```bash
cd ~/sdr-solarprime

# Criar estrutura completa
mkdir -p {api/{routes,middleware},services,models,agents/{tools,knowledge},config,utils,scripts,docs,tests/{unit,integration,e2e,fixtures},migrations/supabase,logs,assets}

# Criar arquivo .gitignore
cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
.venv

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Environment
.env
.env.local
.env.*.local

# Logs
logs/
*.log

# Database
*.db
*.sqlite3

# Cache
.cache/
.pytest_cache/

# OS
.DS_Store
Thumbs.db

# Project specific
/data/
/temp/
/backups/
EOF
```

### 8.2 Criar Arquivos Base

```bash
# Criar requirements.txt inicial
cat > requirements.txt << EOF
# Core
fastapi==0.115.0
uvicorn[standard]==0.30.0
python-multipart==0.0.9
python-dotenv==1.0.0

# AI & LLM
agno==0.2.0
google-generativeai==0.7.2

# Database
supabase==2.5.0
psycopg2-binary==2.9.9
SQLAlchemy==2.0.31

# Redis & Queue
redis==5.0.7
celery==5.3.6

# API Integrations
httpx==0.27.0
requests==2.32.3
kommo-python==0.1.2

# Utils
pydantic==2.8.2
pydantic-settings==2.3.4
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# Development
pytest==8.2.2
pytest-asyncio==0.23.7
black==24.4.2
flake8==7.1.0
mypy==1.10.1

# Monitoring
sentry-sdk==2.7.1
prometheus-client==0.20.0
EOF
```

---

## 9. Variáveis de Ambiente

### 9.1 Criar Arquivo .env

```bash
# Criar arquivo .env
cat > .env.example << EOF
# Environment
ENVIRONMENT=development
DEBUG=True

# Application
APP_NAME="SDR IA SolarPrime"
APP_VERSION="1.0.0"
SECRET_KEY="gerar_uma_chave_segura_aqui"

# API URLs
API_BASE_URL="https://seu_dominio.com.br"
WEBHOOK_URL="https://seu_dominio.com.br/webhook"

# Google Gemini
GEMINI_API_KEY="sua_api_key_gemini"
GEMINI_MODEL="gemini-2.5-pro"
GEMINI_TEMPERATURE=0.7
GEMINI_MAX_TOKENS=2048

# Supabase
SUPABASE_URL="https://seu_projeto.supabase.co"
SUPABASE_ANON_KEY="sua_anon_key"
SUPABASE_SERVICE_KEY="sua_service_key"

# Evolution API
EVOLUTION_API_URL="http://localhost:8080"
EVOLUTION_API_KEY="sua_api_key"
EVOLUTION_INSTANCE_NAME="solarprime"
EVOLUTION_INSTANCE_TOKEN="seu_token"

# Kommo CRM
KOMMO_CLIENT_ID="seu_client_id"
KOMMO_CLIENT_SECRET="seu_client_secret"
KOMMO_REDIRECT_URI="https://seu_dominio.com.br/auth/callback"
KOMMO_SUBDOMAIN="seu_subdomain"

# Redis
REDIS_URL="redis://:sua_senha_redis_aqui@localhost:6379/0"
CELERY_BROKER_URL="redis://:sua_senha_redis_aqui@localhost:6379/1"
CELERY_RESULT_BACKEND="redis://:sua_senha_redis_aqui@localhost:6379/2"

# Business Config
AI_RESPONSE_DELAY_SECONDS=2
BUSINESS_HOURS_START="08:00"
BUSINESS_HOURS_END="18:00"
TIMEZONE="America/Sao_Paulo"

# Reporting
REPORT_DAY_OF_WEEK="monday"
REPORT_TIME="09:00"
WHATSAPP_GROUP_ID="grupo_id_aqui"

# Security
JWT_SECRET_KEY="gerar_outra_chave_segura"
JWT_ALGORITHM="HS256"
JWT_EXPIRATION_HOURS=24

# Logging
LOG_LEVEL="INFO"
LOG_FILE="/home/solarprime/sdr-solarprime/logs/app.log"

# Monitoring
SENTRY_DSN=""
ENABLE_METRICS=True
EOF

# Copiar para .env real
cp .env.example .env

# Editar com suas credenciais
nano .env
```

### 9.2 Gerar Chaves Secretas

```bash
# Gerar SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Gerar JWT_SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 10. Validação do Setup

### 10.1 Script de Validação

```bash
# Criar script de validação
cat > validate_setup.py << EOF
#!/usr/bin/env python3
"""
Script de validação do ambiente
"""
import sys
import subprocess
import pkg_resources

def check_command(command):
    """Verifica se um comando está disponível"""
    try:
        subprocess.run(command, shell=True, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False

def check_python_version():
    """Verifica versão do Python"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 11:
        print("✅ Python 3.11+ instalado")
        return True
    else:
        print("❌ Python 3.11+ não encontrado")
        return False

def check_packages():
    """Verifica pacotes Python essenciais"""
    required = ['fastapi', 'uvicorn', 'agno', 'redis', 'celery']
    missing = []
    
    for package in required:
        try:
            pkg_resources.get_distribution(package)
        except pkg_resources.DistributionNotFound:
            missing.append(package)
    
    if not missing:
        print("✅ Pacotes Python essenciais instalados")
        return True
    else:
        print(f"❌ Pacotes faltando: {', '.join(missing)}")
        return False

def check_services():
    """Verifica serviços essenciais"""
    services = {
        'Docker': 'docker --version',
        'Redis': 'redis-cli -h localhost -p 6379 ping',
        'Nginx': 'systemctl is-active nginx',
    }
    
    all_ok = True
    for service, command in services.items():
        if check_command(command):
            print(f"✅ {service} está funcionando")
        else:
            print(f"❌ {service} não está funcionando")
            all_ok = False
    
    return all_ok

def check_ports():
    """Verifica portas importantes"""
    import socket
    
    ports = {
        80: "HTTP",
        443: "HTTPS",
        6379: "Redis",
        8000: "FastAPI"
    }
    
    for port, service in ports.items():
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        
        if result == 0:
            print(f"✅ Porta {port} ({service}) está aberta")
        else:
            print(f"⚠️  Porta {port} ({service}) está fechada")

def main():
    print("🔍 Validando ambiente de desenvolvimento...\n")
    
    checks = [
        check_python_version(),
        check_packages(),
        check_services(),
    ]
    
    print("\n📊 Verificando portas:")
    check_ports()
    
    if all(checks):
        print("\n✅ Ambiente configurado corretamente!")
    else:
        print("\n❌ Alguns problemas foram encontrados. Verifique as mensagens acima.")

if __name__ == "__main__":
    main()
EOF

# Tornar executável
chmod +x validate_setup.py

# Executar validação
python validate_setup.py
```

### 10.2 Checklist Final

- [ ] VPS acessível via SSH
- [ ] Python 3.11 instalado e configurado
- [ ] Ambiente virtual criado
- [ ] Docker e Docker Compose funcionando
- [ ] Redis rodando e acessível
- [ ] Nginx configurado e com SSL
- [ ] Firewall configurado
- [ ] Fail2ban ativo
- [ ] Estrutura de diretórios criada
- [ ] Arquivo .env configurado
- [ ] Todas as validações passando

---

## 🎉 Próximos Passos

Parabéns! Seu ambiente está configurado. Agora você pode seguir para:

1. **[02. Desenvolvimento do Agente IA](02-agente-ia.md)** - Implementar o agente com AGnO Framework
2. Instalar as dependências Python: `pip install -r requirements.txt`
3. Começar o desenvolvimento da aplicação

---

## 🆘 Troubleshooting

### Problema: Erro de permissão no Docker
```bash
# Solução: Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER
# Fazer logout e login novamente
```

### Problema: Redis não conecta
```bash
# Verificar se está rodando
docker ps | grep redis

# Ver logs
docker logs redis-solarprime

# Testar conexão
redis-cli -h localhost -p 6379 -a "sua_senha" ping
```

### Problema: Nginx não inicia
```bash
# Verificar erro
sudo nginx -t

# Ver logs
sudo tail -f /var/log/nginx/error.log

# Verificar porta 80
sudo lsof -i :80
```

### Problema: Python não encontrado
```bash
# Verificar alternativas
sudo update-alternatives --config python

# Criar link manualmente
sudo ln -sf /usr/bin/python3.11 /usr/bin/python
```

---

**💡 Dica**: Faça um snapshot da sua VPS após completar este setup. Isso facilitará recuperação em caso de problemas.