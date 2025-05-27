"""
TTS Manager for handling multiple Text-to-Speech engines
Enhanced version with Coqui TTS, Kokoro TTS, and pyttsx3 support
"""
from abc import ABC, abstractmethod
import os
import logging
import tempfile
import uuid
import sys
import soundfile as sf

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check Python version for compatibility warnings
PYTHON_VERSION = sys.version_info
logger.info(
    f"Python version: {PYTHON_VERSION[0]}.{PYTHON_VERSION[1]}.{PYTHON_VERSION[2]}")


class TTSEngine(ABC):
    @abstractmethod
    async def generate_speech(self, text: str) -> str:
        """Generate speech from text and return the path to the audio file"""
        pass

    @abstractmethod
    def get_info(self) -> dict:
        """Return information about the TTS engine"""
        pass

# Updated TTS engine selection: keeping stable and working engines
# Current engines: Pyttsx3, Coqui TTS, Kokoro Neural TTS, Google TTS


class Pyttsx3TTS(TTSEngine):
    def __init__(self):
        try:
            import pyttsx3
            self.tts = pyttsx3.init()
            # Configure voice properties
            voices = self.tts.getProperty('voices')
            if voices:
                # Try to use a female voice if available
                for voice in voices:
                    if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                        self.tts.setProperty('voice', voice.id)
                        break

            self.tts.setProperty('rate', 180)  # Speed of speech
            self.tts.setProperty('volume', 0.9)  # Volume level
            self.available = True
            logger.info("Pyttsx3 TTS initialized successfully")
        except Exception as e:
            self.available = False
            logger.error(f"Failed to initialize Pyttsx3 TTS: {e}")

    async def generate_speech(self, text: str) -> str:
        if not self.available:
            raise Exception("Pyttsx3 TTS is not available")

        try:
            output_path = os.path.join(
                tempfile.gettempdir(), f"pyttsx3_tts_{uuid.uuid4()}.wav")
            self.tts.save_to_file(text, output_path)
            self.tts.runAndWait()
            return output_path
        except Exception as e:
            logger.error(f"Pyttsx3 TTS generation failed: {e}")
            raise

    def get_info(self) -> dict:
        return {
            "name": "Pyttsx3 TTS",
            "type": "system",
            "available": self.available,
            "features": ["System voices", "Cross-platform", "Lightweight"]
        }


class CoquiTTSEngine(TTSEngine):
    """Coqui TTS Engine Wrapper"""

    def __init__(self):
        try:
            from coqui_tts import CoquiTTS
            self.tts = CoquiTTS()
            self.available = self.tts.available
            if self.available:
                logger.info("Coqui TTS initialized successfully")
            else:
                logger.warning("Coqui TTS initialization failed")
        except Exception as e:
            self.available = False
            logger.info(f"Coqui TTS not available: {e}")

    async def generate_speech(self, text: str) -> str:
        if not self.available:
            raise Exception("Coqui TTS is not available")

        try:
            # Sintetizar áudio
            audio_data = self.tts.synthesize(text)

            if audio_data is None:
                raise Exception("Failed to synthesize audio")

            # Salvar em arquivo temporário
            output_path = os.path.join(
                tempfile.gettempdir(), f"coqui_tts_{uuid.uuid4()}.wav")
            sf.write(output_path, audio_data, self.tts.sample_rate)

            return output_path
        except Exception as e:
            logger.error(f"Coqui TTS generation failed: {e}")
            raise

    def get_info(self) -> dict:
        if self.available:
            return self.tts.get_info()
        else:
            return {
                "name": "Coqui TTS",
                "type": "neural",
                "available": False,
                "features": ["Not available"]
            }


