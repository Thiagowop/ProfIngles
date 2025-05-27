#!/usr/bin/env python3
"""
Kokoro TTS Engine Implementation - REAL NEURAL VERSION
Real neural text-to-speech using kokoro library
"""

import os
import logging
import numpy as np
import torch  # Added for PyTorch tensor handling
from typing import Optional
import warnings

# Suppress warnings
warnings.filterwarnings("ignore", category=UserWarning)

# Disable Japanese support since MeCab isn't properly installed
os.environ['KOKORO_DISABLE_JAPANESE'] = '1'

logger = logging.getLogger(__name__)

# Check if kokoro is available
try:
    from kokoro import KPipeline
    KOKORO_AVAILABLE = True
    logger.info("✅ kokoro disponível")
except ImportError:
    KOKORO_AVAILABLE = False
    logger.warning("⚠️ kokoro não disponível")

# Optional scipy for audio file saving
try:
    from scipy.io import wavfile
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

class KokoroTTS:
    """Real Kokoro TTS using kokoro neural model with all quality improvements"""
    
    # Best voices per language based on quality grades
    BEST_VOICES = {
        'american_english': {
            'female': ['af_bella', 'af_heart', 'af_nicole', 'af_aoede'],  # A-, A, B-, C+
            'male': ['am_fenrir', 'am_michael', 'am_puck']  # C+, C+, C+
        },
        'british_english': {
            'female': ['bf_emma', 'bf_isabella'],  # B-, C
            'male': ['bm_fable', 'bm_george']  # C, C
        },
        'portuguese_brazil': {
            'female': ['pf_dora'],  # Brazilian Portuguese female
            'male': ['pm_alex', 'pm_santa']  # Brazilian Portuguese males
        }
    }

    # Map internal voice codes to display names
    VOICE_MAP = {
        # American English
        'af_bella': 'EN-US Bella',
        'af_heart': 'EN-US Heart',
        'af_nicole': 'EN-US Nicole',
        'af_aoede': 'EN-US Aoede',
        'am_fenrir': 'EN-US Fenrir',
        'am_michael': 'EN-US Michael',
        'am_puck': 'EN-US Puck',
        # British English
        'bf_emma': 'EN-GB Emma',
        'bf_isabella': 'EN-GB Isabella',
        'bm_fable': 'EN-GB Fable',
        'bm_george': 'EN-GB George',
        'bm_lewis': 'EN-GB Lewis',
        # Portuguese
        'pf_dora': 'PT-BR Dora',
        'pm_alex': 'PT-BR Alex',
        'pm_santa': 'PT-BR Santa'
    }
    
    # Reverse mapping for synthesis
    DISPLAY_TO_INTERNAL = {v: k for k, v in VOICE_MAP.items()}
    
    def __init__(self, lang_code='a', default_voice=None):
        self.sample_rate = 24000  # Kokoro TTS sample rate
        self.model = None
        self.available = False
        self.lang_code = lang_code
        
        # Ensure lang_code is valid (remove 'j' option)
        if lang_code not in ['a', 'b', 'p']:
            self.lang_code = 'a'  # Default to American English
        
        # Set default voice
        if default_voice:
            # Convert from display name to internal if needed
            if default_voice in self.DISPLAY_TO_INTERNAL:
                self.default_voice = self.DISPLAY_TO_INTERNAL[default_voice]
            else:
                self.default_voice = default_voice
        else:
            self.default_voice = self._get_best_voice()
            
        # Convert default voice to display name for logs
        display_voice = self.VOICE_MAP.get(self.default_voice, self.default_voice)
        
        if KOKORO_AVAILABLE:
            try:
                # Initialize Kokoro model using KPipeline with specified language
                self.model = KPipeline(lang_code=self.lang_code)
                self.available = True
                logger.info(f"✅ Kokoro TTS neural model inicializado com lang_code='{self.lang_code}', voz padrão='{display_voice}'")
            except Exception as e:
                logger.error(f"❌ Erro ao inicializar Kokoro TTS: {e}")
                self.available = False
        else:
            logger.warning("⚠️ Kokoro TTS não disponível")
    
    def _get_best_voice(self):
        """Get the best available voice for the current language using dictionary lookup"""
        voice_map = {
            'a': 'af_bella',  # American English - Grade A- female voice
            'b': 'bf_emma',   # British English - Grade B- female voice
            'p': 'pf_dora'    # Portuguese (Brazil) - Brazilian Portuguese female voice
        }
        return voice_map.get(self.lang_code, 'af_heart')  # Fallback to high-quality American voice
    
    def get_available_voices(self):
        """Get list of available voices for current language with display names"""
        # Get internal voices first
        internal_voices = {}
        if self.lang_code == 'a':
            internal_voices = {
                'female': self.BEST_VOICES['american_english']['female'],
                'male': self.BEST_VOICES['american_english']['male']
            }
        elif self.lang_code == 'b':
            internal_voices = {
                'female': self.BEST_VOICES['british_english']['female'],
                'male': self.BEST_VOICES['british_english']['male']
            }
        elif self.lang_code == 'p':
            internal_voices = {
                'female': self.BEST_VOICES['portuguese_brazil']['female'],
                'male': self.BEST_VOICES['portuguese_brazil']['male']
            }
        else:
            internal_voices = {'female': ['af_heart'], 'male': ['am_fenrir']}
            
        # Convert to display names
        display_voices = {}
        for gender, voices in internal_voices.items():
            display_voices[gender] = [self.VOICE_MAP.get(voice, voice) for voice in voices]
            
        return display_voices
    
    def synthesize(self, text: str, voice: str = "default", save_file: Optional[str] = None) -> Optional[np.ndarray]:
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
            
            # Configure voice
            if voice == "default":
                voice_param = self.default_voice
            elif voice in ["female", "male"]:
                # Select best voice for gender
                available = self.get_available_voices()
                voices = available.get(voice, [])
                
                # Get first voice and convert to internal name if needed
                if voices:
                    display_voice = voices[0]
                    voice_param = self.DISPLAY_TO_INTERNAL.get(display_voice, display_voice)
                else:
                    voice_param = self.default_voice
            else:
                # If voice is a display name, convert to internal
                voice_param = self.DISPLAY_TO_INTERNAL.get(voice, voice)
            
            # Log using display name
            display_voice = self.VOICE_MAP.get(voice_param, voice_param)
            logger.info(f"🎭 Usando voz: {display_voice}")
            
            # Generate audio using Kokoro KPipeline
            results = list(self.model(text, voice=voice_param))
            
            if not results:
                logger.warning("Kokoro TTS não retornou resultados")
                return None
                
            # Extract audio from results and concatenate
            audio_chunks = []
            for result in results:
                if hasattr(result, 'output') and hasattr(result.output, 'audio'):
                    # Convert torch tensor to numpy if necessary
                    audio_tensor = result.output.audio
                    if hasattr(audio_tensor, 'numpy'):
                        audio_chunk = audio_tensor.numpy()
                    elif hasattr(audio_tensor, 'cpu'):
                        audio_chunk = audio_tensor.cpu().numpy()
                    else:
                        audio_chunk = np.array(audio_tensor)
                    audio_chunks.append(audio_chunk)
            
            if not audio_chunks:
                logger.warning("Nenhum áudio extraído dos resultados")
                return None
                
            # Concatenate all chunks
            audio = np.concatenate(audio_chunks)
              # Ensure proper format
            if audio.dtype != np.float32:
                audio = audio.astype(np.float32)
            
            # Normalize to prevent clipping (optimized to avoid double calculation)
            max_abs = np.max(np.abs(audio))
            if max_abs > 0:
                audio = audio / max_abs * 0.8
            
            # Optional: Save to file
            if save_file and SCIPY_AVAILABLE:
                try:
                    # Convert to 16-bit for WAV file
                    audio_16bit = (audio * 32767).astype(np.int16)
                    wavfile.write(save_file, self.sample_rate, audio_16bit)
                    logger.info(f"💾 Áudio salvo em: {save_file}")
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao salvar áudio: {e}")
            
            logger.info(f"✅ Áudio neural gerado: {len(audio)} samples, {len(audio)/self.sample_rate:.2f}s com voz {display_voice}")
            return audio
            
        except Exception as e:
            logger.error(f"❌ Erro na síntese Kokoro TTS: {e}")
            logger.error(f"Detalhes do erro: {type(e).__name__}: {str(e)}")
            return None

    def get_info(self) -> dict:
        """Return information about the TTS engine"""
        voices = self.get_available_voices()
        
        # Use language name instead of code for better display
        lang_names = {
            'a': 'American English',
            'b': 'British English',
            'p': 'Portuguese Brazilian'
        }
        
        language_name = lang_names.get(self.lang_code, 'Unknown')
        
        # Convert default_voice to display name
        display_default = self.VOICE_MAP.get(self.default_voice, self.default_voice)
        
        # Add voice-specific information to the name
        engine_name = "Kokoro Neural TTS"
        if self.default_voice in ['af_bella']:
            engine_name = "Kokoro Neural TTS (Bella)"
        elif self.default_voice in ['af_heart']:
            engine_name = "Kokoro Neural TTS (Heart)"
        elif self.default_voice in ['am_michael', 'am_fenrir']:
            engine_name = f"Kokoro Neural TTS ({display_default})"
            
        return {
            "name": engine_name,
            "type": "neural",
            "available": self.available,
            "language": language_name,  # Friendly name
            "lang_code": self.lang_code, # Keep code for compatibility
            "default_voice": display_default,
            "voice_id": self.default_voice,  # Add internal voice ID
            "available_voices": voices,
            "features": ["High quality", "Neural synthesis", "Natural voice", "Real Kokoro TTS", "Multiple voices"]
        }

