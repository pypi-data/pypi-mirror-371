"""Base class for semantic validators."""

import logging
from ...models.result import Result


class SemanticValidatorBase:
    """Abstract base class for semantic validators."""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.validator_name = "semantic"
    
    @classmethod
    def get_instance(cls, **kwargs):
        """
        Get or create an instance of the semantic validator.
        
        This method should implement the singleton pattern for performance,
        as semantic models can be expensive to load.
        
        Args:
            **kwargs: Additional arguments for validator configuration
            
        Returns:
            Instance of the semantic validator
        """
        pass
    
    def validate(self, text1: str, text2: str, threshold: float = 0.8) -> Result:
        """
        Validate semantic similarity between two texts.
        
        Args:
            text1: First text to compare
            text2: Second text to compare  
            threshold: Minimum similarity threshold (0.0 to 1.0)
            
        Returns:
            Result object with validation outcome
            
        Raises:
            SemanticValidationError: If validation fails
        """
        pass