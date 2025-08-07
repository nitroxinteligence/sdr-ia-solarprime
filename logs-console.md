2025-08-07 15:43:31.754 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📸 IMAGEM DETECTADA - Analisando estrutura...
2025-08-07 15:43:31.754 | INFO     | app.api.webhooks:process_message_with_agent:554 | Campos disponíveis na imageMessage: ['url', 'mimetype', 'caption', 'fileSha256', 'fileLength', 'height', 'width', 'mediaKey', 'fileEncSha256', 'directPath', 'mediaKeyTimestamp', 'jpegThumbnail', 'contextInfo', 'firstScanSidecar', 'firstScanLength', 'scansSidecar', 'scanLengths', 'midQualityFileSha256', 'imageSourceType']
2025-08-07 15:43:31.755 | INFO     | app.api.webhooks:process_message_with_agent:561 | jpegThumbnail é string, tamanho: 960 chars
2025-08-07 15:43:31.755 | INFO     | app.api.webhooks:process_message_with_agent:562 | jpegThumbnail primeiros 50 chars: /9j/4AAQSkZJRgABAQAAAQABAAD/2wBDABsSFBcUERsXFhceHB
2025-08-07 15:43:31.755 | INFO     | app.api.webhooks:process_message_with_agent:565 | jpegThumbnail parece ser base64 válido
2025-08-07 15:43:31.755 | INFO     | app.api.webhooks:process_message_with_agent:572 | mediaKey presente: 0pomlp/C41alGUXGXJRS...
2025-08-07 15:43:31.755 | INFO     | app.api.webhooks:process_message_with_agent:574 | directPath presente: /o1/v/t24/f2/m231/AQODWOx8Idn7nPIh46WNe6Ze7uKKlR81...
2025-08-07 15:43:31.755 | INFO     | app.api.webhooks:process_message_with_agent:576 | URL presente: https://mmg.whatsapp.net/o1/v/t24/f2/m231/AQODWOx8...
2025-08-07 15:43:31.755 | INFO     | app.api.webhooks:process_message_with_agent:597 | 🔐 Incluindo mediaKey para descriptografia
2025-08-07 15:43:31.756 | INFO     | app.integrations.evolution:download_media:1043 | Baixando mídia de: https://mmg.whatsapp.net/o1/v/t24/f2/m231/AQODWOx8...
2025-08-07 15:43:31.756 | INFO     | app.integrations.evolution:download_media:1045 | MediaKey presente - mídia será descriptografada (tipo: image)
2025-08-07 15:43:35.027 | INFO     | app.integrations.evolution:download_media:1065 | Mídia baixada com sucesso: 1008266 bytes
2025-08-07 15:43:35.027 | INFO     | app.integrations.evolution:download_media:1069 | Iniciando descriptografia da mídia...
2025-08-07 15:43:35.027 | INFO     | app.integrations.evolution:decrypt_whatsapp_media:944 | MediaKey decodificada: 32 bytes
2025-08-07 15:43:35.028 | INFO     | app.integrations.evolution:decrypt_whatsapp_media:977 | IV: 16 bytes, Cipher Key: 32 bytes, MAC Key: 32 bytes
2025-08-07 15:43:35.031 | INFO     | app.integrations.evolution:decrypt_whatsapp_media:1013 | Mídia descriptografada com sucesso: 1008245 bytes
2025-08-07 15:43:35.032 | INFO     | app.integrations.evolution:download_media:1077 | Mídia descriptografada com sucesso: 1008245 bytes
2025-08-07 15:43:35.032 | INFO     | app.api.webhooks:process_message_with_agent:603 | Imagem baixada, primeiros 20 bytes (hex): ffd8ffe000104a46494600010100000100010000
2025-08-07 15:43:35.048 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ AGNO Media Detection: ffd8ffe000104a4649460001
2025-08-07 15:43:35.048 | INFO     | app.api.webhooks:process_message_with_agent:640 | 🔍 AGNO validou mídia: jpeg
2025-08-07 15:43:35.049 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ Imagem validada (jpeg): 1344328 chars
2025-08-07 15:43:35.277 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por phone: 558182986181
2025-08-07 15:43:35.483 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Conversation_id encontrado: daf3b279-53d3-4d73-b011-9c8a7c17744c
2025-08-07 15:43:35.484 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: daf3b279-53d3-4d73-b011-9c8a7c17744c
2025-08-07 15:43:35.703 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Query executada, 13 mensagens encontradas (limite solicitado: 100)
2025-08-07 15:43:35.703 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ Apenas 13 mensagens disponíveis (menos que o limite de 100)
2025-08-07 15:43:35.704 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por conversation_id: daf3b279-53d3-4d73-b011-9c8a7c17744c
2025-08-07 15:43:35.704 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: daf3b279-53d3-4d73-b011-9c8a7c17744c
2025-08-07 15:43:35.918 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Query executada, 13 mensagens encontradas (limite solicitado: 100)
2025-08-07 15:43:35.918 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ Apenas 13 mensagens disponíveis (menos que o limite de 100)
2025-08-07 15:43:35.918 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Histórico carregado: 13 mensagens
2025-08-07 15:43:35.919 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🎯 MULTIMODAL: Iniciando processamento
2025-08-07 15:43:35.919 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📌 Tipo: IMAGE
2025-08-07 15:43:35.919 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📊 Tamanho dados base64: 1,344,328 caracteres
2025-08-07 15:43:35.919 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 💬 Caption: Sim, ta aqui
2025-08-07 15:43:35.920 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ⏰ Timestamp: 2025-08-07 15:43:35
2025-08-07 15:43:35.920 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ══════════════════════════════════════════════════
2025-08-07 15:43:35.920 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🌆 =============================================
2025-08-07 15:43:35.920 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🌆 PROCESSAMENTO DE IMAGEM INICIADO
2025-08-07 15:43:35.920 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🌆 =============================================
2025-08-07 15:43:35.921 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 IMAGEM - Formato detectado: base64
2025-08-07 15:43:35.921 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📈 IMAGEM - Métricas:
2025-08-07 15:43:35.921 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Base64: 1,344,328 caracteres
2025-08-07 15:43:35.921 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Estimado: 1,008,246 bytes (984.6 KB / 0.96 MB)
2025-08-07 15:43:35.947 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📐 IMAGEM - Dimensões: 2268x4032 pixels
2025-08-07 15:43:36.344 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 Etapa 1/4: Decodificando base64...
2025-08-07 15:43:36.363 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ Decodificação completa em 0.02s
2025-08-07 15:43:36.363 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Tamanho real: 1,008,245 bytes
2025-08-07 15:43:36.363 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Taxa compressão: 25.0%
2025-08-07 15:43:36.363 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 Etapa 2/4: Detectando formato da imagem...
2025-08-07 15:43:36.364 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ AGNO Media Detection: ffd8ffe000104a4649460001
2025-08-07 15:43:36.364 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ Formato detectado: JPEG
2025-08-07 15:43:36.364 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Confiança: high
2025-08-07 15:43:36.364 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Tempo detecção: 0.00s
2025-08-07 15:43:36.364 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔧 Usando PIL + Gemini direto (correção implementada)
2025-08-07 15:43:36.374 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📤 Enviando imagem para Gemini Vision com prompt otimizado...
2025-08-07 15:43:56.237 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ PIL + Gemini direto: Sucesso (latência otimizada)
2025-08-07 15:43:57.539 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ══════════════════════════════════════════════════
2025-08-07 15:43:57.540 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ MULTIMODAL: Processamento concluído
2025-08-07 15:43:57.540 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Tipo: image
2025-08-07 15:43:57.540 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Status: success
2025-08-07 15:43:57.540 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Tempo total: 21.62s
2025-08-07 15:43:57.540 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ══════════════════════════════════════════════════
2025-08-07 15:43:57.541 | INFO     | app.utils.logger:log_with_emoji:140 | 💭 Decisão: AGENTIC SDR resolve sozinha
INFO:     127.0.0.1:49316 - "GET /health HTTP/1.1" 200 OK
WARNING  MemoryDb not provided.                                                 
2025-08-07 15:44:25.672 | INFO     | app.utils.logger:log_with_emoji:140 | 💬 Resposta: Resposta gerada: <RESPOSTA_FINAL>Perfeito, Mateus! Vi aqui sua conta da Celpe no valor de *R$458,20*. Com a nossa Ass...
2025-08-07 15:44:25.927 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando emoji para reaction | Data: {'reaction': '✅', 'recipient': 'reaction', 'type': 'emoji'}
INFO:     127.0.0.1:41186 - "GET /health HTTP/1.1" 200 OK