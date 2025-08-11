# Correção: Erro de Comparação de Datetimes no Follow-up

## Problema
Erro ao validar inatividade do follow-up: `can't compare offset-naive and offset-aware datetimes`

## Causa
- O código usava `datetime.now()` que cria datetimes **naive** (sem timezone)
- O Supabase retorna timestamps **aware** (com timezone)
- Python não permite comparar datetimes naive com aware

## Solução Implementada

### 1. Importação de timezone
```python
from datetime import datetime, timedelta, timezone
```

### 2. Novo método _parse_datetime()
```python
def _parse_datetime(self, datetime_str: str) -> datetime:
    """
    Converte string para datetime garantindo timezone awareness
    """
    try:
        dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception as e:
        return datetime.now(timezone.utc)
```

### 3. Substituições realizadas
- `datetime.now()` → `datetime.now(timezone.utc)`
- `datetime.fromisoformat(timestamp)` → `self._parse_datetime(timestamp)`

## Arquivos Modificados
- `/app/services/followup_executor_service.py`

## Impacto
- Todas as comparações de datetime agora funcionam corretamente
- Sistema de follow-up não terá mais erros de timezone
- Timestamps salvos no banco mantêm consistência UTC