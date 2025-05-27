import sys
import asyncio
import logging

logging.basicConfig(level=logging.INFO)

async def test_backend():
    try:
        print("🔄 Testing backend imports...")
        
        # Test imports
        from main_advanced import app
        print("✅ FastAPI app imported")
        
        from llm_models import ai_manager
        print("✅ AI manager imported")
        
        from tts_manager import tts_manager
        print("✅ TTS manager imported")
        
        # Test AI manager initialization
        print("🔄 Testing AI manager initialization...")
        await ai_manager.initialize()
        print(f"✅ AI Manager initialized. Available models: {ai_manager.available_models}")
        
        # Test TTS manager initialization
        print("🔄 Testing TTS manager initialization...")
        await tts_manager.initialize()
        engines = tts_manager.get_available_engines()
        print(f"✅ TTS Manager initialized. Available engines: {list(engines.keys())}")
        
        if tts_manager.current_engine:
            print(f"🎯 Current TTS engine: {tts_manager.current_engine}")
            
            # Test speech generation
            test_text = "Hello! Testing TTS functionality."
            print(f"🗣️ Testing speech generation...")
            result = await tts_manager.generate_speech(test_text)
            
            if result["success"]:
                print(f"✅ Speech generated successfully with {result['engine']}!")
                print(f"   Audio file: {result['audio_path']}")
            else:
                print(f"❌ Speech generation failed: {result.get('error')}")
        else:
            print("⚠️ No TTS engines available")
            
        print("✅ Backend testing completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Backend test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_backend())
    sys.exit(0 if success else 1)
