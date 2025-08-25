"""Tests for AisertConfig functionality."""
import pytest
import tempfile
import json
import os

from aisert import AisertConfig
from aisert.config.defaults import DefaultConfig


class TestAisertConfig:
    """Test AisertConfig functionality."""

    def test_init_with_constructor(self):
        """Test config initialization with constructor."""
        config = AisertConfig(
            token_provider="openai",
            token_model="gpt-4",
            token_encoding="cl100k_base",
            semantic_provider="sentence_transformers",
            semantic_model="all-MiniLM-L6-v2"
        )
        assert config.token_model == "gpt-4"
        assert config.token_provider == "openai"
        assert config.token_encoding == "cl100k_base"
        assert config.semantic_model == "all-MiniLM-L6-v2"

    def test_get_default_config(self):
        """Test getting default configuration."""
        config = AisertConfig.get_default_config()
        assert config.token_model == "gpt-3.5-turbo"
        assert config.token_provider == "openai"
        assert config.semantic_model == "all-MiniLM-L6-v2"

    def test_constructor_with_all_params(self):
        """Test constructor with all parameters."""
        config = AisertConfig(
            token_provider="anthropic",
            token_model="claude-3",
            semantic_provider="openai",
            semantic_model="text-embedding-3-small"
        )
        assert config.token_provider == "anthropic"
        assert config.token_model == "claude-3"
        assert config.semantic_provider == "openai"
        assert config.semantic_model == "text-embedding-3-small"

    def test_has_config_methods(self):
        """Test has_*_config methods."""
        config = AisertConfig()
        assert not config.has_token_config()
        assert not config.has_semantic_config()
        
        config.with_token("openai", "gpt-4")
        assert config.has_token_config()
        assert not config.has_semantic_config()
        
        config.with_semantic("sentence_transformers", "all-MiniLM-L6-v2")
        assert config.has_token_config()
        assert config.has_semantic_config()

    def test_get_default_config_method(self):
        """Test get_default_config method."""
        config = AisertConfig.get_default_config()
        assert config.has_token_config()
        assert config.has_semantic_config()
        assert config.token_model == "gpt-3.5-turbo"
        assert config.semantic_model == "text-embedding-3-small"

    def test_set_defaults_method(self):
        """Test set_defaults method."""
        # Set custom defaults
        AisertConfig.set_defaults(
            token_provider="anthropic",
            token_model="claude-3",
            semantic_provider="tfidf"
        )
        
        # Get default config should use new defaults
        config = AisertConfig.get_default_config()
        assert config.token_provider == "anthropic"
        assert config.token_model == "claude-3"
        assert config.semantic_provider == "tfidf"
        
        # Reset to original defaults
        AisertConfig.set_defaults(
            token_provider="openai",
            token_model="gpt-3.5-turbo",
            semantic_provider="openai",
            semantic_model="text-embedding-3-small"
        )

    def test_repr(self):
        """Test string representation of config."""
        config = (
            AisertConfig()
            .with_token("openai", "gpt-4")
        )
        repr_str = repr(config)
        assert "gpt-4" in repr_str
        assert "openai" in repr_str


class TestDefaultConfig:
    """Test DefaultConfig functionality."""

    def test_to_dict(self):
        """Test converting default config to dictionary."""
        config_dict = DefaultConfig.to_dict()
        assert isinstance(config_dict, dict)
        assert "token_model" in config_dict
        assert "model_provider" in config_dict
        assert config_dict["token_model"] == "gpt-3.5-turbo"
        assert config_dict["token_provider"] == "openai"

    def test_default_values(self):
        """Test default configuration values."""
        assert DefaultConfig.token_model == "gpt-3.5-turbo"
        assert DefaultConfig.token_provider == "openai"
        assert DefaultConfig.semantic_model == "text-embedding-3-small"
        assert DefaultConfig.token_encoding is None