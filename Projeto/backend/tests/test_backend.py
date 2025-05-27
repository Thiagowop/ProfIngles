#!/usr/bin/env python3
"""
Script de teste para o English Teacher Voice Chatbot
Este script testa as funcionalidades principais do backend
"""

import requests
import json
import time
import os
from pathlib import Path

# Configurações
BASE_URL = "http://localhost:8000"
TEST_AUDIO_PATH = "test_audio.wav"

def print_status(message, status="info"):
    """Imprime mensagem com status colorido"""
    colors = {
        "info": "\033[94m",      # Azul
        "success": "\033[92m",   # Verde
        "warning": "\033[93m",   # Amarelo
        "error": "\033[91m",     # Vermelho
        "reset": "\033[0m"       # Reset
    }
    print(f"{colors.get(status, '')}{message}{colors['reset']}")

def test_health_check():
    """Testa o endpoint de health check"""
    print_status("🔍 Testando health check...", "info")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_status("✅ Backend está rodando!", "success")
            print(f"   - Whisper: {'✅' if data.get('whisper_loaded') else '❌'}")
            print(f"   - TTS: {'✅' if data.get('tts_loaded') else '❌'}")
            print(f"   - Ollama: {'✅' if data.get('ollama_available') else '❌'}")
            return True
        else:
            print_status(f"❌ Health check falhou: {response.status_code}", "error")
            return False
    except requests.exceptions.RequestException as e:
        print_status(f"❌ Erro de conexão: {e}", "error")
        print_status("💡 Certifique-se de que o backend está rodando em http://localhost:8000", "warning")
        return False

def test_chat():
    """Testa o endpoint de chat"""
    print_status("💬 Testando chat...", "info")
    
    test_messages = [
        "Hello! I want to practice English.",
        "Can you help me with pronunciation?",
        "What is the difference between 'there', 'their' and 'they're'?"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n📝 Teste {i}: {message}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/chat",
                json={"message": message},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print_status("✅ Resposta recebida:", "success")
                print(f"🤖 Professor: {data['response'][:100]}...")
            else:
                print_status(f"❌ Erro no chat: {response.status_code}", "error")
                print(f"Resposta: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print_status(f"❌ Erro de conexão no chat: {e}", "error")

def test_conversation_history():
    """Testa o histórico de conversas"""
    print_status("\n📋 Testando histórico de conversas...", "info")
    
    try:
        response = requests.get(f"{BASE_URL}/conversation-history")
        if response.status_code == 200:
            data = response.json()
            history = data.get('history', [])
            print_status(f"✅ Histórico obtido: {len(history)} mensagens", "success")
            
            for msg in history[-3:]:  # Últimas 3 mensagens
                role = "👤 Você" if msg['role'] == 'user' else "🤖 Professor"
                print(f"   {role}: {msg['content'][:50]}...")
        else:
            print_status(f"❌ Erro ao obter histórico: {response.status_code}", "error")
            
    except requests.exceptions.RequestException as e:
        print_status(f"❌ Erro de conexão no histórico: {e}", "error")

def test_clear_history():
    """Testa a limpeza do histórico"""
    print_status("\n🗑️ Testando limpeza do histórico...", "info")
    
    try:
        response = requests.delete(f"{BASE_URL}/conversation-history")
        if response.status_code == 200:
            print_status("✅ Histórico limpo com sucesso!", "success")
        else:
            print_status(f"❌ Erro ao limpar histórico: {response.status_code}", "error")
            
    except requests.exceptions.RequestException as e:
        print_status(f"❌ Erro de conexão na limpeza: {e}", "error")

def create_test_audio():
    """Cria um arquivo de áudio de teste simples"""
    try:
        import numpy as np
        import soundfile as sf
        
        # Gerar tom simples de teste
        duration = 2.0  # segundos
        sample_rate = 22050
        frequency = 440  # A4
        
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio = 0.3 * np.sin(2 * np.pi * frequency * t)
        
        sf.write(TEST_AUDIO_PATH, audio, sample_rate)
        return True
    except ImportError:
        print_status("⚠️ Não foi possível criar áudio de teste (numpy/soundfile não disponível)", "warning")
        return False

def test_speech_to_text():
    """Testa o endpoint de speech-to-text"""
    print_status("\n🎤 Testando Speech-to-Text...", "info")
    
    if not os.path.exists(TEST_AUDIO_PATH):
        if not create_test_audio():
            print_status("❌ Não foi possível testar STT sem arquivo de áudio", "error")
            return
    
    try:
        with open(TEST_AUDIO_PATH, 'rb') as audio_file:
            files = {'audio': ('test.wav', audio_file, 'audio/wav')}
            response = requests.post(f"{BASE_URL}/speech-to-text", files=files, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print_status("✅ Speech-to-Text funcionando!", "success")
            print(f"📝 Texto detectado: {data.get('text', 'Nenhum texto')}")
        else:
            print_status(f"❌ Erro no STT: {response.status_code}", "error")
            print(f"Resposta: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print_status(f"❌ Erro de conexão no STT: {e}", "error")

def main():
    """Função principal"""
    print_status("🎓 English Teacher Voice Chatbot - Teste do Backend", "info")
    print_status("=" * 60, "info")
    
    # Teste 1: Health Check
    if not test_health_check():
        print_status("\n❌ Backend não está funcionando. Parando testes.", "error")
        return
    
    # Teste 2: Chat
    test_chat()
    
    # Teste 3: Histórico
    test_conversation_history()
    
    # Teste 4: Speech-to-Text
    test_speech_to_text()
    
    # Teste 5: Limpar histórico
    test_clear_history()
    
    # Limpeza
    if os.path.exists(TEST_AUDIO_PATH):
        os.remove(TEST_AUDIO_PATH)
    
    print_status("\n🎉 Testes concluídos!", "success")
    print_status("💡 Se todos os testes passaram, o backend está funcionando corretamente!", "info")

if __name__ == "__main__":
    main()
