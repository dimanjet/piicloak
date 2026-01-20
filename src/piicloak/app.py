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

import sys
from .config import HOST, PORT, DEBUG, LOG_LEVEL
from .engine import create_analyzer, create_anonymizer, load_spacy_model
from .api import create_app
from .recognizers import SUPPORTED_ENTITIES


def create_application():
    """Create the complete application with all components."""
    print("Loading spaCy model...")
    nlp = load_spacy_model()
    
    print("Initializing analyzer engine...")
    analyzer = create_analyzer(nlp)
    anonymizer = create_anonymizer()
    
    print("Creating Flask application...")
    app = create_app(analyzer, anonymizer)
    
    return app


def main():
    """Main entry point for the service."""
    print("=" * 70)
    print("PIICloak - Enterprise PII Detection & Anonymization API")
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
    print("=" * 70)
    print(f"\n🚀 Server starting on http://{HOST}:{PORT}")
    print(f"📊 Log level: {LOG_LEVEL}")
    print("\nPress CTRL+C to stop")
    print()
    
    app.run(host=HOST, port=PORT, debug=DEBUG)


if __name__ == '__main__':
    main()
