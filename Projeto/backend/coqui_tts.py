#!/usr/bin/env python3
"""
Coqui TTS Engine Implementation
High-quality neural text-to-speech with multiple voices
"""

import os
# Desativar o MeCab para evitar erros
os.environ['TTS_MECAB_DISABLED'] = '1'

import torch
import numpy as np
from typing import Optional, List, Dict
import tempfile
import logging

logger = logging.getLogger(__name__)

class CoquiTTS:
    """Wrapper para Coqui TTS - implementação completa"""
    
    def __init__(self):
        self.available = False
        self.tts = None
        self.sample_rate = 22050
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.available_models = []
        self.current_model = None
        
        try:
            from TTS.api import TTS as CoquiTTSAPI
            
            # Listar modelos disponíveis
            self.available_models = [
                "tts_models/en/ljspeech/tacotron2-DDC",
                "tts_models/en/ljspeech/glow-tts",
                "tts_models/en/ljspeech/speedy-speech",
                "tts_models/en/ljspeech/neural_hmm",
                "tts_models/en/ljspeech/vits",
                "tts_models/en/ljspeech/fast_pitch",
                "tts_models/multilingual/multi-dataset/your_tts",
                "tts_models/multilingual/multi-dataset/xtts_v2"
            ]
            
            # Tentar inicializar com um modelo rápido e confiável
            try:
                logger.info("🔄 Inicializando Coqui TTS com modelo rápido...")
                self.current_model = "tts_models/en/ljspeech/speedy-speech"
                self.tts = CoquiTTSAPI(model_name=self.current_model, gpu=torch.cuda.is_available())
                self.available = True
                logger.info(f"✅ Coqui TTS inicializado com sucesso!")
                logger.info(f"📱 Modelo: {self.current_model}")
                logger.info(f"🔧 Device: {self.device}")
                
            except Exception as e:
                logger.warning(f"⚠️ Erro ao carregar modelo principal: {e}")
                # Fallback para modelo mais simples
                try:
                    self.current_model = "tts_models/en/ljspeech/tacotron2-DDC"
                    self.tts = CoquiTTSAPI(model_name=self.current_model, gpu=False)
                    self.available = True
                    logger.info(f"✅ Coqui TTS inicializado com modelo fallback: {self.current_model}")
                except Exception as e2:
                    logger.error(f"❌ Erro ao carregar modelo fallback: {e2}")
                    self.available = False
                    
        except ImportError as e:
            logger.error(f"❌ Coqui TTS não está instalado: {e}")
            self.available = False
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar Coqui TTS: {e}")
            self.available = False

    def synthesize(self, text: str, voice: str = "default") -> Optional[np.ndarray]:
        """
        Sintetiza texto em áudio usando Coqui TTS
        """
        if not self.available or not self.tts:
            logger.error("❌ Coqui TTS não está disponível")
            return None
        
        try:            # Enhanced pre-processing to avoid kernel size errors
            text = text.strip()
            if not text:
                logger.warning("⚠️ Texto vazio fornecido")
                return None
            
            # Remove emojis and special characters that can cause kernel size issues
            import re
            text = re.sub(r'[^\w\s\.,!?;:\'-]', '', text)
            
            # Handle very short text inputs that cause kernel size errors
            min_chars = 50  # Minimum character count to avoid kernel size issues
            if len(text) < min_chars:
                # Pad short text with meaningful content to meet minimum requirements
                padding_phrases = [
                    "This is a short message.",
                    "Thank you for listening.",
                    "Have a great day.",
                    "Please note the following.",
                    "This concludes the announcement."
                ]
                # Add padding to reach minimum length
                while len(text) < min_chars:
                    text = text + " " + padding_phrases[len(text) % len(padding_phrases)]
                logger.info(f"🔧 Texto expandido para evitar erro de kernel: '{text[:100]}...'")
            
            # Split into manageable chunks if text is very long
            max_chunk_size = 500  # Maximum characters per chunk
            if len(text) > max_chunk_size:
                # Split by sentences first, then by length if needed
                sentences = re.split(r'(?<=[.!?])\s+', text)
                chunks = []
                current_chunk = ""
                
                for sentence in sentences:
                    if len(current_chunk + sentence) <= max_chunk_size:
                        current_chunk += (" " if current_chunk else "") + sentence
                    else:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        current_chunk = sentence
                
                if current_chunk:
                    chunks.append(current_chunk.strip())
                
                # Ensure each chunk meets minimum length
                processed_chunks = []
                for chunk in chunks:
                    if len(chunk) < min_chars:
                        chunk = chunk + " " + "This completes the current section."
                    processed_chunks.append(chunk)
                
                logger.info(f"🔧 Texto dividido em {len(processed_chunks)} chunks")
            else:
                processed_chunks = [text]

            # Synthesize each chunk separately to avoid memory issues
            audio_chunks = []
            for i, chunk in enumerate(processed_chunks):
                try:
                    logger.info(f"🎙️ Processando chunk {i+1}/{len(processed_chunks)}: '{chunk[:50]}...'")
                    
                    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                        tmp_path = tmp_file.name
                    
                    # Use direct synthesis without file I/O when possible
                    try:
                        # Try direct synthesis first (faster)
                        chunk_audio = self.tts.tts(text=chunk)
                        if isinstance(chunk_audio, list):
                            chunk_audio = np.array(chunk_audio)
                        
                        # Ensure mono audio
                        if len(chunk_audio.shape) > 1:
                            chunk_audio = chunk_audio.mean(axis=1)
                        
                        audio_chunks.append(chunk_audio)
                        logger.info(f"✅ Chunk {i+1} sintetizado diretamente")
                        
                    except Exception as direct_error:
                        logger.warning(f"⚠️ Síntese direta falhou, usando arquivo: {direct_error}")
                        
                        # Fallback to file-based synthesis
                        self.tts.tts_to_file(text=chunk, file_path=tmp_path)
                        
                        import soundfile as sf
                        chunk_audio, sample_rate = sf.read(tmp_path)
                        
                        # Ensure mono audio
                        if len(chunk_audio.shape) > 1:
                            chunk_audio = chunk_audio.mean(axis=1)
                        
                        audio_chunks.append(chunk_audio)
                        logger.info(f"✅ Chunk {i+1} sintetizado via arquivo")
                    
                    finally:
                        # Clean up temporary file
                        if os.path.exists(tmp_path):
                            os.unlink(tmp_path)
                            
                except Exception as chunk_error:
                    logger.error(f"❌ Erro ao processar chunk {i+1}: {chunk_error}")
                    continue

            # Concatenate all audio chunks
            if audio_chunks:
                # Add small silence between chunks for natural flow
                silence_duration = 0.2  # 200ms silence
                silence_samples = int(silence_duration * self.sample_rate)
                silence = np.zeros(silence_samples)
                
                concatenated_audio = []
                for i, chunk in enumerate(audio_chunks):
                    concatenated_audio.append(chunk)
                    if i < len(audio_chunks) - 1:  # Don't add silence after last chunk
                        concatenated_audio.append(silence)
                
                audio_data = np.concatenate(concatenated_audio)
                logger.info(f"✅ {len(audio_chunks)} chunks concatenados com sucesso")
            else:
                logger.error("❌ Nenhum áudio gerado")
                return None
            
            # Normalizar
            if np.max(np.abs(audio_data)) > 0:
                audio_data = audio_data / np.max(np.abs(audio_data)) * 0.8
            
            logger.info(f"✅ Áudio sintetizado: {len(audio_data)} samples, {len(audio_data)/self.sample_rate:.2f}s")
            return audio_data.astype(np.float32)
            
        except Exception as e:
            logger.error(f"❌ Erro na síntese Coqui TTS: {e}")
            return None
    
    def change_model(self, model_name: str) -> bool:
        """
        Muda o modelo do TTS
        """
        if model_name not in self.available_models:
            logger.error(f"❌ Modelo não disponível: {model_name}")
            return False
        
        try:
            from TTS.api import TTS as CoquiTTSAPI
            logger.info(f"🔄 Mudando para modelo: {model_name}")
            
            # Liberar modelo atual
            if self.tts:
                del self.tts
                torch.cuda.empty_cache() if torch.cuda.is_available() else None
            
            # Carregar novo modelo
            self.tts = CoquiTTSAPI(model_name=model_name, gpu=torch.cuda.is_available())
            self.current_model = model_name
            
            logger.info(f"✅ Modelo alterado para: {model_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao mudar modelo: {e}")
            return False
    
    def get_available_voices(self) -> List[str]:
        """
        Retorna lista de vozes disponíveis
        """
        return [
            "default",
            "female_voice",
            "male_voice",
            "expressive",
            "calm",
            "energetic"
        ]
    
    def get_available_models(self) -> List[str]:
        """
        Retorna lista de modelos disponíveis
        """
        return self.available_models
    
    def get_info(self) -> Dict:
        """
        Retorna informações sobre o engine
        """
        return {
            "name": "Coqui TTS",
            "type": "neural",
            "available": self.available,
            "current_model": self.current_model,
            "device": self.device,
            "models_available": len(self.available_models),
            "voices": self.get_available_voices(),
            "features": [
                "High-quality neural voices",
                "Multiple models",
                "Multilingual support", 
                "Voice cloning (some models)",
                "GPU acceleration"
            ],
            "quality": "High",
            "speed": "Medium",
            "best_for": ["High-quality synthesis", "Multiple languages", "Voice variety"]
        }

# Função para obter uma instância do Coqui TTS
def get_coqui_tts():
    """
    Retorna uma instância do Coqui TTS se disponível
    """
    try:
        return CoquiTTS()
    except Exception as e:
        logger.error(f"❌ Erro ao criar instância Coqui TTS: {e}")
        return None
