#!/usr/bin/env python3
"""
Test script for TTS Manager integration with Kokoro Neural TTS
"""

import asyncio
import sys
import os
from tts_manager import TTSManager

async def test_tts_manager():
    print('🧪 Testando TTS Manager com Kokoro Neural integrado...')
    
    try:
        # Initialize manager
        manager = TTSManager()
        await manager.initialize()
        print('✅ TTS Manager inicializado com sucesso!')

        # Show available engines
        engines = manager.get_available_engines()
        print(f'\n🔧 Engines disponíveis: {len(engines)}')
        for name, info in engines.items():
            print(f'   {name}: {info["name"]} ({info["type"]})')

        # Show Kokoro engines specifically
        kokoro_engines = manager.get_kokoro_engines()
        if kokoro_engines:
            print(f'\n🎯 Kokoro Neural Engines: {len(kokoro_engines)}')
            for name, info in kokoro_engines.items():
                lang_name = info.get('language_name', 'Unknown')
                default_voice = info.get('default_voice', 'Unknown')
                print(f'   {name}: {lang_name} - {default_voice}')

        # Test American English
        if 'kokoro_en_us' in engines:
            print('\n🇺🇸 Testando Kokoro American English...')
            result = await manager.generate_speech_with_language(
                'Hello! This is a test of the integrated Kokoro neural TTS system.',
                language='en-US',
                voice='af_bella'
            )
            if result['success']:
                print(f'✅ Sucesso! Arquivo: {result["audio_path"]}')
                file_size = os.path.getsize(result["audio_path"]) if os.path.exists(result["audio_path"]) else 0
                print(f'   Tamanho do arquivo: {file_size} bytes')
            else:
                print(f'❌ Erro: {result["error"]}')

        # Test Portuguese Brazilian
        if 'kokoro_pt_br' in engines:
            print('\n🇧🇷 Testando Kokoro Português Brasileiro...')
            result = await manager.generate_speech_with_language(
                'Olá! Este é um teste do sistema Kokoro neural integrado.',
                language='pt-BR',
                voice='pf_dora'
            )
            if result['success']:
                print(f'✅ Sucesso! Arquivo: {result["audio_path"]}')
                file_size = os.path.getsize(result["audio_path"]) if os.path.exists(result["audio_path"]) else 0
                print(f'   Tamanho do arquivo: {file_size} bytes')
            else:
                print(f'❌ Erro: {result["error"]}')

        # Test engine switching
        print('\n🔄 Testando troca automática de engine...')
        best_engine = manager.switch_to_best_kokoro()
        if best_engine:
            print(f'✅ Melhor engine selecionado: {best_engine}')
        else:
            print('❌ Nenhum engine Kokoro disponível')

        print('\n🏆 Teste do TTS Manager completo!')

    except Exception as e:
        print(f'❌ Erro durante o teste: {str(e)}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(test_tts_manager())
