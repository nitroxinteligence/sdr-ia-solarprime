2025-08-04 20:37:08.307 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🎵 ÁUDIO DETECTADO - Analisando estrutura...
2025-08-04 20:37:08.307 | INFO     | app.api.webhooks:process_message_with_agent:613 | Campos disponíveis no audioMessage: ['url', 'mimetype', 'fileSha256', 'fileLength', 'seconds', 'ptt', 'mediaKey', 'fileEncSha256', 'directPath', 'mediaKeyTimestamp', 'streamingSidecar', 'waveform']
2025-08-04 20:37:08.307 | INFO     | app.api.webhooks:process_message_with_agent:614 | Mimetype: audio/ogg; codecs=opus
2025-08-04 20:37:08.307 | INFO     | app.api.webhooks:process_message_with_agent:615 | Duração: 5 segundos
2025-08-04 20:37:08.308 | INFO     | app.api.webhooks:process_message_with_agent:616 | É nota de voz (ptt): True
2025-08-04 20:37:08.308 | INFO     | app.api.webhooks:process_message_with_agent:620 | mediaKey presente: 2vgd/95760zsvdoNcjZq...
2025-08-04 20:37:08.308 | INFO     | app.api.webhooks:process_message_with_agent:622 | directPath presente: /v/t62.7117-24/21315874_1162308139033821_593660086...
2025-08-04 20:37:08.309 | INFO     | app.api.webhooks:process_message_with_agent:641 | 🔐 Incluindo mediaKey para descriptografia de áudio
2025-08-04 20:37:08.309 | INFO     | app.integrations.evolution:download_media:955 | Baixando mídia de: https://mmg.whatsapp.net/v/t62.7117-24/21315874_11...
2025-08-04 20:37:08.309 | INFO     | app.integrations.evolution:download_media:957 | MediaKey presente - mídia será descriptografada (tipo: audio)
2025-08-04 20:37:09.020 | INFO     | app.integrations.evolution:download_media:977 | Mídia baixada com sucesso: 12202 bytes
2025-08-04 20:37:09.021 | INFO     | app.integrations.evolution:download_media:981 | Iniciando descriptografia da mídia...
2025-08-04 20:37:09.021 | INFO     | app.integrations.evolution:decrypt_whatsapp_media:856 | MediaKey decodificada: 32 bytes
2025-08-04 20:37:09.022 | INFO     | app.integrations.evolution:decrypt_whatsapp_media:889 | IV: 16 bytes, Cipher Key: 32 bytes, MAC Key: 32 bytes
2025-08-04 20:37:09.022 | INFO     | app.integrations.evolution:decrypt_whatsapp_media:925 | Mídia descriptografada com sucesso: 12189 bytes
2025-08-04 20:37:09.022 | INFO     | app.integrations.evolution:download_media:989 | Mídia descriptografada com sucesso: 12189 bytes
2025-08-04 20:37:09.023 | INFO     | app.api.webhooks:process_message_with_agent:647 | Áudio baixado, primeiros 20 bytes (hex): 4f67675300020000000000000000640000000000
2025-08-04 20:37:09.023 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ AGNO Media Detection: 4f6767530002000000000000
2025-08-04 20:37:09.023 | INFO     | app.api.webhooks:process_message_with_agent:653 | 🔍 AGNO validou áudio: ogg
2025-08-04 20:37:09.024 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por phone: 558182986181
2025-08-04 20:37:09.263 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Conversation_id encontrado: fff09a52-a2aa-4aa8-9513-0429546068ee
2025-08-04 20:37:09.263 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: fff09a52-a2aa-4aa8-9513-0429546068ee
2025-08-04 20:37:09.692 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Query executada, 3 mensagens encontradas
2025-08-04 20:37:09.693 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por conversation_id: fff09a52-a2aa-4aa8-9513-0429546068ee
2025-08-04 20:37:09.693 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: fff09a52-a2aa-4aa8-9513-0429546068ee
2025-08-04 20:37:10.114 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Query executada, 3 mensagens encontradas
2025-08-04 20:37:10.114 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Histórico carregado: 3 mensagens
2025-08-04 20:37:10.114 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ══════════════════════════════════════════════════
2025-08-04 20:37:10.115 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🎯 MULTIMODAL: Iniciando processamento
2025-08-04 20:37:10.115 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📌 Tipo: AUDIO
2025-08-04 20:37:10.115 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📊 Tamanho dados base64: 16,252 caracteres
2025-08-04 20:37:10.115 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 💬 Caption: Sem legenda
2025-08-04 20:37:10.115 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ⏰ Timestamp: 2025-08-04 20:37:10
2025-08-04 20:37:10.115 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ══════════════════════════════════════════════════
2025-08-04 20:37:10.115 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Processamento de áudio solicitado
2025-08-04 20:37:10.116 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Iniciando transcrição de áudio (audio/ogg)
2025-08-04 20:37:10.116 | INFO     | app.services.audio_transcriber:transcribe_from_base64:107 | ✅ Formato de áudio validado: base64
2025-08-04 20:37:10.116 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ Formato de áudio validado: base64
2025-08-04 20:37:10.116 | INFO     | app.services.audio_transcriber:transcribe_from_base64:162 | 🎵 Detectado áudio Opus/criptografado do WhatsApp, usando ffmpeg...
2025-08-04 20:37:10.236 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Áudio convertido para WAV: 5.3 segundos
2025-08-04 20:37:10.237 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Enviando áudio para Google Speech Recognition...
2025-08-04 20:37:11.622 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ Transcrição concluída: 64 caracteres
INFO:     10.11.0.4:38196 - "POST /webhook/kommo/events HTTP/1.1" 200 OK
2025-08-04 20:37:14.875 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando typing para 558182986181 | Data: {'duration_seconds': 3.0, 'message_length': 0, 'recipient': '558182986181', 'type': 'typing'}
2025-08-04 20:37:20.940 | INFO     | app.services.kommo_auto_sync:sync_lead_updates:320 | 📝 1 leads atualizados para sincronizar
INFO:     10.11.0.4:39230 - "POST /webhook/kommo/events HTTP/1.1" 200 OK
2025-08-04 20:37:22.597 | INFO     | app.teams.agents.crm_enhanced:add_tags_to_lead:204 | ✅ Tags adicionadas ao lead 1941856: []
2025-08-04 20:37:23.183 | INFO     | app.services.kommo_auto_sync:_move_to_correct_stage:294 | 📍 Lead 1941856 movido para estágio novo_lead
2025-08-04 20:37:23.183 | INFO     | app.services.kommo_auto_sync:_sync_lead_updates:345 | 🔄 Lead 84964647-0999-4f53-bab9-f5a031d037c3 atualizado no Kommo
WARNING  MemoryDb not provided.                                                 
INFO:     127.0.0.1:52666 - "GET /health HTTP/1.1" 200 OK
ERROR    Rate limit error from OpenAI API: Error code: 429 - {'error':          
         {'message': 'You exceeded your current quota, please check your plan   
         and billing details. For more information on this error, read the docs:
         https://platform.openai.com/docs/guides/error-codes/api-errors.',      
         'type': 'insufficient_quota', 'param': None, 'code':                   
         'insufficient_quota'}}                                                 
