# 🔧 CORREÇÃO SCHEMA SUPABASE - Coluna is_qualified

## 🐛 Problema Identificado
**Erro**: `Could not find the 'is_qualified' column of 'leads' in the schema cache`
- Código tentando usar coluna `is_qualified` que não existe
- Tabela `leads` usa `qualification_status` ao invés

## ✅ Solução Implementada

### 1. Ajuste no Código
Mudamos para usar colunas existentes:

```python
# ANTES (erro)
updates = {
    "is_qualified": team_state.get("is_qualified", False),
    "qualification_stage": data["stage"]
}

# DEPOIS (correto)
updates = {
    "qualification_status": "QUALIFIED" if is_qualified else "NOT_QUALIFIED",
    "current_stage": data["stage"]
}
```

### 2. Schema Atual da Tabela leads
Colunas relacionadas a qualificação:
- `qualification_status` (PENDING, QUALIFIED, NOT_QUALIFIED)
- `qualification_score` (0-100)
- `current_stage` (estágio atual do lead)
- `is_decision_maker` (boolean)

NÃO existem:
- ❌ `is_qualified`
- ❌ `qualification_stage` 
- ❌ `classification`

### 3. Migration SQL Opcional
Criamos um SQL para adicionar `is_qualified` como coluna computada:

```sql
ALTER TABLE public.leads 
ADD COLUMN IF NOT EXISTS is_qualified BOOLEAN 
GENERATED ALWAYS AS (
    CASE 
        WHEN qualification_status = 'QUALIFIED' THEN TRUE
        ELSE FALSE
    END
) STORED;
```

**Arquivo**: `sqls/ADD_IS_QUALIFIED_COLUMN.sql`

## 📊 Mapeamento de Campos

| Código (Antigo) | Banco (Atual) | Valor |
|-----------------|---------------|-------|
| is_qualified | qualification_status | QUALIFIED/NOT_QUALIFIED/PENDING |
| qualification_stage | current_stage | String do estágio |
| classification | (não existe) | Removido |
| qualification_score | qualification_score | 0-100 |

## 🚀 Como Aplicar

### Opção 1: Usar Código Corrigido (RECOMENDADO)
- Já implementado e funcionando
- Não precisa alterar banco
- Compatível com schema existente

### Opção 2: Aplicar Migration (OPCIONAL)
```bash
# No Supabase SQL Editor:
1. Abrir SQL Editor
2. Colar conteúdo de ADD_IS_QUALIFIED_COLUMN.sql
3. Executar
```

## 📝 Arquivos Modificados

1. **app/teams/sdr_team.py**
   - Linha 447-461: Usar qualification_status
   - Linha 450: Usar current_stage

2. **app/teams/agents/qualification.py**
   - Linha 474-481: Ajustado para schema correto

## ✅ Benefícios

- Sistema funcionando com schema existente
- Sem necessidade de alterar banco
- Compatibilidade mantida
- Código mais robusto

## 🔍 Validação

```python
# Campos que FUNCIONAM:
lead_updates = {
    "qualification_status": "QUALIFIED",  # ✅
    "qualification_score": 85,            # ✅
    "current_stage": "PRESENTING",        # ✅
    "is_decision_maker": True             # ✅
}

# Campos que NÃO funcionam:
lead_updates = {
    "is_qualified": True,      # ❌ Não existe
    "classification": "hot",   # ❌ Não existe
    "qualification_stage": ""  # ❌ Use current_stage
}
```

---

**Data**: 04/08/2025
**Status**: RESOLVIDO
**Prioridade**: ALTA
**Impacto**: Sistema 100% funcional