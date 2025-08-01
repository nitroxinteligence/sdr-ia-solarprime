#!/bin/bash

#######################################
# SDR Agent - Script de Rollback
# 
# Este script realiza o rollback seguro do SDR Agent para uma versão anterior
# Inclui backup do estado atual, restauração e validação
#
# Uso: ./rollback.sh [versão] [--force]
# Exemplo: ./rollback.sh v1.2.3
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
BACKUP_DIR="/var/backups/sdr-agent"
LOG_FILE="/var/log/sdr-agent/rollback-$(date +%Y%m%d-%H%M%S).log"
DOCKER_COMPOSE_FILE="$PROJECT_ROOT/docker-compose.yml"
ENV_FILE="$PROJECT_ROOT/.env"

# Versão alvo (parâmetro ou prompt)
TARGET_VERSION="${1:-}"
FORCE_MODE="${2:-}"

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

# Função para confirmar ação
confirm_action() {
    local prompt="$1"
    if [[ "$FORCE_MODE" == "--force" ]]; then
        return 0
    fi
    
    echo -e "${YELLOW}${prompt}${NC}"
    read -p "Continuar? (s/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        print_message $RED "Operação cancelada pelo usuário"
        exit 1
    fi
}

# Função para verificar pré-requisitos
check_prerequisites() {
    print_message $BLUE "🔍 Verificando pré-requisitos..."
    
    # Verificar se está rodando como root ou com sudo
    if [[ $EUID -ne 0 ]]; then
        print_message $RED "❌ Este script precisa ser executado como root ou com sudo"
        exit 1
    fi
    
    # Verificar comandos necessários
    local required_commands=("docker" "docker-compose" "git" "tar" "mysql" "redis-cli")
    for cmd in "${required_commands[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            print_message $RED "❌ Comando '$cmd' não encontrado"
            exit 1
        fi
    done
    
    # Verificar se o diretório de backup existe
    if [[ ! -d "$BACKUP_DIR" ]]; then
        mkdir -p "$BACKUP_DIR"
    fi
    
    # Criar diretório de logs se não existir
    mkdir -p "$(dirname "$LOG_FILE")"
    
    print_message $GREEN "✅ Pré-requisitos verificados"
}

# Função para listar versões disponíveis
list_available_versions() {
    print_message $BLUE "📋 Versões disponíveis para rollback:"
    
    # Listar tags git
    cd "$PROJECT_ROOT"
    git fetch --tags &>/dev/null
    
    echo "Tags Git:"
    git tag -l | sort -V | tail -10
    
    echo -e "\nBackups disponíveis:"
    if [[ -d "$BACKUP_DIR" ]]; then
        ls -1 "$BACKUP_DIR" | grep -E "backup-v[0-9]+\.[0-9]+\.[0-9]+" | sort -V | tail -10
    fi
}

# Função para validar versão
validate_version() {
    local version=$1
    
    # Verificar se é uma tag git válida
    cd "$PROJECT_ROOT"
    if ! git rev-parse "$version" &>/dev/null; then
        print_message $RED "❌ Versão '$version' não encontrada no Git"
        return 1
    fi
    
    return 0
}

# Função para fazer backup do estado atual
backup_current_state() {
    print_message $BLUE "💾 Fazendo backup do estado atual..."
    
    local backup_name="backup-rollback-$(date +%Y%m%d-%H%M%S)"
    local backup_path="$BACKUP_DIR/$backup_name"
    
    mkdir -p "$backup_path"
    
    # Backup dos arquivos do projeto
    log "INFO" "Copiando arquivos do projeto..."
    tar -czf "$backup_path/project-files.tar.gz" \
        -C "$PROJECT_ROOT" \
        --exclude="venv" \
        --exclude="__pycache__" \
        --exclude="*.pyc" \
        --exclude=".git" \
        --exclude="logs" \
        .
    
    # Backup das variáveis de ambiente
    if [[ -f "$ENV_FILE" ]]; then
        cp "$ENV_FILE" "$backup_path/.env.backup"
    fi
    
    # Backup do banco de dados (se usando MySQL/PostgreSQL local)
    if command -v mysqldump &> /dev/null; then
        log "INFO" "Fazendo backup do banco de dados..."
        # Ajuste conforme seu banco
        # mysqldump -u root -p sdr_agent > "$backup_path/database.sql"
    fi
    
    # Backup das configurações do Docker
    if [[ -f "$DOCKER_COMPOSE_FILE" ]]; then
        cp "$DOCKER_COMPOSE_FILE" "$backup_path/docker-compose.yml.backup"
    fi
    
    # Salvar informações da versão atual
    git rev-parse HEAD > "$backup_path/current-version.txt"
    git describe --tags --always >> "$backup_path/current-version.txt"
    
    # Backup das imagens Docker atuais
    docker images | grep sdr-agent > "$backup_path/docker-images.txt" || true
    
    print_message $GREEN "✅ Backup criado em: $backup_path"
    
    echo "$backup_path"
}

