# Integração Supabase - SDR IA SolarPrime

## 📋 Resumo da Implementação

A integração completa com Supabase foi implementada, substituindo o SQLite do AGnO Framework por um banco de dados PostgreSQL robusto e escalável. O sistema agora persiste todos os dados de leads, conversas, mensagens e analytics no Supabase.

## 🏗️ Arquitetura de Dados

```
┌─────────────────────────────────────────────────────────┐
│                   SUPABASE DATABASE                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────┐     ┌──────────────┐     ┌──────────┐   │
│  │  leads  │────<│ conversations │────<│ messages │   │
│  └─────────┘     └──────────────┘     └──────────┘   │
│       │                                                 │
│       ├──────────<─────────────┐                      │
│       │                        │                       │
│  ┌────────────────┐     ┌─────────────┐              │
│  │ qualifications │     │  follow_ups │               │
│  └────────────────┘     └─────────────┘               │
│                                                         │
│                    ┌───────────┐                       │
│                    │ analytics │                       │
│                    └───────────┘                       │
└─────────────────────────────────────────────────────────┘
```

## 📁 Estrutura de Arquivos Criados

```
SDR IA SolarPrime - Python/
├── models/
│   ├── __init__.py
│   ├── base.py                    # Modelo base com campos comuns
│   ├── lead.py                    # Modelo de leads
│   ├── conversation.py            # Modelo de conversas
│   ├── message.py                 # Modelo de mensagens
│   ├── qualification.py           # Modelo de qualificação
│   ├── follow_up.py              # Modelo de follow-ups
│   └── analytics.py              # Modelo de analytics
├── repositories/
│   ├── __init__.py
│   ├── base.py                    # Repositório base CRUD
│   ├── lead_repository.py         # Repositório de leads
│   ├── conversation_repository.py # Repositório de conversas
│   └── message_repository.py      # Repositório de mensagens
├── services/
│   ├── database.py               # Serviço principal do Supabase
│   └── analytics_service.py      # Serviço de analytics
├── scripts/
│   ├── create_supabase_tables.sql     # SQL para criar tabelas
│   ├── migrate_sqlite_to_supabase.py  # Migração de dados
│   └── test_supabase_integration.py   # Testes de integração
└── docs/
    └── SUPABASE_INTEGRATION.md        # Esta documentação
```

## 🔧 Componentes Implementados

### 1. **Models (Pydantic)**
- **BaseDBModel**: Modelo base com id, created_at, updated_at
- **Lead**: Informações completas do lead (telefone, nome, email, conta de luz, etc.)
- **Conversation**: Sessões de conversa com leads
- **Message**: Histórico completo de mensagens
- **LeadQualification**: Dados de qualificação detalhados
- **FollowUp**: Agendamento de follow-ups automáticos
- **Analytics**: Eventos e métricas do sistema

### 2. **Repositories**
- **BaseRepository**: Operações CRUD genéricas
- **LeadRepository**: 
  - `create_or_update()`: Cria ou atualiza lead por telefone
  - `get_by_phone()`: Busca por telefone
  - `get_qualified_leads()`: Lista leads qualificados
  - `get_by_stage()`: Lista por estágio do funil
- **ConversationRepository**:
  - `create_or_resume()`: Cria ou retoma conversa
  - `get_active_by_lead()`: Busca conversa ativa
  - `update_stage_and_sentiment()`: Atualiza progresso
- **MessageRepository**:
  - `save_user_message()`: Salva mensagem do usuário
  - `save_assistant_message()`: Salva resposta do bot
  - `get_conversation_context()`: Obtém contexto formatado

### 3. **Database Service**
- Cliente Supabase singleton
- Acesso direto às tabelas
- Health check integrado
- Tratamento de erros padronizado

### 4. **Analytics Service**
- `track_event()`: Registra eventos customizados
- `get_dashboard_metrics()`: Métricas para dashboard
- `get_conversion_funnel()`: Dados do funil de vendas
- `generate_weekly_report()`: Relatórios automáticos

### 5. **Integração no Agente SDR**
O agente foi modificado para:
- Criar/atualizar lead automaticamente ao receber mensagem
- Criar/retomar conversa por sessão
- Salvar todas as mensagens no banco
- Atualizar informações do lead em tempo real
- Calcular score de qualificação
- Rastrear analytics de cada interação

## 🚀 Como Usar

### 1. Configurar Supabase

