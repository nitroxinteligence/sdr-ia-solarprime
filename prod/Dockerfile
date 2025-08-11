# =============================================================================
# SDR IA SolarPrime v0.2 - AGENTIC SDR Production Dockerfile
# =============================================================================
# Otimizado para deploy no Easypanel com AGENTIC SDR, Evolution API e Redis
# Suporte para AGNO Framework, Multimodal e Reasoning
# =============================================================================

# Use Python 3.11 para compatibilidade com AGENTIC SDR e AGNO Framework
FROM python:3.11-slim as builder

# Variáveis de ambiente para otimização
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependências do sistema necessárias para compilação
# Incluindo dependências para AGNO Framework, Multimodal e Reasoning
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    curl \
    wget \
    libmagic1 \
    libmagic-dev \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-por \
    libreoffice \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Criar diretório de trabalho
WORKDIR /build

# Copiar requirements e instalar dependências Python
COPY requirements.txt .
# Força atualização do pip e instalação limpa das dependências
RUN pip install --upgrade pip && \
    pip install --user --no-warn-script-location -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

# Variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/home/app/.local/bin:$PATH" \
    PYTHONPATH="/app:$PYTHONPATH"

# Instalar dependências runtime mínimas para AGENTIC SDR
# Incluindo suporte para multimodal (áudio, imagem, documentos)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    wget \
    libmagic1 \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-por \
    ffmpeg \
    libsndfile1 \
    libreoffice \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Criar usuário não-root
RUN groupadd -r app && useradd -r -g app -d /home/app -s /sbin/nologin app

# Criar diretórios necessários
RUN mkdir -p /app /app/logs /app/static && \
    chown -R app:app /app

# Copiar dependências Python do builder
COPY --from=builder --chown=app:app /root/.local /home/app/.local

# Mudar para diretório da aplicação
WORKDIR /app

# Copiar código da aplicação
COPY --chown=app:app . .

# Criar diretórios adicionais para AGENTIC SDR
# Incluindo diretórios para multimodal e processamento
RUN mkdir -p /app/temp /app/uploads /app/media /app/documents /app/audio && \
    chown -R app:app /app

# Mudar para usuário não-root
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expor porta
EXPOSE 8000

# Comando de inicialização otimizado para AGENTIC SDR
# Usando 1 worker por padrão para AGENTIC SDR (state management)
# Configuração otimizada para produção no EasyPanel
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port 8000 --workers ${UVICORN_WORKERS:-1} --worker-class uvicorn.workers.UvicornWorker --access-log --log-level info"]