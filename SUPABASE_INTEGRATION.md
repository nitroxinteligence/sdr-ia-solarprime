# Integração Supabase - SDR IA SolarPrime

## 📋 Visão Geral

A integração com Supabase fornece persistência de dados completa para o agente SDR, incluindo:
- Gerenciamento de leads e qualificação
- Histórico completo de conversas
- Sistema de follow-up automatizado
- Analytics e métricas
- Integração seamless com AGnO Framework

## 🚀 Setup Rápido

### 1. Configurar Credenciais

Adicione ao arquivo `.env`:

```env
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_ANON_KEY=sua_anon_key_aqui
SUPABASE_SERVICE_KEY=sua_service_key_aqui  # Recomendado para backend
```

### 2. Criar Tabelas

Execute o SQL no Supabase:
```bash
# Copie o conteúdo de:
scripts/create_supabase_tables.sql

# Cole no SQL Editor do Supabase e execute
```

### 3. Verificar Instalação

```bash
# Teste rápido
python scripts/quick_test_supabase.py

# Verificação completa
python scripts/verify_supabase_setup.py
```

## 📊 Estrutura do Banco de Dados

### Tabelas Principais

#### `leads`
- Informações completas do lead
- Score de qualificação
- Estágio atual do funil
- Dados da propriedade e conta de luz

#### `conversations`
- Sessões de conversa
- Contexto e memória
- Sentimento e estágio

#### `messages`
- Histórico completo de mensagens
- Suporte multimodal (texto, áudio, imagem)
- Análise de sentimento

#### `lead_qualifications`
- Critérios de qualificação detalhados
- Histórico de mudanças
- Análise de fit

#### `follow_ups`
- Follow-ups agendados
- Templates personalizados
- Histórico de tentativas

#### `analytics`
- Métricas de conversão
- Performance do agente
- Insights de qualificação

## 🔧 Uso no Código

### Repository Pattern

```python
from repositories.lead_repository import lead_repository

# Criar ou atualizar lead
lead = await lead_repository.create_or_update({
    "phone_number": "5511999999999",
    "name": "João Silva"
})

# Buscar lead por telefone
lead = await lead_repository.get_by_phone("5511999999999")

# Listar leads qualificados
qualified = await lead_repository.get_qualified_leads(min_score=70)
```

### Integração Automática no Agente

O agente SDR salva automaticamente:
- Todos os leads processados
- Conversas e mensagens
- Scores de qualificação
- Análises e métricas

```python
# No agents/sdr_agent.py
response = await agent.process_message(phone_number, message)
# Dados são salvos automaticamente no Supabase!
```

## 🛡️ Segurança

### Row Level Security (RLS)

Para desenvolvimento:
1. **Opção 1**: Use `SUPABASE_SERVICE_KEY` (recomendado)
2. **Opção 2**: Execute `scripts/disable_rls_for_testing.sql` (apenas dev)

**⚠️ NUNCA desabilite RLS em produção!**

### Boas Práticas

- Sempre use Service Key para operações backend
- Mantenha RLS ativo em produção
- Configure políticas apropriadas
- Monitore logs de acesso

## 📈 Analytics e Relatórios

### Métricas Disponíveis

```python
from services.analytics_service import analytics_service

# Taxa de conversão
conversion_rate = await analytics_service.get_conversion_rate()

# Leads por estágio
stage_distribution = await analytics_service.get_leads_by_stage()

# Performance temporal
daily_metrics = await analytics_service.get_daily_metrics()
```

### Views Prontas

- `lead_analytics_view`: Visão consolidada de leads
- `conversation_metrics_view`: Métricas de conversação
- `qualification_funnel_view`: Funil de qualificação

## 🔄 Migração de Dados

### Do SQLite para Supabase

```bash
# Migrar dados existentes
python scripts/migrate_to_supabase.py

# Verificar migração
python scripts/verify_migration.py
```

## 🐛 Troubleshooting

### Problemas Comuns

#### "row-level security policy violation"
- **Causa**: RLS ativo sem permissões
- **Solução**: Use Service Key ou ajuste políticas RLS

#### "relation does not exist"
- **Causa**: Tabelas não criadas
- **Solução**: Execute o script SQL de criação

#### "JSON object requested, multiple rows returned"
- **Causa**: Query retornando múltiplos resultados
- **Solução**: Use `.limit(1)` ou ajuste a query

### Scripts de Diagnóstico

```bash
# Verificar configuração completa
python scripts/verify_supabase_setup.py

# Teste rápido de funcionalidade
python scripts/quick_test_supabase.py

# Testar integração completa
python scripts/test_supabase_integration.py
```

## 📚 Recursos Adicionais

- [Documentação Supabase](https://supabase.com/docs)
- [Python Client Library](https://github.com/supabase-community/supabase-py)
- [RLS Guide](https://supabase.com/docs/guides/auth/row-level-security)
- [Performance Tips](https://supabase.com/docs/guides/performance)

## 🤝 Suporte

Para problemas específicos:
1. Execute `verify_supabase_setup.py` para diagnóstico
2. Verifique logs em `logs/sdr_agent.log`
3. Consulte a documentação do Supabase
4. Abra uma issue no repositório