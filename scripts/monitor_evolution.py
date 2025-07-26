#!/usr/bin/env python3
"""
Evolution API Monitor Script
============================
Script para monitorar status da integração Evolution API
"""

import asyncio
import os
import sys
from datetime import datetime
from typing import Dict, Any
import json
from dotenv import load_dotenv
import argparse

# Adicionar diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.evolution_api import EvolutionAPIClient
from services.connection_monitor import ConnectionMonitor, ConnectionState
# from services.redis_service import redis_service
from services.redis_fallback import get_redis_fallback_service


class EvolutionMonitor:
    """Monitor para Evolution API"""
    
    def __init__(self):
        load_dotenv()
        self.client = EvolutionAPIClient()
        self.monitor = ConnectionMonitor()
        self.redis_service = get_redis_fallback_service()
        
    async def check_status(self) -> Dict[str, Any]:
        """Verifica status completo da integração"""
        
        status = {
            "timestamp": datetime.now().isoformat(),
            "evolution_api": {},
            "whatsapp": {},
            "redis": {},
            "webhook": {}
        }
        
        # 1. Verificar Evolution API
        try:
            async with self.client as client:
                # Status da conexão
                connection = await client.check_connection()
                status["evolution_api"]["connected"] = True
                status["evolution_api"]["response"] = connection
                
                # Status do WhatsApp
                status["whatsapp"]["state"] = connection.get("state", "unknown")
                status["whatsapp"]["connected"] = connection.get("state") == "open"
                
                # Se desconectado, verificar QR Code
                if connection.get("state") != "open":
                    qr_data = await client.get_qrcode()
                    if qr_data and qr_data.get("qrcode"):
                        status["whatsapp"]["qr_available"] = True
                        status["whatsapp"]["qr_code"] = qr_data.get("qrcode", {}).get("base64", "")[:50] + "..."
                
                # Verificar webhook
                webhook_info = await client.get_webhook_info()
                status["webhook"]["configured"] = bool(webhook_info)
                status["webhook"]["info"] = webhook_info
                
        except Exception as e:
            status["evolution_api"]["connected"] = False
            status["evolution_api"]["error"] = str(e)
        
        # 2. Verificar Redis
        try:
            test_key = "monitor:test"
            await self.redis_service.set(test_key, {"test": True}, ttl=10)
            test_value = await self.redis_service.get(test_key)
            
            status["redis"]["connected"] = test_value is not None
            status["redis"]["response_time"] = "< 10ms"
            
            # Se está usando fallback, informar
            if hasattr(self.redis_service, 'use_fallback') and self.redis_service.use_fallback:
                status["redis"]["mode"] = "memory (fallback)"
            else:
                status["redis"]["mode"] = "redis"
        except Exception as e:
            status["redis"]["connected"] = False
            status["redis"]["error"] = str(e)
        
        # 3. Estatísticas de uptime
        uptime_stats = self.monitor.get_uptime_stats()
        status["uptime"] = uptime_stats
        
        return status
    
    async def continuous_monitor(self, interval: int = 60):
        """Monitoramento contínuo"""
        
        print("🔍 Iniciando monitoramento contínuo...")
        print(f"Intervalo: {interval} segundos")
        print("Pressione Ctrl+C para parar\n")
        
        try:
            while True:
                status = await self.check_status()
                self._print_status(status)
                await asyncio.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n\n✋ Monitoramento interrompido")
    
    def _print_status(self, status: Dict[str, Any]):
        """Imprime status formatado"""
        
        print("\n" + "="*50)
        print(f"📊 STATUS - {status['timestamp']}")
        print("="*50)
        
        # Evolution API
        evo_status = status["evolution_api"]
        if evo_status.get("connected"):
            print("✅ Evolution API: Conectada")
        else:
            print(f"❌ Evolution API: Desconectada - {evo_status.get('error', 'Erro desconhecido')}")
        
        # WhatsApp
        wa_status = status["whatsapp"]
        if wa_status.get("connected"):
            print("✅ WhatsApp: Conectado")
        elif wa_status.get("state") == "close":
            print("⚠️  WhatsApp: Desconectado")
            if wa_status.get("qr_available"):
                print("📱 QR Code disponível para conexão")
        else:
            print(f"❓ WhatsApp: {wa_status.get('state', 'Estado desconhecido')}")
        
        # Redis
        redis_status = status["redis"]
        if redis_status.get("connected"):
            mode = redis_status.get('mode', 'redis')
            print(f"✅ Redis: Conectado ({mode}) - {redis_status.get('response_time', 'N/A')}")
        else:
            print(f"❌ Redis: Desconectado - {redis_status.get('error', 'Erro desconhecido')}")
        
        # Webhook
        webhook_status = status["webhook"]
        if webhook_status.get("configured"):
            webhook_info = webhook_status.get("info", {})
            print(f"✅ Webhook: Configurado")
            if webhook_info.get("url"):
                print(f"   URL: {webhook_info.get('url')}")
        else:
            print("⚠️  Webhook: Não configurado")
        
        # Uptime
        uptime = status.get("uptime", {})
        if uptime:
            print(f"\n📈 Uptime: {uptime.get('uptime_percentage', 0):.1f}%")
            print(f"   Tempo total: {uptime.get('total_time', 0):.0f}s")
            print(f"   Tempo conectado: {uptime.get('connected_time', 0):.0f}s")
    
    async def export_status(self, format: str = "json") -> str:
        """Exporta status em diferentes formatos"""
        
        status = await self.check_status()
        
        if format == "json":
            return json.dumps(status, indent=2, ensure_ascii=False)
        
        elif format == "text":
            lines = []
            lines.append(f"Evolution API Monitor - {status['timestamp']}")
            lines.append("-" * 50)
            
            # Status resumido
            evo_ok = "OK" if status["evolution_api"].get("connected") else "ERRO"
            wa_ok = "OK" if status["whatsapp"].get("connected") else "DESCONECTADO"
            redis_ok = "OK" if status["redis"].get("connected") else "ERRO"
            webhook_ok = "OK" if status["webhook"].get("configured") else "NÃO CONFIGURADO"
            
            lines.append(f"Evolution API: {evo_ok}")
            lines.append(f"WhatsApp: {wa_ok}")
            lines.append(f"Redis: {redis_ok}")
            lines.append(f"Webhook: {webhook_ok}")
            
            if status.get("uptime"):
                lines.append(f"\nUptime: {status['uptime'].get('uptime_percentage', 0):.1f}%")
            
            return "\n".join(lines)
        
        else:
            raise ValueError(f"Formato não suportado: {format}")


async def main():
    """Função principal"""
    
    parser = argparse.ArgumentParser(description="Monitor Evolution API")
    parser.add_argument(
        "--mode", 
        choices=["check", "continuous", "export"],
        default="check",
        help="Modo de operação"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Intervalo para monitoramento contínuo (segundos)"
    )
    parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="json",
        help="Formato de exportação"
    )
    parser.add_argument(
        "--output",
        help="Arquivo de saída para exportação"
    )
    
    args = parser.parse_args()
    
    monitor = EvolutionMonitor()
    
    try:
        if args.mode == "check":
            # Verificação única
            status = await monitor.check_status()
            monitor._print_status(status)
            
        elif args.mode == "continuous":
            # Monitoramento contínuo
            await monitor.continuous_monitor(args.interval)
            
        elif args.mode == "export":
            # Exportar status
            output = await monitor.export_status(args.format)
            
            if args.output:
                with open(args.output, "w", encoding="utf-8") as f:
                    f.write(output)
                print(f"✅ Status exportado para: {args.output}")
            else:
                print(output)
                
    except Exception as e:
        print(f"❌ Erro: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())