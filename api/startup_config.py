"""
Startup Configuration Validator
================================
Valida configurações e serviços no startup da aplicação
"""

import os
import sys
from typing import Dict, Any, List
from loguru import logger

# Importar configuração centralizada
try:
    from core.environment import env_config
except ImportError:
    logger.error("❌ Não foi possível importar configuração de ambiente")
    env_config = None


class StartupValidator:
    """Validador de configuração no startup"""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: List[str] = []
        
    def validate_environment_variables(self) -> bool:
        """Valida variáveis de ambiente obrigatórias"""
        required_vars = {
            "GEMINI_API_KEY": "API Key do Google Gemini para IA",
            "EVOLUTION_API_KEY": "API Key da Evolution API para WhatsApp",
            "EVOLUTION_INSTANCE_NAME": "Nome da instância Evolution API",
        }
        
        optional_vars = {
            "REDIS_URL": "URL do Redis para cache",
            "SUPABASE_URL": "URL do Supabase para banco de dados",
            "SUPABASE_KEY": "Chave do Supabase",
            "KOMMO_CLIENT_ID": "ID do cliente Kommo CRM",
            "KOMMO_CLIENT_SECRET": "Secret do cliente Kommo CRM",
        }
        
        all_valid = True
        
        # Verificar obrigatórias
        for var, description in required_vars.items():
            value = os.getenv(var)
            if not value:
                self.errors.append(f"❌ {var} não configurada - {description}")
                all_valid = False
            else:
                # Ocultar valor sensível
                masked_value = value[:4] + "****" if len(value) > 4 else "****"
                self.info.append(f"✅ {var} configurada ({masked_value}...)")
        
        # Verificar opcionais
        for var, description in optional_vars.items():
            value = os.getenv(var)
            if not value:
                self.warnings.append(f"⚠️  {var} não configurada - {description}")
            else:
                self.info.append(f"✅ {var} configurada")
                
        return all_valid
    
    def validate_services(self) -> Dict[str, bool]:
        """Valida conectividade com serviços externos"""
        if not env_config:
            self.errors.append("❌ Configuração de ambiente não disponível")
            return {}
            
        return env_config.validate_services()
    
    def validate_file_permissions(self) -> bool:
        """Valida permissões de escrita em diretórios importantes"""
        directories = ["logs", "temp", "uploads", "data"]
        all_valid = True
        
        for directory in directories:
            path = os.path.join(os.getcwd(), directory)
            if not os.path.exists(path):
                try:
                    os.makedirs(path, exist_ok=True)
                    self.info.append(f"✅ Diretório {directory} criado")
                except Exception as e:
                    self.errors.append(f"❌ Não foi possível criar diretório {directory}: {e}")
                    all_valid = False
            elif not os.access(path, os.W_OK):
                self.errors.append(f"❌ Sem permissão de escrita em {directory}")
                all_valid = False
            else:
                self.info.append(f"✅ Diretório {directory} OK")
                
        return all_valid
    
    def print_validation_report(self):
        """Imprime relatório de validação"""
        print("\n" + "="*60)
        print("🔍 Validação de Configuração - SDR IA SolarPrime")
        print("="*60)
        
        # Informações
        if self.info:
            print("\nℹ️  Informações:")
            for info in self.info:
                print(f"   {info}")
        
        # Avisos
        if self.warnings:
            print("\n⚠️  Avisos:")
            for warning in self.warnings:
                print(f"   {warning}")
        
        # Erros
        if self.errors:
            print("\n❌ Erros:")
            for error in self.errors:
                print(f"   {error}")
        
        # Status final
        print("\n" + "-"*60)
        if self.errors:
            print("❌ Validação FALHOU - Corrija os erros acima")
        elif self.warnings:
            print("⚠️  Validação OK com avisos - Funcionalidade limitada")
        else:
            print("✅ Validação OK - Todos os sistemas operacionais")
        print("="*60 + "\n")
    
    def should_fail_startup(self) -> bool:
        """Determina se deve falhar o startup baseado nos erros"""
        # Em desenvolvimento, não falhar por serviços externos
        if env_config and env_config.is_development:
            # Só falhar se houver erros críticos (não relacionados a serviços)
            critical_errors = [e for e in self.errors if "Redis" not in e and "Evolution API" not in e]
            return len(critical_errors) > 0
        
        # Em produção, falhar se houver qualquer erro
        return len(self.errors) > 0
    
    def run_validation(self) -> bool:
        """Executa todas as validações"""
        logger.info("🔍 Iniciando validação de configuração...")
        
        # 1. Validar variáveis de ambiente
        env_valid = self.validate_environment_variables()
        
        # 2. Validar permissões de arquivo
        files_valid = self.validate_file_permissions()
        
        # 3. Validar serviços (não falha em desenvolvimento)
        services = self.validate_services()
        
        # 4. Imprimir informações do ambiente
        if env_config:
            env_config.print_startup_info()
        
        # 5. Imprimir relatório de validação
        self.print_validation_report()
        
        # Retornar se deve continuar ou não
        return not self.should_fail_startup()


# Função utilitária para uso no startup
def validate_startup_config() -> bool:
    """Valida configuração no startup da aplicação"""
    validator = StartupValidator()
    return validator.run_validation()