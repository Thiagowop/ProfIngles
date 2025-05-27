#!/usr/bin/env python3
"""
Teste simples do TTS Manager corrigido
"""

try:
    print("Tentando importar o módulo...")
    import tts_manager
    print("Módulo importado com sucesso!")
    
    print("Tentando importar a classe TTSManager...")
    from tts_manager import TTSManager
    print("Classe TTSManager importada com sucesso!")
    
    print("Criando instância do TTSManager...")
    manager = TTSManager()
    print("TTSManager criado com sucesso!")
    
    print("✅ TESTE CONCLUÍDO COM SUCESSO!")
    
except Exception as e:
    print(f"❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
