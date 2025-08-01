#!/usr/bin/env python3
"""
Enhanced Health Check - SDR IA SolarPrime

Health check avançado que utiliza testes reais para validar
a integridade completa do sistema em ambiente de produção
ou staging.

CARACTERÍSTICAS:
✅ Testes reais (não-destrutivos) em produção
✅ Monitoramento contínuo de saúde do sistema
✅ Alertas proativos para problemas
✅ Métricas de performance e disponibilidade
✅ Integração com sistema de monitoramento
✅ Relatórios automatizados

MODO DE USO:
    python enhanced_health_check.py [opções]

EXEMPLOS:
    # Health check completo
    python enhanced_health_check.py --full
    
    # Health check específico do Google Calendar
    python enhanced_health_check.py --service google-calendar
    
    # Monitoramento contínuo
    python enhanced_health_check.py --monitor --interval 300
    
    # Health check para CI/CD
    python enhanced_health_check.py --ci --timeout 60
"""

import os
import sys
import argparse
import asyncio
import time
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import logging

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

@dataclass
class HealthCheckResult:
    """Resultado de um health check"""
    service: str
    status: str  # 'healthy', 'degraded', 'unhealthy'
    response_time: float
    timestamp: datetime
    details: Dict[str, Any]
    error: Optional[str] = None

@dataclass
class SystemHealthReport:
    """Relatório completo de saúde do sistema"""
    overall_status: str
    total_checks: int
    healthy_checks: int
    degraded_checks: int
    unhealthy_checks: int
    avg_response_time: float
    timestamp: datetime
    services: List[HealthCheckResult]

