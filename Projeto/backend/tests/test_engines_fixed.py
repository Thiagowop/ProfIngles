#!/usr/bin/env python3
"""
Test engines after fixes
"""
import asyncio
import sys
sys.path.append('.')
from tts_manager import TTSManager

async def test_engines():
    manager = TTSManager()
    await manager.initialize()
    
    print('=== AVAILABLE ENGINES ===')
    engines = manager.get_available_engines()
    for name, info in engines.items():
        print(f'{name}: {info.get("name", "Unknown")}')
    
    print('\n=== KOKORO ENGINES SPECIFICALLY ===')
    kokoro_engines = manager.get_kokoro_engines()
    for name, info in kokoro_engines.items():
        print(f'{name}: {info.get("name", "Unknown")} - Lang: {info.get("lang_code", "N/A")}')
    
    print(f'\n=== TOTAL ENGINES: {len(engines)} ===')
    print(f'=== KOKORO ENGINES: {len(kokoro_engines)} ===')

asyncio.run(test_engines())
