# =============================================================================
# SDR IA SolarPrime - Dockerfile para Easypanel
# =============================================================================
# Otimizado para deploy no Easypanel com Evolution API e Redis
# =============================================================================

# Use Python 3.11 para compatibilidade com o projeto
FROM python:3.11-slim as builder

# Variáveis de ambiente para otimização
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependências do sistema necessárias para compilação
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Criar diretório de trabalho
WORKDIR /build

# Copiar requirements e instalar dependências Python
COPY requirements.txt .
# Força atualização do pip e instalação limpa das dependências
RUN pip install --upgrade pip && \
    pip install --user --no-warn-script-location -r requirements.txt && \
    # Força instalação do google-genai caso não tenha sido instalado
    pip install --user --no-warn-script-location google-genai || true

# Stage 2: Runtime
FROM python:3.11-slim

# Variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/home/app/.local/bin:$PATH" \
    PYTHONPATH="/app:$PYTHONPATH"

# Instalar dependências runtime mínimas
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Criar usuário não-root
RUN groupadd -r app && useradd -r -g app -d /home/app -s /sbin/nologin app

# Criar diretórios necessários
RUN mkdir -p /app /app/logs /app/static && \
    chown -R app:app /app

# Copiar dependências Python do builder
COPY --from=builder --chown=app:app /root/.local /home/app/.local

# Verificar se google-genai está instalado e instalar se necessário
RUN python -c "import importlib.util; exit(0 if importlib.util.find_spec('google_genai') else 1)" || \
    pip install --user google-genai

# Mudar para diretório da aplicação
WORKDIR /app

# Copiar código da aplicação
COPY --chown=app:app . .

# Criar diretórios adicionais se necessário
RUN mkdir -p /app/temp /app/uploads && \
    chown -R app:app /app

# Mudar para usuário não-root
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expor porta
EXPOSE 8000

# Comando de inicialização otimizado para Easypanel
# Reduzido para 2 workers para economizar recursos no container
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--access-log"]