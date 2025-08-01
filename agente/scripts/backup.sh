#!/bin/bash

#######################################
# SDR Agent - Script de Backup Automático
# 
# Este script realiza backup completo do sistema SDR Agent incluindo:
# - Banco de dados Supabase
# - Configurações e variáveis de ambiente
# - Logs de conversação
# - Arquivos do sistema
# 
# Pode ser agendado via cron para execução automática
# Mantém últimos 30 dias de backups
#
# Uso: ./backup.sh [--full] [--database-only] [--config-only]
# Cron: 0 2 * * * /path/to/backup.sh >> /var/log/sdr-backup.log 2>&1
#######################################

set -euo pipefail

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configurações
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_ROOT="/var/backups/sdr-agent"
BACKUP_DIR="$BACKUP_ROOT/$(date +%Y%m%d-%H%M%S)"
LOG_FILE="/var/log/sdr-agent/backup-$(date +%Y%m%d).log"
RETENTION_DAYS=30

# Carregar variáveis de ambiente
if [[ -f "$PROJECT_ROOT/.env" ]]; then
    export $(grep -v '^#' "$PROJECT_ROOT/.env" | xargs)
fi

# Modo de backup (padrão: full)
BACKUP_MODE="${1:---full}"

# Função de logging
log() {
    local level=$1
    shift
    local message="$@"
    echo -e "[$(date +'%Y-%m-%d %H:%M:%S')] [$level] $message" | tee -a "$LOG_FILE"
}

# Função para exibir mensagens coloridas
print_message() {
    local color=$1
    shift
    echo -e "${color}$@${NC}"
}

# Função para verificar espaço em disco
check_disk_space() {
    local required_gb=5  # Requer pelo menos 5GB livres
    local available_gb=$(df -BG "$BACKUP_ROOT" | awk 'NR==2 {print $4}' | sed 's/G//')
    
    if [[ $available_gb -lt $required_gb ]]; then
        log "ERROR" "Espaço insuficiente em disco. Disponível: ${available_gb}GB, Necessário: ${required_gb}GB"
        return 1
    fi
    
    log "INFO" "Espaço em disco OK: ${available_gb}GB disponíveis"
    return 0
}

# Função para criar estrutura de diretórios
create_backup_structure() {
    log "INFO" "Criando estrutura de backup em $BACKUP_DIR"
    
    mkdir -p "$BACKUP_DIR"/{database,config,logs,files,scripts,conversations}
    
    # Criar arquivo de metadados
    cat > "$BACKUP_DIR/metadata.json" <<EOF
{
    "backup_date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "backup_type": "$BACKUP_MODE",
    "project_root": "$PROJECT_ROOT",
    "hostname": "$(hostname)",
    "user": "$(whoami)",
    "version": "$(cd $PROJECT_ROOT && git describe --tags --always 2>/dev/null || echo 'unknown')"
}
EOF
}

# Função para backup do banco de dados Supabase
backup_database() {
    log "INFO" "Iniciando backup do banco de dados Supabase..."
    
    if [[ -z "${SUPABASE_URL:-}" ]] || [[ -z "${SUPABASE_SERVICE_KEY:-}" ]]; then
        log "WARNING" "Credenciais do Supabase não encontradas. Pulando backup do banco."
        return
    fi
    
    # Extrair informações de conexão
    SUPABASE_PROJECT=$(echo "$SUPABASE_URL" | sed -n 's/https:\/\/\([^.]*\).*/\1/p')
    
    # Criar script Python para export via Supabase
    cat > "$BACKUP_DIR/database/export_supabase.py" <<'PYTHON_SCRIPT'
import os
import json
import asyncio
from datetime import datetime
from supabase import create_client, Client

async def export_data():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")
    
    supabase: Client = create_client(url, key)
    
    tables = [
        "profiles",
        "conversations", 
        "messages",
        "leads",
        "follow_ups",
        "knowledge_base",
        "agent_sessions"
    ]
    
    backup_data = {
        "export_date": datetime.utcnow().isoformat(),
        "tables": {}
    }
    
    for table in tables:
        print(f"Exportando tabela {table}...")
        try:
            # Buscar todos os registros
            response = supabase.table(table).select("*").execute()
            backup_data["tables"][table] = {
                "count": len(response.data),
                "data": response.data
            }
            print(f"  - {len(response.data)} registros exportados")
        except Exception as e:
            print(f"  - Erro ao exportar {table}: {e}")
            backup_data["tables"][table] = {
                "count": 0,
                "data": [],
                "error": str(e)
            }
    
    # Salvar backup
    with open("supabase_backup.json", "w", encoding="utf-8") as f:
        json.dump(backup_data, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"Backup concluído: supabase_backup.json")

if __name__ == "__main__":
    asyncio.run(export_data())
PYTHON_SCRIPT
    
    # Executar export
    cd "$BACKUP_DIR/database"
    python export_supabase.py || {
        log "ERROR" "Falha ao exportar dados do Supabase"
        return 1
    }
    
    # Comprimir backup
    gzip supabase_backup.json
    
    # Remover script temporário
    rm export_supabase.py
    
    log "INFO" "Backup do banco de dados concluído"
}

