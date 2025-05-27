# English Teacher Voice Chatbot

Um chatbot de voz para ensino de inglês, combinando reconhecimento de fala, modelos de linguagem (LLM) e múltiplos motores de texto-para-fala (TTS), com backend FastAPI e frontend React.

---

## 🌟 Funcionalidades
- **Reconhecimento de Fala**: Transcrição de áudio com Faster-Whisper
- **Modelos de Linguagem (LLM)**: Integração com Ollama (llama3, Qwen, etc.)
- **Texto-para-Fala (TTS)**: Pyttsx3, Kokoro, Google, Coqui
- **Backend FastAPI**: API moderna com WebSocket
- **Frontend React**: Interface web responsiva com Tailwind CSS

---

## 📋 Requisitos
- **Python**: 3.11.x recomendado
- **Node.js**: 18+ (frontend)
- **Ollama**: Serviço local de LLM ([https://ollama.ai](https://ollama.ai))
- **Windows** (PowerShell) ou Linux/Mac (ajuste comandos conforme o SO)

---

## 📁 Estrutura do Projeto

```
Projeto/
├── backend/
│   ├── mainfinal.py           # Backend principal
│   ├── main_advanced.py       # Backend otimizado (multi-modelo)
│   ├── llm_models.py          # Gerenciamento de LLM
│   ├── tts_manager.py         # Gerenciamento de TTS
│   ├── ai_models.py           # Configuração de IA
│   ├── coqui_tts.py           # Engine Coqui TTS
│   ├── kokoro_tts.py          # Engine Kokoro TTS
│   ├── kokoro_neural_tts.py   # Engine Kokoro Neural TTS
│   ├── google_tts.py          # Engine Google TTS
│   ├── requirements.txt       # Dependências
│   ├── models/                # Modelos auxiliares
│   ├── uploads/               # Uploads de áudio
│   ├── tests/                 # Testes automatizados
│   └── backup/                # Scripts/variantes antigos (IGNORADO NO GIT)
├── frontend/                  # Aplicação React
│   ├── package.json           # Dependências e scripts
│   ├── tsconfig.json          # Configuração TypeScript
│   ├── tailwind.config.js     # Tailwind CSS
│   ├── postcss.config.js      # PostCSS
│   ├── public/                # Arquivos estáticos
│   └── src/                   # Código-fonte React
├── uploads/                   # Uploads globais (IGNORADO NO GIT)
├── venv/                      # Ambiente virtual Python (IGNORADO NO GIT)
├── .gitignore                 # Ignora backup, venv, uploads, etc.
├── start_full_app.ps1         # Script para iniciar backend e frontend (opcional)
└── README.md                  # Este arquivo
```

---

## 🚀 Como rodar o projeto

### 1. Backend (FastAPI)

```powershell
cd Projeto/backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main_advanced:app --reload --host 0.0.0.0 --port 8000
```

- Para rodar o backend manualmente, sempre ative o ambiente virtual antes.
- O backend pode ser iniciado também pelo script `start_full_app.ps1` na raiz do projeto (opcional).

### 2. Frontend (React)

```powershell
cd Projeto/frontend
npm install
npm start
```

Acesse: [http://localhost:3000](http://localhost:3000)

---

## 🔗 Endpoints principais do backend

- `/` : Status do backend
- `/health` : Healthcheck
- `/models` : Modelos LLM disponíveis
- `/tts/engines` : Engines TTS disponíveis
- `/tts` : Geração de áudio TTS
- `/transcribe` : Transcrição de áudio
- `/chat` : Chat com seleção automática de modelo
- `/ws` : WebSocket

---

## 🛠️ Dicas, Manutenção e Troubleshooting

- **Coqui TTS**: Se não for usar, remova do `tts_manager.py` para evitar erro de inicialização (arquivo `mecabrc` ausente).
- **Kokoro TTS**: Avisos de "Defaulting repo_id" são normais e não afetam o funcionamento.
- **Pydantic DeprecationWarning**: Troque `stats.dict()` por `stats.model_dump()` em `main_advanced.py` para compatibilidade com Pydantic v2.
- **FastAPI on_event**: Migre para handler de lifespan futuramente para evitar avisos de depreciação.
- **Ambiente virtual**: Sempre ative o venv antes de rodar o backend para garantir dependências corretas.
- **Limpeza**: Para liberar espaço, remova pastas `__pycache__` e arquivos `.pyc` periodicamente.
- **Backup**: A pasta `backup/` guarda scripts antigos e variantes, não é usada em produção e está ignorada no git.
- **Uploads**: Pastas `uploads/` (backend e raiz) são ignoradas no git para evitar versionar arquivos de áudio temporários.
- **Logs**: Consulte logs do backend para detalhes de erros e avisos.

---

## 🧹 Limpeza e Estrutura para GitHub

- Apenas arquivos essenciais permanecem na raiz e subpastas.
- `.gitignore` já ignora `backup/`, `uploads/`, `venv/` e arquivos temporários.
- Scripts antigos, variantes e requirements alternativos estão em `backup/`.
- O projeto está pronto para versionamento e publicação.

---

## 🤝 Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests com melhorias, correções ou sugestões.

---

## 📄 Licença

MIT
