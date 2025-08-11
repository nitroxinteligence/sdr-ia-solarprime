
#  relatório de diagnóstico e solução: inconsistências de fuso horário e horário comercial

**documento:** `DIAGNOSTICO_E_SOLUCAO_TIMING_AGENT.md`  
**versão:** 1.0  
**data:** 07/08/2025  
**autor:** engenharia sênior

---

## 1. resumo executivo

A análise dos logs de erro e do código-fonte em `@app/**` identificou uma falha crítica e sistêmica na maneira como o aplicativo lida com data e hora. O problema se manifesta de duas formas principais:

1.  **agendamentos fora do horário comercial:** follow-ups e lembretes estão sendo agendados para horários fora do expediente (08:00 - 20:00), como de madrugada, o que é unprofessional e viola as regras de negócio.
2.  **cálculos de tempo incorretos:** os deltas de tempo para agendamentos (ex: "daqui a 30 minutos") estão sendo calculados incorretamente, provavelmente devido à falta de tratamento de fuso horário (`timezone`).

A causa raiz para ambos os problemas é a **ausência de uma função utilitária centralizada para manipulação de data e hora que seja ciente do fuso horário e das regras de negócio (horário comercial)**. Atualmente, a lógica de agendamento está duplicada e implementada de forma inconsistente em pelo menos dois locais críticos, um dos quais (`app/api/webhooks.py`) ignora completamente essas regras.

Este relatório propõe uma solução robusta e definitiva: a criação de uma função utilitária central em `app/utils/time_utils.py` para lidar com todos os cálculos de agendamento, garantindo que todas as partes do sistema operem de forma consistente e correta.

---

## 2. diagnóstico detalhado

### 2.1. causa raiz: lógica de tempo descentralizada e inconsistente

O problema fundamental é que existem duas implementações concorrentes e conflitantes para agendamento de follow-ups:

-   **implementação incorreta (em `webhooks.py`):** a função `_schedule_inactivity_followup` em `app/api/webhooks.py` é a responsável por agendar os follow-ups de inatividade de 30 minutos e 24 horas. Sua lógica é a seguinte:

    ```python
    # em app/api/webhooks.py
    scheduled_time = datetime.now() + timedelta(minutes=30)
    scheduled_24h = datetime.now() + timedelta(hours=24)
    ```

    **diagnóstico:** esta implementação é a fonte direta dos erros observados.
    1.  **ignora fuso horário:** `datetime.now()` usa o fuso horário do servidor, não o `timezone` definido em `app/config.py` (`america/sao_paulo`). Isso causa as discrepâncias de cálculo (ex: 35 minutos em vez de 30).
    2.  **ignora horário comercial:** a função simplesmente adiciona um `timedelta`, agendando follow-ups para qualquer horário, incluindo de madrugada.

-   **implementação parcialmente correta (em `followup.py`):** o `followupagent` em `app/teams/agents/followup.py` contém uma lógica melhor, mas que não está sendo usada pelo webhook:

    ```python
    # em app/teams/agents/followup.py
    scheduled_at = datetime.now() + timedelta(hours=delay_hours)
    scheduled_at = self._adjust_to_business_hours(scheduled_at)
    ```

    **diagnóstico:** este agente possui uma função `_adjust_to_business_hours` que tenta respeitar o horário comercial. No entanto, esta função também sofre de dois problemas:
    1.  **lógica isolada:** por ser um método privado (`_`), não pode ser reutilizado por outras partes do sistema.
    2.  **ainda ignora fuso horário:** a lógica de ajuste também usa `datetime.now()` sem o `timezone` correto, tornando seus cálculos imprecisos.

### 2.2. falha arquitetural

A existência de duas lógicas diferentes para a mesma tarefa de negócio (agendar um follow-up) é uma falha de design. A função `_schedule_inactivity_followup` no webhook deveria delegar a tarefa de agendamento para o `followupagent` ou, idealmente, ambas deveriam usar uma **função utilitária centralizada**.

---

## 3. solução proposta: centralização e robustez da lógica de tempo

A solução definitiva consiste em criar uma única fonte de verdade para todos os cálculos de data e hora que envolvem regras de negócio, e refatorar o código para usá-la.

### passo 1: criar uma função utilitária de tempo inteligente

Vamos criar uma nova função `adjust_datetime_to_business_hours` em `app/utils/time_utils.py`. Esta função será a única responsável por todos os cálculos de agendamento futuro.

-   **arquivo a ser criado/modificado:** `app/utils/time_utils.py`
-   **nova função:**

