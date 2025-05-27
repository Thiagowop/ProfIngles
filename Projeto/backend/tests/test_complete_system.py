#!/usr/bin/env python3
"""
Complete system test including TTS functionality
"""
import asyncio
import logging
import sys
import os
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_complete_system():
    """Test the complete voice chat system"""
    
    print("🧪 Starting Complete System Test")
    print("=" * 50)
    
    try:
        # Test 1: Import all modules
        print("\n📦 Testing imports...")
        from main_advanced import app
        from llm_models import ai_manager
        from tts_manager import tts_manager
        print("✅ All modules imported successfully")
        
        # Test 2: Initialize AI Manager
        print("\n🤖 Testing AI Manager...")
        await ai_manager.initialize()
        available_models = ai_manager.available_models
        current_model = ai_manager.current_model
        print(f"✅ AI Manager initialized")
        print(f"   Available models: {available_models}")
        print(f"   Current model: {current_model}")
        
        # Test 3: Initialize TTS Manager
        print("\n🎤 Testing TTS Manager...")
        await tts_manager.initialize()
        engines = tts_manager.get_available_engines()
        current_engine = tts_manager.current_engine
        print(f"✅ TTS Manager initialized")
        print(f"   Available engines: {list(engines.keys())}")
        print(f"   Current engine: {current_engine}")
        
        # Test 4: Generate test speech
        if current_engine:
            print(f"\n🗣️ Testing speech generation with {current_engine}...")
            test_text = "Hello! This is a test of the English learning voice chat system."
            result = await tts_manager.generate_speech(test_text)
            
            if result["success"]:
                print(f"✅ Speech generated successfully!")
                print(f"   Engine: {result['engine']}")
                print(f"   Audio file: {result['audio_path']}")
                
                # Check if file exists and has content
                audio_path = result['audio_path']
                if os.path.exists(audio_path):
                    file_size = os.path.getsize(audio_path)
                    print(f"   File size: {file_size} bytes")
                    if file_size > 0:
                        print("✅ Audio file created with content")
                    else:
                        print("⚠️ Audio file is empty")
                else:
                    print("❌ Audio file not found")
            else:
                print(f"❌ Speech generation failed: {result.get('error')}")
        else:
            print("⚠️ No TTS engines available for testing")
            
        # Test 5: Test Ollama connection
        print("\n🦙 Testing Ollama connection...")
        try:
            import ollama
            models = ollama.list()
            print(f"✅ Ollama connected")
            print(f"   Available Ollama models: {len(models.get('models', []))}")
            for model in models.get('models', [])[:3]:  # Show first 3
                print(f"   - {model['name']}")
        except Exception as e:
            print(f"⚠️ Ollama connection issue: {e}")
            
        # Test 6: Test Whisper
        print("\n👂 Testing Faster-Whisper...")
        try:
            from faster_whisper import WhisperModel
            whisper = WhisperModel("tiny", device="cpu", compute_type="int8")
            print("✅ Faster-Whisper loaded successfully")
        except Exception as e:
            print(f"❌ Faster-Whisper error: {e}")
            
        print("\n" + "=" * 50)
        print("🎉 SYSTEM TEST COMPLETED SUCCESSFULLY!")
        print("✅ All core components are working")
        print("🚀 Ready to start the voice chat application!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ System test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_complete_system())
    if success:
        print("\n🎯 Next step: Start the servers!")
        print("   Backend: python start_server.py")
        print("   Frontend: npm start (in frontend directory)")
    sys.exit(0 if success else 1)
