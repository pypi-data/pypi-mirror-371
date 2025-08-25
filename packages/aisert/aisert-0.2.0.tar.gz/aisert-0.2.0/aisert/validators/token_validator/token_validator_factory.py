from .common_token_validators import AnthropicTokenValidator, GoogleTokenValidator, HuggingFaceTokenValidator, \
    OpenAITokenValidator
from .token_validator_base import TokenValidatorBase
from ...exception import TokenValidationError


class TokenValidatorFactory:
    """
    Factory class for creating instances of token validators based on the model provider.
    This class provides a method to get an instance of a specific token validator
    based on the model provider and token model.
    """
    _token_validators = {
        "anthropic": AnthropicTokenValidator,
        "google": GoogleTokenValidator,
        "huggingface": HuggingFaceTokenValidator,
        "openai": OpenAITokenValidator
    }

    @classmethod
    def register_token_validator(cls, model_provider: str, token_validator_class):
        """
        A class method ot register custom token validators
        :param model_provider: provider of the model
        :param token_validator_class: custom token validator class
        """
        if not (isinstance(token_validator_class, type) and issubclass(token_validator_class, TokenValidatorBase)):
            raise TokenValidationError("token_validator_class must be a subclass of TokenValidatorBase.")

        cls._token_validators[model_provider] = token_validator_class

    @staticmethod
    def get_instance(model_provider: str, token_model: str = None, token_encoding: str = None, api_key: str = None, **kwargs):
        """
        Get an instance of TokenValidator with the specified provider and model.
        :param model_provider: Provider name
        :param token_model: Model name
        :param token_encoding: Encoding method
        :param api_key: API key if needed
        :return: An instance of TokenValidator.
        """
        if not model_provider:
            raise TokenValidationError("model_provider must be provided.")

        if model_provider in TokenValidatorFactory._token_validators:
            token_validator_cls = TokenValidatorFactory._token_validators[model_provider]
            # Pass all relevant arguments, let validator decide what to use
            return token_validator_cls.get_instance(
                token_model=token_model, 
                token_encoding=token_encoding, 
                api_key=api_key, 
                **kwargs
            )
        else:
            raise TokenValidationError(f"Unsupported model provider: {model_provider}")
