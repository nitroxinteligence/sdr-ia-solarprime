#!/bin/bash
#
# Evolution API Setup Script
# ==========================
# Script para configurar a integração com Evolution API
#

set -e

echo "🚀 Configuração da Integração Evolution API"
echo "=========================================="
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Verificar se estamos no diretório correto
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}❌ Erro: Execute este script do diretório raiz do projeto${NC}"
    exit 1
fi

# Função para verificar variáveis de ambiente
check_env_var() {
    local var_name=$1
    local var_value=${!var_name}
    
    if [ -z "$var_value" ]; then
        echo -e "${RED}❌ $var_name não está configurada${NC}"
        return 1
    else
        echo -e "${GREEN}✅ $var_name está configurada${NC}"
        return 0
    fi
}

# Função para testar conexão
test_connection() {
    local url=$1
    local api_key=$2
    
    echo -e "${BLUE}🔍 Testando conexão com Evolution API...${NC}"
    
    response=$(curl -s -w "\n%{http_code}" -X GET \
        "$url/instance/fetchInstances" \
        -H "apikey: $api_key" \
        -H "Content-Type: application/json")
    
    http_code=$(echo "$response" | tail -n 1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" -eq 200 ]; then
        echo -e "${GREEN}✅ Conexão com Evolution API estabelecida!${NC}"
        return 0
    else
        echo -e "${RED}❌ Falha na conexão. HTTP Code: $http_code${NC}"
        echo -e "${RED}Resposta: $body${NC}"
        return 1
    fi
}

# 1. Verificar arquivo .env
echo -e "${BLUE}📋 Verificando arquivo .env...${NC}"
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo -e "${YELLOW}⚠️ Arquivo .env não encontrado. Copiando de .env.example...${NC}"
        cp .env.example .env
        echo -e "${GREEN}✅ Arquivo .env criado. Por favor, configure as variáveis necessárias.${NC}"
    else
        echo -e "${RED}❌ Arquivo .env não encontrado e .env.example não está disponível.${NC}"
        exit 1
    fi
fi

# 2. Carregar variáveis de ambiente
echo -e "${BLUE}🔧 Carregando variáveis de ambiente...${NC}"
export $(grep -v '^#' .env | xargs)

# 3. Verificar variáveis Evolution API
echo ""
echo -e "${BLUE}🔍 Verificando configurações Evolution API...${NC}"

REQUIRED_VARS=(
    "EVOLUTION_API_URL"
    "EVOLUTION_API_KEY"
    "EVOLUTION_INSTANCE_NAME"
)

all_configured=true
for var in "${REQUIRED_VARS[@]}"; do
    if ! check_env_var "$var"; then
        all_configured=false
    fi
done

if [ "$all_configured" = false ]; then
    echo ""
    echo -e "${YELLOW}⚠️ Algumas variáveis não estão configuradas.${NC}"
    echo -e "${YELLOW}Por favor, edite o arquivo .env e configure:${NC}"
    echo ""
    echo "EVOLUTION_API_URL=https://sua-evolution-api.com"
    echo "EVOLUTION_API_KEY=sua-chave-api"
    echo "EVOLUTION_INSTANCE_NAME=nome-da-instancia"
    echo ""
    exit 1
fi

# 4. Instalar dependências
echo ""
echo -e "${BLUE}📦 Instalando dependências Python...${NC}"

# Verificar se pip está instalado
if ! command -v pip &> /dev/null; then
    echo -e "${RED}❌ pip não está instalado. Por favor, instale o Python 3.8+${NC}"
    exit 1
fi

# Instalar dependências
pip install -r requirements.txt

# 5. Verificar Redis
echo ""
echo -e "${BLUE}🔍 Verificando Redis...${NC}"

if command -v redis-cli &> /dev/null; then
    if redis-cli ping > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Redis está rodando${NC}"
    else
        echo -e "${YELLOW}⚠️ Redis não está rodando. Iniciando...${NC}"
        
        # Tentar iniciar Redis
        if [ "$(uname)" == "Darwin" ]; then
            # macOS
            if command -v brew &> /dev/null; then
                brew services start redis
            else
                echo -e "${RED}❌ Por favor, instale o Redis manualmente${NC}"
            fi
        elif [ -f /etc/debian_version ]; then
            # Debian/Ubuntu
            sudo systemctl start redis-server
        else
            echo -e "${RED}❌ Por favor, inicie o Redis manualmente${NC}"
        fi
    fi
else
    echo -e "${YELLOW}⚠️ Redis não está instalado${NC}"
    echo -e "${YELLOW}Para instalar:${NC}"
    echo "  macOS: brew install redis"
    echo "  Ubuntu/Debian: sudo apt-get install redis-server"
    echo ""
fi

# 6. Testar conexão com Evolution API
echo ""
if test_connection "$EVOLUTION_API_URL" "$EVOLUTION_API_KEY"; then
    # 7. Verificar instância
    echo ""
    echo -e "${BLUE}🔍 Verificando instância '$EVOLUTION_INSTANCE_NAME'...${NC}"
    
    instance_response=$(curl -s -X GET \
        "$EVOLUTION_API_URL/instance/fetchInstances/$EVOLUTION_INSTANCE_NAME" \
        -H "apikey: $EVOLUTION_API_KEY")
    
    if [[ "$instance_response" == *"\"instance\""* ]]; then
        echo -e "${GREEN}✅ Instância encontrada!${NC}"
        
        # Verificar status da conexão
        connection_response=$(curl -s -X GET \
            "$EVOLUTION_API_URL/instance/connectionState/$EVOLUTION_INSTANCE_NAME" \
            -H "apikey: $EVOLUTION_API_KEY")
        
        if [[ "$connection_response" == *"\"state\":\"open\""* ]]; then
            echo -e "${GREEN}✅ WhatsApp está conectado!${NC}"
        else
            echo -e "${YELLOW}⚠️ WhatsApp não está conectado. Acesse o QR Code para conectar.${NC}"
            echo -e "${BLUE}URL para QR Code: $EVOLUTION_API_URL/instance/qrcode/$EVOLUTION_INSTANCE_NAME${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️ Instância não encontrada. Deseja criar? (s/n)${NC}"
        read -r create_instance
        
        if [ "$create_instance" = "s" ] || [ "$create_instance" = "S" ]; then
            echo -e "${BLUE}Criando instância...${NC}"
            
            create_response=$(curl -s -X POST \
                "$EVOLUTION_API_URL/instance/create" \
                -H "apikey: $EVOLUTION_API_KEY" \
                -H "Content-Type: application/json" \
                -d "{
                    \"instanceName\": \"$EVOLUTION_INSTANCE_NAME\",
                    \"qrcode\": true,
                    \"integration\": \"WHATSAPP-BAILEYS\"
                }")
            
            if [[ "$create_response" == *"\"instance\""* ]]; then
                echo -e "${GREEN}✅ Instância criada com sucesso!${NC}"
                echo -e "${BLUE}Acesse o QR Code para conectar o WhatsApp${NC}"
            else
                echo -e "${RED}❌ Erro ao criar instância: $create_response${NC}"
            fi
        fi
    fi
fi

# 8. Criar diretórios necessários
echo ""
echo -e "${BLUE}📁 Criando diretórios necessários...${NC}"

directories=("logs" "temp" "media" "reports")
for dir in "${directories[@]}"; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        echo -e "${GREEN}✅ Diretório '$dir' criado${NC}"
    else
        echo -e "${BLUE}📁 Diretório '$dir' já existe${NC}"
    fi
done

# 9. Configurar webhook
echo ""
echo -e "${BLUE}🔗 Configurando webhook...${NC}"

if [ -n "$WEBHOOK_BASE_URL" ]; then
    echo -e "${GREEN}✅ WEBHOOK_BASE_URL está configurado: $WEBHOOK_BASE_URL${NC}"
    echo -e "${BLUE}O webhook será configurado automaticamente quando a aplicação iniciar${NC}"
else
    echo -e "${YELLOW}⚠️ WEBHOOK_BASE_URL não está configurado${NC}"
    echo -e "${YELLOW}Configure no .env para receber mensagens do WhatsApp${NC}"
fi

# 10. Resumo final
echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}✅ Configuração concluída!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo -e "${BLUE}📋 Próximos passos:${NC}"
echo ""
echo "1. Se o WhatsApp não está conectado:"
echo "   - Execute: python -m api.main"
echo "   - Acesse: http://localhost:8000/instance/qrcode"
echo "   - Escaneie o QR Code com seu WhatsApp"
echo ""
echo "2. Para iniciar a aplicação:"
echo "   uvicorn api.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "3. Para executar testes:"
echo "   ./scripts/run_tests.sh"
echo ""
echo "4. Para monitorar a conexão:"
echo "   Acesse: http://localhost:8000/instance/status"
echo ""
echo -e "${GREEN}Boa sorte! 🚀${NC}"