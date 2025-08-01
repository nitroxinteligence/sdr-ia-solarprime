#!/usr/bin/env python3
"""
SDR Agent - Script de Health Check

Este script verifica a saúde de todos os componentes do sistema SDR Agent,
incluindo APIs externas, banco de dados, serviços e webhooks.

Pode ser usado por ferramentas de monitoramento ou executado manualmente.

Uso:
    python health_check.py [--json] [--verbose] [--critical-only]
    
Retorna:
    0 - Sistema saudável
    1 - Warnings encontrados
    2 - Erros críticos encontrados
"""

import os
import sys
import json
import time
import asyncio
import argparse
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Tuple
import httpx
import redis
from colorama import init, Fore, Style

# Adicionar o diretório pai ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar configurações e serviços
from core.config import (
    EVOLUTION_API_URL, EVOLUTION_API_KEY, EVOLUTION_INSTANCE_NAME,
    SUPABASE_URL, SUPABASE_SERVICE_KEY,
    KOMMO_BASE_URL, KOMMO_LONG_LIVED_TOKEN,
    GOOGLE_CALENDAR_ID, GOOGLE_SERVICE_ACCOUNT_EMAIL,
    REDIS_URL, REDIS_ENABLED,
    API_PORT
)
from services.supabase_service import SupabaseService
from services.evolution_service import EvolutionService
from services.kommo_service import KommoService
from services.calendar_service import CalendarService

