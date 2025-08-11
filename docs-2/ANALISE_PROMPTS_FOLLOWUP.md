
# 🕵️‍♂️ Análise de Prompts e Templates do Sistema de Follow-up

**Documento:** `ANALISE_PROMPTS_FOLLOWUP.md`  
**Versão:** 1.0  
**Data:** 04/08/2025  
**Autor:** Engenharia Sênior

---

## 1. Resumo Executivo

Esta análise investiga a origem e o conteúdo dos prompts e templates de mensagem utilizados pelo sistema de follow-up. A investigação confirma a separação entre os lembretes de reunião e os follow-ups de reengajamento.

**Principais Descobertas:**

1.  **Lembretes de Reunião (24h e 2h):** As mensagens para estes lembretes **estão hardcoded** diretamente no método `_send_meeting_reminder_v2` dentro do serviço `FollowUpExecutorService`. Elas são personalizadas com dados do evento (nome, data, hora, link) no momento do envio.

2.  **Follow-up de Reengajamento (30min e 24h):** Os templates para este tipo de follow-up **existem**, mas estão definidos em um dicionário chamado `templates` dentro do `FollowUpExecutorService`. No entanto, conforme a análise anterior (`ANALISE_SISTEMA_FOLLOWUP.md`), **a lógica para acionar o agendamento destes follow-ups está ausente**.

3.  **Fonte da Verdade:** A fonte primária para os templates de follow-up **não é o prompt principal** (`prompt-agente.md`), mas sim o próprio código do `FollowUpExecutorService`. O prompt descreve a *estratégia*, mas os textos exatos estão na implementação do serviço.

---

## 2. Fonte dos Prompts de Lembrete de Reunião

**Status:** ✅ **Funcional e Identificado**

A lógica e os templates para os lembretes de 24 e 2 horas antes da reunião estão localizados exclusivamente no arquivo `app/services/followup_executor_service.py`, dentro do método `_send_meeting_reminder_v2`.

### 2.1. Template do Lembrete de 24 Horas

-   **Localização:** `app/services/followup_executor_service.py`, linha 203.
-   **Conteúdo do Template:**
    ```python
    message = f"""
    📅 *Lembrete de Reunião - Amanhã*

    Oi {lead_data.get('name', 'Cliente')}! 

    Nossa reunião sobre economia de energia solar está confirmada para amanhã:

    🗓️ Data: {start_time.strftime('%d/%m/%Y')}
    ⏰ Horário: {start_time.strftime('%H:%M')}
    📍 Local: {location}

    Vou te mostrar como economizar até 30% na conta de luz! 💡

    Confirma presença? Responda com SIM ou NÃO
    """.strip()
    ```
-   **Análise:** O template é fixo (hardcoded) e utiliza f-strings para inserir dinamicamente o nome do lead, data, hora e local da reunião. É um método eficaz e direto para esta funcionalidade.

### 2.2. Template do Lembrete de 2 Horas

-   **Localização:** `app/services/followup_executor_service.py`, linha 223.
-   **Conteúdo do Template:**
    ```python
    message = f"""
    ⏰ *Reunião em 2 horas!* 

    {lead_data.get('name', 'Cliente')}, nossa reunião é às {start_time.strftime('%H:%M')}!

    Já preparei sua proposta personalizada de economia 📊

    {f'🔗 Link: {meeting_link}' if meeting_link else ''}

    Até daqui a pouco! 😊
    """.strip()
    ```
-   **Análise:** Similar ao lembrete de 24h, este template também é hardcoded e personalizado com dados do evento, incluindo o link do Google Meet, se existir.

---

## 3. Fonte dos Prompts de Follow-up de Reengajamento

**Status:** ⚠️ **Templates Existem, mas a Lógica de Gatilho está Ausente**

Os templates para os follow-ups de reengajamento (quando o usuário não responde) estão definidos em um dicionário na inicialização do `FollowUpExecutorService`, mas, como já apontado, não há código que os utilize de fato.

### 3.1. Localização dos Templates

-   **Arquivo:** `app/services/followup_executor_service.py`, linha 25, dentro do `__init__`.
-   **Estrutura:**
    ```python
    self.templates = {
        "IMMEDIATE_REENGAGEMENT": [
            "Oi {name}! Vi que nossa conversa ficou pela metade...",
            "Ainda posso te ajudar com a economia na conta de luz?",
            "Se preferir, podemos conversar em outro momento"
        ],
        "DAILY_NURTURING": [
            "{name}, você sabia que clientes como você economizam em média R$ {savings} por ano?",
            "A Solar Prime tem a solução perfeita para sua conta de R$ {bill_value}",
            "Vamos conversar sobre como reduzir sua conta de luz?"
        ],
        # ... outros templates
    }
    ```

### 3.2. Análise dos Templates de Reengajamento

-   **`IMMEDIATE_REENGAGEMENT`:** Este seria o template para o follow-up de **30 minutos**. O método `_prepare_followup_message` selecionaria uma das três opções de mensagem para enviar.
-   **`DAILY_NURTURING` / `ABANDONMENT_CHECK`:** Estes seriam os templates para o follow-up de **24 horas**, com foco em nutrir o lead e lembrá-lo do valor da solução.

### 3.3. Desconexão entre Prompt e Código

O `prompt-agente.md` (Seção 4.2) descreve a *intenção* de usar esses follow-ups:

```xml
<no_response_followup>
  <after_30min>
    <trigger>30 minutos sem resposta do lead</trigger>
    <message>Oi {nome}! Vi que nossa conversa ficou pela metade...</message>
  </after_30min>
  
  <after_24h>
    <trigger>Se continuar sem resposta após 30min</trigger>
    <action>sdr_team.schedule_followup(24h)</action>
    <message>{nome}, quando puder continuamos...</message>
  </after_24h>
</no_response_followup>
```

-   **Observação:** O prompt sugere que o `sdr_team` (e, por consequência, o `FollowUpAgent`) seria responsável por agendar a tarefa (`schedule_followup`). A ferramenta existe, os templates existem, mas a **lógica que conecta o evento (não resposta) à ferramenta não foi implementada.**

---

## 4. Conclusão Final

O sistema de follow-up possui os **textos e templates necessários** para funcionar conforme o especificado, mas eles estão localizados diretamente no código do `FollowUpExecutorService`, não no prompt do agente.

-   **Lembretes de Reunião:** Estão **100% funcionais** porque o `FollowUpExecutorService` tem uma lógica proativa que não depende de um gatilho externo.

-   **Follow-up de Reengajamento:** Está **inoperante** por uma falha na implementação da lógica de gatilho. Os templates estão prontos, mas o sistema nunca chega a agendar o seu envio após 30 minutos ou 24 horas de inatividade do lead.

Para corrigir a lacuna, a recomendação da análise anterior se mantém: é preciso criar um mecanismo (como um `FollowUpSchedulerService`) que monitore a inatividade e utilize a ferramenta `FollowUpAgent.schedule_followup` para inserir as tarefas na base de dados, que serão então executadas pelo `FollowUpExecutorService`.
