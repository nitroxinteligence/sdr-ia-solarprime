2025-08-04 11:38:41.298 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📸 IMAGEM DETECTADA - Analisando estrutura...
2025-08-04 11:38:41.298 | INFO     | app.api.webhooks:process_message_with_agent:415 | Campos disponíveis na imageMessage: ['url', 'mimetype', 'fileSha256', 'fileLength', 'height', 'width', 'mediaKey', 'fileEncSha256', 'directPath', 'mediaKeyTimestamp', 'jpegThumbnail', 'contextInfo', 'firstScanSidecar', 'firstScanLength', 'scansSidecar', 'scanLengths', 'midQualityFileSha256', 'imageSourceType']
2025-08-04 11:38:41.299 | INFO     | app.api.webhooks:process_message_with_agent:422 | jpegThumbnail é string, tamanho: 1088 chars
2025-08-04 11:38:41.299 | INFO     | app.api.webhooks:process_message_with_agent:423 | jpegThumbnail primeiros 50 chars: /9j/4AAQSkZJRgABAQAAAQABAAD/2wBDABsSFBcUERsXFhceHB
2025-08-04 11:38:41.299 | INFO     | app.api.webhooks:process_message_with_agent:426 | jpegThumbnail parece ser base64 válido
2025-08-04 11:38:41.299 | INFO     | app.api.webhooks:process_message_with_agent:433 | mediaKey presente: 7GQyoDY8MkBZJA6SOeTq...
2025-08-04 11:38:41.300 | INFO     | app.api.webhooks:process_message_with_agent:435 | directPath presente: /v/t62.7118-24/25387842_752696437341201_4493947754...
2025-08-04 11:38:41.300 | INFO     | app.api.webhooks:process_message_with_agent:437 | URL presente: https://mmg.whatsapp.net/v/t62.7118-24/25387842_75...
2025-08-04 11:38:41.300 | INFO     | app.api.webhooks:detect_media_format:63 | Formato detectado: Base64 válido
2025-08-04 11:38:41.300 | INFO     | app.api.webhooks:process_message_with_agent:445 | 📸 jpegThumbnail formato detectado: base64
2025-08-04 11:38:41.300 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ AGNO Media Detection: ffd8ffe000104a4649460001
2025-08-04 11:38:41.301 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ jpegThumbnail validado como base64: 1088 chars
2025-08-04 11:38:41.301 | INFO     | app.api.webhooks:process_message_with_agent:487 | 🔍 Thumbnail muito pequena (1088 chars), baixando imagem completa...
2025-08-04 11:38:41.301 | INFO     | app.api.webhooks:process_message_with_agent:505 | 🔐 Incluindo mediaKey para descriptografia
2025-08-04 11:38:41.301 | INFO     | app.integrations.evolution:download_media:955 | Baixando mídia de: https://mmg.whatsapp.net/v/t62.7118-24/25387842_75...
2025-08-04 11:38:41.301 | INFO     | app.integrations.evolution:download_media:957 | MediaKey presente - mídia será descriptografada (tipo: image)
2025-08-04 11:38:41.345 | INFO     | app.integrations.evolution:download_media:977 | Mídia baixada com sucesso: 58458 bytes
2025-08-04 11:38:41.347 | INFO     | app.integrations.evolution:download_media:981 | Iniciando descriptografia da mídia...
2025-08-04 11:38:41.348 | INFO     | app.integrations.evolution:decrypt_whatsapp_media:856 | MediaKey decodificada: 32 bytes
2025-08-04 11:38:41.351 | INFO     | app.integrations.evolution:decrypt_whatsapp_media:889 | IV: 16 bytes, Cipher Key: 32 bytes, MAC Key: 32 bytes
2025-08-04 11:38:41.353 | INFO     | app.integrations.evolution:decrypt_whatsapp_media:925 | Mídia descriptografada com sucesso: 58442 bytes
2025-08-04 11:38:41.354 | INFO     | app.integrations.evolution:download_media:989 | Mídia descriptografada com sucesso: 58442 bytes
2025-08-04 11:38:41.354 | INFO     | app.api.webhooks:process_message_with_agent:511 | Imagem baixada, primeiros 20 bytes (hex): ffd8ffe000104a46494600010100000100010000
2025-08-04 11:38:41.355 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ AGNO Media Detection: ffd8ffe000104a4649460001
2025-08-04 11:38:41.355 | INFO     | app.api.webhooks:process_message_with_agent:534 | 🔍 AGNO validou mídia: jpeg
2025-08-04 11:38:41.355 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ Imagem validada (jpeg): 77924 chars
2025-08-04 11:38:41.356 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por phone: 558182986181
2025-08-04 11:38:41.944 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Conversation_id encontrado: 5cb645e6-a5b5-4488-89bb-5ee6239ada6e
2025-08-04 11:38:41.944 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: 5cb645e6-a5b5-4488-89bb-5ee6239ada6e
2025-08-04 11:38:42.523 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Query executada, 9 mensagens encontradas
2025-08-04 11:38:42.525 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por conversation_id: 5cb645e6-a5b5-4488-89bb-5ee6239ada6e
2025-08-04 11:38:42.525 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: 5cb645e6-a5b5-4488-89bb-5ee6239ada6e
2025-08-04 11:38:43.557 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Query executada, 9 mensagens encontradas
2025-08-04 11:38:43.558 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Histórico carregado: 9 mensagens
2025-08-04 11:38:43.558 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ══════════════════════════════════════════════════
2025-08-04 11:38:43.558 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🎯 MULTIMODAL: Iniciando processamento
2025-08-04 11:38:43.558 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📌 Tipo: IMAGE
2025-08-04 11:38:43.558 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📊 Tamanho dados base64: 77,924 caracteres
2025-08-04 11:38:43.559 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 💬 Caption: Sem legenda
2025-08-04 11:38:43.559 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ⏰ Timestamp: 2025-08-04 11:38:43
2025-08-04 11:38:43.559 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ══════════════════════════════════════════════════
2025-08-04 11:38:43.559 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🌆 =============================================
2025-08-04 11:38:43.559 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🌆 PROCESSAMENTO DE IMAGEM INICIADO
2025-08-04 11:38:43.559 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🌆 =============================================
2025-08-04 11:38:43.559 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 IMAGEM - Formato detectado: base64
2025-08-04 11:38:43.560 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📈 IMAGEM - Métricas:
2025-08-04 11:38:43.560 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Base64: 77,924 caracteres
2025-08-04 11:38:43.560 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Estimado: 58,443 bytes (57.1 KB / 0.06 MB)
2025-08-04 11:38:44.317 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 Etapa 1/4: Decodificando base64...
2025-08-04 11:38:44.318 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ Decodificação completa em 0.00s
2025-08-04 11:38:44.318 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Tamanho real: 58,442 bytes
2025-08-04 11:38:44.318 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Taxa compressão: 25.0%
2025-08-04 11:38:44.319 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 Etapa 2/4: Detectando formato da imagem...
2025-08-04 11:38:44.319 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ AGNO Media Detection: ffd8ffe000104a4649460001
2025-08-04 11:38:44.319 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ Formato detectado: JPEG
2025-08-04 11:38:44.319 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Confiança: high
2025-08-04 11:38:44.319 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Tempo detecção: 0.00s
2025-08-04 11:38:44.321 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ AGNO Image processamento falhou: 1 validation error for Image
  Value error, 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte [type=value_error, input_value={'content': '/9j/4AAQSkZJ...jpeg', 'detail': 'high'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.8/v/value_error