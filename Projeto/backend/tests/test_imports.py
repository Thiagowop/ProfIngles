#!/usr/bin/env python3
"""
Simple test to check Kokoro TTS import
"""
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

print("🔄 Testing Kokoro TTS import...")

try:
    from kokoro_neural_tts import KokoroTTS
    print("✅ KokoroTTS imported successfully")
    
    # Test initialization
    kokoro = KokoroTTS(lang_code='a', default_voice='am_michael')
    print(f"✅ KokoroTTS initialized - Available: {kokoro.available}")
    
    if hasattr(kokoro, 'get_info'):
        info = kokoro.get_info()
        print(f"📊 Kokoro info: {info}")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Initialization error: {e}")

print("\n🔄 Testing coqui_tts import...")
try:
    from coqui_tts import CoquiTTS
    print("✅ CoquiTTS imported successfully")
    
    # Test initialization  
    coqui = CoquiTTS()
    print(f"✅ CoquiTTS initialized - Available: {coqui.available}")
    
except ImportError as e:
    print(f"❌ Coqui import error: {e}")
except Exception as e:
    print(f"❌ Coqui initialization error: {e}")
