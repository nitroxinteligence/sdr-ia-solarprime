#!/usr/bin/env python3
"""
🔥 DIAGNÓSTICO E CORREÇÃO DEFINITIVA DO KOMMO
Estamos em 4 de agosto de 2025
"""
import requests
import aiohttp
import asyncio
import json
import base64
import time
import os
from datetime import datetime
from dotenv import load_dotenv, set_key
from pathlib import Path

# Carregar .env
load_dotenv()

class KommoDiagnostic:
    """Diagnóstico completo e correção automática"""
    
    def __init__(self):
        self.token = os.getenv('KOMMO_LONG_LIVED_TOKEN')
        self.subdomain = os.getenv('KOMMO_SUBDOMAIN', 'leonardofvieira00')
        self.client_id = os.getenv('KOMMO_CLIENT_ID')
        self.client_secret = os.getenv('KOMMO_CLIENT_SECRET')
        self.base_url = os.getenv('KOMMO_BASE_URL')
        self.env_path = Path('.env')
        
    def analyze_token(self):
        """Análise detalhada do token JWT"""
        print("\n" + "="*70)
        print("🔍 ANÁLISE DO TOKEN JWT")
        print("="*70)
        
        if not self.token:
            print("❌ Token não encontrado no .env!")
            return False
            
        print(f"📊 Token Info:")
        print(f"   Tamanho: {len(self.token)} caracteres")
        print(f"   Início: {self.token[:30]}...")
        
        try:
            # Decodificar JWT
            parts = self.token.split('.')
            if len(parts) != 3:
                print("❌ Token mal formatado - deve ter 3 partes separadas por '.'")
                return False
                
            # Decodificar payload
            payload = parts[1]
            padding = 4 - len(payload) % 4
            if padding != 4:
                payload += '=' * padding
            
            decoded = base64.urlsafe_b64decode(payload)
            token_data = json.loads(decoded)
            
            print(f"\n📋 Dados Decodificados:")
            print(f"   Client ID: {token_data.get('aud')}")
            print(f"   Account ID: {token_data.get('account_id')}")
            print(f"   User ID: {token_data.get('sub')}")
            print(f"   API Domain: {token_data.get('api_domain')}")
            print(f"   Base Domain: {token_data.get('base_domain')}")
            print(f"   Subdomain Hash: {token_data.get('hash_uuid')}")
            print(f"   Escopos: {', '.join(token_data.get('scopes', []))}")
            
            # Verificar validade
            iat = token_data.get('iat', 0)
            exp = token_data.get('exp', 0)
            current_time = int(time.time())
            
            print(f"\n📅 Validade:")
            print(f"   Emitido: {datetime.fromtimestamp(iat).strftime('%d/%m/%Y %H:%M:%S')}")
            print(f"   Expira: {datetime.fromtimestamp(exp).strftime('%d/%m/%Y %H:%M:%S')}")
            print(f"   Status: {'✅ Válido' if current_time < exp else '❌ Expirado'}")
            
            # Guardar account_id para uso posterior
            self.account_id = token_data.get('account_id')
            self.api_domain = token_data.get('api_domain', 'api-c.kommo.com')
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao decodificar token: {e}")
            return False
    
    def test_all_endpoints(self):
        """Testa todos os endpoints possíveis"""
        print("\n" + "="*70)
        print("🌐 TESTANDO TODOS OS ENDPOINTS POSSÍVEIS")
        print("="*70)
        
        # Headers com diferentes formatos
        headers_variations = [
            {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            },
            {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
                "User-Agent": "SDR-IA-SolarPrime/1.0"
            },
            {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
        ]
        
        # URLs para testar
        urls_to_test = [
            # Usando subdomain direto
            f"https://{self.subdomain}.kommo.com/api/v4/account",
            f"https://{self.subdomain}.amocrm.com/api/v4/account",
            
            # Usando API domains regionais
            f"https://api-a.kommo.com/api/v4/account",
            f"https://api-b.kommo.com/api/v4/account",
            f"https://api-c.kommo.com/api/v4/account",
            f"https://api-d.kommo.com/api/v4/account",
            f"https://api-e.kommo.com/api/v4/account",
            
            # Usando domain do token (se disponível)
            f"https://{getattr(self, 'api_domain', 'api-c.kommo.com')}/api/v4/account" if hasattr(self, 'api_domain') else None
        ]
        
        # Remover None da lista
        urls_to_test = [url for url in urls_to_test if url]
        
        for headers_idx, headers in enumerate(headers_variations, 1):
            print(f"\n📝 Testando com Headers Variação #{headers_idx}")
            
            for url in urls_to_test:
                print(f"\n   🔗 URL: {url}")
                
                try:
                    response = requests.get(url, headers=headers, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        print(f"   ✅ SUCESSO! Status: {response.status_code}")
                        print(f"   📊 Conta: {data.get('name')}")
                        print(f"   🆔 ID: {data.get('id')}")
                        print(f"   🌍 País: {data.get('country')}")
                        print(f"\n   🎯 URL FUNCIONANDO: {url}")
                        print(f"   🎯 HEADERS FUNCIONANDO: Variação #{headers_idx}")
                        
                        # Salvar configuração funcional
                        self.working_url = url.split('/api/v4')[0]
                        self.working_headers = headers
                        return True
                        
                    elif response.status_code == 401:
                        error_detail = response.json() if response.text else {}
                        print(f"   ❌ 401 - {error_detail.get('detail', 'Unauthorized')}")
                        
                    else:
                        print(f"   ⚠️ Status: {response.status_code}")
                        
                except requests.exceptions.Timeout:
                    print(f"   ⏱️ Timeout")
                except Exception as e:
                    print(f"   ❌ Erro: {str(e)[:50]}")
        
        return False
    
    async def test_async_connection(self):
        """Testa conexão assíncrona (como o código usa)"""
        print("\n" + "="*70)
        print("⚡ TESTANDO CONEXÃO ASSÍNCRONA")
        print("="*70)
        
        if not hasattr(self, 'working_url'):
            # Usar URLs padrão
            test_urls = [
                f"https://{self.subdomain}.kommo.com",
                f"https://api-c.kommo.com"
            ]
        else:
            test_urls = [self.working_url]
        
        headers = getattr(self, 'working_headers', {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        })
        
        async with aiohttp.ClientSession() as session:
            for base_url in test_urls:
                url = f"{base_url}/api/v4/account"
                print(f"\n📡 Testando: {url}")
                
                try:
                    async with session.get(url, headers=headers) as response:
                        if response.status == 200:
                            data = await response.json()
                            print(f"✅ Conexão assíncrona funcionando!")
                            print(f"   Conta: {data.get('name')}")
                            self.async_working = True
                            self.final_url = base_url
                            return True
                        else:
                            text = await response.text()
                            print(f"❌ Status: {response.status} - {text[:100]}")
                            
                except Exception as e:
                    print(f"❌ Erro assíncrono: {e}")
        
        return False
    
    def fix_env_file(self):
        """Corrige o arquivo .env automaticamente"""
        print("\n" + "="*70)
        print("🔧 APLICANDO CORREÇÕES NO .ENV")
        print("="*70)
        
        if hasattr(self, 'final_url'):
            print(f"\n✅ Atualizando KOMMO_BASE_URL para: {self.final_url}")
            set_key(self.env_path, "KOMMO_BASE_URL", self.final_url)
            
            # Se descobrimos que é um subdomínio diferente
            if self.final_url.startswith(f"https://{self.subdomain}"):
                print("✅ URL usa subdomain direto - configuração correta")
            else:
                print(f"⚠️ URL usa servidor regional: {self.final_url}")
        
        print("\n📝 Configuração final no .env:")
        print(f"   KOMMO_BASE_URL={getattr(self, 'final_url', self.base_url)}")
        print(f"   KOMMO_SUBDOMAIN={self.subdomain}")
        print(f"   KOMMO_LONG_LIVED_TOKEN={self.token[:30]}...")
    
    def test_api_operations(self):
        """Testa operações básicas da API"""
        print("\n" + "="*70)
        print("🧪 TESTANDO OPERAÇÕES DA API")
        print("="*70)
        
        if not hasattr(self, 'working_url'):
            print("❌ Nenhuma URL funcionando encontrada")
            return False
        
        headers = self.working_headers
        base_url = self.working_url
        
        # Teste 1: Buscar pipelines
        print("\n📊 Teste 1: Buscando pipelines...")
        url = f"{base_url}/api/v4/leads/pipelines"
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                pipelines = data.get('_embedded', {}).get('pipelines', [])
                print(f"✅ {len(pipelines)} pipelines encontrados")
                for p in pipelines[:3]:
                    print(f"   - {p.get('name')} (ID: {p.get('id')})")
            else:
                print(f"❌ Erro: {response.status_code}")
        except Exception as e:
            print(f"❌ Erro: {e}")
        
        # Teste 2: Buscar campos personalizados
        print("\n📋 Teste 2: Buscando campos personalizados...")
        url = f"{base_url}/api/v4/leads/custom_fields"
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                fields = data.get('_embedded', {}).get('custom_fields', [])
                print(f"✅ {len(fields)} campos encontrados")
                for f in fields[:5]:
                    print(f"   - {f.get('name')} (ID: {f.get('id')})")
            else:
                print(f"❌ Erro: {response.status_code}")
        except Exception as e:
            print(f"❌ Erro: {e}")
        
        return True
    
    def suggest_solution(self):
        """Sugere soluções baseadas no diagnóstico"""
        print("\n" + "="*70)
        print("💡 SOLUÇÃO RECOMENDADA")
        print("="*70)
        
        if hasattr(self, 'working_url'):
            print(f"\n✅ AUTENTICAÇÃO FUNCIONANDO!")
            print(f"\n📝 Use estas configurações no .env:")
            print(f"   KOMMO_BASE_URL={self.working_url}")
            print(f"   KOMMO_SUBDOMAIN={self.subdomain}")
            print(f"\n🚀 O sistema deve funcionar com essas configurações")
        else:
            print("\n❌ NENHUMA CONFIGURAÇÃO FUNCIONOU")
            print("\n🔧 AÇÕES NECESSÁRIAS:")
            print("\n1. VERIFIQUE A INTEGRAÇÃO NO KOMMO:")
            print(f"   • Acesse: https://{self.subdomain}.kommo.com")
            print("   • Vá em: Configurações → Integrações")
            print("   • Procure por: 'SDR IA Solar Prime' ou integrações privadas")
            print("   • Status deve estar: ATIVO/INSTALADO")
            print("\n2. SE NÃO EXISTIR OU ESTIVER INATIVA:")
            print("   • Clique em 'Criar integração'")
            print("   • Escolha: 'Integração privada'")
            print("   • Nome: 'SDR IA Solar Prime'")
            print("   • Após criar, vá em 'Keys and Scopes'")
            print("   • Clique em 'Generate long-lived token'")
            print("   • Escolha: 5 anos de validade")
            print("   • COPIE O TOKEN IMEDIATAMENTE")
            print("\n3. ATUALIZE O .ENV:")
            print("   • Cole o novo token na linha KOMMO_LONG_LIVED_TOKEN=")
            print("   • NÃO use aspas")
            print("   • NÃO adicione espaços")
            print("\n4. POSSÍVEIS PROBLEMAS:")
            print("   • A integração foi criada em outro account")
            print("   • O usuário não tem permissões de admin")
            print("   • A conta está suspensa ou sem pagamento")
            print("   • IP bloqueado por muitas tentativas (aguarde 1h)")

async def main():
    """Executa diagnóstico completo"""
    print("\n" + "="*70)
    print("🚀 DIAGNÓSTICO COMPLETO DO KOMMO - 4 DE AGOSTO DE 2025")
    print("="*70)
    
    diagnostic = KommoDiagnostic()
    
    # 1. Analisar token
    if not diagnostic.analyze_token():
        print("\n❌ Token inválido ou mal formatado")
        diagnostic.suggest_solution()
        return
    
    # 2. Testar todos os endpoints
    if diagnostic.test_all_endpoints():
        print("\n✅ Encontrada configuração funcional!")
        
        # 3. Testar conexão assíncrona
        await diagnostic.test_async_connection()
        
        # 4. Testar operações da API
        diagnostic.test_api_operations()
        
        # 5. Corrigir .env
        diagnostic.fix_env_file()
        
        print("\n" + "="*70)
        print("✅ DIAGNÓSTICO COMPLETO - SISTEMA PRONTO")
        print("="*70)
        print("\n🚀 Reinicie o servidor com: python main.py")
    else:
        print("\n❌ Nenhuma configuração funcionou")
        diagnostic.suggest_solution()

if __name__ == "__main__":
    asyncio.run(main())