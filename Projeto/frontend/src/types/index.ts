export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  audioUrl?: string;
}

export interface ConversationState {
  messages: Message[];
  isLoading: boolean;
  isRecording: boolean;
  isPlaying: boolean;
}

export interface APIResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

export interface SpeechToTextResponse {
  text: string;
}

export interface ChatResponse {
  response: string;
}

export interface HealthCheck {
  status: string;
  whisper_loaded: boolean;
  tts_loaded: boolean;
  ollama_available: boolean;
  current_model?: string;
  available_models?: string[];
  tts_engines?: string[];
}
