#!/usr/bin/env python3
"""
Teste específico do AGnO Framework Multimodal
=============================================
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.sdr_agent import create_sdr_agent
from agno.media import Image
import base64

async def test_multimodal():
    print("🚀 Testando AGnO Framework Multimodal\n")
    
    # Criar agente
    agent = create_sdr_agent()
    print("✅ Agente SDR criado com sucesso!")
    
    # Teste 1: Simular com dados base64 (imagem pequena de teste)
    print("\n📸 Teste 1: Processamento com base64")
    
    # Base64 de uma imagem 1x1 pixel (apenas para teste)
    test_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    
    try:
        response, metadata = await agent.process_message(
            "Segue a foto da minha conta de luz",
            "+5511999999999",
            media_type="image",
            media_data={"base64": test_base64}
        )
        
        print(f"✅ Resposta do agente: {response[:150]}...")
        print(f"📊 Estágio: {metadata.get('stage')}")
        print(f"💭 Sentimento: {metadata.get('sentiment')}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # Teste 2: Simular com caminho de arquivo
    print("\n\n📁 Teste 2: Processamento com arquivo local")
    
    # Criar um arquivo de teste temporário
    test_image_path = "/tmp/test_conta_luz.jpg"
    
    # Criar uma imagem de teste mínima
    import io
    from PIL import Image as PILImage
    
    # Criar imagem simples
    img = PILImage.new('RGB', (100, 100), color='white')
    img.save(test_image_path, 'JPEG')
    print(f"✅ Arquivo de teste criado: {test_image_path}")
    
    try:
        response2, metadata2 = await agent.process_message(
            "Aqui está minha conta escaneada",
            "+5511999999999",
            media_type="image", 
            media_data={"path": test_image_path}
        )
        
        print(f"✅ Resposta do agente: {response2[:150]}...")
        
        # Verificar se algum dado foi extraído
        if metadata2.get('lead_info', {}).get('bill_value'):
            print("🎉 Dados extraídos com sucesso!")
            print(f"   Valor: {metadata2['lead_info']['bill_value']}")
        else:
            print("ℹ️  Nenhum dado foi extraído (esperado para imagem de teste)")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # Teste 3: Verificar imports AGnO
    print("\n\n🔍 Teste 3: Verificação de Módulos AGnO")
    
    try:
        from agno.media import Image, Audio, Video
        print("✅ Módulos multimodais AGnO importados com sucesso!")
        
        # Criar objeto Image do AGnO
        agno_img = Image(filepath=test_image_path)
        print(f"✅ Objeto Image AGnO criado: {type(agno_img)}")
        
    except Exception as e:
        print(f"❌ Erro ao importar módulos AGnO: {e}")
    
    # Teste 4: Verificar suporte a PDF
    print("\n\n📄 Teste 4: Verificação de Suporte a PDF")
    
    try:
        from agno.document_reader import PDFReader, PDFImageReader
        print("✅ Módulos PDFReader e PDFImageReader disponíveis!")
        
        # Criar um PDF de teste simples
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        
        test_pdf_path = "/tmp/test_conta_luz.pdf"
        
        # Criar PDF com texto simulando conta de luz
        c = canvas.Canvas(test_pdf_path, pagesize=A4)
        c.drawString(100, 750, "CONTA DE ENERGIA ELÉTRICA")
        c.drawString(100, 700, "Cliente: João Silva")
        c.drawString(100, 650, "CPF: 123.456.789-00")
        c.drawString(100, 600, "Endereço: Rua das Flores, 123")
        c.drawString(100, 550, "Valor Total: R$ 450,00")
        c.drawString(100, 500, "Consumo: 350 kWh")
        c.drawString(100, 450, "Referência: 11/2024")
        c.drawString(100, 400, "Distribuidora: CELPE")
        c.save()
        
        print(f"✅ PDF de teste criado: {test_pdf_path}")
        
        # Testar processamento de PDF
        response3, metadata3 = await agent.process_message(
            "Aqui está minha conta em PDF",
            "+5511999999999",
            media_type="document",
            media_data={"path": test_pdf_path, "mime_type": "application/pdf"}
        )
        
        print(f"✅ Resposta do agente: {response3[:150]}...")
        
        # Verificar se dados foram extraídos
        if metadata3.get('lead_info', {}).get('bill_value'):
            print("🎉 Dados extraídos do PDF com sucesso!")
            print(f"   Valor: {metadata3['lead_info']['bill_value']}")
            print(f"   Consumo: {metadata3['lead_info'].get('consumption_kwh')}")
        else:
            print("ℹ️  Processamento de PDF retornou ao fallback de imagem")
        
        # Limpar arquivo de teste
        if os.path.exists(test_pdf_path):
            os.remove(test_pdf_path)
            print("🧹 PDF de teste removido")
            
    except ImportError as e:
        print(f"⚠️  Módulos PDF do AGnO não disponíveis: {e}")
        print("   PDFs serão processados como imagens (fallback)")
    except Exception as e:
        print(f"❌ Erro ao testar suporte a PDF: {e}")
    
    # Limpar arquivo de teste de imagem
    import os
    if os.path.exists(test_image_path):
        os.remove(test_image_path)
        print("\n🧹 Arquivo de teste de imagem removido")
    
    print("\n✅ Todos os testes concluídos!")

if __name__ == "__main__":
    # Verificar se PIL está instalado
    try:
        from PIL import Image as PILImage
    except ImportError:
        print("❌ Pillow não está instalado. Instalando...")
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "Pillow"])
        print("✅ Pillow instalado!")
    
    # Verificar se reportlab está instalado (para criar PDFs de teste)
    try:
        import reportlab
    except ImportError:
        print("❌ ReportLab não está instalado. Instalando...")
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "reportlab"])
        print("✅ ReportLab instalado!")
    
    asyncio.run(test_multimodal())