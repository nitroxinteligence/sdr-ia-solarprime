
# Plano de Implementação: Reações e Respostas a Mensagens

## 1. Resumo Executivo (TL;DR)

Para implementar reações com emojis e respostas diretas a mensagens específicas, precisamos de uma abordagem em três frentes:

1.  **API e Webhook:** Capturar os dados necessários (como o `id` da mensagem e o `sender`) do payload do webhook da Evolution API quando uma mensagem é recebida.
2.  **Cliente da API (`evolution.py`):** Adicionar dois novos métodos ao nosso `EvolutionAPIClient`:
    *   `send_reaction(phone, message_id, emoji)`: Para enviar uma reação a uma mensagem específica.
    - `send_reply(phone, message_id, text)`: Para enviar uma resposta que cita/marca a mensagem original do usuário.
3.  **Lógica do Agente (`agentic_sdr.py`):** Aprimorar a inteligência do agente para que ele possa decidir *quando* usar essas novas habilidades. Isso envolve:
    *   Analisar o conteúdo e o sentimento da mensagem do usuário para decidir se uma reação (ex: 👍, ❤️, 😂) é apropriada.
    -   Manter o contexto da mensagem que está sendo respondida para que a resposta seja relevante.

Este plano garante uma integração robusta e inteligente, tornando a comunicação do agente muito mais humana e contextual.

---

## 2. Pesquisa e Documentação da Evolution API

Após pesquisa, confirmei que a Evolution API suporta nativamente as funcionalidades de reação e resposta.

### Endpoint de Reação (`/message/sendReaction`)

- **Método:** `POST`
- **Endpoint:** `/message/sendReaction/{instance}`
- **Payload (Corpo da Requisição):**
  ```json
  {
    "reactionMessage": {
      "key": {
        "remoteJid": "5511999999999@s.whatsapp.net",
        "id": "MESSAGE_ID_TO_REACT_TO"
      },
      "reaction": "👍" 
    }
  }
  ```
- **Parâmetros Chave:**
  - `remoteJid`: O número do contato.
  - `id`: O ID da mensagem original à qual queremos reagir.
  - `reaction`: O emoji a ser enviado como reação.

### Endpoint de Resposta/Citação (`/message/sendText` com `options`)

- **Método:** `POST`
- **Endpoint:** `/message/sendText/{instance}`
- **Payload (Corpo da Requisição):
  ```json
  {
    "number": "5511999999999",
    "text": "Esta é a minha resposta à sua pergunta.",
    "options": {
      "quoted": {
        "key": {
          "remoteJid": "5511999999999@s.whatsapp.net",
          "id": "MESSAGE_ID_TO_REPLY_TO"
        }
      }
    }
  }
  ```
- **Parâmetros Chave:**
  - O endpoint é o mesmo de enviar uma mensagem de texto, mas incluímos o objeto `options.quoted`.
  - `options.quoted.key.id`: O ID da mensagem que será citada na resposta.

---

## 3. Plano de Implementação Detalhado

### Passo 1: Capturar Dados Essenciais do Webhook

Precisamos garantir que, ao receber uma mensagem, estamos salvando as informações necessárias para poder reagir ou responder a ela mais tarde.

- **Arquivo a ser modificado:** `app/api/webhooks.py`
- **Função:** `process_new_message`
- **Análise:** A função já extrai o `message_id` e o `remote_jid` do payload. O `message_id` é crucial. Precisamos garantir que ele seja passado para o agente.
- **Ação:** Nenhuma mudança é estritamente necessária aqui, pois a função `process_message_with_agent` já recebe o `message_id` e o `original_message`. O que faremos é usar essa informação na lógica do agente.

### Passo 2: Adicionar Novos Métodos ao Cliente da Evolution API

Vamos adicionar as novas funcionalidades ao nosso cliente para que o agente possa usá-las.

- **Arquivo a ser modificado:** `app/integrations/evolution.py`
- **Classe:** `EvolutionAPIClient`
- **Ação:** Adicionar os dois métodos a seguir à classe:

  ```python
  # Adicionar este método em app/integrations/evolution.py
  async def send_reaction(self, phone: str, message_id: str, emoji: str) -> Dict[str, Any]:
      """
      Envia uma reação a uma mensagem específica.
      """
      try:
          phone = self._format_phone(phone)
          payload = {
              "reactionMessage": {
                  "key": {
                      "remoteJid": f"{phone}@s.whatsapp.net",
                      "id": message_id
                  },
                  "reaction": emoji
              }
          }
          
          response = await self._make_request(
              "post",
              f"/message/sendReaction/{self.instance_name}",
              json=payload
          )
          
          emoji_logger.evolution_send(phone, "reaction", reaction=emoji, message_id=message_id)
          return response
          
      except Exception as e:
          emoji_logger.evolution_error(f"Erro ao enviar reação: {e}")
          return None

  # Adicionar este método em app/integrations/evolution.py
  async def send_reply(self, phone: str, message_id: str, text: str) -> Dict[str, Any]:
      """
      Envia uma resposta citando uma mensagem anterior.
      """
      try:
          phone = self._format_phone(phone)
          payload = {
              "number": phone,
              "text": text,
              "options": {
                  "quoted": {
                      "key": {
                          "remoteJid": f"{phone}@s.whatsapp.net",
                          "id": message_id
                      }
                  }
              }
          }

          # Reutiliza o método send_text_message, mas com o payload de resposta
          # Para isso, vamos modificar send_text_message para aceitar um payload customizado
          return await self.send_text_message(phone, text, payload_override=payload)

      except Exception as e:
          emoji_logger.evolution_error(f"Erro ao enviar resposta: {e}")
          return None
  ```

