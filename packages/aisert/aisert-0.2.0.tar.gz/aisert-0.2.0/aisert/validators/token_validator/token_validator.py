"""Token validation module for counting and validating token limits in text content."""
import json

from .token_validator_factory import TokenValidatorFactory
from ...exception import TokenValidationError
from ..validator import BaseValidator
from ...models.result import Result
from ...models.validator_enums import ValidatorEnums


class TokenValidator(BaseValidator):
    """Validates the number of tokens in a given text."""

    def __init__(self, config):
        super().__init__(ValidatorEnums.TOKENS)
        if not config or not config.has_token_config():
            raise TokenValidationError("Token validation requires token configuration")
        self.token_provider = config.token_provider
        self.token_model = config.token_model
        self.token_encoding = config.token_encoding

    def validate(self, text, token_limit: int = 100, **kwargs):
        """Validates the number of tokens in the text."""
        try:
            token_validator = TokenValidatorFactory.get_instance(
                model_provider=self.token_provider,
                token_model=self.token_model,
                token_encoding=self.token_encoding
            )
            
            if not isinstance(text, str):
                text = json.dumps(text)

            token_count = token_validator.count(text)
            self.logger.debug(f"Token count: {token_count}")

            if token_count > token_limit:
                raise TokenValidationError(
                    f"Token limit exceeded: {token_count} tokens found, limit is {token_limit}")
            
            return Result(self.validator_name, True, f"Token count {token_count} is within limit {token_limit}")

        except TokenValidationError:
            raise
        except Exception as e:
            raise TokenValidationError(f"Unexpected error: {e}") from e