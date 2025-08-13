# 📊 DOCUMENTAÇÃO COMPLETA: Testes KommoCRM Pipeline

## 🎯 OBJETIVO

Validar 100% a eficiência do sistema refatorado (AgenticSDR Refactored + TeamCoordinator) através de testes reais de movimentação de cards no KommoCRM, simulando conversas completas baseadas no prompt da Helen Vieira.

---

## 🏗️ ARQUITETURA DOS TESTES

### Componentes Testados
- **AgenticSDR Refactored** - Agente principal refatorado
- **TeamCoordinator** - Coordenador de equipe
- **CRMService100Real** - Serviço real do Kommo
- **KommoAPIClient** - Cliente da API Kommo
- **SDRTeam** - Time de agentes especializados

### Pipeline Stages (IDs Reais)
```python
NOVO_LEAD = 89709459
EM_QUALIFICACAO = 89709463
QUALIFICADO = 89709467
REUNIAO_AGENDADA = 89709595
NAO_INTERESSADO = 89709599
```

---

## 🧪 TESTE 1: Pipeline Flow Completo

### Arquivo: `test_kommo_pipeline_flow.py`

### Cenários Testados

#### CENÁRIO 1: Lead Qualificado → Reunião Agendada
Simula conversa completa de sucesso seguindo o fluxo da Helen:
1. **Abertura** - Saudação e coleta de nome
2. **Apresentação** - 4 soluções numeradas
3. **Qualificação** - Coleta valor da conta
4. **Confirmação** - Verificação de decisor
5. **Agendamento** - Marcação de reunião

**Validações:**
- Lead move de NOVO_LEAD → EM_QUALIFICACAO → QUALIFICADO → REUNIAO_AGENDADA
- Score de qualificação aumenta progressivamente
- Teams acionado no momento correto

#### CENÁRIO 2: Lead Não Interessado
Simula lead que demonstra desinteresse:
1. Abertura normal
2. Coleta de nome
3. Valor abaixo do mínimo (R$ 2.000)
4. Desinteresse explícito

**Validações:**
- Lead move para NAO_INTERESSADO
- Sistema detecta sinais negativos
- Encerramento adequado

#### CENÁRIO 3: Follow-up e Reengajamento
Simula lead que para de responder:
1. Conversa inicial
2. 30 minutos sem resposta → Follow-up 1
3. 24 horas sem resposta → Follow-up 2
4. Sem resposta final → NAO_INTERESSADO

**Validações:**
- Follow-ups agendados corretamente
- Timing respeitado
- Movimentação final para NAO_INTERESSADO

#### CENÁRIO 4: Critérios de Qualificação
Testa todos os critérios do prompt:
- Valor da conta ≥ R$ 4.000
- Decisor presente
- Sem usina própria
- Sem contrato vigente
- Demonstra interesse

**Validações:**
- Lead qualificado apenas quando TODOS critérios atendidos
- Movimentação correta baseada em critérios

---

## 🤖 TESTE 2: Transições Automáticas

### Arquivo: `test_kommo_automated_transitions.py`

### Testes de Automação

#### TESTE 1: Transição por Score
- Score < 30 → NOVO_LEAD
- Score 30-60 → EM_QUALIFICACAO
- Score > 60 → QUALIFICADO

**Validação:** Movimentação automática baseada em score

#### TESTE 2: Transição por Agendamento
- Qualquer estágio → REUNIAO_AGENDADA quando reunião é marcada

**Validação:** Trigger automático de agendamento

#### TESTE 3: Detecção de Desinteresse
Palavras-chave testadas:
- "não tenho interesse"
- "não quero"
- "pode me remover"
- "para de mandar mensagem"

**Validação:** Detecção automática e movimentação para NAO_INTERESSADO

#### TESTE 4: Follow-up Automation
- Sem resposta 30min → Follow-up automático
- Sem resposta 24h → Follow-up final
- Continua sem resposta → NAO_INTERESSADO

**Validação:** Sistema de follow-up funciona autonomamente

#### TESTE 5: Team Coordinator Integration
Testa decisões do coordenador:
- Quando acionar CRM agent
- Quando agendar reunião
- Quando criar follow-up

