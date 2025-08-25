import logging
from typing import Optional
from aisert.config.defaults import DefaultConfig


class AisertConfig:
    """Configuration settings for Aisert validation operations.
    
    Supports token counting and semantic similarity validation with various providers.
    
    Args:
        token_provider: Token counting provider ("openai", "anthropic", "huggingface")
        token_model: Model name for token counting
        token_encoding: Specific encoding for tokenization (OpenAI only)
        semantic_provider: Semantic similarity provider ("openai", "sentence_transformers", "tfidf")
        semantic_model: Model name for semantic similarity
    
    Example:
        >>> config = AisertConfig(
        ...     token_provider="openai", 
        ...     token_model="gpt-4",
        ...     semantic_provider="sentence_transformers",
        ...     semantic_model="all-MiniLM-L6-v2"
        ... )
    """

    def __init__(self, token_provider: str = None, token_model: str = None, token_encoding: str = None,
                 semantic_provider: str = None, semantic_model: str = None):
        self._token_provider = token_provider
        self._token_model = token_model
        self._token_encoding = token_encoding

        self._semantic_provider = semantic_provider
        self._semantic_model = semantic_model

        self.logger = logging.getLogger(self.__class__.__name__)

    @property
    def token_provider(self):
        return self._token_provider

    @property
    def token_model(self):
        return self._token_model

    @property
    def token_encoding(self):
        return self._token_encoding

    @property
    def semantic_provider(self):
        return self._semantic_provider

    @property
    def semantic_model(self):
        return self._semantic_model

    def has_token_config(self) -> bool:
        """Check if token config is set."""
        return self._token_provider is not None

    def has_semantic_config(self) -> bool:
        """Check if semantic config is set."""
        return self._semantic_provider is not None

    @classmethod
    def set_defaults(cls, token_provider: str = None, token_model: str = None, token_encoding: str = None,
                     semantic_provider: str = None, semantic_model: str = None):
        """Set global default configuration values.
        
        Args:
            token_provider: Default token counting provider
            token_model: Default token counting model
            token_encoding: Default token encoding
            semantic_provider: Default semantic similarity provider
            semantic_model: Default semantic similarity model
        
        Example:
            >>> AisertConfig.set_defaults(token_provider="anthropic", token_model="claude-3")
        """
        if token_provider:
            DefaultConfig.token_provider = token_provider
        if token_model:
            DefaultConfig.token_model = token_model
        if token_encoding is not None:
            DefaultConfig.token_encoding = token_encoding
        if semantic_provider:
            DefaultConfig.semantic_provider = semantic_provider
        if semantic_model:
            DefaultConfig.semantic_model = semantic_model

    @classmethod
    def get_default_config(cls) -> "AisertConfig":
        """Get default configuration with all default values applied.
        
        Returns:
            AisertConfig: Configuration instance with default values
        
        Example:
            >>> config = AisertConfig.get_default_config()
            >>> print(config.token_provider)
            openai
        """
        return DefaultConfig.apply_all_defaults(cls)

    def __repr__(self):
        parts = []
        if self.has_token_config():
            parts.append(f"token({self.token_provider}, {self.token_model})")
        if self.has_semantic_config():
            parts.append(f"semantic({self.semantic_provider}, {self.semantic_model})")
        return f"AisertConfig({', '.join(parts)})"
