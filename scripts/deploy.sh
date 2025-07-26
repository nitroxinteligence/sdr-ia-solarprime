#!/bin/bash
# =============================================================================
# SDR IA SolarPrime - Script de Deploy para Produção
# =============================================================================
# Este script automatiza o processo de deploy no Hostinger VPS
# Requisitos: Ubuntu 22.04, Python 3.10+, Git, Nginx
# =============================================================================

set -e  # Parar em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configurações
APP_DIR="/home/ubuntu/sdr-solarprime"
VENV_DIR="$APP_DIR/venv"
SERVICE_NAME="sdr-solarprime"
NGINX_SITE="sdr-solarprime"
BACKUP_DIR="/home/ubuntu/backups"

# Função para log
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Verificar se está rodando como usuário correto
if [ "$USER" != "ubuntu" ]; then
    error "Este script deve ser executado como usuário 'ubuntu'"
    exit 1
fi

# 1. Criar backup antes do deploy
log "Criando backup pré-deploy..."
mkdir -p "$BACKUP_DIR"
BACKUP_FILE="$BACKUP_DIR/backup-$(date +'%Y%m%d-%H%M%S').tar.gz"
tar -czf "$BACKUP_FILE" -C "$APP_DIR" . --exclude='venv' --exclude='__pycache__' --exclude='.git' || true

# 2. Atualizar código do repositório
log "Atualizando código do repositório..."
cd "$APP_DIR"
git fetch origin
git reset --hard origin/main

# 3. Verificar e copiar arquivo de ambiente
if [ ! -f ".env" ]; then
    if [ -f ".env.production" ]; then
        log "Copiando .env.production para .env..."
        cp .env.production .env
    else
        error "Arquivo .env não encontrado! Configure as variáveis de ambiente primeiro."
        exit 1
    fi
fi

# 4. Ativar ambiente virtual e instalar dependências
log "Ativando ambiente virtual e instalando dependências..."
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install -r requirements.txt

# 5. Executar migrações do banco de dados (se aplicável)
if [ -d "alembic" ]; then
    log "Executando migrações do banco de dados..."
    alembic upgrade head || warning "Falha nas migrações - verifique manualmente"
fi

# 6. Coletar arquivos estáticos (se aplicável)
if [ -d "static" ]; then
    log "Coletando arquivos estáticos..."
    python -m api.collect_static || true
fi

# 7. Testar a aplicação
log "Testando a aplicação..."
python -c "from api.main import app; print('✓ Aplicação carregada com sucesso')" || {
    error "Falha ao carregar aplicação"
    exit 1
}

# 8. Reiniciar serviços
log "Reiniciando serviços..."
sudo systemctl daemon-reload
sudo systemctl restart "$SERVICE_NAME"
sudo systemctl restart nginx

# 9. Verificar status dos serviços
log "Verificando status dos serviços..."
sleep 3

if systemctl is-active --quiet "$SERVICE_NAME"; then
    log "✓ Serviço $SERVICE_NAME está ativo"
else
    error "Serviço $SERVICE_NAME falhou ao iniciar"
    sudo journalctl -u "$SERVICE_NAME" -n 50
    exit 1
fi

if systemctl is-active --quiet nginx; then
    log "✓ Nginx está ativo"
else
    error "Nginx falhou ao iniciar"
    exit 1
fi

# 10. Verificar saúde da aplicação
log "Verificando saúde da aplicação..."
sleep 2

HEALTH_CHECK=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health || echo "000")
if [ "$HEALTH_CHECK" = "200" ]; then
    log "✓ Aplicação respondendo corretamente"
else
    warning "Health check retornou código: $HEALTH_CHECK"
fi

# 11. Verificar webhook
WEBHOOK_STATUS=$(curl -s http://localhost:8000/webhook/status | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', 'unknown'))" 2>/dev/null || echo "error")
if [ "$WEBHOOK_STATUS" = "active" ]; then
    log "✓ Webhook está ativo"
else
    warning "Status do webhook: $WEBHOOK_STATUS"
fi

# 12. Limpar caches e arquivos temporários
log "Limpando arquivos temporários..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

# 13. Configurar rotação de logs
log "Configurando rotação de logs..."
sudo tee /etc/logrotate.d/sdr-solarprime > /dev/null <<EOF
/var/log/sdr-solarprime/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 ubuntu ubuntu
    sharedscripts
    postrotate
        systemctl reload sdr-solarprime > /dev/null 2>&1 || true
    endscript
}
EOF

# 14. Configurar monitoramento básico
log "Configurando monitoramento..."
cat > ~/check_sdr.sh <<'SCRIPT'
#!/bin/bash
# Script de verificação rápida
SERVICE="sdr-solarprime"
URL="http://localhost:8000/health"

if ! systemctl is-active --quiet "$SERVICE"; then
    echo "ERRO: Serviço $SERVICE não está rodando"
    exit 1
fi

if ! curl -f -s "$URL" > /dev/null; then
    echo "ERRO: Aplicação não está respondendo"
    exit 1
fi

echo "OK: Sistema funcionando normalmente"
SCRIPT

chmod +x ~/check_sdr.sh

# 15. Exibir resumo do deploy
log "========================================"
log "Deploy concluído com sucesso!"
log "========================================"
log "Serviço: $SERVICE_NAME"
log "Diretório: $APP_DIR"
log "Backup salvo em: $BACKUP_FILE"
log "Para verificar logs: sudo journalctl -u $SERVICE_NAME -f"
log "Para verificar status: sudo systemctl status $SERVICE_NAME"
log "Para teste rápido: ~/check_sdr.sh"
log "========================================"

# Fim do script
exit 0