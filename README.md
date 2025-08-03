# 🤖 SDR IA SolarPrime v0.2 - AGENTIC SDR

Sistema Inteligente de Vendas com AGENTIC SDR - Totalmente configurável via arquivo `.env`

## 🚀 Features Principais

### ✅ Controle Total via .env
Configure todo o comportamento do sistema sem alterar código:

- **Agentes**: Habilite/desabilite agentes especializados individualmente
- **Timing**: Configure tempos de digitação e resposta para humanização
- **Funcionalidades**: Ative/desative recursos específicos
- **IA**: Configure modelos, temperatura e parâmetros de geração

### 🤖 AGENTIC SDR
Agente principal ultra-humanizado com:
- Análise contextual inteligente
- Personalidade adaptativa
- Multimodal (imagens, áudio, documentos)
- Memory persistente
- Decision engine inteligente

### 👥 SDR Team
Time de agentes especializados:
- **QualificationAgent**: Qualifica leads e calcula scores
- **CalendarAgent**: Agenda reuniões e gerencia calendário
- **FollowUpAgent**: Nurturing e reengajamento
- **KnowledgeAgent**: Busca informações e documentos
- **CRMAgent**: Integração com Kommo CRM
- **BillAnalyzerAgent**: Análise de contas de luz

### 📊 Sistema de Logs com Emojis
Debug visual com emojis categorizados para facilitar o monitoramento:
- 🤖 AGENTIC SDR
- 👥 SDR Teams
- 🗄️ Supabase
- 📨 Evolution API
- 🚀 Sistema

## 📦 Instalação

### 1. Clone o repositório
```bash
git clone https://github.com/nitroxinteligence/sdr-ia-solarprime.git
cd sdr-ia-solarprime
git checkout productionv1
```

### 2. Instale as dependências
```bash
pip install -r requirements.txt
```

### 3. Configure o ambiente
```bash
cp .env.example .env
# Edite o .env com suas chaves e configurações
```

### 4. Configure as credenciais do Google (se usar Calendar)
```bash
mkdir credentials
# Adicione seus arquivos de credenciais na pasta credentials/
```

### 5. Execute o sistema
```bash
python main.py
```

## ⚙️ Configurações Disponíveis

### Controle de Agentes
```env
ENABLE_QUALIFICATION_AGENT=true
ENABLE_CALENDAR_AGENT=true
ENABLE_FOLLOWUP_AGENT=true
ENABLE_KNOWLEDGE_AGENT=true
ENABLE_CRM_AGENT=true
ENABLE_BILL_ANALYZER_AGENT=true
```

### Timing e Humanização
```env
# Tempos de digitação (segundos)
TYPING_DURATION_SHORT=2
TYPING_DURATION_MEDIUM=4
TYPING_DURATION_LONG=7

# Delays de resposta (segundos)
RESPONSE_DELAY_MIN=1
RESPONSE_DELAY_MAX=5
RESPONSE_DELAY_THINKING=8

# Comportamento humano
SIMULATE_READING_TIME=true
READING_SPEED_WPM=200
RESPONSE_TIME_VARIATION=0.3
```

### Funcionalidades
```env
ENABLE_CONTEXT_ANALYSIS=true
ENABLE_SENTIMENT_ANALYSIS=true
ENABLE_EMOTIONAL_TRIGGERS=true
ENABLE_LEAD_SCORING=true
ENABLE_MULTIMODAL_ANALYSIS=true
```

### IA e Modelos
```env
PRIMARY_AI_MODEL=gemini-2.5-pro
FALLBACK_AI_MODEL=o1-mini
ENABLE_MODEL_FALLBACK=true
AI_TEMPERATURE=0.7
AI_MAX_TOKENS=4096
```

## 🐳 Deploy com Docker

### Desenvolvimento
```bash
docker-compose up -d
```

### Produção (EasyPanel)
```bash
# Use o arquivo easypanel.yml para deploy no EasyPanel
cd prod
# Siga as instruções em PRODUCTION_DEPLOY_GUIDE.md
```

## 📚 Documentação

- [Guia de Implementação](docs/README_IMPLEMENTATION.md)
- [Guia do Teams](docs/README_TEAMS.md)
- [Deploy em Produção](docs/PRODUCTION_DEPLOY_GUIDE.md)
- [Integração Google Calendar](docs/GOOGLE_CALENDAR_IMPLEMENTATION.md)

## 🔧 Tecnologias

- **Python 3.11+**
- **AGnO Framework** - Agentes inteligentes
- **Supabase** - Banco de dados e autenticação
- **Evolution API** - WhatsApp
- **Redis** - Cache e rate limiting
- **Docker** - Containerização

## 📝 Licença

MIT

## 👥 Contribuindo

Contribuições são bem-vindas! Por favor, abra uma issue ou pull request.

## 📞 Suporte

Para suporte, abra uma issue no GitHub.

---

**SDR IA SolarPrime v0.2** - Sistema Inteligente de Vendas com AGENTIC SDR