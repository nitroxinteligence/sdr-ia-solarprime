#!/bin/bash
# =============================================================================
# SDR IA SolarPrime - Script de Configuração Inicial para Produção
# =============================================================================
# Este script configura o ambiente de produção no Hostinger VPS pela primeira vez
# Execute apenas uma vez durante a configuração inicial
# =============================================================================

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configurações
DOMAIN="api.seudominio.com.br"
APP_USER="ubuntu"
APP_DIR="/home/$APP_USER/sdr-solarprime"
SERVICE_NAME="sdr-solarprime"

# Funções auxiliares
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Verificar se está rodando como root
if [ "$EUID" -ne 0 ]; then 
    error "Este script deve ser executado como root (use sudo)"
    exit 1
fi

log "Iniciando configuração de produção para SDR IA SolarPrime..."

# 1. Atualizar sistema
log "Atualizando sistema..."
apt update
apt upgrade -y

# 2. Instalar dependências do sistema
log "Instalando dependências do sistema..."
apt install -y \
    python3.10 \
    python3.10-venv \
    python3-pip \
    git \
    nginx \
    certbot \
    python3-certbot-nginx \
    redis-server \
    postgresql-client \
    htop \
    ncdu \
    ufw \
    fail2ban \
    logrotate

# 3. Configurar firewall
log "Configurando firewall..."
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 8000/tcp  # Temporário, remover depois
ufw --force enable

# 4. Criar usuário da aplicação (se não existir)
if ! id "$APP_USER" &>/dev/null; then
    log "Criando usuário $APP_USER..."
    adduser --disabled-password --gecos "" $APP_USER
    usermod -aG sudo $APP_USER
fi

# 5. Criar estrutura de diretórios
log "Criando estrutura de diretórios..."
sudo -u $APP_USER mkdir -p $APP_DIR
mkdir -p /var/log/sdr-solarprime
chown $APP_USER:$APP_USER /var/log/sdr-solarprime

# 6. Clonar repositório (se não existir)
if [ ! -d "$APP_DIR/.git" ]; then
    log "Clonando repositório..."
    read -p "Digite a URL do repositório Git: " GIT_REPO
    sudo -u $APP_USER git clone "$GIT_REPO" "$APP_DIR"
fi

# 7. Configurar ambiente Python
log "Configurando ambiente Python..."
cd $APP_DIR
sudo -u $APP_USER python3.10 -m venv venv
sudo -u $APP_USER ./venv/bin/pip install --upgrade pip
sudo -u $APP_USER ./venv/bin/pip install -r requirements.txt

# 8. Configurar variáveis de ambiente
if [ ! -f "$APP_DIR/.env" ]; then
    log "Configurando variáveis de ambiente..."
    if [ -f "$APP_DIR/.env.production" ]; then
        cp "$APP_DIR/.env.production" "$APP_DIR/.env"
        chown $APP_USER:$APP_USER "$APP_DIR/.env"
        chmod 600 "$APP_DIR/.env"
        info "Por favor, edite $APP_DIR/.env e configure as variáveis necessárias"
    else
        error "Arquivo .env.production não encontrado!"
    fi
fi

# 9. Criar serviço systemd
log "Criando serviço systemd..."
cat > /etc/systemd/system/$SERVICE_NAME.service <<EOF
[Unit]
Description=SDR IA SolarPrime - Intelligent Sales Agent
After=network.target

[Service]
Type=exec
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=$APP_DIR/venv/bin/uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10
StandardOutput=append:/var/log/sdr-solarprime/app.log
StandardError=append:/var/log/sdr-solarprime/error.log

# Limites de recursos
LimitNOFILE=65536
LimitNPROC=4096

# Segurança
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

# 10. Configurar Nginx
log "Configurando Nginx..."
cat > /etc/nginx/sites-available/$SERVICE_NAME <<EOF
# Redirect HTTP to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name $DOMAIN;
    
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    location / {
        return 301 https://\$server_name\$request_uri;
    }
}

