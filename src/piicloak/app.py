#!/usr/bin/env python3
"""
PIICloak - Main application entry point.

Enterprise-grade PII detection and anonymization API.
Optimized for Salesforce data and legal documents.

Usage:
    python -m piicloak

Or:
    from piicloak.app import create_application
    app = create_application()
    app.run()
"""

from . import __version__
from .config import DETECTOR_BACKEND, HOST, PORT, DEBUG, LOG_LEVEL
from .engine import create_anonymizer, create_detector_backend, load_spacy_model
from .api import create_app
from .recognizers import SUPPORTED_ENTITIES


def create_application():
    """Create the complete application with all components."""
    nlp = None
    if DETECTOR_BACKEND.strip().lower().replace("_", "-") == "presidio":
        print("Loading spaCy model...")
        nlp = load_spacy_model()

    print(f"Initializing {DETECTOR_BACKEND} detector backend...")
    analyzer = create_detector_backend(DETECTOR_BACKEND, nlp)
    anonymizer = create_anonymizer()

    print("Creating Flask application...")
    app = create_app(analyzer, anonymizer)

    return app


def main():
    """Main entry point for the service."""
    print("=" * 70)
    print(f"PIICloak v{__version__} - Enterprise PII Detection & Anonymization API")
    print("=" * 70)

    app = create_application()

    print("\nEndpoints:")
    print("  POST /anonymize      - Anonymize text")
    print("  POST /anonymize/docx - Anonymize .docx file")
    print("  POST /analyze        - Detect PII only")
    print("  GET  /entities       - List supported entities")
    print("  GET  /metrics        - Prometheus metrics")
    print("  GET  /health         - Health check")
    print(f"\nSupported entities: {len(SUPPORTED_ENTITIES)}")
    print(f"Version: {__version__}")
    print("=" * 70)
    print(f"\n🚀 Server starting on http://{HOST}:{PORT}")
    print(f"📊 Log level: {LOG_LEVEL}")
    print("\nPress CTRL+C to stop")
    print()

    app.run(host=HOST, port=PORT, debug=DEBUG)


if __name__ == "__main__":
    main()
