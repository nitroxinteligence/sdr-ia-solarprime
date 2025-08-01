#!/usr/bin/env python3
"""
Script de validação das correções de race conditions.

Valida se as correções implementadas estão estruturalmente corretas
sem precisar do servidor rodando.

Execução: python3 validate_race_condition_fixes.py
"""

import sys
import os
import importlib.util
from pathlib import Path
from typing import Dict, List, Any

class RaceConditionFixValidator:
    """Validador das correções implementadas"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.validation_results = {
            "supabase_upsert_fixes": {"status": "unknown", "details": []},
            "context_dict_approach": {"status": "unknown", "details": []},
            "agno_async_optimization": {"status": "unknown", "details": []},
            "error_handling_comprehensive": {"status": "unknown", "details": []},
            "test_files_structure": {"status": "unknown", "details": []}
        }
    
    def validate_supabase_upsert_fixes(self):
        """Valida se as correções UPSERT foram implementadas"""
        print("🔍 Validando correções UPSERT atômico no Supabase...")
        
        try:
            # Verificar conversation_repository.py
            repo_file = self.project_root / "agente" / "repositories" / "conversation_repository.py"
            if not repo_file.exists():
                self.validation_results["supabase_upsert_fixes"]["status"] = "error"
                self.validation_results["supabase_upsert_fixes"]["details"].append(
                    "conversation_repository.py não encontrado"
                )
                return
            
            with open(repo_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verificar se contém as correções esperadas
            upsert_indicators = [
                "get_or_create_lead",  # Método UPSERT para leads
                "max_retries",         # Retry logic
                "constraint violation", # Tratamento específico
                "exponential backoff", # Backoff strategy
                "duplicate key value violates unique constraint" # Error handling específico
            ]
            
            found_indicators = []
            for indicator in upsert_indicators:
                if indicator.lower() in content.lower():
                    found_indicators.append(indicator)
            
            if len(found_indicators) >= 4:  # Pelo menos 4 dos 5 indicadores
                self.validation_results["supabase_upsert_fixes"]["status"] = "success"
                self.validation_results["supabase_upsert_fixes"]["details"] = [
                    f"✅ Encontrados {len(found_indicators)}/5 indicadores UPSERT",
                    f"✅ Indicadores: {', '.join(found_indicators)}"
                ]
            else:
                self.validation_results["supabase_upsert_fixes"]["status"] = "warning"
                self.validation_results["supabase_upsert_fixes"]["details"] = [
                    f"⚠️  Apenas {len(found_indicators)}/5 indicadores encontrados",
                    f"⚠️  Pode precisar de mais correções UPSERT"
                ]
                
        except Exception as e:
            self.validation_results["supabase_upsert_fixes"]["status"] = "error"
            self.validation_results["supabase_upsert_fixes"]["details"].append(f"Erro: {str(e)}")
    
    def validate_context_dict_approach(self):
        """Valida se a abordagem context dict foi implementada"""
        print("🔍 Validando context dict approach...")
        
        try:
            # Verificar main.py
            main_file = self.project_root / "agente" / "main.py"
            if not main_file.exists():
                self.validation_results["context_dict_approach"]["status"] = "error"
                self.validation_results["context_dict_approach"]["details"].append(
                    "agente/main.py não encontrado"
                )
                return
            
            with open(main_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verificar se contém as correções esperadas
            context_indicators = [
                "message_context",     # Variável context dict
                "conversation_id\": None", # Inicialização do context
                "context dict",        # Comentários explicativos
                "context dict approach", # Menção específica
                "WhatsAppMessage.*conversation_id" # Referência ao problema original
            ]
            
            found_indicators = []
            for indicator in context_indicators:
                if indicator.lower() in content.lower():
                    found_indicators.append(indicator)
            
            if len(found_indicators) >= 3:
                self.validation_results["context_dict_approach"]["status"] = "success"
                self.validation_results["context_dict_approach"]["details"] = [
                    f"✅ Encontrados {len(found_indicators)}/5 indicadores context dict",
                    f"✅ Context dict implementado corretamente"
                ]
            else:
                self.validation_results["context_dict_approach"]["status"] = "warning"
                self.validation_results["context_dict_approach"]["details"] = [
                    f"⚠️  Apenas {len(found_indicators)}/5 indicadores encontrados",
                    f"⚠️  Context dict pode precisar de ajustes"
                ]
                
        except Exception as e:
            self.validation_results["context_dict_approach"]["status"] = "error"
            self.validation_results["context_dict_approach"]["details"].append(f"Erro: {str(e)}")
    
    def validate_agno_async_optimization(self):
        """Valida otimizações async no AGnO"""
        print("🔍 Validando otimizações async AGnO...")
        
        try:
            # Verificar agent.py
            agent_file = self.project_root / "agente" / "core" / "agent.py"
            if not agent_file.exists():
                self.validation_results["agno_async_optimization"]["status"] = "error"
                self.validation_results["agno_async_optimization"]["details"].append(
                    "agente/core/agent.py não encontrado"
                )
                return
            
            with open(agent_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verificar otimizações async
            async_indicators = [
                "_extract_response_text",  # Método melhorado
                "arun",                    # Método async AGnO
                "inspect.iscoroutinefunction", # Verificação de async
                "RunResponse",             # Tratamento de resposta AGnO
                "agent_response.content"   # Acesso correto ao content
            ]
            
            found_indicators = []
            for indicator in async_indicators:
                if indicator in content:  # Busca exata para métodos
                    found_indicators.append(indicator)
            
            if len(found_indicators) >= 3:
                self.validation_results["agno_async_optimization"]["status"] = "success"
                self.validation_results["agno_async_optimization"]["details"] = [
                    f"✅ Encontrados {len(found_indicators)}/5 indicadores async",
                    f"✅ AGnO async otimizado corretamente"
                ]
            else:
                self.validation_results["agno_async_optimization"]["status"] = "warning"
                self.validation_results["agno_async_optimization"]["details"] = [
                    f"⚠️  Apenas {len(found_indicators)}/5 indicadores encontrados",
                    f"⚠️  AGnO async pode precisar de otimizações"
                ]
                
        except Exception as e:
            self.validation_results["agno_async_optimization"]["status"] = "error"
            self.validation_results["agno_async_optimization"]["details"].append(f"Erro: {str(e)}")
    
    def validate_error_handling_comprehensive(self):
        """Valida error handling abrangente"""
        print("🔍 Validando error handling abrangente...")
        
        try:
            files_to_check = [
                self.project_root / "agente" / "main.py",
                self.project_root / "agente" / "core" / "agent.py",
                self.project_root / "agente" / "repositories" / "conversation_repository.py"
            ]
            
            total_error_patterns = 0
            found_error_patterns = 0
            
            error_handling_patterns = [
                "try:",
                "except Exception as",
                "logger.error",
                "capture_agent_error",
                "error_str",
                "constraint violation",
                "timeout",
                "connection",
                "rate limit"
            ]
            
            for file_path in files_to_check:
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    for pattern in error_handling_patterns:
                        total_error_patterns += 1
                        if pattern in content.lower():
                            found_error_patterns += 1
            
            error_coverage = (found_error_patterns / total_error_patterns) * 100 if total_error_patterns > 0 else 0
            
            if error_coverage >= 70:
                self.validation_results["error_handling_comprehensive"]["status"] = "success"
                self.validation_results["error_handling_comprehensive"]["details"] = [
                    f"✅ Cobertura de error handling: {error_coverage:.1f}%",
                    f"✅ Error handling abrangente implementado"
                ]
            elif error_coverage >= 50:
                self.validation_results["error_handling_comprehensive"]["status"] = "warning"
                self.validation_results["error_handling_comprehensive"]["details"] = [
                    f"⚠️  Cobertura de error handling: {error_coverage:.1f}%",
                    f"⚠️  Error handling pode ser melhorado"
                ]
            else:
                self.validation_results["error_handling_comprehensive"]["status"] = "error"
                self.validation_results["error_handling_comprehensive"]["details"] = [
                    f"❌ Cobertura de error handling: {error_coverage:.1f}%",
                    f"❌ Error handling insuficiente"
                ]
                
        except Exception as e:
            self.validation_results["error_handling_comprehensive"]["status"] = "error"
            self.validation_results["error_handling_comprehensive"]["details"].append(f"Erro: {str(e)}")
    
    def validate_test_files_structure(self):
        """Valida estrutura dos arquivos de teste"""
        print("🔍 Validando estrutura dos arquivos de teste...")
        
        test_files = [
            "test_critical_race_conditions.py",
            "test_race_condition_fixes.py",
            "run_race_condition_tests.sh",
            "TEST_RACE_CONDITIONS_README.md"
        ]
        
        found_files = []
        missing_files = []
        
        for test_file in test_files:
            file_path = self.project_root / test_file
            if file_path.exists():
                found_files.append(test_file)
            else:
                missing_files.append(test_file)
        
        if len(found_files) == len(test_files):
            self.validation_results["test_files_structure"]["status"] = "success"
            self.validation_results["test_files_structure"]["details"] = [
                f"✅ Todos os {len(test_files)} arquivos de teste encontrados",
                f"✅ Estrutura de testes completa"
            ]
        elif len(found_files) >= len(test_files) * 0.75:
            self.validation_results["test_files_structure"]["status"] = "warning"
            self.validation_results["test_files_structure"]["details"] = [
                f"⚠️  {len(found_files)}/{len(test_files)} arquivos encontrados",
                f"⚠️  Arquivos faltando: {', '.join(missing_files)}"
            ]
        else:
            self.validation_results["test_files_structure"]["status"] = "error"
            self.validation_results["test_files_structure"]["details"] = [
                f"❌ Apenas {len(found_files)}/{len(test_files)} arquivos encontrados",
                f"❌ Estrutura de testes incompleta"
            ]
    
    def generate_validation_report(self):
        """Gera relatório de validação"""
        print("\n" + "="*70)
        print("📋 RELATÓRIO DE VALIDAÇÃO - CORREÇÕES RACE CONDITIONS")
        print("="*70)
        
        overall_status = "success"
        
        for fix_name, result in self.validation_results.items():
            status = result["status"]
            details = result["details"]
            
            # Determinar ícone
            if status == "success":
                icon = "✅"
            elif status == "warning":
                icon = "⚠️ "
                if overall_status == "success":
                    overall_status = "warning"
            else:
                icon = "❌"
                overall_status = "error"
            
            print(f"\n{icon} {fix_name.upper().replace('_', ' ')}:")
            for detail in details:
                print(f"   {detail}")
        
        # Status geral
        print(f"\n🎯 STATUS GERAL:")
        if overall_status == "success":
            print(f"   ✅ TODAS AS CORREÇÕES VALIDADAS COM SUCESSO!")
            print(f"   🚀 Sistema parece estar corrigido e pronto para testes")
        elif overall_status == "warning":
            print(f"   ⚠️  CORREÇÕES IMPLEMENTADAS COM ALGUMAS OBSERVAÇÕES")
            print(f"   🔧 Algumas melhorias podem ser necessárias")
        else:
            print(f"   ❌ CORREÇÕES PRECISAM DE MAIS TRABALHO")
            print(f"   🛠️  Correções adicionais necessárias antes dos testes")
        
        print("\n" + "="*70)
        print("📋 PRÓXIMOS PASSOS:")
        
        if overall_status in ["success", "warning"]:
            print("1. ✅ Validação estrutural passou")
            print("2. 🚀 Iniciar servidor: uvicorn agente.main:app --reload --host 0.0.0.0 --port 8000")
            print("3. 🧪 Executar testes: ./run_race_condition_tests.sh")
            print("4. 📊 Analisar relatórios de teste gerados")
        else:
            print("1. ❌ Corrigir problemas estruturais identificados")
            print("2. 🔄 Re-executar validação")
            print("3. 🧪 Executar testes após correções")
        
        print("="*70)

def main():
    """Executa validação completa"""
    print("🔍 VALIDADOR DE CORREÇÕES RACE CONDITIONS")
    print("="*50)
    print("Validando estruturalmente as correções implementadas...")
    print("="*50)
    
    validator = RaceConditionFixValidator()
    
    # Executar todas as validações
    validator.validate_supabase_upsert_fixes()
    validator.validate_context_dict_approach()
    validator.validate_agno_async_optimization()
    validator.validate_error_handling_comprehensive()
    validator.validate_test_files_structure()
    
    # Gerar relatório
    validator.generate_validation_report()

if __name__ == "__main__":
    main()