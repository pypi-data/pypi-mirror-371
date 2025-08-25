from .common_semantic_validators import TFIDFSemanticValidator, HuggingFaceSemanticValidator, OpenAISemanticValidator, \
    SentenceTransformersSemanticValidator
from ...exception import SemanticValidationError


class SemanticValidatorFactory:
    """Factory for creating semantic validator instances based on provider."""

    _semantic_validators = {
        "sentence_transformers": SentenceTransformersSemanticValidator,
        "tfidf": TFIDFSemanticValidator,
        "huggingface": HuggingFaceSemanticValidator,
        "openai": OpenAISemanticValidator,
    }

    @classmethod
    def get_instance(cls, provider: str, model_name: str = None, api_key: str = None, **kwargs):
        """Get semantic validator instance for the specified provider."""
        if provider in cls._semantic_validators:
            validator_cls = cls._semantic_validators[provider]
            # Pass all relevant arguments, let validator decide what to use
            return validator_cls.get_instance(model_name=model_name, api_key=api_key, **kwargs)
        else:
            raise SemanticValidationError(f"Unsupported semantic provider: {provider}")

    @classmethod
    def register_semantic_validator(cls, provider: str, validator_class):
        """Register custom semantic validator."""
        if not (isinstance(validator_class, type) and hasattr(validator_class, 'get_instance')):
            raise SemanticValidationError("validator_class must have get_instance class method.")

        cls._semantic_validators[provider] = validator_class
