#!/usr/bin/env python3
"""
Script de Limpeza da Knowledge Base - Camada 3
Remove formatação incorreta de todos os registros da knowledge_base

Uso: python scripts/clean_knowledge_base.py [--dry-run] [--verbose]
"""

import asyncio
import re
import sys
import argparse
from pathlib import Path
from loguru import logger
from typing import List, Dict, Any

# Adiciona o diretório raiz ao path para importar módulos do projeto
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.integrations.supabase_client import supabase_client


def sanitize_knowledge_content(text: str) -> str:
    """
    Sanitiza o conteúdo da knowledge_base usando a mesma lógica do webhooks.py
    Remove emojis, markdown duplo, enumerações e formatação incorreta
    
    Args:
        text: Texto a ser sanitizado
        
    Returns:
        Texto limpo sem formatação incorreta
    """
    if not isinstance(text, str):
        return ""

    # 1. Remover emojis (padrão Unicode abrangente)
    emoji_pattern = re.compile("["
                               u"\U0001f600-\U0001f64f"  # emoticons
                               u"\U0001f300-\U0001f5ff"  # symbols & pictographs
                               u"\U0001f680-\U0001f6ff"  # transport & map symbols
                               u"\U0001f1e0-\U0001f1ff"  # flags (ios)
                               u"\u2600-\u26ff"          # miscellaneous symbols
                               u"\u2700-\u27bf"          # dingbats
                               u"\u2300-\u23ff"          # misc technical
                               u"\ufe0f"                # variation selector
                               u"\u200d"                # zero width joiner
                               "]+", flags=re.UNICODE)
    text = emoji_pattern.sub(r'', text)

    # 2. Remover todo o markdown (negrito duplo, itálico, etc.)
    # Remove **, *, _, __, ~, `, etc.
    text = re.sub(r'\*{2,}', '', text)  # Remove ** (markdown duplo)
    text = re.sub(r'[_~`]', '', text)   # Remove outros markdowns

    # 3. Remover enumerações e juntar linhas
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        # Remove padrões como "1. ", "- ", "* " no início da linha
        cleaned_line = re.sub(r'^\s*\d+\.\s*|^\s*[-*]\s*', '', line.strip())
        if cleaned_line:
            cleaned_lines.append(cleaned_line)
    
    text = ' '.join(cleaned_lines)

    # 4. Remover espaços duplos e limpar
    text = ' '.join(text.split())

    return text.strip()


async def get_all_knowledge_records() -> List[Dict[str, Any]]:
    """
    Busca todos os registros da knowledge_base
    
    Returns:
        Lista de registros da knowledge_base
    """
    try:
        logger.info("🔍 Buscando todos os registros da knowledge_base...")
        
        result = supabase_client.client.table("knowledge_base").select(
            "id, title, content, category, tags"
        ).execute()
        
        if result.data:
            logger.info(f"✅ Encontrados {len(result.data)} registros para análise")
            return result.data
        else:
            logger.warning("⚠️ Nenhum registro encontrado na knowledge_base")
            return []
            
    except Exception as e:
        logger.error(f"❌ Erro ao buscar registros: {e}")
        return []


