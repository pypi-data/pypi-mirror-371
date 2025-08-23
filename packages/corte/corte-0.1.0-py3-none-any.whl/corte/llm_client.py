"""LLM client functionality for processing text with various AI providers."""

from typing import Dict, List, Optional, Any
import os
from abc import ABC, abstractmethod
import openai
import anthropic
from dotenv import load_dotenv

load_dotenv()

try:
    from langchain_core.language_models import BaseLLM
    from langchain_openai import ChatOpenAI
    from langchain_anthropic import ChatAnthropic
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_community.llms import Ollama
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False


class LLMClient(ABC):
    """Abstract base class for LLM clients."""
    
    @abstractmethod
    def process_text(self, text: str, prompt: str) -> str:
        """Process text with the LLM using the given prompt."""
        pass


class OpenAIClient(LLMClient):
    """OpenAI API client."""
    
    def __init__(self, model: str = "gpt-3.5-turbo", api_key: Optional[str] = None):
        """
        Initialize OpenAI client.
        
        Args:
            model: OpenAI model to use
            api_key: API key (defaults to OPENAI_API_KEY env var)
        """
        self.model = model
        self.client = openai.OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
    
    def process_text(self, text: str, prompt: str) -> str:
        """
        Process text using OpenAI API.
        
        Args:
            text: Input text to process
            prompt: System prompt for processing
            
        Returns:
            Processed text response
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content


class AnthropicClient(LLMClient):
    """Anthropic Claude API client."""
    
    def __init__(self, model: str = "claude-3-sonnet-20240229", api_key: Optional[str] = None):
        """
        Initialize Anthropic client.
        
        Args:
            model: Anthropic model to use
            api_key: API key (defaults to ANTHROPIC_API_KEY env var)
        """
        self.model = model
        self.client = anthropic.Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
    
    def process_text(self, text: str, prompt: str) -> str:
        """
        Process text using Anthropic API.
        
        Args:
            text: Input text to process
            prompt: System prompt for processing
            
        Returns:
            Processed text response
        """
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            system=prompt,
            messages=[
                {"role": "user", "content": text}
            ]
        )
        return response.content[0].text


class LangChainClient(LLMClient):
    """LangChain-based LLM client supporting multiple providers."""
    
    def __init__(self, provider: str, model: str = None, **kwargs):
        """
        Initialize LangChain client.
        
        Args:
            provider: LangChain provider ('langchain_openai', 'langchain_anthropic', 'langchain_google', 'ollama')
            model: Model name for the provider
            **kwargs: Additional arguments for model initialization
        """
        if not LANGCHAIN_AVAILABLE:
            raise ImportError("LangChain is not installed. Install with: pip install langchain")
        
        self.provider = provider.lower()
        self.model_name = model
        self.llm = self._create_langchain_model(model, **kwargs)
    
    def _create_langchain_model(self, model: str = None, **kwargs) -> BaseLLM:
        """Create appropriate LangChain model based on provider."""
        if self.provider == "langchain_openai":
            return ChatOpenAI(
                model=model or "gpt-3.5-turbo",
                api_key=kwargs.get('api_key') or os.getenv("OPENAI_API_KEY"),
                **{k: v for k, v in kwargs.items() if k != 'api_key'}
            )
        elif self.provider == "langchain_anthropic":
            return ChatAnthropic(
                model=model or "claude-3-sonnet-20240229",
                api_key=kwargs.get('api_key') or os.getenv("ANTHROPIC_API_KEY"),
                **{k: v for k, v in kwargs.items() if k != 'api_key'}
            )
        elif self.provider == "langchain_google":
            return ChatGoogleGenerativeAI(
                model=model or "gemini-pro",
                google_api_key=kwargs.get('api_key') or os.getenv("GOOGLE_API_KEY"),
                **{k: v for k, v in kwargs.items() if k != 'api_key'}
            )
        elif self.provider == "ollama":
            return Ollama(
                model=model or "llama2",
                base_url=kwargs.get('base_url', 'http://localhost:11434'),
                **{k: v for k, v in kwargs.items() if k not in ['api_key', 'base_url']}
            )
        else:
            raise ValueError(f"Unsupported LangChain provider: {self.provider}")
    
    def process_text(self, text: str, prompt: str) -> str:
        """
        Process text using LangChain model.
        
        Args:
            text: Input text to process
            prompt: System prompt for processing
            
        Returns:
            Processed text response
        """
        # Format the prompt and text for LangChain
        full_prompt = f"{prompt}\n\nText to process:\n{text}"
        
        try:
            response = self.llm.invoke(full_prompt)
            # Handle different response types from LangChain models
            if hasattr(response, 'content'):
                return response.content
            else:
                return str(response)
        except Exception as e:
            raise RuntimeError(f"LangChain processing failed: {str(e)}")


class LLMClientFactory:
    """Factory for creating LLM clients."""
    
    @staticmethod
    def create_client(provider: str, **kwargs) -> LLMClient:
        """
        Create an LLM client for the specified provider.
        
        Args:
            provider: LLM provider ('openai', 'anthropic', or LangChain providers)
            **kwargs: Additional arguments for client initialization
            
        Returns:
            LLM client instance
        """
        provider_lower = provider.lower()
        
        # Direct provider implementations
        if provider_lower == "openai":
            return OpenAIClient(**kwargs)
        elif provider_lower == "anthropic":
            return AnthropicClient(**kwargs)
        
        # LangChain providers
        langchain_providers = [
            "langchain_openai", "langchain_anthropic", 
            "langchain_google", "ollama"
        ]
        
        if provider_lower in langchain_providers:
            if not LANGCHAIN_AVAILABLE:
                raise ImportError(
                    f"LangChain is required for {provider} but not installed. "
                    "Install with: pip install langchain"
                )
            return LangChainClient(provider=provider_lower, **kwargs)
        
        raise ValueError(f"Unsupported provider: {provider}")
    
    @staticmethod
    def get_available_providers() -> List[str]:
        """Get list of available LLM providers."""
        providers = ["openai", "anthropic"]
        
        if LANGCHAIN_AVAILABLE:
            providers.extend([
                "langchain_openai", 
                "langchain_anthropic", 
                "langchain_google", 
                "ollama"
            ])
        
        return providers
    
    @staticmethod
    def get_langchain_status() -> Dict[str, Any]:
        """Get information about LangChain availability and providers."""
        return {
            "available": LANGCHAIN_AVAILABLE,
            "providers": [
                "langchain_openai", 
                "langchain_anthropic", 
                "langchain_google", 
                "ollama"
            ] if LANGCHAIN_AVAILABLE else [],
            "installation_command": "pip install langchain langchain-openai langchain-anthropic langchain-google-genai langchain-community"
        }