class KokoroTTSEngine(TTSEngine):
    """Kokoro Neural TTS Engine Wrapper - Uses corrected implementation"""

    def __init__(self, lang_code='a', voice=None):
        self.default_voice = voice or 'default'
        try:
            # Use the corrected neural Kokoro TTS implementation
            from kokoro_neural_tts import KokoroTTS
            self.tts = KokoroTTS(lang_code=lang_code, default_voice=voice)
            self.available = self.tts.available
            if self.available:
                logger.info(
                    f"Kokoro NEURAL TTS initialized successfully with lang_code='{lang_code}'")
            else:
                logger.warning("Kokoro neural TTS initialization failed")
        except ImportError as e:
            self.available = False
            logger.info(
                f"Kokoro neural TTS not available - missing dependencies: {e}")
        except Exception as e:
            self.available = False
            logger.info(f"Kokoro neural TTS initialization error: {e}")

    async def generate_speech(self, text: str) -> str:
        """Generate speech using the default voice for this engine"""
        if not self.available:
            raise Exception("Kokoro neural TTS is not available")

        try:
            # Synthesize audio using corrected implementation with default voice
            audio_data = self.tts.synthesize(text, voice=self.default_voice)

            if audio_data is None:
                raise Exception(
                    "Failed to synthesize audio - neural model returned None")

            # Create engine-specific temp directory to avoid conflicts
            temp_dir = os.path.join(tempfile.gettempdir(), "kokoro_tts")
            os.makedirs(temp_dir, exist_ok=True)

            # Save to temporary file
            output_path = os.path.join(
                temp_dir, f"kokoro_neural_{uuid.uuid4()}.wav")
            sf.write(output_path, audio_data, self.tts.sample_rate)

            logger.info(
                f"Kokoro neural TTS generated: {len(audio_data)} samples, {len(audio_data)/self.tts.sample_rate:.2f}s")
            return output_path
        except Exception as e:
            logger.error(f"Kokoro neural TTS generation failed: {e}")
            raise

    def get_info(self) -> dict:
        if self.available:
            info = self.tts.get_info()
            # Verificar se 'lang_code' está presente antes de acessá-lo
            if "lang_code" in info:
                if info["lang_code"] == "a":
                    if info["default_voice"] in ["am_michael", "am_adam"]:
                        info["name"] = "Kokoro Neural TTS (American English Male)"
                    else:
                        info["name"] = "Kokoro Neural TTS (American English Female)"
                elif info["lang_code"] == "b":
                    if info["default_voice"].startswith("bm_"):
                        info["name"] = "Kokoro Neural TTS (British English Male)"
                    else:
                        info["name"] = "Kokoro Neural TTS (British English Female)"
                elif info["lang_code"] == "p":
                    info["name"] = "Kokoro Neural TTS (Portuguese Brazilian)"
            return info
        else:
            return {
                "name": "Kokoro Neural TTS",
                "type": "neural",
                "available": False,
                "features": ["Not available - requires kokoro>=0.9.4 and misaki[en]"]
            }


class GoogleTTSEngine(TTSEngine):
    """Google TTS Engine Wrapper"""

    def __init__(self):
        try:
            from google_tts import GoogleTTS
            self.tts = GoogleTTS()
            self.available = self.tts.available
            if self.available:
                logger.info("Google TTS initialized successfully")
            else:
                logger.warning("Google TTS initialization failed")
        except Exception as e:
            self.available = False
            logger.info(f"Google TTS not available: {e}")

    async def generate_speech(self, text: str) -> str:
        if not self.available:
            raise Exception("Google TTS is not available")

        try:
            # Sintetizar áudio (retorna caminho do arquivo)
            audio_path = self.tts.synthesize(text)

            if audio_path is None:
                raise Exception("Failed to synthesize audio")

            return audio_path
        except Exception as e:
            logger.error(f"Google TTS generation failed: {e}")
            raise

    def get_info(self) -> dict:
        if self.available:
            return self.tts.get_info()
        else:
            return {
                "name": "Google TTS",
                "type": "cloud",
                "available": False,
                "features": ["Not available"]
            }