- **Ação Adicional:** Modificar `send_text_message` para aceitar um `payload_override`.

  ```python
  # Modificar a assinatura e o início de send_text_message em app/integrations/evolution.py
  async def send_text_message(
      self,
      phone: str,
      message: str,
      delay: Optional[float] = None,
      simulate_typing: bool = True,
      payload_override: Optional[Dict[str, Any]] = None
  ) -> Dict[str, Any]:
      try:
          # ... (código de formatação de telefone e delay) ...

          # Simular digitação se habilitado
          if simulate_typing:
              await self.send_typing(phone, len(message))
          
          # Preparar payload
          if payload_override:
              payload = payload_override
          else:
              payload = {
                  "number": phone,
                  "text": message
              }
          
          # ... (restante do código para fazer a requisição) ...
  ```

### Passo 3: Integrar a Lógica no Agente Principal

Esta é a parte mais importante. O agente precisa decidir *quando* e *como* reagir ou responder. Isso será feito através de uma nova ferramenta e da atualização do prompt.

- **Arquivo a ser modificado:** `app/agents/agentic_sdr.py`
- **Classe:** `AgenticSDR`

1.  **Criar uma Nova Ferramenta de Comunicação:**
    Adicionaremos uma nova ferramenta que o agente pode usar para decidir como se comunicar.

    ```python
    # Adicionar este método como uma nova ferramenta em AgenticSDR
    @tool
    async def communicate_with_user(
        self,
        phone: str,
        message_id: str,
        response_text: str,
        should_react: bool = False,
        reaction_emoji: Optional[str] = None,
        should_reply: bool = False
    ) -> Dict[str, Any]:
        """
        Envia uma resposta, e opcionalmente uma reação ou uma resposta direta a uma mensagem anterior.
        Use esta ferramenta para controlar como você se comunica com o usuário.
        - `should_react`: Defina como True para enviar um emoji como reação à mensagem do usuário.
        - `reaction_emoji`: O emoji a ser usado na reação (ex: "👍", "❤️").
        - `should_reply`: Defina como True para citar a mensagem do usuário em sua resposta.
        """
        from app.integrations.evolution import evolution_client

        if should_react and reaction_emoji:
            await evolution_client.send_reaction(phone, message_id, reaction_emoji)
            await asyncio.sleep(0.5) # Pequena pausa após reagir

        if should_reply:
            result = await evolution_client.send_reply(phone, message_id, response_text)
        else:
            result = await evolution_client.send_text_message(phone, response_text)
        
        return {"success": bool(result), "response": result}
    ```

2.  **Atualizar o Prompt do Agente:**
    Precisamos instruir o agente sobre como e quando usar a nova ferramenta `communicate_with_user`.

    - **Arquivo a ser modificado:** `app/prompts/prompt-agente.md`
    - **Ação:** Adicionar uma nova seção ao prompt:

      ```markdown
      ## 🗣️ Comunicação Avançada: Reações e Respostas

      Para tornar a conversa mais natural, você pode reagir a mensagens e respondê-las diretamente.

      **Use a ferramenta `communicate_with_user` para controlar isso:**

      - **Quando Reagir?**
        - Use reações para reconhecer mensagens curtas ou confirmar entendimento sem uma resposta de texto completa.
        - **Exemplos:**
          - Se o usuário diz "Ok, entendi", reaja com `👍`.
          - Se o usuário envia um elogio, reaja com `❤️` ou `😊`.
          - Se o usuário envia algo engraçado, reaja com `😂`.
        - **Como:** Chame `communicate_with_user` com `should_react=True` e o `reaction_emoji` apropriado.

      - **Quando Responder Diretamente (Citar)?**
        - Use respostas diretas para manter o contexto em conversas longas ou para responder a uma pergunta específica que não foi a última mensagem.
        - **Exemplo:** Se o usuário perguntou sobre o preço há 5 mensagens e agora pergunta sobre a instalação, você pode responder à pergunta sobre o preço citando-a.
        - **Como:** Chame `communicate_with_user` com `should_reply=True`.
      ```

3.  **Modificar o Fluxo de Processamento:**
    Finalmente, precisamos ajustar `process_message` para usar a nova ferramenta em vez de chamar `evolution_client.send_text_message` diretamente.

    - **Arquivo a ser modificado:** `app/agents/agentic_sdr.py`
    - **Função:** `process_message`
    - **Ação:** Substitua a lógica de envio de resposta no final da função.

      ```python
      # Em app/agents/agentic_sdr.py -> process_message

      # ... (após a linha `response = await self.agent.run(...)`)

      # REMOVA a lógica antiga de envio que usa `evolution_client.send_text_message`

      # ADICIONE a nova lógica que usa a ferramenta do agente:
      if response:
          # O agente agora decidirá como responder usando a ferramenta
          # O prompt o instruirá a chamar `communicate_with_user`
          # A resposta final já terá sido enviada pela ferramenta.
          emoji_logger.agentic_response(f"Resposta enviada via ferramenta de comunicação: {response}")
      else:
          emoji_logger.system_warning(f"Nenhuma resposta gerada para {phone}")
      ```

---

## 4. Conclusão

Ao seguir estes três passos, o sistema ganhará duas novas capacidades de comunicação que o tornarão significativamente mais humano e interativo. A lógica de quando reagir ou responder ficará a cargo da inteligência do LLM, guiada pelo prompt atualizado, enquanto a infraestrutura de código fornecerá as ferramentas necessárias para executar essas ações de forma confiável.
