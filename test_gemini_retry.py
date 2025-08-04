#!/usr/bin/env python3
"""
Script de teste para verificar o sistema de retry com Gemini
"""

import asyncio
import os
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from app.utils.retry_handler import async_retry, GEMINI_RETRY_CONFIG
from app.utils.logger import emoji_logger
from app.config import settings
from agno.models.google import Gemini


class GeminiRetryTest:
    """Classe de teste para o sistema de retry"""
    
    def __init__(self):
        try:
            self.model = Gemini(
                id="gemini-2.5-flash",
                api_key=settings.google_api_key
            )
            emoji_logger.system_ready("Teste Retry", model="gemini-2.5-flash")
        except Exception as e:
            emoji_logger.system_error(f"Erro ao inicializar Gemini: {e}")
            self.model = None
    
    @async_retry(GEMINI_RETRY_CONFIG)
    async def test_call_with_retry(self, prompt: str):
        """Testa chamada com retry automático"""
        if not self.model:
            raise Exception("Modelo não disponível")
        
        response = self.model.invoke(prompt)
        return response
    
    async def run_test(self):
        """Executa teste completo"""
        emoji_logger.system_info("🧪 Iniciando teste do sistema de retry...")
        
        # Teste 1: Chamada simples
        try:
            emoji_logger.system_info("📝 Teste 1: Chamada simples com retry")
            response = await self.test_call_with_retry(
                "Responda apenas 'OK' se você está funcionando"
            )
            emoji_logger.system_ready(f"✅ Resposta recebida: {response[:100]}")
        except Exception as e:
            emoji_logger.system_error("Teste 1 falhou", error=str(e))
        
        # Teste 2: Simular erro forçando prompt muito grande
        try:
            emoji_logger.system_info("📝 Teste 2: Testando com prompt grande")
            large_prompt = "Teste " * 10000  # Prompt muito grande
            response = await self.test_call_with_retry(large_prompt[:8000])
            emoji_logger.system_ready(f"✅ Teste 2 passou: {response[:100]}")
        except Exception as e:
            emoji_logger.system_warning(f"⚠️ Teste 2 falhou (esperado): {e}")
        
        # Teste 3: Múltiplas chamadas paralelas
        try:
            emoji_logger.system_info("📝 Teste 3: Múltiplas chamadas paralelas")
            prompts = [
                "Diga 'Teste 1 OK'",
                "Diga 'Teste 2 OK'",
                "Diga 'Teste 3 OK'"
            ]
            
            tasks = [self.test_call_with_retry(p) for p in prompts]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    emoji_logger.system_warning(f"⚠️ Chamada {i+1} falhou: {result}")
                else:
                    emoji_logger.system_ready(f"✅ Chamada {i+1}: {result[:50]}")
        
        except Exception as e:
            emoji_logger.system_error("Teste 3 falhou", error=str(e))
        
        emoji_logger.system_info("🏁 Teste concluído!")


async def main():
    """Função principal"""
    tester = GeminiRetryTest()
    await tester.run_test()


if __name__ == "__main__":
    asyncio.run(main())