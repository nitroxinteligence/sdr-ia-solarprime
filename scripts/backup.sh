#!/bin/bash
# =============================================================================
# SDR IA SolarPrime - Script de Backup Automatizado
# =============================================================================
# Realiza backup completo da aplicação e dados
# =============================================================================

set -e

# Configurações
APP_DIR="/home/ubuntu/sdr-solarprime"
BACKUP_DIR="/home/ubuntu/backups"
REMOTE_BACKUP=${REMOTE_BACKUP:-""}  # Configure para backup remoto
KEEP_DAYS=7
KEEP_WEEKLY=4
KEEP_MONTHLY=3
DATE=$(date +%Y%m%d_%H%M%S)
DAY_OF_WEEK=$(date +%u)
DAY_OF_MONTH=$(date +%d)

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

# Criar diretório de backup
mkdir -p "$BACKUP_DIR"/{daily,weekly,monthly}

log "Iniciando backup do SDR IA SolarPrime..."

# 1. Backup do código da aplicação
log "Fazendo backup do código..."
tar -czf "$BACKUP_DIR/daily/app_$DATE.tar.gz" \
    -C "$APP_DIR" . \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='.git' \
    --exclude='*.pyc' \
    --exclude='logs/*.log' \
    --exclude='temp/*' || {
    error "Falha no backup do código"
    exit 1
}

# 2. Backup das variáveis de ambiente
log "Fazendo backup das configurações..."
if [ -f "$APP_DIR/.env" ]; then
    cp "$APP_DIR/.env" "$BACKUP_DIR/daily/env_$DATE"
    # Criptografar arquivo .env se openssl disponível
    if command -v openssl &> /dev/null; then
        openssl enc -aes-256-cbc -salt -in "$BACKUP_DIR/daily/env_$DATE" \
            -out "$BACKUP_DIR/daily/env_$DATE.enc" \
            -k "${BACKUP_ENCRYPTION_KEY:-defaultkey}" 2>/dev/null && \
        rm "$BACKUP_DIR/daily/env_$DATE"
    fi
fi

# 3. Backup dos logs importantes
log "Fazendo backup dos logs..."
if [ -d "/var/log/sdr-solarprime" ]; then
    tar -czf "$BACKUP_DIR/daily/logs_$DATE.tar.gz" \
        -C "/var/log/sdr-solarprime" . \
        --exclude='*.gz' || warning "Alguns logs não foram incluídos"
fi

# 4. Backup do banco de dados (Supabase export)
log "Exportando dados do Supabase..."
if [ -f "$APP_DIR/.env" ]; then
    # Extrair credenciais do Supabase
    source "$APP_DIR/.env"
    
    if [ -n "$SUPABASE_URL" ] && [ -n "$SUPABASE_SERVICE_KEY" ]; then
        # Criar script Python para export
        cat > /tmp/export_supabase.py << 'EOF'
import os
import json
from datetime import datetime
from supabase import create_client, Client

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_KEY")

if url and key:
    supabase: Client = create_client(url, key)
    
    tables = ["profiles", "conversations", "messages", "leads", "follow_ups"]
    backup_data = {}
    
    for table in tables:
        try:
            data = supabase.table(table).select("*").execute()
            backup_data[table] = data.data
            print(f"Exported {len(data.data)} records from {table}")
        except Exception as e:
            print(f"Error exporting {table}: {e}")
    
    with open(f"/tmp/supabase_export.json", "w") as f:
        json.dump(backup_data, f, indent=2, default=str)
EOF
        
        cd "$APP_DIR"
        ./venv/bin/python /tmp/export_supabase.py && \
        mv /tmp/supabase_export.json "$BACKUP_DIR/daily/supabase_$DATE.json" || \
        warning "Falha ao exportar dados do Supabase"
        
        rm -f /tmp/export_supabase.py
    fi
fi

# 5. Backup da configuração do Nginx
log "Fazendo backup das configurações do Nginx..."
if [ -f "/etc/nginx/sites-available/sdr-solarprime" ]; then
    cp "/etc/nginx/sites-available/sdr-solarprime" "$BACKUP_DIR/daily/nginx_$DATE.conf"
fi

# 6. Backup dos certificados SSL (apenas referência)
if [ -d "/etc/letsencrypt/live" ]; then
    log "Listando certificados SSL..."
    ls -la /etc/letsencrypt/live/ > "$BACKUP_DIR/daily/ssl_certs_list_$DATE.txt"
fi

# 7. Criar arquivo de metadados
cat > "$BACKUP_DIR/daily/backup_metadata_$DATE.json" << EOF
{
    "timestamp": "$(date -Iseconds)",
    "hostname": "$(hostname)",
    "app_version": "$(cd $APP_DIR && git describe --tags --always 2>/dev/null || echo 'unknown')",
    "backup_size": "$(du -sh $BACKUP_DIR/daily/*_$DATE* | awk '{sum += $1} END {print sum}')",
    "system_info": {
        "kernel": "$(uname -r)",
        "memory": "$(free -h | awk 'NR==2 {print $2}')",
        "disk": "$(df -h / | awk 'NR==2 {print $4}')"
    }
}
EOF

