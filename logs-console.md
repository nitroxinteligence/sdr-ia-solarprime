2025-08-04 21:14:17.623 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🎵 ÁUDIO DETECTADO - Analisando estrutura...
2025-08-04 21:14:17.623 | INFO     | app.api.webhooks:process_message_with_agent:613 | Campos disponíveis no audioMessage: ['url', 'mimetype', 'fileSha256', 'fileLength', 'seconds', 'ptt', 'mediaKey', 'fileEncSha256', 'directPath', 'mediaKeyTimestamp', 'streamingSidecar', 'waveform']
2025-08-04 21:14:17.623 | INFO     | app.api.webhooks:process_message_with_agent:614 | Mimetype: audio/ogg; codecs=opus
2025-08-04 21:14:17.623 | INFO     | app.api.webhooks:process_message_with_agent:615 | Duração: 4 segundos
2025-08-04 21:14:17.624 | INFO     | app.api.webhooks:process_message_with_agent:616 | É nota de voz (ptt): True
2025-08-04 21:14:17.624 | INFO     | app.api.webhooks:process_message_with_agent:620 | mediaKey presente: AQlvdGtUTDI2kDf76u1y...
2025-08-04 21:14:17.624 | INFO     | app.api.webhooks:process_message_with_agent:622 | directPath presente: /v/t62.7117-24/17616249_796094509412814_2060487594...
2025-08-04 21:14:17.624 | INFO     | app.api.webhooks:process_message_with_agent:641 | 🔐 Incluindo mediaKey para descriptografia de áudio
2025-08-04 21:14:17.625 | INFO     | app.integrations.evolution:download_media:955 | Baixando mídia de: https://mmg.whatsapp.net/v/t62.7117-24/17616249_79...
2025-08-04 21:14:17.625 | INFO     | app.integrations.evolution:download_media:957 | MediaKey presente - mídia será descriptografada (tipo: audio)
2025-08-04 21:14:18.336 | INFO     | app.integrations.evolution:download_media:977 | Mídia baixada com sucesso: 9514 bytes
2025-08-04 21:14:18.336 | INFO     | app.integrations.evolution:download_media:981 | Iniciando descriptografia da mídia...
2025-08-04 21:14:18.337 | INFO     | app.integrations.evolution:decrypt_whatsapp_media:856 | MediaKey decodificada: 32 bytes
2025-08-04 21:14:18.337 | INFO     | app.integrations.evolution:decrypt_whatsapp_media:889 | IV: 16 bytes, Cipher Key: 32 bytes, MAC Key: 32 bytes
2025-08-04 21:14:18.338 | INFO     | app.integrations.evolution:decrypt_whatsapp_media:925 | Mídia descriptografada com sucesso: 9492 bytes
2025-08-04 21:14:18.339 | INFO     | app.integrations.evolution:download_media:989 | Mídia descriptografada com sucesso: 9492 bytes
2025-08-04 21:14:18.340 | INFO     | app.api.webhooks:process_message_with_agent:647 | Áudio baixado, primeiros 20 bytes (hex): 4f67675300020000000000000000640000000000
2025-08-04 21:14:18.340 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ AGNO Media Detection: 4f6767530002000000000000
2025-08-04 21:14:18.341 | INFO     | app.api.webhooks:process_message_with_agent:653 | 🔍 AGNO validou áudio: ogg
2025-08-04 21:14:18.344 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por phone: 558182986181
2025-08-04 21:14:18.563 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Conversation_id encontrado: fff09a52-a2aa-4aa8-9513-0429546068ee
2025-08-04 21:14:18.563 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: fff09a52-a2aa-4aa8-9513-0429546068ee
2025-08-04 21:14:19.146 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Query executada, 7 mensagens encontradas
2025-08-04 21:14:19.148 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por conversation_id: fff09a52-a2aa-4aa8-9513-0429546068ee
2025-08-04 21:14:19.149 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: fff09a52-a2aa-4aa8-9513-0429546068ee
2025-08-04 21:14:19.751 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Query executada, 7 mensagens encontradas
2025-08-04 21:14:19.752 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Histórico carregado: 7 mensagens
2025-08-04 21:14:19.752 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ══════════════════════════════════════════════════
2025-08-04 21:14:19.752 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🎯 MULTIMODAL: Iniciando processamento
2025-08-04 21:14:19.752 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📌 Tipo: AUDIO
2025-08-04 21:14:19.753 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📊 Tamanho dados base64: 12,656 caracteres
2025-08-04 21:14:19.753 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 💬 Caption: Sem legenda
2025-08-04 21:14:19.753 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ⏰ Timestamp: 2025-08-04 21:14:19
2025-08-04 21:14:19.753 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ══════════════════════════════════════════════════
2025-08-04 21:14:19.753 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Processamento de áudio solicitado
2025-08-04 21:14:20.037 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ AudioTranscriber com Google Speech + OpenAI Whisper fallback
2025-08-04 21:14:20.037 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Iniciando transcrição de áudio (audio/ogg)
2025-08-04 21:14:20.038 | INFO     | app.services.audio_transcriber:transcribe_from_base64:121 | ✅ Formato de áudio validado: base64
2025-08-04 21:14:20.038 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ Formato de áudio validado: base64
2025-08-04 21:14:20.040 | INFO     | app.services.audio_transcriber:transcribe_from_base64:176 | 🎵 Detectado áudio Opus/criptografado do WhatsApp, usando ffmpeg...
2025-08-04 21:14:20.174 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Áudio convertido para WAV: 4.4 segundos
2025-08-04 21:14:20.174 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Enviando áudio para Google Speech Recognition...
2025-08-04 21:14:21.110 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ Transcrição concluída: 37 caracteres
2025-08-04 21:14:21.115 | INFO     | app.utils.logger:log_with_emoji:140 | 💭 Decisão: AGENTIC SDR resolve sozinha
2025-08-04 21:14:21.116 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ AGNO Context enhanced: 7 mensagens, quality=poor, score=0.31
2025-08-04 21:14:21.116 | ERROR    | app.utils.retry_handler:wrapper:103 | ❌ _gemini_call_with_retry failed with non-retryable error: 'Gemini' object is not callable
2025-08-04 21:14:21.116 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ ⚠️ Gemini falhou após múltiplas tentativas: 'Gemini' object is not callable
2025-08-04 21:14:21.116 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ 🔄 Ativando fallback OpenAI o3-mini com retry...
2025-08-04 21:14:21.713 | ERROR    | app.utils.retry_handler:wrapper:103 | ❌ _openai_call_with_retry failed with non-retryable error: OpenAI o3-mini falhou: API Error 429: {
    "error": {
        "message": "You exceeded your current quota, please check your plan and billing details. For more information on this error, read the docs: https://platform.openai.com/docs/guides/error-codes/api-errors.",
        "type": "insufficient_quota",
        "param": null,
        "code": "insufficient_quota"
    }
}

