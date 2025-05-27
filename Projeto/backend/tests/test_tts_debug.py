#!/usr/bin/env python3
"""
Debug script to test TTS Manager initialization
"""
import sys
import asyncio
import logging

# Configure logging to see debug info
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

sys.path.append('.')
from tts_manager import TTSManager

async def test_tts_manager():
    print("🔄 Testing TTS Manager initialization...")
    try:
        manager = TTSManager()
        await manager.initialize()
        
        print(f"\n📊 Available engines: {list(manager.engines.keys())}")
        print(f"🎯 Current engine: {manager.current_engine}")
        
        engines_info = manager.get_available_engines()
        print(f"\n📋 Engine details:")
        for name, info in engines_info.items():
            print(f"  - {name}: {info.get('name', 'Unknown')} - Available: {info.get('available', False)}")
        
        # Test Kokoro engines specifically
        print(f"\n🎌 Kokoro engines:")
        try:
            kokoro_engines = manager.get_kokoro_engines()
            for name, info in kokoro_engines.items():
                print(f"  - {name}: {info.get('name', 'Unknown')} - Lang: {info.get('lang_code', 'N/A')}")
        except Exception as e:
            print(f"❌ Error getting Kokoro engines: {e}")
        
        return manager
    except Exception as e:
        print(f"❌ Error initializing TTS Manager: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    asyncio.run(test_tts_manager())
