2025-08-07 18:23:43.330 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📸 IMAGEM DETECTADA - Analisando estrutura...
2025-08-07 18:23:43.330 | INFO     | app.api.webhooks:process_message_with_agent:604 | Campos disponíveis na imageMessage: ['url', 'mimetype', 'fileSha256', 'fileLength', 'height', 'width', 'mediaKey', 'fileEncSha256', 'directPath', 'mediaKeyTimestamp', 'jpegThumbnail', 'contextInfo', 'firstScanSidecar', 'firstScanLength', 'scansSidecar', 'scanLengths', 'midQualityFileSha256', 'imageSourceType']
2025-08-07 18:23:43.331 | INFO     | app.api.webhooks:process_message_with_agent:611 | jpegThumbnail é string, tamanho: 960 chars
2025-08-07 18:23:43.331 | INFO     | app.api.webhooks:process_message_with_agent:612 | jpegThumbnail primeiros 50 chars: /9j/4AAQSkZJRgABAQAAAQABAAD/2wBDABsSFBcUERsXFhceHB
2025-08-07 18:23:43.331 | INFO     | app.api.webhooks:process_message_with_agent:615 | jpegThumbnail parece ser base64 válido
2025-08-07 18:23:43.331 | INFO     | app.api.webhooks:process_message_with_agent:622 | mediaKey presente: 0pomlp/C41alGUXGXJRS...
2025-08-07 18:23:43.331 | INFO     | app.api.webhooks:process_message_with_agent:624 | directPath presente: /o1/v/t24/f2/m231/AQODWOx8Idn7nPIh46WNe6Ze7uKKlR81...
2025-08-07 18:23:43.331 | INFO     | app.api.webhooks:process_message_with_agent:626 | URL presente: https://mmg.whatsapp.net/o1/v/t24/f2/m231/AQODWOx8...
2025-08-07 18:23:43.332 | INFO     | app.api.webhooks:process_message_with_agent:647 | 🔐 Incluindo mediaKey para descriptografia
2025-08-07 18:23:43.332 | INFO     | app.integrations.evolution:download_media:1057 | Baixando mídia de: https://mmg.whatsapp.net/o1/v/t24/f2/m231/AQODWOx8...
2025-08-07 18:23:43.332 | INFO     | app.integrations.evolution:download_media:1059 | MediaKey presente - mídia será descriptografada (tipo: image)
2025-08-07 18:23:45.248 | INFO     | app.integrations.evolution:download_media:1079 | Mídia baixada com sucesso: 1008266 bytes
2025-08-07 18:23:45.249 | INFO     | app.integrations.evolution:download_media:1083 | Iniciando descriptografia da mídia...
2025-08-07 18:23:45.249 | INFO     | app.integrations.evolution:decrypt_whatsapp_media:958 | MediaKey decodificada: 32 bytes
2025-08-07 18:23:45.249 | INFO     | app.integrations.evolution:decrypt_whatsapp_media:991 | IV: 16 bytes, Cipher Key: 32 bytes, MAC Key: 32 bytes
2025-08-07 18:23:45.250 | INFO     | app.integrations.evolution:decrypt_whatsapp_media:1027 | Mídia descriptografada com sucesso: 1008245 bytes
2025-08-07 18:23:45.251 | INFO     | app.integrations.evolution:download_media:1091 | Mídia descriptografada com sucesso: 1008245 bytes
2025-08-07 18:23:45.251 | INFO     | app.api.webhooks:process_message_with_agent:653 | Imagem baixada, primeiros 20 bytes (hex): ffd8ffe000104a46494600010100000100010000
2025-08-07 18:23:45.257 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ AGNO Media Detection: ffd8ffe000104a4649460001
2025-08-07 18:23:45.257 | INFO     | app.api.webhooks:process_message_with_agent:690 | 🔍 AGNO validou mídia: jpeg
2025-08-07 18:23:45.257 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ Imagem validada (jpeg): 1344328 chars
2025-08-07 18:23:45.481 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por phone: 558182986181
2025-08-07 18:23:45.711 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Conversation_id encontrado: f8d38c51-e842-45e6-8f96-154a18f70dd9
2025-08-07 18:23:45.711 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: f8d38c51-e842-45e6-8f96-154a18f70dd9
2025-08-07 18:23:47.337 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Query executada, 9 mensagens encontradas (limite solicitado: 100)
2025-08-07 18:23:47.338 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ Apenas 9 mensagens disponíveis (menos que o limite de 100)
2025-08-07 18:23:47.338 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por conversation_id: f8d38c51-e842-45e6-8f96-154a18f70dd9
2025-08-07 18:23:47.339 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: f8d38c51-e842-45e6-8f96-154a18f70dd9
2025-08-07 18:23:48.979 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Query executada, 9 mensagens encontradas (limite solicitado: 100)
2025-08-07 18:23:48.980 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ Apenas 9 mensagens disponíveis (menos que o limite de 100)
2025-08-07 18:23:48.980 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Histórico carregado: 9 mensagens
2025-08-07 18:23:48.980 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🎯 MULTIMODAL: Iniciando processamento
2025-08-07 18:23:48.981 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📌 Tipo: IMAGE
2025-08-07 18:23:48.981 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📊 Tamanho dados base64: 1,344,328 caracteres
2025-08-07 18:23:48.981 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 💬 Caption: Sem legenda
2025-08-07 18:23:48.981 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ⏰ Timestamp: 2025-08-07 18:23:48
2025-08-07 18:23:48.981 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ══════════════════════════════════════════════════
2025-08-07 18:23:48.982 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🌆 =============================================
2025-08-07 18:23:48.982 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🌆 PROCESSAMENTO DE IMAGEM INICIADO
2025-08-07 18:23:48.982 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🌆 =============================================
2025-08-07 18:23:48.982 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 IMAGEM - Formato detectado: base64
2025-08-07 18:23:48.983 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📈 IMAGEM - Métricas:
2025-08-07 18:23:48.983 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Base64: 1,344,328 caracteres
2025-08-07 18:23:48.983 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Estimado: 1,008,246 bytes (984.6 KB / 0.96 MB)
2025-08-07 18:23:48.986 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📐 IMAGEM - Dimensões: 2268x4032 pixels
2025-08-07 18:23:48.986 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 Etapa 1/4: Decodificando base64...
2025-08-07 18:23:48.990 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ Decodificação completa em 0.00s
2025-08-07 18:23:48.990 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Tamanho real: 1,008,245 bytes
2025-08-07 18:23:48.990 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Taxa compressão: 25.0%
2025-08-07 18:23:48.990 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 Etapa 2/4: Detectando formato da imagem...
2025-08-07 18:23:48.991 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ AGNO Media Detection: ffd8ffe000104a4649460001
2025-08-07 18:23:48.991 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ Formato detectado: JPEG
2025-08-07 18:23:48.991 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Confiança: high
2025-08-07 18:23:48.991 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Tempo detecção: 0.00s
2025-08-07 18:23:48.992 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔧 Usando PIL + Gemini direto (correção implementada)
2025-08-07 18:23:48.998 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📤 Enviando imagem para Gemini Vision com prompt otimizado...
2025-08-07 18:24:03.839 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ PIL + Gemini direto: Sucesso (latência otimizada)
2025-08-07 18:24:03.839 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 💰 Valor da conta detectado: R$ 350.81
2025-08-07 18:24:05.547 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ══════════════════════════════════════════════════
2025-08-07 18:24:05.547 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ MULTIMODAL: Processamento concluído
2025-08-07 18:24:05.547 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Tipo: image
2025-08-07 18:24:05.548 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Status: success
2025-08-07 18:24:05.548 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️   • Tempo total: 16.57s
2025-08-07 18:24:05.548 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ══════════════════════════════════════════════════
2025-08-07 18:24:05.548 | INFO     | app.utils.logger:log_with_emoji:140 | 💭 Decisão: AGENTIC SDR resolve sozinha
2025-08-07 18:24:05.548 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ Análise multimodal incluída no contexto formatado
2025-08-07 18:24:05.549 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📝 Prompt para o agente (primeiros 500 chars): 
                    CONTEXTO DO LEAD:
                    - Nome: None
                    - Telefone: 558182986181
                    - Estágio: EM_QUALIFICACAO
                    - Status: PENDING
                    
                    === ANÁLISE MULTIMODAL RECEBIDA ===
