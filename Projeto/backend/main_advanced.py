"""
Backend FastAPI otimizado com sistema multi-modelo dinâmico
Versão premium para conversas em tempo real
"""
import os
import asyncio
import time
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
# import whisper
from faster_whisper import WhisperModel
import ollama
import tempfile
import uuid
from pathlib import Path
import logging
from llm_models import ai_manager, AIModelConfig
from tts_manager import tts_manager

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Advanced English Learning Voice Chat", version="2.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos carregados
whisper_model = None
ollama_client = None

# Configurações
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Configurações otimizadas por tipo de conversa
CONVERSATION_CONFIGS = {
    "speed": {
        "whisper_model": "tiny",
        "max_tokens": 50,
        "temperature": 0.7,
        "auto_switch": True,
        "context_limit": 5
    },
    "balanced": {
        "whisper_model": "base", 
        "max_tokens": 100,
        "temperature": 0.8,
        "auto_switch": True,
        "context_limit": 10
    },
    "quality": {
        "whisper_model": "small",
        "max_tokens": 200,
        "temperature": 0.9,
        "auto_switch": False,
        "context_limit": 20
    }
}

current_config = "balanced"
conversation_history = []

# Modelos de dados
class ChatMessage(BaseModel):
    message: str
    conversation_type: Optional[str] = "dynamic"
    model_preference: Optional[str] = None
    
class ModelSwitchRequest(BaseModel):
    model_name: str
    
class ConfigUpdateRequest(BaseModel):
    config_type: str  # "speed", "balanced", "quality"

class ConversationStats(BaseModel):
    model_used: str
    response_time: float
    tokens_generated: int
    conversation_length: int

# WebSocket connections
connected_clients = []

@app.on_event("startup")
async def startup_event():
    """Inicialização da aplicação"""
    global whisper_model
    
    logger.info("🚀 Iniciando sistema avançado de chat...")
    
    # Inicializa Whisper
    try:
        config = CONVERSATION_CONFIGS[current_config]
        whisper_model = WhisperModel(config["whisper_model"], device="cpu", compute_type="int8")
        logger.info(f"✅ Faster-Whisper {config['whisper_model']} carregado")
    except Exception as e:
        logger.error(f"❌ Erro carregando Whisper: {e}")
        whisper_model = WhisperModel("tiny", device="cpu", compute_type="int8")  # Fallback
    
    # Inicializa gerenciador de modelos
    try:
        await ai_manager.initialize()
        logger.info("✅ Gerenciador de modelos inicializado")
    except Exception as e:
        logger.error(f"❌ Erro no gerenciador: {e}")
        
    # Inicializa TTS manager
    try:
        await tts_manager.initialize()
        logger.info("✅ TTS manager inicializado")
    except Exception as e:
        logger.error(f"❌ Erro no TTS manager: {e}")

@app.get("/")
async def root():
    return {
        "message": "Advanced English Learning Voice Chat API",
        "version": "2.0.0",
        "features": ["Multi-model support", "Dynamic model switching", "Real-time optimization"],
        "current_model": ai_manager.current_model,
        "available_models": ai_manager.available_models
    }

@app.get("/health")
async def health_check():
    """Endpoint de verificação de saúde do sistema"""
    try:
        # Verificar se Ollama está disponível
        ollama_available = False
        try:
            ollama.list()
            ollama_available = True
        except:
            ollama_available = False
            
        return {
            "status": "healthy",
            "whisper_loaded": whisper_model is not None,
            "tts_loaded": tts_manager is not None,
            "ollama_available": ollama_available,
            "current_model": ai_manager.current_model,
            "available_models": ai_manager.available_models,
            "tts_engines": list(tts_manager.engines.keys()) if tts_manager else []
        }
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "error",
            "error": str(e),
            "whisper_loaded": False,
            "tts_loaded": False,
            "ollama_available": False
        }

