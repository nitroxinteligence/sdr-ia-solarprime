#!/usr/bin/env python3
"""
Teste dos Logs Aprimorados do Sistema Multimodal
Valida se os logs detalhados estão funcionando corretamente
"""

import asyncio
import base64
from pathlib import Path
from datetime import datetime
from io import BytesIO
from PIL import Image

# Configurar ambiente
from dotenv import load_dotenv
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(env_path)

from app.agents.agentic_sdr import AgenticSDR
from app.utils.logger import emoji_logger


async def test_image_logs():
    """Testa logs de processamento de imagem"""
    print("\n" + "="*60)
    print("TESTE 1: LOGS DE PROCESSAMENTO DE IMAGEM")
    print("="*60)
    
    sdr = AgenticSDR()
    
    # Criar uma imagem pequena de teste
    img = Image.new('RGB', (200, 200), color='blue')
    buffer = BytesIO()
    img.save(buffer, format='JPEG')
    image_bytes = buffer.getvalue()
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
    
    print(f"Criada imagem de teste: {len(image_bytes)} bytes")
    print("Processando...\n")
    
    result = await sdr.process_multimodal_content(
        media_type="image",
        media_data=image_base64,
        caption="Imagem azul de teste para validar logs"
    )
    
    print(f"\nResultado: {result.get('status', 'unknown')}")
    if 'processing_time' in result:
        print(f"Tempo de processamento: {result['processing_time']:.2f}s")
    
    return result


async def test_pdf_logs():
    """Testa logs de processamento de PDF"""
    print("\n" + "="*60)
    print("TESTE 2: LOGS DE PROCESSAMENTO DE PDF")
    print("="*60)
    
    sdr = AgenticSDR()
    
    # PDF mínimo
    pdf_content = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>
endobj
4 0 obj
<< /Length 50 >>
stream
BT
/F1 12 Tf
100 700 Td
(Teste de PDF) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000203 00000 n
trailer
<< /Size 5 /Root 1 0 R >>
startxref
303
%%EOF"""
    
    pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')
    
    print(f"Criado PDF de teste: {len(pdf_content)} bytes")
    print("Processando...\n")
    
    result = await sdr.process_multimodal_content(
        media_type="pdf",
        media_data=pdf_base64,
        caption="PDF de teste"
    )
    
    print(f"\nResultado: {result.get('status', 'unknown')}")
    if 'processing_time' in result:
        print(f"Tempo de processamento: {result['processing_time']:.2f}s")
    
    return result


async def test_audio_logs():
    """Testa logs de processamento de áudio"""
    print("\n" + "="*60)
    print("TESTE 3: LOGS DE PROCESSAMENTO DE ÁUDIO")
    print("="*60)
    
    sdr = AgenticSDR()
    
    # WAV header mínimo (áudio vazio)
    wav_header = b'RIFF' + b'\x24\x00\x00\x00' + b'WAVE'
    wav_header += b'fmt ' + b'\x10\x00\x00\x00'
    wav_header += b'\x01\x00'  # PCM
    wav_header += b'\x01\x00'  # 1 canal
    wav_header += b'\x44\xAC\x00\x00'  # 44100 Hz
    wav_header += b'\x88\x58\x01\x00'
    wav_header += b'\x02\x00'
    wav_header += b'\x10\x00'
    wav_header += b'data' + b'\x00\x00\x00\x00'
    
    audio_base64 = base64.b64encode(wav_header).decode('utf-8')
    
    print(f"Criado áudio de teste: {len(wav_header)} bytes")
    print("Processando...\n")
    
    result = await sdr.process_multimodal_content(
        media_type="audio",
        media_data=audio_base64,
        caption="Áudio de teste"
    )
    
    print(f"\nResultado: {result.get('status', 'unknown')}")
    if 'processing_time' in result:
        print(f"Tempo de processamento: {result['processing_time']:.2f}s")
    
    return result


async def test_error_logs():
    """Testa logs de erro"""
    print("\n" + "="*60)
    print("TESTE 4: LOGS DE ERRO (TIPO INVÁLIDO)")
    print("="*60)
    
    sdr = AgenticSDR()
    
    print("Tentando processar tipo inválido 'xyz'...\n")
    
    result = await sdr.process_multimodal_content(
        media_type="xyz",
        media_data="dados_invalidos",
        caption="Teste de erro"
    )
    
    print(f"\nResultado: {result.get('status', 'unknown')}")
    print(f"Erro: {result.get('error', 'N/A')}")
    
    return result


async def main():
    """Executa todos os testes de logs"""
    print("\n" + "🚀" * 30)
    print("TESTE DO SISTEMA DE LOGS APRIMORADOS")
    print("🚀" * 30)
    print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    
    # Executar testes
    print("\n📊 Executando bateria de testes...\n")
    
    try:
        results['image'] = await test_image_logs()
    except Exception as e:
        print(f"❌ Erro no teste de imagem: {e}")
        results['image'] = {'status': 'error', 'error': str(e)}
    
    try:
        results['pdf'] = await test_pdf_logs()
    except Exception as e:
        print(f"❌ Erro no teste de PDF: {e}")
        results['pdf'] = {'status': 'error', 'error': str(e)}
    
    try:
        results['audio'] = await test_audio_logs()
    except Exception as e:
        print(f"❌ Erro no teste de áudio: {e}")
        results['audio'] = {'status': 'error', 'error': str(e)}
    
    try:
        results['error'] = await test_error_logs()
    except Exception as e:
        print(f"❌ Erro no teste de erro: {e}")
        results['error'] = {'status': 'error', 'error': str(e)}
    
    # Resumo final
    print("\n" + "="*60)
    print("📊 RESUMO DOS TESTES DE LOGS")
    print("="*60)
    
    for test_name, result in results.items():
        status = result.get('status', 'unknown')
        icon = "✅" if status in ['success', 'processed'] else "❌"
        print(f"{icon} {test_name.upper()}: {status}")
    
    print("\n" + "="*60)
    print("✅ TESTE DE LOGS CONCLUÍDO!")
    print("="*60)
    print("\nVerifique o console acima para ver os logs detalhados.")
    print("Os logs devem mostrar:")
    print("  • Etapas numeradas do processamento")
    print("  • Métricas de tamanho e tempo")
    print("  • Detecção de formato")
    print("  • Fallbacks quando necessário")
    print("  • Mensagens de erro detalhadas")
    
    return results


if __name__ == "__main__":
    asyncio.run(main())