2025-08-04 21:14:21.713 | ERROR    | app.utils.logger:log_with_emoji:140 | 💥 Erro em Fallback OpenAI também falhou: OpenAI o3-mini falhou: API Error 429: {
    "error": {
        "message": "You exceeded your current quota, please check your plan and billing details. For more information on this error, read the docs: https://platform.openai.com/docs/guides/error-codes/api-errors.",
        "type": "insufficient_quota",
        "param": null,
        "code": "insufficient_quota"
    }
}
 | Data: {'component': 'Fallback OpenAI também falhou'}
2025-08-04 21:14:21.713 | ERROR    | app.utils.logger:log_with_emoji:140 | 💥 Erro em AGENTIC SDR: Erro ao gerar resposta: OpenAI o3-mini falhou: API Error 429: {
    "error": {
        "message": "You exceeded your current quota, please check your plan and billing details. For more information on this error, read the docs: https://platform.openai.com/docs/guides/error-codes/api-errors.",
        "type": "insufficient_quota",
        "param": null,
        "code": "insufficient_quota"
    }
}
 | Data: {'component': 'AGENTIC SDR'}
2025-08-04 21:14:21.713 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ Nenhuma resposta gerada, usando fallback
2025-08-04 21:14:21.714 | INFO     | app.utils.logger:log_with_emoji:140 | 💬 Resposta: Resposta gerada: Olá! Sou a Helen da Solar Prime. Vi sua mensagem e adoraria ajudar! Você tem interesse em economizar...