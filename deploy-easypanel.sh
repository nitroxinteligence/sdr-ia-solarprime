#!/bin/bash

# Script de Deploy para EasyPanel
# AGENTIC SDR - SOLAR PRIME v0.3

echo "=========================================="
echo "🚀 Deploy AGENTIC SDR - SOLAR PRIME"
echo "=========================================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar se está no branch correto
CURRENT_BRANCH=$(git branch --show-current)
echo -e "${YELLOW}📌 Branch atual: $CURRENT_BRANCH${NC}"

# Opção 1: Deploy direto do GitHub
echo ""
echo -e "${GREEN}Opção 1: Deploy direto do GitHub${NC}"
echo "No EasyPanel, configure:"
echo "  - Repository: https://github.com/nitroxinteligence/agentic-sdr-solar-prime"
echo "  - Branch: main"
echo "  - Build Type: Dockerfile"
echo ""

# Opção 2: Build e push para registry
echo -e "${GREEN}Opção 2: Build local e push para registry${NC}"
echo "Execute os comandos:"
echo ""
echo "# Build da imagem"
echo "docker build -t agentic-sdr:latest ."
echo ""
echo "# Tag para seu registry"
echo "docker tag agentic-sdr:latest your-registry.com/agentic-sdr:latest"
echo ""
echo "# Push para registry"
echo "docker push your-registry.com/agentic-sdr:latest"
echo ""

# Opção 3: Deploy via git push
echo -e "${GREEN}Opção 3: Deploy via git push (recomendado)${NC}"
echo ""
echo "1. No EasyPanel, crie um novo serviço:"
echo "   - Nome: agentic-sdr-solar-prime"
echo "   - Tipo: GitHub App"
echo "   - Repository: agentic-sdr-solar-prime"
echo "   - Branch: main"
echo ""
echo "2. Configure as variáveis de ambiente:"
cat << 'EOF'
SUPABASE_URL=sua-url-aqui
SUPABASE_KEY=sua-key-aqui
EVOLUTION_API_URL=sua-url-aqui
EVOLUTION_API_KEY=sua-key-aqui
EVOLUTION_INSTANCE_NAME=sua-instancia-aqui
KOMMO_BASE_URL=sua-url-aqui
KOMMO_LONG_LIVED_TOKEN=seu-token-aqui
KOMMO_PIPELINE_ID=11672895
GOOGLE_API_KEY=sua-key-aqui
GOOGLE_CALENDAR_ID=seu-calendario-aqui

# Configurações do Transbordo
HUMAN_INTERVENTION_PAUSE_HOURS=24
KOMMO_HUMAN_HANDOFF_STAGE_ID=90421387
KOMMO_NOT_INTERESTED_STAGE_ID=89709599
KOMMO_MEETING_SCHEDULED_STAGE_ID=89709595
KOMMO_AGENT_USER_ID=11031887

# Configurações de Agentes
ENABLE_CALENDAR_AGENT=true
ENABLE_CRM_AGENT=true
ENABLE_FOLLOWUP_AGENT=true

# Configurações de IA
PRIMARY_AI_MODEL=gemini-1.5-pro
FALLBACK_AI_MODEL=gpt-4-turbo
AI_TEMPERATURE=0.7
EOF

echo ""
echo "3. Configure os recursos:"
echo "   - Memory: 2GB"
echo "   - CPU: 1 core"
echo "   - Replicas: 1"
echo ""
echo "4. Configure o domínio:"
echo "   - Domain: seu-dominio.com"
echo "   - Port: 8000"
echo ""

# Verificar Dockerfile
if [ -f "Dockerfile" ]; then
    echo -e "${GREEN}✅ Dockerfile encontrado${NC}"
else
    echo -e "${RED}❌ Dockerfile não encontrado!${NC}"
    exit 1
fi

# Verificar requirements.txt
if [ -f "requirements.txt" ]; then
    echo -e "${GREEN}✅ requirements.txt encontrado${NC}"
else
    echo -e "${RED}❌ requirements.txt não encontrado!${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}📝 Instruções para corrigir o erro no EasyPanel:${NC}"
echo ""
echo "1. Delete o serviço 'sdr-api' atual"
echo "2. Crie um novo serviço apontando para:"
echo "   - Repo: https://github.com/nitroxinteligence/agentic-sdr-solar-prime"
echo "   - Branch: main"
echo "3. Configure todas as variáveis de ambiente"
echo "4. Clique em Deploy"
echo ""
echo -e "${GREEN}✨ Deploy preparado com sucesso!${NC}"