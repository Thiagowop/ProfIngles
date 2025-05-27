#!/usr/bin/env python3
"""
Kokoro TTS Engine Implementation
Real neural text-to-speech using kokoro-onnx
"""

import os
import logging
import numpy as np
from typing import Optional
import warnings

# Suppress warnings
warnings.filterwarnings("ignore", category=UserWarning)

logger = logging.getLogger(__name__)

# Check if kokoro-onnx is available
try:
    from kokoro_onnx import Kokoro
    KOKORO_AVAILABLE = True
    logger.info("✅ kokoro-onnx disponível")
except ImportError:
    KOKORO_AVAILABLE = False
    logger.warning("⚠️ kokoro-onnx não disponível")

class KokoroTTS:
    """Real Kokoro TTS using kokoro-onnx neural model"""
    
    def __init__(self):
        self.sample_rate = 24000  # Kokoro TTS sample rate
        self.model = None
        self.available = False
        
        if KOKORO_AVAILABLE:
            try:
                # Initialize Kokoro model
                self.model = Kokoro()
                self.available = True
                logger.info("✅ Kokoro TTS neural model inicializado")
            except Exception as e:
                logger.error(f"❌ Erro ao inicializar Kokoro TTS: {e}")
                self.available = False
        else:
            logger.warning("⚠️ Kokoro TTS não disponível")
    
    def synthesize(self, text: str, voice: str = "default") -> Optional[np.ndarray]:
        """Synthesize text to speech using Kokoro neural TTS model"""
        if not self.available or not self.model:
            logger.warning("Kokoro TTS não está disponível")
            return None
            
        try:
            # Clean text
            text = text.strip()
            if not text:
                return None
                
            logger.info(f"🎤 Sintetizando: '{text[:50]}...'")
            
            # Generate audio using Kokoro
            audio_samples = self.model.create(text)
            
            if audio_samples is None or len(audio_samples) == 0:
                logger.warning("Kokoro TTS retornou áudio vazio")
                return None
                
            # Convert to numpy array and normalize
            audio = np.array(audio_samples, dtype=np.float32)
            
            # Normalize to prevent clipping
            if np.max(np.abs(audio)) > 0:
                audio = audio / np.max(np.abs(audio)) * 0.8
            
            logger.info(f"✅ Áudio gerado: {len(audio)} samples, {len(audio)/self.sample_rate:.2f}s")
            return audio
            
        except Exception as e:
            logger.error(f"❌ Erro na síntese Kokoro TTS: {e}")
            return None
    
    def get_info(self) -> dict:
        """Return information about the TTS engine"""
        return {
            "name": "Kokoro TTS",
            "type": "neural",
            "available": self.available,
            "features": ["High quality", "Neural synthesis", "Natural voice"]
        }

class FallbackTTS:
    """Simple fallback TTS using basic synthesis"""
    
    def __init__(self):
        self.sample_rate = 22050
        self.available = True
        logger.warning("⚠️ Usando TTS fallback - qualidade limitada")
    
    def synthesize(self, text: str, voice: str = "default") -> np.ndarray:
        """Simple synthesis for fallback"""
        try:
            words = len(text.split())
            duration = max(1.0, words * 0.5)
            t = np.linspace(0, duration, int(self.sample_rate * duration))
            
            # Simple tone generation
            freq = 150 if voice == "male" else 200
            audio = 0.3 * np.sin(2 * np.pi * freq * t)
            
            # Simple envelope
            fade_samples = int(0.1 * self.sample_rate)
            envelope = np.ones_like(audio)
            envelope[:fade_samples] = np.linspace(0, 1, fade_samples)
            envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)
            
            audio *= envelope
            return audio.astype(np.float32)
            
        except Exception as e:
            logger.error(f"Erro no TTS fallback: {e}")
            return np.zeros(int(self.sample_rate), dtype=np.float32)
    
    def get_info(self) -> dict:
        return {
            "name": "Fallback TTS",
            "type": "synthetic",
            "available": True,
            "features": ["Basic synthesis", "Fallback only"]
        }

def get_tts_engine():
    """Get the best available TTS engine"""
    if KOKORO_AVAILABLE:
        kokoro = KokoroTTS()
        if kokoro.available:
            return kokoro
    
    logger.warning("Kokoro TTS não disponível, usando fallback")
    return FallbackTTS()

# Main initialization
if __name__ == "__main__":
    print("🚀 Testando Kokoro TTS Engine")
    tts = get_tts_engine()
    print(f"Engine: {tts.get_info()}")
    
    # Test synthesis
    audio = tts.synthesize("Hello world!")
    if audio is not None:
        print(f"✅ Síntese bem-sucedida: {len(audio)} samples")
    else:
        print("❌ Falha na síntese")
