#!/usr/bin/env python3
"""
Script para verificar e corrigir leads com kommo_lead_id inválidos
"""

import asyncio
from app.integrations.supabase_client import SupabaseClient
from loguru import logger

async def fix_invalid_kommo_ids():
    """Verifica e corrige leads com kommo_lead_id inválidos"""
    
    db = SupabaseClient()
    
    try:
        # Buscar todos os leads
        logger.info("🔍 Buscando leads com kommo_lead_id...")
        
        result = db.client.table('leads').select("*").execute()
        leads = result.data if result.data else []
        
        logger.info(f"📊 Total de leads encontrados: {len(leads)}")
        
        invalid_count = 0
        fixed_count = 0
        
        for lead in leads:
            kommo_id = lead.get("kommo_lead_id")
            
            # Verificar IDs inválidos
            if kommo_id and (
                str(kommo_id) == "None" or
                str(kommo_id) == "0" or
                len(str(kommo_id)) > 10 or  # IDs muito grandes são suspeitos
                not str(kommo_id).isdigit()  # Deve ser numérico
            ):
                invalid_count += 1
                logger.warning(f"❌ Lead {lead['id']} tem kommo_id inválido: {kommo_id}")
                
                # Limpar o ID inválido
                try:
                    db.client.table('leads').update({
                        'kommo_lead_id': None
                    }).eq('id', lead['id']).execute()
                    
                    fixed_count += 1
                    logger.info(f"✅ Limpou kommo_id inválido do lead {lead['id']}")
                except Exception as e:
                    logger.error(f"Erro ao limpar lead {lead['id']}: {e}")
        
        logger.info(f"\n📊 Resumo:")
        logger.info(f"   - Total de leads: {len(leads)}")
        logger.info(f"   - IDs inválidos encontrados: {invalid_count}")
        logger.info(f"   - IDs corrigidos: {fixed_count}")
        
        # Verificar leads sem nome
        leads_sem_nome = [l for l in leads if not l.get('name') or l.get('name') == 'None']
        if leads_sem_nome:
            logger.warning(f"\n⚠️  {len(leads_sem_nome)} leads sem nome válido")
            for lead in leads_sem_nome[:5]:  # Mostrar apenas os 5 primeiros
                logger.info(f"   - Lead {lead['id']}: phone={lead.get('phone_number')}")
                
    except Exception as e:
        logger.error(f"❌ Erro ao verificar leads: {e}")

async def main():
    """Executa a correção"""
    logger.info("🚀 Iniciando correção de kommo_lead_id inválidos\n")
    await fix_invalid_kommo_ids()
    logger.info("\n✅ Correção concluída!")

if __name__ == "__main__":
    asyncio.run(main())