TIPO: BILL_IMAGE
ANÁLISE: Aqui está uma análise estruturada da imagem fornecida:

**- Tipo de documento:** DANFE - Documento Auxiliar da Nota Fiscal de Energia Elétrica Eletrônica

**- Valores encontrados:**

* Total a pa...
2025-08-07 18:24:05.549 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📏 Tamanho do prompt: 5407 caracteres
2025-08-07 18:24:05.549 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ ✅ Multimodal incluído no prompt: Aqui está uma análise estruturada da imagem fornecida:

**- Tipo de documento:** DANFE - Documento Auxiliar da Nota Fiscal de Energia Elétrica Eletrônica

**- Valores encontrados:**

* Total a pagar: ...
2025-08-07 18:24:05.549 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🖼️ Multimodal incluído no prompt: tipo=bill_image, tem conteúdo=True
2025-08-07 18:24:05.549 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🚀 Preparando para chamar agent.arun...
2025-08-07 18:24:05.549 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📝 Agent tem instructions? True
2025-08-07 18:24:05.550 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📝 Agent tem memory? True
2025-08-07 18:24:05.550 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📝 Agent tem model? True
2025-08-07 18:24:05.550 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🚀 Chamando agent.arun com timeout de 30s...
INFO:     127.0.0.1:41720 - "GET /health HTTP/1.1" 200 OK
INFO:     127.0.0.1:58282 - "GET /health HTTP/1.1" 200 OK
2025-08-07 18:24:35.616 | ERROR    | app.utils.logger:log_with_emoji:140 | 💥 Erro em Agent Timeout: ❌ Timeout em agent.arun após 30s | Data: {'component': 'Agent Timeout'}
2025-08-07 18:24:35.617 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔄 Tentando gerar resposta de fallback...
2025-08-07 18:24:35.617 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔄 Gerando resposta de fallback...
2025-08-07 18:24:35.617 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 Tipo do result: <class 'str'>
2025-08-07 18:24:35.618 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 result tem content? False
2025-08-07 18:24:35.618 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔍 result como string: Entendi! Para te ajudar melhor com energia solar, qual o valor da sua conta de luz?...
2025-08-07 18:24:35.618 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📋 Result não é None, tipo: str
2025-08-07 18:24:35.618 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📄 raw_response (primeiros 200 chars): Entendi! Para te ajudar melhor com energia solar, qual o valor da sua conta de luz?...
2025-08-07 18:24:35.618 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 📏 Tamanho raw_response: 83 caracteres
2025-08-07 18:24:35.842 | INFO     | app.utils.logger:log_with_emoji:140 | 💬 Resposta: Resposta gerada: <RESPOSTA_FINAL>Entendi! Para te ajudar melhor com energia solar, qual o valor da sua conta de luz?<...
2025-08-07 18:24:35.842 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔎 extract_final_response recebeu: tipo=<class 'str'>, tamanho=116, primeiros 200 chars: <RESPOSTA_FINAL>Entendi! Para te ajudar melhor com energia solar, qual o valor da sua conta de luz?</RESPOSTA_FINAL>
2025-08-07 18:24:35.843 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ 🔎 extract_final_response recebeu: tipo=<class 'str'>, tamanho=116, primeiros 200 chars: <RESPOSTA_FINAL>Entendi! Para te ajudar melhor com energia solar, qual o valor da sua conta de luz?</RESPOSTA_FINAL>
2025-08-07 18:24:36.968 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando emoji para reaction | Data: {'reaction': '✅', 'recipient': 'reaction', 'type': 'emoji'}
2025-08-07 18:24:36.968 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Reação '✅' enviada com sucesso. ID: 3EB03408868C444F5725B6E32346D3726BFD6D04
2025-08-07 18:24:37.179 | INFO     | app.utils.logger:log_with_emoji:140 | 📞 Webhook recebido: /whatsapp/send-message de evolution-api | Data: {'event': 'SEND_MESSAGE', 'endpoint': '/whatsapp/send-message', 'source': 'evolution-api'}