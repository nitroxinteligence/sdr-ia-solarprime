"""
Environment Configuration Manager
=================================
Gerenciador centralizado de configurações de ambiente
"""

import os
from typing import Dict, Any, Optional
from loguru import logger


class EnvironmentConfig:
    """Configuração centralizada de ambiente"""
    
    def __init__(self):
        self.environment = os.getenv("ENVIRONMENT", "development").lower()
        self.is_production = self.environment == "production"
        self.is_development = self.environment == "development"
        
        # Detectar se está rodando em Docker
        self.is_docker = os.path.exists("/.dockerenv") or os.getenv("DOCKER_CONTAINER", "false").lower() == "true"
        
        # Configurar URLs baseadas no ambiente
        self._configure_urls()
        
        logger.info(f"🔧 Ambiente detectado: {self.environment}")
        logger.info(f"🐳 Docker: {'Sim' if self.is_docker else 'Não'}")
        
    def _configure_urls(self):
        """Configura URLs baseadas no ambiente"""
        
        if self.is_production or self.is_docker:
            # Em produção ou Docker, usar nomes de serviço
            self.evolution_api_url = os.getenv("EVOLUTION_API_URL", "http://evolution-api:8080")
            self.redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
            self.celery_broker_url = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/1")
            self.celery_result_backend = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/2")
        else:
            # Em desenvolvimento, usar localhost
            self.evolution_api_url = os.getenv("EVOLUTION_API_URL", "http://localhost:8080")
            self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
            self.celery_broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1")
            self.celery_result_backend = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")
            
        # Outras configurações
        self.evolution_api_key = os.getenv("EVOLUTION_API_KEY", "")
        self.evolution_instance_name = os.getenv("EVOLUTION_INSTANCE_NAME", "solarprime")
        
        # Log das URLs configuradas
        logger.info(f"📡 Evolution API URL: {self.evolution_api_url}")
        logger.info(f"💾 Redis URL: {self.redis_url}")
        
    def get_service_url(self, service: str) -> str:
        """Retorna URL do serviço baseada no ambiente"""
        urls = {
            "evolution_api": self.evolution_api_url,
            "redis": self.redis_url,
            "celery_broker": self.celery_broker_url,
            "celery_result": self.celery_result_backend
        }
        return urls.get(service, "")
    
    def get_config(self) -> Dict[str, Any]:
        """Retorna configuração completa"""
        return {
            "environment": self.environment,
            "is_production": self.is_production,
            "is_development": self.is_development,
            "is_docker": self.is_docker,
            "urls": {
                "evolution_api": self.evolution_api_url,
                "redis": self.redis_url,
                "celery_broker": self.celery_broker_url,
                "celery_result": self.celery_result_backend
            }
        }
    
    def validate_services(self) -> Dict[str, Dict[str, Any]]:
        """Valida disponibilidade dos serviços"""
        import httpx
        import redis
        import asyncio
        
        results = {}
        
        # Validar Evolution API
        logger.info("🔍 Verificando Evolution API...")
        try:
            with httpx.Client(timeout=3.0) as client:
                response = client.get(f"{self.evolution_api_url}/manager/api/instances")
                results["evolution_api"] = {
                    "available": response.status_code < 500,
                    "status_code": response.status_code,
                    "url": self.evolution_api_url,
                    "message": "OK" if response.status_code < 500 else f"HTTP {response.status_code}"
                }
        except httpx.ConnectError:
            results["evolution_api"] = {
                "available": False,
                "url": self.evolution_api_url,
                "message": "Não foi possível conectar"
            }
        except Exception as e:
            results["evolution_api"] = {
                "available": False,
                "url": self.evolution_api_url,
                "message": str(e)
            }
            
        # Validar Redis
        logger.info("🔍 Verificando Redis...")
        try:
            r = redis.from_url(self.redis_url, socket_connect_timeout=3)
            r.ping()
            results["redis"] = {
                "available": True,
                "url": self.redis_url,
                "message": "OK"
            }
        except redis.ConnectionError:
            results["redis"] = {
                "available": False,
                "url": self.redis_url,
                "message": "Não foi possível conectar"
            }
        except Exception as e:
            results["redis"] = {
                "available": False,
                "url": self.redis_url,
                "message": str(e)
            }
            
        return results
    
    def print_startup_info(self):
        """Imprime informações de startup"""
        print("\n" + "="*60)
        print("🚀 SDR IA SolarPrime - Configuração de Ambiente")
        print("="*60)
        print(f"📍 Ambiente: {self.environment.upper()}")
        print(f"🐳 Docker: {'Sim' if self.is_docker else 'Não'}")
        print(f"🔧 Modo: {'Produção' if self.is_production else 'Desenvolvimento'}")
        print("-"*60)
        
        # Validar serviços
        services_status = self.validate_services()
        
        print("\n📡 Status dos Serviços:")
        print("-"*60)
        
        for service, status in services_status.items():
            icon = "✅" if status["available"] else "⚠️"
            service_name = service.replace("_", " ").title()
            print(f"{icon} {service_name}: {status['url']}")
            if not status["available"]:
                print(f"   └─ {status['message']}")
        
        print("-"*60)
        
        # Avisos para desenvolvimento
        if self.is_development:
            print("\n💡 Dicas para Desenvolvimento:")
            print("-"*60)
            
            if not services_status["evolution_api"]["available"]:
                print("📱 Evolution API não está rodando localmente.")
                print("   Para iniciar: docker run -p 8080:8080 evolution-api/evolution-api")
                
            if not services_status["redis"]["available"]:
                print("💾 Redis não está rodando localmente.")
                print("   Para iniciar: docker run -p 6379:6379 redis:alpine")
                
            print("\n⚡ A aplicação funcionará com funcionalidades limitadas.")
            print("   - WhatsApp: Não disponível sem Evolution API")
            print("   - Cache: Usando memória (sem Redis)")
        
        print("="*60 + "\n")


# Instância global
env_config = EnvironmentConfig()