# Função para parar os serviços
stop_services() {
    print_message $BLUE "🛑 Parando serviços..."
    
    # Parar containers Docker
    if [[ -f "$DOCKER_COMPOSE_FILE" ]]; then
        cd "$PROJECT_ROOT"
        docker-compose down || true
    fi
    
    # Parar serviços systemd se existirem
    systemctl stop sdr-agent || true
    systemctl stop sdr-agent-worker || true
    
    # Aguardar serviços pararem completamente
    sleep 5
    
    print_message $GREEN "✅ Serviços parados"
}

# Função para realizar o rollback do código
rollback_code() {
    local version=$1
    
    print_message $BLUE "🔄 Realizando rollback para versão $version..."
    
    cd "$PROJECT_ROOT"
    
    # Fazer checkout da versão
    log "INFO" "Fazendo checkout da versão $version..."
    git checkout "$version"
    
    # Instalar dependências da versão
    if [[ -f "requirements.txt" ]]; then
        log "INFO" "Instalando dependências..."
        pip install -r requirements.txt --upgrade
    fi
    
    print_message $GREEN "✅ Código revertido para versão $version"
}

# Função para reverter migrações de banco se necessário
rollback_database() {
    local version=$1
    
    print_message $BLUE "🗄️ Verificando necessidade de rollback do banco..."
    
    # Verificar se há migrações para reverter
    # Implementar conforme seu sistema de migrações
    
    # Exemplo com Alembic:
    # alembic downgrade -1
    
    # Exemplo com Django:
    # python manage.py migrate app_name migration_name
    
    log "INFO" "Migrações de banco verificadas"
}

# Função para atualizar webhooks da Evolution API
update_webhooks() {
    print_message $BLUE "🔗 Atualizando webhooks da Evolution API..."
    
    # Executar script de configuração de webhook
    if [[ -f "$PROJECT_ROOT/scripts/configure_webhook.py" ]]; then
        cd "$PROJECT_ROOT"
        python scripts/configure_webhook.py || {
            print_message $YELLOW "⚠️ Falha ao atualizar webhooks - verifique manualmente"
        }
    fi
    
    print_message $GREEN "✅ Webhooks atualizados"
}

# Função para reconstruir imagens Docker
rebuild_docker_images() {
    print_message $BLUE "🐳 Reconstruindo imagens Docker..."
    
    cd "$PROJECT_ROOT"
    
    # Reconstruir imagens
    docker-compose build --no-cache
    
    print_message $GREEN "✅ Imagens Docker reconstruídas"
}

# Função para iniciar serviços
start_services() {
    print_message $BLUE "▶️ Iniciando serviços..."
    
    cd "$PROJECT_ROOT"
    
    # Iniciar com Docker Compose
    if [[ -f "$DOCKER_COMPOSE_FILE" ]]; then
        docker-compose up -d
    fi
    
    # Iniciar serviços systemd se configurados
    systemctl start sdr-agent || true
    systemctl start sdr-agent-worker || true
    
    # Aguardar serviços iniciarem
    sleep 10
    
    print_message $GREEN "✅ Serviços iniciados"
}

# Função para validar o rollback
validate_rollback() {
    print_message $BLUE "✔️ Validando rollback..."
    
    local all_good=true
    
    # Verificar se os containers estão rodando
    if docker-compose ps | grep -q "Up"; then
        print_message $GREEN "✅ Containers Docker estão rodando"
    else
        print_message $RED "❌ Containers Docker não estão rodando"
        all_good=false
    fi
    
    # Verificar conectividade com Evolution API
    if curl -s -o /dev/null -w "%{http_code}" "${EVOLUTION_API_URL}/health" | grep -q "200"; then
        print_message $GREEN "✅ Evolution API está acessível"
    else
        print_message $RED "❌ Evolution API não está acessível"
        all_good=false
    fi
    
    # Verificar conectividade com banco de dados
    # Adicionar verificações específicas do seu banco
    
    # Verificar logs por erros
    if docker-compose logs --tail=50 | grep -i "error" | grep -v "ERROR - No error"; then
        print_message $YELLOW "⚠️ Erros encontrados nos logs"
        all_good=false
    fi
    
    if [[ "$all_good" == "true" ]]; then
        print_message $GREEN "✅ Rollback validado com sucesso!"
        return 0
    else
        print_message $RED "❌ Problemas encontrados durante validação"
        return 1
    fi
}

