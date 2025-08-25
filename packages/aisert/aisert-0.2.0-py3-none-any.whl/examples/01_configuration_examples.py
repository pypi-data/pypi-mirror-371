"""
Configuration Examples - Different ways to configure Aisert

Shows all configuration options and patterns.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aisert import AisertConfig


def default_configuration():
    """Using default configuration - no setup required."""
    print("=== Default Configuration ===")
    
    config = AisertConfig.get_default_config()
    print(f"Result: {config}")
    # Expected: AisertConfig(token(openai, gpt-3.5-turbo), semantic(openai, text-embedding-3-small))


def constructor_configuration():
    """Using constructor parameters for custom configuration."""
    print("\n=== Constructor Configuration ===")
    
    # Token counting only
    config1 = AisertConfig(token_provider="openai", token_model="gpt-4")
    print(f"Token only: {config1}")
    # Expected: AisertConfig(token(openai, gpt-4))
    
    # Semantic validation only
    config2 = AisertConfig(semantic_provider="sentence_transformers", semantic_model="all-MiniLM-L6-v2")
    print(f"Semantic only: {config2}")
    # Expected: AisertConfig(semantic(sentence_transformers, all-MiniLM-L6-v2))
    
    # Full configuration
    config3 = AisertConfig(
        token_provider="anthropic",
        token_model="claude-3",
        semantic_provider="tfidf"
    )
    print(f"Full config: {config3}")
    # Expected: AisertConfig(token(anthropic, claude-3), semantic(tfidf, None))


def global_defaults_configuration():
    """Setting global defaults for all future configurations."""
    print("\n=== Global Defaults Configuration ===")
    
    # Set custom global defaults
    AisertConfig.set_defaults(
        token_provider="anthropic",
        token_model="claude-3",
        semantic_provider="tfidf"
    )
    
    config = AisertConfig.get_default_config()
    print(f"Custom defaults: {config}")
    # Expected: AisertConfig(token(anthropic, claude-3), semantic(tfidf, text-embedding-3-small))
    
    # Reset to original defaults
    AisertConfig.set_defaults(
        token_provider="openai",
        token_model="gpt-3.5-turbo",
        semantic_provider="openai",
        semantic_model="text-embedding-3-small"
    )


def provider_specific_configurations():
    """Examples for different AI providers."""
    print("\n=== Provider-Specific Configurations ===")
    
    # OpenAI configuration
    openai_config = AisertConfig(
        token_provider="openai",
        token_model="gpt-4",
        token_encoding="cl100k_base",
        semantic_provider="openai",
        semantic_model="text-embedding-3-large"
    )
    print(f"OpenAI: {openai_config}")
    
    # Anthropic configuration
    anthropic_config = AisertConfig(
        token_provider="anthropic",
        token_model="claude-3-sonnet",
        semantic_provider="sentence_transformers",
        semantic_model="all-MiniLM-L6-v2"
    )
    print(f"Anthropic: {anthropic_config}")
    
    # Lightweight configuration (no heavy dependencies)
    lightweight_config = AisertConfig(
        semantic_provider="tfidf"  # No torch/transformers needed
    )
    print(f"Lightweight: {lightweight_config}")


if __name__ == "__main__":
    print("🔧 Aisert Configuration Examples")
    print("=" * 50)
    
    default_configuration()
    constructor_configuration()
    global_defaults_configuration()
    provider_specific_configurations()
    
    print("\n✨ Configuration examples completed!")