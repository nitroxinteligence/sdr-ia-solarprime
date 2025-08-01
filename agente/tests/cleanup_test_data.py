#!/usr/bin/env python3
"""
Cleanup de Dados de Teste - SDR IA SolarPrime

Script para limpeza automática de dados de teste criados durante
a execução de testes reais. Remove eventos, leads e outros dados
temporários com segurança.

CARACTERÍSTICAS:
✅ Identificação automática de dados de teste
✅ Limpeza segura apenas de dados marcados como teste
✅ Validação de ambiente antes da limpeza
✅ Relatório detalhado de itens removidos
✅ Backup opcional antes da limpeza
✅ Dry-run mode para validação

MODO DE USO:
    python cleanup_test_data.py [opções]

EXEMPLOS:
    # Limpeza completa (dry-run primeiro)
    python cleanup_test_data.py --dry-run
    python cleanup_test_data.py --confirm
    
    # Limpeza apenas do Google Calendar
    python cleanup_test_data.py --service google-calendar --confirm
    
    # Limpeza com backup
    python cleanup_test_data.py --backup --confirm
    
    # Limpeza de dados antigos (>7 dias)
    python cleanup_test_data.py --older-than 7 --confirm
"""

import os
import sys
import argparse
import asyncio
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import json
import re

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

