#!/usr/bin/env python
"""
Script de diagnóstico para verificar modelos e engines TTS
English Teacher Voice Chatbot
"""
import os
import sys
import json
import requests
import time
from pathlib import Path

# Cores para terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    """Imprime um cabeçalho formatado"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD} {text} {Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.END}")

def print_section(text):
    """Imprime uma seção formatada"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}[{text}]{Colors.END}")
    print(f"{Colors.BLUE}{'-' * 40}{Colors.END}")

def print_success(text):
    """Imprime uma mensagem de sucesso"""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_warning(text):
    """Imprime uma mensagem de aviso"""
    print(f"{Colors.YELLOW}⚠️ {text}{Colors.END}")

def print_error(text):
    """Imprime uma mensagem de erro"""
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_info(text):
    """Imprime uma mensagem informativa"""
    print(f"{Colors.CYAN}ℹ️ {text}{Colors.END}")

def check_backend_status(base_url="http://localhost:8000"):
    """Verifica o status do backend"""
    print_section("Verificando status do backend")
    
    try:
        # Verificar root endpoint
        root_response = requests.get(f"{base_url}/", timeout=5)
        if root_response.status_code == 200:
            print_success(f"API base respondendo: {root_response.json()}")
        else:
            print_error(f"API base retornou código {root_response.status_code}")
            return False
            
        # Verificar health endpoint
        health_response = requests.get(f"{base_url}/health", timeout=5)
        if health_response.status_code == 200:
            health_data = health_response.json()
            print_success("Health check bem-sucedido:")
            for key, value in health_data.items():
                status_color = Colors.GREEN if value == True else Colors.YELLOW
                print(f"  - {key}: {status_color}{value}{Colors.END}")
            
            if not health_data.get("ollama_available"):
                print_warning("Ollama não está disponível - isso afetará os modelos LLM")
                
            return True
        else:
            print_error(f"Health check falhou com código {health_response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print_error(f"Não foi possível conectar ao backend em {base_url}")
        print_info("Certifique-se de que o servidor backend está rodando")
        return False
    except Exception as e:
        print_error(f"Erro verificando backend: {e}")
        return False

def get_models(base_url="http://localhost:8000"):
    """Tenta obter a lista de modelos"""
    print_section("Verificando modelos disponíveis")
    endpoints = ["/models", "/ai-models", "/available-models", "/llm-models"]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                models = response.json()
                print_success(f"Modelos disponíveis via {endpoint}:")
                print(json.dumps(models, indent=2))
                return models
            elif response.status_code == 404:
                print_warning(f"Endpoint {endpoint} não encontrado")
            else:
                print_warning(f"Endpoint {endpoint} retornou código {response.status_code}")
        except Exception as e:
            print_warning(f"Erro acessando {endpoint}: {e}")
    
    print_info("Tentando listar modelos via Ollama diretamente...")
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json()
            print_success("Modelos Ollama disponíveis:")
            model_names = [model['name'] for model in models['models']]
            print(json.dumps(model_names, indent=2))
            return model_names
        else:
            print_error(f"Erro acessando Ollama API: {response.status_code}")
    except Exception as e:
        print_error(f"Erro acessando Ollama API: {e}")
    
    print_error("Não foi possível obter a lista de modelos")
    return []

def get_tts_engines(base_url="http://localhost:8000"):
    """Tenta obter a lista de engines TTS"""
    print_section("Verificando engines TTS")
    endpoints = ["/tts-engines", "/tts/engines", "/voices", "/tts/voices"]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                engines = response.json()
                print_success(f"Engines TTS via {endpoint}:")
                print(json.dumps(engines, indent=2))
                return engines
            elif response.status_code == 404:
                print_warning(f"Endpoint {endpoint} não encontrado")
            else:
                print_warning(f"Endpoint {endpoint} retornou código {response.status_code}")
        except Exception as e:
            print_warning(f"Erro acessando {endpoint}: {e}")
    
    # Tentar extrair do health
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            if 'tts_engines' in health_data:
                print_success("Engines TTS via /health:")
                print(json.dumps(health_data['tts_engines'], indent=2))
                return health_data['tts_engines']
    except Exception as e:
        pass
    
    print_error("Não foi possível obter a lista de engines TTS")
    return []

def check_api_functionality(base_url="http://localhost:8000"):
    """Verifica a funcionalidade básica da API"""
    print_section("Verificando funcionalidade da API")
    
    endpoints = [
        {"path": "/", "method": "GET", "name": "Root"},
        {"path": "/health", "method": "GET", "name": "Health Check"},
        {"path": "/conversation-history", "method": "GET", "name": "Conversation History"}
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.request(
                endpoint["method"].lower(),
                f"{base_url}{endpoint['path']}",
                timeout=5
            )
            
            if response.status_code < 400:
                print_success(f"{endpoint['name']} ({endpoint['path']}) - OK ({response.status_code})")
            else:
                print_error(f"{endpoint['name']} ({endpoint['path']}) - Falhou ({response.status_code})")
                
        except Exception as e:
            print_error(f"{endpoint['name']} ({endpoint['path']}) - Erro: {e}")

def suggest_fixes():
    """Sugere correções para possíveis problemas"""
    print_section("Sugestões para corrigir problemas")
    
    print_info("1. Se os modelos não aparecem na interface:")
    print("   - Verifique se o endpoint /models existe no backend")
    print("   - Adicione um endpoint GET /models que retorne a lista de modelos")
    print("   - Exemplos de implementação:")
    print("""
    @app.get("/models")
    async def get_models():
        """Lista todos os modelos disponíveis"""
        try:
            ollama_models = ollama.list()
            return {
                "models": [m["name"] for m in ollama_models["models"]]
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao listar modelos: {str(e)}")
    """)
    
    print_info("\n2. Se os engines TTS não aparecem:")
    print("   - Adicione um endpoint GET /tts-engines que liste as engines")
    print("   - Exemplos de implementação:")
    print("""
    @app.get("/tts-engines")
    async def get_tts_engines():
        """Retorna as engines TTS disponíveis"""
        if not tts_manager.engines:
            await tts_manager.initialize()
        
        return {
            "engines": list(tts_manager.engines.keys())
        }
    """)
    
    print_info("\n3. Para corrigir problema de conexão WebSocket:")
    print("   - Garanta que frontend e backend usam a mesma rota (/ws)")
    print("   - Verifique nas ferramentas de desenvolvedor do navegador se há erros de conexão")

def main():
    """Função principal"""
    print_header("DIAGNÓSTICO - ENGLISH TEACHER VOICE CHATBOT")
    
    backend_url = "http://localhost:8000"  # URL padrão
    
    if len(sys.argv) > 1:
        backend_url = sys.argv[1]
        print_info(f"Usando URL do backend: {backend_url}")
    
    # Verificar status do backend
    backend_ok = check_backend_status(backend_url)
    if not backend_ok:
        print_error("Não foi possível conectar ao backend. Verifique se o servidor está rodando.")
        return
    
    # Tentar obter modelos
    models = get_models(backend_url)
    
    # Tentar obter engines TTS
    tts_engines = get_tts_engines(backend_url)
    
    # Verificar funcionalidade da API
    check_api_functionality(backend_url)
    
    # Sugerir correções
    suggest_fixes()
    
    print_header("DIAGNÓSTICO CONCLUÍDO")

if __name__ == "__main__":
    main()
