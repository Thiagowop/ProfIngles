#!/bin/bash

echo "🚀 Instalando English Teacher Voice Chatbot - Backend"
echo "=================================================="

# Verificar se Python está instalado
if ! command -v python &> /dev/null; then
    echo "❌ Python não está instalado. Por favor, instale Python 3.8 ou superior."
    exit 1
fi

# Verificar versão do Python
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
echo "✅ Python $PYTHON_VERSION encontrado"

# Criar ambiente virtual (opcional, mas recomendado)
read -p "Deseja criar um ambiente virtual? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔧 Criando ambiente virtual..."
    python -m venv venv
    
    # Ativar ambiente virtual
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
    echo "✅ Ambiente virtual ativado"
fi

# Instalar dependências
echo "📦 Instalando dependências Python..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ Backend instalado com sucesso!"
echo ""
echo "⚠️  IMPORTANTE: Antes de iniciar, certifique-se de:"
echo "1. Instalar e executar Ollama: https://ollama.ai/"
echo "2. Baixar um modelo de linguagem: ollama pull llama3.1:8b"
echo "3. Iniciar o Ollama: ollama serve"
echo ""
echo "Para iniciar o backend, execute:"
echo "python main.py"
