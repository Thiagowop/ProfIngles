#!/usr/bin/env python3
"""
Teste do Kokoro TTS Engine
Este script testa se o Kokoro TTS está funcionando corretamente
"""

import sys
import os
import numpy as np
import tempfile
import wave

# Adicionar o diretório backend ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_kokoro_tts():
    """Testa o Kokoro TTS Engine"""
    print("🔧 Testando Kokoro TTS Engine...")
    
    try:
        # Importar o Kokoro TTS
        from kokoro_tts import get_tts_engine
        
        # Inicializar o engine
        tts = get_tts_engine()
        print(f"✅ Kokoro TTS inicializado com sucesso!")
        print(f"🎵 Sample Rate: {tts.sample_rate} Hz")
        print(f"🔧 Available: {tts.available}")
        
        # Testar síntese de texto
        test_text = "Hello! This is a test of the Kokoro TTS engine."
        print(f"\n🎤 Sintetizando: '{test_text}'")
        
        audio_data = tts.synthesize(test_text)
        
        if audio_data is not None and len(audio_data) > 0:
            print(f"✅ Áudio sintetizado com sucesso!")
            print(f"📊 Tamanho do áudio: {len(audio_data)} samples")
            print(f"⏱️ Duração: {len(audio_data) / tts.sample_rate:.2f} segundos")
            print(f"🔊 Range do áudio: {np.min(audio_data):.3f} a {np.max(audio_data):.3f}")
            
            # Salvar áudio de teste
            test_file = "test_kokoro_output.wav"
            with wave.open(test_file, 'wb') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(tts.sample_rate)
                
                # Converter para int16
                audio_int16 = (audio_data * 32767).astype(np.int16)
                wav_file.writeframes(audio_int16.tobytes())
            
            print(f"💾 Áudio salvo como: {test_file}")
            
            # Obter informações do engine
            info = tts.get_info()
            print(f"\n📋 Informações do Engine:")
            for key, value in info.items():
                print(f"   {key}: {value}")
            
            return True
            
        else:
            print("❌ Falha na síntese de áudio")
            return False
            
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def test_dependencies():
    """Testa se todas as dependências estão instaladas"""
    print("🔍 Verificando dependências...")
    
    required_modules = [
        'torch',
        'numpy', 
        'soundfile',
        'scipy'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module} - NÃO ENCONTRADO")
            missing_modules.append(module)
    
    if missing_modules:
        print(f"\n⚠️ Módulos faltando: {', '.join(missing_modules)}")
        print("💡 Execute: pip install " + " ".join(missing_modules))
        return False
    else:
        print("✅ Todas as dependências estão instaladas!")
        return True

if __name__ == "__main__":
    print("🚀 Iniciando teste do Kokoro TTS Engine")
    print("=" * 50)
    
    # Testar dependências primeiro
    if test_dependencies():
        print("\n" + "=" * 50)
        # Testar o TTS
        success = test_kokoro_tts()
        
        print("\n" + "=" * 50)
        if success:
            print("🎉 Teste do Kokoro TTS: SUCESSO!")
        else:
            print("💥 Teste do Kokoro TTS: FALHOU!")
    else:
        print("💥 Dependências faltando - não é possível testar o TTS")
