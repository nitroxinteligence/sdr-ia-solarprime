1:48:08.311 | INFO     | app.teams.sdr_team:initialize:312 | Team configurado sem memória (melhor estabilidade)
2025-08-04 21:48:08.743 | INFO     | app.teams.agents.knowledge:load_knowledge_base:184 | 📚 Carregados 67 documentos na base de conhecimento
2025-08-04 21:48:08.743 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team pronto | Data: {'agents_active': 6, 'startup_ms': 1000.0}
2025-08-04 21:48:08.743 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ SDR Team inicializado pronto
2025-08-04 21:48:08.743 | INFO     | app.utils.logger:log_with_emoji:140 | ✅ AGENTIC SDR pronto | Data: {'startup_ms': 500.0}
2025-08-04 21:48:09.247 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por phone: 558182986181
2025-08-04 21:48:09.516 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Conversation_id encontrado: fff09a52-a2aa-4aa8-9513-0429546068ee
2025-08-04 21:48:09.516 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: fff09a52-a2aa-4aa8-9513-0429546068ee
2025-08-04 21:48:10.224 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Query executada, 11 mensagens encontradas
2025-08-04 21:48:10.225 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Buscando mensagens por conversation_id: fff09a52-a2aa-4aa8-9513-0429546068ee
2025-08-04 21:48:10.225 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Executando query para conversation_id: fff09a52-a2aa-4aa8-9513-0429546068ee
2025-08-04 21:48:10.935 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Query executada, 11 mensagens encontradas
2025-08-04 21:48:10.936 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ Histórico carregado: 11 mensagens
2025-08-04 21:48:10.936 | INFO     | app.utils.logger:log_with_emoji:140 | 💭 Decisão: AGENTIC SDR resolve sozinha
2025-08-04 21:48:10.936 | INFO     | app.utils.logger:log_with_emoji:140 | ℹ️ AGNO Context enhanced: 11 mensagens, quality=fair, score=0.31
2025-08-04 21:48:10.937 | ERROR    | app.utils.retry_handler:wrapper:103 | ❌ _gemini_call_with_retry failed with non-retryable error: 'str' object has no attribute 'role'
2025-08-04 21:48:10.937 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ ⚠️ Gemini falhou após múltiplas tentativas: 'str' object has no attribute 'role'
2025-08-04 21:48:10.938 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ 🔄 Ativando fallback OpenAI o3-mini com retry...
2025-08-04 21:48:11.342 | ERROR    | app.utils.retry_handler:wrapper:103 | ❌ _openai_call_with_retry failed with non-retryable error: OpenAI o3-mini falhou: API Error 429: {
    "error": {
        "message": "You exceeded your current quota, please check your plan and billing details. For more information on this error, read the docs: https://platform.openai.com/docs/guides/error-codes/api-errors.",
        "type": "insufficient_quota",
        "param": null,
        "code": "insufficient_quota"
    }
}

2025-08-04 21:48:11.343 | ERROR    | app.utils.logger:log_with_emoji:140 | 💥 Erro em Fallback OpenAI também falhou: OpenAI o3-mini falhou: API Error 429: {
    "error": {
        "message": "You exceeded your current quota, please check your plan and billing details. For more information on this error, read the docs: https://platform.openai.com/docs/guides/error-codes/api-errors.",
        "type": "insufficient_quota",
        "param": null,
        "code": "insufficient_quota"
    }
}
 | Data: {'component': 'Fallback OpenAI também falhou'}
2025-08-04 21:48:11.343 | ERROR    | app.utils.logger:log_with_emoji:140 | 💥 Erro em AGENTIC SDR: Erro ao gerar resposta: OpenAI o3-mini falhou: API Error 429: {
    "error": {
        "message": "You exceeded your current quota, please check your plan and billing details. For more information on this error, read the docs: https://platform.openai.com/docs/guides/error-codes/api-errors.",
        "type": "insufficient_quota",
        "param": null,
        "code": "insufficient_quota"
    }
}
 | Data: {'component': 'AGENTIC SDR'}
2025-08-04 21:48:11.343 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ Nenhuma resposta gerada, usando fallback
2025-08-04 21:48:11.343 | INFO     | app.utils.logger:log_with_emoji:140 | 💬 Resposta: Resposta gerada: Oi! Tudo bem? Sou a Helen da Solar Prime! Como posso ajudar você hoje?...
2025-08-04 21:48:14.612 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando typing para 558182986181 | Data: {'duration_seconds': 3.0, 'message_length': 0, 'recipient': '558182986181', 'type': 'typing'}