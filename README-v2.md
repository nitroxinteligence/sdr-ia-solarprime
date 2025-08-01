# 🤖 SDR IA SolarPrime

Sistema inteligente de vendas (SDR) para energia solar que automatiza a qualificação de leads e agendamento de reuniões via WhatsApp, desenvolvido com AGnO Framework e Google Gemini 2.5 Pro.

## 🚀 Visão Geral

O **SDR IA SolarPrime** é um agente de vendas virtual que:
- 💬 Conversa naturalmente via WhatsApp
- 📸 Analisa fotos de contas de luz automaticamente
- 🎯 Qualifica leads através de conversação inteligente
- 📅 Agenda reuniões com consultores
- 🧠 Mantém contexto e memória das conversas

## 🛠️ Tecnologias

- **Backend**: FastAPI + Uvicorn
- **IA**: AGnO Framework + Google Gemini 2.5 Pro
- **WhatsApp**: Evolution API v2
- **Banco de Dados**: Supabase (PostgreSQL)
- **Cache**: Redis
- **Deploy**: Docker + Easypanel/Railway

## 📋 Pré-requisitos

- Python 3.11+
- Redis (opcional, com fallback)
- Conta Google Cloud (para Gemini API)
- Evolution API configurada
- Supabase configurado

## 🔧 Instalação

1. **Clone o repositório**
```bash
git clone https://github.com/seu-usuario/sdr-ia-solarprime.git
cd sdr-ia-solarprime
```

2. **Crie o ambiente virtual**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. **Instale as dependências**
```bash
pip install -r requirements.txt
```

4. **Configure as variáveis de ambiente**
```bash
cp .env.example .env
# Edite o arquivo .env com suas credenciais
```

## 🚀 Executando

### Desenvolvimento
```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Produção com Docker
```bash
docker-compose up -d
```

## 📱 Configuração do WhatsApp

1. Configure a Evolution API
2. Conecte o WhatsApp via QR Code
3. Configure o webhook:
```bash
python scripts/update_webhook_production.py
```

## 🧪 Testes

```bash
# Testes unitários
pytest tests/unit/

# Testes de integração
pytest tests/integration/

# Verificar sistema
python scripts/pre_flight_check.py
```

## 📊 Arquitetura

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  WhatsApp   │────▶│ Evolution API│────▶│  Webhook    │
│  Cliente    │     │              │     │  FastAPI    │
└─────────────┘     └──────────────┘     └──────┬──────┘
                                                  │
                                          ┌───────▼───────┐
                                          │   AGnO Agent  │
                                          │  Gemini 2.5   │
                                          └───────┬───────┘
                                                  │
                                          ┌───────▼───────┐
                                          │   Supabase    │
                                          │   Database    │
                                          └───────────────┘
```

## 🌟 Funcionalidades

### Agente Luna
- Personalidade consultiva e profissional
- Conversação natural em português
- Análise de imagens (contas de luz)
- Qualificação em múltiplos estágios

### Fluxo de Qualificação
1. **Identificação**: Captura nome do lead
2. **Descoberta**: Tipo de imóvel e interesse
3. **Qualificação**: Valor da conta de energia
4. **Agendamento**: Marcar reunião com consultor

### Integrações
- ✅ WhatsApp (Evolution API)
- ✅ Análise de Imagens (Gemini Vision)
- ✅ Banco de Dados (Supabase)
- ✅ Cache (Redis com fallback)
- 🔄 CRM (Kommo - em desenvolvimento)

## 🚀 Deploy

### Easypanel (Recomendado)
Veja [EASYPANEL_DEPLOY_GUIDE.md](EASYPANEL_DEPLOY_GUIDE.md)

### Railway
Veja [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

### VPS Hostinger
Veja [HOSTINGER_DEPLOY_GUIDE.md](HOSTINGER_DEPLOY_GUIDE.md)

## 📝 Documentação

- [Guia de Configuração](docs/configuration.md)
- [API Reference](docs/api.md)
- [Troubleshooting](docs/troubleshooting.md)

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto é proprietário da Nitrox AI para Solarprime Boa Viagem.

## 👥 Time

Desenvolvido por **Nitrox AI** para **Solarprime Boa Viagem**

## 📞 Suporte

Para suporte, entre em contato através do email: suporte@nitroxai.com

---

**SDR IA SolarPrime** - Transformando leads em clientes com inteligência artificial 🚀