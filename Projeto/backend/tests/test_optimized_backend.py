#!/usr/bin/env python3
"""
Teste da versão otimizada do main_advanced.py
"""
import asyncio
import time
import requests
from pathlib import Path

async def test_optimized_backend():
    """Testa o backend otimizado"""
    print("🧪 Testando Backend Otimizado")
    print("=" * 50)
    
    # Aguarda um pouco para o servidor inicializar
    print("⏳ Aguardando inicialização do servidor...")
    await asyncio.sleep(5)
    
    base_url = "http://localhost:8000"
    
    # Teste 1: Endpoint raiz
    print("\n1️⃣ Testando endpoint raiz...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data.get('status', 'unknown')}")
            print(f"📊 Tempo de inicialização: {data.get('startup_time', 'N/A')}s")
            print(f"🎯 Versão: {data.get('version', 'N/A')}")
        else:
            print(f"❌ Erro: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
    
    # Teste 2: Health check
    print("\n2️⃣ Testando health check...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data.get('status', 'unknown')}")
            components = data.get('components', {})
            for name, status in components.items():
                status_icon = "✅" if status else "❌"
                print(f"   {status_icon} {name}: {status}")
        else:
            print(f"❌ Health check falhou: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro no health check: {e}")
    
    # Teste 3: Status detalhado
    print("\n3️⃣ Testando status detalhado...")
    try:
        response = requests.get(f"{base_url}/status")
        if response.status_code == 200:
            data = response.json()
            system = data.get('system', {})
            print(f"✅ Sistema inicializado: {system.get('initialized', False)}")
            print(f"📈 Tempo de startup: {system.get('startup_time', 'N/A')}s")
            
            ollama = data.get('ollama', {})
            print(f"🤖 Ollama disponível: {ollama.get('available', False)}")
            print(f"🏃 Ollama executando: {ollama.get('running', False)}")
            
            ai_models = data.get('ai_models', {})
            models_count = len(ai_models.get('available', []))
            print(f"🧠 Modelos AI: {models_count} disponíveis")
            
            tts = data.get('tts', {})
            engines_count = len(tts.get('engines', []))
            print(f"🎤 Engines TTS: {engines_count} disponíveis")
            
        else:
            print(f"❌ Status detalhado falhou: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro no status: {e}")
    
    # Teste 4: TTS Engines
    print("\n4️⃣ Testando TTS engines...")
    try:
        response = requests.get(f"{base_url}/tts/engines")
        if response.status_code == 200:
            data = response.json()
            engines = data.get('available_engines', {})
            print(f"✅ {len(engines)} engines TTS encontradas:")
            for name, info in engines.items():
                engine_name = info.get('name', 'Unknown')
                print(f"   🎭 {name}: {engine_name}")
        else:
            print(f"❌ TTS engines falhou: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro no TTS: {e}")
    
    print(f"\n🎉 Teste completo!")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(test_optimized_backend())
