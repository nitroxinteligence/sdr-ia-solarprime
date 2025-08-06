
# Análise e Solução do Fluxo de "Typing" no Agente

## 1. Resumo Executivo (TL;DR)

O comportamento atual do "typing" está incorreto devido a **duas chamadas de `send_typing` em momentos errados do fluxo de processamento**. 

1.  **Primeira Chamada (Incorreta):** Ocorre em `app/api/webhooks.py` **antes** do agente processar a mensagem. Isso causa o primeiro "typing" que o usuário vê, que é prematuro e com duração baseada na mensagem *recebida*, não na resposta.
2.  **Segunda Chamada (Correta, mas Redundante):** Ocorre em `app/integrations/evolution.py` **antes** de cada mensagem ser enviada. Esta é a chamada que queremos manter, mas ela atualmente é a *segunda* que o usuário vê.

**A solução proposta envolve:**

1.  **Remover a chamada prematura** de `send_typing` no webhook.
2.  **Centralizar e aprimorar a lógica de `send_typing`** dentro do `EvolutionAPIClient` para que a duração seja calculada dinamicamente com base no tamanho da resposta a ser enviada, exatamente como solicitado.

Isso garantirá que o "typing" apareça apenas uma vez, no momento certo (após o processamento e antes do envio), e com uma duração que simula realisticamente um humano digitando a resposta.

---

## 2. Análise Detalhada do Fluxo Atual (O Problema)

Para entender por que o "typing" se comporta de forma estranha, vamos mapear o fluxo de uma mensagem desde o recebimento até a resposta:

1.  **Recebimento da Mensagem:**
    - O webhook em `app/api/webhooks.py` recebe a mensagem do usuário.
    - A função `process_new_message` é chamada.

2.  **Buffer de Mensagens:**
    - A mensagem é adicionada ao `MessageBuffer` (se ativado).
    - O buffer aguarda um curto período por mais mensagens. Se não houver mais, ele combina o conteúdo e chama `process_message_with_agent`.

3.  **Início do Processamento pelo Agente:**
    - A função `process_message_with_agent` em `app/api/webhooks.py` é executada.
    - **Aqui ocorre o PRIMEIRO ERRO:** O código imediatamente dispara uma tarefa para simular o "typing":
      ```python
      # app/api/webhooks.py -> process_message_with_agent
      # ...
      estimated_processing_time = max(3.0, min(len(message_content) * 0.05, 10.0))
      asyncio.create_task(evolution_client.send_typing(phone, duration_seconds=estimated_processing_time))
      ```
    - **Problema:** Este "typing" é acionado *antes* do agente sequer começar a pensar. A sua duração é calculada com base no tamanho da mensagem do *usuário*, não da resposta do agente.

4.  **Processamento do Agente:**
    - Em seguida, o código chama `agentic.process_message(...)`.
    - Esta chamada pode levar vários segundos, durante os quais o primeiro "typing" (que já foi enviado) termina, e o usuário fica esperando sem ver nenhum indicador.

5.  **Envio da Resposta:**
    - O agente gera a resposta.
    - O código então chama `evolution_client.send_text_message(...)` para enviar a resposta.

6.  **Chamada de Typing Redundante:**
    - Dentro do método `send_text_message` em `app/integrations/evolution.py`, há **outra chamada** para `send_typing`:
      ```python
      # app/integrations/evolution.py -> send_text_message
      if simulate_typing:
          await self.send_typing(phone, len(message))
      ```
    - **Este é o SEGUNDO "typing"**. Ele ocorre no momento correto (logo antes de enviar a mensagem), mas como o primeiro já foi exibido, a experiência do usuário é de um "bug": `typing...` -> (pausa longa) -> `typing...` -> (mensagem chega).

**Em resumo, o fluxo atual é ineficiente e confuso para o usuário final.**

---

## 3. Plano de Ação: Implementando o Fluxo Ideal

Para corrigir o comportamento e implementar a lógica desejada, precisamos centralizar o controle do "typing" e torná-lo dependente do conteúdo da resposta.

### Passo 1: Remover a Chamada de Typing Prematura

A primeira e mais importante correção é eliminar o "typing" que ocorre antes do processamento do agente.

- **Arquivo a ser modificado:** `app/api/webhooks.py`
- **Função:** `process_message_with_agent`
- **Ação:** **Remova completamente** o seguinte bloco de código:

  ```python
  # REMOVER ESTE BLOCO INTEIRO
  try:
      # Estima tempo de processamento baseado no tamanho da mensagem
      estimated_processing_time = max(3.0, min(len(message_content) * 0.05, 10.0))
      emoji_logger.webhook_process(f"Enviando typing por ~{estimated_processing_time:.1f}s enquanto processa...")
      
      # Envia typing sem bloquear o processamento
      asyncio.create_task(evolution_client.send_typing(phone, duration_seconds=estimated_processing_time))
      
  except Exception as typing_error:
      emoji_logger.system_warning(f"Erro ao enviar typing inicial: {typing_error}")
      # Continua mesmo se falhar o typing
  ```

