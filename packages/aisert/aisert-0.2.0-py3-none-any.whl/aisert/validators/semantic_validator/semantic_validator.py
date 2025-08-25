"""Semantic validation wrapper for consistent interface."""

from .semantic_validator_factory import SemanticValidatorFactory
from .semantic_validator_base import SemanticValidatorBase
from ...exception import SemanticValidationError


class SemanticValidator(SemanticValidatorBase):
    """Validates semantic similarity between texts."""

    def __init__(self, config):
        super().__init__()
        if not config or not config.has_semantic_config():
            raise SemanticValidationError("Semantic validation requires semantic configuration")
        self.provider = config.semantic_provider
        self.model_name = config.semantic_model

    def validate(self, text1: str, text2: str, threshold: float = 0.8, **kwargs):
        """Validates semantic similarity between two texts."""
        try:
            semantic_validator = SemanticValidatorFactory.get_instance(
                provider=self.provider,
                model_name=self.model_name
            )
            
            return semantic_validator.validate(text1, text2, threshold)

        except SemanticValidationError:
            raise
        except Exception as e:
            raise SemanticValidationError(f"Unexpected error: {e}") from e