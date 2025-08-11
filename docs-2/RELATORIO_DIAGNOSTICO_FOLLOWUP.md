### **RELATÓRIO DE DIAGNÓSTICO: Inconsistências no Sistema de Follow-Up**

**Data:** 07/08/2025
**Analista:** Gemini
**Status:** Análise Concluída

### **Sumário Executivo**

O sistema de follow-up apresentou dois erros críticos: **1) Envio de múltiplos follow-ups duplicados em um curto intervalo de tempo** e **2) Vazamento da tag de formatação `<RESPOSTA_FINAL>` para o usuário**.

A análise revelou que a causa raiz da **duplicação** é uma condição de corrida no `FollowUpExecutorService`, onde múltiplos jobs de reengajamento para o mesmo evento são criados e executados em paralelo antes que o sistema possa atualizar seu estado. O **vazamento da tag** é um erro intermitente de parsing na geração de mensagens inteligentes, onde a lógica de extração falha em limpar a resposta do modelo de linguagem em 100% dos casos.

A análise de risco para os lembretes de reunião indica que o problema de duplicação é **baixo** para este cenário, mas o risco de vazamento de tag permanece **médio**.

A seguir, o detalhamento completo dos diagnósticos e as soluções recomendadas.

---

### **1. Análise do Problema 1: Múltiplos Follow-ups Duplicados**

**Sintoma:** O log do WhatsApp mostra 6 mensagens de follow-up enviadas para o mesmo lead em um intervalo de menos de 4 minutos (de 08:01:38 a 08:04:59), todas com variações da mesma intenção de reengajamento.

**Diagnóstico Detalhado:**

A causa raiz não é um único bug, mas uma combinação de como os follow-ups são agendados e como o serviço executor os processa, criando uma condição de corrida.

1.  **Gatilho de Agendamento Duplo:** A investigação do arquivo `app/api/webhooks.py` mostra que a função `_schedule_inactivity_followup` é chamada sempre que o agente envia uma resposta. Esta função cria **dois** registros na tabela `follow_ups` simultaneamente:
    *   Um follow-up de reengajamento para **30 minutos** (`reengagement`).
    *   Um follow-up de reengajamento para **24 horas** (`nurturing`).

2.  **Serviço Executor Periódico:** O `FollowUpExecutorService` (`app/services/followup_executor_service.py`) opera em um loop que verifica a tabela `follow_ups` a cada 60 segundos (`check_interval = 60`) por tarefas com `status = 'pending'` e `scheduled_at <= now`.

3.  **A Falha Lógica (Condição de Corrida):** O problema central reside aqui. Se, por qualquer motivo (um pequeno atraso, um deploy, etc.), múltiplos follow-ups para o mesmo lead se tornam "devidos" ao mesmo tempo, o `FollowUpExecutorService` irá:
    *   Executar a query e obter uma **lista** de todos os follow-ups pendentes.
    *   Iterar sobre essa lista e executar **todos eles em sequência rápida**.
    *   A lógica de validação `_validate_inactivity_followup` verifica se o **usuário** respondeu, mas não verifica se outro **follow-up do sistema** para o mesmo lead acabou de ser enviado segundos antes.
    *   **Resultado:** O sistema envia todas as mensagens da fila antes de ter a chance de marcar a primeira como "executada" e reavaliar a situação. Ele não possui um mecanismo de "lock" por lead para garantir que apenas um follow-up seja processado por vez.

---

### **2. Análise do Problema 2: Vazamento da Tag `<RESPOSTA_FINAL>`**

**Sintoma:** A primeira mensagem de follow-up enviada continha a tag de formatação interna: `Certo, Mateus. Entendido. <RESPOSTA_FINAL> Oi Mateus...`

**Diagnóstico Detalhado:**

Este erro é um vazamento do processamento interno do modelo de linguagem para o usuário final.

1.  **Propósito da Tag:** O prompt do agente (`app/prompts/prompt-agente.md`) instrui o modelo a envolver a resposta final na tag `<RESPOSTA_FINAL>`. Isso serve para separar o "raciocínio" da "resposta".

