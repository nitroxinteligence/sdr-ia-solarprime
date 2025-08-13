#!/usr/bin/env python3
"""
Script para buscar e analisar TODOS os campos customizados disponíveis no Kommo
Identifica IDs corretos, tipos e valores aceitos para campos select
Foco nos campos: solution_type, calendar_link, location
"""

import asyncio
import aiohttp
import json
from datetime import datetime
import os
from pathlib import Path

# Carregar configuração
from dotenv import load_dotenv

# Tentar carregar .env
possible_paths = [
    Path('.env'),
    Path(__file__).parent / '.env',
]

for env_path in possible_paths:
    if env_path.exists():
        load_dotenv(env_path, override=True)
        print(f"✅ Arquivo .env encontrado: {env_path}")
        break

# Configurações do Kommo
TOKEN = os.getenv("KOMMO_LONG_LIVED_TOKEN")
BASE_URL = os.getenv("KOMMO_BASE_URL", "https://leonardofvieira00.kommo.com")

if not TOKEN:
    print("❌ ERRO: KOMMO_LONG_LIVED_TOKEN não encontrado no .env")
    exit(1)

class KommoCustomFieldsAnalyzer:
    """Analisador de campos customizados do Kommo"""
    
    def __init__(self):
        self.token = TOKEN
        self.base_url = BASE_URL
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        self.session = None
        
    async def initialize(self):
        """Inicializa sessão HTTP"""
        connector = aiohttp.TCPConnector(
            limit=10,
            limit_per_host=5,
            ttl_dns_cache=300,
            use_dns_cache=True,
        )
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=aiohttp.ClientTimeout(total=30)
        )
    
    async def close(self):
        """Fecha sessão HTTP"""
        if self.session and not self.session.closed:
            await self.session.close()
            await asyncio.sleep(0.1)
    
    async def test_connection(self):
        """Testa conexão com a API"""
        try:
            async with self.session.get(
                f"{self.base_url}/api/v4/account",
                headers=self.headers
            ) as response:
                if response.status == 200:
                    account = await response.json()
                    print(f"✅ Conectado ao Kommo: {account.get('name', 'N/A')}")
                    return True
                else:
                    print(f"❌ Erro de conexão: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Erro na conexão: {e}")
            return False
    
    async def analyze_custom_fields(self):
        """Analisa todos os campos customizados disponíveis"""
        print("\n" + "="*80)
        print("📊 ANALISANDO CAMPOS CUSTOMIZADOS DO KOMMO")
        print("="*80)
        
        # Campos de diferentes entidades
        entities = {
            "leads": "Leads (Negócios)",
            "contacts": "Contatos",
            "companies": "Empresas"
        }
        
        all_fields = {}
        
        for entity, description in entities.items():
            print(f"\n🔍 {description.upper()}:")
            print("-" * 60)
            
            try:
                async with self.session.get(
                    f"{self.base_url}/api/v4/{entity}/custom_fields",
                    headers=self.headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        fields = data.get("_embedded", {}).get("custom_fields", [])
                        
                        entity_fields = []
                        
                        for field in fields:
                            field_info = {
                                "id": field.get("id"),
                                "name": field.get("name"),
                                "type": field.get("type"),
                                "code": field.get("code"),
                                "sort": field.get("sort"),
                                "entity_type": entity,
                                "is_required": field.get("required_statuses"),
                                "settings": field.get("settings", {}),
                                "enums": field.get("enums", [])
                            }
                            
                            entity_fields.append(field_info)
                            
                            # Exibir informações do campo
                            print(f"📋 Nome: {field_info['name']}")
                            print(f"   ID: {field_info['id']}")
                            print(f"   Tipo: {field_info['type']}")
                            print(f"   Código: {field_info['code']}")
                            
                            # Se for campo select, mostrar opções
                            if field_info['enums']:
                                print(f"   🎯 Opções (SELECT):")
                                for enum in field_info['enums']:
                                    print(f"      • {enum.get('value')} (ID: {enum.get('id')})")
                            
                            # Se tiver configurações especiais
                            if field_info['settings']:
                                print(f"   ⚙️ Configurações: {field_info['settings']}")
                            
                            print()
                        
                        all_fields[entity] = entity_fields
                        print(f"✅ {len(entity_fields)} campos encontrados em {description}")
                        
                    else:
                        error = await response.text()
                        print(f"❌ Erro ao buscar campos de {entity}: {response.status}")
                        print(f"   {error}")
                        
            except Exception as e:
                print(f"❌ Erro na requisição para {entity}: {e}")
        
        return all_fields
    
    async def find_target_fields(self, all_fields):
        """Procura campos específicos de interesse"""
        print("\n" + "="*80)
        print("🎯 CAMPOS DE INTERESSE IDENTIFICADOS")
        print("="*80)
        
        # Campos que estamos procurando
        target_fields = {
            "solution_type": ["solução", "solution", "tipo", "type", "solar"],
            "calendar_link": ["calendar", "calendário", "evento", "link", "google"],
            "location": ["local", "location", "endereço", "address", "instalação"]
        }
        
        found_fields = {}
        
        for target_name, keywords in target_fields.items():
            print(f"\n🔍 Procurando por '{target_name.upper()}':")
            print("-" * 40)
            
            matches = []
            
            for entity, fields in all_fields.items():
                for field in fields:
                    field_name_lower = field['name'].lower()
                    
                    # Verificar se alguma palavra-chave está no nome
                    for keyword in keywords:
                        if keyword.lower() in field_name_lower:
                            match_info = {
                                **field,
                                "match_keyword": keyword,
                                "match_score": len([k for k in keywords if k.lower() in field_name_lower])
                            }
                            matches.append(match_info)
                            break
            
            # Ordenar por score de match (mais matches = melhor)
            matches.sort(key=lambda x: x['match_score'], reverse=True)
            
            if matches:
                print("📍 Candidatos encontrados:")
                for i, match in enumerate(matches[:5], 1):  # Top 5
                    print(f"   {i}. {match['name']} (ID: {match['id']})")
                    print(f"      Entidade: {match['entity_type']}")
                    print(f"      Tipo: {match['type']}")
                    print(f"      Palavra-chave: {match['match_keyword']}")
                    
                    if match['enums']:
                        print(f"      Opções SELECT:")
                        for enum in match['enums'][:10]:  # Primeiras 10
                            print(f"         • {enum.get('value')} (ID: {enum.get('id')})")
                    print()
                
                found_fields[target_name] = matches
            else:
                print("❌ Nenhum campo encontrado")
        
        return found_fields
    
    async def generate_mapping_code(self, found_fields):
        """Gera código Python com o mapeamento correto"""
        print("\n" + "="*80)
        print("💾 GERANDO CÓDIGO DE MAPEAMENTO")
        print("="*80)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Gerar mapeamento para custom_fields
        mapping_lines = []
        mapping_lines.append("# Mapeamento de campos customizados do Kommo")
        mapping_lines.append(f"# Gerado automaticamente em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        mapping_lines.append("")
        mapping_lines.append("self.custom_fields = {")
        
        # Campos existentes conhecidos
        known_fields = {
            "phone": 392802,
            "whatsapp": 392802,
            "bill_value": 392804,
            "valor_conta": 392804,
            "conversation_id": 392860
        }
        
        # Adicionar campos conhecidos
        for field_name, field_id in known_fields.items():
            mapping_lines.append(f'    "{field_name}": {field_id},  # Campo conhecido')
        
        # Adicionar campos encontrados
        for target_name, matches in found_fields.items():
            if matches:
                # Usar o melhor match (primeiro da lista)
                best_match = matches[0]
                mapping_lines.append(f'    "{target_name}": {best_match["id"]},  # {best_match["name"]} ({best_match["type"]})')
                
                # Se tiver opções de select, adicionar comentário
                if best_match['enums']:
                    mapping_lines.append(f'    # Opções para {target_name}:')
                    for enum in best_match['enums'][:5]:  # Primeiras 5
                        mapping_lines.append(f'    #   {enum.get("value")} = {enum.get("id")}')
            else:
                mapping_lines.append(f'    "{target_name}": None,  # Campo não encontrado')
        
        mapping_lines.append("}")
        
        # Salvar arquivo
        mapping_code = "\n".join(mapping_lines)
        
        filename = f"kommo_field_mapping_{timestamp}.py"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(mapping_code)
        
        print(f"📄 Código gerado em: {filename}")
        print("\n📋 Preview do mapeamento:")
        print("-" * 40)
        print(mapping_code)
        
        return mapping_code
    
    async def save_detailed_report(self, all_fields, found_fields):
        """Salva relatório detalhado em JSON"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "kommo_base_url": self.base_url,
            "total_entities": len(all_fields),
            "all_fields": all_fields,
            "target_fields_analysis": found_fields,
            "summary": {
                "total_fields": sum(len(fields) for fields in all_fields.values()),
                "fields_by_entity": {entity: len(fields) for entity, fields in all_fields.items()},
                "target_fields_found": {name: len(matches) for name, matches in found_fields.items()}
            }
        }
        
        filename = f"kommo_fields_analysis_{timestamp}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Relatório detalhado salvo em: {filename}")
        
        return report

async def main():
    """Função principal"""
    analyzer = KommoCustomFieldsAnalyzer()
    
    try:
        await analyzer.initialize()
        
        # Testar conexão
        if not await analyzer.test_connection():
            return
        
        # Analisar campos customizados
        all_fields = await analyzer.analyze_custom_fields()
        
        if not all_fields:
            print("❌ Nenhum campo customizado encontrado")
            return
        
        # Procurar campos específicos
        found_fields = await analyzer.find_target_fields(all_fields)
        
        # Gerar código de mapeamento
        await analyzer.generate_mapping_code(found_fields)
        
        # Salvar relatório detalhado
        await analyzer.save_detailed_report(all_fields, found_fields)
        
        print("\n🎉 ANÁLISE COMPLETA!")
        print("="*80)
        print("✅ Campos customizados analisados")
        print("✅ Mapeamento gerado")
        print("✅ Relatório JSON salvo")
        
    except Exception as e:
        print(f"❌ Erro durante análise: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        await analyzer.close()

if __name__ == "__main__":
    print("🚀 Iniciando análise de campos customizados do Kommo...")
    asyncio.run(main())