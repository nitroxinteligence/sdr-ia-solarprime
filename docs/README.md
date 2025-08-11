# 🤖 Agente de IA SDR SolarPrime - Guia Completo de Desenvolvimento

## 📋 Visão Geral do Projeto

O **Agente de IA SDR SolarPrime** é um sistema inteligente de vendas automatizado para energia solar que opera via WhatsApp. Este documento fornece um guia completo e detalhado para desenvolver o sistema do zero, utilizando as tecnologias mais modernas disponíveis em 2025.

### 🎯 Objetivos do Sistema

- **Automatizar** o processo completo de qualificação de leads via WhatsApp
- **Integrar** com Kommo CRM para gestão profissional do pipeline de vendas e Google Calendar para agendamento de reuniões, cancelamento e reagendamentos. EvolutionAPI para integrar com o WhatsApp e Supabase como Banco de dados.
- **Utilizar** Google Gemini 2.5 Pro para conversação natural e inteligente
- **Implementar** RAG (Retrieval Augmented Generation) com conhecimento específico sobre energia solar com Supabase
- **Escalar** o processo de vendas mantendo qualidade e personalização

### O AGENTE DEVE FUNCIONAR DA SEGUINTE FORMA

- Faz atendimento e qualificação de leads
- Conecta com o Google Calendar para agendamento de reuniões, cancelamento e reagendamentos
- Conecta com o Evolution API para integrar com o WhatsApp
- Conecta com o Supabase para armazenar dados dos leads, recuperação de contexto das conversas entre usuário e Agente
- Faz Follow-UP Automatico e inteligente usando a tabela follow-ups.
- Faz lembrete de agendamentos. Ex: puxa o agendamento feito para o cliente X dentro do Google Calendar e envia uma mensagem personalizada lembrando do compromisso
- Utilize o Typing, Reaction, Localization, etc... Da EvolutionAPI nativamente (devemos aproveitar o máximo possível dos serviços da EvolutionAPI para evitar complexidade)

---

## 🚀 Funcionalidades Principais

### 🤝 Qualificação Inteligente de Leads

TODO O PROCESSO DE QUALIFICAÇÃO PODE ESTAR DENTRO DO PROMPT @prompt-agente.md:

- **Identificação automática** do perfil do lead
- **Análise de necessidades** baseada em conversas naturais
- **Classificação por potencial** (Hot, Warm, Cold)
- **Score de qualificação** automático (0-100)
- **Extração de informações** relevantes (orçamento, timeline, autoridade)

### 💬 Processamento Multimodal

TODO O PROCESSAMENTO MULTIMODAL PODE SER FEITO PELO AGNO FRAMEWORK:

https://docs.agno.com/agents/multimodal
https://docs.agno.com/reference/document_reader/docx
https://docs.agno.com/reference/document_reader/pdf
https://docs.agno.com/reference/document_reader/pdf_url
https://docs.agno.com/reference/document_reader/pdf_image
https://docs.agno.com/reference/document_reader/pdf_image_url

- **Áudio:** Transcrição automática de mensagens de voz
- **Imagem:** OCR para imagens e documentos
- **PDF:** Análise completa de documentos
- **Texto:** Processamento de linguagem natural avançado

### 🔄 Follow-up Inteligente

O FOLLOW-UP INTELIGENTE PODE SER CRIADO COM O AGNO FRAMEWORK COM WORKFLOWS: 
ANTES DE IMPLEMENTAR O FOLLOW-UP LEIA TODOS OS LINKS ABAIXO E IMPLEMENTE DE ACORDO COM A ESTRUTURA DO AGENTE PRINCIPAL:

https://docs.agno.com/workflows_2/overview
https://docs.agno.com/workflows_2/types_of_workflows
https://docs.agno.com/workflows_2/run_workflow
https://docs.agno.com/workflows_2/workflow_session_state
https://docs.agno.com/workflows_2/advanced

- **Follow-up imediato:** 30 minutos após inatividade
- **Follow-up diário:** 24 horas sem resposta
- **Confirmação de reuniões:** No dia do agendamento às 8h
- **Reagendamento automático:** Quando solicitado pelo cliente
- **Classificação de abandono:** Leads que não respondem após 2 tentativas

### 📅 Agendamento Automatizado

EXECUTE Context7 MCP SEMPRE ANTES DE IMPLEMENTAR/REFATORAR ALGO SOBRE O GOOGLE CALENDAR:

- **Integração direta** com Kommo CRM
- **Consulta de disponibilidade** em tempo real
- **Reagendamento inteligente** quando necessário
- **Confirmação automática** no dia da reunião
- **Movimentação de cards** no kanban do Kommo

### 📊 Relatórios Automáticos

DEVEMOS CRIAR UM AGENTE IA ESPECÍFICO COM O AGNO FRAMEWORK PARA GERAR OS RELATÓRIOS E QUE ESTE AGENTE DEVE SER EXECUTADO SEMPRE TODA SEGUNDA-FEIRA ÀS 09H DA MANHÃ E ENVIAR UMA MENSAGEM PARA O GRUPO ESCOLHIDO COM OS RELATÓRIOS:

#### Relatórios Semanais (configurável)
- Leads recebidos
- Leads qualificados  
- Leads quentes identificados
- Reuniões agendadas
- Taxa de conversão

**Entrega:** Grupo do WhatsApp da Solarprime (SEGUNDA-FEIRA ÀS 09H)

### 🎭 Experiência Conversacional Natural

- **Simulação de digitação** ("digitando... e gravando áudio..." no WhatsApp)
- **Tempo de resposta configurável** (Entre 30s à 1 minuto no tempo de resposta "CRIAR DELAY")
- **Personalidade do Helen Vieira** (Prompt completo em @prompt-agente.md)
- **Uso apropriado de emojis** para WhatsApp como: 

---

## 🏗️ Arquitetura do Sistema

### Stack Tecnológico Detalhado

| Componente | Tecnologia | Versão | Função |
|------------|------------|---------|---------|
| **Framework AI** | AGnO Framework | Latest | Orquestração de agentes de IA |
| **LLM** | Google Gemini 2.5 Pro | 2.5 | Processamento de linguagem natural |
| **WhatsApp** | Evolution API | v2 | Integração com WhatsApp Business |
| **CRM** | Kommo CRM | v4 | Gestão de leads e pipeline de vendas |
| **Banco de Dados** | Supabase | Latest | PostgreSQL + pgvector para RAG |
| **Cache** | Redis | 7.0+ | Cache e filas de mensagens |
| **API** | FastAPI | 0.115+ | Backend REST API |
| **Servidor** | Ubuntu | 22.04 LTS | VPS Hostinger |
| **Google Calendar** | Google Calendar API | v3 | Integração com Google Calendar |

