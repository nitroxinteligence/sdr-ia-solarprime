2025-08-04 03:42:14.490 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🎵 ÁUDIO DETECTADO - Analisando estrutura...
2025-08-04 03:42:14.490 | INFO     | app.api.webhooks:process_message_with_agent:569 | Campos disponíveis no audioMessage: ['url', 'mimetype', 'fileSha256', 'fileLength', 'seconds', 'ptt', 'mediaKey', 'fileEncSha256', 'directPath', 'mediaKeyTimestamp', 'streamingSidecar', 'waveform']
2025-08-04 03:42:14.491 | INFO     | app.api.webhooks:process_message_with_agent:570 | Mimetype: audio/ogg; codecs=opus
2025-08-04 03:42:14.491 | INFO     | app.api.webhooks:process_message_with_agent:571 | Duração: 6 segundos
2025-08-04 03:42:14.491 | INFO     | app.api.webhooks:process_message_with_agent:572 | É nota de voz (ptt): True
2025-08-04 03:42:14.491 | INFO     | app.api.webhooks:process_message_with_agent:576 | mediaKey presente: KgAIdLf7qYQxZswFjR6U...
2025-08-04 03:42:14.491 | INFO     | app.api.webhooks:process_message_with_agent:578 | directPath presente: /v/t62.7117-24/13202611_1087617640177574_383771000...
2025-08-04 03:42:14.491 | INFO     | app.integrations.evolution:download_media:853 | Baixando mídia de: https://mmg.whatsapp.net/v/t62.7117-24/13202611_10...
2025-08-04 03:42:15.373 | INFO     | app.integrations.evolution:download_media:873 | Mídia baixada com sucesso: 13674 bytes
2025-08-04 03:42:15.374 | INFO     | app.api.webhooks:process_message_with_agent:592 | Áudio baixado, primeiros 20 bytes (hex): af5c08b73e14b919b47b86d72a90f4a8321687f2
2025-08-04 03:42:15.374 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ AGNO Media Detection: af5c08b73e14b919b47b86d7
2025-08-04 03:42:15.374 | WARNING  | app.api.webhooks:process_message_with_agent:600 | ⚠️ AGNO não reconheceu formato do áudio: af5c08b73e14b919b47b86d7, continuando...
2025-08-04 03:42:15.375 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por phone: 558182986181
2025-08-04 03:42:15.583 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Conversation_id encontrado: 5cb645e6-a5b5-4488-89bb-5ee6239ada6e
2025-08-04 03:42:15.584 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: 5cb645e6-a5b5-4488-89bb-5ee6239ada6e
2025-08-04 03:42:16.563 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Query executada, 19 mensagens encontradas
2025-08-04 03:42:16.565 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por conversation_id: 5cb645e6-a5b5-4488-89bb-5ee6239ada6e
2025-08-04 03:42:16.565 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: 5cb645e6-a5b5-4488-89bb-5ee6239ada6e
2025-08-04 03:42:17.541 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Query executada, 19 mensagens encontradas
2025-08-04 03:42:17.541 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Histórico carregado: 19 mensagens
2025-08-04 03:42:17.542 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ══════════════════════════════════════════════════
2025-08-04 03:42:17.542 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🎯 MULTIMODAL: Iniciando processamento
2025-08-04 03:42:17.542 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📌 Tipo: AUDIO
2025-08-04 03:42:17.542 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📊 Tamanho dados base64: 18,232 caracteres
2025-08-04 03:42:17.542 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 💬 Caption: Sem legenda
2025-08-04 03:42:17.542 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ⏰ Timestamp: 2025-08-04 03:42:17
2025-08-04 03:42:17.542 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ══════════════════════════════════════════════════
2025-08-04 03:42:17.542 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Processamento de áudio solicitado
2025-08-04 03:42:17.562 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ AudioTranscriber inicializado com SpeechRecognition
2025-08-04 03:42:17.563 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Iniciando transcrição de áudio (audio/ogg)
2025-08-04 03:42:17.563 | INFO     | app.services.audio_transcriber:transcribe_from_base64:106 | ✅ Formato de áudio validado: base64
2025-08-04 03:42:17.563 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ Formato de áudio validado: base64
2025-08-04 03:42:18.428 | ERROR    | app.services.audio_transcriber:transcribe_from_base64:164 | Erro ao converter áudio: Não foi possível carregar o áudio em nenhum formato
2025-08-04 03:42:18.428 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ ❌ ÁUDIO: Erro na transcrição
2025-08-04 03:42:18.429 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️   • Erro: Erro ao processar formato de áudio: Não foi possível carregar o áudio em nenhum formato
2025-08-04 03:42:18.429 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️   • Tempo total: 0.89s