#!/usr/bin/env python3
"""
Script para obter QR Code da Evolution API
"""

import httpx
import asyncio
import os
from dotenv import load_dotenv
# import qrcode  # Não necessário
# import io

load_dotenv()

async def get_qrcode():
    base_url = os.getenv("EVOLUTION_API_URL", "")
    api_key = os.getenv("EVOLUTION_API_KEY", "")
    instance_name = os.getenv("EVOLUTION_INSTANCE_NAME", "Teste-Agente")
    
    if base_url.endswith('/manager'):
        base_url = base_url[:-8]
    
    headers = {
        "apikey": api_key,
        "Content-Type": "application/json"
    }
    
    print(f"📱 Obtendo QR Code para '{instance_name}'...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Tentar diferentes endpoints
            endpoints = [
                f"{base_url}/instance/qrcode/{instance_name}",
                f"{base_url}/instance/qr/{instance_name}",
                f"{base_url}/instance/qrcode/base64/{instance_name}"
            ]
            
            for endpoint in endpoints:
                print(f"\nTentando: {endpoint}")
                try:
                    response = await client.get(endpoint, headers=headers)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Procurar QR code nos dados
                        qr_data = None
                        pairing_code = None
                        
                        if isinstance(data, dict):
                            qr_data = data.get("base64") or data.get("qrcode", {}).get("base64")
                            pairing_code = data.get("pairingCode") or data.get("qrcode", {}).get("pairingCode")
                        
                        if qr_data or pairing_code:
                            print("\n✅ QR Code encontrado!")
                            
                            if pairing_code:
                                print("\n" + "=" * 60)
                                print("🔢 CÓDIGO DE PAREAMENTO (mais fácil!):")
                                print(f"\n   >>> {pairing_code} <<<")
                                print("\nComo usar:")
                                print("1. Abra o WhatsApp no celular")
                                print("2. Vá em Configurações > Dispositivos conectados")
                                print("3. Toque em 'Conectar dispositivo'")
                                print("4. Escolha 'Conectar com número de telefone'")
                                print(f"5. Digite: {pairing_code}")
                                print("=" * 60)
                            
                            if qr_data:
                                print(f"\n📄 QR Code Base64 disponível")
                                print(f"Tamanho: {len(qr_data)} caracteres")
                                
                                # Salvar QR code como arquivo
                                try:
                                    # Remover prefixo data:image se houver
                                    if qr_data.startswith('data:'):
                                        qr_data = qr_data.split(',')[1]
                                    
                                    # Decodificar e salvar
                                    import base64
                                    qr_bytes = base64.b64decode(qr_data)
                                    
                                    filename = f"qrcode_{instance_name}.png"
                                    with open(filename, 'wb') as f:
                                        f.write(qr_bytes)
                                    
                                    print(f"\n💾 QR Code salvo como: {filename}")
                                    print(f"   Abra o arquivo para escanear!")
                                except Exception as e:
                                    print(f"\n⚠️ Não foi possível salvar QR code: {e}")
                            
                            print(f"\n🌐 Ou acesse diretamente:")
                            print(f"   {endpoint}")
                            
                            return True
                        else:
                            print("   ❌ Resposta sem QR code")
                    else:
                        print(f"   ❌ Status: {response.status_code}")
                except Exception as e:
                    print(f"   ❌ Erro: {e}")
            
            # Se não encontrou, tentar restart
            print("\n🔄 Tentando reiniciar instância para gerar novo QR Code...")
            try:
                # Logout primeiro
                logout_response = await client.delete(
                    f"{base_url}/instance/logout/{instance_name}",
                    headers=headers
                )
                print(f"   Logout: {logout_response.status_code}")
                
                await asyncio.sleep(2)
                
                # Conectar novamente
                connect_response = await client.get(
                    f"{base_url}/instance/connect/{instance_name}",
                    headers=headers
                )
                
                if connect_response.status_code == 200:
                    data = connect_response.json()
                    qrcode_data = data.get("qrcode", {})
                    
                    if qrcode_data:
                        pairing_code = qrcode_data.get("pairingCode")
                        if pairing_code:
                            print("\n" + "=" * 60)
                            print("✅ NOVO CÓDIGO DE PAREAMENTO GERADO!")
                            print(f"\n   >>> {pairing_code} <<<")
                            print("\nUse este código no WhatsApp!")
                            print("=" * 60)
                            return True
                
            except Exception as e:
                print(f"   ❌ Erro ao reiniciar: {e}")
            
            print("\n❌ Não foi possível obter QR Code")
            print("\n💡 Sugestões:")
            print("1. Verifique se a instância está criada corretamente")
            print("2. Tente acessar o painel web da Evolution API")
            print("3. Verifique os logs do servidor Evolution API")
            
        except Exception as e:
            print(f"\n❌ Erro geral: {e}")
            return False

if __name__ == "__main__":
    asyncio.run(get_qrcode())