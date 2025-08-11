# 🧹 Script de Limpeza da Knowledge Base

**Arquivo:** `clean_knowledge_base.py`  
**Propósito:** Camada 3 da solução para problemas de formatação do agente Helen  
**Versão:** 1.0  

## 📋 Descrição

Este script implementa a **Camada 3** da solução para os problemas de formatação identificados no agente Helen. Ele sanitiza todos os registros existentes na tabela `knowledge_base`, removendo:

- ✅ **Emojis** (✍️, 💰, etc.)
- ✅ **Markdown duplo** (**texto**)
- ✅ **Enumerações** (1., 2., 3.)
- ✅ **Listas com marcadores** (-, *)
- ✅ **Quebras de linha múltiplas**

## 🚀 Como Usar

### 1. Modo Simulação (Padrão - Seguro)
```bash
# Análise sem modificar dados
python scripts/clean_knowledge_base.py

# Análise com detalhes de cada registro
python scripts/clean_knowledge_base.py --verbose
```

### 2. Modo Execução (Modifica dados)
```bash
# ATENÇÃO: Modifica os dados efetivamente!
python scripts/clean_knowledge_base.py --execute

# Com detalhes
python scripts/clean_knowledge_base.py --execute --verbose
```

### 3. Parâmetros Disponíveis

| Parâmetro | Descrição |
|-----------|-----------|
| `--dry-run` | Simula sem modificar (padrão) |
| `--execute` | Executa modificações reais |
| `--verbose` | Mostra detalhes de cada registro |
| `-v` | Alias para `--verbose` |

## 📊 Exemplo de Saída

```
🔍 MODO SIMULAÇÃO - Nenhum dado será modificado
🔍 Buscando todos os registros da knowledge_base...
✅ Encontrados 45 registros para análise
📊 Iniciando simulação de 45 registros...

🔍 REGISTRO: Garantias e Benefícios (ID: 123)
  📝 Problemas: has_double_markdown, has_enumerations
  📄 Original: **Garantias da Solar Prime**: 1. Garantia de 25 anos...
  ✨ Limpo: Garantias da Solar Prime: Garantia de 25 anos...

============================================================
📊 RELATÓRIO FINAL DA LIMPEZA
============================================================
📈 Total de registros analisados: 45
⚠️  Registros com problemas encontrados: 8
🔍 Modo simulação - nenhum dado foi modificado
📝 Registros que seriam limpos: 8

🔍 TIPOS DE PROBLEMAS ENCONTRADOS:
  😀 Emojis: 3 registros
  ** Markdown duplo: 5 registros
  1. Enumerações: 6 registros
  \n Quebras de linha: 4 registros

💡 Execute sem --dry-run para aplicar as correções.
```

## 🔒 Segurança

### Medidas de Proteção:
1. **Modo simulação por padrão** - nunca modifica dados a menos que `--execute` seja especificado
2. **Confirmação manual** - solicita confirmação antes de executar modificações
3. **Backup dos dados originais** - mantém histórico no campo `updated_at`
4. **Log detalhado** - registra todas as operações executadas
5. **Rollback possível** - as modificações são reversíveis

### Recomendações:
```bash
# 1. SEMPRE execute primeiro em modo simulação
python scripts/clean_knowledge_base.py --verbose

# 2. Analise o relatório cuidadosamente

# 3. Só então execute as modificações
python scripts/clean_knowledge_base.py --execute
```

## 🎯 Casos de Uso

### Cenário 1: Análise Inicial
```bash
# Descobrir quantos registros têm problemas
python scripts/clean_knowledge_base.py
```

### Cenário 2: Análise Detalhada
```bash
# Ver exatamente quais problemas cada registro tem
python scripts/clean_knowledge_base.py --verbose
```

### Cenário 3: Limpeza Completa
```bash
# Aplicar todas as correções
python scripts/clean_knowledge_base.py --execute --verbose
```

## 🔧 Funcionamento Interno

### 1. Análise
- Busca todos os registros da `knowledge_base`
- Identifica problemas de formatação em cada registro
- Gera versão limpa de cada conteúdo problemático

### 2. Sanitização
- Remove emojis usando regex Unicode
- Remove markdown duplo (`**texto**` → `texto`)
- Remove enumerações (`1. item` → `item`)
- Remove quebras de linha (`\n` → ` `)
- Limpa espaços duplos

### 3. Relatório
- Estatísticas completas da operação
- Detalhamento por tipo de problema
- Contagem de registros processados

## 📝 Logs e Monitoramento

O script usa `loguru` para logging estruturado:

- `✅ INFO`: Operações normais
- `⚠️  WARNING`: Situações de atenção
- `❌ ERROR`: Problemas que impedem a operação
- `🎉 SUCCESS`: Operações concluídas com sucesso

## 🔄 Integração com as Outras Camadas

Esta **Camada 3** complementa:

- **Camada 1**: Regras fortalecidas no prompt do agente
- **Camada 2**: Sanitização agressiva no `webhooks.py`

Juntas, as três camadas garantem que:
1. O agente não gere formatação incorreta (Camada 1)
2. Qualquer formatação incorreta seja removida antes do envio (Camada 2)
3. A fonte dos dados esteja sempre limpa (Camada 3)

## ⚡ Conclusão

Execute este script uma vez para limpar toda a base de conhecimento existente. Após a execução, os problemas de formatação do agente Helen devem ser completamente eliminados.

**Próximos passos após a execução:**
1. Testar o agente com mensagens que antes geravam problemas
2. Verificar se não há mais emojis, markdown duplo ou enumerações nas respostas
3. Monitorar por alguns dias para confirmar a eficácia da solução