@app.get("/models")
async def get_models():
    """Lista todos os modelos disponíveis com informações detalhadas"""
    print(f"Debug: Available models: {ai_manager.available_models}")
    models_info = {}
    for model_name in ai_manager.available_models:
        info = ai_manager.get_model_info(model_name)
        print(f"Debug: Model info for {model_name}: {info}")
        models_info[model_name] = info
    
    response = {
        "current_model": ai_manager.current_model,
        "available_models": models_info,
        "recommendations": {
            "casual": ai_manager.get_model_recommendations("casual"),
            "dynamic": ai_manager.get_model_recommendations("dynamic"),
            "educational": ai_manager.get_model_recommendations("educational"),
            "advanced": ai_manager.get_model_recommendations("advanced")
        }
    }
    print(f"Debug: Full response: {response}")
    return response

@app.post("/switch-model")
async def switch_model(request: ModelSwitchRequest):
    """Alterna para um modelo específico"""
    success = ai_manager.switch_model(request.model_name)
    if success:
        # Notifica clientes WebSocket
        for client in connected_clients:
            try:
                await client.send_json({
                    "type": "model_switched",
                    "model": request.model_name,
                    "info": ai_manager.get_model_info()
                })
            except:
                pass
                
        return {
            "success": True,
            "current_model": ai_manager.current_model,
            "model_info": ai_manager.get_model_info()
        }
    else:
        raise HTTPException(status_code=400, detail="Modelo não disponível")

@app.post("/config")
async def update_config(request: ConfigUpdateRequest):
    """Atualiza configuração de conversação"""
    global current_config, whisper_model
    
    if request.config_type not in CONVERSATION_CONFIGS:
        raise HTTPException(status_code=400, detail="Tipo de configuração inválido")
    
    current_config = request.config_type
    config = CONVERSATION_CONFIGS[current_config]
    
    # Recarrega Whisper se necessário
    try:
        whisper_model = WhisperModel(config["whisper_model"], device="cpu", compute_type="int8")
        logger.info(f"🔄 Whisper atualizado para {config['whisper_model']}")
    except Exception as e:
        logger.error(f"❌ Erro atualizando Whisper: {e}")
    
    return {
        "success": True,
        "config": current_config,
        "settings": config
    }

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """Transcreve áudio usando Whisper otimizado"""
    if not whisper_model:
        raise HTTPException(status_code=500, detail="Whisper não inicializado")
    
    start_time = time.time()
    
    try:
        # Salva arquivo temporário
        file_id = str(uuid.uuid4())
        file_path = UPLOAD_DIR / f"{file_id}.wav"
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Transcrição
        segments, info = whisper_model.transcribe(str(file_path))
        text = "".join([segment.text for segment in segments]).strip()
        
        # Limpeza
        file_path.unlink()
        
        processing_time = time.time() - start_time
        
        return {
            "text": text,
            "processing_time": processing_time,
            "language": info.language,
            "confidence": info.language_probability
        }
        
    except Exception as e:
        logger.error(f"❌ Erro na transcrição: {e}")
        raise HTTPException(status_code=500, detail=f"Erro na transcrição: {str(e)}")

