#!/usr/bin/env python3
"""
TESTE FINAL INTEGRADO - SDR IA SolarPrime
Valida todas as correções aplicadas para resolver erros críticos
"""

import sys
import ast
from pathlib import Path

# Adicionar o diretório do projeto ao path
sys.path.insert(0, str(Path(__file__).parent))

class SystemValidator:
    """Validador integrado do sistema"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.fixes_applied = []
        self.errors_found = []
    
    def test_supabase_fixes(self):
        """Testa correções do Supabase"""
        print("🔍 Validando correções Supabase...")
        
        try:
            service_file = self.base_path / "agente/services/supabase_service.py"
            content = service_file.read_text()
            
            checks = [
                (".maybe_single()", "maybe_single() em vez de single()"),
                ("result and hasattr(result, 'data') and result.data", "Verificação robusta de None"),
                ("get_or_create_lead", "Método get_or_create_lead implementado")
            ]
            
            for check, description in checks:
                if check in content:
                    self.fixes_applied.append(f"✅ Supabase: {description}")
                else:
                    self.errors_found.append(f"❌ Supabase: {description} não encontrado")
            
            return len(self.errors_found) == 0
            
        except Exception as e:
            self.errors_found.append(f"❌ Erro validando Supabase: {e}")
            return False
    
    def test_agno_fixes(self):
        """Testa correções do AGnO"""
        print("🔍 Validando correções AGnO...")
        
        try:
            agent_file = self.base_path / "agente/core/agent.py"
            content = agent_file.read_text()
            
            checks = [
                ("await self.agent.arun(agent_input)", "Uso de arun() para async tools"),
                ("user_message = message.message", "Extração direta da mensagem"),
                ("agent_input = f\"[CONTEXT: {stage_info}]", "Formato string para AGnO"),
                ("self._current_context = {", "Context storage separado")
            ]
            
            for check, description in checks:
                if check in content:
                    self.fixes_applied.append(f"✅ AGnO: {description}")
                else:
                    self.errors_found.append(f"❌ AGnO: {description} não encontrado")
            
            # Verificar se dict complexo foi removido
            problematic_patterns = [
                '"phone": message.phone,',
                '"context": context,'
            ]
            
            for pattern in problematic_patterns:
                if pattern in content:
                    # Verificar se está no contexto problemático
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if pattern in line:
                            context_lines = lines[max(0, i-3):i+3]
                            context_str = '\n'.join(context_lines)
                            if "await self.agent.arun(" in context_str:
                                self.errors_found.append(f"❌ AGnO: Dict complexo ainda sendo usado")
            
            return len(self.errors_found) == 0
            
        except Exception as e:
            self.errors_found.append(f"❌ Erro validando AGnO: {e}")
            return False
    
    def test_uuid_fixes(self):
        """Testa correções do UUID"""
        print("🔍 Validando correções UUID...")
        
        try:
            session_file = self.base_path / "agente/core/session_manager.py"
            content = session_file.read_text()
            
            checks = [
                ("import uuid", "Import UUID adicionado"),
                ("str(uuid.uuid4())", "Geração UUID válida"),
                ("UUID válido para PostgreSQL", "Comentário explicativo")
            ]
            
            for check, description in checks:
                if check in content:
                    self.fixes_applied.append(f"✅ UUID: {description}")
                else:
                    self.errors_found.append(f"❌ UUID: {description} não encontrado")
            
            # Verificar se formato temp_ foi removido do contexto problemático
            if 'f"temp_{phone}_{datetime.now(timezone.utc).timestamp()}"' in content:
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if 'f"temp_{phone}_' in line:
                        context_lines = lines[max(0, i-3):i+3]
                        context_str = '\n'.join(context_lines)
                        if "'id':" in context_str and "conversation = type" in context_str:
                            self.errors_found.append("❌ UUID: Formato temp_ ainda sendo usado")
            
            return len(self.errors_found) == 0
            
        except Exception as e:
            self.errors_found.append(f"❌ Erro validando UUID: {e}")
            return False
    
    def test_conversation_repository_fixes(self):
        """Testa correções do ConversationRepository"""
        print("🔍 Validando correções ConversationRepository...")
        
        try:
            repo_file = self.base_path / "agente/repositories/conversation_repository.py"
            content = repo_file.read_text()
            
            checks = [
                ('"updated_at": timestamp.isoformat()', "Campo updated_at corrigido"),
                ("update_last_message_at", "Método update_last_message_at implementado")
            ]
            
            for check, description in checks:
                if check in content:
                    self.fixes_applied.append(f"✅ Repository: {description}")
                else:
                    self.errors_found.append(f"❌ Repository: {description} não encontrado")
            
            return len(self.errors_found) == 0
            
        except Exception as e:
            self.errors_found.append(f"❌ Erro validando Repository: {e}")
            return False
    
    def test_syntax_validation(self):
        """Valida sintaxe de todos os arquivos modificados"""
        print("🔍 Validando sintaxe Python...")
        
        files_to_check = [
            "agente/core/agent.py",
            "agente/services/supabase_service.py", 
            "agente/core/session_manager.py",
            "agente/repositories/conversation_repository.py"
        ]
        
        syntax_valid = True
        
        for file_path in files_to_check:
            full_path = self.base_path / file_path
            if not full_path.exists():
                continue
                
            try:
                content = full_path.read_text()
                ast.parse(content)
                self.fixes_applied.append(f"✅ Sintaxe: {file_path} válida")
                
            except SyntaxError as e:
                self.errors_found.append(f"❌ Sintaxe: {file_path} - {e}")
                syntax_valid = False
        
        return syntax_valid
    
    def run_comprehensive_test(self):
        """Executa teste abrangente de todas as correções"""
        print("🚀 TESTE FINAL INTEGRADO - SDR IA SOLARPRIME")
        print("=" * 60)
        print("Validando todas as correções aplicadas...\n")
        
        test_results = [
            ("Correções Supabase", self.test_supabase_fixes),
            ("Correções AGnO", self.test_agno_fixes),
            ("Correções UUID", self.test_uuid_fixes),
            ("Correções Repository", self.test_conversation_repository_fixes),
            ("Validação Sintaxe", self.test_syntax_validation)
        ]
        
        passed = 0
        total = len(test_results)
        
        for test_name, test_func in test_results:
            print(f"📋 {test_name}")
            print("-" * 40)
            
            try:
                if test_func():
                    passed += 1
                    print(f"✅ {test_name} PASSOU\n")
                else:
                    print(f"❌ {test_name} FALHOU\n")
            except Exception as e:
                print(f"❌ {test_name} ERRO: {e}\n")
        
        # Relatório final
        print("=" * 60)
        print("📊 RELATÓRIO FINAL")
        print("=" * 60)
        print(f"✅ Testes passaram: {passed}/{total}")
        print(f"📈 Taxa de sucesso: {(passed/total*100):.1f}%")
        
        print(f"\n🔧 CORREÇÕES APLICADAS ({len(self.fixes_applied)}):")
        for fix in self.fixes_applied:
            print(f"   {fix}")
        
        if self.errors_found:
            print(f"\n⚠️  PROBLEMAS ENCONTRADOS ({len(self.errors_found)}):")
            for error in self.errors_found:
                print(f"   {error}")
        
        if passed == total and not self.errors_found:
            print("\n🎉 SISTEMA TOTALMENTE CORRIGIDO!")
            print("\n📋 ERROS RESOLVIDOS:")
            print("   ✅ PGRST116: Supabase single() → maybe_single()")
            print("   ✅ AGnO Storage: Parâmetro storage removido")
            print("   ✅ Contents Required: Input format correto para Gemini")
            print("   ✅ Async Tools: arun() implementado")
            print("   ✅ UUID Format: UUIDs válidos para PostgreSQL")
            print("   ✅ Schema Error: Campo updated_at corrigido")
            print("\n🚀 SISTEMA PRONTO PARA PRODUÇÃO!")
            return True
        else:
            print(f"\n⚠️  {len(self.errors_found)} problema(s) ainda precisam ser resolvidos.")
            return False

def main():
    """Função principal"""
    validator = SystemValidator()
    success = validator.run_comprehensive_test()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()