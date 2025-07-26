# 🚀 Deploy SDR IA SolarPrime na Hostinger VPS

## 📋 Pré-requisitos

- **Hostinger VPS** com Ubuntu 22.04 LTS
- **Acesso SSH** ao servidor
- **Domínio** apontando para o IP do VPS
- **Python 3.11** instalado

## 🔧 Passo a Passo Completo

### 1️⃣ Acesse seu VPS Hostinger

```bash
# Conecte via SSH
ssh root@SEU_IP_HOSTINGER
```

### 2️⃣ Prepare o Servidor

```bash
# Atualize o sistema
apt update && apt upgrade -y

# Instale dependências essenciais
apt install -y python3.11 python3.11-venv python3-pip git nginx certbot python3-certbot-nginx curl

# Instale Redis (para cache)
apt install -y redis-server
systemctl enable redis-server
systemctl start redis-server

# Crie usuário para a aplicação (segurança)
adduser sdrapp --disabled-password --gecos ""
usermod -aG sudo sdrapp
```

### 3️⃣ Clone e Configure o Projeto

```bash
# Como usuário sdrapp
su - sdrapp

# Clone o repositório
cd /home/sdrapp
git clone https://github.com/seu-usuario/sdr-ia-solarprime.git
cd sdr-ia-solarprime

# Crie ambiente virtual
python3.11 -m venv venv
source venv/bin/activate

# Instale dependências
pip install --upgrade pip
pip install -r requirements.txt
```

### 4️⃣ Configure Variáveis de Ambiente

```bash
# Crie arquivo .env
nano .env
```

Adicione suas configurações:
```env
# Configurações de Produção Hostinger
ENVIRONMENT=production
DEBUG=False

# Gemini AI
GEMINI_API_KEY=sua_chave_aqui

# Evolution API
EVOLUTION_API_URL=https://evoapi-evolution-api.fzvgou.easypanel.host
EVOLUTION_API_KEY=336B531BEA18-41AE-B5E9-ADC8BE525431
EVOLUTION_INSTANCE_NAME=Teste-Agente

# Supabase
SUPABASE_URL=https://rcjcpwqezmlhenmhrski.supabase.co
SUPABASE_ANON_KEY=sua_chave_aqui
SUPABASE_SERVICE_KEY=sua_chave_aqui

# Redis (local)
REDIS_URL=redis://localhost:6379/0

# Webhook - IMPORTANTE: Será atualizado após configurar domínio
WEBHOOK_BASE_URL=https://seudominio.com
```

### 5️⃣ Configure o Systemd Service

```bash
# Volte para root
exit

# Crie o service
nano /etc/systemd/system/sdr-ia.service
```

```ini
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
```

### 6️⃣ Configure o Nginx

```bash
# Crie configuração do site
nano /etc/nginx/sites-available/sdr-ia
```

```nginx
upstream sdr_backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name seudominio.com www.seudominio.com;

    # Tamanho máximo para upload (imagens de contas)
    client_max_body_size 10M;

    # Timeouts para webhook
    proxy_connect_timeout 300s;
    proxy_send_timeout 300s;
    proxy_read_timeout 300s;

    location / {
        proxy_pass http://sdr_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://sdr_backend/health;
        access_log off;
    }
}
```

```bash
# Ative o site
ln -s /etc/nginx/sites-available/sdr-ia /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

### 7️⃣ Configure SSL com Let's Encrypt

```bash
# Obtenha certificado SSL
certbot --nginx -d seudominio.com -d www.seudominio.com

# Escolha opção 2 para redirecionar HTTP para HTTPS
```

### 8️⃣ Configure DNS na Hostinger

1. Acesse o painel da Hostinger
2. Vá em **Domínios** → **DNS/Nameservers**
3. Adicione os registros:
   - **Tipo A**: `@` → IP do seu VPS
   - **Tipo A**: `www` → IP do seu VPS
   - **Tipo A**: `api` → IP do seu VPS (opcional)

### 9️⃣ Inicie a Aplicação

```bash
# Inicie e habilite o serviço
systemctl daemon-reload
systemctl enable sdr-ia
systemctl start sdr-ia

# Verifique status
systemctl status sdr-ia

# Veja logs em tempo real
journalctl -u sdr-ia -f
```

### 🔟 Configure o Webhook na Evolution API

```bash
# Como usuário sdrapp
su - sdrapp
cd /home/sdrapp/sdr-ia-solarprime
source venv/bin/activate

