#!/usr/bin/env python3
"""
Test TTS Manager directly
"""
import logging
from tts_manager import TTSManager

# Configure logging
logging.basicConfig(level=logging.INFO)

# Create TTS manager instance
tts_manager = TTSManager()

# Print available engines
print("\n=== TTS MANAGER ENGINES ===")
print(f"Current engine: {tts_manager.current_engine}")
engines = tts_manager.engines
print(f"Total engines: {len(engines)}")

# Display all engines
print("\n=== ALL ENGINES ===")
for name, engine in engines.items():
    info = engine.get_info()
    print(f"{name}: {info.get('name', 'Unknown')}")

# Display Kokoro engines specifically
print("\n=== KOKORO ENGINES ===")
kokoro_engines = {name: engine for name, engine in engines.items() if name.startswith('kokoro_')}
for name, engine in kokoro_engines.items():
    info = engine.get_info()
    print(f"{name}: {info.get('name', 'Unknown')}")
    print(f"  - Default voice: {info.get('default_voice', 'Unknown')}")
    print(f"  - Language: {info.get('language', 'Unknown')} (code: {info.get('lang_code', 'Unknown')})")
    print(f"  - Available voices: {info.get('available_voices', {})}")
    print("")

# Test specific voices
for engine_name in kokoro_engines:
    engine = kokoro_engines[engine_name]
    print(f"\nTesting engine: {engine_name}")
    available_voices = engine.get_info().get('available_voices', {})
    print(f"Available voices by gender: {available_voices}")
    
    # Flatten the voice list
    all_voices = []
    for gender_voices in available_voices.values():
        all_voices.extend(gender_voices)
    
    print(f"All available voices: {all_voices}")
    print("---")