Crie um projeto no [Supabase](https://supabase.com) e execute o SQL:

```bash
# No Supabase SQL Editor, execute:
scripts/create_supabase_tables.sql
```

### 2. Configurar Variáveis de Ambiente

Adicione ao `.env`:

```env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... (opcional)
```

### 3. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 4. Migrar Dados Existentes (Opcional)

```bash
python scripts/migrate_sqlite_to_supabase.py
```

### 5. Testar Integração

```bash
python scripts/test_supabase_integration.py
```

## 📊 Schema do Banco de Dados

### Tabela: leads
- `id` (UUID): Identificador único
- `phone_number` (VARCHAR): Telefone único
- `name` (VARCHAR): Nome do lead
- `email` (VARCHAR): Email
- `document` (VARCHAR): CPF/CNPJ
- `property_type` (VARCHAR): casa/apartamento/comercial
- `address` (TEXT): Endereço
- `bill_value` (DECIMAL): Valor da conta
- `consumption_kwh` (INTEGER): Consumo em kWh
- `current_stage` (VARCHAR): Estágio no funil
- `qualification_score` (INTEGER): Score 0-100
- `interested` (BOOLEAN): Se está interessado
- `kommo_lead_id` (VARCHAR): ID no CRM

### Tabela: conversations
- `id` (UUID): Identificador único
- `lead_id` (UUID): Referência ao lead
- `session_id` (VARCHAR): ID da sessão única
- `started_at` (TIMESTAMP): Início da conversa
- `ended_at` (TIMESTAMP): Fim da conversa
- `total_messages` (INTEGER): Total de mensagens
- `current_stage` (VARCHAR): Estágio atual
- `sentiment` (VARCHAR): positivo/neutro/negativo
- `is_active` (BOOLEAN): Se está ativa

### Tabela: messages
- `id` (UUID): Identificador único
- `conversation_id` (UUID): Referência à conversa
- `whatsapp_message_id` (VARCHAR): ID no WhatsApp
- `role` (VARCHAR): user/assistant
- `content` (TEXT): Conteúdo da mensagem
- `media_type` (VARCHAR): Tipo de mídia
- `media_url` (TEXT): URL da mídia
- `media_data` (JSONB): Dados adicionais

## 🔄 Fluxo de Dados

1. **Recepção de Mensagem**:
   - WhatsApp → Evolution API → Webhook → FastAPI

2. **Processamento**:
   - Criar/atualizar lead no Supabase
   - Criar/retomar conversa
   - Salvar mensagem do usuário
   - Processar com agente AGnO

3. **Resposta**:
   - Gerar resposta com AGnO
   - Salvar resposta no banco
   - Atualizar lead e conversa
   - Calcular score de qualificação
   - Rastrear analytics

4. **Analytics**:
   - Eventos customizados
   - Métricas em tempo real
   - Relatórios automáticos

## 📈 Analytics e Métricas

O sistema coleta automaticamente:
- Total de leads por estágio
- Taxa de conversão do funil
- Tempo médio de resposta
- Distribuição de sentimentos
- Mensagens por conversa
- Leads qualificados vs não qualificados

## 🛡️ Segurança

- Row Level Security (RLS) habilitado
- Políticas de acesso configuradas
- Service role para operações do backend
- Todas as credenciais em variáveis de ambiente

## 🧪 Testes

Execute o script de teste completo:

```bash
python scripts/test_supabase_integration.py
```

Testa:
- Conexão com banco
- Operações CRUD
- Integração com agente
- Analytics e métricas

## 📝 Notas Importantes

1. **Performance**: Índices criados para queries otimizadas
2. **Escalabilidade**: Supabase suporta milhões de registros
3. **Real-time**: Possibilidade de usar subscriptions do Supabase
4. **Backup**: Supabase faz backup automático diário
5. **Migrations**: Use Alembic para versionamento do schema

## 🎯 Próximos Passos

1. Implementar real-time subscriptions
2. Adicionar busca vetorial com pgvector
3. Criar dashboard com métricas visuais
4. Implementar sistema de notificações
5. Adicionar testes automatizados

## ✅ Conclusão

A integração com Supabase está 100% funcional e pronta para produção. O sistema agora tem:
- ✅ Persistência completa de dados
- ✅ Rastreamento de leads e conversas
- ✅ Histórico de mensagens
- ✅ Analytics e métricas
- ✅ Migração de dados existentes
- ✅ Testes de integração
- ✅ Documentação completa

O agente SDR agora salva automaticamente todos os dados no Supabase, mantendo compatibilidade total com o AGnO Framework!