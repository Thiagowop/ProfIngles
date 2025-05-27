# -*- coding: utf-8 -*-
"""
Sistema de gerenciamento de modelos LLM para o chatbot de inglês
"""
import asyncio
import time
from typing import Dict, List, Optional
from dataclasses import dataclass
import ollama


@dataclass
class AIModelConfig:
    name: str
    size: str
    ram_usage: str
    speed_rating: int  # 1-5, onde 5 é mais rápido
    conversation_quality: int  # 1-5, onde 5 é melhor qualidade
    best_for: List[str]
    context_window: int
    temperature: float
    system_prompt: str


class AIModelManager:
    def __init__(self):
        self.models = {
            # Modelos rápidos para conversas casuais
            "gemma2:2b": AIModelConfig(
                name="gemma2:2b",
                size="1.6GB",
                ram_usage="~2-3GB",
                speed_rating=5,
                conversation_quality=3,
                best_for=["conversas rápidas",
                          "prática básica", "vocabulário"],
                context_window=8192,
                temperature=0.7,
                system_prompt="You are a friendly English tutor. Keep responses SHORT (1-2 sentences max). Focus on natural conversation. Correct mistakes gently."
            ),

            # Modelos balanceados para conversas dinâmicas
            "llama3.2:3b": AIModelConfig(
                name="llama3.2:3b",
                size="2.0GB",
                ram_usage="~3-4GB",
                speed_rating=4,
                conversation_quality=4,
                best_for=["conversas dinâmicas", "explicações", "role-play"],
                context_window=131072,
                temperature=0.8,
                system_prompt="You are an engaging English conversation partner. Be natural, ask follow-up questions, and create dynamic conversations. Keep responses conversational (2-3 sentences). Gently correct errors."
            ),

            "qwen2.5:3b": AIModelConfig(
                name="qwen2.5:3b",
                size="1.9GB",
                ram_usage="~3-4GB",
                speed_rating=4,
                conversation_quality=4,
                best_for=["ensino estruturado",
                          "gramática", "explicações detalhadas"],
                context_window=32768,
                temperature=0.6,
                system_prompt="You are a professional English teacher. Provide clear explanations and examples. Keep responses focused and educational (2-4 sentences). Always explain corrections."
            ),

            # Modelos premium para conversas avançadas
            "qwen2.5:7b": AIModelConfig(
                name="qwen2.5:7b",
                size="4.4GB",
                ram_usage="~6-8GB",
                speed_rating=3,
                conversation_quality=5,
                best_for=["ensino avançado", "business English",
                          "preparação para exames"],
                context_window=32768,
                temperature=0.7,
                system_prompt="You are an expert English instructor specializing in advanced learning. Provide detailed feedback and sophisticated language examples. Tailor difficulty to student level."
            ),

            # Modelos customizados com contexto estendido
            "qwen2.5-extended": AIModelConfig(
                name="qwen2.5-extended",
                size="4.7GB",
                ram_usage="~6-8GB",
                speed_rating=3,
                conversation_quality=5,
                best_for=["conversas longas",
                          "contexto estendido", "memorização"],
                context_window=8192,
                temperature=0.8,
                system_prompt="You are an advanced English conversation partner with excellent memory. Maintain context from earlier in our conversation. Provide natural, flowing dialogue."
            ),

            "qwen2.5-ultra-extended": AIModelConfig(
                name="qwen2.5-ultra-extended",
                size="4.7GB",
                ram_usage="~6-8GB",
                speed_rating=2,
                conversation_quality=5,
                best_for=["conversas muito longas",
                          "máximo contexto", "sessões estendidas"],
                context_window=32768,
                temperature=0.8,
                system_prompt="You are a premium English tutor with exceptional memory and context awareness. Remember details from throughout our entire conversation. Provide sophisticated, contextual responses."
            ),

            "llama3.1:8b": AIModelConfig(
                name="llama3.1:8b",
                size="4.9GB",
                ram_usage="~7-9GB",
                speed_rating=2,
                conversation_quality=5,
                best_for=["conversas premium",
                          "análise profunda", "máxima qualidade"],
                context_window=131072,
                temperature=0.9,
                system_prompt="You are a world-class English conversation partner and tutor. Provide the highest quality dialogue with perfect grammar awareness and cultural context."
            )}
        self.current_model = "gemma2:2b"  # Modelo padrão rápido
        self.available_models = []
        self.model_performance = {
            model_name: {
                "response_time": 0,
                "tokens_per_second": 0
            } for model_name in self.models.keys()
        }

    async def initialize(self, skip_benchmark=False):
        """Inicializa o gerenciador verificando modelos disponíveis"""
        await self.check_available_models()
        if not skip_benchmark:
            await self.benchmark_models()
        else:
            print("⚡ Pulando benchmark para inicialização rápida")
            # Usar velocidades estimadas dos modelos configurados
            for model_name in self.available_models:
                if model_name in self.models:
                    speed_rating = self.models[model_name].speed_rating
                    estimated_tokens_per_sec = speed_rating * 2  # Estimativa baseada no rating
                    self.model_performance[model_name] = {
                        "response_time": 2.0 / speed_rating,  # Estimativa
                        "tokens_per_second": estimated_tokens_per_sec,
                        "estimated": True
                    }

    async def check_available_models(self):
        """Verifica quais modelos estão disponíveis no sistema"""
        try:
            models = ollama.list()
            # Handle different possible structures from ollama.list()
            if isinstance(models, dict) and 'models' in models:
                model_list = models['models']
            else:
                model_list = models if isinstance(models, list) else []

            self.available_models = []
            for model in model_list:
                if isinstance(model, dict):
                    # Try different possible key names
                    model_name = model.get('name') or model.get(
                        'model') or model.get('id', '')
                    if model_name:
                        # Extract name:tag format
                        if ':' in model_name:
                            self.available_models.append(model_name)
                        else:
                            self.available_models.append(
                                f"{model_name}:latest")
                elif isinstance(model, str):
                    self.available_models.append(model)

            # Sempre usar todos os modelos configurados independentemente do Ollama
            self.available_models = list(self.models.keys())
            print("✅ Usando todos os modelos configurados")

            print(f"✅ Modelos disponíveis: {self.available_models}")
        except Exception as e:
            print(f"❌ Erro ao verificar modelos: {e}")
            # Usar todos os modelos configurados como fallback em caso de erro
            self.available_models = list(self.models.keys())
            print(
                f"⚠️ Erro ao conectar com Ollama, usando {len(self.available_models)} modelos configurados como fallback")

    async def benchmark_models(self):
        """Testa velocidade de resposta dos modelos disponíveis"""
        test_prompt = "Hi! How are you today?"

        for model_name in self.available_models:
            if model_name in self.models:
                try:
                    start_time = time.time()
                    response = ollama.chat(
                        model=model_name,
                        messages=[{"role": "user", "content": test_prompt}],
                        # Resposta curta para teste
                        options={"num_predict": 20}
                    )
                    response_time = time.time() - start_time

                    self.model_performance[model_name] = {
                        "response_time": response_time,
                        "tokens_per_second": 20 / response_time if response_time > 0 else 0
                    }
                    print(
                        f"🚀 {model_name}: {response_time:.2f}s ({20/response_time:.1f} tokens/s)")

                except Exception as e:
                    print(f"❌ Erro testando {model_name}: {e}")

    def get_model_recommendations(self, conversation_type: str = "casual") -> List[str]:
        """Retorna modelos recomendados para tipo de conversa"""
        recommendations = []

        type_mapping = {
            "casual": ["conversas rápidas", "prática básica"],
            "dynamic": ["conversas dinâmicas", "role-play"],
            "educational": ["ensino estruturado", "gramática"],
            "advanced": ["conversas complexas", "tópicos avançados"],
            "business": ["business English", "preparação para exames"],
            "extended": ["conversas longas", "contexto estendido"],
            "ultra": ["conversas muito longas", "máximo contexto", "sessões estendidas"],
            "premium": ["conversas premium", "análise profunda", "máxima qualidade"]
        }

        target_uses = type_mapping.get(
            conversation_type, ["conversas rápidas"])

        for model_name, config in self.models.items():
            if model_name in self.available_models:
                if any(use in config.best_for for use in target_uses):
                    recommendations.append(model_name)

        # Ordena por velocidade para conversas casuais, qualidade para avançadas
        if conversation_type in ["casual", "dynamic"]:
            recommendations.sort(
                key=lambda x: self.models[x].speed_rating, reverse=True)
        else:
            recommendations.sort(
                key=lambda x: self.models[x].conversation_quality, reverse=True)

        return recommendations[:3]  # Top 3

    def switch_model(self, model_name: str) -> bool:
        """Alterna para um modelo específico"""
        if model_name in self.available_models and model_name in self.models:
            self.current_model = model_name
            print(f"🔄 Alternado para modelo: {model_name}")
            return True
        return False

    def get_current_config(self) -> AIModelConfig:
        """Retorna configuração do modelo atual"""
        return self.models[self.current_model]

    def get_model_info(self, model_name: str = None) -> Dict:
        """Retorna informações detalhadas de um modelo"""
        model = model_name or self.current_model
        if model in self.models:
            config = self.models[model]
            performance = self.model_performance.get(model, {})

            return {
                "name": config.name,
                "size": config.size,
                "ram_usage": config.ram_usage,
                "speed_rating": config.speed_rating,
                "quality_rating": config.conversation_quality,
                "best_for": config.best_for,
                "context_window": config.context_window,
                "available": model in self.available_models,
                "performance": performance
            }
        return {}

    async def auto_select_model(self, user_message: str, conversation_history: List = None) -> str:
        """Seleciona automaticamente o melhor modelo baseado no contexto"""
        message_length = len(user_message.split())
        history_length = len(
            conversation_history) if conversation_history else 0

        # Regras para seleção automática
        if history_length > 20:
            # Conversas muito longas - usa modelo ultra-extended
            candidates = self.get_model_recommendations("ultra")
        elif history_length > 10:
            # Conversas médias/longas - usa modelo extended
            candidates = self.get_model_recommendations("extended")
        elif message_length <= 5 and history_length <= 3:
            # Conversas rápidas e simples
            candidates = self.get_model_recommendations("casual")
        elif "explain" in user_message.lower() or "grammar" in user_message.lower():
            # Pedidos educacionais
            candidates = self.get_model_recommendations("educational")
        elif "business" in user_message.lower() or "professional" in user_message.lower():
            # Contexto profissional
            candidates = self.get_model_recommendations("business")
        elif message_length > 20:
            # Mensagens complexas - usa modelo premium
            candidates = self.get_model_recommendations("premium")
        else:
            # Conversas dinâmicas padrão
            candidates = self.get_model_recommendations("dynamic")

        # Seleciona o primeiro candidato disponível
        for model in candidates:
            if model in self.available_models:
                if model != self.current_model:
                    self.switch_model(model)
                return model

        return self.current_model


# Instância global
ai_manager = AIModelManager()
