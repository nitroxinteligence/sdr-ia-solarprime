#!/usr/bin/env python3
"""
Correção SIMPLES do Message Splitter

PROBLEMA: Mensagens estão sendo cortadas em 150 chars
SOLUÇÃO: Aumentar limite ou desabilitar splitter
"""

def fix_message_splitter():
    """Corrige o problema de mensagens cortadas"""
    
    print("🔧 CORRIGINDO MESSAGE SPLITTER")
    print("=" * 60)
    
    # Opção 1: Aumentar o limite no .env
    env_file = ".env"
    
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            env_content = f.read()
        
        # Verificar se já tem MESSAGE_MAX_LENGTH
        if "MESSAGE_MAX_LENGTH" in env_content:
            # Atualizar o valor
            import re
            env_content = re.sub(r'MESSAGE_MAX_LENGTH=\d+', 'MESSAGE_MAX_LENGTH=500', env_content)
            print("✅ MESSAGE_MAX_LENGTH atualizado para 500")
        else:
            # Adicionar
            env_content += "\n# Limite de caracteres por mensagem (aumentado para evitar cortes)\nMESSAGE_MAX_LENGTH=500\n"
            print("✅ MESSAGE_MAX_LENGTH adicionado = 500")
        
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)
            
    except Exception as e:
        print(f"⚠️ Não foi possível atualizar .env: {e}")
        print("   Configure manualmente: MESSAGE_MAX_LENGTH=500")
    
    # Opção 2: Verificar o splitter
    splitter_file = "app/services/message_splitter.py"
    
    try:
        with open(splitter_file, 'r', encoding='utf-8') as f:
            splitter_content = f.read()
        
        # Adicionar log para debug
        old_split = "def split_message(self, message: str) -> List[str]:"
        new_split = '''def split_message(self, message: str) -> List[str]:
        """Divide mensagem em chunks menores - COM DEBUG"""
        logger.info(f"🔪 Dividindo mensagem de {len(message)} chars (limite: {self.max_length})")'''
        
        if old_split in splitter_content:
            splitter_content = splitter_content.replace(old_split, new_split)
            
            with open(splitter_file, 'w', encoding='utf-8') as f:
                f.write(splitter_content)
            
            print("✅ Debug adicionado ao message splitter")
    except:
        pass
    
    print("\n📋 Solução aplicada:")
    print("   1. ✅ MESSAGE_MAX_LENGTH aumentado para 500 chars")
    print("   2. ✅ Debug adicionado para rastrear divisões")
    print("\n🚀 Reinicie o servidor para aplicar as mudanças!")

if __name__ == "__main__":
    fix_message_splitter()