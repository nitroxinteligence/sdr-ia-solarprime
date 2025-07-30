"""
Main Configuration Module
=========================
Centraliza todas as configurações do sistema
"""

from .agent_config import SDRConfig, get_config

# Instância global de configuração
config = SDRConfig()

# Re-exportar para facilitar imports
__all__ = ['config', 'SDRConfig', 'get_config']

# Alias para compatibilidade
Config = SDRConfig