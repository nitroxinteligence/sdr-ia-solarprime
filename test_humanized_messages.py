#!/usr/bin/env python3
"""
Test Humanized Messages
======================
Script para testar todas as mensagens humanizadas do sistema
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.messages import (
    HumanizedMessages,
    get_error_message,
    get_fallback_message,
    get_follow_up_message,
    get_greeting,
    get_special_message,
    personalize_message
)


def test_error_messages():
    """Testa mensagens de erro"""
    print("\n=== MENSAGENS DE ERRO TÉCNICO ===")
    for i in range(3):
        print(f"{i+1}. {get_error_message('ERRO_TECNICO')}")
    
    print("\n=== MENSAGENS DE ERRO DE IMAGEM ===")
    for i in range(3):
        print(f"{i+1}. {get_error_message('ERRO_IMAGEM')}")
    
    print("\n=== MENSAGENS DE ERRO DE PDF ===")
    for i in range(3):
        print(f"{i+1}. {get_error_message('ERRO_PDF')}")
    
    print("\n=== MENSAGENS DE ERRO DE ÁUDIO ===")
    for i in range(3):
        print(f"{i+1}. {get_error_message('ERRO_AUDIO')}")


def test_fallback_messages():
    """Testa mensagens fallback por estágio"""
    stages = [
        "INITIAL_CONTACT",
        "IDENTIFICATION", 
        "QUALIFICATION",
        "DISCOVERY",
        "SCHEDULING",
        "NURTURING"
    ]
    
    print("\n=== MENSAGENS FALLBACK POR ESTÁGIO ===")
    for stage in stages:
        print(f"\n{stage}:")
        for i in range(2):
            print(f"  {i+1}. {get_fallback_message(stage, 'João')}")


def test_follow_up_messages():
    """Testa mensagens de follow-up"""
    intervals = ["30_minutos", "24_horas", "48_horas", "7_dias"]
    
    print("\n=== MENSAGENS DE FOLLOW-UP ===")
    for interval in intervals:
        print(f"\n{interval.upper().replace('_', ' ')}:")
        for i in range(2):
            print(f"  {i+1}. {get_follow_up_message(interval, 'Maria')}")


def test_special_situations():
    """Testa mensagens para situações especiais"""
    situations = [
        "multiplas_mensagens",
        "comando_clear",
        "horario_comercial",
        "agradecimento"
    ]
    
    print("\n=== MENSAGENS PARA SITUAÇÕES ESPECIAIS ===")
    for situation in situations:
        print(f"\n{situation.upper().replace('_', ' ')}:")
        for i in range(2):
            print(f"  {i+1}. {get_special_message(situation, 'Carlos')}")


def test_greetings():
    """Testa saudações baseadas em horário"""
    print("\n=== SAUDAÇÕES ===")
    for i in range(5):
        print(f"{i+1}. {get_greeting()}")


def test_personalized_errors():
    """Testa mensagens de erro personalizadas"""
    print("\n=== MENSAGENS DE ERRO PERSONALIZADAS ===")
    
    # Teste com nome
    print("\nCom nome 'Ana':")
    for i in range(3):
        print(f"{i+1}. {personalize_message('ERRO_TECNICO', 'Ana')}")
    
    # Teste sem nome  
    print("\nSem nome:")
    for i in range(3):
        print(f"{i+1}. {personalize_message('ERRO_IMAGEM')}")


def test_message_variations():
    """Testa se há variação nas mensagens"""
    print("\n=== TESTE DE VARIAÇÃO (10 mensagens) ===")
    
    print("\nVariação em ERRO_TECNICO:")
    messages = [get_error_message('ERRO_TECNICO') for _ in range(10)]
    unique_messages = set(messages)
    print(f"Total de mensagens únicas: {len(unique_messages)} de 10")
    for msg in unique_messages:
        print(f"  - {msg}")
    
    print("\nVariação em FOLLOW-UP 30 minutos:")
    messages = [get_follow_up_message('30_minutos', 'Pedro') for _ in range(10)]
    unique_messages = set(messages)
    print(f"Total de mensagens únicas: {len(unique_messages)} de 10")
    for msg in unique_messages:
        print(f"  - {msg}")


def main():
    """Executa todos os testes"""
    print("=" * 60)
    print("TESTE DE MENSAGENS HUMANIZADAS - SDR IA SOLARPRIME")
    print("=" * 60)
    
    test_error_messages()
    test_fallback_messages()
    test_follow_up_messages()
    test_special_situations()
    test_greetings()
    test_personalized_errors()
    test_message_variations()
    
    print("\n" + "=" * 60)
    print("TESTES CONCLUÍDOS!")
    print("=" * 60)


if __name__ == "__main__":
    main()