### Diagrama de Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                    CAMADA DE APLICAÇÃO                      │
├─────────────────────────────────────────────────────────────┤
│  FastAPI + Uvicorn    │    Agno Framework    │   Pydantic   │
├─────────────────────────────────────────────────────────────┤
│                    CAMADA DE INTEGRAÇÃO                     │
├─────────────────────────────────────────────────────────────┤
│ Evolution API (WhatsApp) │ Kommo CRM API │ Google Gemini 2.5 Pro │ Google Calendar API |
├─────────────────────────────────────────────────────────────┤
│                    CAMADA DE DADOS                          │
├─────────────────────────────────────────────────────────────────┤
│    Supabase (PostgreSQL)    │    Redis (Cache/Queue)       │
├─────────────────────────────────────────────────────────────┤
│                    CAMADA DE INFRAESTRUTURA                 │
├─────────────────────────────────────────────────────────────┤
│      Hostinger VPS (Ubuntu 22.04)     │     Nginx          │
└─────────────────────────────────────────────────────────────┘
```

### Componentes Principais

#### 🧠 Framework de IA
- **Agno Framework:** Framework ultrarrápido para agentes de IA
- **Google Gemini 2.5 Pro:** LLM conversacional principal
- **Memória persistente:** Contexto de conversas mantido
- **Reasoning Tools:** Ferramentas de raciocínio avançado
- **Storage:** Memória de longa duração para persistir dados

DOCUMENTAÇÃO DO AGNO FRAMEWORK:



#### 📱 Integração WhatsApp

DOCUMENTAÇÃO DA EVOLUTION API:

claude-code —docs “https://doc.evolution-api.com/v2/pt/configuration/available-resources”
claude-code —docs “https://doc.evolution-api.com/v2/pt/configuration/webhooks”
claude-code —docs “https://doc.evolution-api.com/v2/pt/requirements/redis”
claude-code —docs “https://doc.evolution-api.com/v2/pt/get-started/introduction”
claude-code —docs “https://doc.evolution-api.com/v2/api-reference/get-information”
claude-code —docs “https://doc.evolution-api.com/v2/api-reference/webhook/set”
claude-code —docs “https://doc.evolution-api.com/v2/api-reference/webhook/get”
claude-code —docs “https://doc.evolution-api.com/v2/api-reference/message-controller/send-text”
claude-code —docs “https://doc.evolution-api.com/v2/api-reference/message-controller/send-reaction”
claude-code —docs “https://doc.evolution-api.com/v2/api-reference/chat-controller/get-base64”
claude-code —docs “https://doc.evolution-api.com/v2/api-reference/chat-controller/fetch-profilepic-url”
claude-code —docs “https://doc.evolution-api.com/v2/api-reference/profile-settings/fetch-business-profile”
claude-code —docs “https://doc.evolution-api.com/v2/api-reference/profile-settings/fetch-profile”
claude-code —docs “https://doc.evolution-api.com/v2/api-reference/group-controller/find-group-by-jid“

- **Evolution API:** API não oficial para WhatsApp Business
- **Baileys Integration:** Suporte completo ao protocolo WhatsApp
- **Webhooks em tempo real:** Processamento instantâneo de mensagens
- **Suporte multimodal:** Texto, áudio, imagem, documentos

#### 🗄️ Banco de Dados

EXECUTE Context7 MCP PARA EXTRAIR TODA A DOCUMENTAÇÃO DO SUPABASE 2025 ATUALIZADA.

- **Supabase:** PostgreSQL com recursos em tempo real
- **Realtime subscriptions:** Atualizações instantâneas
- **Row Level Security:** Segurança avançada de dados
- **Backup automático:** Proteção completa dos dados

#### 🔄 Sistema de Filas
- **Celery:** Processamento assíncrono de tarefas
- **Redis:** Broker de mensagens e cache
- **Task scheduling:** Agendamento de follow-ups (Aqui use o Workflow Agno Framework)
- **Retry logic:** Tratamento de falhas automático

---

## 📚 Documentação Estruturada do Projeto

Este guia está organizado em documentos específicos para cada fase do desenvolvimento. Siga a ordem recomendada para implementar o sistema com sucesso.

### 📁 Estrutura da Documentação

#### 🔧 Fase 1: Configuração e Setup
- **[01. Setup do Ambiente]
  - Configuração da VPS Hostinger
  - Instalação do Ubuntu 22.04 e dependências
  - Setup do Python, Docker, Redis e Nginx
  - Configuração de segurança e firewall

#### 🧠 Fase 2: Desenvolvimento do Agente de IA
- **[02. Desenvolvimento do Agente IA]
  - Implementação com Agno Framework
  - Integração com Google Gemini 2.5 Pro
  - Sistema de memória e contexto

#### 📊 Fase 3: RAG e Base de Conhecimento
- **[03. Sistema RAG com Supabase]
  - Configuração do Supabase e pgvector
  - Implementação de embeddings
  - Popular base de conhecimento sobre energia solar
  - Integração do RAG com o agente

#### 🔌 Fase 4: Integrações
- **[04. API e Webhooks]
  - Desenvolvimento da API FastAPI
  - Configuração dos webhooks Evolution API (Execute Context7 MCP para extrair toda documentação da EvolutionAPI 2025 Atualizada)
  - Processamento de mensagens multimodais
  - Sistema de filas com Redis

#### 💼 Fase 5: CRM e Automação
- **[05. Integração Kommo CRM]
  - Autenticação OAuth2 e Long Lived Token
  - Gestão automatizada de leads
  - Pipeline de vendas customizadoß

#### 🚀 Fase 6: Deploy e Produção
- **[06. Deploy e Monitoramento]
  - Deploy em produção
  - Configuração de monitoramento
  - Sistema de logs e alertas
  - Otimização de performance

---

#### Configurações do Cliente
```env
# Tempo de resposta (configurável)
AGENTE_RESPONSE_DELAY_SECONDS=2

# Relatórios
REPORT_DAY_OF_WEEK=monday
REPORT_TIME=09:00
WHATSAPP_GROUP_ID=group_id_for_reports

