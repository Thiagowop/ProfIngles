import pyttsx3
import tempfile
import os
import uuid

print("🔄 Testing pyttsx3 TTS...")

try:
    # Initialize pyttsx3
    tts = pyttsx3.init()
    print("✅ pyttsx3 initialized successfully")
    
    # Get available voices
    voices = tts.getProperty('voices')
    print(f"📋 Found {len(voices)} voices:")
    for i, voice in enumerate(voices[:3]):  # Show first 3 voices
        print(f"  {i+1}. {voice.name} ({voice.id})")
    
    # Set properties
    tts.setProperty('rate', 180)
    tts.setProperty('volume', 0.9)
    
    # Generate test audio
    test_text = "Hello! This is a test of the text-to-speech system."
    output_path = os.path.join(tempfile.gettempdir(), f"test_tts_{uuid.uuid4()}.wav")
    
    print(f"🗣️ Generating speech: '{test_text}'")
    print(f"📁 Output path: {output_path}")
    
    tts.save_to_file(test_text, output_path)
    tts.runAndWait()
    
    if os.path.exists(output_path):
        print(f"✅ Audio file created successfully!")
        print(f"   File size: {os.path.getsize(output_path)} bytes")
    else:
        print("❌ Audio file was not created")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