# Função para backup de configurações
backup_config() {
    log "INFO" "Fazendo backup das configurações..."
    
    # Copiar arquivos de configuração
    if [[ -f "$PROJECT_ROOT/.env" ]]; then
        cp "$PROJECT_ROOT/.env" "$BACKUP_DIR/config/.env"
        # Mascarar informações sensíveis
        sed -i 's/\(.*KEY=\).*/\1[MASKED]/' "$BACKUP_DIR/config/.env"
        sed -i 's/\(.*TOKEN=\).*/\1[MASKED]/' "$BACKUP_DIR/config/.env"
        sed -i 's/\(.*PASSWORD=\).*/\1[MASKED]/' "$BACKUP_DIR/config/.env"
    fi
    
    # Copiar outras configurações
    for config_file in \
        "docker-compose.yml" \
        "docker-compose.production.yml" \
        "nginx/sdr-solarprime.conf" \
        "agente/core/config.py"
    do
        if [[ -f "$PROJECT_ROOT/$config_file" ]]; then
            mkdir -p "$BACKUP_DIR/config/$(dirname "$config_file")"
            cp "$PROJECT_ROOT/$config_file" "$BACKUP_DIR/config/$config_file"
        fi
    done
    
    # Salvar informações do sistema
    cat > "$BACKUP_DIR/config/system_info.txt" <<EOF
Sistema: $(uname -a)
Docker: $(docker --version 2>/dev/null || echo "Não instalado")
Docker Compose: $(docker-compose --version 2>/dev/null || echo "Não instalado")
Python: $(python3 --version 2>/dev/null || echo "Não instalado")
Node.js: $(node --version 2>/dev/null || echo "Não instalado")
Redis: $(redis-cli --version 2>/dev/null || echo "Não instalado")

Containers em execução:
$(docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "Nenhum")

Uso de disco:
$(df -h)

Memória:
$(free -h 2>/dev/null || echo "Comando não disponível")
EOF
    
    log "INFO" "Backup de configurações concluído"
}

# Função para backup de logs
backup_logs() {
    log "INFO" "Fazendo backup dos logs..."
    
    # Diretórios de logs
    log_dirs=(
        "/var/log/sdr-agent"
        "$PROJECT_ROOT/logs"
        "$PROJECT_ROOT/agente/logs"
    )
    
    for log_dir in "${log_dirs[@]}"; do
        if [[ -d "$log_dir" ]]; then
            log "INFO" "Copiando logs de $log_dir"
            
            # Copiar apenas logs recentes (últimos 7 dias)
            find "$log_dir" -name "*.log" -mtime -7 -exec cp {} "$BACKUP_DIR/logs/" \; 2>/dev/null || true
        fi
    done
    
    # Logs do Docker
    if command -v docker &> /dev/null; then
        log "INFO" "Exportando logs do Docker..."
        
        # Listar containers do projeto
        containers=$(docker ps -a --filter "name=sdr" --format "{{.Names}}" 2>/dev/null || true)
        
        for container in $containers; do
            docker logs "$container" --tail 1000 > "$BACKUP_DIR/logs/docker-${container}.log" 2>&1 || true
        done
    fi
    
    # Comprimir logs
    cd "$BACKUP_DIR/logs"
    for log_file in *.log; do
        [[ -f "$log_file" ]] && gzip "$log_file"
    done
    
    log "INFO" "Backup de logs concluído"
}

