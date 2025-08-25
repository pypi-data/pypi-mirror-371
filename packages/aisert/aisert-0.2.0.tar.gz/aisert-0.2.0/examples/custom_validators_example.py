"""
Custom Validators Example - Bring Your Own Token & Semantic Validators

Shows how to create and register custom validators for specialized use cases.
"""

import sys
import os
import threading

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aisert import Aisert, AisertConfig
from aisert.validators.token_validator.token_validator_base import TokenValidatorBase
from aisert.validators.token_validator.token_validator_factory import TokenValidatorFactory
from aisert.validators.semantic_validator.semantic_validator_base import SemanticValidatorBase
from aisert.validators.semantic_validator.semantic_validator_factory import SemanticValidatorFactory
from aisert.exception import TokenValidationError, SemanticValidationError
from aisert.models.result import Result


class WordCountTokenValidator(TokenValidatorBase):
    """Simple word-based token validator."""
    _instances = {}
    _lock = threading.RLock()

    def __init__(self, model_name: str):
        super().__init__()
        self.model_name = model_name

    @classmethod
    def get_instance(cls, token_model: str = None, **kwargs):
        with cls._lock:
            if token_model not in cls._instances:
                cls._instances[token_model] = cls(token_model)
            return cls._instances[token_model]

    def count(self, text: str) -> int:
        """Count words as tokens."""
        if not isinstance(text, str):
            text = str(text)
        return len(text.split())


class CharacterCountTokenValidator(TokenValidatorBase):
    """Character-based token validator."""
    _instances = {}
    _lock = threading.RLock()

    def __init__(self, model_name: str):
        super().__init__()
        self.model_name = model_name

    @classmethod
    def get_instance(cls, token_model: str = None, **kwargs):
        with cls._lock:
            if token_model not in cls._instances:
                cls._instances[token_model] = cls(token_model)
            return cls._instances[token_model]

    def count(self, text: str) -> int:
        """Count characters as tokens."""
        if not isinstance(text, str):
            text = str(text)
        return len(text)


class KeywordOverlapSemanticValidator(SemanticValidatorBase):
    """Keyword overlap-based semantic similarity."""
    _instances = {}
    _lock = threading.RLock()

    def __init__(self, model_name: str = None):
        super().__init__()
        self.model_name = model_name or "keyword_overlap"

    @classmethod
    def get_instance(cls, model_name: str = None, **kwargs):
        key = model_name or "default"
        with cls._lock:
            if key not in cls._instances:
                cls._instances[key] = cls(model_name)
            return cls._instances[key]

    def validate(self, text1: str, text2: str, threshold: float = 0.8) -> Result:
        """Calculate similarity based on keyword overlap."""
        if not (0 <= threshold <= 1):
            raise SemanticValidationError("Threshold must be between 0 and 1")

        # Simple keyword overlap calculation
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 and not words2:
            similarity = 1.0
        elif not words1 or not words2:
            similarity = 0.0
        else:
            intersection = len(words1 & words2)
            union = len(words1 | words2)
            similarity = intersection / union

        if similarity < threshold:
            raise SemanticValidationError(
                f"Keyword overlap similarity: {similarity:.3f} is less than threshold: {threshold}"
            )

        return Result(self.validator_name, True,
                     f"Keyword overlap similarity: {similarity:.3f}, Threshold: {threshold}")


class JaccardSemanticValidator(SemanticValidatorBase):
    """Jaccard similarity-based semantic validator."""
    _instances = {}
    _lock = threading.RLock()

    def __init__(self, model_name: str = None):
        super().__init__()
        self.model_name = model_name or "jaccard"

    @classmethod
    def get_instance(cls, model_name: str = None, **kwargs):
        key = model_name or "default"
        with cls._lock:
            if key not in cls._instances:
                cls._instances[key] = cls(model_name)
            return cls._instances[key]

    def validate(self, text1: str, text2: str, threshold: float = 0.8) -> Result:
        """Calculate Jaccard similarity."""
        if not (0 <= threshold <= 1):
            raise SemanticValidationError("Threshold must be between 0 and 1")

        # Jaccard similarity calculation
        set1 = set(text1.lower().split())
        set2 = set(text2.lower().split())
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        similarity = intersection / union if union > 0 else 0.0

        if similarity < threshold:
            raise SemanticValidationError(
                f"Jaccard similarity: {similarity:.3f} is less than threshold: {threshold}"
            )

        return Result(self.validator_name, True,
                     f"Jaccard similarity: {similarity:.3f}, Threshold: {threshold}")