**Validação:** TeamCoordinator toma decisões corretas

---

## 🚀 COMO EXECUTAR OS TESTES

### Método 1: Script Automatizado (Recomendado)
```bash
./run_kommo_tests.sh
```

### Método 2: Testes Individuais
```bash
# Teste de pipeline flow
python3 test_kommo_pipeline_flow.py

# Teste de transições automáticas
python3 test_kommo_automated_transitions.py
```

### Método 3: Teste Específico

```python
# No Python
from tests.test_kommo_pipeline_flow import KommoPipelineFlowTest

tester = KommoPipelineFlowTest()
await tester.setup()
await tester.test_scenario_qualified_to_meeting()
```

---

## 📊 ESTRUTURA DOS RELATÓRIOS

### Relatórios Individuais
- `test_kommo_pipeline_report.json` - Resultados do teste de pipeline
- `test_kommo_automated_report.json` - Resultados das transições automáticas

### Relatório Consolidado
- `test_reports/consolidated_kommo_tests.json`

### Estrutura do Relatório
```json
{
  "timestamp": "2024-01-XX",
  "test_results": {
    "scenario_1": true/false,
    "scenario_2": true/false,
    ...
  },
  "total_tests": X,
  "passed_tests": Y,
  "success_rate": "XX%",
  "system_components": {...}
}
```

---

## ✅ CRITÉRIOS DE SUCESSO

### Sistema 100% Validado quando:
1. ✅ Todos os cenários de conversa passam
2. ✅ Transições automáticas funcionam
3. ✅ Follow-ups são agendados corretamente
4. ✅ TeamCoordinator toma decisões corretas
5. ✅ Movimentação de cards é precisa
6. ✅ Critérios de qualificação são respeitados

---

## 🔧 CONFIGURAÇÃO NECESSÁRIA

### Variáveis de Ambiente (.env)
```env
# KommoCRM
KOMMO_ACCESS_TOKEN=seu_token_aqui
KOMMO_SUBDOMAIN=solarprimebrasil
KOMMO_PIPELINE_ID=1234567

# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=seu_key_aqui

# AI Models
GEMINI_API_KEY=seu_key_aqui
OPENAI_API_KEY=seu_key_aqui
```

### Dependências
```bash
pip install -r requirements.txt
```

---

## 🐛 TROUBLESHOOTING

### Erro: "Não foi possível conectar ao Kommo"
- Verificar KOMMO_ACCESS_TOKEN no .env
- Verificar conectividade com API Kommo
- Token pode ter expirado

### Erro: "Lead não foi criado"
- Verificar permissões do token
- Verificar pipeline_id correto
- Verificar campos obrigatórios

### Erro: "Stage não encontrado"
- Verificar IDs dos stages estão corretos
- Pipeline pode ter sido modificado no Kommo

---

## 📈 MÉTRICAS DE SUCESSO

### Taxas Esperadas
- **Pipeline Flow**: 100% de sucesso
- **Transições Automáticas**: 100% de sucesso
- **Detecção de Desinteresse**: > 95% precisão
- **Follow-ups**: 100% agendamento correto

### Performance
- **Tempo médio por teste**: < 30 segundos
- **Tempo total suite**: < 5 minutos
- **Taxa de falsos positivos**: < 5%

---

## 🎯 CONCLUSÃO

Os testes validam completamente a integração entre:
- AgenticSDR Refactored (agente principal)
- TeamCoordinator (orquestração)
- KommoCRM (movimentação de cards)
- SDRTeam (agentes especializados)

**Resultado Esperado:** Sistema 100% funcional com movimentação precisa de cards baseada em conversas reais seguindo o prompt da Helen Vieira.

---

## 📝 NOTAS IMPORTANTES

1. **Dados Reais**: Os testes usam a API real do Kommo (não mock)
2. **Limpeza**: Leads de teste devem ser removidos após execução
3. **Rate Limits**: Respeitar limites da API Kommo
4. **Ambiente**: Preferencialmente executar em ambiente de staging

---

**Última Atualização:** 2024
**Versão:** 1.0
**Status:** ✅ PRONTO PARA EXECUÇÃO