# Função para backup de conversações
backup_conversations() {
    log "INFO" "Fazendo backup de conversações recentes..."
    
    # Script Python para exportar conversas dos últimos 7 dias
    cat > "$BACKUP_DIR/conversations/export_conversations.py" <<'PYTHON_SCRIPT'
import os
import json
import asyncio
from datetime import datetime, timedelta, timezone
from supabase import create_client, Client

async def export_recent_conversations():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")
    
    if not url or not key:
        print("Credenciais Supabase não encontradas")
        return
    
    supabase: Client = create_client(url, key)
    
    # Data limite (7 dias atrás)
    since = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    
    print(f"Exportando conversações desde {since}...")
    
    try:
        # Buscar conversações recentes
        conversations = supabase.table("conversations")\
            .select("*")\
            .gte("updated_at", since)\
            .execute()
        
        print(f"Encontradas {len(conversations.data)} conversações")
        
        # Para cada conversação, buscar mensagens
        export_data = {
            "export_date": datetime.now(timezone.utc).isoformat(),
            "since": since,
            "conversations": []
        }
        
        for conv in conversations.data:
            conv_id = conv["id"]
            
            # Buscar mensagens da conversação
            messages = supabase.table("messages")\
                .select("*")\
                .eq("conversation_id", conv_id)\
                .order("created_at")\
                .execute()
            
            # Buscar lead associado
            lead = None
            if conv.get("phone"):
                lead_result = supabase.table("leads")\
                    .select("*")\
                    .eq("phone", conv["phone"])\
                    .execute()
                if lead_result.data:
                    lead = lead_result.data[0]
            
            export_data["conversations"].append({
                "conversation": conv,
                "messages": messages.data,
                "lead": lead,
                "message_count": len(messages.data)
            })
        
        # Salvar export
        with open("conversations_backup.json", "w", encoding="utf-8") as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"Backup concluído: conversations_backup.json")
        
        # Estatísticas
        total_messages = sum(c["message_count"] for c in export_data["conversations"])
        print(f"Total: {len(export_data['conversations'])} conversações, {total_messages} mensagens")
        
    except Exception as e:
        print(f"Erro ao exportar conversações: {e}")

if __name__ == "__main__":
    asyncio.run(export_recent_conversations())
PYTHON_SCRIPT
    
    # Executar export
    cd "$BACKUP_DIR/conversations"
    python export_conversations.py || {
        log "WARNING" "Falha ao exportar conversações"
    }
    
    # Comprimir se existir
    if [[ -f "conversations_backup.json" ]]; then
        gzip conversations_backup.json
    fi
    
    # Remover script temporário
    rm export_conversations.py
    
    log "INFO" "Backup de conversações concluído"
}

# Função para backup de arquivos do projeto
backup_files() {
    log "INFO" "Fazendo backup dos arquivos do projeto..."
    
    # Criar arquivo tar com exclusões
    cd "$PROJECT_ROOT"
    
    tar -czf "$BACKUP_DIR/files/project_files.tar.gz" \
        --exclude="venv" \
        --exclude="__pycache__" \
        --exclude="*.pyc" \
        --exclude=".git" \
        --exclude="node_modules" \
        --exclude="temp" \
        --exclude="*.log" \
        --exclude="dump.rdb" \
        agente/ \
        scripts/ \
        tools/ \
        services/ \
        || {
            log "WARNING" "Alguns arquivos não puderam ser incluídos no backup"
        }
    
    log "INFO" "Backup de arquivos concluído"
}

# Função para backup de scripts customizados
backup_scripts() {
    log "INFO" "Fazendo backup de scripts customizados..."
    
    # Copiar scripts importantes
    scripts_to_backup=(
        "scripts/*.sh"
        "scripts/*.py"
        "agente/scripts/*.sh"
        "agente/scripts/*.py"
    )
    
    for pattern in "${scripts_to_backup[@]}"; do
        for script in $PROJECT_ROOT/$pattern; do
            if [[ -f "$script" ]]; then
                cp "$script" "$BACKUP_DIR/scripts/" 2>/dev/null || true
            fi
        done
    done
    
    log "INFO" "Backup de scripts concluído"
}

# Função para comprimir backup final
compress_backup() {
    log "INFO" "Comprimindo backup..."
    
    cd "$BACKUP_ROOT"
    backup_name="$(basename "$BACKUP_DIR")"
    
    # Criar arquivo tar.gz
    tar -czf "${backup_name}.tar.gz" "$backup_name/"
    
    # Calcular checksum
    sha256sum "${backup_name}.tar.gz" > "${backup_name}.tar.gz.sha256"
    
    # Remover diretório não comprimido
    rm -rf "$backup_name"
    
    # Tamanho final
    size=$(du -h "${backup_name}.tar.gz" | cut -f1)
    log "INFO" "Backup comprimido: ${backup_name}.tar.gz ($size)"
}

