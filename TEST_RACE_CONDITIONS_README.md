# 🧪 Testes de Race Conditions - SDR IA SolarPrime

Este documento explica como usar os testes criados para validar as correções de race conditions implementadas no sistema.

## 🎯 Problemas Testados

Os testes foram criados para validar especificamente as correções dos seguintes problemas críticos relatados em produção:

1. **`duplicate key value violates unique constraint 'conversations_session_id_key'`**
   - Race condition na criação de conversas
   - Corrigido com UPSERT atômico no Supabase

2. **`WhatsAppMessage object has no field 'conversation_id'`**
   - Tentativa de acesso a campo inexistente no Pydantic
   - Corrigido com context dictionary approach

3. **Problemas de concorrência geral**
   - Múltiplas requisições simultâneas
   - Timeout e performance sob carga

## 📁 Arquivos de Teste

### `test_critical_race_conditions.py`
**Teste focado e rápido** - Testa especificamente os problemas críticos:
- ✅ Constraint violations com mesmo session_id
- ✅ Pydantic field access errors
- ✅ Sessões concorrentes para mesmo telefone
- ✅ Performance sob alta carga (50 requisições)

**Duração**: ~30 segundos

### `test_race_condition_fixes.py`
**Teste completo e extensivo** - Simulação realística de produção:
- ✅ Race conditions diversos
- ✅ Teste de stress prolongado
- ✅ Análise detalhada de performance
- ✅ Relatório completo de métricas

**Duração**: 30+ segundos (configurável)

### `run_race_condition_tests.sh`
**Script de execução simplificada** - Interface amigável para executar os testes.

## 🚀 Como Executar

### Opção 1: Script Automatizado (Recomendado)
```bash
# Torna o script executável (apenas primeira vez)
chmod +x run_race_condition_tests.sh

# Executa o script
./run_race_condition_tests.sh
```

### Opção 2: Execução Manual

#### Pré-requisitos
```bash
# Instalar dependências
pip3 install aiohttp

# Verificar se o servidor está rodando
curl http://localhost:8000/health
```

#### Executar Teste Crítico (Rápido)
```bash
python3 test_critical_race_conditions.py
```

#### Executar Teste Completo
```bash
python3 test_race_condition_fixes.py
```

## 📊 Interpretação dos Resultados

### ✅ **Correções Funcionando** (Esperado)
```
🔐 CONSTRAINT VIOLATIONS 'conversations_session_id_key':
   📊 Total de testes: 15
   ❌ Violations detectadas: 0
   ✅ SUCESSO! UPSERT atômico funcionando corretamente

🏷️  PYDANTIC FIELD ERRORS 'conversation_id':
   📊 Total de testes: 10
   ❌ Errors detectados: 0
   ✅ SUCESSO! Context dict approach funcionando corretamente

🎯 VEREDICTO FINAL:
   ✅ TODAS AS CORREÇÕES FUNCIONANDO!
   🚀 Sistema pronto para produção
```

### ❌ **Correções Precisam de Ajustes**
```
🔐 CONSTRAINT VIOLATIONS 'conversations_session_id_key':
   📊 Total de testes: 15
   ❌ Violations detectadas: 5
   ❌ FALHA! UPSERT precisa de mais ajustes

🎯 VEREDICTO FINAL:
   ❌ CORREÇÕES PRECISAM DE AJUSTES!
   ⚠️  Não implantar em produção ainda
```

## 📄 Relatórios Gerados

Os testes geram relatórios JSON detalhados:

- `critical_race_conditions_report_YYYYMMDD_HHMMSS.json`
- `race_condition_test_report_YYYYMMDD_HHMMSS.json`

Esses arquivos contêm:
- ✅ Métricas detalhadas de performance
- ✅ Detalhes de todos os erros encontrados
- ✅ Análise de race conditions específicos
- ✅ Timestamps e contexto completo

## 🔧 Configuração dos Testes

### Teste Crítico (`test_critical_race_conditions.py`)
```python
# Configurações principais (início do arquivo)
CONCURRENCY_SESSIONS = 15      # Requisições simultâneas para constraint test
PYDANTIC_TESTS = 10           # Testes de pydantic field access
MULTI_SESSION_TESTS = 8       # Sessões concorrentes mesmo telefone
LOAD_TEST_REQUESTS = 50       # Requisições para teste de carga
```

### Teste Completo (`test_race_condition_fixes.py`)
```python
# Configurações principais (início do arquivo)
CONCURRENCY_LEVEL = 10        # Requisições simultâneas por batch
TEST_DURATION_SECONDS = 30    # Duração total do teste
PHONE_NUMBERS = [...]         # Lista de números de teste
```

## 🐛 Troubleshooting

### Problema: Servidor não responde
```bash
# Verificar se o servidor está rodando
ps aux | grep uvicorn

# Iniciar o servidor
uvicorn agente.main:app --reload --host 0.0.0.0 --port 8000
```

### Problema: Dependências não instaladas
```bash
pip3 install aiohttp asyncio
```

### Problema: Timeout nos testes
- Aumente o timeout nos arquivos de teste (linha `timeout=aiohttp.ClientTimeout(total=10)`)
- Reduza a concorrência (`CONCURRENCY_LEVEL = 5`)

### Problema: Muitos erros de conexão
- Verifique se há rate limiting no servidor
- Reduza a frequência das requisições
- Verifique logs do servidor para problemas

## 📈 Benchmarks Esperados

### Performance Normal
- ⚡ Tempo médio de resposta: 50-200ms
- ⚡ Taxa de sucesso: >95%
- ⚡ Timeouts: <5%

### Sob Carga
- ⚡ Tempo médio de resposta: 100-500ms
- ⚡ Taxa de sucesso: >90%
- ⚡ Timeouts: <10%

## 🎯 Próximos Passos Após Testes

### Se Testes Passaram ✅
1. Executar em ambiente de staging
2. Monitor de logs de produção
3. Deploy gradual com rollback preparado

### Se Testes Falharam ❌
1. Analisar relatórios JSON detalhados
2. Identificar padrões nos erros
3. Implementar correções adicionais
4. Re-executar testes

## 🔍 Monitoramento Contínuo

Após deploy em produção, monitore:
- ✅ Constraint violations em logs
- ✅ Pydantic field access errors
- ✅ Performance de response time
- ✅ Taxa de erro em webhooks

---

**📞 Suporte**: Em caso de problemas, analise os logs detalhados e relatórios JSON gerados pelos testes.