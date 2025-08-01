#!/usr/bin/env python3
"""
Script para Execução de Testes Reais - SDR IA SolarPrime

Script de conveniência para executar testes reais com configurações adequadas.
Inclui validação de ambiente, relatórios de performance e cleanup automático.

MODO DE USO:
    python run_real_tests.py [opções]

EXEMPLOS:
    # Executar todos os testes de integração real
    python run_real_tests.py --integration
    
    # Executar apenas testes do Google Calendar
    python run_real_tests.py --google-calendar
    
    # Executar testes de performance
    python run_real_tests.py --performance
    
    # Executar teste específico
    python run_real_tests.py --test test_service_account_authentication
    
    # Modo verboso com relatórios detalhados
    python run_real_tests.py --integration --verbose --report
"""

import os
import sys
import argparse
import subprocess
import asyncio
from pathlib import Path
from datetime import datetime
import json

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

class RealTestRunner:
    """Runner para testes reais com configurações avançadas"""
    
    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.config_file = self.test_dir / "pytest_real.ini"
        self.results = {}
        
    def setup_environment(self):
        """Configura ambiente para testes reais"""
        print("🔧 Configurando ambiente de testes reais...")
        
        # Set environment variables
        os.environ['PYTEST_RUNNING'] = 'true'
        os.environ['TESTING'] = 'true'
        os.environ['ENVIRONMENT'] = 'test'
        
        # Validate required environment variables
        required_vars = [
            'GOOGLE_PROJECT_ID',
            'GOOGLE_PRIVATE_KEY',
            'GOOGLE_SERVICE_ACCOUNT_EMAIL',
            'GOOGLE_CALENDAR_ID'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
                
        if missing_vars:
            print(f"❌ Variáveis de ambiente faltando: {missing_vars}")
            print("💡 Configure as credenciais de teste antes de executar")
            return False
            
        print("✅ Ambiente configurado com sucesso")
        return True
    
    def build_pytest_command(self, args):
        """Constrói comando pytest baseado nos argumentos"""
        cmd = [
            'python', '-m', 'pytest',
            '-c', str(self.config_file),
            '--tb=short',
            '--durations=10'
        ]
        
        # Add verbosity
        if args.verbose:
            cmd.extend(['-v', '-s'])
        else:
            cmd.append('-q')
            
        # Add markers based on test type
        if args.integration:
            cmd.extend(['-m', 'integration_real'])
        elif args.performance:
            cmd.extend(['-m', 'performance_real'])
        elif args.google_calendar:
            cmd.extend(['-m', 'google_calendar'])
        elif args.test:
            cmd.extend(['-k', args.test])
            
        # Add test paths
        if args.integration or args.google_calendar or args.test:
            cmd.append(str(self.test_dir / 'real_integration'))
        elif args.performance:
            cmd.append(str(self.test_dir / 'performance_real'))
        else:
            # Default: run all real tests
            cmd.extend([
                str(self.test_dir / 'real_integration'),
                str(self.test_dir / 'e2e_real'),
                str(self.test_dir / 'performance_real')
            ])
            
        # Add output options
        if args.report:
            report_file = self.test_dir / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            cmd.extend(['--html', str(report_file), '--self-contained-html'])
            
        if args.coverage:
            cmd.extend([
                '--cov=agente',
                '--cov-report=html',
                '--cov-report=term-missing'
            ])
            
        return cmd
    
    def run_environment_setup(self):
        """Executa setup do ambiente de teste"""
        print("\n🧪 Executando setup do ambiente...")
        
        setup_script = self.test_dir / "setup_test_environment.py"
        if setup_script.exists():
            try:
                result = subprocess.run([
                    'python', str(setup_script)
                ], capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    print("✅ Setup do ambiente concluído")
                    print(result.stdout)
                    return True
                else:
                    print("❌ Falha no setup do ambiente")
                    print(result.stderr)
                    return False
                    
            except subprocess.TimeoutExpired:
                print("❌ Setup do ambiente excedeu timeout de 60s")
                return False
        else:
            print("⚠️  Script de setup não encontrado, continuando...")
            return True
    
    def run_tests(self, args):
        """Executa os testes com configurações especificadas"""
        start_time = datetime.now()
        
        print(f"\n🚀 Iniciando testes reais - {start_time.strftime('%H:%M:%S')}")
        print("=" * 60)
        
        # Build and execute pytest command
        cmd = self.build_pytest_command(args)
        
        print(f"📝 Comando: {' '.join(cmd)}")
        print()
        
        try:
            result = subprocess.run(cmd, timeout=args.timeout)
            
            end_time = datetime.now()
            duration = end_time - start_time
            
            print("\n" + "=" * 60)
            print(f"⏱️  Duração total: {duration}")
            print(f"📊 Código de saída: {result.returncode}")
            
            # Store results
            self.results = {
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration_seconds': duration.total_seconds(),
                'exit_code': result.returncode,
                'command': ' '.join(cmd)
            }
            
            if result.returncode == 0:
                print("✅ TODOS OS TESTES PASSARAM!")
            else:
                print("❌ ALGUNS TESTES FALHARAM")
                
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            print(f"\n❌ TIMEOUT: Testes excederam {args.timeout}s")
            return False
        except KeyboardInterrupt:
            print("\n⏹️  Testes interrompidos pelo usuário")
            return False
    
    def generate_summary_report(self, args):
        """Gera relatório resumido dos testes"""
        if not self.results:
            return
            
        print("\n📋 RELATÓRIO RESUMIDO")
        print("=" * 40)
        print(f"Início: {self.results['start_time']}")
        print(f"Fim: {self.results['end_time']}")
        print(f"Duração: {self.results['duration_seconds']:.1f}s")
        print(f"Status: {'SUCESSO' if self.results['exit_code'] == 0 else 'FALHA'}")
        
        # Save detailed report
        if args.report:
            report_file = self.test_dir / f"test_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w') as f:
                json.dump(self.results, f, indent=2)
            print(f"📄 Relatório salvo: {report_file}")
    
    def cleanup_test_data(self):
        """Executa limpeza de dados de teste restantes"""
        print("\n🧹 Limpeza automática...")
        
        cleanup_script = self.test_dir / "cleanup_test_data.py"
        if cleanup_script.exists():
            try:
                subprocess.run([
                    'python', str(cleanup_script)
                ], timeout=30)
                print("✅ Limpeza concluída")
            except:
                print("⚠️  Limpeza não pôde ser executada")
        else:
            print("ℹ️  Script de limpeza não encontrado")

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description="Executa testes reais do SDR IA SolarPrime",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  %(prog)s --integration                    # Testes de integração
  %(prog)s --google-calendar --verbose      # Testes Google Calendar verbosos
  %(prog)s --performance --report           # Testes de performance com relatório
  %(prog)s --test test_create_event_real    # Teste específico
        """
    )
    
    # Test type options
    test_group = parser.add_mutually_exclusive_group()
    test_group.add_argument('--integration', action='store_true',
                           help='Executar testes de integração real')
    test_group.add_argument('--performance', action='store_true',
                           help='Executar testes de performance')
    test_group.add_argument('--google-calendar', action='store_true',
                           help='Executar apenas testes do Google Calendar')
    test_group.add_argument('--test', type=str,
                           help='Executar teste específico por nome')
    
    # Output options
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Saída verbosa com detalhes')
    parser.add_argument('--report', action='store_true',
                       help='Gerar relatório HTML detalhado')
    parser.add_argument('--coverage', action='store_true',
                       help='Gerar relatório de cobertura de código')
    
    # Execution options
    parser.add_argument('--timeout', type=int, default=600,
                       help='Timeout em segundos (padrão: 600)')
    parser.add_argument('--no-setup', action='store_true',
                       help='Pular setup do ambiente')
    parser.add_argument('--no-cleanup', action='store_true',
                       help='Pular limpeza automática')
    
    args = parser.parse_args()
    
    # Initialize runner
    runner = RealTestRunner()
    
    try:
        # Setup environment
        if not runner.setup_environment():
            sys.exit(1)
        
        # Run environment setup script
        if not args.no_setup:
            if not runner.run_environment_setup():
                print("⚠️  Continuando apesar de falha no setup...")
        
        # Run tests
        success = runner.run_tests(args)
        
        # Generate reports
        runner.generate_summary_report(args)
        
        # Cleanup
        if not args.no_cleanup:
            runner.cleanup_test_data()
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n⏹️  Execução interrompida")
        sys.exit(130)
    except Exception as e:
        print(f"\n🚨 ERRO CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(2)

if __name__ == "__main__":
    main()