#!/usr/bin/env python3
"""
Test script for TTS functionality
"""
import asyncio
import pytest
from tts_manager import tts_manager

@pytest.mark.asyncio
async def test_tts():
    print("🔄 Initializing TTS Manager...")
    await tts_manager.initialize()
    
    print("\n📋 Available TTS engines:")
    engines = tts_manager.get_available_engines()
    for name, info in engines.items():
        print(f"  ✅ {name}: {info['name']} ({info['type']})")
    
    if engines:
        print(f"\n🎯 Current engine: {tts_manager.current_engine}")
        
        # Test speech generation
        test_text = "Hello! This is a test of the text-to-speech system."
        print(f"\n🗣️ Testing speech generation with: '{test_text}'")
        
        result = await tts_manager.generate_speech(test_text)
        if result["success"]:
            print(f"✅ Speech generated successfully!")
            print(f"   Audio file: {result['audio_path']}")
            print(f"   Engine used: {result['engine']}")
        else:
            print(f"❌ Speech generation failed: {result.get('error', 'Unknown error')}")
    else:
        print("❌ No TTS engines available!")
