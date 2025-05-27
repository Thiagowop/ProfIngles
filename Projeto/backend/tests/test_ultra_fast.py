#!/usr/bin/env python3
"""
Teste rápido da versão ultra-otimizada
"""
import sys
import time
import requests
import json

def test_endpoints():
    """Testa os endpoints principais"""
    base_url = "http://127.0.0.1:8000"
    
    print("🧪 Testando endpoints da versão ULTRA-OTIMIZADA...")
    
    # Teste 1: Health check
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check: OK")
        else:
            print(f"❌ Health check: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check: {e}")
    
    # Teste 2: Status detalhado
    try:
        response = requests.get(f"{base_url}/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Status detalhado: OK")
            print(f"   - Inicialização completa: {data['system']['initialized']}")
            print(f"   - Tempo de startup: {data['system']['startup_time']:.2f}s")
            print(f"   - Modo ultra-fast: {data['system']['ultra_fast_mode']}")
        else:
            print(f"❌ Status detalhado: {response.status_code}")
    except Exception as e:
        print(f"❌ Status detalhado: {e}")
    
    # Teste 3: Lista de modelos
    try:
        response = requests.get(f"{base_url}/models", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Lista de modelos: OK")
            print(f"   - Modelos disponíveis: {len(data['available_models'])}")
            print(f"   - Modelo atual: {data['current_model']}")
        else:
            print(f"❌ Lista de modelos: {response.status_code}")
    except Exception as e:
        print(f"❌ Lista de modelos: {e}")
    
    # Teste 4: Engines TTS
    try:
        response = requests.get(f"{base_url}/tts/engines", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Engines TTS: OK")
            print(f"   - Engines disponíveis: {len(data['available_engines'])}")
            print(f"   - Engine atual: {data['current_engine']}")
            
            # Mostrar as engines TTS encontradas
            if data['available_engines']:
                print("   - Engines TTS:")
                for engine_name, engine_info in data['available_engines'].items():
                    if isinstance(engine_info, dict):
                        name = engine_info.get('name', engine_name)
                        print(f"     • {name}")
                    else:
                        print(f"     • {engine_name}")
        else:
            print(f"❌ Engines TTS: {response.status_code}")
    except Exception as e:
        print(f"❌ Engines TTS: {e}")
    
    # Teste 5: Chat simples
    try:
        chat_data = {
            "message": "Hello, how are you?",
            "conversation_type": "speed"
        }
        response = requests.post(f"{base_url}/chat", json=chat_data, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Chat: OK")
            print(f"   - Resposta: {data['response'][:50]}...")
            print(f"   - Tempo de resposta: {data['response_time']:.2f}s")
            print(f"   - Modelo usado: {data['model_used']}")
        else:
            print(f"❌ Chat: {response.status_code}")
    except Exception as e:
        print(f"❌ Chat: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando testes da versão ULTRA-OTIMIZADA...")
    print("📡 Aguardando servidor estar pronto...")
    
    # Aguardar servidor estar pronto
    for i in range(30):
        try:
            response = requests.get("http://127.0.0.1:8000/", timeout=2)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'ready':
                    print(f"✅ Servidor pronto em {i+1} tentativas!")
                    break
                else:
                    print(f"⏳ Tentativa {i+1}: Servidor ainda inicializando...")
            time.sleep(1)
        except:
            print(f"⏳ Tentativa {i+1}: Aguardando servidor...")
            time.sleep(1)
    else:
        print("❌ Timeout: Servidor não ficou pronto em 30 segundos")
        sys.exit(1)
    
    # Executar testes
    test_endpoints()
    print("\n🎉 Testes concluídos!")
