"""
Performance Monitor
===================
Monitoramento de performance para garantir <30s de resposta
"""

import time
import asyncio
from typing import Dict, Any, Callable, Optional, TypeVar, cast
from datetime import datetime, timedelta
from functools import wraps
from loguru import logger
import json

from services.database import supabase_client

T = TypeVar('T')


class PerformanceMonitor:
    """Monitor de performance com alertas e métricas"""
    
    def __init__(self):
        self.metrics: Dict[str, list] = {}
        self.alerts: list = []
        self.thresholds = {
            'response_time': 30.0,  # 30 segundos máximo
            'warning_time': 20.0,   # 20 segundos para warning
            'target_time': 15.0     # 15 segundos ideal
        }
        self.supabase = supabase_client
        
    async def track_response_time(self, func: Callable[..., T]) -> Callable[..., T]:
        """Decorator para monitorar tempo de resposta"""
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> T:
            start_time = time.time()
            function_name = func.__name__
            
            try:
                # Executar função
                result = await func(*args, **kwargs)
                
                # Calcular duração
                duration = time.time() - start_time
                
                # Registrar métrica
                await self._record_metric(function_name, 'response_time', duration)
                
                # Verificar thresholds e alertar
                if duration > self.thresholds['response_time']:
                    await self._create_alert(
                        level='critical',
                        message=f"Response time exceeded 30s: {duration:.2f}s in {function_name}",
                        details={'function': function_name, 'duration': duration}
                    )
                elif duration > self.thresholds['warning_time']:
                    await self._create_alert(
                        level='warning',
                        message=f"Response time warning: {duration:.2f}s in {function_name}",
                        details={'function': function_name, 'duration': duration}
                    )
                elif duration < self.thresholds['target_time']:
                    logger.success(f"✅ Excellent response time: {duration:.2f}s")
                    
                return result
                
            except asyncio.TimeoutError:
                duration = time.time() - start_time
                await self._create_alert(
                    level='critical',
                    message=f"Timeout after {duration:.2f}s in {function_name}",
                    details={'function': function_name, 'duration': duration, 'error': 'timeout'}
                )
                raise
                
            except Exception as e:
                duration = time.time() - start_time
                await self._record_metric(function_name, 'error', 1)
                await self._create_alert(
                    level='error',
                    message=f"Error in {function_name}: {str(e)}",
                    details={'function': function_name, 'duration': duration, 'error': str(e)}
                )
                raise
                
        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> T:
            # Para funções síncronas
            start_time = time.time()
            function_name = func.__name__
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Registrar de forma assíncrona
                asyncio.create_task(
                    self._record_metric(function_name, 'response_time', duration)
                )
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                asyncio.create_task(
                    self._create_alert(
                        level='error',
                        message=f"Error in {function_name}: {str(e)}",
                        details={'function': function_name, 'duration': duration, 'error': str(e)}
                    )
                )
                raise
                
        if asyncio.iscoroutinefunction(func):
            return cast(Callable[..., T], async_wrapper)
        else:
            return cast(Callable[..., T], sync_wrapper)
            
    async def _record_metric(self, name: str, metric_type: str, value: float):
        """Registra métrica no sistema"""
        key = f"{name}:{metric_type}"
        
        # Adicionar à memória
        if key not in self.metrics:
            self.metrics[key] = []
        self.metrics[key].append({
            'timestamp': datetime.now().isoformat(),
            'value': value
        })
        
        # Limitar histórico em memória (últimas 100 entradas)
        if len(self.metrics[key]) > 100:
            self.metrics[key] = self.metrics[key][-100:]
            
        # Salvar no Supabase (assíncrono)
        try:
            await self._save_metric_to_db(name, metric_type, value)
        except Exception as e:
            logger.error(f"Erro ao salvar métrica no banco: {e}")
            
    async def _save_metric_to_db(self, name: str, metric_type: str, value: float):
        """Salva métrica no Supabase"""
        # Criar tabela se não existir
        self.supabase.table('performance_metrics').insert({
            'function_name': name,
            'metric_type': metric_type,
            'value': value,
            'timestamp': datetime.now().isoformat()
        }).execute()
        
    async def _create_alert(self, level: str, message: str, details: Dict[str, Any]):
        """Cria alerta de performance"""
        alert = {
            'level': level,
            'message': message,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        
        # Adicionar à lista
        self.alerts.append(alert)
        
        # Log apropriado
        if level == 'critical':
            logger.critical(f"🚨 {message}")
        elif level == 'warning':
            logger.warning(f"⚠️ {message}")
        elif level == 'error':
            logger.error(f"❌ {message}")
            
        # Salvar no banco para histórico
        try:
            self.supabase.table('performance_alerts').insert(alert).execute()
        except Exception as e:
            logger.error(f"Erro ao salvar alerta: {e}")
            
        # TODO: Enviar notificação (WhatsApp, email, etc)
        
    def get_metrics_summary(self, function_name: Optional[str] = None) -> Dict[str, Any]:
        """Obtém resumo das métricas"""
        summary = {}
        
        for key, values in self.metrics.items():
            name, metric_type = key.split(':')
            
            if function_name and name != function_name:
                continue
                
            if name not in summary:
                summary[name] = {}
                
            # Calcular estatísticas
            if values and metric_type == 'response_time':
                times = [v['value'] for v in values]
                summary[name][metric_type] = {
                    'count': len(times),
                    'average': sum(times) / len(times),
                    'min': min(times),
                    'max': max(times),
                    'last': times[-1],
                    'under_15s': sum(1 for t in times if t < 15),
                    'under_30s': sum(1 for t in times if t < 30),
                    'over_30s': sum(1 for t in times if t >= 30)
                }
                
        return summary
        
    def get_recent_alerts(self, hours: int = 24) -> list:
        """Obtém alertas recentes"""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        recent = [
            alert for alert in self.alerts
            if datetime.fromisoformat(alert['timestamp']) > cutoff
        ]
        
        return sorted(recent, key=lambda x: x['timestamp'], reverse=True)
        
    async def generate_performance_report(self) -> Dict[str, Any]:
        """Gera relatório de performance"""
        summary = self.get_metrics_summary()
        recent_alerts = self.get_recent_alerts()
        
        # Calcular SLA
        total_requests = 0
        under_30s = 0
        
        for func, metrics in summary.items():
            if 'response_time' in metrics:
                rt = metrics['response_time']
                total_requests += rt['count']
                under_30s += rt['under_30s']
                
        sla_percentage = (under_30s / total_requests * 100) if total_requests > 0 else 0
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'sla_target': '< 30 seconds',
            'sla_achievement': f"{sla_percentage:.2f}%",
            'total_requests': total_requests,
            'requests_under_30s': under_30s,
            'requests_over_30s': total_requests - under_30s,
            'critical_alerts': len([a for a in recent_alerts if a['level'] == 'critical']),
            'warnings': len([a for a in recent_alerts if a['level'] == 'warning']),
            'function_metrics': summary,
            'recent_alerts': recent_alerts[:10]  # Top 10 alertas
        }
        
        # Salvar relatório
        try:
            self.supabase.table('performance_reports').insert({
                'report_data': json.dumps(report),
                'sla_percentage': sla_percentage,
                'total_requests': total_requests,
                'created_at': datetime.now().isoformat()
            }).execute()
        except Exception as e:
            logger.error(f"Erro ao salvar relatório: {e}")
            
        return report
        
    def create_monitoring_tables_sql(self) -> str:
        """SQL para criar tabelas de monitoramento"""
        return """
        -- Tabela de métricas de performance
        CREATE TABLE IF NOT EXISTS performance_metrics (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            function_name VARCHAR(255) NOT NULL,
            metric_type VARCHAR(50) NOT NULL,
            value FLOAT NOT NULL,
            timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Índices para queries rápidas
        CREATE INDEX idx_metrics_function ON performance_metrics(function_name);
        CREATE INDEX idx_metrics_timestamp ON performance_metrics(timestamp);
        CREATE INDEX idx_metrics_type ON performance_metrics(metric_type);
        
        -- Tabela de alertas
        CREATE TABLE IF NOT EXISTS performance_alerts (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            level VARCHAR(20) NOT NULL,
            message TEXT NOT NULL,
            details JSONB DEFAULT '{}',
            timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            resolved BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Índices
        CREATE INDEX idx_alerts_level ON performance_alerts(level);
        CREATE INDEX idx_alerts_timestamp ON performance_alerts(timestamp);
        CREATE INDEX idx_alerts_resolved ON performance_alerts(resolved);
        
        -- Tabela de relatórios
        CREATE TABLE IF NOT EXISTS performance_reports (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            report_data JSONB NOT NULL,
            sla_percentage FLOAT,
            total_requests INTEGER,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Políticas RLS
        ALTER TABLE performance_metrics ENABLE ROW LEVEL SECURITY;
        ALTER TABLE performance_alerts ENABLE ROW LEVEL SECURITY;
        ALTER TABLE performance_reports ENABLE ROW LEVEL SECURITY;
        
        -- Acesso apenas para service role
        CREATE POLICY "Service role full access to metrics" ON performance_metrics
            FOR ALL USING (auth.role() = 'service_role');
            
        CREATE POLICY "Service role full access to alerts" ON performance_alerts
            FOR ALL USING (auth.role() = 'service_role');
            
        CREATE POLICY "Service role full access to reports" ON performance_reports
            FOR ALL USING (auth.role() = 'service_role');
        """


# Instância global
performance_monitor = PerformanceMonitor()


# Decorator helper
def monitor_performance(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator helper para monitorar performance"""
    return performance_monitor.track_response_time(func)