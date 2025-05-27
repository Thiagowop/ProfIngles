import React, { useState, useEffect, useRef } from 'react';
import { Mic, MicOff, Zap, Clock, Cpu } from 'lucide-react';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  processingTime?: number;
}

const RealTimeChat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [inputText, setInputText] = useState('');
  const [currentModel] = useState('gemma2:2b');
  const [avgResponseTime, setAvgResponseTime] = useState(0);
  const [totalMessages, setTotalMessages] = useState(0);
  
  const wsRef = useRef<WebSocket | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  // Conectar WebSocket para tempo real
  useEffect(() => {
    const connectWebSocket = () => {
      wsRef.current = new WebSocket('ws://localhost:8000/ws');
      
      wsRef.current.onopen = () => {
        console.log('🔌 Conectado ao servidor tempo real');
      };
      
      wsRef.current.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        if (data.type === 'chat_response') {
          const newMessage: Message = {
            id: Date.now().toString(),
            role: 'assistant',
            content: data.content,
            timestamp: new Date(),
            processingTime: data.processing_time
          };
          
          setMessages(prev => [...prev, newMessage]);
          setIsProcessing(false);
          
          // Atualizar estatísticas
          if (data.processing_time) {
            setTotalMessages(prev => prev + 1);
            setAvgResponseTime(prev => 
              (prev * (totalMessages) + data.processing_time) / (totalMessages + 1)
            );
          }
          
          // Auto-play da resposta
          speakText(data.content);
        }
      };
      
      wsRef.current.onclose = () => {
        console.log('🔌 Desconectado do servidor');
        // Reconectar após 3 segundos
        setTimeout(connectWebSocket, 3000);
      };
    };
    
    connectWebSocket();
    
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [totalMessages]);

  // Função para falar texto
  const speakText = (text: string) => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 1.0;
      utterance.pitch = 1.0;
      utterance.volume = 0.8;
      
      // Escolher voz em inglês
      const voices = speechSynthesis.getVoices();
      const englishVoice = voices.find(voice => 
        voice.lang.includes('en') && voice.name.includes('Female')
      ) || voices.find(voice => voice.lang.includes('en'));
      
      if (englishVoice) {
        utterance.voice = englishVoice;
      }
      
      speechSynthesis.speak(utterance);
    }
  };

  // Iniciar gravação
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];
      
      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };
      
      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        await processAudio(audioBlob);
        
        // Parar stream
        stream.getTracks().forEach(track => track.stop());
      };
      
      mediaRecorderRef.current.start();
      setIsRecording(true);
      
    } catch (error) {
      console.error('Erro ao acessar microfone:', error);
      alert('Erro ao acessar microfone. Verifique as permissões.');
    }
  };

  // Parar gravação
  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  // Processar áudio
  const processAudio = async (audioBlob: Blob) => {
    setIsProcessing(true);
    
    try {
      const formData = new FormData();
      formData.append('audio', audioBlob, 'audio.wav');
      
      const response = await fetch('http://localhost:8000/speech-to-text-fast', {
        method: 'POST',
        body: formData,
      });
      
      if (response.ok) {
        const data = await response.json();
        const transcribedText = data.text;
        
        if (transcribedText.trim()) {
          await sendMessage(transcribedText);
        } else {
          setIsProcessing(false);
        }
      }
    } catch (error) {
      console.error('Erro no processamento de áudio:', error);
      setIsProcessing(false);
    }
  };

  // Enviar mensagem
  const sendMessage = async (text: string) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: text,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsProcessing(true);
    
    // Enviar via WebSocket para tempo real
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'chat',
        content: text
      }));
    }
  };

  // Enviar mensagem de texto
  const handleTextSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputText.trim()) {
      sendMessage(inputText.trim());
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-4xl mx-auto">
        {/* Header com estatísticas */}
        <div className="bg-white rounded-lg shadow-lg p-4 mb-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Zap className="text-yellow-500 w-6 h-6" />
              <h1 className="text-xl font-bold text-gray-800">
                English Teacher - Real-time Mode
              </h1>
            </div>
            
            <div className="flex items-center space-x-6 text-sm">
              <div className="flex items-center space-x-2">
                <Cpu className="w-4 h-4 text-blue-500" />
                <span className="text-gray-600">Modelo: {currentModel}</span>
              </div>
              
              <div className="flex items-center space-x-2">
                <Clock className="w-4 h-4 text-green-500" />
                <span className="text-gray-600">
                  Resp. média: {avgResponseTime.toFixed(2)}s
                </span>
              </div>
              
              <div className="text-gray-600">
                Mensagens: {totalMessages}
              </div>
            </div>
          </div>
        </div>

        {/* Container de mensagens */}
        <div className="bg-white rounded-lg shadow-lg h-96 mb-4 overflow-y-auto p-4">
          {messages.length === 0 ? (
            <div className="text-center text-gray-500 mt-8">
              <Zap className="w-12 h-12 mx-auto mb-4 text-yellow-500" />
              <p className="text-lg font-medium">Modo Tempo Real Ativo!</p>
              <p className="text-sm mt-2">
                Clique no microfone e comece a falar em inglês.
                <br />
                Respostas super rápidas garantidas! ⚡
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                      message.role === 'user'
                        ? 'bg-blue-500 text-white'
                        : 'bg-gray-200 text-gray-800'
                    }`}
                  >
                    <p className="text-sm">{message.content}</p>
                    {message.processingTime && (
                      <p className="text-xs mt-1 opacity-70">
                        ⚡ {message.processingTime.toFixed(2)}s
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Controles */}
        <div className="bg-white rounded-lg shadow-lg p-4">
          {/* Indicador de status */}
          <div className="mb-4 text-center">
            {isProcessing && (
              <div className="inline-flex items-center space-x-2 text-blue-600">
                <div className="animate-spin w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full"></div>
                <span className="text-sm">Processando em tempo real...</span>
              </div>
            )}
          </div>

          {/* Botão de gravação */}
          <div className="flex items-center justify-center mb-4">
            <button
              onClick={isRecording ? stopRecording : startRecording}
              disabled={isProcessing}
              className={`w-16 h-16 rounded-full flex items-center justify-center transition-all duration-200 ${
                isRecording
                  ? 'bg-red-500 hover:bg-red-600 animate-pulse'
                  : 'bg-blue-500 hover:bg-blue-600'
              } text-white disabled:opacity-50 disabled:cursor-not-allowed`}
            >
              {isRecording ? (
                <MicOff className="w-8 h-8" />
              ) : (
                <Mic className="w-8 h-8" />
              )}
            </button>
          </div>

          {/* Input de texto alternativo */}
          <form onSubmit={handleTextSubmit} className="flex space-x-2">
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Ou digite sua mensagem em inglês..."
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isProcessing}
            />
            <button
              type="submit"
              disabled={!inputText.trim() || isProcessing}
              className="px-6 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Enviar
            </button>
          </form>

          {/* Dicas de uso */}
          <div className="mt-4 text-xs text-gray-500 text-center">
            💡 Dica: Fale claramente e pause entre frases para melhor reconhecimento.
            <br />
            🎯 Modo otimizado para conversas rápidas e dinâmicas!
          </div>
        </div>
      </div>
    </div>
  );
};

export default RealTimeChat;
