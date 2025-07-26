#!/bin/bash
# =============================================================================
# SDR IA SolarPrime - Script de Monitoramento Completo
# =============================================================================
# Monitora saúde do sistema, performance e disponibilidade
# =============================================================================

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configurações
SERVICE_NAME="sdr-solarprime"
API_URL="http://localhost:8000"
LOG_DIR="/var/log/sdr-solarprime"
ALERT_EMAIL=${ALERT_EMAIL:-"admin@seudominio.com.br"}
ALERT_WHATSAPP=${ALERT_WHATSAPP:-""}

# Funções auxiliares
ok() {
    echo -e "${GREEN}✓${NC} $1"
}

warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

error() {
    echo -e "${RED}✗${NC} $1"
}

info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

metric() {
    echo -e "${CYAN}📊${NC} $1"
}

send_alert() {
    local subject="$1"
    local message="$2"
    local severity="${3:-warning}"
    
    # Log do alerta
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] ALERT [$severity]: $subject - $message" >> "$LOG_DIR/alerts.log"
    
    # Enviar email se configurado
    if [ -n "$ALERT_EMAIL" ] && command -v mail &> /dev/null; then
        echo "$message" | mail -s "[SDR Alert] $subject" "$ALERT_EMAIL"
    fi
    
    # TODO: Implementar envio via WhatsApp se configurado
}

# Header
echo "=========================================="
echo "   SDR IA SolarPrime - Monitor v1.0"
echo "   $(date +'%Y-%m-%d %H:%M:%S')"
echo "=========================================="
echo ""

# 1. Status dos Serviços
echo -e "${CYAN}[SERVIÇOS]${NC}"

# Verificar serviço principal
if systemctl is-active --quiet "$SERVICE_NAME"; then
    ok "SDR SolarPrime está ativo"
    uptime=$(systemctl show "$SERVICE_NAME" -p ActiveEnterTimestamp --value)
    info "Ativo desde: $uptime"
else
    error "SDR SolarPrime está inativo"
    send_alert "Serviço Inativo" "O serviço $SERVICE_NAME está parado!" "critical"
fi

# Verificar Nginx
if systemctl is-active --quiet nginx; then
    ok "Nginx está ativo"
else
    error "Nginx está inativo"
fi

# Verificar Redis (se configurado)
if systemctl is-active --quiet redis-server; then
    ok "Redis está ativo"
    redis_memory=$(redis-cli info memory | grep used_memory_human | cut -d: -f2 | tr -d '\r')
    metric "Memória Redis: $redis_memory"
fi

echo ""

# 2. Verificação da API
echo -e "${CYAN}[API HEALTH]${NC}"

# Health check básico
health_response=$(curl -s -w "\n%{http_code}" "$API_URL/health" 2>/dev/null)
http_code=$(echo "$health_response" | tail -n1)
health_body=$(echo "$health_response" | head -n-1)

if [ "$http_code" = "200" ]; then
    ok "API respondendo (HTTP $http_code)"
else
    error "API não está respondendo (HTTP $http_code)"
    send_alert "API Down" "A API não está respondendo. HTTP: $http_code" "critical"
fi