```python
# adicionar no final de app/utils/time_utils.py
from datetime import datetime, time, timedelta
import pytz
from app.config import settings

def adjust_datetime_to_business_hours(dt: datetime) -> datetime:
    """
    ajusta um datetime para estar dentro do horário comercial (08:00-20:00) 
    e em dias úteis (seg-sex), respeitando o fuso horário do sistema.

    args:
        dt: o datetime a ser ajustado.

    returns:
        um novo objeto datetime ajustado para o próximo horário comercial válido.
    """
    try:
        tz = pytz.timezone(settings.timezone)
    except pytz.UnknownTimeZoneError:
        tz = pytz.utc

    # garante que o datetime de entrada tenha o fuso horário correto
    if dt.tzinfo is None:
        dt = tz.localize(dt)
    else:
        dt = dt.astimezone(tz)

    business_start = time(8, 0)
    business_end = time(20, 0)

    # se for fim de semana, avança para a próxima segunda-feira às 8h
    if dt.weekday() >= 5: # 5 = sábado, 6 = domingo
        days_to_monday = 7 - dt.weekday()
        dt = (dt + timedelta(days=days_to_monday)).replace(hour=business_start.hour, minute=business_start.minute, second=0, microsecond=0)
        return dt

    # se for antes do horário comercial, ajusta para o início do dia
    if dt.time() < business_start:
        return dt.replace(hour=business_start.hour, minute=business_start.minute, second=0, microsecond=0)

    # se for depois do horário comercial, avança para o próximo dia útil às 8h
    if dt.time() > business_end:
        next_day = dt + timedelta(days=1)
        # se o próximo dia for fim de semana, avança para segunda
        if next_day.weekday() >= 5:
            days_to_monday = 7 - next_day.weekday()
            next_day += timedelta(days=days_to_monday)
        return next_day.replace(hour=business_start.hour, minute=business_start.minute, second=0, microsecond=0)

    # se já está dentro do horário comercial, retorna como está
    return dt
```

### passo 2: refatorar `_schedule_inactivity_followup` para usar a nova função

Agora, vamos corrigir o agendamento de follow-up de inatividade para que ele use nossa nova função inteligente.

-   **arquivo a ser modificado:** `app/api/webhooks.py`
-   **lógica de substituição:**

```python
# em app/api/webhooks.py
# ...
from app.utils.time_utils import adjust_datetime_to_business_hours # <--- importar a nova função
# ...

# dentro de _schedule_inactivity_followup
# ...
# --- linha a ser removida ---
# scheduled_time = datetime.now() + timedelta(minutes=30)

# --- nova lógica ---
now_with_tz = datetime.now(pytz.timezone(settings.timezone))
base_schedule_time = now_with_tz + timedelta(minutes=30)
scheduled_time = adjust_datetime_to_business_hours(base_schedule_time)

# ... (para o follow-up de 24h)
# --- linha a ser removida ---
# scheduled_24h = datetime.now() + timedelta(hours=24)

# --- nova lógica ---
base_schedule_24h = now_with_tz + timedelta(hours=24)
scheduled_24h = adjust_datetime_to_business_hours(base_schedule_24h)
# ...
```

### passo 3: refatorar `followupagent` para usar a nova função

Para eliminar a duplicação de código e garantir consistência, o `followupagent` também usará a função centralizada.

-   **arquivo a ser modificado:** `app/teams/agents/followup.py`
-   **lógica de substituição:**

```python
# em app/teams/agents/followup.py
# ...
from app.utils.time_utils import adjust_datetime_to_business_hours # <--- importar a nova função
# ...

# dentro de FollowUpAgent.schedule_followup
# ...
# --- linha a ser removida ---
# scheduled_at = self._adjust_to_business_hours(scheduled_at)

# --- nova lógica ---
scheduled_at = adjust_datetime_to_business_hours(scheduled_at)
# ...

# remover completamente a função _adjust_to_business_hours do agente
```

---

## 4. benefícios da solução proposta

1.  **correção definitiva:** resolve os dois problemas reportados (horário comercial e fuso horário) na sua origem.
2.  **código centralizado e reutilizável:** a lógica de tempo de negócio passa a existir em um único local (`time_utils.py`), facilitando a manutenção e evitando bugs futuros.
3.  **resiliência e profissionalismo:** o sistema passa a respeitar o horário comercial de forma consistente, melhorando a experiência do cliente e a imagem da empresa.
4.  **consistência arquitetural:** alinha o comportamento do sistema com as regras de negócio definidas, eliminando implementações conflitantes.