# 8. Criar backups semanais e mensais
if [ "$DAY_OF_WEEK" = "7" ]; then  # Domingo
    log "Criando backup semanal..."
    cp "$BACKUP_DIR/daily/app_$DATE.tar.gz" "$BACKUP_DIR/weekly/app_week_$DATE.tar.gz"
    [ -f "$BACKUP_DIR/daily/supabase_$DATE.json" ] && \
        cp "$BACKUP_DIR/daily/supabase_$DATE.json" "$BACKUP_DIR/weekly/supabase_week_$DATE.json"
fi

if [ "$DAY_OF_MONTH" = "01" ]; then
    log "Criando backup mensal..."
    cp "$BACKUP_DIR/daily/app_$DATE.tar.gz" "$BACKUP_DIR/monthly/app_month_$DATE.tar.gz"
    [ -f "$BACKUP_DIR/daily/supabase_$DATE.json" ] && \
        cp "$BACKUP_DIR/daily/supabase_$DATE.json" "$BACKUP_DIR/monthly/supabase_month_$DATE.json"
fi

# 9. Upload para backup remoto (se configurado)
if [ -n "$REMOTE_BACKUP" ]; then
    log "Enviando backup para armazenamento remoto..."
    # Exemplo com rclone (configure primeiro)
    if command -v rclone &> /dev/null; then
        rclone copy "$BACKUP_DIR/daily/" "$REMOTE_BACKUP/daily/" --include "*_$DATE*" || \
            warning "Falha no upload remoto"
    else
        warning "rclone não instalado - backup remoto não realizado"
    fi
fi

# 10. Limpeza de backups antigos
log "Limpando backups antigos..."

# Limpar diários
find "$BACKUP_DIR/daily" -name "app_*.tar.gz" -mtime +$KEEP_DAYS -delete
find "$BACKUP_DIR/daily" -name "env_*" -mtime +$KEEP_DAYS -delete
find "$BACKUP_DIR/daily" -name "logs_*.tar.gz" -mtime +$KEEP_DAYS -delete
find "$BACKUP_DIR/daily" -name "supabase_*.json" -mtime +$KEEP_DAYS -delete
find "$BACKUP_DIR/daily" -name "*.conf" -mtime +$KEEP_DAYS -delete
find "$BACKUP_DIR/daily" -name "*.txt" -mtime +$KEEP_DAYS -delete
find "$BACKUP_DIR/daily" -name "*.json" -mtime +$KEEP_DAYS -delete

# Limpar semanais
find "$BACKUP_DIR/weekly" -name "*week*.tar.gz" -mtime +$((KEEP_WEEKLY * 7)) -delete
find "$BACKUP_DIR/weekly" -name "*week*.json" -mtime +$((KEEP_WEEKLY * 7)) -delete

# Limpar mensais
find "$BACKUP_DIR/monthly" -name "*month*.tar.gz" -mtime +$((KEEP_MONTHLY * 30)) -delete
find "$BACKUP_DIR/monthly" -name "*month*.json" -mtime +$((KEEP_MONTHLY * 30)) -delete

# 11. Verificar integridade dos backups
log "Verificando integridade dos backups..."
for file in "$BACKUP_DIR/daily/"*"_$DATE"*.tar.gz; do
    if [ -f "$file" ]; then
        if tar -tzf "$file" >/dev/null 2>&1; then
            ok_files=$((ok_files + 1))
        else
            error "Arquivo corrompido: $file"
            corrupted_files=$((corrupted_files + 1))
        fi
    fi
done

# 12. Relatório final
log "=========================================="
log "Backup concluído!"
log "=========================================="
log "Data: $(date)"
log "Arquivos criados:"
ls -lh "$BACKUP_DIR/daily/"*"_$DATE"* | awk '{print "  - " $9 " (" $5 ")"}'
log "Espaço usado em backups: $(du -sh $BACKUP_DIR | cut -f1)"
log "Espaço livre no disco: $(df -h $BACKUP_DIR | awk 'NR==2 {print $4}')"

# Enviar notificação se configurado
if [ -n "$BACKUP_NOTIFICATION_URL" ]; then
    curl -s -X POST "$BACKUP_NOTIFICATION_URL" \
        -H "Content-Type: application/json" \
        -d "{\"text\": \"Backup SDR SolarPrime concluído com sucesso\", \"date\": \"$DATE\"}" \
        >/dev/null 2>&1 || true
fi

# Registrar no log
echo "$(date -Iseconds) - Backup completed successfully" >> "$BACKUP_DIR/backup.log"

exit 0