# Verificar conexão com Evolution API
evolution_status=$(curl -s "$API_URL/webhook/status" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if data.get('config', {}).get('evolution_api_configured'):
        print('configured')
    else:
        print('not_configured')
except:
    print('error')
" 2>/dev/null)

if [ "$evolution_status" = "configured" ]; then
    ok "Evolution API configurada"
else
    warning "Evolution API não configurada ou com erro"
fi

echo ""

# 3. Recursos do Sistema
echo -e "${CYAN}[RECURSOS DO SISTEMA]${NC}"

# CPU
cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
cpu_int=${cpu_usage%.*}
if [ "$cpu_int" -lt 80 ]; then
    ok "CPU: ${cpu_usage}%"
else
    warning "CPU alta: ${cpu_usage}%"
    send_alert "CPU Alta" "Uso de CPU está em ${cpu_usage}%"
fi

# Memória
mem_info=$(free -m | awk 'NR==2')
mem_total=$(echo "$mem_info" | awk '{print $2}')
mem_used=$(echo "$mem_info" | awk '{print $3}')
mem_percent=$((mem_used * 100 / mem_total))

if [ "$mem_percent" -lt 80 ]; then
    ok "Memória: ${mem_percent}% (${mem_used}MB/${mem_total}MB)"
else
    warning "Memória alta: ${mem_percent}% (${mem_used}MB/${mem_total}MB)"
    send_alert "Memória Alta" "Uso de memória está em ${mem_percent}%"
fi

# Disco
disk_usage=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$disk_usage" -lt 80 ]; then
    ok "Disco: ${disk_usage}%"
else
    warning "Disco alto: ${disk_usage}%"
    send_alert "Disco Cheio" "Uso de disco está em ${disk_usage}%" "critical"
fi

# Load Average
load_avg=$(uptime | awk -F'load average:' '{print $2}')
ok "Load Average:$load_avg"

echo ""

# 4. Análise de Logs
echo -e "${CYAN}[ANÁLISE DE LOGS]${NC}"

if [ -d "$LOG_DIR" ]; then
    # Erros nas últimas 24h
    errors_24h=$(find "$LOG_DIR" -name "*.log" -mtime -1 -exec grep -i "error" {} \; 2>/dev/null | wc -l)
    if [ "$errors_24h" -gt 100 ]; then
        warning "Muitos erros nas últimas 24h: $errors_24h"
    else
        info "Erros nas últimas 24h: $errors_24h"
    fi
    
    # Warnings nas últimas 24h
    warnings_24h=$(find "$LOG_DIR" -name "*.log" -mtime -1 -exec grep -i "warning" {} \; 2>/dev/null | wc -l)
    info "Avisos nas últimas 24h: $warnings_24h"
    
    # Tamanho dos logs
    log_size=$(du -sh "$LOG_DIR" 2>/dev/null | cut -f1)
    metric "Tamanho total dos logs: $log_size"
else
    warning "Diretório de logs não encontrado"
fi

echo ""

# 5. Conectividade Externa
echo -e "${CYAN}[CONECTIVIDADE]${NC}"

# Verificar DNS
if ping -c 1 -W 2 8.8.8.8 >/dev/null 2>&1; then
    ok "Conectividade com internet OK"
else
    error "Sem conectividade com internet"
    send_alert "Sem Internet" "Sistema sem acesso à internet" "critical"
fi

# Verificar Evolution API (se URL configurada)
if [ -f ".env" ]; then
    evo_url=$(grep EVOLUTION_API_URL .env | cut -d'=' -f2 | tr -d '"' | tr -d "'")
    if [ -n "$evo_url" ]; then
        if curl -s -f -m 5 "$evo_url" >/dev/null 2>&1; then
            ok "Evolution API acessível"
        else
            warning "Evolution API inacessível"
        fi
    fi
fi

echo ""

# 6. Performance da Aplicação
echo -e "${CYAN}[PERFORMANCE]${NC}"

# Tempo de resposta da API
start_time=$(date +%s%N)
curl -s "$API_URL/health" >/dev/null 2>&1
end_time=$(date +%s%N)
response_time=$(( (end_time - start_time) / 1000000 ))

if [ "$response_time" -lt 1000 ]; then
    ok "Tempo de resposta: ${response_time}ms"
else
    warning "Tempo de resposta alto: ${response_time}ms"
fi

# Processos da aplicação
app_processes=$(pgrep -f "uvicorn.*sdr" | wc -l)
metric "Processos da aplicação: $app_processes"

# Conexões ativas
active_connections=$(ss -tunp 2>/dev/null | grep :8000 | wc -l)
metric "Conexões ativas na porta 8000: $active_connections"

echo ""

# 7. Segurança
echo -e "${CYAN}[SEGURANÇA]${NC}"

# Verificar certificado SSL (se configurado)
if [ -d "/etc/letsencrypt/live" ]; then
    for cert in /etc/letsencrypt/live/*/cert.pem; do
        if [ -f "$cert" ]; then
            domain=$(basename $(dirname "$cert"))
            expiry=$(openssl x509 -enddate -noout -in "$cert" | cut -d= -f2)
            expiry_epoch=$(date -d "$expiry" +%s)
            current_epoch=$(date +%s)
            days_left=$(( (expiry_epoch - current_epoch) / 86400 ))
            
            if [ "$days_left" -gt 30 ]; then
                ok "SSL $domain expira em $days_left dias"
            elif [ "$days_left" -gt 7 ]; then
                warning "SSL $domain expira em $days_left dias"
            else
                error "SSL $domain expira em $days_left dias!"
                send_alert "SSL Expirando" "Certificado SSL de $domain expira em $days_left dias" "critical"
            fi
        fi
    done
else
    info "Certificados SSL não configurados"
fi

# Verificar fail2ban
if systemctl is-active --quiet fail2ban; then
    banned_ips=$(fail2ban-client status sshd 2>/dev/null | grep "Currently banned" | cut -d: -f2 | tr -d ' ')
    ok "Fail2ban ativo (IPs banidos: ${banned_ips:-0})"
else
    warning "Fail2ban não está ativo"
fi

echo ""

# 8. Resumo e Recomendações
echo -e "${CYAN}[RESUMO]${NC}"

# Calcular score de saúde
health_score=100
[ "$http_code" != "200" ] && health_score=$((health_score - 30))
[ "$cpu_int" -gt 80 ] && health_score=$((health_score - 10))
[ "$mem_percent" -gt 80 ] && health_score=$((health_score - 10))
[ "$disk_usage" -gt 80 ] && health_score=$((health_score - 20))
[ "$errors_24h" -gt 100 ] && health_score=$((health_score - 15))

if [ "$health_score" -ge 90 ]; then
    echo -e "${GREEN}Sistema saudável (Score: $health_score/100)${NC}"
elif [ "$health_score" -ge 70 ]; then
    echo -e "${YELLOW}Sistema com avisos (Score: $health_score/100)${NC}"
else
    echo -e "${RED}Sistema com problemas (Score: $health_score/100)${NC}"
fi

# Recomendações
if [ "$health_score" -lt 90 ]; then
    echo ""
    echo -e "${CYAN}[RECOMENDAÇÕES]${NC}"
    [ "$cpu_int" -gt 80 ] && info "• Verificar processos consumindo CPU"
    [ "$mem_percent" -gt 80 ] && info "• Considerar aumentar memória ou otimizar aplicação"
    [ "$disk_usage" -gt 80 ] && info "• Limpar logs antigos ou aumentar espaço em disco"
    [ "$errors_24h" -gt 100 ] && info "• Analisar logs de erro para identificar problemas"
fi

echo ""
echo "=========================================="
echo "Monitoramento concluído: $(date +'%H:%M:%S')"
echo "=========================================="

# Salvar resultado em arquivo para histórico
{
    echo "$(date +'%Y-%m-%d %H:%M:%S'),${health_score},${cpu_usage},${mem_percent},${disk_usage},${response_time},${errors_24h}"
} >> "$LOG_DIR/monitoring-history.csv"

exit 0