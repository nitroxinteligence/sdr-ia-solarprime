
#  relatório de diagnóstico e solução: erro de `noneType` no Kommo Auto-Sync

**documento:** `DIAGNOSTICO_E_SOLUCAO_KOMMO_SYNC_ERROR.md`  
**versão:** 1.0  
**data:** 07/08/2025  
**autor:** engenharia sênior

---

## 1. resumo executivo

O sistema está enfrentando um erro crítico (`typeError`) no serviço de sincronização automática com o kommo crm (`kommo_auto_sync.py`). O erro ocorre porque a função que cria um "deal" para um lead qualificado tenta realizar uma operação numérica na variável `qualification_score`, mas esta variável está com o valor `none`.

Este não é um bug isolado, mas um sintoma de um problema mais profundo no fluxo de dados: **uma condição de corrida (race condition) e a falta de validação de dados entre o momento em que um lead é qualificado pelo `agenticsdr` e o momento em que o `kommoautosyncservice` tenta processá-lo.**

O serviço de sincronização está pegando leads que foram marcados como `"qualified"` no banco de dados, mas que ainda não tiveram seu `qualification_score` calculado e salvo. Este relatório detalha a causa raiz e apresenta um plano de ação em duas etapas para resolver o problema de forma robusta.

---

## 2. diagnóstico detalhado do erro

### 2.1. erro primário: `typeError: '>=' not supported between instances of 'nonetype' and 'int'`

-   **arquivo:** `app/services/kommo_auto_sync.py`
-   **função:** `_create_deal_for_qualified_lead` (que internamente chama `_determine_tags`)
-   **contexto:** o `kommoautosyncservice` executa em segundo plano, buscando por leads com `qualification_status == 'qualified'` para criar um "deal" (negócio) no kommo crm.
-   **causa imediata:** a função `_determine_tags` é chamada para definir as tags do lead no kommo. Esta função contém uma lógica como `if qualification_score >= 70:`, que compara o score do lead. O erro acontece porque `lead.get('qualification_score')` está retornando `none`.

```python
# app/services/kommo_auto_sync.py -> def _determine_tags(self, lead: dict[str, any]) -> list:

# ...
# a variável qualification_score é none, causando o erro na linha seguinte
qualification_score = lead.get("qualification_score") or 0
if qualification_score >= 70: # <--- erro acontece aqui: if none >= 70
    tags.extend(self.auto_tags["hot"])
# ...
```

### 2.2. causa raiz: condição de corrida e falta de atomicidade

O verdadeiro problema é um **defeito no fluxo de qualificação de leads**:

1.  **qualificação não atômica:** o `agenticsdr` (em `app/agents/agentic_sdr.py`) provavelmente atualiza o status do lead para `"qualified"` no banco de dados em uma operação.
2.  **cálculo de score separado:** o cálculo e a persistência do `qualification_score` podem ocorrer em um passo subsequente ou falhar silenciosamente.
3.  **sync service "apressado":** o `kommoautosyncservice`, rodando a cada 30 segundos, encontra este lead "meio-qualificado" (com status `qualified`, mas `qualification_score` ainda `none`).
4.  **falha na sincronização:** o serviço de sincronização tenta processar este lead inconsistente, resultando no `typeerror`.

### 2.3. erro secundário: log "teste de qualificação? eu não entendi"

-   **causa:** este log indica que um lead foi criado no kommo com este texto como nome. Isso é um sintoma da instabilidade geral. Provavelmente, durante um teste manual ou um fluxo de erro, uma resposta padrão do agente foi salva incorretamente como o nome do lead no banco de dados, e o `kommoautosyncservice` sincronizou esses dados corrompidos.

---

## 3. plano de ação para correção

A solução será implementada em duas fases: uma contenção imediata para parar os erros e uma correção definitiva para garantir a integridade dos dados.

### fase 1: contenção imediata (programação defensiva)

O objetivo é tornar o `kommoautosyncservice` mais robusto para que ele não quebre ao encontrar dados inconsistentes.

**ação 1: validar `qualification_score` antes de usar**

Vamos modificar a função `_determine_tags` em `app/services/kommo_auto_sync.py` para verificar se `qualification_score` não é `none` antes de tentar a comparação numérica.

-   **arquivo a ser modificado:** `app/services/kommo_auto_sync.py`
-   **lógica:**

```python
# em def _determine_tags(self, lead: dict[str, any]) -> list:

# ...
# correção: usar a conversão segura que já existe no projeto
from app.utils.safe_conversions import safe_int_conversion

qualification_score = safe_int_conversion(lead.get("qualification_score"), 0)

# agora a comparação é segura, pois o valor será 0 se for none
if qualification_score >= 70:
    tags.extend(self.auto_tags["hot"])
# ...
```

**ação 2: validação na criação do deal**

Adicionar uma verificação no início de `_create_deal_for_qualified_lead` para garantir que o lead tenha os dados mínimos necessários antes de prosseguir.

-   **arquivo a ser modificado:** `app/services/kommo_auto_sync.py`
-   **lógica:**

```python
# em async def _create_deal_for_qualified_lead(self, lead: dict[str, any]):

# ...
# validação no início da função
score = lead.get('qualification_score')
if score is none:
    logger.warning(f"lead {lead['id']} está qualificado mas não tem score. pulando a criação do deal por agora.")
    return # <--- sai da função se o score não existir

# o resto da função continua...
```

### fase 2: correção definitiva (garantir a atomicidade dos dados)

O objetivo é consertar a causa raiz, garantindo que um lead só seja marcado como qualificado quando todas as informações necessárias estiverem prontas e salvas juntas.

**ação 3: qualificação atômica no `agenticsdr`**

Precisamos revisar o `agenticsdr` para garantir que a lógica de qualificação calcule o score e, em uma **única operação de atualização**, salve tanto o `qualification_status = 'qualified'` quanto o `qualification_score`.

-   **arquivo a ser revisado:** `app/agents/agentic_sdr.py`
-   **lógica a ser implementada:** encontrar o local onde a qualificação é decidida e garantir que a chamada ao `supabase_client.update_lead` inclua ambos os campos no mesmo dicionário de `update_data`.

```python
# exemplo de como a atualização deve ser no agenticsdr
update_payload = {
    "qualification_status": "qualified",
    "qualification_score": 85 # <--- valor calculado
}
await supabase_client.update_lead(lead_id, update_payload)
```

---

## 4. próximos passos

1.  **aplicar imediatamente as correções da fase 1** para estabilizar o serviço de sincronização e parar os erros.
2.  **iniciar a análise e refatoração da fase 2** para corrigir a causa raiz no `agenticsdr`, garantindo a consistência dos dados a longo prazo.
3.  **realizar uma limpeza de dados** no kommo para remover leads com nomes inválidos como "teste de qualificação?".
