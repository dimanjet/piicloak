"""Pytest configuration and fixtures."""

import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture(scope="session")
def nlp():
    """Load spaCy model once for all tests."""
    import spacy
    return spacy.load("en_core_web_lg")


@pytest.fixture(scope="session")
def analyzer(nlp):
    """Create analyzer engine once for all tests."""
    from piicloak.engine import create_analyzer
    return create_analyzer(nlp)


@pytest.fixture(scope="session")
def anonymizer():
    """Create anonymizer engine once for all tests."""
    from piicloak.engine import create_anonymizer
    return create_anonymizer()


@pytest.fixture(scope="session")
def app(analyzer, anonymizer):
    """Create Flask app for testing."""
    from piicloak.api import create_app
    app = create_app(analyzer, anonymizer)
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()
