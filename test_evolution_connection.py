#!/usr/bin/env python3
"""
Script de teste para verificar conexão com Evolution API
"""
import asyncio
import sys
from pathlib import Path

# Adiciona o diretório do projeto ao path
sys.path.insert(0, str(Path(__file__).parent))

from app.integrations.evolution import evolution_client
from app.utils.logger import emoji_logger
from loguru import logger

async def test_connection():
    """Testa a conexão com Evolution API"""
    
    print("\n" + "="*60)
    print("🔧 TESTE DE CONEXÃO COM EVOLUTION API")
    print("="*60 + "\n")
    
    try:
        # 1. Teste de health check
        print("1️⃣ Testando Health Check...")
        health_status = await evolution_client.health_check()
        if health_status:
            emoji_logger.evolution_success("✅ Health check passou!")
        else:
            emoji_logger.evolution_error("❌ Health check falhou!")
        
        # 2. Teste de informações da instância
        print("\n2️⃣ Obtendo informações da instância...")
        try:
            info = await evolution_client.get_instance_info()
            emoji_logger.evolution_success(f"✅ Instância: {evolution_client.instance_name}")
            emoji_logger.system_info(f"Status: {info.get('state', 'unknown')}")
            
            if info.get('state') == 'open':
                emoji_logger.evolution_success("✅ WhatsApp conectado!")
            else:
                emoji_logger.evolution_warning("⚠️ WhatsApp não conectado. Estado: " + str(info.get('state')))
                
        except Exception as e:
            emoji_logger.evolution_error(f"❌ Erro ao obter info da instância: {e}")
        
        # 3. Teste do circuit breaker
        print("\n3️⃣ Testando Circuit Breaker...")
        emoji_logger.system_info(f"Falhas: {evolution_client._circuit_breaker_failure_count}/{evolution_client._circuit_breaker_threshold}")
        emoji_logger.system_info(f"Connection Failed: {evolution_client._connection_failed}")
        
        # 4. Teste de reconexão
        print("\n4️⃣ Testando capacidade de reconexão...")
        # Força uma falha para testar reconexão
        evolution_client._connection_failed = True
        await evolution_client.health_check()
        
        if not evolution_client._connection_failed:
            emoji_logger.evolution_success("✅ Reconexão automática funcionando!")
        else:
            emoji_logger.system_warning("⚠️ Reconexão não foi bem sucedida")
        
        print("\n" + "="*60)
        print("📊 RESUMO DO TESTE")
        print("="*60)
        
        if health_status and not evolution_client._connection_failed:
            emoji_logger.evolution_success("✅ Conexão com Evolution API está FUNCIONANDO!")
            emoji_logger.system_info(f"Base URL: {evolution_client.base_url}")
            emoji_logger.system_info(f"Instance: {evolution_client.instance_name}")
            return True
        else:
            emoji_logger.evolution_error("❌ Problemas detectados na conexão")
            emoji_logger.system_info("Verifique:")
            emoji_logger.system_info("1. Se o Evolution API está rodando")
            emoji_logger.system_info("2. Se a URL está correta no .env")
            emoji_logger.system_info("3. Se a API key está válida")
            return False
            
    except Exception as e:
        emoji_logger.evolution_error(f"❌ Erro crítico no teste: {e}")
        logger.exception("Detalhes do erro:")
        return False
    finally:
        # Fecha a conexão
        await evolution_client.close()
        print("\n✅ Conexão fechada\n")

if __name__ == "__main__":
    # Executa o teste
    success = asyncio.run(test_connection())
    
    # Define código de saída
    sys.exit(0 if success else 1)