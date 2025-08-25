import logging
from typing import List, Optional

from .models.report import AisertReport

from .exception import AisertError

from .config.config import AisertConfig
from .models.result import AisertStatus, Result
from .validators.contains_validator import ContainsValidator
from .validators.not_contains_validator import NotContainsValidator
from .validators.schema_validator import SchemaValidator
from .validators.semantic_validator import SemanticValidator
from .validators.token_validator.token_validator import TokenValidator


class Aisert:
    """Main validation class for AI/LLM response validation.
    
    The :class:`Aisert` class provides a fluent interface for validating AI-generated
    content using multiple validation methods that can be chained together.
    
    Validation methods include:
    
    * :meth:`assert_schema` -- Validate against Pydantic models
    * :meth:`assert_contains` -- Check for required content
    * :meth:`assert_not_contains` -- Check for forbidden content
    * :meth:`assert_tokens` -- Validate token count limits
    * :meth:`assert_semantic_matches` -- Check semantic similarity
    
    Each validation method supports both strict mode (raises exceptions on failure)
    and non-strict mode (collects errors for later inspection).
    
    .. versionadded:: 0.1.0
    """

    def __init__(self, content, config: Optional[AisertConfig] = None):
        """Initialize Aisert with content to validate.
        
        Args:
            content: Text, dict, or list to validate (typically LLM response)
            config: Optional configuration for token counting and semantic models
        
        Example:
            >>> aisert = Aisert("Hello world")
            >>> config = AisertConfig(token_provider="openai", token_model="gpt-4")
            >>> aisert = Aisert("Hello world", config)
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.content = content
        self.status = AisertStatus()
        self.config = config if config is not None else AisertConfig.get_default_config()

    def assert_schema(self, schema, strict: bool = True):
        """
        Validate content against a Pydantic model schema.
        
        Args:
            schema: Pydantic model class or generic type to validate against
            strict: If True, raises exception on failure; if False, collects error
        
        Returns:
            Self for method chaining
        
        Raises:
            SchemaValidationError: If validation fails and strict=True
        
        Example:
            >>> aisert.assert_schema(UserModel)  # Validates JSON against UserModel
            <aisert.aisert.Aisert object at 0x...>
        """
        self.logger.debug(f"Checking if content is matching {schema}")
        self._validate(SchemaValidator(), strict, self.content, schema)
        return self

    def assert_contains(self, items: List[str], strict: bool = True):
        """Validate that content contains all specified items.
        
        :param items: List of strings that must be present in the content
        :type items: List[str]
        :param strict: If ``True``, raises exception on failure; if ``False``, collects error
        :type strict: bool
        :return: Self for method chaining
        :rtype: Aisert
        :raises ContainsValidationError: If any items are missing and *strict* is ``True``
        
        Example usage::
        
            aisert = Aisert("Hello world")
            aisert.assert_contains(["Hello", "world"])
        
        .. versionadded:: 0.1.0
        """
        self.logger.debug(f"Checking if content contains {items}")
        self._validate(ContainsValidator(), strict, self.content, items)
        return self

    def assert_not_contains(self, items: List[str], strict: bool = True):
        """
        Validate that content does NOT contain any of the specified items.
        
        Args:
            items: List of strings that must NOT be present in the content
            strict: If True, raises exception on failure; if False, collects error
        
        Returns:
            Self for method chaining
        
        Raises:
            ContainsValidationError: If any flagged items are found and strict=True
        
        Example:
            >>> aisert.assert_not_contains(["spam", "inappropriate"])
            <aisert.aisert.Aisert object at 0x...>
        """
        self.logger.debug(f"Checking if content not contains {items}")
        self._validate(NotContainsValidator(), strict, self.content, items)
        return self

    def assert_tokens(self, max_tokens: int, strict: bool = True):
        """
        Validate that content token count is within the specified limit.
        
        Uses the configured token model and provider for accurate counting.
        
        Args:
            max_tokens: Maximum number of tokens allowed
            strict: If True, raises exception on failure; if False, collects error
        
        Returns:
            Self for method chaining
        
        Raises:
            TokenValidationError: If token count exceeds limit and strict=True
        
        Example:
            >>> aisert.assert_tokens(max_tokens=100)  # Ensure response is under 100 tokens
            <aisert.aisert.Aisert object at 0x...>
        """
        self.logger.debug(f"Checking if tokens less than: {max_tokens}")
        self._validate(TokenValidator(self.config), strict, self.content, token_limit=max_tokens)
        return self

    def assert_semantic_matches(self, expected_text: str, threshold: float = 0.8, strict: bool = True):
        """
        Validate semantic similarity between content and expected text.
        
        Uses sentence transformers to compute cosine similarity between embeddings.
        Note: First use may take ~30 seconds to load the model.
        
        Args:
            expected_text: Text to compare against for semantic similarity
            threshold: Minimum similarity score (0.0 to 1.0) required to pass
            strict: If True, raises exception on failure; if False, collects error
        
        Returns:
            Self for method chaining
        
        Raises:
            SemanticValidationError: If similarity below threshold and strict=True
        
        Example:
            >>> aisert.assert_semantic_matches("Information about AI", threshold=0.75)
            <aisert.aisert.Aisert object at 0x...>
        """
        self.logger.debug(f"Checking semantic match")
        self._validate(SemanticValidator(self.config), strict, self.content, expected_text, threshold=threshold)
        return self

    def _validate(self, validator, strict, *args, **kwargs):
        """
        Calls the validate method of validator and updates result.
        :param validator: The validator instance.
        :param args: Positional arguments for the validator.
        :param kwargs: Keyword arguments for the validator.
        """
        try:
            result = validator.validate(*args, **kwargs)
            # self.logger.debug(f"{validator.validator_name} validation result: {result.status}")
        except AisertError as e:
            if strict:
                self.logger.error(f"{validator.validator_name} validation failed")
                raise
            else:
                self.logger.error(f"{validator.validator_name} validation failed: {str(e)}")
                result = Result(validator.validator_name, False, str(e))
        self.status.update(result)

    def collect(self):
        """Finalize validation chain and return comprehensive results.
        
        This method must be called at the end of a validation chain to execute
        all queued validations and return the results.
        
        :return: Validation report containing status and detailed results
        :rtype: AisertReport
        
        The returned :class:`AisertReport` contains:
        
        * ``status`` -- ``True`` if all validations passed, ``False`` otherwise
        * ``rules`` -- Dictionary mapping execution order to validation results
        
        Example usage::
        
            report = aisert.assert_contains(["test"]).collect()
            if report.status:
                print("All validations passed!")
            else:
                print(f"Failures: {report.rules}")
        
        .. versionadded:: 0.1.0
        """
        results = {
            "status": all(result.status for result in self.status.validators.values()),
            "rules": {}
        }
        for k, v in self.status.validators.items():
            results["rules"][k] = v.to_dict()
        return AisertReport(**results)
