"""
Connection Monitor Service
==========================
Serviço de monitoramento contínuo da conexão WhatsApp
"""

import asyncio
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Callable
from loguru import logger
from enum import Enum

from services.evolution_api import evolution_client
# from services.redis_service import redis_service
from services.redis_fallback import get_redis_fallback_service


class ConnectionState(Enum):
    """Estados possíveis da conexão"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    QR_CODE = "qr_code"
    ERROR = "error"
    UNKNOWN = "unknown"


class ConnectionMonitor:
    """Monitor de conexão WhatsApp"""
    
    def __init__(self):
        self.check_interval = int(os.getenv("CONNECTION_CHECK_INTERVAL", "60"))  # segundos
        self.alert_threshold = int(os.getenv("CONNECTION_ALERT_THRESHOLD", "5"))  # tentativas
        self.monitoring_task: Optional[asyncio.Task] = None
        self.is_running = False
        self.state_history: List[Dict[str, Any]] = []
        self.failure_count = 0
        self.last_state = ConnectionState.UNKNOWN
        self.callbacks: Dict[str, List[Callable]] = {
            "on_connected": [],
            "on_disconnected": [],
            "on_qr_code": [],
            "on_error": []
        }
        self.redis_service = get_redis_fallback_service()
    
    def add_callback(self, event: str, callback: Callable):
        """Adiciona callback para eventos"""
        if event in self.callbacks:
            self.callbacks[event].append(callback)
    
    async def start(self):
        """Inicia monitoramento"""
        if self.is_running:
            logger.warning("Monitor já está em execução")
            return
        
        self.is_running = True
        self.monitoring_task = asyncio.create_task(self._monitor_loop())
        logger.info("🔍 Monitor de conexão WhatsApp iniciado")
    
    async def stop(self):
        """Para monitoramento"""
        self.is_running = False
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Monitor de conexão WhatsApp parado")
    
    async def _monitor_loop(self):
        """Loop principal de monitoramento"""
        while self.is_running:
            try:
                await self._check_connection()
                await asyncio.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"Erro no loop de monitoramento: {e}")
                await asyncio.sleep(self.check_interval)
    
    async def _check_connection(self):
        """Verifica status da conexão"""
        try:
            status_data = await evolution_client.check_connection()
            
            # Mapear estado
            state = self._map_connection_state(status_data)
            
            # Registrar histórico
            self._record_state(state, status_data)
            
            # Processar mudança de estado
            if state != self.last_state:
                await self._handle_state_change(state, status_data)
            
            # Atualizar cache
            await self.redis_service.set(
                "whatsapp:connection:status",
                {
                    "state": state.value,
                    "data": status_data,
                    "timestamp": datetime.now().isoformat()
                },
                ttl=120  # 2 minutos
            )
            
            # Reset contador de falhas se conectado
            if state == ConnectionState.CONNECTED:
                self.failure_count = 0
            
            self.last_state = state
                
        except Exception as e:
            logger.error(f"Erro ao verificar conexão: {e}")
            self.failure_count += 1
            
            # Alertar se muitas falhas
            if self.failure_count >= self.alert_threshold:
                await self._trigger_callbacks("on_error", {
                    "error": str(e),
                    "failure_count": self.failure_count
                })
    
    def _map_connection_state(self, status_data: Dict[str, Any]) -> ConnectionState:
        """Mapeia dados de status para enum"""
        state = status_data.get("state", "").lower()
        
        if state == "open":
            return ConnectionState.CONNECTED
        elif state == "close":
            return ConnectionState.DISCONNECTED
        elif state == "connecting":
            return ConnectionState.CONNECTING
        elif "qr" in state or status_data.get("qrcode"):
            return ConnectionState.QR_CODE
        elif status_data.get("error"):
            return ConnectionState.ERROR
        else:
            return ConnectionState.UNKNOWN
    
    def _record_state(self, state: ConnectionState, data: Dict[str, Any]):
        """Registra estado no histórico"""
        record = {
            "state": state.value,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        
        self.state_history.append(record)
        
        # Manter apenas últimos 100 registros
        if len(self.state_history) > 100:
            self.state_history = self.state_history[-100:]
    
    async def _handle_state_change(
        self, 
        new_state: ConnectionState, 
        data: Dict[str, Any]
    ):
        """Processa mudança de estado"""
        logger.info(f"📱 WhatsApp mudou de {self.last_state.value} para {new_state.value}")
        
        # Executar callbacks específicos
        if new_state == ConnectionState.CONNECTED:
            await self._trigger_callbacks("on_connected", data)
            
        elif new_state == ConnectionState.DISCONNECTED:
            await self._trigger_callbacks("on_disconnected", data)
            
        elif new_state == ConnectionState.QR_CODE:
            # Obter QR Code completo
            try:
                async with evolution_client as client:
                    qr_data = await client.get_qrcode()
                    if qr_data:
                        data["qrcode"] = qr_data
            except:
                pass
                
            await self._trigger_callbacks("on_qr_code", data)
            
        elif new_state == ConnectionState.ERROR:
            await self._trigger_callbacks("on_error", data)
    
    async def _trigger_callbacks(self, event: str, data: Dict[str, Any]):
        """Executa callbacks de evento"""
        for callback in self.callbacks.get(event, []):
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(data)
                else:
                    callback(data)
            except Exception as e:
                logger.error(f"Erro ao executar callback {event}: {e}")
    
    async def get_current_status(self) -> Dict[str, Any]:
        """Obtém status atual"""
        # Tentar cache primeiro
        cached = await self.redis_service.get("whatsapp:connection:status")
        if cached:
            return cached
        
        # Se não tem cache, verificar agora
        await self._check_connection()
        
        return {
            "state": self.last_state.value,
            "failure_count": self.failure_count,
            "last_check": datetime.now().isoformat()
        }
    
    def get_uptime_stats(self) -> Dict[str, Any]:
        """Calcula estatísticas de uptime"""
        if not self.state_history:
            return {
                "uptime_percentage": 0,
                "total_time": 0,
                "connected_time": 0,
                "disconnected_time": 0
            }
        
        # Calcular tempo em cada estado
        state_durations = {}
        
        for i in range(len(self.state_history) - 1):
            current = self.state_history[i]
            next_record = self.state_history[i + 1]
            
            state = current["state"]
            duration = (
                datetime.fromisoformat(next_record["timestamp"]) - 
                datetime.fromisoformat(current["timestamp"])
            ).total_seconds()
            
            if state not in state_durations:
                state_durations[state] = 0
            state_durations[state] += duration
        
        total_time = sum(state_durations.values())
        connected_time = state_durations.get("connected", 0)
        
        return {
            "uptime_percentage": (connected_time / total_time * 100) if total_time > 0 else 0,
            "total_time": total_time,
            "connected_time": connected_time,
            "disconnected_time": state_durations.get("disconnected", 0),
            "state_durations": state_durations
        }
    
    async def force_reconnect(self) -> bool:
        """Força reconexão"""
        try:
            async with evolution_client as client:
                # Tentar reiniciar instância
                await client.restart_instance()
                
                # Aguardar um pouco
                await asyncio.sleep(5)
                
                # Verificar novo status
                await self._check_connection()
                
                return self.last_state == ConnectionState.CONNECTED
                
        except Exception as e:
            logger.error(f"Erro ao forçar reconexão: {e}")
            return False


# Instância global
connection_monitor = ConnectionMonitor()


# Callbacks padrão para notificações
async def on_disconnected(data: Dict[str, Any]):
    """Callback quando desconecta"""
    logger.error("🔴 WhatsApp DESCONECTADO!")
    
    # TODO: Enviar notificação para admin
    # TODO: Tentar reconexão automática


async def on_qr_code(data: Dict[str, Any]):
    """Callback quando precisa de QR Code"""
    logger.warning("📱 QR Code necessário para conectar WhatsApp")
    
    qr_data = data.get("qrcode", {})
    if qr_data.get("base64"):
        # TODO: Enviar QR Code para admin
        logger.info(f"QR Code: {qr_data.get('base64', '')[:50]}...")


# Registrar callbacks padrão
connection_monitor.add_callback("on_disconnected", on_disconnected)
connection_monitor.add_callback("on_qr_code", on_qr_code)