# HTTPS Server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name $DOMAIN;
    
    # SSL certificates (serão adicionados pelo certbot)
    # ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    
    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    
    # Logging
    access_log /var/log/nginx/$SERVICE_NAME.access.log;
    error_log /var/log/nginx/$SERVICE_NAME.error.log;
    
    # Proxy configuration
    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Webhook endpoint com timeout maior
    location /webhook/ {
        proxy_pass http://localhost:8000/webhook/;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Timeout maior para webhooks
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
        proxy_send_timeout 300s;
        
        # Buffer settings
        proxy_buffering off;
        proxy_request_buffering off;
    }
    
    # Health check endpoint
    location /health {
        proxy_pass http://localhost:8000/health;
        access_log off;
    }
    
    # Static files (se houver)
    location /static/ {
        alias $APP_DIR/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# 11. Ativar site no Nginx
ln -sf /etc/nginx/sites-available/$SERVICE_NAME /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t

# 12. Configurar Redis (opcional)
log "Configurando Redis..."
cat >> /etc/redis/redis.conf <<EOF

# Configurações customizadas para SDR SolarPrime
maxmemory 256mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
EOF

systemctl restart redis-server

# 13. Configurar fail2ban
log "Configurando fail2ban..."
cat > /etc/fail2ban/jail.local <<EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true

[nginx-http-auth]
enabled = true

[nginx-limit-req]
enabled = true
EOF

systemctl restart fail2ban

# 14. Configurar backups automáticos
log "Configurando backups automáticos..."
cat > /home/$APP_USER/backup.sh <<'EOF'
#!/bin/bash
# Script de backup automático

BACKUP_DIR="/home/ubuntu/backups"
APP_DIR="/home/ubuntu/sdr-solarprime"
DATE=$(date +%Y%m%d_%H%M%S)
KEEP_DAYS=7

# Criar diretório de backup
mkdir -p "$BACKUP_DIR"

# Backup do código (excluindo venv e cache)
tar -czf "$BACKUP_DIR/app_$DATE.tar.gz" \
    -C "$APP_DIR" . \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='.git' \
    --exclude='*.pyc'

# Backup do .env
cp "$APP_DIR/.env" "$BACKUP_DIR/env_$DATE"

# Limpar backups antigos
find "$BACKUP_DIR" -name "app_*.tar.gz" -mtime +$KEEP_DAYS -delete
find "$BACKUP_DIR" -name "env_*" -mtime +$KEEP_DAYS -delete

echo "Backup concluído: $DATE"
EOF

chown $APP_USER:$APP_USER /home/$APP_USER/backup.sh
chmod +x /home/$APP_USER/backup.sh

# Adicionar ao crontab
echo "0 3 * * * /home/$APP_USER/backup.sh >> /var/log/sdr-solarprime/backup.log 2>&1" | crontab -u $APP_USER -

# 15. Criar script de monitoramento
log "Criando script de monitoramento..."
cat > /home/$APP_USER/monitor.sh <<'EOF'
#!/bin/bash
# Script de monitoramento

check_service() {
    if systemctl is-active --quiet sdr-solarprime; then
        echo "✓ Serviço SDR SolarPrime está ativo"
    else
        echo "✗ Serviço SDR SolarPrime está inativo"
        systemctl status sdr-solarprime --no-pager
    fi
}

check_nginx() {
    if systemctl is-active --quiet nginx; then
        echo "✓ Nginx está ativo"
    else
        echo "✗ Nginx está inativo"
    fi
}

check_redis() {
    if systemctl is-active --quiet redis-server; then
        echo "✓ Redis está ativo"
    else
        echo "✗ Redis está inativo"
    fi
}

check_api() {
    response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
    if [ "$response" = "200" ]; then
        echo "✓ API está respondendo (HTTP $response)"
    else
        echo "✗ API não está respondendo (HTTP $response)"
    fi
}

check_disk() {
    usage=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ "$usage" -lt 80 ]; then
        echo "✓ Uso de disco: ${usage}%"
    else
        echo "⚠ Uso de disco alto: ${usage}%"
    fi
}

check_memory() {
    usage=$(free | awk 'NR==2 {printf "%.0f", $3/$2 * 100.0}')
    if [ "$usage" -lt 80 ]; then
        echo "✓ Uso de memória: ${usage}%"
    else
        echo "⚠ Uso de memória alto: ${usage}%"
    fi
}

echo "=== Monitor SDR SolarPrime ==="
echo "Data: $(date)"
echo "=============================="
check_service
check_nginx
check_redis
check_api
check_disk
check_memory
echo "=============================="
EOF

chown $APP_USER:$APP_USER /home/$APP_USER/monitor.sh
chmod +x /home/$APP_USER/monitor.sh

# 16. Habilitar e iniciar serviços
log "Habilitando serviços..."
systemctl daemon-reload
systemctl enable $SERVICE_NAME
systemctl enable nginx
systemctl enable redis-server

# 17. Informações finais
log "=========================================="
log "Configuração inicial concluída!"
log "=========================================="
info "Próximos passos:"
echo "1. Configure o DNS para apontar $DOMAIN para este servidor"
echo "2. Execute: sudo certbot --nginx -d $DOMAIN"
echo "3. Edite as variáveis em: $APP_DIR/.env"
echo "4. Inicie os serviços: sudo systemctl start $SERVICE_NAME"
echo "5. Verifique o status: /home/$APP_USER/monitor.sh"
echo "6. Configure o webhook na Evolution API para: https://$DOMAIN/webhook/whatsapp"
log "=========================================="

# Fim do script
exit 0