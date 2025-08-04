2025-08-04 21:21:30.875 | ERROR    | app.utils.retry_handler:wrapper:103 | ❌ _gemini_call_with_retry failed with non-retryable error: 'Gemini' object has no attribute 'run'
2025-08-04 21:21:30.876 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ ⚠️ Gemini falhou após múltiplas tentativas: 'Gemini' object has no attribute 'run'
2025-08-04 21:21:30.876 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ 🔄 Ativando fallback OpenAI o3-mini com retry...
2025-08-04 21:21:31.281 | ERROR    | app.utils.retry_handler:wrapper:103 | ❌ _openai_call_with_retry failed with non-retryable error: OpenAI o3-mini falhou: API Error 429: {
    "error": {
        "message": "You exceeded your current quota, please check your plan and billing details. For more information on this error, read the docs: https://platform.openai.com/docs/guides/error-codes/api-errors.",
        "type": "insufficient_quota",
        "param": null,
        "code": "insufficient_quota"
    }
}

2025-08-04 21:21:31.282 | ERROR    | app.utils.logger:log_with_emoji:140 | 💥 Erro em Fallback OpenAI também falhou: OpenAI o3-mini falhou: API Error 429: {
    "error": {
        "message": "You exceeded your current quota, please check your plan and billing details. For more information on this error, read the docs: https://platform.openai.com/docs/guides/error-codes/api-errors.",
        "type": "insufficient_quota",
        "param": null,
        "code": "insufficient_quota"
    }
}
 | Data: {'component': 'Fallback OpenAI também falhou'}
2025-08-04 21:21:31.282 | ERROR    | app.utils.logger:log_with_emoji:140 | 💥 Erro em AGENTIC SDR: Erro ao gerar resposta: OpenAI o3-mini falhou: API Error 429: {
    "error": {
        "message": "You exceeded your current quota, please check your plan and billing details. For more information on this error, read the docs: https://platform.openai.com/docs/guides/error-codes/api-errors.",
        "type": "insufficient_quota",
        "param": null,
        "code": "insufficient_quota"
    }
}
 | Data: {'component': 'AGENTIC SDR'}
2025-08-04 21:21:31.282 | WARNING  | app.utils.logger:log_with_emoji:140 | ⚠️ Nenhuma resposta gerada, usando fallback
2025-08-04 21:21:31.282 | INFO     | app.utils.logger:log_with_emoji:140 | 💬 Resposta: Resposta gerada: Oi! Tudo bem? Sou a Helen da Solar Prime! Como posso ajudar você hoje?...
2025-08-04 21:21:34.540 | INFO     | app.utils.logger:log_with_emoji:140 | 📤 Enviando typing para 558182986181 | Data: {'duration_seconds': 3.0, 'message_length': 0, 'recipient': '558182986181', 'type': 'typing'}