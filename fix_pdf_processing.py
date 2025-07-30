#!/usr/bin/env python3
"""
Fix PDF Processing Issue
========================
Correção para o problema de processamento de PDF
"""

import os

def fix_pdf_processing():
    """Aplica correção no processamento de PDF"""
    
    file_path = "agents/sdr_agent.py"
    
    # Ler o arquivo
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Correção 1: Adicionar verificação se o arquivo existe
    old_code1 = """                if 'path' in pdf_data:
                    logger.info(f"📂 Processando PDF do caminho: {pdf_data['path']}")
                    with open(pdf_data['path'], 'rb') as f:
                        pdf_content = f.read()"""
    
    new_code1 = """                if 'path' in pdf_data:
                    logger.info(f"📂 Processando PDF do caminho: {pdf_data['path']}")
                    if os.path.exists(pdf_data['path']):
                        with open(pdf_data['path'], 'rb') as f:
                            pdf_content = f.read()
                        logger.info(f"✅ PDF lido com sucesso: {len(pdf_content)} bytes")
                    else:
                        logger.error(f"❌ Arquivo PDF não encontrado: {pdf_data['path']}")"""
    
    # Correção 2: Log mais detalhado dos dados recebidos
    old_code2 = """    async def _process_pdf_with_ocr(self, pdf_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Processa PDF usando capacidades nativas do Gemini 2.5 Pro"""
        try:
            logger.info("📄 Processamento de PDF iniciado - usando Gemini 2.5 Pro nativo")"""
    
    new_code2 = """    async def _process_pdf_with_ocr(self, pdf_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Processa PDF usando capacidades nativas do Gemini 2.5 Pro"""
        try:
            logger.info("📄 Processamento de PDF iniciado - usando Gemini 2.5 Pro nativo")
            logger.debug(f"🔍 Dados recebidos para processamento: {list(pdf_data.keys())}")"""
    
    # Aplicar correções
    content = content.replace(old_code1, new_code1)
    content = content.replace(old_code2, new_code2)
    
    # Salvar arquivo
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Correções aplicadas com sucesso!")
    print("\nPróximos passos:")
    print("1. Reinicie o servidor")
    print("2. Teste enviando um PDF novamente")
    print("3. Verifique os logs para mais detalhes")

if __name__ == "__main__":
    fix_pdf_processing()