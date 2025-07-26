#!/bin/bash
# =============================================================================
# SDR IA SolarPrime - Script de Configuração SSL/HTTPS
# =============================================================================
# Este script configura certificados SSL usando Let's Encrypt
# =============================================================================

set -e

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Funções
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Verificar se está rodando como root
if [ "$EUID" -ne 0 ]; then 
    error "Este script deve ser executado como root (use sudo)"
    exit 1
fi

# Solicitar informações
read -p "Digite o domínio (ex: api.seudominio.com.br): " DOMAIN
read -p "Digite o email para notificações SSL: " EMAIL

if [ -z "$DOMAIN" ] || [ -z "$EMAIL" ]; then
    error "Domínio e email são obrigatórios!"
    exit 1
fi

log "Configurando SSL para $DOMAIN..."

# 1. Verificar se o domínio está apontando para este servidor
log "Verificando DNS..."
SERVER_IP=$(curl -s ifconfig.me)
DOMAIN_IP=$(dig +short $DOMAIN | tail -n1)

if [ "$SERVER_IP" != "$DOMAIN_IP" ]; then
    warning "O domínio $DOMAIN está apontando para $DOMAIN_IP"
    warning "Este servidor tem IP: $SERVER_IP"
    read -p "Deseja continuar mesmo assim? (s/N): " CONTINUE
    if [ "$CONTINUE" != "s" ] && [ "$CONTINUE" != "S" ]; then
        exit 1
    fi
fi

# 2. Instalar Certbot se necessário
if ! command -v certbot &> /dev/null; then
    log "Instalando Certbot..."
    apt update
    apt install -y certbot python3-certbot-nginx
fi

# 3. Verificar configuração do Nginx
log "Verificando configuração do Nginx..."
if ! nginx -t; then
    error "Configuração do Nginx inválida! Corrija antes de continuar."
    exit 1
fi

# 4. Criar diretório para validação
mkdir -p /var/www/certbot

# 5. Obter certificado SSL
log "Obtendo certificado SSL..."
certbot certonly \
    --nginx \
    --non-interactive \
    --agree-tos \
    --email "$EMAIL" \
    -d "$DOMAIN" \
    --redirect \
    --staple-ocsp

if [ $? -eq 0 ]; then
    log "Certificado SSL obtido com sucesso!"
else
    error "Falha ao obter certificado SSL"
    exit 1
fi

# 6. Atualizar configuração do Nginx
log "Atualizando configuração do Nginx..."

# Fazer backup da configuração atual
cp /etc/nginx/sites-available/sdr-solarprime /etc/nginx/sites-available/sdr-solarprime.backup

# Adicionar configurações SSL se não existirem
if ! grep -q "ssl_certificate.*$DOMAIN" /etc/nginx/sites-available/sdr-solarprime; then
    sed -i "/listen 443 ssl http2;/a\\
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;\\
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;\\
    ssl_trusted_certificate /etc/letsencrypt/live/$DOMAIN/chain.pem;\\
    \\
    # SSL Session\\
    ssl_session_timeout 1d;\\
    ssl_session_cache shared:SSL:50m;\\
    ssl_session_tickets off;\\
    \\
    # OCSP Stapling\\
    ssl_stapling on;\\
    ssl_stapling_verify on;\\
    resolver 8.8.8.8 8.8.4.4 valid=300s;\\
    resolver_timeout 5s;" /etc/nginx/sites-available/sdr-solarprime
fi

# 7. Adicionar header HSTS
if ! grep -q "Strict-Transport-Security" /etc/nginx/sites-available/sdr-solarprime; then
    sed -i "/add_header X-Frame-Options/a\\
    add_header Strict-Transport-Security \"max-age=63072000; includeSubDomains; preload\" always;" /etc/nginx/sites-available/sdr-solarprime
fi

# 8. Testar e recarregar Nginx
log "Testando configuração do Nginx..."
if nginx -t; then
    log "Recarregando Nginx..."
    systemctl reload nginx
else
    error "Configuração do Nginx inválida após mudanças!"
    mv /etc/nginx/sites-available/sdr-solarprime.backup /etc/nginx/sites-available/sdr-solarprime
    exit 1
fi

# 9. Configurar renovação automática
log "Configurando renovação automática..."
cat > /etc/cron.d/certbot-renew <<EOF
# Renovar certificados SSL duas vezes por dia
0 */12 * * * root certbot renew --quiet --post-hook "systemctl reload nginx"
EOF

# 10. Testar renovação
log "Testando processo de renovação..."
certbot renew --dry-run

# 11. Criar script de verificação SSL
cat > /usr/local/bin/check-ssl.sh <<'EOF'
#!/bin/bash
# Verificar status do certificado SSL

DOMAIN="$1"
if [ -z "$DOMAIN" ]; then
    echo "Uso: $0 <dominio>"
    exit 1
fi

echo "Verificando SSL para $DOMAIN..."
echo ""

# Verificar data de expiração
echo "Data de expiração:"
echo | openssl s_client -servername "$DOMAIN" -connect "$DOMAIN":443 2>/dev/null | openssl x509 -noout -dates | grep notAfter

echo ""
echo "Informações do certificado:"
echo | openssl s_client -servername "$DOMAIN" -connect "$DOMAIN":443 2>/dev/null | openssl x509 -noout -subject -issuer

echo ""
echo "Verificando HTTPS:"
curl -Is "https://$DOMAIN" | head -n1
EOF

chmod +x /usr/local/bin/check-ssl.sh

# 12. Verificar SSL
log "Verificando certificado SSL..."
/usr/local/bin/check-ssl.sh "$DOMAIN"

# 13. Atualizar Evolution API webhook
log "=========================================="
log "SSL configurado com sucesso!"
log "=========================================="
echo ""
warning "IMPORTANTE: Atualize o webhook na Evolution API para:"
echo "https://$DOMAIN/webhook/whatsapp"
echo ""
log "Comandos úteis:"
echo "- Verificar SSL: /usr/local/bin/check-ssl.sh $DOMAIN"
echo "- Ver certificados: certbot certificates"
echo "- Renovar manualmente: sudo certbot renew"
echo "- Ver logs: sudo journalctl -u certbot.timer"
log "=========================================="

# Fim do script
exit 0