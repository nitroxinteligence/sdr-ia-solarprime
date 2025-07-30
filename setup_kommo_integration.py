#!/usr/bin/env python3
"""
Script de Configuração Automática - Kommo CRM
=============================================
Configura a integração com Kommo de forma simples e rápida
"""

import asyncio
import sys
import os
from loguru import logger
from dotenv import load_dotenv, set_key

# Adicionar o diretório raiz ao Python path
sys.path.append('.')

from services.kommo_auth_simple import KommoAuthSimple
from services.kommo_service_updated import KommoServiceSimple
from config.config import get_config


class KommoSetup:
    """Assistente de configuração do Kommo"""
    
    def __init__(self):
        self.config = get_config()
        self.env_file = ".env"
        
    async def run(self):
        """Executa o assistente de configuração"""
        logger.info("=" * 80)
        logger.info("🚀 ASSISTENTE DE CONFIGURAÇÃO - KOMMO CRM")
        logger.info("=" * 80)
        
        # Verificar se já existe token
        existing_token = os.getenv("KOMMO_LONG_LIVED_TOKEN")
        
        if existing_token:
            logger.info("✅ Long-Lived Token já configurado!")
            test = input("\nDeseja testar o token existente? (S/n): ")
            
            if test.lower() != 'n':
                await self.test_existing_token(existing_token)
                
            replace = input("\nDeseja substituir o token? (s/N): ")
            if replace.lower() != 's':
                await self.configure_integration()
                return
        
        # Instruções para obter token
        await self.show_instructions()
        
        # Solicitar token
        token = input("\nCole seu Long-Lived Token aqui: ").strip()
        
        if not token:
            logger.error("❌ Token não fornecido!")
            return
        
        # Testar token
        if await self.test_token(token):
            # Salvar no .env
            await self.save_token(token)
            
            # Configurar integração
            await self.configure_integration()
        else:
            logger.error("❌ Token inválido! Verifique e tente novamente.")
    
    async def show_instructions(self):
        """Mostra instruções para obter o token"""
        logger.info("\n📋 COMO OBTER SEU LONG-LIVED TOKEN:")
        logger.info("=" * 50)
        logger.info("1. Acesse: https://leonardofvieira00.kommo.com/")
        logger.info("2. Vá em: Configurações → Integrações")
        logger.info("3. Clique em: + Criar Integração")
        logger.info("4. Escolha: Privada")
        logger.info("5. Preencha:")
        logger.info("   - Nome: SDR IA SolarPrime")
        logger.info("   - Descrição: Integração WhatsApp AI")
        logger.info("   - NÃO preencha Redirect URL")
        logger.info("6. Salve a integração")
        logger.info("7. Abra a aba: Chaves e escopos")
        logger.info("8. Clique em: Gerar token de longa duração")
        logger.info("9. Escolha: 5 anos de validade")
        logger.info("10. Copie o token gerado")
        logger.info("=" * 50)
    
    async def test_token(self, token: str) -> bool:
        """Testa se o token é válido"""
        try:
            auth = KommoAuthSimple(self.config)
            await auth.set_token(token)
            return await auth.test_token()
        except Exception as e:
            logger.error(f"Erro ao testar token: {str(e)}")
            return False
    
    async def test_existing_token(self, token: str):
        """Testa token existente"""
        logger.info("\n🧪 Testando token...")
        await self.test_token(token)
    
    async def save_token(self, token: str):
        """Salva token no arquivo .env"""
        try:
            set_key(self.env_file, "KOMMO_LONG_LIVED_TOKEN", token)
            logger.info("✅ Token salvo no arquivo .env!")
            
            # Recarregar variáveis
            load_dotenv(override=True)
            
        except Exception as e:
            logger.error(f"Erro ao salvar token: {str(e)}")
    
    async def configure_integration(self):
        """Configura a integração detectando IDs automaticamente"""
        logger.info("\n🔧 CONFIGURANDO INTEGRAÇÃO...")
        
        service = KommoServiceSimple()
        
        # 1. Testar conexão
        logger.info("\n1️⃣ Testando conexão...")
        try:
            account = await service.test_connection()
            logger.info(f"   Conta: {account.get('name')}")
            logger.info(f"   ID: {account.get('id')}")
        except Exception as e:
            logger.error(f"❌ Falha na conexão: {str(e)}")
            return
        
        # 2. Detectar pipelines
        logger.info("\n2️⃣ Detectando pipelines...")
        try:
            pipelines = await service.get_pipelines()
            
            if pipelines:
                logger.info(f"   Encontrados {len(pipelines)} pipelines")
                
                # Se já tem pipeline configurado, mostrar
                current_id = self.config.kommo.pipeline_id
                if current_id:
                    logger.info(f"   Pipeline atual: {current_id}")
                
                # Listar pipelines
                for i, pipeline in enumerate(pipelines):
                    status = "✅" if pipeline.get("is_main") else ""
                    logger.info(f"   {i+1}. {pipeline['name']} (ID: {pipeline['id']}) {status}")
                
                # Selecionar pipeline
                if len(pipelines) == 1:
                    selected = pipelines[0]
                    logger.info(f"   Usando pipeline único: {selected['name']}")
                else:
                    choice = input("\nEscolha o pipeline (número): ")
                    try:
                        selected = pipelines[int(choice) - 1]
                    except:
                        selected = pipelines[0]
                        logger.info(f"   Usando pipeline principal: {selected['name']}")
                
                # Salvar no .env
                set_key(self.env_file, "KOMMO_PIPELINE_ID", str(selected['id']))
                logger.info(f"✅ Pipeline configurado: {selected['name']}")
                
        except Exception as e:
            logger.error(f"❌ Erro ao detectar pipelines: {str(e)}")
        
        # 3. Criar lead de teste
        logger.info("\n3️⃣ Criar lead de teste?")
        create_test = input("   Criar lead de teste? (s/N): ")
        
        if create_test.lower() == 's':
            try:
                test_lead = await service.create_lead({
                    "name": "Teste SDR IA - Pode Deletar",
                    "whatsapp": "+5511999999999",
                    "price": 1000
                })
                
                if test_lead:
                    logger.info(f"✅ Lead de teste criado! ID: {test_lead['id']}")
                    logger.info("   Você pode deletá-lo no Kommo após verificar")
                    
            except Exception as e:
                logger.error(f"❌ Erro ao criar lead: {str(e)}")
        
        # Resumo final
        logger.info("\n" + "=" * 80)
        logger.info("✅ CONFIGURAÇÃO CONCLUÍDA!")
        logger.info("=" * 80)
        logger.info("\n📋 Próximos passos:")
        logger.info("1. Execute os testes: python test_kommo_simple.py")
        logger.info("2. O sistema já está pronto para usar!")
        logger.info("3. Não é necessário renovar o token por 5 anos")
        logger.info("\n💡 Dica: Para trocar o token, execute este script novamente")


async def main():
    """Função principal"""
    # Configurar logging
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>",
        level="INFO"
    )
    
    # Carregar .env
    load_dotenv()
    
    # Executar setup
    setup = KommoSetup()
    await setup.run()


if __name__ == "__main__":
    asyncio.run(main())