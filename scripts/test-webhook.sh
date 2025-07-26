#!/bin/bash
# =============================================================================
# SDR IA SolarPrime - Script de Teste de Webhook
# =============================================================================
# Testa o webhook enviando diferentes tipos de eventos
# =============================================================================

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configurações
WEBHOOK_URL=${WEBHOOK_URL:-"http://localhost:8000/webhook/whatsapp"}
INSTANCE_NAME=${INSTANCE_NAME:-"Teste-Agente"}

# Funções
log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

send_webhook() {
    local event_type="$1"
    local payload="$2"
    local description="$3"
    
    echo -e "\n${YELLOW}Teste: $description${NC}"
    log "Enviando evento $event_type..."
    
    response=$(curl -s -w "\n%{http_code}" -X POST "$WEBHOOK_URL" \
        -H "Content-Type: application/json" \
        -d "$payload" 2>/dev/null)
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" = "200" ]; then
        log "✅ Sucesso (HTTP $http_code)"
        echo "Resposta: $body"
    else
        error "Falha (HTTP $http_code)"
        echo "Resposta: $body"
    fi
}

# Banner
echo "=========================================="
echo "   SDR IA SolarPrime - Teste de Webhook"
echo "   URL: $WEBHOOK_URL"
echo "=========================================="

# 1. Teste de Conexão Básica
info "Verificando conectividade..."
# Webhook só aceita POST, então testar com POST vazio
if curl -X POST -f -s "$WEBHOOK_URL" -H "Content-Type: application/json" -d '{}' >/dev/null 2>&1; then
    log "✅ Webhook acessível"
else
    warning "Webhook pode estar offline ou retornando erro - continuando testes..."
fi

# 2. Teste de Nova Mensagem (MESSAGES_UPSERT)
payload_message=$(cat <<EOF
{
    "event": "MESSAGES_UPSERT",
    "instance": "$INSTANCE_NAME",
    "data": {
        "key": {
            "id": "MSG$(date +%s)",
            "remoteJid": "5511999999999@s.whatsapp.net",
            "fromMe": false
        },
        "message": {
            "conversation": "Olá! Gostaria de saber sobre energia solar"
        },
        "messageTimestamp": $(date +%s),
        "pushName": "João Silva",
        "broadcast": false,
        "participant": null,
        "messageType": "conversation"
    }
}
EOF
)

send_webhook "MESSAGES_UPSERT" "$payload_message" "Nova mensagem de texto"

sleep 2

# 3. Teste de Atualização de Status (MESSAGES_UPDATE)
payload_status=$(cat <<EOF
{
    "event": "MESSAGES_UPDATE",
    "instance": "$INSTANCE_NAME",
    "data": {
        "key": {
            "id": "MSG$(date +%s)",
            "remoteJid": "5511999999999@s.whatsapp.net",
            "fromMe": true
        },
        "update": {
            "status": 3,
            "statusDescription": "READ"
        }
    }
}
EOF
)

send_webhook "MESSAGES_UPDATE" "$payload_status" "Atualização de status de mensagem"

sleep 2

# 4. Teste de Mudança de Conexão (CONNECTION_UPDATE)
payload_connection=$(cat <<EOF
{
    "event": "CONNECTION_UPDATE",
    "instance": "$INSTANCE_NAME",
    "data": {
        "state": "open",
        "statusReason": 200,
        "statusDescription": "Connected"
    }
}
EOF
)

send_webhook "CONNECTION_UPDATE" "$payload_connection" "Atualização de conexão (conectado)"

sleep 2

# 5. Teste de Presença (PRESENCE_UPDATE)
payload_presence=$(cat <<EOF
{
    "event": "PRESENCE_UPDATE",
    "instance": "$INSTANCE_NAME",
    "data": {
        "id": "5511999999999@s.whatsapp.net",
        "presences": {
            "5511999999999@s.whatsapp.net": {
                "lastKnownPresence": "available",
                "lastSeen": null
            }
        }
    }
}
EOF
)

send_webhook "PRESENCE_UPDATE" "$payload_presence" "Atualização de presença (online)"

sleep 2

# 6. Teste de Mensagem com Mídia
payload_media=$(cat <<EOF
{
    "event": "MESSAGES_UPSERT",
    "instance": "$INSTANCE_NAME",
    "data": {
        "key": {
            "id": "MSG_MEDIA_$(date +%s)",
            "remoteJid": "5511999999999@s.whatsapp.net",
            "fromMe": false
        },
        "message": {
            "imageMessage": {
                "url": "https://example.com/conta-de-luz.jpg",
                "mimetype": "image/jpeg",
                "caption": "Minha conta de luz",
                "fileLength": "123456",
                "height": 1024,
                "width": 768
            }
        },
        "messageTimestamp": $(date +%s),
        "pushName": "Maria Santos",
        "messageType": "imageMessage"
    }
}
EOF
)

send_webhook "MESSAGES_UPSERT" "$payload_media" "Mensagem com imagem (conta de luz)"

sleep 2

# 7. Teste de Localização
payload_location=$(cat <<EOF
{
    "event": "MESSAGES_UPSERT",
    "instance": "$INSTANCE_NAME",
    "data": {
        "key": {
            "id": "MSG_LOC_$(date +%s)",
            "remoteJid": "5511999999999@s.whatsapp.net",
            "fromMe": false
        },
        "message": {
            "locationMessage": {
                "degreesLatitude": -23.550520,
                "degreesLongitude": -46.633308,
                "name": "Minha Casa",
                "address": "São Paulo, SP"
            }
        },
        "messageTimestamp": $(date +%s),
        "pushName": "Pedro Costa",
        "messageType": "locationMessage"
    }
}
EOF
)

send_webhook "MESSAGES_UPSERT" "$payload_location" "Mensagem com localização"

sleep 2

# 8. Teste de Evento Desconhecido
payload_unknown=$(cat <<EOF
{
    "event": "UNKNOWN_EVENT",
    "instance": "$INSTANCE_NAME",
    "data": {
        "test": true
    }
}
EOF
)

send_webhook "UNKNOWN_EVENT" "$payload_unknown" "Evento desconhecido (deve ser processado sem erro)"

# Resumo
echo -e "\n${GREEN}=========================================="
echo "   Testes concluídos!"
echo "==========================================${NC}"
echo ""
info "Verifique os logs da aplicação para confirmar o processamento"
info "Logs: tail -f /var/log/sdr-solarprime/app.log"
echo ""
info "Para testar com webhook real da Evolution API:"
echo "1. Configure o webhook na interface do Evolution Manager"
echo "2. Envie uma mensagem real pelo WhatsApp"
echo "3. Monitore os logs em tempo real"

exit 0