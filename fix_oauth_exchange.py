#!/usr/bin/env python3
"""
Script Corrigido para Trocar Código OAuth
=========================================
"""

import asyncio
import sys
import httpx
from loguru import logger

# Adicionar o diretório raiz ao Python path
sys.path.append('.')

from config.config import get_config


async def exchange_code_with_different_endpoint():
    """Tenta trocar código usando diferentes endpoints possíveis"""
    
    config = get_config()
    
    # Código OAuth
    code = "def5020033f9a17a381668925f153cc4e1ddac39f5bbd3be290307536a0c369b87d616091009a8f172b78d4dcce100540fd2bcd5ded9da60e09190b6acdbc07b8a06ec132aa6b49ad35e272f9a4edcea6f6c0b543479f7091cb05362f288eca74b2025bb3bf9e6191bb7737050ba5ae345e2de6a0880241ca18e36007a79fd428247f1a4b2029893beff9bb36611243d671853b9edf70a48988d38884957cee3bde6eac815b7711490ed78609ccaf152d686fd327b598ebb9ceeda658b19b42d75ba41e8e9f01d4cd95d6e458d7a540d08dc16991b01438f6577dd2dca10869e58470df464a9709313e873a041495eade5d3851c7e6017f0c4e3d0d4b2caf7dc99b347fd401fb1bc0870f1d82a8dfb1578a96d26a33db66fd27f455573d24b6831c36ee3d40b952dfa066301bc5d21a9e4cea150b1474c6390bbaaeaab40969eea7c06ccd4b27ba91508c0aa1e8bf169663e619532ff9c3bd3f9468ed987571ca67db5584ba9e687b70a10e76a090ec891d5754f8933cffaa07c19ee914167ff17dfd259a0eabc6c7a762e4e024e3ff4201a57c6b07bf3c4bd0eaf5cd12a0612301d59a6e448c71f2a3f1848884ec2206561f8a66ece0bd483e80d18d6191aba1c6a27944431177ed859213d6734e7f662fd249d6e9f43dd34836036719cb20d56fa53865faa015efbd0a88022bf569e93f16694950b22bf8dd751eaf792ffafab175088edd3a64486d4ff6299908cc70154c35efbaeea8ed6fe89"
    
    # Dados para troca
    data = {
        "client_id": config.kommo.client_id,
        "client_secret": config.kommo.client_secret,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": config.kommo.redirect_uri
    }
    
    # Diferentes endpoints possíveis
    endpoints = [
        f"https://{config.kommo.subdomain}.kommo.com/oauth/token",
        f"https://{config.kommo.subdomain}.kommo.com/api/oauth/access_token",
        f"https://{config.kommo.subdomain}.kommo.com/api/v4/oauth/access_token",
        f"https://www.kommo.com/oauth/token"
    ]
    
    logger.info("🔄 Tentando trocar código OAuth em diferentes endpoints...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for endpoint in endpoints:
            logger.info(f"\n📡 Tentando: {endpoint}")
            
            try:
                # Tentar POST com JSON
                response = await client.post(endpoint, json=data)
                logger.info(f"   Status (JSON): {response.status_code}")
                
                if response.status_code == 200:
                    logger.info("✅ Sucesso com JSON!")
                    tokens = response.json()
                    logger.info(f"   Access Token: {tokens.get('access_token', '')[:30]}...")
                    return tokens
                elif response.status_code != 404:
                    logger.info(f"   Resposta: {response.text[:200]}...")
                
                # Tentar POST com form data
                response = await client.post(endpoint, data=data)
                logger.info(f"   Status (Form): {response.status_code}")
                
                if response.status_code == 200:
                    logger.info("✅ Sucesso com Form Data!")
                    tokens = response.json()
                    logger.info(f"   Access Token: {tokens.get('access_token', '')[:30]}...")
                    return tokens
                elif response.status_code != 404:
                    logger.info(f"   Resposta: {response.text[:200]}...")
                    
            except Exception as e:
                logger.error(f"   Erro: {str(e)}")
    
    logger.error("\n❌ Nenhum endpoint funcionou!")
    logger.info("\n💡 Sugestão: Use a interface do Kommo para criar uma integração privada")
    logger.info("   Acesse: https://leonardofvieira00.kommo.com/settings/integrations/")


async def main():
    await exchange_code_with_different_endpoint()


if __name__ == "__main__":
    # Configurar logging
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>",
        level="INFO"
    )
    
    asyncio.run(main())