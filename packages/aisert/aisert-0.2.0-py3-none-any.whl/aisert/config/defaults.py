from typing import Dict


class DefaultConfig:
    """
    Default configuration for Aisert
    This class holds the default settings for the Asert application.
    """

    # Default values for the configuration
    token_encoding: str = None
    token_model: str = "gpt-3.5-turbo"
    token_provider: str = "openai"
    semantic_provider: str = "openai"
    semantic_model: str = "text-embedding-3-small"
    


    @staticmethod
    def to_dict() -> Dict[str, str]:
        """
        Converts the DefaultConfig to a dictionary.
        :return: A dictionary containing the default configuration values.
        """
        return {
            "token_encoding": DefaultConfig.token_encoding,
            "token_model": DefaultConfig.token_model,
            "token_provider": DefaultConfig.token_provider,
            "semantic_provider": DefaultConfig.semantic_provider,
            "semantic_model": DefaultConfig.semantic_model,
        }

    @staticmethod
    def apply_all_defaults(config_class):
        """Apply all default configurations."""
        return config_class(
            token_provider=DefaultConfig.token_provider,
            token_model=DefaultConfig.token_model,
            token_encoding=DefaultConfig.token_encoding,
            semantic_provider=DefaultConfig.semantic_provider,
            semantic_model=DefaultConfig.semantic_model
        )