class EnhancedHealthChecker:
    """Health checker avançado com testes reais"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._load_default_config()
        self.results: List[HealthCheckResult] = []
        self.logger = self._setup_logging()
        
    def _setup_logging(self) -> logging.Logger:
        """Configura logging para health checks"""
        logger = logging.getLogger('enhanced_health_check')
        logger.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        return logger
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Carrega configuração padrão"""
        return {
            'timeout': 30,
            'retries': 3,
            'thresholds': {
                'response_time_warning': 2.0,
                'response_time_critical': 5.0,
                'success_rate_warning': 95.0,
                'success_rate_critical': 90.0
            },
            'services': {
                'google_calendar': {
                    'enabled': True,
                    'timeout': 10,
                    'critical': True
                },
                'kommo_crm': {
                    'enabled': True,
                    'timeout': 15,
                    'critical': True
                },
                'evolution_api': {
                    'enabled': True,
                    'timeout': 10,
                    'critical': True
                },
                'supabase_db': {
                    'enabled': True,
                    'timeout': 5,
                    'critical': True
                }
            }
        }
    
    async def check_google_calendar_health(self) -> HealthCheckResult:
        """
        Health check avançado do Google Calendar
        
        TESTES:
        - Conectividade e autenticação
        - Tempo de resposta
        - Operações básicas (não-destrutivas)
        - Rate limiting status
        """
        service_name = "google_calendar"
        start_time = time.time()
        
        try:
            self.logger.info("🔍 Iniciando health check do Google Calendar...")
            
            # Import and initialize service
            from agente.services.calendar_service import get_calendar_service
            service = get_calendar_service()
            
            details = {}
            
            # Check 1: Service availability
            if not service.is_available():
                return HealthCheckResult(
                    service=service_name,
                    status='unhealthy',
                    response_time=time.time() - start_time,
                    timestamp=datetime.now(),
                    details={'error': 'Service not available'},
                    error='Google Calendar service not available'
                )
            
            details['service_available'] = True
            
            # Check 2: Authentication & Basic connectivity
            calendar_info = await service._rate_limited_execute(
                service.service.calendars().get,
                calendarId=service.calendar_id
            )
            
            details['authentication'] = 'success'
            details['calendar_id'] = calendar_info.get('id')
            details['calendar_summary'] = calendar_info.get('summary')
            
            # Check 3: Read operations (list recent events)
            end_time = datetime.now() + timedelta(days=1)
            start_search = datetime.now() - timedelta(days=1)
            
            events_result = await service._rate_limited_execute(
                service.service.events().list,
                calendarId=service.calendar_id,
                timeMin=start_search.isoformat() + 'Z',
                timeMax=end_time.isoformat() + 'Z',
                maxResults=5,
                singleEvents=True,
                orderBy='startTime'
            )
            
            details['read_operations'] = 'success'
            details['events_found'] = len(events_result.get('items', []))
            
            # Check 4: Response time validation
            response_time = time.time() - start_time
            details['response_time'] = response_time
            
            # Determine status based on response time
            if response_time <= self.config['thresholds']['response_time_warning']:
                status = 'healthy'
            elif response_time <= self.config['thresholds']['response_time_critical']:
                status = 'degraded'
            else:
                status = 'unhealthy'
            
            self.logger.info(f"✅ Google Calendar health check: {status} ({response_time:.3f}s)")
            
            return HealthCheckResult(
                service=service_name,
                status=status,
                response_time=response_time,
                timestamp=datetime.now(),
                details=details
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            error_msg = f"Google Calendar health check failed: {str(e)}"
            
            self.logger.error(f"❌ {error_msg}")
            
            return HealthCheckResult(
                service=service_name,
                status='unhealthy',
                response_time=response_time,
                timestamp=datetime.now(),
                details={'error': str(e)},
                error=error_msg
            )
    
    async def check_kommo_crm_health(self) -> HealthCheckResult:
        """Health check do Kommo CRM"""
        service_name = "kommo_crm"
        start_time = time.time()
        
        try:
            self.logger.info("🔍 Iniciando health check do Kommo CRM...")
            
            # Basic configuration check
            required_vars = ['KOMMO_SUBDOMAIN', 'KOMMO_LONG_LIVED_TOKEN']
            missing_vars = [var for var in required_vars if not os.getenv(var)]
            
            if missing_vars:
                return HealthCheckResult(
                    service=service_name,
                    status='unhealthy',
                    response_time=time.time() - start_time,
                    timestamp=datetime.now(),
                    details={'missing_config': missing_vars},
                    error=f'Missing configuration: {missing_vars}'
                )
            
            # TODO: Implementar teste real quando serviço estiver pronto
            response_time = time.time() - start_time
            
            self.logger.info("⚠️  Kommo CRM health check: implementação pendente")
            
            return HealthCheckResult(
                service=service_name,
                status='degraded',
                response_time=response_time,
                timestamp=datetime.now(),
                details={'status': 'implementation_pending'},
                error='Health check implementation pending'
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            error_msg = f"Kommo CRM health check failed: {str(e)}"
            
            self.logger.error(f"❌ {error_msg}")
            
            return HealthCheckResult(
                service=service_name,
                status='unhealthy',
                response_time=response_time,
                timestamp=datetime.now(),
                details={'error': str(e)},
                error=error_msg
            )
    
    async def check_evolution_api_health(self) -> HealthCheckResult:
        """Health check da Evolution API"""
        service_name = "evolution_api"
        start_time = time.time()
        
        try:
            self.logger.info("🔍 Iniciando health check da Evolution API...")
            
            # Basic configuration check
            required_vars = ['EVOLUTION_API_URL', 'EVOLUTION_API_KEY', 'EVOLUTION_INSTANCE']
            missing_vars = [var for var in required_vars if not os.getenv(var)]
            
            if missing_vars:
                return HealthCheckResult(
                    service=service_name,
                    status='unhealthy',
                    response_time=time.time() - start_time,
                    timestamp=datetime.now(),
                    details={'missing_config': missing_vars},
                    error=f'Missing configuration: {missing_vars}'
                )
            
            # TODO: Implementar teste real quando serviço estiver pronto
            response_time = time.time() - start_time
            
            self.logger.info("⚠️  Evolution API health check: implementação pendente")
            
            return HealthCheckResult(
                service=service_name,
                status='degraded',
                response_time=response_time,
                timestamp=datetime.now(),
                details={'status': 'implementation_pending'},
                error='Health check implementation pending'
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            error_msg = f"Evolution API health check failed: {str(e)}"
            
            self.logger.error(f"❌ {error_msg}")
            
            return HealthCheckResult(
                service=service_name,
                status='unhealthy',
                response_time=response_time,
                timestamp=datetime.now(),
                details={'error': str(e)},
                error=error_msg
            )
    
    async def check_supabase_db_health(self) -> HealthCheckResult:
        """Health check do Supabase Database"""
        service_name = "supabase_db"
        start_time = time.time()
        
        try:
            self.logger.info("🔍 Iniciando health check do Supabase...")
            
            # Basic configuration check
            required_vars = ['SUPABASE_URL', 'SUPABASE_SERVICE_KEY']
            missing_vars = [var for var in required_vars if not os.getenv(var)]
            
            if missing_vars:
                return HealthCheckResult(
                    service=service_name,
                    status='unhealthy',
                    response_time=time.time() - start_time,
                    timestamp=datetime.now(),
                    details={'missing_config': missing_vars},
                    error=f'Missing configuration: {missing_vars}'
                )
            
            # TODO: Implementar teste real quando serviço estiver pronto
            response_time = time.time() - start_time
            
            self.logger.info("⚠️  Supabase health check: implementação pendente")
            
            return HealthCheckResult(
                service=service_name,
                status='degraded',
                response_time=response_time,
                timestamp=datetime.now(),
                details={'status': 'implementation_pending'},
                error='Health check implementation pending'
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            error_msg = f"Supabase health check failed: {str(e)}"
            
            self.logger.error(f"❌ {error_msg}")
            
            return HealthCheckResult(
                service=service_name,
                status='unhealthy',
                response_time=response_time,
                timestamp=datetime.now(),
                details={'error': str(e)},
                error=error_msg
            )
    
    async def run_all_health_checks(self, services: Optional[List[str]] = None) -> SystemHealthReport:
        """
        Executa todos os health checks ou apenas serviços especificados
        """
        self.logger.info("🚀 Iniciando health checks do sistema...")
        
        # Define which services to check
        available_checks = {
            'google_calendar': self.check_google_calendar_health,
            'kommo_crm': self.check_kommo_crm_health,
            'evolution_api': self.check_evolution_api_health,
            'supabase_db': self.check_supabase_db_health
        }
        
        if services:
            checks_to_run = {k: v for k, v in available_checks.items() if k in services}
        else:
            checks_to_run = {k: v for k, v in available_checks.items() 
                           if self.config['services'].get(k, {}).get('enabled', True)}
        
        # Execute health checks concurrently
        tasks = []
        for service_name, check_func in checks_to_run.items():
            task = asyncio.create_task(check_func())
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        health_results = []
        for result in results:
            if isinstance(result, HealthCheckResult):
                health_results.append(result)
            elif isinstance(result, Exception):
                self.logger.error(f"Health check exception: {result}")
                # Create error result
                health_results.append(HealthCheckResult(
                    service='unknown',
                    status='unhealthy',
                    response_time=0,
                    timestamp=datetime.now(),
                    details={'exception': str(result)},
                    error=str(result)
                ))
        
        # Generate system health report
        report = self._generate_system_report(health_results)
        self.results = health_results
        
        return report
    
    def _generate_system_report(self, results: List[HealthCheckResult]) -> SystemHealthReport:
        """Gera relatório consolidado de saúde do sistema"""
        healthy_count = sum(1 for r in results if r.status == 'healthy')
        degraded_count = sum(1 for r in results if r.status == 'degraded')
        unhealthy_count = sum(1 for r in results if r.status == 'unhealthy')
        
        # Determine overall status
        if unhealthy_count > 0:
            overall_status = 'unhealthy'
        elif degraded_count > 0:
            overall_status = 'degraded'
        else:
            overall_status = 'healthy'
        
        # Calculate average response time
        avg_response_time = sum(r.response_time for r in results) / len(results) if results else 0
        
        return SystemHealthReport(
            overall_status=overall_status,
            total_checks=len(results),
            healthy_checks=healthy_count,
            degraded_checks=degraded_count,
            unhealthy_checks=unhealthy_count,
            avg_response_time=avg_response_time,
            timestamp=datetime.now(),
            services=results
        )
    
    def print_health_report(self, report: SystemHealthReport):
        """Imprime relatório de saúde formatado"""
        status_icons = {
            'healthy': '✅',
            'degraded': '⚠️ ',
            'unhealthy': '❌'
        }
        
        print(f"\n🏥 RELATÓRIO DE SAÚDE DO SISTEMA")
        print("=" * 60)
        print(f"Status Geral: {status_icons[report.overall_status]} {report.overall_status.upper()}")
        print(f"Timestamp: {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Checks Executados: {report.total_checks}")
        print(f"Tempo Médio de Resposta: {report.avg_response_time:.3f}s")
        print()
        
        # Services summary
        print("📊 RESUMO POR STATUS:")
        print(f"   ✅ Saudáveis: {report.healthy_checks}")
        print(f"   ⚠️  Degradados: {report.degraded_checks}")
        print(f"   ❌ Não Saudáveis: {report.unhealthy_checks}")
        print()
        
        # Detailed service results
        print("🔍 DETALHES POR SERVIÇO:")
        print("-" * 60)
        
        for service in report.services:
            icon = status_icons[service.status]
            print(f"{icon} {service.service:15} | {service.response_time:6.3f}s | {service.status}")
            
            if service.error:
                print(f"    ❌ Erro: {service.error}")
            
            # Show key details
            if service.details:
                key_details = {k: v for k, v in service.details.items() 
                             if k in ['calendar_summary', 'events_found', 'authentication']}
                if key_details:
                    details_str = " | ".join(f"{k}: {v}" for k, v in key_details.items())
                    print(f"    ℹ️  {details_str}")
        
        print()
    
    def save_health_report(self, report: SystemHealthReport, filename: Optional[str] = None):
        """Salva relatório de saúde em arquivo JSON"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"health_report_{timestamp}.json"
        
        # Convert to JSON-serializable format
        report_data = {
            'overall_status': report.overall_status,
            'total_checks': report.total_checks,
            'healthy_checks': report.healthy_checks,
            'degraded_checks': report.degraded_checks,
            'unhealthy_checks': report.unhealthy_checks,
            'avg_response_time': report.avg_response_time,
            'timestamp': report.timestamp.isoformat(),
            'services': []
        }
        
        for service in report.services:
            service_data = {
                'service': service.service,
                'status': service.status,
                'response_time': service.response_time,
                'timestamp': service.timestamp.isoformat(),
                'details': service.details,
                'error': service.error
            }
            report_data['services'].append(service_data)
        
        # Save to file
        with open(filename, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        self.logger.info(f"📄 Relatório salvo: {filename}")
    
    async def run_continuous_monitoring(self, interval: int = 300):
        """
        Executa monitoramento contínuo de saúde
        
        Args:
            interval: Intervalo em segundos entre checks (padrão: 5 min)
        """
        self.logger.info(f"🔄 Iniciando monitoramento contínuo (intervalo: {interval}s)")
        
        try:
            while True:
                report = await self.run_all_health_checks()
                self.print_health_report(report)
                
                # Save report with timestamp
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                self.save_health_report(report, f"continuous_health_{timestamp}.json")
                
                # Alert on critical issues
                if report.overall_status == 'unhealthy':
                    self.logger.error("🚨 ALERTA CRÍTICO: Sistema não saudável!")
                
                # Wait for next check
                self.logger.info(f"⏰ Próximo check em {interval}s...")
                await asyncio.sleep(interval)
                
        except KeyboardInterrupt:
            self.logger.info("⏹️  Monitoramento interrompido pelo usuário")

async def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description="Enhanced Health Check para SDR IA SolarPrime",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  %(prog)s --full                          # Health check completo
  %(prog)s --service google-calendar       # Apenas Google Calendar
  %(prog)s --monitor --interval 300        # Monitoramento contínuo
  %(prog)s --ci --timeout 60               # Para CI/CD
        """
    )
    
    # Check type options
    parser.add_argument('--full', action='store_true',
                       help='Executar health check completo de todos os serviços')
    parser.add_argument('--service', type=str, choices=['google-calendar', 'kommo-crm', 'evolution-api', 'supabase-db'],
                       help='Executar health check de serviço específico')
    parser.add_argument('--monitor', action='store_true',
                       help='Executar monitoramento contínuo')
    
    # Configuration options
    parser.add_argument('--interval', type=int, default=300,
                       help='Intervalo para monitoramento contínuo em segundos (padrão: 300)')
    parser.add_argument('--timeout', type=int, default=30,
                       help='Timeout para health checks em segundos (padrão: 30)')
    parser.add_argument('--ci', action='store_true',
                       help='Modo CI/CD com output otimizado')
    
    # Output options
    parser.add_argument('--save-report', action='store_true',
                       help='Salvar relatório em arquivo JSON')
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='Saída mínima (apenas erros)')
    
    args = parser.parse_args()
    
    try:
        # Initialize health checker
        config = {
            'timeout': args.timeout,
            'retries': 3 if not args.ci else 1,
            'thresholds': {
                'response_time_warning': 2.0,
                'response_time_critical': 5.0,
                'success_rate_warning': 95.0,
                'success_rate_critical': 90.0
            }
        }
        
        checker = EnhancedHealthChecker(config)
        
        # Configure logging for CI mode
        if args.ci or args.quiet:
            logging.getLogger('enhanced_health_check').setLevel(logging.WARNING)
        
        # Determine services to check
        services = None
        if args.service:
            services = [args.service.replace('-', '_')]
        
        if args.monitor:
            # Continuous monitoring
            await checker.run_continuous_monitoring(args.interval)
        else:
            # Single health check run
            report = await checker.run_all_health_checks(services)
            
            if not args.quiet:
                checker.print_health_report(report)
            
            if args.save_report:
                checker.save_health_report(report)
            
            # Exit with appropriate code for CI/CD
            if args.ci:
                if report.overall_status == 'healthy':
                    print("HEALTHY")
                    sys.exit(0)
                elif report.overall_status == 'degraded':
                    print("DEGRADED")
                    sys.exit(1)
                else:
                    print("UNHEALTHY")
                    sys.exit(2)
            else:
                sys.exit(0 if report.overall_status != 'unhealthy' else 1)
        
    except KeyboardInterrupt:
        print("\n⏹️  Health check interrompido")
        sys.exit(130)
    except Exception as e:
        print(f"\n🚨 ERRO CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(2)

if __name__ == "__main__":
    asyncio.run(main())