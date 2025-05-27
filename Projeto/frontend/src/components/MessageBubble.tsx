import React from 'react';
import { Message } from '../types';
import { User, Bot, Volume2, VolumeX } from 'lucide-react';

interface MessageBubbleProps {
  message: Message;
  onPlayAudio?: (text: string) => void;
  isPlayingAudio?: boolean;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({
  message,
  onPlayAudio,
  isPlayingAudio = false,
}) => {
  const isUser = message.role === 'user';
  
  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className={`flex mb-4 ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`flex max-w-xs lg:max-w-md ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
        {/* Avatar */}
        <div className={`flex-shrink-0 ${isUser ? 'ml-3' : 'mr-3'}`}>
          <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
            isUser 
              ? 'bg-primary-500 text-white' 
              : 'bg-secondary-500 text-white'
          }`}>
            {isUser ? <User size={20} /> : <Bot size={20} />}
          </div>
        </div>

        {/* Message Content */}
        <div className={`flex flex-col ${isUser ? 'items-end' : 'items-start'}`}>
          <div className={`px-4 py-2 rounded-lg shadow-md ${
            isUser
              ? 'bg-primary-500 text-white'
              : 'bg-white text-gray-800 border border-gray-200'
          }`}>
            <p className="text-sm">{message.content}</p>
          </div>
          
          {/* Timestamp and Audio Button */}
          <div className={`flex items-center mt-1 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
            <span className="text-xs text-gray-500">
              {formatTime(message.timestamp)}
            </span>
            
            {/* Audio Button for Assistant Messages */}
            {!isUser && onPlayAudio && (
              <button
                onClick={() => onPlayAudio(message.content)}
                disabled={isPlayingAudio}
                className={`ml-2 p-1 rounded-full transition-colors ${
                  isPlayingAudio
                    ? 'bg-secondary-200 text-secondary-600'
                    : 'hover:bg-gray-100 text-gray-600'
                }`}
                title="Ouvir mensagem"
              >
                {isPlayingAudio ? <VolumeX size={14} /> : <Volume2 size={14} />}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
