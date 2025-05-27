#!/usr/bin/env python3
"""
Teste Completo do Sistema TTS
Este script testa todos os engines TTS disponíveis
"""

import sys
import os
import asyncio
import logging

# Adicionar o diretório backend ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_all_tts_engines():
    """Testa todos os engines TTS disponíveis"""
    print("🚀 TESTE COMPLETO DO SISTEMA TTS")
    print("=" * 60)
    try:
        # Importar o TTS Manager
        from tts_manager import tts_manager
        
        print(f"🔧 TTS Manager importado")
        
        # Inicializar o TTS Manager (IMPORTANTE!)
        await tts_manager.initialize()
        
        print(f"✅ TTS Manager inicializado")
        print(f"🎯 Engine atual: {tts_manager.current_engine}")
        
        # Listar engines disponíveis
        available_engines = tts_manager.get_available_engines()
        print(f"\n📋 Engines disponíveis: {len(available_engines)}")
        
        for engine_name, info in available_engines.items():
            print(f"   ✅ {engine_name}: {info.get('name', 'Unknown')}")
            print(f"      Tipo: {info.get('type', 'Unknown')}")
            print(f"      Recursos: {', '.join(info.get('features', []))}")
            if 'best_for' in info:
                print(f"      Melhor para: {', '.join(info['best_for'])}")
            print()
        
        if not available_engines:
            print("❌ Nenhum engine TTS disponível!")
            return False
        
        # Texto de teste
        test_text = "Hello! This is a test of the text-to-speech system. How does it sound?"
        
        # Testar cada engine
        results = {}
        
        for engine_name in available_engines.keys():
            print(f"\n🎤 Testando {engine_name}...")
            print("-" * 40)
            
            # Mudar para este engine
            if tts_manager.switch_engine(engine_name):
                print(f"✅ Engine alterado para: {engine_name}")
                
                # Tentar sintetizar
                try:
                    result = await tts_manager.generate_speech(test_text)
                    
                    if result['success']:
                        audio_path = result['audio_path']
                        print(f"✅ Áudio gerado: {audio_path}")
                        
                        # Verificar se o arquivo existe
                        if os.path.exists(audio_path):
                            file_size = os.path.getsize(audio_path)
                            print(f"📁 Tamanho do arquivo: {file_size} bytes")
                            results[engine_name] = {
                                'success': True,
                                'file_path': audio_path,
                                'file_size': file_size
                            }
                        else:
                            print(f"❌ Arquivo não encontrado: {audio_path}")
                            results[engine_name] = {'success': False, 'error': 'File not found'}
                    else:
                        error_msg = result.get('error', 'Unknown error')
                        print(f"❌ Erro na síntese: {error_msg}")
                        results[engine_name] = {'success': False, 'error': error_msg}
                        
                except Exception as e:
                    print(f"❌ Exceção durante teste: {e}")
                    results[engine_name] = {'success': False, 'error': str(e)}
            else:
                print(f"❌ Não foi possível mudar para engine: {engine_name}")
                results[engine_name] = {'success': False, 'error': 'Could not switch engine'}
        
        # Resumo dos resultados
        print("\n" + "=" * 60)
        print("📊 RESUMO DOS TESTES")
        print("=" * 60)
        
        successful_engines = []
        failed_engines = []
        
        for engine_name, result in results.items():
            if result['success']:
                successful_engines.append(engine_name)
                print(f"✅ {engine_name}: SUCESSO")
                if 'file_size' in result:
                    print(f"   📁 Arquivo: {result['file_size']} bytes")
            else:
                failed_engines.append(engine_name)
                print(f"❌ {engine_name}: FALHOU")
                print(f"   💥 Erro: {result.get('error', 'Unknown')}")
        
        print(f"\n🎯 Engines funcionando: {len(successful_engines)}/{len(results)}")
        print(f"✅ Sucessos: {', '.join(successful_engines) if successful_engines else 'Nenhum'}")
        print(f"❌ Falhas: {', '.join(failed_engines) if failed_engines else 'Nenhum'}")
        
        return len(successful_engines) > 0
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

async def test_individual_engines():
    """Testa engines individualmente"""
    print("\n🔍 TESTE INDIVIDUAL DOS ENGINES")
    print("=" * 60)
    
    # Teste Coqui TTS
    print("\n1️⃣ Testando Coqui TTS diretamente...")
    try:
        from coqui_tts import CoquiTTS
        coqui = CoquiTTS()
        
        if coqui.available:
            print("✅ Coqui TTS disponível")
            audio = coqui.synthesize("Testing Coqui TTS directly")
            if audio is not None:
                print(f"✅ Síntese bem-sucedida: {len(audio)} samples")
            else:
                print("❌ Síntese falhou")
        else:
            print("❌ Coqui TTS não disponível")
            
    except Exception as e:
        print(f"❌ Erro no Coqui TTS: {e}")
    
    # Teste Dias TTS
    print("\n2️⃣ Testando Dias TTS diretamente...")
    try:
        import dias_tts
        print("✅ Dias TTS importado com sucesso")
        # Test basic functionality if possible
        print("✅ Dias TTS disponível")
    except Exception as e:
        print(f"❌ Erro no Dias TTS: {e}")
    
    # Teste Kokoro TTS
    print("\n3️⃣ Testando Kokoro TTS diretamente...")
    try:
        from kokoro_tts import KokoroTTS
        kokoro = KokoroTTS()
        
        audio = kokoro.synthesize("Testing Kokoro TTS directly")
        if audio is not None:
            print(f"✅ Kokoro TTS bem-sucedido: {len(audio)} samples")
        else:
            print("❌ Kokoro TTS falhou")
            
    except Exception as e:
        print(f"❌ Erro no Kokoro TTS: {e}")
    
    # Teste pyttsx3
    print("\n4️⃣ Testando pyttsx3 diretamente...")
    try:
        import pyttsx3
        engine = pyttsx3.init()
        print("✅ pyttsx3 disponível")
        
        # Testar se consegue obter vozes
        voices = engine.getProperty('voices')
        print(f"🎤 Vozes disponíveis: {len(voices) if voices else 0}")
        
    except Exception as e:
        print(f"❌ Erro no pyttsx3: {e}")

async def main():
    """Função principal"""
    print("🎯 INICIANDO TESTE COMPLETO DO SISTEMA TTS")
    print("📅 Este teste verificará todos os engines TTS disponíveis")
    print()
    
    # Teste individual dos engines
    await test_individual_engines()
    
    # Teste completo do sistema
    success = await test_all_tts_engines()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 TESTE GERAL: SUCESSO!")
        print("✅ Pelo menos um engine TTS está funcionando")
    else:
        print("💥 TESTE GERAL: FALHOU!")
        print("❌ Nenhum engine TTS está funcionando")
    
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