**Resultado:** Isso garante que nenhum "typing" será exibido antes que o agente tenha uma resposta pronta.

### Passo 2: Aprimorar a Lógica de Duração do Typing

Agora, vamos aprimorar a lógica dentro do `EvolutionAPIClient` para que a duração do "typing" seja calculada de forma inteligente, como você especificou.

- **Arquivo a ser modificado:** `app/integrations/evolution.py`
- **Classe:** `EvolutionAPIClient`
- **Ação:** Substituiremos a lógica de cálculo de duração atual por uma nova, mais alinhada com a percepção humana.

1.  **Adicione um novo método auxiliar** dentro da classe `EvolutionAPIClient` para calcular a duração:

    ```python
    def _calculate_humanized_typing_duration(self, message_length: int) -> float:
        """
        Calcula uma duração de "typing" humanizada baseada no tamanho da mensagem.
        """
        if message_length > 500:
            base_duration = 12.0
        elif message_length > 250:
            base_duration = 8.0
        elif message_length > 150:
            base_duration = 5.0
        elif message_length > 50:
            base_duration = 3.0
        else:
            base_duration = 2.0

        # Adicionar uma pequena variação aleatória para mais naturalidade
        variation = base_duration * 0.15
        duration = base_duration + random.uniform(-variation, variation)
        
        return max(1.0, min(duration, 15.0)) # Garante que a duração esteja entre 1 e 15 segundos
    ```

2.  **Modifique o método `send_typing`** para usar esta nova função. Substitua o bloco de cálculo de `duration` existente:

    ```python
    # Em app/integrations/evolution.py -> send_typing

    # SUBSTITUA o bloco de cálculo de `duration`:
    # if duration_seconds:
    #     duration = duration_seconds
    # else:
    #     # ... lógica antiga ...

    # PELA NOVA LÓGICA:
    if not duration_seconds:
        duration = self._calculate_humanized_typing_duration(message_length)
    else:
        duration = duration_seconds
    ```

### Passo 3: Garantir a Chamada Correta

O fluxo de envio de mensagens em `app/api/webhooks.py` já lida corretamente com a divisão de mensagens. Como agora a lógica de `send_typing` está encapsulada e corrigida dentro de `send_text_message`, o comportamento desejado (typing antes de cada chunk) ocorrerá automaticamente.

**Verificação Final (nenhuma alteração necessária aqui):**

```python
# app/api/webhooks.py -> process_message_with_agent

# ... (após a resposta do agente ser recebida)

if settings.enable_message_splitter and len(response) > settings.message_max_length:
    # ...
    for i, chunk in enumerate(chunks):
        # Esta chamada agora acionará o typing correto para cada chunk
        result = await evolution_client.send_text_message(
            phone,
            chunk,
            simulate_typing=True # Garantir que está True
        )
else:
    # Esta chamada acionará o typing correto para a mensagem única
    result = await evolution_client.send_text_message(
        phone,
        response,
        simulate_typing=True # Garantir que está True
    )
```

---

## 4. Resultado Esperado Após as Mudanças

Com as modificações propostas, o fluxo de interação será o seguinte:

1.  O usuário envia uma ou mais mensagens.
2.  O `MessageBuffer` aguarda e combina as mensagens.
3.  O `AgenticSDR` processa o texto combinado para gerar uma resposta (sem nenhum "typing" visível para o usuário neste momento).
4.  O sistema recebe a resposta completa do agente.
5.  Se a resposta for longa, ela é dividida em `chunks`.
6.  Para o **primeiro chunk**:
    a. O método `send_text_message` é chamado.
    b. Dentro dele, `send_typing` é acionado com a duração calculada para o tamanho *deste chunk*.
    c. O usuário vê "digitando..." pela duração correta.
    d. O primeiro chunk da mensagem é enviado.
7.  Para o **segundo chunk** (e subsequentes):
    a. Ocorre um pequeno delay (`message_chunk_delay`).
    b. O método `send_text_message` é chamado novamente.
    c. `send_typing` é acionado novamente, com a duração calculada para o tamanho do *novo chunk*.
    d. O usuário vê "digitando..." novamente.
    e. O segundo chunk é enviado.
8.  O processo se repete até que todas as partes da mensagem sejam entregues.

Este novo fluxo é mais limpo, eficiente e corresponde exatamente à experiência de usuário natural e profissional que você descreveu.
