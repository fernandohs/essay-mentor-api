"""
LangChain LLM Adapter.
Provides LangChain integration for advanced LLM features (chains, memory, RAG, agents).
"""

from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import StrOutputParser
from pydantic import SecretStr
from app.adapters.base import BaseLLMAdapter
from app.core.config import settings


class LangChainAdapter(BaseLLMAdapter):
    """
    LangChain adapter for advanced LLM features.
    
    Supports:
    - OpenAI models (GPT-4, GPT-3.5, etc.)
    - Ollama models (Llama, Mistral, Qwen, etc.)
    - Chains, Memory, RAG, Agents (via LangChain)
    """
    
    def __init__(self, model: str, base_url: str, api_key: Optional[str] = None):
        super().__init__(model, base_url, api_key)
        self.llm = self._create_llm()
        self.output_parser = StrOutputParser()
    
    def _create_llm(self):
        """
        Create LangChain LLM based on provider.
        
        Returns:
            LangChain LLM instance
        """
        # Detect provider by base_url or model
        if self.base_url and "api.openai.com" in self.base_url:
            return ChatOpenAI(
                model=self.model,
                temperature=settings.LLM_TEMPERATURE,
                api_key=SecretStr(self.api_key) if self.api_key else None,
                max_tokens=settings.LLM_NUM_PREDICT
            )
        elif self.base_url and "ollama" in self.base_url.lower():
            return ChatOllama(
                model=self.model,
                base_url=self.base_url,
                temperature=settings.LLM_TEMPERATURE,
                num_predict=settings.LLM_NUM_PREDICT
            )
        else:
            # Default to Ollama for other cases
            return ChatOllama(
                model=self.model,
                base_url=settings.OLLAMA_URL,
                temperature=settings.LLM_TEMPERATURE,
                num_predict=settings.LLM_NUM_PREDICT
            )
    
    def generate(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        num_predict: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Generate text using LangChain.
        
        Args:
            prompt: The prompt to send to the LLM
            temperature: Temperature setting for generation
            num_predict: Maximum number of tokens to generate
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Generated text response from the LLM
            
        Raises:
            ConnectionError: If LLM request fails
        """
        try:
            # Update temperature if provided
            if temperature is not None:
                # Create new LLM with updated temperature
                if isinstance(self.llm, ChatOpenAI):
                    self.llm = ChatOpenAI(
                        model=self.model,
                        temperature=temperature,
                        api_key=SecretStr(self.api_key) if self.api_key else None,
                        max_tokens=num_predict or self.llm.max_tokens
                    )
                elif isinstance(self.llm, ChatOllama):
                    self.llm = ChatOllama(
                        model=self.model,
                        base_url=self.base_url,
                        temperature=temperature,
                        num_predict=num_predict or settings.LLM_NUM_PREDICT
                    )
            
            # Invoke LLM with prompt
            response = self.llm.invoke([HumanMessage(content=prompt)])
            
            # Parse and return content
            return self.output_parser.parse(response)
            
        except Exception as e:
            raise ConnectionError(f"Error generating response with LangChain: {e}")
    
    def get_llm(self):
        """
        Get the underlying LangChain LLM instance.
        Useful for creating chains and advanced workflows.
        
        Returns:
            LangChain LLM instance
        """
        return self.llm
    
    def get_chain(self):
        """
        Get a basic prompt LLM chain for this adapter.
        
        Returns:
            LangChain chain instance
        """
        from langchain.chains import LLMChain
        from langchain_core.prompts import PromptTemplate
        
        prompt_template = PromptTemplate(
            input_variables=["prompt"],
            template="{prompt}"
        )
        
        return LLMChain(llm=self.llm, prompt=prompt_template)

__all__ = ["LangChainAdapter"]
