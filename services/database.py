"""
Database Service
================
Serviço principal para conexão com Supabase
"""

import os
from typing import Optional, Dict, Any
from supabase import create_client, Client
from loguru import logger
from dotenv import load_dotenv

load_dotenv()


class DatabaseService:
    """Serviço de banco de dados com Supabase"""
    
    _instance: Optional['DatabaseService'] = None
    _client: Optional[Client] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is None:
            self._initialize_client()
    
    def _initialize_client(self):
        """Inicializa cliente Supabase"""
        try:
            url = os.getenv("SUPABASE_URL")
            # Usar Service Key para operações do backend (bypassa RLS)
            key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY")
            
            if not url or not key:
                logger.error("Supabase credentials not found in environment")
                raise ValueError("Missing Supabase credentials")
            
            self._client = create_client(url, key)
            logger.info("✅ Supabase client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            raise
    
    @property
    def client(self) -> Client:
        """Retorna cliente Supabase"""
        if self._client is None:
            self._initialize_client()
        return self._client
    
    # Métodos de tabela específicos
    
    @property
    def leads(self):
        """Acesso à tabela leads"""
        return self.client.table("leads")
    
    @property
    def conversations(self):
        """Acesso à tabela conversations"""
        return self.client.table("conversations")
    
    @property
    def messages(self):
        """Acesso à tabela messages"""
        return self.client.table("messages")
    
    @property
    def qualifications(self):
        """Acesso à tabela lead_qualifications"""
        return self.client.table("lead_qualifications")
    
    @property
    def follow_ups(self):
        """Acesso à tabela follow_ups"""
        return self.client.table("follow_ups")
    
    @property
    def analytics(self):
        """Acesso à tabela analytics"""
        return self.client.table("analytics")
    
    # Métodos utilitários
    
    async def health_check(self) -> bool:
        """Verifica conexão com banco"""
        try:
            # Tenta fazer uma query simples
            result = self.leads.select("id").limit(1).execute()
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    def handle_error(self, error: Exception, operation: str) -> Dict[str, Any]:
        """Trata erros de banco de dados"""
        logger.error(f"Database error in {operation}: {error}")
        
        error_message = str(error)
        
        # Erros comuns
        if "duplicate key" in error_message:
            return {
                "error": "duplicate_entry",
                "message": "Registro já existe"
            }
        elif "foreign key" in error_message:
            return {
                "error": "invalid_reference",
                "message": "Referência inválida"
            }
        elif "not found" in error_message:
            return {
                "error": "not_found",
                "message": "Registro não encontrado"
            }
        else:
            return {
                "error": "database_error",
                "message": "Erro ao acessar banco de dados"
            }


# Instância global
db = DatabaseService()

# Alias para compatibilidade
supabase_client = db.client