# Inicializar colorama
init(autoreset=True)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HealthStatus:
    """Enum para status de saúde"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class HealthChecker:
    """Classe principal para verificação de saúde do sistema"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "overall_status": HealthStatus.HEALTHY,
            "checks": {},
            "metrics": {},
            "active_sessions": 0,
            "warnings": [],
            "errors": []
        }
        
    async def check_all(self) -> Dict[str, Any]:
        """Executa todas as verificações de saúde"""
        checks = [
            ("API Local", self.check_local_api),
            ("Evolution API", self.check_evolution_api),
            ("Kommo CRM", self.check_kommo_api),
            ("Google Calendar", self.check_calendar_api),
            ("Supabase", self.check_supabase),
            ("Redis", self.check_redis),
            ("Webhooks", self.check_webhooks),
            ("Active Sessions", self.check_active_sessions),
            ("System Resources", self.check_system_resources),
            ("Recent Errors", self.check_recent_errors)
        ]
        
        # Executar checks em paralelo para melhor performance
        tasks = []
        for name, check_func in checks:
            task = asyncio.create_task(self._run_check(name, check_func))
            tasks.append(task)
        
        await asyncio.gather(*tasks)
        
        # Determinar status geral
        self._determine_overall_status()
        
        return self.results
    
    async def _run_check(self, name: str, check_func):
        """Executa um check individual com tratamento de erro"""
        start_time = time.time()
        
        try:
            status, details = await check_func()
            elapsed = time.time() - start_time
            
            self.results["checks"][name] = {
                "status": status,
                "details": details,
                "response_time": f"{elapsed:.3f}s",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            if status == HealthStatus.WARNING:
                self.results["warnings"].append(f"{name}: {details.get('message', 'Warning')}")
            elif status == HealthStatus.CRITICAL:
                self.results["errors"].append(f"{name}: {details.get('message', 'Error')}")
                
        except Exception as e:
            elapsed = time.time() - start_time
            error_msg = str(e)
            
            self.results["checks"][name] = {
                "status": HealthStatus.CRITICAL,
                "details": {"error": error_msg},
                "response_time": f"{elapsed:.3f}s",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            self.results["errors"].append(f"{name}: {error_msg}")
            
            if self.verbose:
                logger.error(f"Error checking {name}: {error_msg}")
    
    async def check_local_api(self) -> Tuple[str, Dict]:
        """Verifica se a API local está respondendo"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"http://localhost:{API_PORT}/health",
                    timeout=5.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return HealthStatus.HEALTHY, {
                        "message": "API is running",
                        "version": data.get("version", "unknown"),
                        "uptime": data.get("uptime", "unknown")
                    }
                else:
                    return HealthStatus.WARNING, {
                        "message": f"API returned status {response.status_code}"
                    }
                    
            except httpx.ConnectError:
                return HealthStatus.CRITICAL, {
                    "message": "API is not running or not accessible"
                }
    
    async def check_evolution_api(self) -> Tuple[str, Dict]:
        """Verifica conectividade com Evolution API"""
        if not EVOLUTION_API_URL:
            return HealthStatus.WARNING, {
                "message": "Evolution API URL not configured"
            }
        
        async with httpx.AsyncClient() as client:
            try:
                # Verificar instância
                response = await client.get(
                    f"{EVOLUTION_API_URL}/instance/fetchInstances",
                    headers={"apikey": EVOLUTION_API_KEY},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    instances = response.json()
                    
                    # Procurar nossa instância
                    our_instance = None
                    for instance in instances:
                        if instance.get("name") == EVOLUTION_INSTANCE_NAME:
                            our_instance = instance
                            break
                    
                    if our_instance:
                        status = our_instance.get("status", {})
                        connected = status.get("state") == "open"
                        
                        return HealthStatus.HEALTHY if connected else HealthStatus.WARNING, {
                            "message": "WhatsApp connected" if connected else "WhatsApp disconnected",
                            "instance": EVOLUTION_INSTANCE_NAME,
                            "phone": status.get("number", "unknown")
                        }
                    else:
                        return HealthStatus.CRITICAL, {
                            "message": f"Instance '{EVOLUTION_INSTANCE_NAME}' not found"
                        }
                else:
                    return HealthStatus.CRITICAL, {
                        "message": f"API returned status {response.status_code}"
                    }
                    
            except Exception as e:
                return HealthStatus.CRITICAL, {
                    "message": f"Failed to connect: {str(e)}"
                }
    
    async def check_kommo_api(self) -> Tuple[str, Dict]:
        """Verifica conectividade com Kommo CRM"""
        if not KOMMO_BASE_URL or not KOMMO_LONG_LIVED_TOKEN:
            return HealthStatus.WARNING, {
                "message": "Kommo CRM not configured"
            }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{KOMMO_BASE_URL}/api/v4/account",
                    headers={"Authorization": f"Bearer {KOMMO_LONG_LIVED_TOKEN}"},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    account = response.json()
                    return HealthStatus.HEALTHY, {
                        "message": "Kommo API connected",
                        "account": account.get("name", "unknown"),
                        "subdomain": account.get("subdomain", "unknown")
                    }
                elif response.status_code == 401:
                    return HealthStatus.CRITICAL, {
                        "message": "Invalid Kommo token"
                    }
                else:
                    return HealthStatus.WARNING, {
                        "message": f"API returned status {response.status_code}"
                    }
                    
            except Exception as e:
                return HealthStatus.CRITICAL, {
                    "message": f"Failed to connect: {str(e)}"
                }
    
    async def check_calendar_api(self) -> Tuple[str, Dict]:
        """Verifica conectividade com Google Calendar"""
        if not GOOGLE_SERVICE_ACCOUNT_EMAIL:
            return HealthStatus.WARNING, {
                "message": "Google Calendar not configured"
            }
        
        try:
            calendar_service = CalendarService()
            
            # Tentar listar eventos (teste simples)
            now = datetime.now(timezone.utc)
            events = await calendar_service.list_events(
                time_min=now,
                time_max=now + timedelta(minutes=1),
                max_results=1
            )
            
            return HealthStatus.HEALTHY, {
                "message": "Google Calendar connected",
                "calendar_id": GOOGLE_CALENDAR_ID,
                "service_account": GOOGLE_SERVICE_ACCOUNT_EMAIL
            }
            
        except Exception as e:
            return HealthStatus.CRITICAL, {
                "message": f"Failed to connect: {str(e)}"
            }
    
    async def check_supabase(self) -> Tuple[str, Dict]:
        """Verifica conectividade com Supabase"""
        if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
            return HealthStatus.WARNING, {
                "message": "Supabase not configured"
            }
        
        try:
            supabase_service = SupabaseService()
            
            # Tentar uma query simples
            result = supabase_service.client.table("profiles").select("id").limit(1).execute()
            
            # Verificar métricas do banco
            metrics = await self._get_database_metrics(supabase_service)
            
            return HealthStatus.HEALTHY, {
                "message": "Supabase connected",
                "url": SUPABASE_URL.split(".")[0],  # Apenas o projeto
                **metrics
            }
            
        except Exception as e:
            return HealthStatus.CRITICAL, {
                "message": f"Failed to connect: {str(e)}"
            }
    
    async def _get_database_metrics(self, supabase_service) -> Dict:
        """Obtém métricas do banco de dados"""
        try:
            # Contar registros em tabelas principais
            tables = ["profiles", "conversations", "messages", "leads"]
            metrics = {}
            
            for table in tables:
                result = supabase_service.client.table(table).select("id", count="exact").execute()
                metrics[f"{table}_count"] = result.count or 0
            
            return metrics
            
        except Exception:
            return {}
    
    async def check_redis(self) -> Tuple[str, Dict]:
        """Verifica conectividade com Redis"""
        if not REDIS_ENABLED:
            return HealthStatus.WARNING, {
                "message": "Redis not enabled"
            }
        
        try:
            r = redis.from_url(REDIS_URL)
            
            # Ping Redis
            if r.ping():
                # Obter informações
                info = r.info()
                memory_used = info.get("used_memory_human", "unknown")
                connected_clients = info.get("connected_clients", 0)
                
                return HealthStatus.HEALTHY, {
                    "message": "Redis connected",
                    "memory_used": memory_used,
                    "connected_clients": connected_clients
                }
            else:
                return HealthStatus.CRITICAL, {
                    "message": "Redis ping failed"
                }
                
        except Exception as e:
            return HealthStatus.CRITICAL, {
                "message": f"Failed to connect: {str(e)}"
            }
    
    async def check_webhooks(self) -> Tuple[str, Dict]:
        """Verifica configuração de webhooks"""
        if not EVOLUTION_API_URL:
            return HealthStatus.WARNING, {
                "message": "Evolution API not configured"
            }
        
        async with httpx.AsyncClient() as client:
            try:
                # Verificar webhook configurado
                response = await client.get(
                    f"{EVOLUTION_API_URL}/webhook/find/{EVOLUTION_INSTANCE_NAME}",
                    headers={"apikey": EVOLUTION_API_KEY},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    webhook = response.json()
                    
                    if webhook.get("enabled"):
                        return HealthStatus.HEALTHY, {
                            "message": "Webhook configured and enabled",
                            "url": webhook.get("url", "unknown"),
                            "events": len(webhook.get("events", []))
                        }
                    else:
                        return HealthStatus.WARNING, {
                            "message": "Webhook configured but disabled"
                        }
                else:
                    return HealthStatus.WARNING, {
                        "message": "Webhook not configured"
                    }
                    
            except Exception as e:
                return HealthStatus.WARNING, {
                    "message": f"Failed to check webhook: {str(e)}"
                }
    
    async def check_active_sessions(self) -> Tuple[str, Dict]:
        """Verifica sessões ativas no sistema"""
        try:
            supabase_service = SupabaseService()
            
            # Buscar conversas ativas (últimas 24h)
            since = datetime.now(timezone.utc) - timedelta(hours=24)
            
            result = supabase_service.client.table("conversations")\
                .select("*")\
                .gte("updated_at", since.isoformat())\
                .execute()
            
            active_conversations = len(result.data) if result.data else 0
            
            # Buscar mensagens recentes (última hora)
            recent_since = datetime.now(timezone.utc) - timedelta(hours=1)
            
            messages_result = supabase_service.client.table("messages")\
                .select("id")\
                .gte("created_at", recent_since.isoformat())\
                .execute()
            
            recent_messages = len(messages_result.data) if messages_result.data else 0
            
            self.results["active_sessions"] = active_conversations
            self.results["metrics"]["recent_messages"] = recent_messages
            
            return HealthStatus.HEALTHY, {
                "message": "Session monitoring active",
                "active_conversations_24h": active_conversations,
                "messages_last_hour": recent_messages
            }
            
        except Exception as e:
            return HealthStatus.WARNING, {
                "message": f"Failed to check sessions: {str(e)}"
            }
    
    async def check_system_resources(self) -> Tuple[str, Dict]:
        """Verifica recursos do sistema"""
        try:
            import psutil
            
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memória
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disco
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            # Determinar status
            if cpu_percent > 90 or memory_percent > 90 or disk_percent > 90:
                status = HealthStatus.CRITICAL
                message = "System resources critical"
            elif cpu_percent > 70 or memory_percent > 70 or disk_percent > 80:
                status = HealthStatus.WARNING
                message = "System resources high"
            else:
                status = HealthStatus.HEALTHY
                message = "System resources normal"
            
            return status, {
                "message": message,
                "cpu_percent": f"{cpu_percent}%",
                "memory_percent": f"{memory_percent}%",
                "disk_percent": f"{disk_percent}%"
            }
            
        except ImportError:
            return HealthStatus.UNKNOWN, {
                "message": "psutil not installed - cannot check system resources"
            }
        except Exception as e:
            return HealthStatus.WARNING, {
                "message": f"Failed to check resources: {str(e)}"
            }
    
    async def check_recent_errors(self) -> Tuple[str, Dict]:
        """Verifica erros recentes nos logs"""
        try:
            # Verificar logs do sistema (se disponível)
            log_file = "/var/log/sdr-agent/app.log"
            
            if os.path.exists(log_file):
                # Ler últimas 1000 linhas
                with open(log_file, 'r') as f:
                    lines = f.readlines()[-1000:]
                
                # Contar erros
                error_count = sum(1 for line in lines if "ERROR" in line)
                critical_count = sum(1 for line in lines if "CRITICAL" in line)
                
                if critical_count > 0:
                    status = HealthStatus.CRITICAL
                    message = f"Found {critical_count} critical errors"
                elif error_count > 10:
                    status = HealthStatus.WARNING
                    message = f"Found {error_count} errors in recent logs"
                else:
                    status = HealthStatus.HEALTHY
                    message = "No significant errors in logs"
                
                return status, {
                    "message": message,
                    "error_count": error_count,
                    "critical_count": critical_count
                }
            else:
                return HealthStatus.UNKNOWN, {
                    "message": "Log file not found"
                }
                
        except Exception as e:
            return HealthStatus.UNKNOWN, {
                "message": f"Failed to check logs: {str(e)}"
            }
    
    def _determine_overall_status(self):
        """Determina o status geral baseado nos checks individuais"""
        has_critical = False
        has_warning = False
        
        for check in self.results["checks"].values():
            if check["status"] == HealthStatus.CRITICAL:
                has_critical = True
            elif check["status"] == HealthStatus.WARNING:
                has_warning = True
        
        if has_critical:
            self.results["overall_status"] = HealthStatus.CRITICAL
        elif has_warning:
            self.results["overall_status"] = HealthStatus.WARNING
        else:
            self.results["overall_status"] = HealthStatus.HEALTHY


def print_colored_results(results: Dict[str, Any], critical_only: bool = False):
    """Imprime resultados com cores no terminal"""
    status_colors = {
        HealthStatus.HEALTHY: Fore.GREEN,
        HealthStatus.WARNING: Fore.YELLOW,
        HealthStatus.CRITICAL: Fore.RED,
        HealthStatus.UNKNOWN: Fore.CYAN
    }
    
    status_symbols = {
        HealthStatus.HEALTHY: "✅",
        HealthStatus.WARNING: "⚠️",
        HealthStatus.CRITICAL: "❌",
        HealthStatus.UNKNOWN: "❓"
    }
    
    # Header
    print(f"\n{Fore.BLUE}{'='*60}")
    print(f"{Fore.BLUE}SDR Agent Health Check Report")
    print(f"{Fore.BLUE}{'='*60}{Style.RESET_ALL}")
    
    # Overall status
    overall = results["overall_status"]
    color = status_colors[overall]
    symbol = status_symbols[overall]
    
    print(f"\n{color}Overall Status: {symbol} {overall.upper()}{Style.RESET_ALL}")
    print(f"Timestamp: {results['timestamp']}")
    print(f"Active Sessions: {results['active_sessions']}")
    
    # Individual checks
    print(f"\n{Fore.BLUE}Service Checks:{Style.RESET_ALL}")
    print("-" * 60)
    
    for service, check in results["checks"].items():
        status = check["status"]
        
        # Skip healthy checks if critical_only
        if critical_only and status == HealthStatus.HEALTHY:
            continue
        
        color = status_colors[status]
        symbol = status_symbols[status]
        
        print(f"{color}{symbol} {service:<20} [{check['response_time']}]{Style.RESET_ALL}")
        
        # Detalhes
        details = check["details"]
        if "message" in details:
            print(f"   └─ {details['message']}")
        
        # Outras informações relevantes
        for key, value in details.items():
            if key != "message" and key != "error":
                print(f"   └─ {key}: {value}")
    
    # Warnings
    if results["warnings"]:
        print(f"\n{Fore.YELLOW}Warnings:{Style.RESET_ALL}")
        for warning in results["warnings"]:
            print(f"  ⚠️  {warning}")
    
    # Errors
    if results["errors"]:
        print(f"\n{Fore.RED}Errors:{Style.RESET_ALL}")
        for error in results["errors"]:
            print(f"  ❌ {error}")
    
    # Metrics
    if results.get("metrics"):
        print(f"\n{Fore.BLUE}Metrics:{Style.RESET_ALL}")
        for metric, value in results["metrics"].items():
            print(f"  • {metric}: {value}")
    
    print(f"\n{Fore.BLUE}{'='*60}{Style.RESET_ALL}\n")


async def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="SDR Agent Health Check")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--critical-only", action="store_true", help="Show only critical issues")
    
    args = parser.parse_args()
    
    # Criar checker
    checker = HealthChecker(verbose=args.verbose)
    
    # Executar checks
    try:
        results = await checker.check_all()
        
        # Output
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print_colored_results(results, args.critical_only)
        
        # Exit code
        if results["overall_status"] == HealthStatus.CRITICAL:
            sys.exit(2)
        elif results["overall_status"] == HealthStatus.WARNING:
            sys.exit(1)
        else:
            sys.exit(0)
            
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        sys.exit(2)


if __name__ == "__main__":
    asyncio.run(main())