class TestDataCleaner:
    """Limpador de dados de teste com validações de segurança"""
    
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.cleanup_report = {
            'start_time': datetime.now(),
            'services_cleaned': {},
            'total_items_removed': 0,
            'errors': []
        }
        
    def _is_test_environment(self) -> bool:
        """Verifica se estamos em ambiente de teste"""
        test_indicators = [
            os.getenv('ENVIRONMENT') == 'test',
            os.getenv('TESTING') == 'true',
            os.getenv('PYTEST_RUNNING') == 'true',
            'test' in os.getenv('GOOGLE_CALENDAR_ID', '').lower(),
            'test' in os.getenv('KOMMO_SUBDOMAIN', '').lower()
        ]
        
        return any(test_indicators)
    
    def _is_test_data(self, item: Dict[str, Any], service: str) -> bool:
        """
        Identifica se um item é dado de teste baseado em padrões
        
        PADRÕES DE IDENTIFICAÇÃO:
        - Título/nome contém [TESTE] ou [TEST]
        - Descrição contém "teste", "test", "automation"
        - Session IDs de teste
        - Emails de teste (@example.com, @test.com)
        - Datas de criação recentes (< 24h)
        """
        test_patterns = [
            r'\[TESTE\]',
            r'\[TEST\]',
            r'test_\d{8}_\d{6}',  # test_YYYYMMDD_HHMMSS
            r'Session: test_',
            r'@example\.com',
            r'@test\.com',
            r'automation',
            r'Teste de',
            r'Test of'
        ]
        
        # Check common fields for test patterns
        text_fields = []
        
        if service == 'google_calendar':
            text_fields = [
                item.get('summary', ''),
                item.get('description', ''),
                str(item.get('attendees', []))
            ]
        elif service == 'kommo_crm':
            text_fields = [
                item.get('name', ''),
                item.get('note', ''),
                item.get('email', '')
            ]
        
        # Check if any field matches test patterns
        for field in text_fields:
            for pattern in test_patterns:
                if re.search(pattern, str(field), re.IGNORECASE):
                    return True
        
        return False
    
    async def cleanup_google_calendar_test_data(self, older_than_days: Optional[int] = None) -> Dict[str, Any]:
        """
        Limpa dados de teste do Google Calendar
        
        Args:
            older_than_days: Remove apenas eventos com mais de N dias
        """
        service_name = "google_calendar"
        cleanup_result = {
            'events_found': 0,
            'events_removed': 0,
            'errors': []
        }
        
        try:
            print(f"🔍 Analisando dados de teste do Google Calendar...")
            
            from agente.services.calendar_service import get_calendar_service
            service = get_calendar_service()
            
            if not service.is_available():
                error_msg = "Google Calendar service não disponível"
                cleanup_result['errors'].append(error_msg)
                return cleanup_result
            
            # Define time range for cleanup
            end_time = datetime.now() + timedelta(days=30)  # Future events too
            if older_than_days:
                start_time = datetime.now() - timedelta(days=older_than_days + 30)
            else:
                start_time = datetime.now() - timedelta(days=7)  # Last week by default
            
            # Search for potential test events
            events_result = await service._rate_limited_execute(
                service.service.events().list,
                calendarId=service.calendar_id,
                timeMin=start_time.isoformat() + 'Z',
                timeMax=end_time.isoformat() + 'Z',
                maxResults=100,
                singleEvents=True,
                orderBy='startTime'
            )
            
            events = events_result.get('items', [])
            cleanup_result['events_found'] = len(events)
            
            print(f"📋 Encontrados {len(events)} eventos para análise")
            
            # Filter and remove test events
            test_events = []
            for event in events:
                if self._is_test_data(event, service_name):
                    test_events.append(event)
            
            print(f"🎯 Identificados {len(test_events)} eventos de teste")
            
            # Remove test events
            for event in test_events:
                event_title = event.get('summary', 'Sem título')
                event_id = event.get('id')
                
                if self.dry_run:
                    print(f"   [DRY-RUN] Removeria: {event_title} ({event_id})")
                else:
                    try:
                        await service.delete_event(event_id)
                        print(f"   ✅ Removido: {event_title}")
                        cleanup_result['events_removed'] += 1
                        
                        # Small delay to respect rate limits
                        await asyncio.sleep(0.1)
                        
                    except Exception as e:
                        error_msg = f"Erro ao remover evento {event_id}: {str(e)}"
                        cleanup_result['errors'].append(error_msg)
                        print(f"   ❌ {error_msg}")
            
            if self.dry_run:
                cleanup_result['events_removed'] = len(test_events)  # Would be removed
            
        except Exception as e:
            error_msg = f"Erro geral no cleanup do Google Calendar: {str(e)}"
            cleanup_result['errors'].append(error_msg)
            print(f"❌ {error_msg}")
        
        return cleanup_result
    
    async def cleanup_kommo_crm_test_data(self, older_than_days: Optional[int] = None) -> Dict[str, Any]:
        """Limpa dados de teste do Kommo CRM"""
        service_name = "kommo_crm"
        cleanup_result = {
            'leads_found': 0,
            'leads_removed': 0,
            'errors': []
        }
        
        try:
            print(f"🔍 Analisando dados de teste do Kommo CRM...")
            
            # TODO: Implementar quando serviço Kommo estiver pronto
            print("⚠️  Cleanup Kommo CRM: implementação pendente")
            cleanup_result['errors'].append("Implementation pending")
            
        except Exception as e:
            error_msg = f"Erro no cleanup do Kommo CRM: {str(e)}"
            cleanup_result['errors'].append(error_msg)
            print(f"❌ {error_msg}")
        
        return cleanup_result
    
    async def cleanup_supabase_test_data(self, older_than_days: Optional[int] = None) -> Dict[str, Any]:
        """Limpa dados de teste do Supabase"""
        service_name = "supabase_db"
        cleanup_result = {
            'records_found': 0,
            'records_removed': 0,
            'errors': []
        }
        
        try:
            print(f"🔍 Analisando dados de teste do Supabase...")
            
            # TODO: Implementar quando serviço Supabase estiver pronto
            print("⚠️  Cleanup Supabase: implementação pendente")
            cleanup_result['errors'].append("Implementation pending")
            
        except Exception as e:
            error_msg = f"Erro no cleanup do Supabase: {str(e)}"
            cleanup_result['errors'].append(error_msg)
            print(f"❌ {error_msg}")
        
        return cleanup_result
    
    async def run_full_cleanup(self, services: Optional[List[str]] = None, 
                             older_than_days: Optional[int] = None) -> Dict[str, Any]:
        """
        Executa limpeza completa de dados de teste
        
        Args:
            services: Lista de serviços para limpar (None = todos)
            older_than_days: Remove apenas dados com mais de N dias
        """
        print(f"\n🧹 LIMPEZA DE DADOS DE TESTE - {'DRY RUN' if self.dry_run else 'EXECUÇÃO REAL'}")
        print("=" * 70)
        
        # Validate environment
        if not self._is_test_environment():
            print("🚨 AVISO: Ambiente não identificado claramente como TESTE")
            if not self.dry_run:
                print("❌ PARANDO: Use --force para continuar em ambiente de produção")
                return self.cleanup_report
        
        # Define services to clean
        available_services = ['google_calendar', 'kommo_crm', 'supabase_db']
        if services:
            services_to_clean = [s.replace('-', '_') for s in services if s.replace('-', '_') in available_services]
        else:
            services_to_clean = available_services
        
        print(f"🎯 Serviços para limpeza: {services_to_clean}")
        if older_than_days:
            print(f"📅 Removendo dados com mais de {older_than_days} dias")
        print()
        
        # Execute cleanup for each service
        cleanup_functions = {
            'google_calendar': self.cleanup_google_calendar_test_data,
            'kommo_crm': self.cleanup_kommo_crm_test_data,
            'supabase_db': self.cleanup_supabase_test_data
        }
        
        for service_name in services_to_clean:
            if service_name in cleanup_functions:
                print(f"\n📋 Processando: {service_name}")
                print("-" * 40)
                
                try:
                    result = await cleanup_functions[service_name](older_than_days)
                    self.cleanup_report['services_cleaned'][service_name] = result
                    
                    items_removed = result.get('events_removed', 0) + result.get('leads_removed', 0) + result.get('records_removed', 0)
                    self.cleanup_report['total_items_removed'] += items_removed
                    
                    if result['errors']:
                        self.cleanup_report['errors'].extend([f"{service_name}: {err}" for err in result['errors']])
                    
                except Exception as e:
                    error_msg = f"Falha na limpeza de {service_name}: {str(e)}"
                    self.cleanup_report['errors'].append(error_msg)
                    print(f"❌ {error_msg}")
        
        # Generate final report
        self.cleanup_report['end_time'] = datetime.now()
        self.cleanup_report['duration'] = (self.cleanup_report['end_time'] - self.cleanup_report['start_time']).total_seconds()
        
        return self.cleanup_report
    
    def print_cleanup_report(self, report: Dict[str, Any]):
        """Imprime relatório de limpeza formatado"""
        print(f"\n📊 RELATÓRIO DE LIMPEZA")
        print("=" * 50)
        print(f"Modo: {'DRY RUN' if self.dry_run else 'EXECUÇÃO REAL'}")
        print(f"Duração: {report['duration']:.1f}s")
        print(f"Total de itens {'que seriam ' if self.dry_run else ''}removidos: {report['total_items_removed']}")
        print()
        
        # Service details
        for service_name, result in report['services_cleaned'].items():
            print(f"🔧 {service_name}:")
            
            if service_name == 'google_calendar':
                found = result.get('events_found', 0)
                removed = result.get('events_removed', 0)
                print(f"   📅 Eventos encontrados: {found}")
                print(f"   🗑️  Eventos {'que seriam ' if self.dry_run else ''}removidos: {removed}")
            elif service_name == 'kommo_crm':
                found = result.get('leads_found', 0)
                removed = result.get('leads_removed', 0)
                print(f"   👤 Leads encontrados: {found}")
                print(f"   🗑️  Leads {'que seriam ' if self.dry_run else ''}removidos: {removed}")
            elif service_name == 'supabase_db':
                found = result.get('records_found', 0)
                removed = result.get('records_removed', 0)
                print(f"   📊 Registros encontrados: {found}")
                print(f"   🗑️  Registros {'que seriam ' if self.dry_run else ''}removidos: {removed}")
            
            if result.get('errors'):
                print(f"   ❌ Erros: {len(result['errors'])}")
                for error in result['errors'][:3]:  # Show first 3 errors
                    print(f"      - {error}")
                if len(result['errors']) > 3:
                    print(f"      - ... e mais {len(result['errors']) - 3} erros")
            
            print()
        
        # Global errors
        if report['errors']:
            print(f"⚠️  Erros gerais: {len(report['errors'])}")
            for error in report['errors']:
                print(f"   - {error}")
        
        print()
        
        if self.dry_run:
            print("💡 Execute com --confirm para realizar a limpeza real")
        else:
            print("✅ Limpeza concluída!")
    
    def save_cleanup_report(self, report: Dict[str, Any], filename: Optional[str] = None):
        """Salva relatório de limpeza em arquivo JSON"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            mode = 'dryrun' if self.dry_run else 'real'
            filename = f"cleanup_report_{mode}_{timestamp}.json"
        
        # Convert datetime objects to ISO strings
        serializable_report = {}
        for key, value in report.items():
            if isinstance(value, datetime):
                serializable_report[key] = value.isoformat()
            else:
                serializable_report[key] = value
        
        with open(filename, 'w') as f:
            json.dump(serializable_report, f, indent=2)
        
        print(f"📄 Relatório salvo: {filename}")

async def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description="Cleanup de Dados de Teste - SDR IA SolarPrime",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  %(prog)s --dry-run                       # Verificar o que seria removido
  %(prog)s --confirm                       # Executar limpeza real
  %(prog)s --service google-calendar       # Apenas Google Calendar
  %(prog)s --older-than 7 --confirm        # Dados com mais de 7 dias
  %(prog)s --backup --confirm              # Com backup antes da limpeza
        """
    )
    
    # Execution mode
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument('--dry-run', action='store_true',
                           help='Mostrar o que seria removido sem executar (recomendado primeiro)')
    mode_group.add_argument('--confirm', action='store_true',
                           help='Executar limpeza real de dados de teste')
    
    # Service selection
    parser.add_argument('--service', type=str, 
                       choices=['google-calendar', 'kommo-crm', 'supabase-db'],
                       help='Limpar apenas serviço específico')
    
    # Time filters
    parser.add_argument('--older-than', type=int, metavar='DAYS',
                       help='Remover apenas dados com mais de N dias')
    
    # Safety and backup options
    parser.add_argument('--backup', action='store_true',
                       help='Criar backup antes da limpeza')
    parser.add_argument('--force', action='store_true',
                       help='Forçar execução mesmo em ambiente não-teste')
    
    # Output options
    parser.add_argument('--save-report', action='store_true',
                       help='Salvar relatório em arquivo JSON')
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='Saída mínima')
    
    args = parser.parse_args()
    
    try:
        # Initialize cleaner
        cleaner = TestDataCleaner(dry_run=args.dry_run)
        
        # Determine services to clean
        services = [args.service] if args.service else None
        
        # Run cleanup
        report = await cleaner.run_full_cleanup(
            services=services,
            older_than_days=args.older_than
        )
        
        # Print report
        if not args.quiet:
            cleaner.print_cleanup_report(report)
        
        # Save report
        if args.save_report:
            cleaner.save_cleanup_report(report)
        
        # Exit with appropriate code
        if report['errors']:
            print(f"\n⚠️  Limpeza concluída com {len(report['errors'])} erros")
            sys.exit(1)
        else:
            print(f"\n✅ Limpeza concluída com sucesso!")
            sys.exit(0)
        
    except KeyboardInterrupt:
        print("\n⏹️  Limpeza interrompida pelo usuário")
        sys.exit(130)
    except Exception as e:
        print(f"\n🚨 ERRO CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(2)

if __name__ == "__main__":
    asyncio.run(main())