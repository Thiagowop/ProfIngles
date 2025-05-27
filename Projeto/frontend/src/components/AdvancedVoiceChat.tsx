import React, { useState, useEffect, useRef } from 'react';
import { Mic, MicOff, Send, Settings, Zap, Brain, BookOpen, Users, Volume2, VolumeX } from 'lucide-react';
import apiClient from '../utils/api';
import { useAudioPlayer } from '../hooks/useAudioPlayer';

interface ModelInfo {
  name: string;
  size: string;
  ram_usage: string;
  speed_rating: number;
  quality_rating: number;
  best_for: string[];
  available: boolean;
  performance?: {
    response_time: number;
    tokens_per_second: number;
  };
}

interface ConversationStats {
  model_used: string;
  response_time: number;
  tokens_generated: number;
  conversation_length: number;
}

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
  stats?: ConversationStats;
  modelInfo?: ModelInfo;
}

const AdvancedVoiceChat: React.FC = () => {
  // Estados principais
  const [messages, setMessages] = useState<Message[]>([]);
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [inputText, setInputText] = useState('');
  const [currentModel, setCurrentModel] = useState('gemma2:2b');
  const [availableModels, setAvailableModels] = useState<{[key: string]: ModelInfo}>({});
  const [conversationMode, setConversationMode] = useState<'speed' | 'balanced' | 'quality'>('balanced');
  const [showSettings, setShowSettings] = useState(false);
  const [autoModelSwitch, setAutoModelSwitch] = useState(true);
  
  // Estados de WebSocket
  const [wsConnection, setWsConnection] = useState<WebSocket | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected'>('disconnected');
  
  // Estados de áudio
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null);
  const [audioChunks, setAudioChunks] = useState<Blob[]>([]);
  const { isPlaying: isPlayingAudio, playAudio } = useAudioPlayer();
  const [availableTtsEngines, setAvailableTtsEngines] = useState<Record<string, any>>({});
  const [currentTtsEngine, setCurrentTtsEngine] = useState<string>('');

  // Refs
  const messagesEndRef = useRef<HTMLDivElement>(null);
    // Inicialização
  useEffect(() => {
    initializeApp();
    connectWebSocket();
    return () => {
      if (wsConnection) {
        wsConnection.close();
      }
    };
  }, []); // eslint-disable-line react-hooks/exhaustive-deps
  const initializeApp = async () => {
    try {
        // Carrega informações dos modelos
        const response = await fetch('http://localhost:8000/models');
        const data = await response.json();
        console.log('Models loaded:', data.available_models);

        // Corrigir estrutura dos dados recebidos
        const formattedModels = Object.entries(data.available_models).reduce((acc: Record<string, ModelInfo>, [key, value]: [string, any]) => {
            acc[key] = {
                ...value,
                name: value.name || key // Garantir que o nome esteja presente
            };
            return acc;
        }, {});

        setAvailableModels(formattedModels);
        setCurrentModel(data.current_model);

        // Carrega informações dos TTS engines
        const ttsData = await apiClient.getTtsEngines();
        setAvailableTtsEngines(ttsData.available_engines);
        setCurrentTtsEngine(ttsData.current_engine);
    } catch (error) {
        console.error('Erro ao inicializar:', error);
    }
  };

  const connectWebSocket = () => {
    try {
      setConnectionStatus('connecting');
      const ws = new WebSocket('ws://localhost:8000/ws');
      
      ws.onopen = () => {
        setConnectionStatus('connected');
        setWsConnection(ws);
      };
      
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
      };
      
      ws.onclose = () => {
        setConnectionStatus('disconnected');
        setWsConnection(null);
        // Reconecta após 3 segundos
        setTimeout(connectWebSocket, 3000);
      };
      
      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setConnectionStatus('disconnected');
      };
    } catch (error) {
      console.error('Erro conectando WebSocket:', error);
      setConnectionStatus('disconnected');
    }
  };  const handleWebSocketMessage = (data: any) => {
    switch (data.type) {
      case 'connected':
        // Atualizar apenas o modelo atual, não os modelos disponíveis
        if (data.current_model) {
          setCurrentModel(data.current_model);
        }
        break;
      case 'model_switched':
        setCurrentModel(data.model);
        break;
    }
  };

  // Controle de áudio
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      
      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          setAudioChunks(prev => [...prev, event.data]);
        }
      };
      
      recorder.onstop = () => {
        processAudio();
        stream.getTracks().forEach(track => track.stop());
      };
      
      setMediaRecorder(recorder);
      setAudioChunks([]);
      recorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Erro ao iniciar gravação:', error);
      alert('Erro ao acessar microfone');
    }
  };

  const stopRecording = () => {
    if (mediaRecorder && isRecording) {
      mediaRecorder.stop();
      setIsRecording(false);
    }
  };

  const processAudio = async () => {
    if (audioChunks.length === 0) return;
    
    setIsProcessing(true);
    
    try {
      const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
      const formData = new FormData();
      formData.append('file', audioBlob, 'audio.wav');
      
      // Transcrição
      const transcribeResponse = await fetch('http://localhost:8000/transcribe', {
        method: 'POST',
        body: formData,
      });
      
      const transcribeData = await transcribeResponse.json();
      
      if (transcribeData.text.trim()) {
        await sendMessage(transcribeData.text.trim());
      }
    } catch (error) {
      console.error('Erro processando áudio:', error);
      alert('Erro ao processar áudio');
    } finally {
      setIsProcessing(false);
      setAudioChunks([]);
    }
  };

  const sendMessage = async (text: string) => {
    if (!text.trim()) return;
    
    const userMessage: Message = {
      id: Date.now().toString(),
      text: text,
      isUser: true,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsProcessing(true);
    
    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text,
          conversation_type: conversationMode,
          model_preference: autoModelSwitch ? null : currentModel
        }),
      });
      
      const data = await response.json();
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: data.response,
        isUser: false,
        timestamp: new Date(),
        stats: data.stats,
        modelInfo: data.model_info
      };
      
      setMessages(prev => [...prev, assistantMessage]);
      setCurrentModel(data.stats.model_used);
    } catch (error) {
      console.error('Erro enviando mensagem:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: 'Desculpe, houve um erro. Tente novamente.',
        isUser: false,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsProcessing(false);
    }
  };

  const switchModel = async (modelName: string) => {
    try {
      const response = await fetch('http://localhost:8000/switch-model', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model_name: modelName }),
      });
      
      if (response.ok) {
        const data = await response.json();
        setCurrentModel(data.current_model);
      }
    } catch (error) {
      console.error('Erro ao trocar modelo:', error);
    }
  };

  const updateConversationMode = async (mode: 'speed' | 'balanced' | 'quality') => {
    try {
      const response = await fetch('http://localhost:8000/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ config_type: mode }),
      });
      
      if (response.ok) {
        setConversationMode(mode);
      }
    } catch (error) {
      console.error('Erro ao atualizar configuração:', error);
    }
  };

  const clearHistory = async () => {
    try {
      await fetch('http://localhost:8000/conversation-history', {
        method: 'DELETE'
      });
      setMessages([]);
    } catch (error) {
      console.error('Erro ao limpar histórico:', error);
    }
  };

  const switchTtsEngine = async (engine: string) => {
    try {
      const data = await apiClient.switchTtsEngine(engine);
      setCurrentTtsEngine(data.current_engine);
    } catch (e) {
      console.error('Erro ao trocar TTS engine:', e);
    }
  };
  
  const handlePlayAudio = async (text: string) => {
    try {
      const audioBlob = await apiClient.textToSpeech(text);
      await playAudio(audioBlob);
    } catch (e) {
      console.error('Erro ao reproduzir áudio:', e);
    }
  };

  // Scroll automático
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const getModeIcon = (mode: string) => {
    switch (mode) {
      case 'speed': return <Zap className="w-4 h-4" />;
      case 'quality': return <Brain className="w-4 h-4" />;
      default: return <Users className="w-4 h-4" />;
    }
  };

  const getModelSpeedColor = (rating: number) => {
    if (rating >= 4) return 'text-green-500';
    if (rating >= 3) return 'text-yellow-500';
    return 'text-red-500';
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <div className="bg-white shadow-lg border-b border-gray-200 p-4">
        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <h1 className="text-2xl font-bold text-gray-800">🎯 Advanced English Chat</h1>
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${
                connectionStatus === 'connected' ? 'bg-green-500' : 
                connectionStatus === 'connecting' ? 'bg-yellow-500' : 'bg-red-500'
              }`}></div>
              <span className="text-sm text-gray-600">{connectionStatus}</span>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            {/* Modo de Conversa */}
            <div className="flex bg-gray-100 rounded-lg p-1">
              {(['speed', 'balanced', 'quality'] as const).map((mode) => (
                <button
                  key={mode}
                  onClick={() => updateConversationMode(mode)}
                  className={`flex items-center space-x-1 px-3 py-1 rounded-md text-sm font-medium transition-all ${
                    conversationMode === mode
                      ? 'bg-blue-500 text-white shadow-sm'
                      : 'text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  {getModeIcon(mode)}
                  <span className="capitalize">{mode}</span>
                </button>
              ))}
            </div>
            
            {/* Modelo Atual */}
            <div className="flex items-center space-x-2 bg-gray-100 rounded-lg px-3 py-2">
              <Brain className="w-4 h-4 text-blue-500" />
              <span className="text-sm font-medium text-gray-700">{currentModel}</span>
              {availableModels[currentModel] && (
                <span className={`text-xs ${getModelSpeedColor(availableModels[currentModel].speed_rating)}`}>
                  ⚡{availableModels[currentModel].speed_rating}/5
                </span>
              )}
            </div>
              <button
              onClick={() => setShowSettings(!showSettings)}
              title="Configurações"
              className="p-2 rounded-lg bg-gray-100 hover:bg-gray-200 transition-colors"
            >
              <Settings className="w-5 h-5 text-gray-600" />
            </button>
          </div>
        </div>
      </div>

      {/* Settings Panel */}
      {showSettings && (
        <div className="bg-white border-b border-gray-200 p-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Modelos Disponíveis */}
            <div>
              <h3 className="font-medium text-gray-800 mb-2">Modelos Disponíveis</h3>
              <div className="space-y-2">
                {Object.entries(availableModels).map(([modelName, info]) => (
                  <button
                    key={modelName}
                    onClick={() => switchModel(modelName)}
                    disabled={!info.available}
                    title={`Trocar para modelo ${modelName} - ${info.best_for ? info.best_for.join(', ') : 'Modelo disponível'}`}
                    className={`w-full text-left p-2 rounded-lg border transition-all ${
                      currentModel === modelName
                        ? 'bg-blue-50 border-blue-300 text-blue-800'
                        : info.available
                        ? 'bg-gray-50 border-gray-200 hover:bg-gray-100'
                        : 'bg-gray-100 border-gray-200 text-gray-400 cursor-not-allowed'
                    }`}
                  >
                    <div className="flex justify-between items-center">
                      <span className="font-medium">{modelName}</span>
                      <div className="flex space-x-1">
                        <span className={`text-xs ${getModelSpeedColor(info.speed_rating)}`}>
                          ⚡{info.speed_rating}
                        </span>
                        <span className="text-xs text-purple-500">
                          🧠{info.quality_rating}
                        </span>
                      </div>
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      {info.size} • {info.ram_usage}
                    </div>
                    {info.performance && (
                      <div className="text-xs text-green-600 mt-1">
                        {info.performance.tokens_per_second.toFixed(1)} tokens/s
                      </div>
                    )}
                  </button>
                ))}
              </div>
            </div>
            
            {/* Configurações */}
            <div>
              <h3 className="font-medium text-gray-800 mb-2">Configurações</h3>
              <div className="space-y-3">
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={autoModelSwitch}
                    onChange={(e) => setAutoModelSwitch(e.target.checked)}
                    className="rounded"
                  />
                  <span className="text-sm text-gray-700">Troca automática de modelo</span>
                </label>
                
                <button
                  onClick={clearHistory}
                  className="w-full px-3 py-2 bg-red-50 text-red-700 rounded-lg hover:bg-red-100 transition-colors text-sm"
                >
                  Limpar Histórico
                </button>
              </div>
            </div>
            
            {/* Estatísticas */}
            <div>
              <h3 className="font-medium text-gray-800 mb-2">Estatísticas</h3>
              <div className="space-y-2 text-sm text-gray-600">
                <div>Mensagens: {messages.length}</div>
                <div>Modelo atual: {currentModel}</div>
                <div>Modo: {conversationMode}</div>
                {messages.length > 0 && messages[messages.length - 1].stats && (
                  <div>
                    Último tempo: {messages[messages.length - 1].stats!.response_time.toFixed(2)}s
                  </div>
                )}
              </div>
            </div>
            
            {/* TTS Engines */}
            <div>
              <h3 className="font-medium text-gray-800 mb-2">TTS Engines</h3>
              <div className="space-y-2">
                {Object.entries(availableTtsEngines).map(([engine, info]) => (
                  <button
                    key={engine}
                    onClick={() => switchTtsEngine(engine)}
                    disabled={!info.available}
                    title={`TTS Engine: ${info.name}`}
                    className={`w-full text-left p-2 rounded-lg border transition-all ${
                      currentTtsEngine === engine
                        ? 'bg-blue-50 border-blue-300 text-blue-800'
                        : info.available
                        ? 'bg-gray-50 border-gray-200 hover:bg-gray-100'
                        : 'bg-gray-100 border-gray-200 text-gray-400 cursor-not-allowed'
                    }`}
                  >
                    <span className="font-medium">{info.name}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-500 mt-8">
            <BookOpen className="w-12 h-12 mx-auto mb-4 text-gray-400" />
            <p className="text-lg font-medium">Comece uma conversa em inglês!</p>
            <p className="text-sm mt-2">Use o microfone para falar ou digite sua mensagem</p>
          </div>
        )}
        
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg shadow-sm ${
                message.isUser
                  ? 'bg-blue-500 text-white'
                  : 'bg-white text-gray-800 border border-gray-200'
              }`}
            >
              <p className="text-sm">{message.text}</p>
              
              {/* Stats para mensagens do assistente */}
              {!message.isUser && message.stats && (
                <div className="mt-2 pt-2 border-t border-gray-100 text-xs text-gray-500">
                  <div className="flex justify-between items-center">
                    <span>{message.stats.model_used}</span>
                    <span>{message.stats.response_time.toFixed(2)}s</span>
                  </div>
                </div>
              )}
              
              <div className="text-xs opacity-75 mt-1">
                {message.timestamp.toLocaleTimeString()}
              </div>
              
              {/* Botão de reprodução de áudio */}
              {!message.isUser && (
                <div className="flex items-center mt-1">
                  <button
                    onClick={() => handlePlayAudio(message.text)}
                    disabled={isPlayingAudio}
                    className={`ml-2 p-1 rounded-full transition-colors ${
                      isPlayingAudio
                        ? 'text-gray-400 cursor-not-allowed'
                        : 'hover:bg-gray-100 text-gray-600'
                    }`}
                    title="Ouvir mensagem"
                  >
                    {isPlayingAudio ? <VolumeX size={14} /> : <Volume2 size={14} />}
                  </button>
                  <span className="text-xs opacity-75 ml-2">{message.timestamp.toLocaleTimeString()}</span>
                </div>
              )}
            </div>
          </div>
        ))}
        
        {isProcessing && (
          <div className="flex justify-start">
            <div className="bg-white border border-gray-200 rounded-lg px-4 py-2 shadow-sm">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse delay-75"></div>
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse delay-150"></div>
                <span className="text-sm text-gray-600 ml-2">Processando...</span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="bg-white border-t border-gray-200 p-4">
        <div className="flex space-x-2">          <button
            onClick={isRecording ? stopRecording : startRecording}
            disabled={isProcessing}
            title={isRecording ? "Parar gravação" : "Iniciar gravação"}
            className={`p-3 rounded-full transition-all ${
              isRecording
                ? 'bg-red-500 hover:bg-red-600 text-white animate-pulse'
                : 'bg-blue-500 hover:bg-blue-600 text-white'
            } ${isProcessing ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            {isRecording ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
          </button>
          
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && sendMessage(inputText)}
            placeholder="Digite sua mensagem ou use o microfone..."
            disabled={isProcessing}
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
            <button
            onClick={() => sendMessage(inputText)}
            disabled={isProcessing || !inputText.trim()}
            title="Enviar mensagem"
            className="px-6 py-3 bg-green-500 hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg transition-colors"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default AdvancedVoiceChat;