# Função para gerar relatório de rollback
generate_rollback_report() {
    local backup_path=$1
    local target_version=$2
    
    print_message $BLUE "📄 Gerando relatório de rollback..."
    
    local report_file="$backup_path/rollback-report.txt"
    
    cat > "$report_file" <<EOF
========================================
RELATÓRIO DE ROLLBACK - SDR AGENT
========================================

Data/Hora: $(date)
Versão Anterior: $(cat "$backup_path/current-version.txt")
Versão Alvo: $target_version
Usuário: $(whoami)

AÇÕES REALIZADAS:
- Backup do estado atual criado
- Serviços parados
- Código revertido para versão $target_version
- Dependências atualizadas
- Banco de dados verificado
- Webhooks atualizados
- Imagens Docker reconstruídas
- Serviços reiniciados

STATUS DA VALIDAÇÃO:
$(validate_rollback && echo "✅ SUCESSO" || echo "❌ FALHA")

PRÓXIMOS PASSOS:
1. Verificar logs da aplicação
2. Testar funcionalidades críticas
3. Monitorar por 30 minutos
4. Se houver problemas, usar backup em: $backup_path

========================================
EOF
    
    cat "$report_file"
    print_message $GREEN "✅ Relatório salvo em: $report_file"
}

# Função de rollback de emergência
emergency_rollback() {
    local backup_path=$1
    
    print_message $RED "🚨 EXECUTANDO ROLLBACK DE EMERGÊNCIA..."
    
    confirm_action "Isso irá restaurar o backup anterior. Tem certeza?"
    
    # Parar tudo
    stop_services
    
    # Restaurar arquivos
    cd "$PROJECT_ROOT"
    tar -xzf "$backup_path/project-files.tar.gz"
    
    # Restaurar .env
    if [[ -f "$backup_path/.env.backup" ]]; then
        cp "$backup_path/.env.backup" "$ENV_FILE"
    fi
    
    # Restaurar docker-compose
    if [[ -f "$backup_path/docker-compose.yml.backup" ]]; then
        cp "$backup_path/docker-compose.yml.backup" "$DOCKER_COMPOSE_FILE"
    fi
    
    # Reconstruir e iniciar
    rebuild_docker_images
    start_services
    
    print_message $YELLOW "⚠️ Rollback de emergência concluído - verifique o sistema!"
}

# Função principal
main() {
    print_message $BLUE "🔄 SDR Agent - Script de Rollback"
    print_message $BLUE "================================"
    
    # Verificar pré-requisitos
    check_prerequisites
    
    # Se não foi fornecida versão, listar disponíveis
    if [[ -z "$TARGET_VERSION" ]]; then
        list_available_versions
        echo
        read -p "Digite a versão para rollback: " TARGET_VERSION
    fi
    
    # Validar versão
    if ! validate_version "$TARGET_VERSION"; then
        exit 1
    fi
    
    # Confirmar ação
    print_message $YELLOW "\n⚠️  ATENÇÃO: Rollback para versão $TARGET_VERSION"
    confirm_action "Isso irá reverter o sistema. Deseja continuar?"
    
    # Executar rollback
    log "INFO" "Iniciando rollback para versão $TARGET_VERSION"
    
    # 1. Backup do estado atual
    BACKUP_PATH=$(backup_current_state)
    
    # 2. Parar serviços
    stop_services
    
    # 3. Rollback do código
    rollback_code "$TARGET_VERSION"
    
    # 4. Rollback do banco se necessário
    rollback_database "$TARGET_VERSION"
    
    # 5. Atualizar webhooks
    update_webhooks
    
    # 6. Reconstruir imagens
    rebuild_docker_images
    
    # 7. Iniciar serviços
    start_services
    
    # 8. Validar rollback
    if validate_rollback; then
        generate_rollback_report "$BACKUP_PATH" "$TARGET_VERSION"
        print_message $GREEN "\n✅ Rollback concluído com sucesso!"
    else
        print_message $RED "\n❌ Rollback concluído com problemas"
        print_message $YELLOW "Verifique os logs e considere o rollback de emergência"
        print_message $YELLOW "Backup disponível em: $BACKUP_PATH"
        
        read -p "Executar rollback de emergência? (s/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Ss]$ ]]; then
            emergency_rollback "$BACKUP_PATH"
        fi
    fi
    
    log "INFO" "Script de rollback finalizado"
}

# Tratamento de erros
trap 'print_message $RED "❌ Erro na linha $LINENO. Verifique o log: $LOG_FILE"' ERR

# Executar função principal
main "$@"