#!/usr/bin/env python3
"""
Script para Inserir Tokens do Kommo Manualmente
===============================================
Use este script se você já tem os tokens de acesso do Kommo
"""

import asyncio
import sys
import json
from datetime import datetime, timedelta
from loguru import logger

# Adicionar o diretório raiz ao Python path
sys.path.append('.')

from utils.cache import redis_client
from config.config import get_config
from services.kommo_auth import KommoAuth


async def insert_tokens_manually():
    """Permite inserir tokens manualmente no Redis"""
    logger.info("=" * 80)
    logger.info("📝 INSERÇÃO MANUAL DE TOKENS - KOMMO CRM")
    logger.info("=" * 80)
    
    logger.info("\n⚠️  Use este script se você já tem os tokens do Kommo")
    logger.info("   Por exemplo, tokens obtidos via Postman ou outra ferramenta")
    
    # Solicitar tokens
    logger.info("\n" + "=" * 80)
    access_token = input("Cole o ACCESS TOKEN aqui: ").strip()
    
    if not access_token:
        logger.error("❌ Access token não fornecido!")
        return
    
    refresh_token = input("\nCole o REFRESH TOKEN aqui (ou deixe vazio se não tiver): ").strip()
    
    # Calcular expiração (86400 segundos = 24 horas por padrão)
    expires_in = 86400
    expires_at = datetime.now() + timedelta(seconds=expires_in)
    
    # Criar estrutura de tokens
    tokens = {
        "access_token": access_token,
        "refresh_token": refresh_token or access_token,  # Usa o mesmo se não tiver refresh
        "token_type": "Bearer",
        "expires_in": expires_in,
        "expires_at": expires_at.isoformat()
    }
    
    try:
        # Salvar no Redis
        TOKEN_CACHE_KEY = "kommo:tokens"
        redis_client.set(TOKEN_CACHE_KEY, json.dumps(tokens))
        
        logger.info("\n✅ Tokens salvos com sucesso!")
        logger.info(f"   Access Token: {access_token[:30]}...")
        if refresh_token:
            logger.info(f"   Refresh Token: {refresh_token[:30]}...")
        logger.info(f"   Expira em: {expires_at.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Testar token
        logger.info("\n🧪 Testando token...")
        config = get_config()
        auth = KommoAuth(config)
        
        test_token = await auth.get_valid_token()
        if test_token:
            logger.info("✅ Token válido e funcionando!")
            logger.info("\n🎉 Agora você pode executar os testes!")
            logger.info("   python test_kommo_integration.py")
        else:
            logger.error("❌ Erro ao validar token!")
            
    except Exception as e:
        logger.error(f"❌ Erro ao salvar tokens: {str(e)}")


async def test_direct_api_call():
    """Testa chamada direta à API do Kommo com token"""
    logger.info("\n" + "=" * 80)
    logger.info("🧪 TESTE DIRETO DA API KOMMO")
    logger.info("=" * 80)
    
    config = get_config()
    
    # Solicitar token para teste
    access_token = input("\nCole o ACCESS TOKEN para teste direto: ").strip()
    
    if not access_token:
        logger.error("❌ Token não fornecido!")
        return
    
    import httpx
    
    try:
        # Testar endpoint de account (informações da conta)
        url = f"https://{config.kommo.subdomain}.kommo.com/api/v4/account"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        logger.info(f"\n📡 Testando: GET {url}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers)
            
            logger.info(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                logger.info("✅ API respondeu com sucesso!")
                logger.info(f"   Nome da conta: {data.get('name', 'N/A')}")
                logger.info(f"   ID da conta: {data.get('id', 'N/A')}")
                logger.info(f"   Subdomínio: {data.get('subdomain', 'N/A')}")
                
                # Se funcionou, salvar o token
                response_save = input("\n💾 Deseja salvar este token? (s/N): ")
                if response_save.lower() == 's':
                    await insert_tokens_manually()
            else:
                logger.error(f"❌ Erro na API: {response.text}")
                
    except Exception as e:
        logger.error(f"❌ Erro no teste: {str(e)}")


async def main():
    """Menu principal"""
    logger.info("Escolha uma opção:")
    logger.info("1. Inserir tokens manualmente")
    logger.info("2. Testar chamada direta à API")
    logger.info("3. Sair")
    
    choice = input("\nOpção (1-3): ").strip()
    
    if choice == "1":
        await insert_tokens_manually()
    elif choice == "2":
        await test_direct_api_call()
    else:
        logger.info("Saindo...")


if __name__ == "__main__":
    # Configurar logging
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>",
        level="INFO"
    )
    
    asyncio.run(main())