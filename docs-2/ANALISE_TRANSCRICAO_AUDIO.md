# Análise da Transcrição de Áudio e Interpretação pelo Agente

## Diagnóstico do Fluxo Atual

A análise do código-fonte (`app/api/webhooks.py`, `app/agents/agentic_sdr.py`, `app/services/audio_transcriber.py`) revela o seguinte fluxo para o processamento de mensagens de áudio:

1.  **Recebimento da Mensagem de Áudio (`app/api/webhooks.py`)**:
    *   Quando uma mensagem de áudio é recebida via webhook da Evolution API, a função `process_new_message` é acionada.
    *   Dentro de `process_message_with_agent`, o áudio é baixado e codificado em Base64.
    *   Um dicionário `media_data` é criado, contendo o tipo (`"audio"`), o `mimetype`, e os dados do áudio em Base64 (`data`).
    *   A função `agentic.process_message()` é então chamada, passando o `media_data` como um dos argumentos.

2.  **Processamento Multimodal pelo `AgenticSDR` (`app/agents/agentic_sdr.py`)**:
    *   O método `process_multimodal_content(self, media_type, media_data, ...)` é invocado.
    *   Se o `media_type` for `"audio"`, o sistema verifica se a transcrição de voz está habilitada (`settings.enable_voice_message_transcription`).
    *   Em seguida, `audio_transcriber.transcribe_from_base64()` é chamado com os dados do áudio em Base64.
    *   **Ponto Crucial**: Se a transcrição for bem-sucedida (`result["status"] == "success"`), o texto transcrito é extraído (`transcribed_text = result["text"]`).
    *   O método `process_multimodal_content` retorna um dicionário que **inclui** o texto transcrito sob a chave `"transcription"`.

3.  **Serviço de Transcrição de Áudio (`app/services/audio_transcriber.py`)**:
    *   Este serviço é responsável por decodificar o áudio, convertê-lo para um formato processável (se necessário, usando `ffmpeg` para áudios do WhatsApp como Opus) e, finalmente, transcrevê-lo para texto usando `SpeechRecognition` (com fallback para OpenAI Whisper).
    *   A saída é um dicionário contendo o texto transcrito na chave `"text"`.

## Conclusão: A Transcrição Chega ao Agente?

**Sim, a transcrição do áudio está sendo realizada e o texto transcrito é passado para o agente.**

No entanto, há um detalhe importante:

*   O método `extract_message_content` (em `app/api/webhooks.py`) é responsável por extrair o conteúdo da mensagem principal. Para áudios, ele retorna uma string genérica como `"[Nota de voz recebida]"` ou `"[Áudio recebido]"`.
*   Quando `AgenticSDR.process_message` chama `self.team.arun()` (ou `self.agent.run()`), o `message` principal que o agente recebe no `team_prompt` (ou nas `instructions` do agente) é essa string genérica.
*   O texto transcrito do áudio está disponível para o agente, mas dentro do dicionário `multimodal_result` (que é parte do `context` passado para o agente).

**Isso significa que o agente tem acesso ao texto transcrito, mas o prompt principal que guia sua interpretação inicial pode não estar explicitamente direcionado para usar essa transcrição como o conteúdo primário da mensagem do usuário.**

## Recomendação para Melhoria

Para garantir que o agente interprete e formule a resposta com base no conteúdo *transcrito* do áudio de forma otimizada, é fundamental ajustar o prompt do agente (`app/prompts/prompt-agente.md`).

O prompt deve ser instruído a:

1.  **Reconhecer a presença de `multimodal_result` no contexto.**
2.  **Priorizar o `multimodal_result['transcription']` como o conteúdo principal da mensagem do usuário** sempre que `media_type` for `"audio"` e a transcrição estiver disponível.

**Exemplo de como a instrução no prompt poderia ser adaptada (conceitual):**

```
🎵 SE FOR ÁUDIO:
- VOCÊ DEVE UTILIZAR O TEXTO DA TRANSCRIÇÃO DISPONÍVEL NO CONTEXTO PARA ENTENDER A MENSAGEM DO USUÁRIO.
- RESPONDA ao conteúdo do áudio de forma natural.
- SE MENCIONAREM valores de conta, processe como qualificação.
- SE PEDIREM informações, forneça de forma clara.
- MANTENHA a conversa fluida e natural.
- TRATE como se estivesse respondendo a um áudio mesmo.
```