def analyze_record_formatting(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analisa um registro e identifica problemas de formatação
    
    Args:
        record: Registro da knowledge_base
        
    Returns:
        Análise dos problemas encontrados
    """
    issues = {
        "has_emojis": False,
        "has_double_markdown": False,
        "has_enumerations": False,
        "has_line_breaks": False,
        "needs_cleaning": False,
        "original_content": record.get('content', ''),
        "cleaned_content": ""
    }
    
    content = record.get('content', '')
    if not content:
        return issues
    
    # Verificar emojis
    emoji_pattern = re.compile("["
                               u"\U0001f600-\U0001f64f"
                               u"\U0001f300-\U0001f5ff"
                               u"\U0001f680-\U0001f6ff"
                               u"\U0001f1e0-\U0001f1ff"
                               u"\u2600-\u26ff"
                               u"\u2700-\u27bf"
                               u"\u2300-\u23ff"
                               u"\ufe0f"
                               u"\u200d"
                               "]+", flags=re.UNICODE)
    
    if emoji_pattern.search(content):
        issues["has_emojis"] = True
        issues["needs_cleaning"] = True
    
    # Verificar markdown duplo
    if re.search(r'\*{2,}', content):
        issues["has_double_markdown"] = True
        issues["needs_cleaning"] = True
    
    # Verificar enumerações
    if re.search(r'^\s*\d+\.\s*|^\s*[-*]\s*', content, re.MULTILINE):
        issues["has_enumerations"] = True
        issues["needs_cleaning"] = True
    
    # Verificar quebras de linha múltiplas
    if '\n' in content or '\r' in content:
        issues["has_line_breaks"] = True
        issues["needs_cleaning"] = True
    
    # Gerar conteúdo limpo
    if issues["needs_cleaning"]:
        issues["cleaned_content"] = sanitize_knowledge_content(content)
    else:
        issues["cleaned_content"] = content
    
    return issues


async def clean_knowledge_base(dry_run: bool = True, verbose: bool = False) -> Dict[str, Any]:
    """
    Limpa a knowledge_base removendo formatação incorreta
    
    Args:
        dry_run: Se True, apenas simula a limpeza sem modificar dados
        verbose: Se True, exibe informações detalhadas
        
    Returns:
        Estatísticas da operação
    """
    stats = {
        "total_records": 0,
        "records_with_issues": 0,
        "records_cleaned": 0,
        "issues_found": {
            "emojis": 0,
            "double_markdown": 0,
            "enumerations": 0,
            "line_breaks": 0
        },
        "errors": 0
    }
    
    try:
        # Buscar todos os registros
        records = await get_all_knowledge_records()
        stats["total_records"] = len(records)
        
        if not records:
            logger.warning("❌ Nenhum registro para processar")
            return stats
        
        logger.info(f"📊 Iniciando {'simulação' if dry_run else 'limpeza'} de {len(records)} registros...")
        
        for record in records:
            record_id = record.get('id')
            title = record.get('title', 'Sem título')
            
            # Analisar registro
            analysis = analyze_record_formatting(record)
            
            if analysis["needs_cleaning"]:
                stats["records_with_issues"] += 1
                
                # Contar tipos de problemas
                if analysis["has_emojis"]:
                    stats["issues_found"]["emojis"] += 1
                if analysis["has_double_markdown"]:
                    stats["issues_found"]["double_markdown"] += 1
                if analysis["has_enumerations"]:
                    stats["issues_found"]["enumerations"] += 1
                if analysis["has_line_breaks"]:
                    stats["issues_found"]["line_breaks"] += 1
                
                if verbose:
                    logger.info(f"\n🔍 REGISTRO: {title} (ID: {record_id})")
                    logger.info(f"  📝 Problemas: {', '.join([k for k, v in analysis.items() if k.startswith('has_') and v])}")
                    logger.info(f"  📄 Original: {analysis['original_content'][:100]}...")
                    logger.info(f"  ✨ Limpo: {analysis['cleaned_content'][:100]}...")
                
                if not dry_run:
                    # Atualizar registro no banco
                    try:
                        update_result = supabase_client.client.table("knowledge_base").update({
                            "content": analysis["cleaned_content"],
                            "updated_at": "NOW()"
                        }).eq("id", record_id).execute()
                        
                        if update_result.data:
                            stats["records_cleaned"] += 1
                            logger.success(f"✅ Registro '{title}' limpo com sucesso")
                        else:
                            logger.error(f"❌ Falha ao limpar registro '{title}'")
                            stats["errors"] += 1
                            
                    except Exception as e:
                        logger.error(f"❌ Erro ao atualizar registro '{title}': {e}")
                        stats["errors"] += 1
            else:
                if verbose:
                    logger.info(f"✅ REGISTRO OK: {title} (ID: {record_id})")
        
        # Relatório final
        logger.info("\n" + "="*60)
        logger.info("📊 RELATÓRIO FINAL DA LIMPEZA")
        logger.info("="*60)
        logger.info(f"📈 Total de registros analisados: {stats['total_records']}")
        logger.info(f"⚠️  Registros com problemas encontrados: {stats['records_with_issues']}")
        
        if dry_run:
            logger.info(f"🔍 Modo simulação - nenhum dado foi modificado")
            logger.info(f"📝 Registros que seriam limpos: {stats['records_with_issues']}")
        else:
            logger.info(f"✅ Registros efetivamente limpos: {stats['records_cleaned']}")
            logger.info(f"❌ Erros durante limpeza: {stats['errors']}")
        
        logger.info("\n🔍 TIPOS DE PROBLEMAS ENCONTRADOS:")
        logger.info(f"  😀 Emojis: {stats['issues_found']['emojis']} registros")
        logger.info(f"  ** Markdown duplo: {stats['issues_found']['double_markdown']} registros")
        logger.info(f"  1. Enumerações: {stats['issues_found']['enumerations']} registros")
        logger.info(f"  \\n Quebras de linha: {stats['issues_found']['line_breaks']} registros")
        
        if not dry_run and stats["records_cleaned"] > 0:
            logger.success(f"\n🎉 Limpeza concluída! {stats['records_cleaned']} registros foram sanitizados.")
        elif dry_run and stats["records_with_issues"] > 0:
            logger.info(f"\n💡 Execute sem --dry-run para aplicar as correções.")
        elif stats["records_with_issues"] == 0:
            logger.success(f"\n🎉 Parabéns! Todos os registros já estão limpos e formatados corretamente.")
        
        return stats
        
    except Exception as e:
        logger.error(f"❌ Erro geral na limpeza: {e}")
        stats["errors"] += 1
        return stats


async def main():
    """Função principal do script"""
    parser = argparse.ArgumentParser(description="Limpa formatação incorreta da knowledge_base")
    parser.add_argument("--dry-run", action="store_true", 
                       help="Simula a limpeza sem modificar dados (padrão: True)")
    parser.add_argument("--execute", action="store_true", 
                       help="Executa a limpeza modificando os dados efetivamente")
    parser.add_argument("--verbose", "-v", action="store_true", 
                       help="Exibe informações detalhadas sobre cada registro")
    
    args = parser.parse_args()
    
    # Por segurança, dry_run é padrão a menos que --execute seja especificado
    dry_run = not args.execute
    
    if dry_run:
        logger.info("🔍 MODO SIMULAÇÃO - Nenhum dado será modificado")
        logger.info("💡 Use --execute para aplicar as correções efetivamente")
    else:
        logger.warning("⚠️  MODO EXECUÇÃO - Os dados SERÃO modificados!")
        
        # Confirmação adicional para modo execução
        response = input("\n❓ Tem certeza que deseja executar a limpeza? (digite 'SIM' para confirmar): ")
        if response.strip().upper() != 'SIM':
            logger.info("❌ Operação cancelada pelo usuário")
            return
    
    logger.info("\n🚀 Iniciando análise da knowledge_base...")
    
    try:
        stats = await clean_knowledge_base(dry_run=dry_run, verbose=args.verbose)
        
        if stats["errors"] > 0:
            logger.error(f"❌ Concluído com {stats['errors']} erros")
            sys.exit(1)
        else:
            logger.success("✅ Operação concluída com sucesso!")
            sys.exit(0)
            
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())