@app.post("/chat")
async def chat_message(message: ChatMessage):
    """Processa mensagem de chat com seleção automática de modelo"""
    global conversation_history
    
    start_time = time.time()
    config = CONVERSATION_CONFIGS[current_config]
    
    try:
        # Seleção automática de modelo se habilitada
        if config["auto_switch"]:
            selected_model = await ai_manager.auto_select_model(
                message.message,
                conversation_history
            )
        else:
            selected_model = message.model_preference or ai_manager.current_model
            ai_manager.switch_model(selected_model)
        
        # Prepara contexto da conversa
        context_limit = config["context_limit"]
        recent_history = conversation_history[-context_limit:] if conversation_history else []
        
        # Monta mensagens para o modelo
        model_config = ai_manager.get_current_config()
        messages = [{"role": "system", "content": model_config.system_prompt}]
        
        # Adiciona histórico recente
        for entry in recent_history:
            messages.append({"role": "user", "content": entry["user"]})
            messages.append({"role": "assistant", "content": entry["assistant"]})
        
        # Adiciona mensagem atual
        messages.append({"role": "user", "content": message.message})
        
        # Gera resposta
        response = ollama.chat(
            model=selected_model,
            messages=messages,
            options={
                "temperature": config["temperature"],
                "num_predict": config["max_tokens"],
                "top_k": 40,
                "top_p": 0.9
            }
        )
        
        assistant_response = response["message"]["content"]
        processing_time = time.time() - start_time
        
        # Atualiza histórico
        conversation_history.append({
            "user": message.message,
            "assistant": assistant_response,
            "model": selected_model,
            "timestamp": time.time()
        })
        
        # Mantém histórico limitado
        if len(conversation_history) > 50:
            conversation_history = conversation_history[-30:]
        
        stats = ConversationStats(
            model_used=selected_model,
            response_time=processing_time,
            tokens_generated=len(assistant_response.split()),
            conversation_length=len(conversation_history)
        )
        
        return {
            "response": assistant_response,
            "stats": stats.dict(),
            "model_info": ai_manager.get_model_info(selected_model)
        }
        
    except Exception as e:
        logger.error(f"❌ Erro no chat: {e}")
        raise HTTPException(status_code=500, detail=f"Erro no chat: {str(e)}")

@app.post("/tts")
async def text_to_speech(request: dict):
    """Converte texto em fala e retorna o áudio WAV"""
    text = request.get("text", "")
    if not text:
        raise HTTPException(status_code=400, detail="Missing 'text' in request body")
    try:
        result = await tts_manager.generate_speech(text)
        audio_path = result.get("audio_path")
        if not audio_path or not os.path.exists(audio_path):
            logger.error("❌ Caminho do áudio inválido ou inexistente")
            raise HTTPException(status_code=500, detail="Erro no TTS: Caminho do áudio inválido ou inexistente")
        return FileResponse(audio_path, media_type="audio/wav")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no TTS: {str(e)}")

# TTS engine management endpoints
@app.get("/tts/engines")
async def list_tts_engines():
    try:
        kokoro_engines = tts_manager.get_kokoro_engines()
        other_engines = {
            name: info for name, info in tts_manager.get_available_engines().items()
            if not name.startswith('kokoro_')
        }
        return {
            "available_engines": {**kokoro_engines, **other_engines},
            "current_engine": tts_manager.current_engine
        }
    except Exception as e:
        logger.error(f"❌ Erro listando engines TTS: {e}")
        return {"error": f"Erro listando engines TTS: {str(e)}"}

@app.get("/tts-engines")
async def get_tts_engines():
    """Lista todos os engines TTS disponíveis (endpoint alternativo)"""
    try:
        # Inicializar TTS Manager se ainda não foi inicializado
        if not hasattr(tts_manager, 'engines') or not tts_manager.engines:
            await tts_manager.initialize()
            
        # Extrair informações sobre cada engine
        engines_info = {}
        for engine_name, engine in tts_manager.engines.items():
            if hasattr(engine, 'get_info'):
                try:
                    engines_info[engine_name] = engine.get_info()
                except Exception as e:
                    logger.error(f"❌ Erro obtendo info do engine {engine_name}: {e}")
                    engines_info[engine_name] = {
                        "name": engine_name,
                        "type": engine.__class__.__name__,
                        "error": str(e)
                    }
            else:
                engines_info[engine_name] = {
                    "name": engine_name,
                    "type": engine.__class__.__name__
                }
        
        return {
            "engines": list(tts_manager.engines.keys()),
            "details": engines_info,
            "default": getattr(tts_manager, 'default_engine', None),
            "current": getattr(tts_manager, 'current_engine', None)
        }
    except Exception as e:
        logger.error(f"❌ Erro ao listar engines TTS: {e}")
        return {"error": f"Erro ao listar engines TTS: {str(e)}"}

