# Changelog

All notable changes to the langchain-g4f project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.2] - 2025-01-23

### Added
- **Tool Calling Support**: Complete OpenAI-compatible tool calling functionality
  - `bind_tools()` method with support for function schemas, Pydantic models, and callable tools
  - Tool choice options: "auto", "none", "required", "any", specific tool names
  - Strict schema adherence option
- **Structured Output Support**: Generate structured responses
  - `with_structured_output()` method supporting Pydantic models and TypedDict schemas
  - Two methods: "function_calling" and "json_mode"
  - Include raw response option with automatic parsing and validation
- **Enhanced Parameters**: Support for all modern LangChain parameters
  - `top_p`: Total probability mass of tokens to consider
  - `frequency_penalty`: Penalize tokens based on frequency
  - `presence_penalty`: Penalize tokens based on presence
  - `reasoning_effort`: For reasoning models (o1 models)
  - `n`: Number of completions to generate
  - `stop`: Stop sequences
  - `timeout`: Request timeout
  - `max_retries`: Maximum number of retries
- **Version Management**: Added version.py with proper version tracking
- **Setup Configuration**: Added setup.py for proper package installation
- **Comprehensive Testing**: Added test suites for functionality and compatibility verification

### Changed
- **Updated Dependencies**: 
  - `langchain-core` from `>=0.1.0` to `>=0.3.74`
  - `g4f` from `==0.5.7.6` to `>=0.5.7.6` (more flexible versioning)
  - `typing-extensions` to `>=4.0.0`
- **Enhanced Type Annotations**: Updated all method signatures with proper type hints
- **Improved Error Handling**: Better exception handling with descriptive error messages
- **Parameter Validation**: Enhanced validation in `validate_environment()` method
- **Method Signatures**: Updated core methods to match latest LangChain patterns

### Fixed
- **Parameter Synchronization**: Fixed sync between `stream` and `streaming` parameters
- **Temperature Handling**: Proper temperature normalization (0 becomes 1e-8)
- **Provider Validation**: Better provider validation with warnings for invalid providers
- **Generation Info**: Added generation info to response objects

### Compatibility
- **LangChain OpenAI**: Full compatibility with `langchain-openai` 0.3.31
- **LangChain Groq**: Full compatibility with `langchain-groq` 0.3.7
- **LangChain Core**: Compatible with `langchain-core` 0.3.74+
- **Backward Compatibility**: All existing code continues to work without changes

### Documentation
- **Upgrade Summary**: Added comprehensive upgrade documentation
- **Usage Examples**: Updated examples with new features
- **API Reference**: Enhanced documentation for all new methods
- **Testing Guide**: Added testing and validation documentation

## [0.0.1] - 2024-XX-XX

### Added
- Initial release with basic ChatG4F functionality
- Core chat model integration with G4F
- Basic provider management
- Image generation capabilities
- Simple LangChain integration

### Features
- Basic chat completion
- Provider selection
- Model configuration
- Streaming support
- Async operations

---

## Migration Guide

### From 0.0.1 to 0.0.2

#### No Breaking Changes
All existing code continues to work without modifications. The update is fully backward compatible.

#### New Features Available
```python
# Tool calling (new in 0.0.2)
from pydantic import BaseModel, Field

class GetWeather(BaseModel):
    location: str = Field(description="City and state")

llm_with_tools = llm.bind_tools([GetWeather])
result = llm_with_tools.invoke("What's the weather in NYC?")

# Structured output (new in 0.0.2)
structured_llm = llm.with_structured_output(GetWeather)
weather_data = structured_llm.invoke("Get weather for San Francisco")

# Advanced parameters (new in 0.0.2)
llm = ChatG4F(
    model="gpt-4o",
    temperature=0.5,
    top_p=0.9,
    frequency_penalty=0.1,
    reasoning_effort="medium",
    max_retries=3
)
```

#### Updated Dependencies
Update your requirements.txt or install command:
```bash
pip install langchain-core>=0.3.74
```

#### Verification
Run the verification script to ensure everything works:
```bash
python verify_installation.py
```

---

## Support

For issues, questions, or contributions:
- GitHub Issues: [https://github.com/xtekky/gpt4free/issues](https://github.com/xtekky/gpt4free/issues)
- Documentation: [README.md](README.md)
- Upgrade Guide: [UPGRADE_SUMMARY.md](UPGRADE_SUMMARY.md)
