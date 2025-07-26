#!/bin/bash
# Deploy automatizado para Hostinger VPS
# =====================================

set -e  # Parar em caso de erro

echo "🚀 Deploy SDR IA SolarPrime na Hostinger VPS"
echo "==========================================="
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar se está rodando como root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}Este script deve ser executado como root${NC}" 
   exit 1
fi

echo -e "${YELLOW}📋 Passo 1: Atualizando sistema...${NC}"
apt update && apt upgrade -y

echo -e "${YELLOW}📋 Passo 2: Instalando dependências...${NC}"
apt install -y python3.11 python3.11-venv python3-pip git nginx certbot python3-certbot-nginx curl redis-server

# Habilitar Redis
systemctl enable redis-server
systemctl start redis-server

echo -e "${YELLOW}📋 Passo 3: Criando usuário da aplicação...${NC}"
if ! id -u sdrapp >/dev/null 2>&1; then
    adduser sdrapp --disabled-password --gecos ""
    usermod -aG sudo sdrapp
    echo -e "${GREEN}✅ Usuário sdrapp criado${NC}"
else
    echo -e "${GREEN}✅ Usuário sdrapp já existe${NC}"
fi

echo -e "${YELLOW}📋 Passo 4: Clonando repositório...${NC}"
read -p "Digite a URL do repositório Git: " GIT_REPO

su - sdrapp -c "
cd /home/sdrapp
if [ ! -d 'sdr-ia-solarprime' ]; then
    git clone $GIT_REPO sdr-ia-solarprime
else
    cd sdr-ia-solarprime
    git pull
fi
"

echo -e "${YELLOW}📋 Passo 5: Configurando ambiente Python...${NC}"
su - sdrapp -c "
cd /home/sdrapp/sdr-ia-solarprime
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
"

echo -e "${YELLOW}📋 Passo 6: Configurando variáveis de ambiente...${NC}"
echo -e "${GREEN}Por favor, edite o arquivo .env com suas configurações:${NC}"
echo "nano /home/sdrapp/sdr-ia-solarprime/.env"
echo ""
read -p "Pressione ENTER após configurar o .env..."

echo -e "${YELLOW}📋 Passo 7: Criando serviço systemd...${NC}"
cat > /etc/systemd/system/sdr-ia.service << 'EOF'
[Unit]
Description=SDR IA SolarPrime FastAPI
After=network.target

[Service]
Type=simple
User=sdrapp
Group=sdrapp
WorkingDirectory=/home/sdrapp/sdr-ia-solarprime
Environment="PATH=/home/sdrapp/sdr-ia-solarprime/venv/bin"
Environment="PYTHONPATH=/home/sdrapp/sdr-ia-solarprime"
ExecStart=/home/sdrapp/sdr-ia-solarprime/venv/bin/uvicorn api.main:app --host 127.0.0.1 --port 8000 --workers 4
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo -e "${YELLOW}📋 Passo 8: Configurando Nginx...${NC}"
read -p "Digite seu domínio (ex: api.seusite.com): " DOMAIN

cat > /etc/nginx/sites-available/sdr-ia << EOF
upstream sdr_backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    client_max_body_size 10M;
    proxy_connect_timeout 300s;
    proxy_send_timeout 300s;
    proxy_read_timeout 300s;

    location / {
        proxy_pass http://sdr_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /health {
        proxy_pass http://sdr_backend/health;
        access_log off;
    }
}
EOF

ln -sf /etc/nginx/sites-available/sdr-ia /etc/nginx/sites-enabled/
nginx -t && systemctl restart nginx

echo -e "${YELLOW}📋 Passo 9: Iniciando aplicação...${NC}"
systemctl daemon-reload
systemctl enable sdr-ia
systemctl start sdr-ia

echo -e "${YELLOW}📋 Passo 10: Configurando SSL...${NC}"
read -p "Deseja configurar SSL agora? (s/n): " CONFIGURE_SSL

if [[ $CONFIGURE_SSL == "s" ]]; then
    certbot --nginx -d $DOMAIN -d www.$DOMAIN
fi

echo -e "${YELLOW}📋 Passo 11: Configurando firewall...${NC}"
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw --force enable

echo -e "${YELLOW}📋 Passo 12: Criando script de monitoramento...${NC}"
cat > /home/sdrapp/check_health.sh << EOF
#!/bin/bash
response=\$(curl -s -o /dev/null -w "%{http_code}" https://$DOMAIN/health)
if [ \$response -eq 200 ]; then
    echo "✅ API está saudável"
else
    echo "❌ API com problemas - Status: \$response"
    systemctl restart sdr-ia
fi
EOF

chmod +x /home/sdrapp/check_health.sh
chown sdrapp:sdrapp /home/sdrapp/check_health.sh

echo -e "${GREEN}✅ Deploy concluído com sucesso!${NC}"
echo ""
echo -e "${YELLOW}📋 Próximos passos:${NC}"
echo "1. Configure o DNS na Hostinger apontando para este servidor"
echo "2. Execute o script de configuração do webhook:"
echo "   su - sdrapp"
echo "   cd /home/sdrapp/sdr-ia-solarprime"
echo "   source venv/bin/activate"
echo "   python scripts/update_webhook_production.py"
echo ""
echo -e "${GREEN}Status da aplicação:${NC}"
systemctl status sdr-ia --no-pager

echo ""
echo -e "${GREEN}Para ver os logs:${NC}"
echo "journalctl -u sdr-ia -f"