def get_tts_engine(lang_code='a', voice=None):
    """Get the best available TTS engine for specified language"""
    if KOKORO_AVAILABLE:
        kokoro = KokoroTTS(lang_code=lang_code, default_voice=voice)
        if kokoro.available:
            return kokoro
    
    logger.warning("Kokoro TTS não disponível")
    return None

def get_american_english_tts():
    """Get American English Kokoro TTS with best female voice"""
    return get_tts_engine('a', 'EN-US Bella')

def get_british_english_tts():
    """Get British English Kokoro TTS with best female voice"""
    return get_tts_engine('b', 'EN-GB Emma')

def get_portuguese_brazil_tts():
    """Get Brazilian Portuguese Kokoro TTS with best female voice"""
    return get_tts_engine('p', 'PT-BR Dora')

# Main test
if __name__ == "__main__":
    print("🚀 Testando Kokoro NEURAL TTS Engine com Múltiplas Vozes")
    
    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    # Test American English with best voice
    print("\n🇺🇸 Testando American English (EN-US Bella - Grade A-):")
    tts_us = get_american_english_tts()
    if tts_us:
        info = tts_us.get_info()
        print(f"✅ Engine: {info['name']} ({info['type']})")
        print(f"📊 Available: {info['available']}")
        print(f"🎭 Default Voice: {info['default_voice']}")
        print(f"🎯 Features: {', '.join(info['features'])}")
        
        # Test synthesis with best female voice
        test_text = "Hello! This is Kokoro neural text to speech with the highest quality American English voice."
        print(f"\n🎤 Testando síntese com EN-US Bella: '{test_text[:50]}...'")
        
        audio = tts_us.synthesize(test_text, voice="EN-US Bella")
        if audio is not None:
            print(f"✅ SUCESSO! Síntese neural A- completa!")
            print(f"📊 Áudio: {len(audio)} samples, {len(audio)/tts_us.sample_rate:.2f}s")
            print(f"📈 Range: {np.min(audio):.6f} to {np.max(audio):.6f}")
            
            # Test different voices
            print(f"\n🎭 Testando diferentes vozes:")
            for voice in ['EN-US Heart', 'EN-US Nicole', 'EN-US Fenrir']:
                audio_voice = tts_us.synthesize("Testing voice quality.", voice=voice)
                if audio_voice is not None:
                    print(f"✅ Voz {voice}: {len(audio_voice)} samples")
                else:
                    print(f"❌ Falha com voz {voice}")
            
            print("🎉 REAL KOKORO NEURAL TTS ESTÁ FUNCIONANDO PERFEITAMENTE!")
        else:
            print("❌ Falha na síntese neural")
    else:
        print("❌ Kokoro TTS não disponível")
    
    # Test audio file saving if scipy is available
    if SCIPY_AVAILABLE and tts_us:
        print("\n💾 Testando salvamento de arquivo de áudio:")
        test_file = "test_kokoro_neural_output.wav"
        try:
            audio_save = tts_us.synthesize("Testing audio file save feature with neural Kokoro TTS.", save_file=test_file)
            if audio_save is not None and os.path.exists(test_file):
                print(f"✅ Áudio salvo com sucesso em: {test_file}")
                print(f"📊 Tamanho do arquivo: {os.path.getsize(test_file)} bytes")
            else:
                print("❌ Falha ao salvar áudio")
        except Exception as e:
            print(f"⚠️ Erro no teste de salvamento: {e}")
    
    print("\n🎯 TESTE COMPLETO - TODAS AS CORREÇÕES APLICADAS!")