def register_custom_validators():
    """Register all custom validators with their factories."""
    # Register token validators
    TokenValidatorFactory.register_token_validator("word_count", WordCountTokenValidator)
    TokenValidatorFactory.register_token_validator("char_count", CharacterCountTokenValidator)
    
    # Register semantic validators
    SemanticValidatorFactory.register_semantic_validator("keyword_overlap", KeywordOverlapSemanticValidator)
    SemanticValidatorFactory.register_semantic_validator("jaccard", JaccardSemanticValidator)
    
    print("✅ Custom validators registered successfully!")


def test_custom_token_validators():
    """Test custom token validators."""
    print("\n=== Testing Custom Token Validators ===")
    
    text = "Hello world from custom validators"
    
    # Test word count validator
    config1 = AisertConfig(token_provider="word_count")
    result1 = Aisert(text, config1).assert_tokens(max_tokens=10, strict=False).collect()
    print(f"Word count validation: {result1.status}")
    print(f"  Details: {list(result1.rules.values())[0]['reason']}")
    
    # Test character count validator
    config2 = AisertConfig(token_provider="char_count")
    result2 = Aisert(text, config2).assert_tokens(max_tokens=50, strict=False).collect()
    print(f"Character count validation: {result2.status}")
    print(f"  Details: {list(result2.rules.values())[0]['reason']}")


def test_custom_semantic_validators():
    """Test custom semantic validators."""
    print("\n=== Testing Custom Semantic Validators ===")
    
    text1 = "Machine learning and artificial intelligence"
    text2 = "AI and machine learning technologies"
    
    # Test keyword overlap validator
    config1 = AisertConfig(semantic_provider="keyword_overlap", semantic_model="simple")
    result1 = Aisert(text1, config1).assert_semantic_matches(text2, threshold=0.3, strict=False).collect()
    print(f"Keyword overlap validation: {result1.status}")
    print(f"  Details: {list(result1.rules.values())[0]['reason']}")
    
    # Test Jaccard similarity validator
    config2 = AisertConfig(semantic_provider="jaccard", semantic_model="simple")
    result2 = Aisert(text1, config2).assert_semantic_matches(text2, threshold=0.2, strict=False).collect()
    print(f"Jaccard similarity validation: {result2.status}")
    print(f"  Details: {list(result2.rules.values())[0]['reason']}")


def test_combined_custom_validation():
    """Test combining custom token and semantic validators."""
    print("\n=== Testing Combined Custom Validation ===")
    
    config = AisertConfig(
        token_provider="word_count",
        token_model="combined_test",
        semantic_provider="keyword_overlap",
        semantic_model="combined_test"
    )
    
    content = "Custom validators provide flexible validation options"
    expected = "Custom validation flexible options"
    
    result = (Aisert(content, config)
             .assert_tokens(max_tokens=20, strict=False)
             .assert_semantic_matches(expected, threshold=0.4, strict=False)
             .collect())
    
    print(f"Combined validation: {result.status}")
    for order, validation in result.rules.items():
        status_icon = "✅" if validation['status'] else "❌"
        print(f"  {status_icon} {validation['validator']}: {validation['reason']}")


def demonstrate_error_handling():
    """Demonstrate error handling with custom validators."""
    print("\n=== Testing Error Handling ===")
    
    config = AisertConfig(semantic_provider="keyword_overlap", semantic_model="error_test")
    
    # Test with threshold out of range
    try:
        result = Aisert("test", config).assert_semantic_matches("test", threshold=1.5).collect()
    except SemanticValidationError as e:
        print(f"✅ Caught expected error: {e}")
    
    # Test with failing validation
    result = (Aisert("completely different text", config)
             .assert_semantic_matches("unrelated content", threshold=0.8, strict=False)
             .collect())
    
    print(f"Failed validation handled gracefully: {not result.status}")
    if not result.status:
        print(f"  Error: {list(result.rules.values())[0]['reason']}")


if __name__ == "__main__":
    print("🔧 Custom Validators Example")
    print("=" * 50)
    
    # Register custom validators
    register_custom_validators()
    
    # Run tests
    test_custom_token_validators()
    test_custom_semantic_validators()
    test_combined_custom_validation()
    demonstrate_error_handling()
    
    print("\n✨ Custom validators example completed!")
    print("💡 You can now create your own validators for specialized use cases.")