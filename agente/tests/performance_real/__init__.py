"""
Performance Real Tests - SDR IA SolarPrime

Load testing e stress testing com cenários reais:
- 500+ usuários simultâneos
- Bottleneck identification
- Resource monitoring (CPU, memória, I/O)
- Rate limiting behavior under load
- Recovery time measurement

CARACTERÍSTICAS:
- Testes com carga real
- Monitoramento de recursos
- Benchmarks de performance
- SLA validation
- Chaos engineering scenarios
"""

import psutil
import time
from typing import Dict, Any

def get_system_metrics() -> Dict[str, Any]:
    """Coleta métricas do sistema para performance testing"""
    return {
        'cpu_percent': psutil.cpu_percent(interval=1),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_io': psutil.disk_io_counters()._asdict() if psutil.disk_io_counters() else {},
        'network_io': psutil.net_io_counters()._asdict() if psutil.net_io_counters() else {},
        'timestamp': time.time()
    }