class TTSManager:
    def __init__(self):
        self.engines: dict[str, TTSEngine] = {}
        self.current_engine: str = None
        # Initialize engines synchronously in constructor
        self.initialize_sync()

    def initialize_sync(self):
        """Initialize available TTS engines synchronously"""
        # Initialize engines one by one, only keeping working ones
        logger.info("Initializing TTS engines...")
        # Always try Pyttsx3 first (most reliable)
        pyttsx3_engine = Pyttsx3TTS()
        if pyttsx3_engine.available:
            self.engines["pyttsx3"] = pyttsx3_engine
            self.current_engine = "pyttsx3"
            logger.info("Pyttsx3 TTS ready")

        # Try Coqui TTS if available
        try:
            coqui_engine = CoquiTTSEngine()
            if coqui_engine.available:
                self.engines["coqui"] = coqui_engine
                logger.info("Coqui TTS ready")
        except Exception as e:
            logger.info(f"Coqui TTS skipped: {e}")
        # Try Kokoro Neural TTS if available (multiple language support)
        try:
            # American English Kokoro - Male Teacher Voice
            kokoro_en_us_male = KokoroTTSEngine(
                lang_code='a', voice='am_michael')
            if kokoro_en_us_male.available:
                self.engines["kokoro_en_us_male"] = kokoro_en_us_male
                if not self.current_engine:  # Set as default if no other engine is set
                    self.current_engine = "kokoro_en_us_male"
                logger.info("Kokoro Neural TTS (American English Male) ready")
        except Exception as e:
            logger.info(
                f"Kokoro Neural TTS (American English Male) skipped: {e}")

        try:
            # American English Kokoro - Female Voice (Heart)
            kokoro_en_us_female_heart = KokoroTTSEngine(
                lang_code='a', voice='af_heart')
            if kokoro_en_us_female_heart.available:
                self.engines["kokoro_en_us_female_heart"] = kokoro_en_us_female_heart
                logger.info(
                    "Kokoro Neural TTS (American English Female - Heart) ready")
        except Exception as e:
            logger.info(
                f"Kokoro Neural TTS (American English Female - Heart) skipped: {e}")

        try:
            # American English Kokoro - Female Voice (Bella)
            kokoro_en_us_female_bella = KokoroTTSEngine(
                lang_code='a', voice='af_bella')
            if kokoro_en_us_female_bella.available:
                self.engines["kokoro_en_us_female_bella"] = kokoro_en_us_female_bella
                logger.info(
                    "Kokoro Neural TTS (American English Female - Bella) ready")
        except Exception as e:
            logger.info(
                f"Kokoro Neural TTS (American English Female - Bella) skipped: {e}")

        try:
            # British English Kokoro - Male Voice
            kokoro_en_gb_male = KokoroTTSEngine(
                lang_code='b', voice='bm_lewis')
            if kokoro_en_gb_male.available:
                self.engines["kokoro_en_gb_male"] = kokoro_en_gb_male
                logger.info("Kokoro Neural TTS (British English Male) ready")
        except Exception as e:
            logger.info(
                f"Kokoro Neural TTS (British English Male) skipped: {e}")

        try:
            # British English Kokoro - Female Voice
            kokoro_en_gb_female = KokoroTTSEngine(
                lang_code='b', voice='bf_emma')
            if kokoro_en_gb_female.available:
                self.engines["kokoro_en_gb_female"] = kokoro_en_gb_female
                logger.info("Kokoro Neural TTS (British English Female) ready")
        except Exception as e:
            logger.info(
                f"Kokoro Neural TTS (British English Female) skipped: {e}")

        try:
            # Portuguese Brazilian Kokoro
            kokoro_pt_br = KokoroTTSEngine(lang_code='p', voice='pf_dora')
            if kokoro_pt_br.available:
                self.engines["kokoro_pt_br"] = kokoro_pt_br
                logger.info("Kokoro Neural TTS (Portuguese Brazilian) ready")
        except Exception as e:
            logger.info(
                f"Kokoro Neural TTS (Portuguese Brazilian) skipped: {e}")

        # Try Google TTS if available
        try:
            google_engine = GoogleTTSEngine()
            if google_engine.available:
                self.engines["google"] = google_engine
                logger.info("Google TTS ready")
        except Exception as e:
            logger.info(f"Google TTS skipped: {e}")

        if not self.engines:
            logger.error("No TTS engines available!")
        else:
            logger.info(
                f"TTS Manager ready with {len(self.engines)} engine(s)")

        # Set default engine to first available
        if not self.current_engine and self.engines:
            self.current_engine = list(self.engines.keys())[0]

    async def initialize(self):
        """Initialize available TTS engines (async version - calls sync version)"""
        self.initialize_sync()

    async def initialize_minimal(self):
        """Inicialização mínima apenas com engines essenciais para velocidade"""
        logger.info("🚀 Inicializando TTS Manager em modo mínimo...")
        self.engines = {}

        # Inicializar apenas Pyttsx3 (mais rápido)
        try:
            pyttsx3_engine = Pyttsx3TTS()
            if pyttsx3_engine.available:
                self.engines['pyttsx3'] = pyttsx3_engine
                logger.info("✅ Pyttsx3 TTS carregado (modo mínimo)")
        except Exception as e:
            logger.error(f"❌ Erro carregando Pyttsx3: {e}")

        # Tentar carregar pelo menos um Kokoro se possível
        try:
            kokoro_michael = KokoroNeuralTTS(
                lang_code='a', voice_name='EN-US Michael')
            if kokoro_michael.available:
                self.engines['kokoro_en_us_male'] = kokoro_michael
                logger.info("✅ Kokoro Michael carregado (modo mínimo)")
        except Exception as e:
            logger.error(f"❌ Erro carregando Kokoro Michael: {e}")

        # Definir engine padrão
        if self.engines:
            self.current_engine = list(self.engines.keys())[0]
            logger.info(f"🎯 Engine padrão: {self.current_engine}")
        else:
            logger.error("❌ Nenhuma engine TTS disponível!")

    def switch_engine(self, engine_name: str) -> bool:
        """Switch to a different TTS engine"""
        if engine_name in self.engines and self.engines[engine_name].available:
            self.current_engine = engine_name
            return True
        return False

    async def generate_speech(self, text: str, voice: str = "default", language: str = None) -> dict:
        """Generate speech using the current engine with optional voice and language selection"""
        if not self.current_engine:
            raise Exception("No TTS engine available")

        # Auto-select Kokoro engine based on language if specified
        if language and language in ['en-US', 'en-GB', 'pt-BR', 'ja']:
            language_engine_map = {
                'en-US': 'kokoro_en_us',
                'en-GB': 'kokoro_en_gb',
                'pt-BR': 'kokoro_pt_br',
                'ja': 'kokoro_ja'
            }

            preferred_engine = language_engine_map.get(language)
            if preferred_engine in self.engines and self.engines[preferred_engine].available:
                self.current_engine = preferred_engine
                logger.info(
                    f"Auto-switched to {preferred_engine} for language {language}")

        engine = self.engines[self.current_engine]
        try:
            # All engines use the standard interface now
            audio_path = await engine.generate_speech(text)

            return {
                "success": True,
                "audio_path": audio_path,
                "engine": self.current_engine,
                "voice": voice if voice != "default" else None,
                "language": language,
                "info": engine.get_info()
            }
        except Exception as e:
            logger.error(f"Speech generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "engine": self.current_engine,
                "voice": voice,                "language": language
            }

    def get_available_engines(self) -> dict:
        """Get information about all available engines"""
        return {
            name: engine.get_info()
            for name, engine in self.engines.items()
            if engine.available
        }

    def get_kokoro_engines(self) -> dict:
        """Get only Kokoro neural TTS engines with language info"""
        kokoro_engines = {}
        logger.info(f"Available engines: {list(self.engines.keys())}")
        for name, engine in self.engines.items():
            if name.startswith('kokoro_') and engine.available:
                logger.info(f"Processing Kokoro engine: {name}")
                info = engine.get_info()
                # Enhanced debug logging
                logger.info(f"Engine {name} info: {info}")
                # Verificar se 'lang_code' está presente antes de acessá-lo
                if 'lang_code' not in info:
                    logger.warning(
                        f"Missing 'lang_code' in Kokoro engine info: {info}")
                    continue

                # Enhanced logic for handling different voices
                if info["lang_code"] == "a":
                    if info["default_voice"] in ["am_michael", "am_adam"]:
                        info["name"] = "Kokoro Neural TTS (American English Male)"
                    elif info["default_voice"] == "af_bella":
                        info["name"] = "Kokoro Neural TTS (American English Female - Bella)"
                    elif info["default_voice"] == "af_heart":
                        info["name"] = "Kokoro Neural TTS (American English Female - Heart)"
                    else:
                        info["name"] = "Kokoro Neural TTS (American English Female)"
                elif info["lang_code"] == "b":
                    if info["default_voice"].startswith("bm_"):
                        info["name"] = "Kokoro Neural TTS (British English Male)"
                    else:
                        info["name"] = "Kokoro Neural TTS (British English Female)"
                elif info["lang_code"] == "p":
                    info["name"] = "Kokoro Neural TTS (Portuguese Brazilian)"
                kokoro_engines[name] = info
        return kokoro_engines

    async def generate_speech_with_language(self, text: str, language: str = 'en-US', voice: str = 'default') -> dict:
        """Generate speech with automatic language detection and best voice selection"""
        return await self.generate_speech(text, voice=voice, language=language)

    def switch_to_best_kokoro(self, language: str = 'en-US') -> str:
        """Switch to the best available Kokoro engine for the specified language"""
        language_engine_map = {
            'en-US': 'kokoro_en_us',
            'en-GB': 'kokoro_en_gb',
            'pt-BR': 'kokoro_pt_br',
            'ja': 'kokoro_ja'
        }

        target_engine = language_engine_map.get(language)
        if target_engine and target_engine in self.engines and self.engines[target_engine].available:
            self.current_engine = target_engine
            logger.info(
                f"Switched to best Kokoro engine: {target_engine} for language {language}")
            return target_engine
        return None


# Global TTS manager instance
tts_manager = TTSManager()
