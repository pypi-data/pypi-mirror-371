"""
Usage Patterns - Direct validation and fluent interface examples

Shows different ways to use Aisert for validation.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aisert import Aisert, AisertConfig
from pydantic import BaseModel


class UserModel(BaseModel):
    name: str
    age: int


def direct_validation():
    """Direct validation - single validator per call."""
    print("=== Direct Validation ===")
    
    content = "Hello world, this is a test message."
    
    # Content validation
    result1 = Aisert(content).assert_contains(["Hello", "test"]).collect()
    print(f"Contains validation: {result1.status}")
    # Expected: True
    
    # Schema validation
    json_content = '{"name": "John", "age": 30}'
    result2 = Aisert(json_content).assert_schema(UserModel).collect()
    print(f"Schema validation: {result2.status}")
    # Expected: True
    
    # Token validation (requires config)
    config = AisertConfig(token_provider="openai", token_model="gpt-3.5-turbo")
    result3 = Aisert(content, config).assert_tokens(max_tokens=20).collect()
    print(f"Token validation: {result3.status}")
    # Expected: True (content is under 20 tokens)


def fluent_interface():
    """Fluent interface - chain multiple validations."""
    print("\n=== Fluent Interface ===")
    
    content = "AI and machine learning are transforming technology."
    config = AisertConfig(
        token_provider="openai",
        token_model="gpt-3.5-turbo",
        semantic_provider="openai",
        semantic_model="text-embedding-3-small"
    )
    
    # Chain multiple validations
    result = (Aisert(content, config)
             .assert_contains(["AI", "technology"])
             .assert_not_contains(["spam", "inappropriate"])
             .assert_tokens(max_tokens=50)
             .assert_semantic_matches("artificial intelligence technology", threshold=0.6)
             .collect())
    
    print(f"Chained validation: {result.status}")
    print(f"Validation count: {len(result.rules)}")
    # Expected: True, 4 validations


def strict_vs_non_strict():
    """Strict mode vs non-strict mode behavior."""
    print("\n=== Strict vs Non-Strict Modes ===")
    
    content = "Hello world"
    
    # Non-strict mode - collects all errors
    result = (Aisert(content)
             .assert_contains(["Hello"], strict=False)  # Pass
             .assert_contains(["missing"], strict=False)  # Fail but continue
             .assert_not_contains(["world"], strict=False)  # Fail but continue
             .collect())
    
    print(f"Non-strict mode - Overall: {result.status}")
    print(f"Individual results: {[v['status'] for v in result.rules.values()]}")
    # Expected: False, [True, False, False]
    
    # Strict mode - stops at first error
    try:
        result = (Aisert(content)
                 .assert_contains(["Hello"])  # Pass
                 .assert_contains(["missing"])  # Fail and raise exception
                 .collect())
        print("Strict mode completed")
    except Exception as e:
        print(f"Strict mode exception: {type(e).__name__}")
        # Expected: ContainsValidationError


def error_handling():
    """Proper error handling patterns."""
    print("\n=== Error Handling ===")
    
    from aisert.exception import AisertError, ContainsValidationError
    
    content = "Test content"
    
    # Specific exception handling
    try:
        Aisert(content).assert_contains(["missing"]).collect()
    except ContainsValidationError as e:
        print(f"Caught specific error: {type(e).__name__}")
        # Expected: ContainsValidationError
    
    # General exception handling
    try:
        Aisert("invalid json").assert_schema(UserModel).collect()
    except AisertError as e:
        print(f"Caught general error: {type(e).__name__}")
        # Expected: SchemaValidationError
    
    # Graceful handling with non-strict mode
    result = (Aisert(content)
             .assert_contains(["Test"], strict=False)
             .assert_contains(["missing"], strict=False)
             .collect())
    
    if result.status:
        print("All validations passed")
    else:
        failed = [v for v in result.rules.values() if not v['status']]
        print(f"Failed validations: {len(failed)}")
        # Expected: 1 failed validation


if __name__ == "__main__":
    print("🚀 Aisert Usage Patterns")
    print("=" * 50)
    
    direct_validation()
    fluent_interface()
    strict_vs_non_strict()
    error_handling()
    
    print("\n✨ Usage patterns completed!")