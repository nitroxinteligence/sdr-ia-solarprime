"""
Celery Tasks Configuration
==========================
Configuração do Celery para tarefas assíncronas
"""

import os
from celery import Celery

# Importar configuração centralizada
try:
    from core.environment import env_config
    redis_url = env_config.redis_url
except ImportError:
    # Fallback se não conseguir importar
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Criar instância do Celery
celery_app = Celery(
    'sdr_ia_solarprime',
    broker=redis_url,
    backend=redis_url
)

# Configurações do Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='America/Sao_Paulo',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutos
    task_soft_time_limit=25 * 60,  # 25 minutos
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
)

# Descoberta automática de tasks
celery_app.autodiscover_tasks([
    'services.follow_up_service',
    'services.kommo_follow_up_service',
    'services.analytics_service',
])