"""
Production Use Cases - Real-world scenarios and pipeline integration

Shows practical applications in production environments.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aisert import Aisert, AisertConfig
from typing import List, Dict, Any


def content_moderation_pipeline():
    """Content moderation for user-generated content."""
    print("=== Content Moderation Pipeline ===")
    
    user_comments = [
        "Great product, really helpful!",
        "This spam content contains inappropriate language",
        "Excellent customer service, highly recommend!"
    ]
    
    flagged_terms = ["spam", "inappropriate", "offensive", "scam"]
    approved_count = 0
    
    for i, comment in enumerate(user_comments, 1):
        result = (Aisert(comment)
                 .assert_not_contains(flagged_terms, strict=False)
                 .collect())
        
        if result.status:
            print(f"Comment {i}: ✅ APPROVED")
            approved_count += 1
        else:
            print(f"Comment {i}: ❌ FLAGGED - {result.rules[1]['reason']}")
    
    print(f"Approval rate: {approved_count}/{len(user_comments)} ({approved_count/len(user_comments)*100:.1f}%)")
    # Expected: 2/3 approved (66.7%)


def api_response_validation():
    """Validate LLM API responses in production."""
    print("\n=== API Response Validation ===")
    
    config = AisertConfig(
        token_provider="openai",
        token_model="gpt-4",
        semantic_provider="openai",
        semantic_model="text-embedding-3-small"
    )
    
    # Simulate LLM responses
    responses = [
        "Thank you for your inquiry. I can help you with account setup.",
        "I cannot process this request due to insufficient information.",
        "Here's a comprehensive guide to getting started with our platform."
    ]
    
    valid_responses = 0
    for i, response in enumerate(responses, 1):
        result = (Aisert(response, config)
                 .assert_contains(["help", "information", "guide"], strict=False)  # Helpful content
                 .assert_not_contains(["error", "failed", "unavailable"], strict=False)  # No errors
                 .assert_tokens(max_tokens=100, strict=False)  # Reasonable length
                 .assert_semantic_matches("helpful customer service", threshold=0.6, strict=False)
                 .collect())
        
        if result.status:
            print(f"Response {i}: ✅ VALID")
            valid_responses += 1
        else:
            failed_checks = sum(1 for v in result.rules.values() if not v['status'])
            print(f"Response {i}: ❌ INVALID ({failed_checks} failed checks)")
    
    print(f"Valid responses: {valid_responses}/{len(responses)}")
    # Expected: Varies based on semantic similarity


def ci_cd_integration():
    """Integration with CI/CD pipelines for automated testing."""
    print("\n=== CI/CD Integration ===")
    
    def validate_generated_docs(content: str) -> bool:
        """Validate auto-generated documentation."""
        result = (Aisert(content)
                 .assert_contains(["API", "endpoint", "parameter"], strict=False)
                 .assert_not_contains(["TODO", "FIXME", "placeholder"], strict=False)
                 .assert_tokens(max_tokens=500, strict=False)
                 .collect())
        return result.status
    
    # Test documentation samples
    docs = [
        "API endpoint /users accepts GET requests with optional id parameter",
        "TODO: Add documentation for this endpoint",
        "This endpoint returns user data in JSON format with id, name, and email fields"
    ]
    
    passed_tests = 0
    for i, doc in enumerate(docs, 1):
        if validate_generated_docs(doc):
            print(f"Doc {i}: ✅ PASS")
            passed_tests += 1
        else:
            print(f"Doc {i}: ❌ FAIL")
    
    print(f"CI/CD Result: {passed_tests}/{len(docs)} tests passed")
    # Expected: 2/3 tests pass (doc with TODO fails)
    
    # Simulate CI/CD exit code
    exit_code = 0 if passed_tests == len(docs) else 1
    print(f"Exit code: {exit_code}")


def batch_processing():
    """High-volume batch processing with performance optimization."""
    print("\n=== Batch Processing ===")
    
    # Lightweight config for high-volume processing
    config = AisertConfig(semantic_provider="tfidf")  # Fast, no model loading
    
    # Simulate large batch of content
    batch_size = 100
    content_batch = [f"User message {i} with some content to validate" for i in range(batch_size)]
    
    import time
    start_time = time.time()
    
    processed = 0
    valid_count = 0
    
    for content in content_batch:
        result = (Aisert(content, config)
                 .assert_not_contains(["spam", "inappropriate"], strict=False)
                 .assert_semantic_matches("user message", threshold=0.3, strict=False)
                 .collect())
        
        processed += 1
        if result.status:
            valid_count += 1
    
    processing_time = time.time() - start_time
    
    print(f"Processed: {processed} items")
    print(f"Valid: {valid_count} ({valid_count/processed*100:.1f}%)")
    print(f"Time: {processing_time:.2f}s ({processing_time/processed*1000:.1f}ms per item)")
    print(f"Throughput: {processed/processing_time:.1f} items/second")
    # Expected: High throughput with TFIDF (no model loading)


def quality_monitoring():
    """Monitor content quality in production with metrics."""
    print("\n=== Quality Monitoring ===")
    
    class QualityMonitor:
        def __init__(self):
            self.metrics = {"total": 0, "passed": 0, "failed": 0}
            self.config = AisertConfig(
                token_provider="openai",
                token_model="gpt-3.5-turbo"
            )
        
        def validate_content(self, content: str, requirements: Dict[str, Any]) -> bool:
            self.metrics["total"] += 1
            
            aisert = Aisert(content, self.config)
            
            if "required_terms" in requirements:
                aisert.assert_contains(requirements["required_terms"], strict=False)
            
            if "forbidden_terms" in requirements:
                aisert.assert_not_contains(requirements["forbidden_terms"], strict=False)
            
            if "max_tokens" in requirements:
                aisert.assert_tokens(requirements["max_tokens"], strict=False)
            
            result = aisert.collect()
            
            if result.status:
                self.metrics["passed"] += 1
                return True
            else:
                self.metrics["failed"] += 1
                return False
        
        def get_quality_score(self) -> float:
            if self.metrics["total"] == 0:
                return 0.0
            return self.metrics["passed"] / self.metrics["total"]
    
    # Usage example
    monitor = QualityMonitor()
    
    # Validate different content types
    test_cases = [
        ("Customer service response with helpful information", {"required_terms": ["helpful"], "max_tokens": 50}),
        ("Product description with spam content", {"forbidden_terms": ["spam"], "max_tokens": 100}),
        ("Technical documentation explaining the API", {"required_terms": ["API"], "max_tokens": 200})
    ]
    
    for content, requirements in test_cases:
        is_valid = monitor.validate_content(content, requirements)
        print(f"Content valid: {is_valid}")
    
    quality_score = monitor.get_quality_score()
    print(f"Overall quality score: {quality_score:.2f} ({quality_score*100:.1f}%)")
    print(f"Metrics: {monitor.metrics}")
    # Expected: Quality score based on validation results


if __name__ == "__main__":
    print("🏭 Aisert Production Use Cases")
    print("=" * 50)
    
    content_moderation_pipeline()
    api_response_validation()
    ci_cd_integration()
    batch_processing()
    quality_monitoring()
    
    print("\n✨ Production use cases completed!")
    print("💡 These patterns can be adapted for your specific production needs.")