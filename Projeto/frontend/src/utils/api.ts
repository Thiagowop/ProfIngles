import axios from 'axios';
import { SpeechToTextResponse, ChatResponse, HealthCheck } from '../types';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

export const apiClient = {
  // Verificar saúde da API
  async healthCheck(): Promise<HealthCheck> {
    const response = await api.get<HealthCheck>('/health');
    return response.data;
  },

  // Speech to Text
  async speechToText(audioBlob: Blob): Promise<string> {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'audio.wav');
    
    const response = await api.post<SpeechToTextResponse>('/speech-to-text', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data.text;
  },

  // Chat com o professor
  async chatWithTeacher(message: string): Promise<string> {
    const response = await api.post<ChatResponse>('/chat', {
      message: message,
    });
    
    return response.data.response;
  },

  // Text to Speech (novo endpoint /tts)
  async textToSpeech(text: string): Promise<Blob> {
    const response = await api.post('/tts', { text }, { responseType: 'blob' });
    return response.data;
  },

  // Listar mecanismos TTS disponíveis
  async getTtsEngines(): Promise<{ available_engines: Record<string, any>; current_engine: string }> {
    const response = await api.get('/tts/engines');
    return response.data;
  },

  // Alternar mecanismo TTS
  async switchTtsEngine(engine: string): Promise<{ success: boolean; current_engine: string }> {
    const response = await api.post('/tts/switch', { engine });
    return response.data;
  },

  // Limpar histórico da conversa
  async clearHistory(): Promise<void> {
    await api.delete('/conversation-history');
  },

  // Obter histórico da conversa
  async getHistory(): Promise<any[]> {
    const response = await api.get('/conversation-history');
    return response.data.history;
  },
};

export default apiClient;