# Horários de funcionamento
BUSINESS_HOURS_START=08:00
BUSINESS_HOURS_END=18:00
TIMEZONE=America/Sao_Paulo
```

## 🔗 Integrações

### Evolution API (WhatsApp)

#### Funcionalidades Suportadas
- **Envio/recebimento** de mensagens de texto
- **Processamento de áudio** com transcrição automática
- **Processamento de imagens** com OCR
- **Processamento de documentos** PDF
- **Simulação de digitação** ("typing...")
- **Status de entrega** e leitura
- **Webhooks em tempo real**

#### Configuração
- Instância dedicada para o projeto
- Webhooks configurados para eventos de mensagem
- Autenticação via API key
- Rate limiting implementado

### Kommo CRM

#### Funcionalidades Integradas
- **Criação automática** de leads
- **Atualização em tempo real** de informações
- **Movimentação no pipeline** baseada na qualificação
- **Agendamento de reuniões** diretamente no CRM
- **Campos personalizados** para dados específicos
- **Tags automáticas** baseadas na análise

#### Pipeline de Vendas
1. **Novo Lead** - Lead iniciou conversa
2. **Em Qualificação** - IA coletando informações
3. **Qualificado** - Informações completas coletadas
4. **Reunião Agendada** - Agendamento confirmado
5. **Reunião Confirmada** - Cliente confirmou presença
6. **Transferido** - Passado para atendimento humano

### Google Gemini 2.5 Pro

#### Utilização Principal
- **Análise de intenções** das mensagens
- **Qualificação automática** de leads
- **Geração de respostas** contextuais
- **Análise de sentimentos**
- **Extração de entidades** (nome, empresa, orçamento)
- **Score de qualificação** baseado em critérios

#### Configurações
- Temperatura otimizada para conversação
- Tokens máximos configurados
- Rate limiting implementado
- Fallback para OpenAI GPT 4.1 Nano caso Gemini falhe

### Supabase (Database)

#### Schema Principal
Todos os schemas de todas as tabelas estão em /SQLs

#### Recursos Utilizados
- **Realtime subscriptions** para atualizações
- **Row Level Security** para proteção
- **Triggers automáticos** para auditoria
- **Backup automático** configurado

---

## 📊 Monitoramento e Analytics

### Métricas Principais

#### Tempo Real
- **Conversas ativas** no momento
- **Tempo médio de resposta**
- **Taxa de qualificação** horária
- **Status da infraestrutura**
- **Filas de processamento**

#### Relatórios Semanais
- **Leads recebidos** por dia
- **Taxa de conversão** por etapa
- **Reuniões agendadas** vs. realizadas
- **Principais objeções** encontradas
- **Performance por período** do dia

#### Analytics Avançados
- **Análise de sentimentos** das conversas
- **Temas mais discutidos**
- **Jornada do cliente** detalhada
- **Efetividade dos follow-ups**
- **ROI do sistema**

### Ferramentas de Monitoramento

#### Logging
- **Logs estruturados** em JSON
- **Diferentes níveis** (DEBUG, INFO, WARNING, ERROR)
- **Rotação automática** de logs
- **Centralização** via ELK Stack

#### Alertas
- **Sentry** para erros em produção
- **Alertas via email/WhatsApp** para falhas críticas
- **Monitoramento de uptime**
- **Alertas de performance**

#### Health Checks
- **Endpoint de saúde** da aplicação
- **Verificação de conexões** externas
- **Status das filas** de processamento
- **Uso de recursos** do servidor

---

## 📚 Documentação

# Documentação EVOLUTION API

claude-code —docs “https://doc.evolution-api.com/v2/pt/configuration/available-resources”
claude-code —docs “https://doc.evolution-api.com/v2/pt/configuration/webhooks”
claude-code —docs “https://doc.evolution-api.com/v2/pt/requirements/redis”
claude-code —docs “https://doc.evolution-api.com/v2/pt/get-started/introduction”
claude-code —docs “https://doc.evolution-api.com/v2/api-reference/get-information”
claude-code —docs “https://doc.evolution-api.com/v2/api-reference/webhook/set”
claude-code —docs “https://doc.evolution-api.com/v2/api-reference/webhook/get”
claude-code —docs “https://doc.evolution-api.com/v2/api-reference/message-controller/send-text”
claude-code —docs “https://doc.evolution-api.com/v2/api-reference/message-controller/send-reaction”
claude-code —docs “https://doc.evolution-api.com/v2/api-reference/chat-controller/get-base64”
claude-code —docs “https://doc.evolution-api.com/v2/api-reference/chat-controller/fetch-profilepic-url”
claude-code —docs “https://doc.evolution-api.com/v2/api-reference/profile-settings/fetch-business-profile”
claude-code —docs “https://doc.evolution-api.com/v2/api-reference/profile-settings/fetch-profile”
claude-code —docs “https://doc.evolution-api.com/v2/api-reference/group-controller/find-group-by-jid“

EXECUTE TAMBÉM **Context7 MCP** PARA OBTER MAIS INFORMAÇÕES SOBRE A DOCUMENTAÇÃO DA EVOLUTION API 2025 ATUALIZADO.

# Documentação AGNO FRAMEWORK

## AGENTES

claude-code --docs "https://docs.agno.com/agents/introduction"
claude-code --docs "https://docs.agno.com/agents/run"
claude-code --docs "https://docs.agno.com/agents/sessions"
claude-code --docs "https://docs.agno.com/agents/state"
claude-code --docs "https://docs.agno.com/agents/memory" (Integre com o supabase)
claude-code --docs "https://docs.agno.com/agents/multimodal" (Processamento multimodal para imagens, áudios e documentos como PDF e vídeos, você apenas precisa entender como integrar com a EvolutionAPI para que o Agente consiga interpretar tudo)
claude-code --docs "https://docs.agno.com/agents/knowledge" (Integre com o Supabase)
claude-code --docs "https://docs.agno.com/knowledge/search" (Interessante termos essa função pois podemos criar um Agente específico para isso e quando o lead/usuário trazer uma pergunta complexa, o Agente pode buscar as informações na tabela knowledge_base do Supabase)
claude-code --docs "https://docs.agno.com/knowledge/hybrid_search"
claude-code --docs "https://docs.agno.com/agents/storage" (Integre com o Supabase)
claude-code --docs "https://docs.agno.com/agents/context" (Para que o Agente consiga ter contexto de toda a conversa e integrado com o banco de dados Supabase)
claude-code --docs "https://docs.agno.com/vectordb/pgvector" (Acredito que isso vai lhe ajudar a configurar corretamente o Supabase)
claude-code --docs "https://docs.agno.com/vectordb/introduction"

## AGNO MULTIMODAL

### Processamento multimodal para imagens, áudios e documentos como PDF e vídeos, você apenas precisa entender como integrar com a EvolutionAPI para que o Agente consiga interpretar tudo

claude-code --docs "https://docs.agno.com/agents/multimodal"
claude-code --docs "https://docs.agno.com/reference/document_reader/docx"
claude-code --docs "https://docs.agno.com/reference/document_reader/pdf"
claude-code --docs "https://docs.agno.com/reference/document_reader/pdf_url"
claude-code --docs "https://docs.agno.com/reference/document_reader/pdf_image"
claude-code --docs "https://docs.agno.com/reference/document_reader/pdf_image_url"

# AGNO WORKFLOWS

EX: VOCE DEVE USAR O WORKFLOW PARA CRIAR O AGENTE DE FOLLOW-UP INTELIGENTE COM GEMINI 2.5 PRO.

claude-code --docs "https://docs.agno.com/workflows_2/overview"
claude-code --docs "https://docs.agno.com/workflows_2/types_of_workflows"
claude-code --docs "https://docs.agno.com/workflows_2/run_workflow"
claude-code --docs "https://docs.agno.com/workflows_2/workflow_session_state"
claude-code --docs "https://docs.agno.com/workflows_2/advanced"

# AGNO TEAMS

claude-code --docs "https://docs.agno.com/teams/introduction"
claude-code --docs "https://docs.agno.com/teams/run"
claude-code --docs "https://docs.agno.com/teams/metrics"
claude-code --docs "https://docs.agno.com/teams/shared-state"
claude-code --docs "https://docs.agno.com/teams/route"
claude-code --docs "https://docs.agno.com/teams/coordinate"
claude-code --docs "https://docs.agno.com/teams/collaborate"
claude-code --docs "https://docs.agno.com/teams/structured-output"

# FASTAPI

claude-code --docs "https://docs.agno.com/applications/fastapi/introduction"

# REDIS

SE FOR NECESSÁRIO, UTILIZE O REDIS DO AGNO FRAMEWORK:

claude-code --docs "https://docs.agno.com/storage/redis"

# REASONING

HABILITAR EM CASOS COMPLEXOS. EX: QUEBRA DE OBJEÇÕES, SITUAÇÕES EM QUE O AGENTE DEVE TOMAR DECISÕES BASEADAS EM INFORMAÇÕES NÃO DIRETAS. ETC...

claude-code --docs "https://docs.agno.com/reasoning/introduction"
claude-code --docs "https://docs.agno.com/reasoning/reasoning-models" (Para este projeto, use o Gemini 2.0 flash thinking)
claude-code --docs "https://docs.agno.com/reasoning/reasoning-agents"

# GEMINI

NESTE PROJETO USE O GEMINI 2.5 PRO

claude-code --docs "https://docs.agno.com/models/google"

# OPENAI

USE O o3-mini COMO FALLBACK CASO O GEMINI 2.5 PRO FALHE

claude-code --docs "https://docs.agno.com/models/openai"

# REFERÊNCIAS DE API

claude-code --docs "https://docs.agno.com/reference/agents/agent"
claude-code --docs "https://docs.agno.com/reference/agents/session"
claude-code --docs "https://docs.agno.com/reference/agents/run-response"
claude-code --docs "https://docs.agno.com/reference/workflows_2/workflow"
claude-code --docs "https://docs.agno.com/reference/workflows_2/workflow_run_response"
claude-code --docs "https://docs.agno.com/reference/workflows_2/step_input"
claude-code --docs "https://docs.agno.com/reference/workflows_2/step_output"
claude-code --docs "https://docs.agno.com/reference/workflows_2/conditional-steps"
claude-code --docs "https://docs.agno.com/reference/workflows_2/parallel-steps"
claude-code --docs "https://docs.agno.com/reference/workflows_2/router-steps"
claude-code --docs "https://docs.agno.com/reference/workflows_2/loop-steps"
claude-code --docs "https://docs.agno.com/reference/workflows_2/steps-step"
claude-code --docs "https://docs.agno.com/reference/models/gemini"
claude-code --docs "https://docs.agno.com/reference/models/openai"
claude-code --docs "https://docs.agno.com/reference/knowledge/base"
claude-code --docs "https://docs.agno.com/reference/vector_db/pgvector"
claude-code --docs "https://docs.agno.com/reference/embedder/gemini"
claude-code --docs "https://docs.agno.com/reference/embedder/openai"
claude-code --docs "https://docs.agno.com/reference/memory/memory"
claude-code --docs "https://docs.agno.com/reference/memory/storage/redis"
claude-code --docs "https://docs.agno.com/reference/chunking/fixed-size"
claude-code --docs "https://docs.agno.com/reference/chunking/agentic"
claude-code --docs "https://docs.agno.com/reference/chunking/semantic"
claude-code --docs "https://docs.agno.com/reference/chunking/document"

# Documentação KommoCRM

claude-code —docs “https://developers.kommo.com/docs/about-kommo-api“
claude-code —docs “https://developers.kommo.com/docs/webhooks-general“
claude-code —docs “https://developers.kommo.com/docs/oauth-20“
claude-code —docs “https://developers.kommo.com/reference/list-webhooks“
claude-code —docs “https://developers.kommo.com/reference/add-webhooks“
claude-code —docs “https://developers.kommo.com/reference/delete-webhook“
claude-code —docs “https://developers.kommo.com/reference/webhook-events“
claude-code —docs “https://developers.kommo.com/reference/get-templates“

## REFERENCIA DA API

## LEADS

claude-code —docs “https://developers.kommo.com/reference/leads-list”
claude-code —docs “https://developers.kommo.com/reference/getting-a-lead-by-its-id”
claude-code —docs “https://developers.kommo.com/reference/adding-leads”
claude-code —docs “https://developers.kommo.com/reference/updating-leads”
claude-code —docs “https://developers.kommo.com/reference/updating-single-lead”
claude-code —docs “https://developers.kommo.com/reference/complex-leads”

## PIPELINE LIST

https://developers.kommo.com/reference/pipelines-list


EXECUTE TAMBÉM **Context7 MCP** PARA OBTER MAIS INFORMAÇÕES SOBRE A DOCUMENTAÇÃO DA KOMMO CRM ATUALIZADO.
PESQUISE TAMBÉM NA WEB PARA MAXIMAS INFORMAÇÕES E MÁXIMO CONTEXTO.

# Documentação Supabase

EXECUTE TAMBÉM **Context7 MCP** PARA OBTER MAIS INFORMAÇÕES SOBRE A DOCUMENTAÇÃO DA SUPABASE ATUALIZADO.
PESQUISE TAMBÉM NA WEB PARA MAXIMAS INFORMAÇÕES E MÁXIMO CONTEXTO.

---

## 🎯 Fluxo de Qualificação PARA VOCÊ ENTENDER COMO FUNCIONA:

### Etapas do Processo

#### Etapa 0 - Identificação do Lead
```
EXEMPLO: "Olá! Seja bem-vindo à Solar Prime. Antes de tudo, como você se chama?"
```
- Captura do nome do lead
- Criação do perfil no sistema
- Insere lead no KommmoCRM Pipeline
- Insere lead no Supabase
- Início da sessão de conversa

#### Etapa 1 - Identificação da Solução
```
EXEMPLO: "Você está buscando desconto na sua energia ou montar uma usina?"
```
**5 Soluções Disponíveis:**
1. Usina solar em casa ou terreno próprio
2. Usina em terreno parceiro
3. Compra de energia com desconto - contas acima de R$4.000
4. Compra de energia com desconto - contas abaixo de R$4.000
5. Usina de investimento (transbordo imediato para humano)

#### Etapa 2 - Valor da Conta
```
EXEMPLO: "Qual o valor médio mensal da sua conta de luz?"
```
- Processamento via OCR se enviada imagem
- Validação de valores mínimos
- Cálculo automático de economia

#### Etapa 3 - Desconto Atual
```
EXEMPLO: "Você já recebe algum tipo de desconto? Se sim, qual a porcentagem e com qual empresa?"
```
- Análise de concorrentes (Origo, Setta)
- Estratégias de diferenciação
- Cálculo comparativo de vantagens

#### Etapa 4 - Agendamento
```
EXEMPLO: "Que tal agendarmos uma reunião para eu te mostrar exatamente como funciona?"
```
- Integração com Kommo CRM
- Consulta de disponibilidade
- Confirmação automática

### Proposta de Valor

#### Benefícios Apresentados
- **Usina solar personalizada** para o consumo
- **20% de desconto mínimo** garantido em contrato
- **Zero investimento inicial**
- **No final do contrato, a usina é sua**
- **Proteção contra bandeiras tarifárias**
- **Previsibilidade financeira total**

---

## 🚦 Sistema de Follow-up (COM WORKFLOW DO AGNO FRAMEWORK)

### Regras de Automação

#### Follow-up Imediato (30 minutos)
- **Trigger:** Inatividade na conversa
- **Condição:** Lead ainda não qualificado
- **Ação:** Mensagem de reengajamento
- **Máximo:** 1 tentativa

#### Follow-up Diário (24 horas)
- **Trigger:** Sem resposta após primeiro follow-up
- **Condição:** Lead demonstrou interesse inicial
- **Ação:** Mensagem de nurturing
- **Máximo:** 1 tentativa

#### Confirmação de Reunião (24h antes)
- **Trigger:** Dia da reunião agendada
- **Condição:** Reunião confirmada no CRM
- **Ação:** Mensagem de confirmação inteligente
- **Máximo:** 2 tentativas

#### Lembrete de Reunião já Agendada (24h antes e 2h antes)
- **Trigger:** Dia da reunião agendada
- **Condição:** Reunião Agendada no CRM
- **Ação:** Mensagem de confirmação inteligente
- **Máximo:** 2 tentativas

#### Reagendamento Inteligente
- **Trigger:** Solicitação do cliente
- **Ação:** Consulta automática de disponibilidade
- **Processo:** Sugestão de novos horários
- **Confirmação:** Atualização automática no CRM

---

## 🤝 Conclusão

Este guia fornece todos os recursos necessários para desenvolver o **Agente de IA SDR SolarPrime** do zero. Com as tecnologias escolhidas (Agno Framework, Gemini 2.5 Pro, Evolution API, Kommo CRM e Supabase), você terá um sistema robusto, escalável e eficiente para automação de vendas via WhatsApp.

### Benefícios da Implementação

- ✅ **Automação completa** do processo de qualificação
- ✅ **Redução de custos** com SDRs humanos
- ✅ **Atendimento 24/7** sem pausas
- ✅ **Qualificação consistente** e padronizada
- ✅ **Integração total** com sistemas existentes
- ✅ **Escalabilidade ilimitada** de atendimento