[![Publish to PyPI](https://github.com/haipad/aisert/actions/workflows/workflow.yml/badge.svg)](https://github.com/haipad/aisert/actions/workflows/workflow.yml)
[![PyPI version](https://badge.fury.io/py/aisert.svg)](https://badge.fury.io/py/aisert)
[![Python versions](https://img.shields.io/pypi/pyversions/aisert.svg)](https://pypi.org/project/aisert/)
[![License](https://img.shields.io/pypi/l/aisert.svg)](https://github.com/haipad/aisert/blob/main/LICENSE)
[![Downloads](https://pepy.tech/badge/aisert)](https://pepy.tech/project/aisert)

# Aisert 🚀

Assert-style validation library for AI outputs - ensure your LLMs behave exactly as expected.

## Installation

```bash
# Basic installation
pip install aisert

# With semantic validation (sentence-transformers)
pip install aisert[sentence-transformers]

# With HuggingFace support
pip install aisert[huggingface]

# All optional features
pip install aisert[all]
```

## Quick Start

```python
from aisert import Aisert, AisertConfig

# Simple validation (no dependencies required)
result = (
    Aisert("Paris is the capital of France.")
    .assert_contains(["Paris", "France"])
    .assert_not_contains(["spam", "inappropriate"])
    .collect()
)

print(f"Validation passed: {result.status}")

# Advanced validation with token counting and semantic similarity
config = AisertConfig(
    token_provider="openai",
    token_model="gpt-4",
    semantic_provider="sentence_transformers",
    semantic_model="all-MiniLM-L6-v2"
)

result = (
    Aisert("AI is transforming technology.", config)
    .assert_tokens(max_tokens=50)
    .assert_semantic_matches("artificial intelligence technology", threshold=0.7)
    .collect()
)
```

## Features

- **🔗 Fluent Interface**: Chain multiple validations with readable API
- **📝 Multiple Validators**: Schema, content, token count, semantic similarity
- **⚡ Optional Dependencies**: Install only what you need
- **🎯 Flexible Modes**: Strict (exceptions) or non-strict (collect errors)
- **🌐 Multi-Provider**: OpenAI, Anthropic, HuggingFace, Google
- **🔧 Extensible**: Custom validators via base classes
- **🚀 Production Ready**: Thread-safe with model caching

## Use Cases

- **🛡️ Content Moderation**: Filter inappropriate content in real-time
- **✅ API Response Validation**: Ensure LLM outputs meet quality standards
- **🧪 Testing AI Systems**: Automated testing for AI applications
- **📊 Quality Monitoring**: Track AI model performance in production
- **🔄 CI/CD Integration**: Validate AI-generated content in pipelines
- **📈 A/B Testing**: Compare different AI model outputs

## Validation Types

```python
# Content validation (no dependencies)
Aisert(content).assert_contains(["required", "keywords"])
Aisert(content).assert_not_contains(["spam", "inappropriate"])

# Schema validation (Pydantic models)
Aisert(json_content).assert_schema(UserModel)

# Token counting (requires API keys)
Aisert(content, config).assert_tokens(max_tokens=100)

# Semantic similarity (requires sentence-transformers)
Aisert(content).assert_semantic_matches("expected meaning", threshold=0.8)
```

## Configuration

```python
# Simple configuration
config = AisertConfig(
    token_provider="openai",
    token_model="gpt-4",
    semantic_provider="sentence_transformers",
    semantic_model="all-MiniLM-L6-v2"
)

# Set API keys (for token counting)
export OPENAI_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"
```

## Error Handling

```python
# Strict mode (default) - raises exceptions
try:
    Aisert(content).assert_contains(["required"])
except AisertError as e:
    print(f"Validation failed: {e}")

# Non-strict mode - collects all errors
result = (
    Aisert(content)
    .assert_contains(["term1"], strict=False)
    .assert_tokens(100, strict=False)
    .collect()
)

if not result.status:
    print("Some validations failed:", result.rules)
```

## Documentation

- **[📚 Examples](https://aisert.readthedocs.io/examples/)** - Configuration, usage patterns, production use cases
- **[📖 API Reference](https://aisert.readthedocs.io/api/)** - Complete API documentation  
- **[🔧 Custom Validators](https://aisert.readthedocs.io/examples/#custom-validators)** - Extend with your own validators

## Requirements

- **Python**: >= 3.9
- **Dependencies**: Optional based on features used
- **API Keys**: Only for token counting (OpenAI, Anthropic, etc.)
- **Memory**: 100-500MB for semantic models (optional)

## License

MIT License

## Links

- **[GitHub](https://github.com/haipad/aisert)** - Source code and issues
- **[Documentation](https://aisert.readthedocs.io/)** - Complete documentation
- **[PyPI](https://pypi.org/project/aisert/)** - Package repository