@app.post("/tts/switch")
async def switch_tts_engine(request: dict):
    engine_name = request.get("engine")
    if not engine_name:
        raise HTTPException(status_code=400, detail="Engine name missing")
    success = tts_manager.switch_engine(engine_name)
    if success:
        return {"success": True, "current_engine": tts_manager.current_engine}
    else:
        raise HTTPException(status_code=400, detail="Invalid or unavailable engine")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket para comunicação em tempo real"""
    await websocket.accept()
    connected_clients.append(websocket)
    
    try:
        # Envia status inicial
        await websocket.send_json({
            "type": "connected",
            "current_model": ai_manager.current_model,
            "config": current_config,
            "available_models": ai_manager.available_models
        })
        
        while True:
            data = await websocket.receive_json()
            
            if data["type"] == "ping":
                await websocket.send_json({"type": "pong"})
                
            elif data["type"] == "get_stats":
                stats = {
                    "conversation_length": len(conversation_history),
                    "current_model": ai_manager.current_model,
                    "model_performance": ai_manager.model_performance,
                    "config": current_config
                }
                await websocket.send_json({"type": "stats", "data": stats})
                
    except WebSocketDisconnect:
        connected_clients.remove(websocket)
    except Exception as e:
        logger.error(f"❌ Erro WebSocket: {e}")
        if websocket in connected_clients:
            connected_clients.remove(websocket)

@app.get("/conversation-history")
async def get_conversation_history():
    """Retorna histórico da conversa"""
    return {
        "history": conversation_history,
        "total_messages": len(conversation_history),
        "current_config": current_config
    }

@app.delete("/conversation-history")
async def clear_conversation_history():
    """Limpa histórico da conversa"""
    global conversation_history
    conversation_history = []
    return {"message": "Histórico limpo", "success": True}

@app.get("/system-info")
async def get_system_info():
    """Retorna informações detalhadas sobre o sistema"""
    try:
        # Verificar Ollama
        ollama_available = False
        ollama_models = []
        try:
            ollama_list = ollama.list()
            ollama_available = True
            # Extract model names based on the response structure
            if isinstance(ollama_list, dict) and 'models' in ollama_list:
                ollama_models = [m.get('name', '') for m in ollama_list.get('models', [])]
            elif isinstance(ollama_list, list):
                ollama_models = [m.get('name', '') if isinstance(m, dict) else m for m in ollama_list]
        except Exception as e:
            logger.error(f"❌ Erro ao verificar Ollama: {e}")
        
        # Informações sobre TTS
        tts_info = {
            "engines_available": list(tts_manager.engines.keys()) if hasattr(tts_manager, 'engines') else [],
            "default_engine": tts_manager.default_engine if hasattr(tts_manager, 'default_engine') else None,
            "current_engine": tts_manager.current_engine if hasattr(tts_manager, 'current_engine') else None
        }
        
        # Whisper
        whisper_info = {
            "model": CONVERSATION_CONFIGS[current_config]["whisper_model"],
            "loaded": whisper_model is not None
        }
        
        # AI Models
        ai_models_info = {
            "current_model": ai_manager.current_model,
            "available_models": ai_manager.available_models,
            "model_performance": ai_manager.model_performance
        }
        
        return {
            "api_version": "2.0.0",
            "status": "healthy",
            "ollama": {
                "available": ollama_available,
                "models": ollama_models
            },
            "tts": tts_info,
            "whisper": whisper_info,
            "ai_models": ai_models_info,
            "config": {
                "current_config": current_config,
                "config_settings": CONVERSATION_CONFIGS[current_config]
            }
        }
    except Exception as e:
        logger.error(f"❌ Erro ao obter informações do sistema: {e}")
        return {
            "status": "error", 
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