# Função para limpar backups antigos
cleanup_old_backups() {
    log "INFO" "Limpando backups antigos (mais de $RETENTION_DAYS dias)..."
    
    # Encontrar e remover backups antigos
    find "$BACKUP_ROOT" -name "*.tar.gz" -mtime +$RETENTION_DAYS -exec rm {} \; 2>/dev/null || true
    find "$BACKUP_ROOT" -name "*.sha256" -mtime +$RETENTION_DAYS -exec rm {} \; 2>/dev/null || true
    
    # Contar backups restantes
    backup_count=$(find "$BACKUP_ROOT" -name "*.tar.gz" | wc -l)
    log "INFO" "Backups mantidos: $backup_count"
}

# Função para enviar notificação (opcional)
send_notification() {
    local status=$1
    local message=$2
    
    # Se tiver webhook configurado
    if [[ -n "${BACKUP_WEBHOOK_URL:-}" ]]; then
        curl -X POST "$BACKUP_WEBHOOK_URL" \
            -H "Content-Type: application/json" \
            -d "{\"status\":\"$status\",\"message\":\"$message\",\"timestamp\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}" \
            2>/dev/null || true
    fi
    
    # Se tiver email configurado
    if [[ -n "${BACKUP_EMAIL:-}" ]] && command -v mail &> /dev/null; then
        echo "$message" | mail -s "SDR Agent Backup - $status" "$BACKUP_EMAIL" 2>/dev/null || true
    fi
}

# Função para gerar relatório
generate_report() {
    local backup_file="$1"
    
    cat > "$BACKUP_ROOT/last_backup_report.txt" <<EOF
SDR Agent - Relatório de Backup
================================

Data/Hora: $(date)
Arquivo: $backup_file
Tamanho: $(du -h "$BACKUP_ROOT/$backup_file" | cut -f1)
Checksum: $(cat "$BACKUP_ROOT/${backup_file}.sha256" | cut -d' ' -f1)

Componentes incluídos:
$(case $BACKUP_MODE in
    --full) echo "✓ Banco de dados
✓ Configurações
✓ Logs
✓ Conversações
✓ Arquivos do projeto
✓ Scripts" ;;
    --database-only) echo "✓ Banco de dados" ;;
    --config-only) echo "✓ Configurações" ;;
esac)

Backups disponíveis: $(find "$BACKUP_ROOT" -name "*.tar.gz" | wc -l)
Espaço usado: $(du -sh "$BACKUP_ROOT" | cut -f1)
Espaço livre: $(df -h "$BACKUP_ROOT" | awk 'NR==2 {print $4}')

================================
EOF
    
    cat "$BACKUP_ROOT/last_backup_report.txt"
}

# Função principal
main() {
    print_message $BLUE "🔄 SDR Agent - Backup Automático"
    print_message $BLUE "================================"
    
    # Criar diretórios necessários
    mkdir -p "$BACKUP_ROOT"
    mkdir -p "$(dirname "$LOG_FILE")"
    
    # Verificar espaço em disco
    if ! check_disk_space; then
        send_notification "ERROR" "Backup falhou: espaço em disco insuficiente"
        exit 1
    fi
    
    # Criar estrutura de backup
    create_backup_structure
    
    # Executar backups conforme modo selecionado
    case $BACKUP_MODE in
        --full)
            backup_database
            backup_config
            backup_logs
            backup_conversations
            backup_files
            backup_scripts
            ;;
        --database-only)
            backup_database
            ;;
        --config-only)
            backup_config
            ;;
        *)
            log "ERROR" "Modo de backup inválido: $BACKUP_MODE"
            exit 1
            ;;
    esac
    
    # Comprimir backup
    compress_backup
    
    # Limpar backups antigos
    cleanup_old_backups
    
    # Nome do arquivo final
    backup_filename="$(basename "$BACKUP_DIR").tar.gz"
    
    # Gerar relatório
    generate_report "$backup_filename"
    
    # Notificar sucesso
    send_notification "SUCCESS" "Backup concluído: $backup_filename"
    
    print_message $GREEN "✅ Backup concluído com sucesso!"
    print_message $GREEN "Arquivo: $BACKUP_ROOT/$backup_filename"
    
    log "INFO" "Backup finalizado com sucesso"
}

# Tratamento de erros
trap 'log "ERROR" "Erro na linha $LINENO. Backup interrompido."; send_notification "ERROR" "Backup falhou na linha $LINENO"' ERR

# Executar função principal
main "$@"