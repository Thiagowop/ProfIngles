#!/usr/bin/env python3
"""
Test script to verify TTS engine and voice naming
"""
import asyncio
import json
import sys
import logging
from tts_manager import tts_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_tts_engines():
    """Test TTS engines and display their names"""
    print("===== TTS ENGINES NAME TEST =====")
    
    # Get all available engines
    all_engines = tts_manager.get_available_engines()
    print(f"Available engines: {len(all_engines)}")
    
    # Print engine details
    print("\n===== ALL ENGINES =====")
    for name, info in all_engines.items():
        print(f"Engine: {name}")
        print(f"  Display Name: {info.get('name', 'Unknown')}")
        print(f"  Type: {info.get('type', 'Unknown')}")
        if "default_voice" in info:
            print(f"  Default Voice: {info.get('default_voice', 'Default')}")
        print("  --------")
    
    # Get Kokoro-specific engines
    kokoro_engines = tts_manager.get_kokoro_engines()
    print("\n===== KOKORO ENGINES =====")
    for name, info in kokoro_engines.items():
        print(f"Kokoro Engine: {name}")
        print(f"  Display Name: {info.get('name', 'Unknown')}")
        lang = info.get('language', 'Unknown')
        print(f"  Language: {lang}")
        if "default_voice" in info:
            print(f"  Default Voice: {info.get('default_voice', 'Default')}")
        if "available_voices" in info:
            print("  Available Voices:")
            for gender, voices in info.get("available_voices", {}).items():
                print(f"    {gender.capitalize()}: {', '.join(voices[:3])}{'...' if len(voices) > 3 else ''}")
        print("  --------")

if __name__ == "__main__":
    print(f"Python {sys.version.split()[0]}")
    asyncio.run(test_tts_engines())
    print("\nTest completed!")