# Execute o script de configuração
python scripts/update_webhook_production.py
```

Quando solicitado, digite: `https://seudominio.com`

## 🔒 Segurança Adicional

### Firewall (UFW)

```bash
# Configure firewall
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw allow 6379/tcp  # Redis (apenas local)
ufw --force enable
```

### Fail2ban (Proteção contra ataques)

```bash
# Instale fail2ban
apt install -y fail2ban

# Configure para Nginx
nano /etc/fail2ban/jail.local
```

```ini
[DEFAULT]
bantime = 1h
findtime = 10m
maxretry = 5

[nginx-limit-req]
enabled = true
```

### Monitoramento

```bash
# Instale htop para monitorar recursos
apt install -y htop

# Configure logs rotation
nano /etc/logrotate.d/sdr-ia
```

```
/home/sdrapp/sdr-ia-solarprime/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0640 sdrapp sdrapp
    sharedscripts
    postrotate
        systemctl reload sdr-ia > /dev/null
    endscript
}
```

## 📊 Monitoramento e Manutenção

### Comandos Úteis

```bash
# Ver logs da aplicação
journalctl -u sdr-ia -f

# Ver logs do Nginx
tail -f /var/log/nginx/error.log

# Reiniciar aplicação
systemctl restart sdr-ia

# Ver status do Redis
redis-cli ping

# Monitorar recursos
htop

# Ver espaço em disco
df -h
```

### Script de Health Check

```bash
# Crie script de monitoramento
nano /home/sdrapp/check_health.sh
```

```bash
#!/bin/bash
response=$(curl -s -o /dev/null -w "%{http_code}" https://seudominio.com/health)
if [ $response -eq 200 ]; then
    echo "✅ API está saudável"
else
    echo "❌ API com problemas - Status: $response"
    systemctl restart sdr-ia
fi
```

```bash
chmod +x /home/sdrapp/check_health.sh

# Adicione ao cron (a cada 5 minutos)
crontab -e
*/5 * * * * /home/sdrapp/check_health.sh
```

## 🚀 Deploy de Atualizações

```bash
# Script de deploy
nano /home/sdrapp/deploy.sh
```

```bash
#!/bin/bash
cd /home/sdrapp/sdr-ia-solarprime
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart sdr-ia
echo "✅ Deploy concluído!"
```

```bash
chmod +x /home/sdrapp/deploy.sh
```

## ⚡ Performance e Otimização

### 1. Configure Swap (se VPS tem pouca RAM)

```bash
# Crie swap de 2GB
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab
```

### 2. Otimize Nginx

```bash
# Edite nginx.conf
nano /etc/nginx/nginx.conf
```

Adicione/ajuste:
```nginx
worker_processes auto;
worker_connections 1024;
keepalive_timeout 65;
gzip on;
gzip_types text/plain application/json;
```

### 3. Configure Limites do Sistema

```bash
# Aumente limites de arquivos abertos
echo "sdrapp soft nofile 65536" >> /etc/security/limits.conf
echo "sdrapp hard nofile 65536" >> /etc/security/limits.conf
```

## 🎯 Troubleshooting

### Problema: Webhook não recebe mensagens
```bash
# Verifique se a URL está correta
curl https://seudominio.com/webhook/whatsapp
# Deve retornar {"detail":"Method Not Allowed"}

# Verifique logs
journalctl -u sdr-ia -f | grep webhook
```

### Problema: Erro 502 Bad Gateway
```bash
# Verifique se o serviço está rodando
systemctl status sdr-ia

# Verifique se está escutando na porta
netstat -tlnp | grep 8000
```

### Problema: SSL não funciona
```bash
# Renove certificado
certbot renew --dry-run
certbot renew
```

## ✅ Checklist Final

- [ ] VPS configurado e atualizado
- [ ] Python 3.11 e dependências instaladas
- [ ] Projeto clonado e configurado
- [ ] Variáveis de ambiente definidas
- [ ] Systemd service funcionando
- [ ] Nginx configurado e rodando
- [ ] SSL instalado e funcionando
- [ ] DNS configurado na Hostinger
- [ ] Webhook configurado na Evolution API
- [ ] Firewall ativado
- [ ] Monitoramento configurado
- [ ] Backup automático (opcional)

## 🎉 Pronto!

Seu SDR IA SolarPrime está rodando em produção na Hostinger! 

Acesse `https://seudominio.com/health` para verificar o status.

Envie uma mensagem no WhatsApp para testar!