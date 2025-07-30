#!/usr/bin/env python3
"""
Script para Gerar Token OAuth do Kommo CRM
==========================================
Este script ajuda a obter o token de acesso OAuth2 para o Kommo CRM
"""

import asyncio
import sys
import webbrowser
from urllib.parse import urlencode
from loguru import logger

# Adicionar o diretório raiz ao Python path
sys.path.append('.')

from config.config import get_config
from services.kommo_auth import KommoAuth


async def generate_oauth_url():
    """Gera URL de autorização OAuth2"""
    config = get_config()
    
    # Parâmetros OAuth2
    params = {
        "mode": "popup",
        "client_id": config.kommo.client_id,
        "redirect_uri": config.kommo.redirect_uri,
        "response_type": "code",
        "state": "kommo_oauth"
    }
    
    # URL de autorização
    auth_url = f"https://{config.kommo.subdomain}.kommo.com/oauth?" + urlencode(params)
    
    return auth_url


async def main():
    """Função principal"""
    logger.info("=" * 80)
    logger.info("🔐 GERADOR DE TOKEN OAUTH - KOMMO CRM")
    logger.info("=" * 80)
    
    config = get_config()
    
    # Exibir configurações atuais
    logger.info("\n📋 Configurações atuais:")
    logger.info(f"   Client ID: {config.kommo.client_id}")
    logger.info(f"   Subdomínio: {config.kommo.subdomain}")
    logger.info(f"   Redirect URI: {config.kommo.redirect_uri}")
    
    # Verificar se já existe token
    auth = KommoAuth(config)
    try:
        existing_token = await auth.get_valid_token()
        if existing_token:
            logger.info("\n✅ Já existe um token válido!")
            logger.info(f"   Token: {existing_token[:20]}...")
            
            response = input("\nDeseja gerar um novo token? (s/N): ")
            if response.lower() != 's':
                logger.info("Mantendo token existente.")
                return
    except:
        logger.info("\n⚠️  Nenhum token encontrado. É necessário fazer a autenticação.")
    
    # Gerar URL de autorização
    auth_url = await generate_oauth_url()
    
    logger.info("\n🌐 URL de Autorização OAuth2:")
    logger.info(f"   {auth_url}")
    
    logger.info("\n📝 Instruções:")
    logger.info("1. Abra a URL acima no navegador")
    logger.info("2. Faça login no Kommo CRM com suas credenciais")
    logger.info("3. Autorize o aplicativo")
    logger.info("4. Você será redirecionado para a URL de callback")
    logger.info("5. Copie o código 'code' da URL de callback")
    logger.info("   Exemplo: https://sdr-api.../callback?code=XXXXX&state=kommo_oauth")
    
    # Tentar abrir no navegador
    try:
        webbrowser.open(auth_url)
        logger.info("\n🌐 Abrindo navegador...")
    except:
        logger.info("\n⚠️  Não foi possível abrir o navegador automaticamente.")
    
    # Solicitar código
    logger.info("\n" + "=" * 80)
    code = input("Cole o código de autorização aqui: ").strip()
    
    if not code:
        logger.error("❌ Código não fornecido!")
        return
    
    # Trocar código por token
    logger.info("\n🔄 Trocando código por token de acesso...")
    
    try:
        tokens = await auth.exchange_code_for_token(code)
        
        if tokens:
            logger.info("\n✅ Token obtido com sucesso!")
            logger.info(f"   Access Token: {tokens['access_token'][:20]}...")
            logger.info(f"   Refresh Token: {tokens['refresh_token'][:20]}...")
            logger.info(f"   Expira em: {tokens['expires_in']} segundos")
            
            # Salvar tokens
            await auth._save_tokens(tokens)
            logger.info("\n💾 Tokens salvos no Redis!")
            
            # Testar token
            logger.info("\n🧪 Testando token...")
            test_token = await auth.get_valid_token()
            if test_token:
                logger.info("✅ Token válido e funcionando!")
            else:
                logger.error("❌ Erro ao validar token!")
        else:
            logger.error("❌ Falha ao obter tokens!")
            
    except Exception as e:
        logger.error(f"❌ Erro: {str(e)}")
        logger.info("\n💡 Dica: Verifique se o redirect_uri está correto no .env")
        logger.info("   Para desenvolvimento local, use: http://localhost:8000/auth/kommo/callback")
        logger.info("   Para produção, use a URL real do servidor")
    
    logger.info("\n" + "=" * 80)


if __name__ == "__main__":
    # Configurar logging
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>",
        level="INFO"
    )
    
    asyncio.run(main())