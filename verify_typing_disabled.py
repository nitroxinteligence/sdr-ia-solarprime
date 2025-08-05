#!/usr/bin/env python3
"""
Script de verificação para garantir que o typing está completamente desabilitado
"""

import sys
from colorama import init, Fore, Style

# Inicializar colorama
init(autoreset=True)

def check_typing_configuration():
    """Verifica se todas as configurações de typing estão corretas"""
    print(f"\n{Fore.CYAN}=== VERIFICANDO CONFIGURAÇÃO DE TYPING ==={Style.RESET_ALL}\n")
    
    errors = []
    warnings = []
    success = []
    
    # 1. Verificar configuração principal
    try:
        from app.config import settings
        
        # Verificar enable_typing_simulation
        if hasattr(settings, 'enable_typing_simulation'):
            if settings.enable_typing_simulation == False:
                success.append("✅ enable_typing_simulation está DESABILITADO")
            else:
                errors.append("❌ enable_typing_simulation está HABILITADO - DEVE SER false!")
        else:
            errors.append("❌ enable_typing_simulation não encontrado no settings!")
            
        # Verificar simulate_reading_time
        if settings.simulate_reading_time == False:
            success.append("✅ simulate_reading_time está DESABILITADO")
        else:
            warnings.append("⚠️  simulate_reading_time está HABILITADO")
            
    except Exception as e:
        errors.append(f"❌ Erro ao importar settings: {e}")
    
    # 2. Verificar arquivo .env
    try:
        with open('.env', 'r') as f:
            env_content = f.read()
            
        if 'ENABLE_TYPING_SIMULATION=false' in env_content:
            success.append("✅ ENABLE_TYPING_SIMULATION=false encontrado no .env")
        elif 'ENABLE_TYPING_SIMULATION=true' in env_content:
            errors.append("❌ ENABLE_TYPING_SIMULATION=true no .env - DEVE SER false!")
        else:
            warnings.append("⚠️  ENABLE_TYPING_SIMULATION não encontrado no .env")
            
        if 'SIMULATE_READING_TIME=false' in env_content:
            success.append("✅ SIMULATE_READING_TIME=false encontrado no .env")
        elif 'SIMULATE_READING_TIME=true' in env_content:
            warnings.append("⚠️  SIMULATE_READING_TIME=true no .env")
            
    except FileNotFoundError:
        warnings.append("⚠️  Arquivo .env não encontrado")
    except Exception as e:
        errors.append(f"❌ Erro ao ler .env: {e}")
    
    # 3. Verificar implementação do send_typing
    try:
        import inspect
        from app.integrations.evolution import EvolutionAPI
        
        # Verificar se send_typing tem a verificação
        source = inspect.getsource(EvolutionAPI.send_typing)
        if 'enable_typing_simulation' in source:
            success.append("✅ send_typing verifica enable_typing_simulation")
        else:
            errors.append("❌ send_typing NÃO verifica enable_typing_simulation!")
            
    except Exception as e:
        warnings.append(f"⚠️  Não foi possível verificar send_typing: {e}")
    
    # Exibir resultados
    print(f"{Fore.GREEN}SUCESSOS ({len(success)}):{Style.RESET_ALL}")
    for s in success:
        print(f"  {s}")
    
    if warnings:
        print(f"\n{Fore.YELLOW}AVISOS ({len(warnings)}):{Style.RESET_ALL}")
        for w in warnings:
            print(f"  {w}")
    
    if errors:
        print(f"\n{Fore.RED}ERROS ({len(errors)}):{Style.RESET_ALL}")
        for e in errors:
            print(f"  {e}")
    
    # Resumo final
    print(f"\n{Fore.CYAN}=== RESUMO ==={Style.RESET_ALL}")
    if not errors:
        print(f"{Fore.GREEN}✅ TYPING ESTÁ COMPLETAMENTE DESABILITADO!{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Todas as verificações passaram com sucesso.{Style.RESET_ALL}")
        return True
    else:
        print(f"{Fore.RED}❌ PROBLEMAS ENCONTRADOS!{Style.RESET_ALL}")
        print(f"{Fore.RED}Corrija os erros acima antes de fazer deploy.{Style.RESET_ALL}")
        return False

def test_typing_behavior():
    """Testa o comportamento real do typing"""
    print(f"\n{Fore.CYAN}=== TESTANDO COMPORTAMENTO DO TYPING ==={Style.RESET_ALL}\n")
    
    try:
        from app.integrations.evolution import EvolutionAPI
        from app.config import settings
        import asyncio
        
        async def test():
            evolution = EvolutionAPI()
            
            # Teste 1: Verificar se send_typing retorna imediatamente
            print("Testando send_typing...")
            start_time = asyncio.get_event_loop().time()
            await evolution.send_typing("5511999999999", 100)
            end_time = asyncio.get_event_loop().time()
            elapsed = end_time - start_time
            
            if elapsed < 0.1:  # Menos de 100ms = retornou imediatamente
                print(f"{Fore.GREEN}✅ send_typing retornou imediatamente ({elapsed:.3f}s){Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}❌ send_typing demorou {elapsed:.3f}s - typing ainda ativo!{Style.RESET_ALL}")
                
            return elapsed < 0.1
            
        # Executar teste
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(test())
        loop.close()
        
        return result
        
    except Exception as e:
        print(f"{Fore.RED}❌ Erro no teste: {e}{Style.RESET_ALL}")
        return False

if __name__ == "__main__":
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}VERIFICADOR DE DESABILITAÇÃO DO TYPING{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    
    # Executar verificações
    config_ok = check_typing_configuration()
    behavior_ok = test_typing_behavior()
    
    # Resultado final
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    if config_ok and behavior_ok:
        print(f"{Fore.GREEN}✅ SISTEMA PRONTO PARA DEPLOY SEM TYPING!{Style.RESET_ALL}")
        sys.exit(0)
    else:
        print(f"{Fore.RED}❌ CORRIJA OS PROBLEMAS ANTES DO DEPLOY!{Style.RESET_ALL}")
        sys.exit(1)