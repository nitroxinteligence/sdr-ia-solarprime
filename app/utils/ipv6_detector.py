"""
Detector de suporte IPv6 - Solução inteligente para Supabase
"""
import socket
import os
from loguru import logger


def has_ipv6_support() -> bool:
    """
    Verifica se o sistema suporta IPv6
    
    Returns:
        True se IPv6 está disponível, False caso contrário
    """
    try:
        # Tenta criar um socket IPv6
        sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        # Tenta conectar a um endereço IPv6 de teste (Google DNS)
        sock.connect(("2001:4860:4860::8888", 80))
        sock.close()
        logger.info("✅ IPv6 suportado neste ambiente")
        return True
    except (socket.error, OSError):
        logger.warning("⚠️ IPv6 NÃO suportado neste ambiente")
        return False


def convert_to_pooler_url(db_url: str) -> str:
    """
    Converte URL direta do Supabase para URL do pooler (suporta IPv4)
    
    Args:
        db_url: URL original do banco
        
    Returns:
        URL do pooler que suporta IPv4
    """
    # Extrai componentes da URL
    if "@" not in db_url:
        return db_url
        
    # Separa credenciais e host
    parts = db_url.split("@")
    credentials = parts[0]  # postgresql://user:pass
    host_and_rest = parts[1]  # host:port/database
    
    # Extrai o project ID do host
    if "db." in host_and_rest and ".supabase.co" in host_and_rest:
        # Formato: db.rcjcpwqezmlhenmhrski.supabase.co:6543/postgres
        project_id = host_and_rest.split(".")[1]
        
        # Detecta a região (padrão para us-east-1 se não especificado)
        # Você pode customizar isso baseado na sua região
        region = os.getenv("SUPABASE_REGION", "us-east-1")
        
        # Constrói nova URL usando o pooler
        # Formato: aws-0-[region].pooler.supabase.com
        pooler_host = f"aws-0-{region}.pooler.supabase.com"
        
        # Mantém a porta 6543 (transaction mode) para melhor compatibilidade
        new_url = f"{credentials}@{pooler_host}:6543/postgres"
        
        logger.info(f"🔄 URL convertida para pooler IPv4: ...@{pooler_host}:6543/postgres")
        return new_url
    
    # Se não é uma URL Supabase padrão, retorna sem modificar
    return db_url


def get_optimal_postgres_url(original_url: str) -> str:
    """
    Retorna a melhor URL PostgreSQL baseada no suporte de IPv6
    
    Args:
        original_url: URL original do banco
        
    Returns:
        URL otimizada (pooler se não há IPv6, original se há)
    """
    # Verifica se já é uma URL do pooler
    if "pooler.supabase.com" in original_url:
        logger.info("✅ Já está usando pooler Supabase")
        return original_url
    
    # Se não suporta IPv6, converte para pooler
    if not has_ipv6_support():
        logger.warning("🔄 Convertendo para pooler Supabase (IPv4)")
        return convert_to_pooler_url(original_url)
    
    # Se suporta IPv6, usa a URL original
    logger.info("✅ Usando conexão direta (IPv6 suportado)")
    return original_url