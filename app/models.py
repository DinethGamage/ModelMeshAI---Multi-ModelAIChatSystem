"""
LLM Model initialization and management.
Provides wrapper functions for different specialized models.
"""

from typing import Optional, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from app.config import config


class ModelManager:
    """Manages different LLM models for various tasks."""
    
    def __init__(self):
        """Initialize model manager with API key validation."""
        if not config.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is required")
        
        self._models: Dict[str, ChatGoogleGenerativeAI] = {}
        self._initialize_models()
    
    def _initialize_models(self) -> None:
        """Initialize all model variants."""
        model_types = ["general", "code", "math", "document"]
        
        for model_type in model_types:
            model_config = config.get_model_config(model_type)
            self._models[model_type] = ChatGoogleGenerativeAI(
                model=model_config["model_name"],
                temperature=model_config["temperature"],
                max_output_tokens=model_config["max_output_tokens"],
                google_api_key=config.GOOGLE_API_KEY,
            )
    
    def get_model(self, model_type: str = "general") -> ChatGoogleGenerativeAI:
        """
        Get a specific model by type.
        
        Args:
            model_type: Type of model (general, code, math, document)
            
        Returns:
            Initialized ChatGoogleGenerativeAI instance
        """
        if model_type not in self._models:
            model_type = "general"
        
        return self._models[model_type]
    
    def get_classification_model(self) -> ChatGoogleGenerativeAI:
        """
        Get model specifically for query classification.
        Uses fast, lightweight model for routing decisions.
        
        Returns:
            ChatGoogleGenerativeAI instance optimized for classification
        """
        return ChatGoogleGenerativeAI(
            model=config.GEMINI_MODEL_GENERAL,
            temperature=0.0,  # Deterministic for classification
            max_output_tokens=100,  # Short classification response
            google_api_key=config.GOOGLE_API_KEY,
        )
    
    def invoke_model(
        self,
        model_type: str,
        prompt: str,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Invoke a model with a prompt.
        
        Args:
            model_type: Type of model to use
            prompt: User prompt
            system_prompt: Optional system prompt for context
            
        Returns:
            Model response as string
        """
        model = self.get_model(model_type)
        
        if system_prompt:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
            response = model.invoke(messages)
        else:
            response = model.invoke(prompt)
        
        return response.content


# Global model manager instance
model_manager = ModelManager()