WARNING  Attempt 1/1 failed: You exceeded your current quota, please check your 
         plan and billing details. For more information on this error, read the 
         docs: https://platform.openai.com/docs/guides/error-codes/api-errors.  
ERROR    Failed after 1 attempts. Last error using OpenAIChat(gpt-4o)           
2025-08-04 20:37:26.504 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ Erro ao transcrever áudio: You exceeded your current quota, please check your plan and billing details. For more information on this error, read the docs: https://platform.openai.com/docs/guides/error-codes/api-errors.
2025-08-04 20:37:26.505 | INFO     | app.utils.logger:log_with_emoji:140 | 💭 Decisão: AGENTIC SDR resolve sozinha
2025-08-04 20:37:26.505 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ AGNO Context enhanced: 3 mensagens, quality=minimal, score=0.26
2025-08-04 20:37:26.772 | ERROR    | app.utils.retry_handler:wrapper:103 | ❌ _openai_call_with_retry failed with non-retryable error: OpenAI o3-mini falhou: API Error 429: {
    "error": {
        "message": "You exceeded your current quota, please check your plan and billing details. For more information on this error, read the docs: https://platform.openai.com/docs/guides/error-codes/api-errors.",
        "type": "insufficient_quota",
        "param": null,
        "code": "insufficient_quota"
    }
}

2025-08-04 20:37:26.773 | ERROR    | app.utils.logger:log_with_emoji:140 | 💥 Erro em Fallback OpenAI falhou após múltiplas tentativas: OpenAI o3-mini falhou: API Error 429: {
    "error": {
        "message": "You exceeded your current quota, please check your plan and billing details. For more information on this error, read the docs: https://platform.openai.com/docs/guides/error-codes/api-errors.",
        "type": "insufficient_quota",
        "param": null,
        "code": "insufficient_quota"
    }
}
 | Data: {'component': 'Fallback OpenAI falhou após múltiplas tentativas'}
2025-08-04 20:37:26.773 | ERROR    | app.utils.logger:log_with_emoji:140 | 💥 Erro em AGENTIC SDR: Erro ao gerar resposta: OpenAI o3-mini falhou: API Error 429: {
    "error": {
        "message": "You exceeded your current quota, please check your plan and billing details. For more information on this error, read the docs: https://platform.openai.com/docs/guides/error-codes/api-errors.",
        "type": "insufficient_quota",
        "param": null,
        "code": "insufficient_quota"
    }
}
 | Data: {'component': 'AGENTIC SDR'}
2025-08-04 20:37:26.773 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ Nenhuma resposta gerada, usando fallback
2025-08-04 20:37:26.774 | INFO     | app.utils.logger:log_with_emoji:140 | 💬 Resposta: Resposta gerada: Olá! Sou a Helen da Solar Prime. Vi sua mensagem e adoraria ajudar! Você tem interesse em economizar...
2025-08-04 20:37:36.167 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'message_length': 135, 'delay_used': 5.0, 'recipient': '558182986181', 'type': 'text'}
2025-08-04 20:37:36.167 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando text para 558182986181 | Data: {'preview': 'Olá! Sou a Helen da Solar Prime. Vi sua mensagem e', 'recipient': '558182986181', 'type': 'text'}
2025-08-04 20:37:36.169 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Mensagem enviada com sucesso. ID: 3EB05EF7042ED1955A3D91F0689D0486900B9EBC
2025-08-04 20:37:36.391 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/send-message de evolution-api | Data: {'event': 'SEND_MESSAGE', 'endpoint': '/whatsapp/send-message', 'source': 'evolution-api'}
2025-08-04 20:37:36.392 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:184 | Evento não reconhecido: SEND_MESSAGE
INFO:     10.11.0.4:41810 - "POST /webhook/whatsapp/send-message HTTP/1.1" 200 OK