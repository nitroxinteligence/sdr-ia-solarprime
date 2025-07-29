"""
Main Configuration Module
=========================
Centraliza todas as configurações do sistema
"""

from .agent_config import SDRConfig

# Instância global de configuração
config = SDRConfig()

# Re-exportar para facilitar imports
__all__ = ['config', 'SDRConfig']

# Alias para compatibilidade
Config = SDRConfig