# -*- coding: utf-8 -*-
"""
Sistema de gerenciamento dinâmico de modelos para diferentes tipos de conversação
"""
import asyncio
import time
from typing import Dict, List, Optional
from dataclasses import dataclass
import ollama

@dataclass
class ModelConfig:
    name: str
    size: str
    ram_usage: str
    speed_rating: int  # 1-5, onde 5 é mais rápido
    conversation_quality: int  # 1-5, onde 5 é melhor qualidade
    best_for: List[str]
    context_window: int
    temperature: float
    system_prompt: str

class ModelManager:
    def __init__(self):
        self.models = {
            # Modelos ultra-rápidos para conversas casuais
            "gemma2:2b": ModelConfig(
                name="gemma2:2b",
                size="1.6GB",
                ram_usage="~2-3GB",
                speed_rating=5,
                conversation_quality=3,
                best_for=["conversas rápidas", "prática básica", "vocabulário"],
                context_window=8192,
                temperature=0.7,
                system_prompt="You are a friendly English tutor. Keep responses SHORT (1-2 sentences max). Focus on natural conversation. Correct mistakes gently."
            ),
            
            # Modelos balanceados para conversas dinâmicas
            "llama3.2:3b": ModelConfig(
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
            
            "qwen2.5:3b": ModelConfig(
                name="qwen2.5:3b",
                size="1.9GB", 
                ram_usage="~3-4GB",
                speed_rating=4,
                conversation_quality=4,
                best_for=["ensino estruturado", "gramática", "explicações detalhadas"],
                context_window=32768,
                temperature=0.6,
                system_prompt="You are a professional English teacher. Provide clear explanations and examples. Keep responses focused and educational (2-4 sentences). Always explain corrections."
            ),
            
            # Modelos premium para conversas avançadas
            "qwen2.5:7b": ModelConfig(
                name="qwen2.5:7b",
                size="4.4GB",
                ram_usage="~6-8GB", 
                speed_rating=3,
                conversation_quality=5,
                best_for=["ensino avançado", "business English", "preparação para exames"],
                context_window=32768,
                temperature=0.7,
                system_prompt="You are an expert English instructor specializing in advanced learning. Provide detailed feedback and sophisticated language examples. Tailor difficulty to student level."
            ),
            
            # Modelos customizados com contexto estendido
            "qwen2.5-extended": ModelConfig(
                name="qwen2.5-extended",
                size="4.7GB",
                ram_usage="~6-8GB",
                speed_rating=3,
                conversation_quality=5,
                best_for=["conversas longas", "contexto estendido", "memorização"],
                context_window=8192,
                temperature=0.8,
                system_prompt="You are an advanced English conversation partner with excellent memory. Maintain context from earlier in our conversation. Provide natural, flowing dialogue."
            ),
            
            "qwen2.5-ultra-extended": ModelConfig(
                name="qwen2.5-ultra-extended",
                size="4.7GB", 
                ram_usage="~6-8GB",
                speed_rating=2,
                conversation_quality=5,
                best_for=["conversas muito longas", "máximo contexto", "sessões estendidas"],
                context_window=32768,
                temperature=0.8,
                system_prompt="You are a premium English tutor with exceptional memory and context awareness. Remember details from throughout our entire conversation. Provide sophisticated, contextual responses."
            ),
            
            "llama3.1:8b": ModelConfig(
                name="llama3.1:8b",
                size="4.9GB",
                ram_usage="~7-9GB",
                speed_rating=2,
                conversation_quality=5,
                best_for=["conversas premium", "análise profunda", "máxima qualidade"],
                context_window=131072,
                temperature=0.9,
                system_prompt="You are a world-class English conversation partner and tutor. Provide the highest quality dialogue with perfect grammar awareness and cultural context."
            )
        }
        
        self.current_model = "gemma2:2b"  # Modelo padrão rápido
        self.available_models = []
        self.model_performance = {}
        
    async def initialize(self):
        """Inicializa o gerenciador verificando modelos disponíveis"""
        await self.check_available_models()
        await self.benchmark_models()
        
    async def check_available_models(self):
        """Verifica quais modelos estão disponíveis no sistema"""
        try:
            models = ollama.list()
            self.available_models = [model['name'].split(':')[0] + ':' + model['name'].split(':')[1] 
                                   for model in models['models']]
            print(f"✅ Modelos disponíveis: {self.available_models}")
        except Exception as e:
            print(f"❌ Erro ao verificar modelos: {e}")
            self.available_models = ["gemma2:2b"]  # Fallback
            
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
                        options={"num_predict": 20}  # Resposta curta para teste
                    )
                    response_time = time.time() - start_time
                    
                    self.model_performance[model_name] = {
                        "response_time": response_time,
                        "tokens_per_second": 20 / response_time if response_time > 0 else 0
                    }
                    print(f"🚀 {model_name}: {response_time:.2f}s ({20/response_time:.1f} tokens/s)")
                    
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
        
        target_uses = type_mapping.get(conversation_type, ["conversas rápidas"])
        
        for model_name, config in self.models.items():
            if model_name in self.available_models:
                if any(use in config.best_for for use in target_uses):
                    recommendations.append(model_name)
                    
        # Ordena por velocidade para conversas casuais, qualidade para avançadas
        if conversation_type in ["casual", "dynamic"]:
            recommendations.sort(key=lambda x: self.models[x].speed_rating, reverse=True)
        else:
            recommendations.sort(key=lambda x: self.models[x].conversation_quality, reverse=True)
            
        return recommendations[:3]  # Top 3
        
    def switch_model(self, model_name: str) -> bool:
        """Alterna para um modelo específico"""
        if model_name in self.available_models and model_name in self.models:
            self.current_model = model_name
            print(f"🔄 Alternado para modelo: {model_name}")
            return True
        return False
        
    def get_current_config(self) -> ModelConfig:
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
        history_length = len(conversation_history) if conversation_history else 0
        
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
model_manager = ModelManager()