2.  **Falha na Extração:** O código que chama o agente é responsável por extrair *apenas* o conteúdo de dentro dessa tag. A função `extract_final_response` em `app/api/webhooks.py` faz isso de forma robusta.

3.  **Ponto da Falha:** O erro ocorreu em uma mensagem gerada pelo `FollowUpExecutorService`. A análise do `_generate_intelligent_message` no serviço mostra que ele também chama o `AgenticSDR` e tenta extrair a resposta. No entanto, a falha indica que:
    *   O modelo de linguagem, de forma intermitente, gerou uma resposta malformada, incluindo texto conversacional *antes* da tag `<RESPOSTA_FINAL>`.
    *   A lógica de extração no `followup_executor_service.py`, embora presente, pode não ser tão robusta quanto a do `webhooks.py` ou falhou em lidar com este formato inesperado, resultando no envio da string parcialmente processada. A ausência de uma camada final de "sanitização" que remove quaisquer tags remanescentes antes do envio é a vulnerabilidade chave.

---

### **3. Análise de Risco para Lembretes de Reunião**

Você corretamente se preocupou se o mesmo problema poderia afetar os lembretes de reunião.

*   **Risco de Duplicação (Baixo):**
    *   Os lembretes de reunião são agendados pela `CalendarAgent` para horários muito distintos (ex: 24 horas e 2 horas antes da reunião).
    *   Como os `scheduled_at` são muito diferentes, é extremamente improvável que o `FollowUpExecutorService` os pegue na mesma execução. A condição de corrida que afeta os follow-ups de reengajamento não se aplica aqui.

*   **Risco de Vazamento de Tag (Médio):**
    *   A geração de mensagens para lembretes de reunião, especialmente as personalizadas (`_generate_intelligent_meeting_reminder`), também utiliza o `AgenticSDR`.
    *   Portanto, ela está suscetível ao mesmo problema de resposta malformada do modelo de linguagem. Sem uma camada de sanitização final e garantida no `FollowUpExecutorService`, existe um risco de que um lembrete de reunião também possa vazar a tag.

---

### **4. Recomendações e Soluções**

Para garantir que o sistema de follow-up seja 100% confiável, recomendo as seguintes ações:

1.  **Solução para Duplicação (Implementar Lock por Lead):**
    *   **O que fazer:** Introduzir um mecanismo de lock distribuído (usando Redis, que já está no projeto) no `FollowUpExecutorService`.
    *   **Como:** Antes de processar um follow-up para um `lead_id`, o serviço deve tentar adquirir um lock (`redis_client.acquire_lock(f"followup:{lead_id}", ttl=60)`). Se não conseguir, significa que outro processo já está tratando desse lead, e ele deve pular a execução. Isso garante que apenas um follow-up por lead seja enviado por ciclo.

2.  **Solução para Vazamento de Tag (Sanitização Final):**
    *   **O que fazer:** Criar uma função de sanitização final e aplicá-la a **toda e qualquer** mensagem antes de ser enviada pela `evolution_client`.
    *   **Como:** Em `app/services/followup_executor_service.py`, antes da linha `await self.evolution.send_text_message(...)`, adicione uma chamada para uma função que remove agressivamente qualquer padrão de tag (`<TAG>...</TAG>`) da mensagem final. Isso atua como uma camada de segurança final, garantindo que, mesmo que a extração falhe, a tag nunca chegue ao usuário.

3.  **Refinamento do Agendamento (Prevenção):**
    *   **O que fazer:** Modificar a lógica de `_schedule_inactivity_followup` em `app/api/webhooks.py`.
    *   **Como:** Em vez de agendar múltiplos follow-ups de uma vez, agende apenas o primeiro (30 minutos). A lógica do `FollowUpExecutorService` deve ser então aprimorada para, caso um follow-up de reengajamento seja enviado e o usuário não responda, ele mesmo agende o próximo da cadeia (o de 24 horas). Isso cria um fluxo sequencial e mais robusto.

A implementação destas soluções resolverá as inconsistências observadas e tornará o sistema de follow-up e lembretes significativamente mais estável e confiável.
