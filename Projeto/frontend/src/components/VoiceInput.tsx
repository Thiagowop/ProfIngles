import React, { useState } from 'react';
import { Mic, MicOff, Send, Square } from 'lucide-react';
import { useAudioRecorder } from '../hooks/useAudioRecorder';

interface VoiceInputProps {
  onSendMessage: (text: string) => void;
  onSendAudio: (audioBlob: Blob) => void;
  isLoading: boolean;
}

export const VoiceInput: React.FC<VoiceInputProps> = ({
  onSendMessage,
  onSendAudio,
  isLoading,
}) => {
  const [textInput, setTextInput] = useState('');
  const [inputMode, setInputMode] = useState<'text' | 'voice'>('voice');
  const { isRecording, audioBlob, startRecording, stopRecording, clearRecording } = useAudioRecorder();

  const handleStartRecording = async () => {
    try {
      clearRecording();
      await startRecording();
    } catch (error) {
      alert('Erro ao acessar o microfone. Verifique as permissões.');
    }
  };

  const handleStopRecording = () => {
    stopRecording();
  };

  const handleSendAudio = () => {
    if (audioBlob) {
      onSendAudio(audioBlob);
      clearRecording();
    }
  };

  const handleSendText = () => {
    if (textInput.trim()) {
      onSendMessage(textInput.trim());
      setTextInput('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendText();
    }
  };

  return (
    <div className="bg-white border-t border-gray-200 p-4">
      {/* Mode Toggle */}
      <div className="flex justify-center mb-4">
        <div className="flex bg-gray-100 rounded-lg p-1">
          <button
            onClick={() => setInputMode('voice')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              inputMode === 'voice'
                ? 'bg-white text-primary-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            Voz
          </button>
          <button
            onClick={() => setInputMode('text')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              inputMode === 'text'
                ? 'bg-white text-primary-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            Texto
          </button>
        </div>
      </div>

      {/* Voice Input */}
      {inputMode === 'voice' && (
        <div className="flex flex-col items-center space-y-4">
          {/* Recording Status */}
          {isRecording && (
            <div className="flex items-center text-red-600">
              <div className="w-3 h-3 bg-red-600 rounded-full animate-pulse mr-2"></div>
              <span className="text-sm font-medium">Gravando...</span>
            </div>
          )}

          {/* Audio Preview */}
          {audioBlob && !isRecording && (
            <div className="flex items-center space-x-2 text-green-600">
              <Square size={16} />
              <span className="text-sm">Áudio gravado - pronto para enviar</span>
            </div>
          )}

          {/* Recording Button */}
          <div className="flex items-center space-x-4">
            {!isRecording ? (
              <button
                onClick={handleStartRecording}
                disabled={isLoading}
                className="w-16 h-16 bg-primary-500 hover:bg-primary-600 disabled:bg-gray-300 text-white rounded-full flex items-center justify-center transition-colors shadow-lg"
                title="Clique para gravar"
              >
                <Mic size={24} />
              </button>
            ) : (
              <button
                onClick={handleStopRecording}
                className="w-16 h-16 bg-red-500 hover:bg-red-600 text-white rounded-full flex items-center justify-center transition-colors shadow-lg animate-pulse"
                title="Clique para parar"
              >
                <MicOff size={24} />
              </button>
            )}

            {/* Send Audio Button */}
            {audioBlob && !isRecording && (
              <button
                onClick={handleSendAudio}
                disabled={isLoading}
                className="px-6 py-3 bg-secondary-500 hover:bg-secondary-600 disabled:bg-gray-300 text-white rounded-lg flex items-center space-x-2 transition-colors shadow-md"
              >
                <Send size={18} />
                <span>Enviar</span>
              </button>
            )}
          </div>

          <p className="text-xs text-gray-500 text-center max-w-sm">
            Clique no microfone para gravar sua pergunta em inglês
          </p>
        </div>
      )}

      {/* Text Input */}
      {inputMode === 'text' && (
        <div className="flex space-x-2">
          <textarea
            value={textInput}
            onChange={(e) => setTextInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Digite sua mensagem em inglês..."
            disabled={isLoading}
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:bg-gray-100"
            rows={2}
          />
          <button
            onClick={handleSendText}
            disabled={isLoading || !textInput.trim()}
            className="px-6 py-3 bg-primary-500 hover:bg-primary-600 disabled:bg-gray-300 text-white rounded-lg flex items-center justify-center transition-colors shadow-md"
            title="Enviar mensagem"
          >
            <Send size={18} />
          </button>
        </div>
      )}
    </div>
  );
};
