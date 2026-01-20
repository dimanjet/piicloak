# Contributing to PII Anonymizer

Thank you for your interest in contributing to PII Anonymizer! This document provides guidelines and instructions for contributing.

## Code of Conduct

Please be respectful and constructive in all interactions. We welcome contributors of all backgrounds and experience levels.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/dimanjet/piicloak/issues)
2. If not, create a new issue with:
   - Clear, descriptive title
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (Python version, OS, etc.)

### Suggesting Features

1. Check existing issues for similar suggestions
2. Create a new issue with:
   - Clear description of the feature
   - Use case / motivation
   - Proposed implementation (if any)

### Pull Requests

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass: `pytest`
6. Format code: `black src/ tests/`
7. Lint code: `flake8 src/ tests/`
8. Commit with clear messages
9. Push and create a Pull Request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/pii-anonymizer.git
cd pii-anonymizer

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install in development mode
pip install -e ".[dev]"

# Download spaCy model
python -m spacy download en_core_web_lg

# Run tests
pytest
```

## Code Style

- Follow PEP 8 guidelines
- Use [Black](https://github.com/psf/black) for formatting
- Use type hints where appropriate
- Write docstrings for public functions/classes
- Keep functions focused and small

## Adding New Recognizers

To add a new PII recognizer:

1. Add pattern(s) to `src/pii_anonymizer/recognizers.py`
2. Create a factory function: `create_your_recognizer()`
3. Add to `get_all_pattern_recognizers()` list
4. Add entity type to `SUPPORTED_ENTITIES`
5. Write tests in `tests/test_recognizers.py`
6. Update README.md with the new entity type

Example:

```python
def create_license_plate_recognizer() -> PatternRecognizer:
    """Create license plate recognizer."""
    patterns = [
        Pattern("US_PLATE", r"\b[A-Z]{2,3}[-\s]?\d{3,4}[-\s]?[A-Z]{0,3}\b", 0.7),
    ]
    return PatternRecognizer(
        supported_entity="LICENSE_PLATE",
        patterns=patterns,
        context=["plate", "vehicle", "car", "license"]
    )
```

## Testing

- Write tests for all new functionality
- Maintain test coverage above 80%
- Use descriptive test names
- Group related tests in classes

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=pii_anonymizer --cov-report=html

# Run specific test file
pytest tests/test_recognizers.py

# Run specific test
pytest tests/test_api.py::TestAnonymizeEndpoint::test_anonymize_email
```

## Documentation

- Update README.md for user-facing changes
- Add docstrings for new functions/classes
- Update API examples if endpoints change

## Questions?

Feel free to open an issue for any questions about contributing.

Thank you for helping improve PII Anonymizer!
