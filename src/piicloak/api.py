"""
Flask API routes for PIICloak service.
"""

import io
from flask import Flask, request, jsonify, Response
from presidio_anonymizer.entities import OperatorConfig

from .config import DEFAULT_SCORE_THRESHOLD, DEFAULT_MODE, ANONYMIZATION_MODES, ENABLE_METRICS
from .recognizers import SUPPORTED_ENTITIES
from .middleware import setup_middleware
from .metrics import setup_metrics, metrics, track_entities


def create_app(analyzer, anonymizer) -> Flask:
    """
    Create and configure the Flask application.
    
    Args:
        analyzer: Presidio AnalyzerEngine instance
        anonymizer: Presidio AnonymizerEngine instance
        
    Returns:
        Configured Flask application
    """
    app = Flask(__name__)
    app.config['JSON_SORT_KEYS'] = False
    
    # Setup middleware and metrics
    setup_middleware(app)
    if ENABLE_METRICS:
        setup_metrics(app)
    
    def get_operators(mode: str) -> dict:
        """Get anonymization operators based on mode."""
        if mode == 'redact':
            return {"DEFAULT": OperatorConfig("redact")}
        elif mode == 'hash':
            return {"DEFAULT": OperatorConfig("hash", {"hash_type": "sha256"})}
        elif mode == 'mask':
            return {"DEFAULT": OperatorConfig("mask", {
                "chars_to_mask": 100, 
                "masking_char": "*", 
                "from_end": False
            })}
        else:  # default: replace
            return {"DEFAULT": OperatorConfig("replace")}

    @app.route('/health', methods=['GET'])
    def health():
        """Health check endpoint with detailed status."""
        return jsonify({
            "status": "ok", 
            "service": "piicloak",
            "version": "1.0.0",
            "endpoints": {
                "anonymize": "/anonymize",
                "analyze": "/analyze",
                "entities": "/entities",
                "metrics": "/metrics",
                "health": "/health"
            }
        })
    
    @app.route('/metrics', methods=['GET'])
    def metrics_endpoint():
        """Prometheus metrics endpoint."""
        if not ENABLE_METRICS:
            return jsonify({"error": "Metrics disabled"}), 404
        
        return Response(metrics.get_metrics(), mimetype='text/plain')

    @app.route('/anonymize', methods=['POST'])
    def anonymize_text():
        """
        Anonymize PII in text.
        
        Request JSON:
            {
                "text": "John works at Acme Corp",
                "entities": ["PERSON", "ORGANIZATION"],  # optional
                "mode": "replace",  # replace, redact, hash, mask
                "language": "en",
                "score_threshold": 0.4
            }
            
        Response JSON:
            {
                "original": "John works at Acme Corp",
                "anonymized": "<PERSON> works at <ORGANIZATION>",
                "entities_found": [...]
            }
        """
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({"error": "Missing 'text' field"}), 400
        
        text = data['text']
        language = data.get('language', 'en')
        entities = data.get('entities', SUPPORTED_ENTITIES)
        mode = data.get('mode', DEFAULT_MODE)
        score_threshold = data.get('score_threshold', DEFAULT_SCORE_THRESHOLD)
        
        if mode not in ANONYMIZATION_MODES:
            return jsonify({
                "error": f"Invalid mode. Must be one of: {ANONYMIZATION_MODES}"
            }), 400
        
        # Analyze
        results = analyzer.analyze(
            text=text,
            entities=entities,
            language=language,
            score_threshold=score_threshold
        )
        
        # Anonymize
        anonymized_result = anonymizer.anonymize(
            text=text,
            analyzer_results=results,
            operators=get_operators(mode)
        )
        
        entities_found = [
            {
                "type": r.entity_type,
                "text": text[r.start:r.end],
                "start": r.start,
                "end": r.end,
                "score": round(r.score, 3)
            }
            for r in results
        ]
        
        # Track metrics
        if ENABLE_METRICS:
            track_entities(len(results))
        
        return jsonify({
            "original": text,
            "anonymized": anonymized_result.text,
            "entities_found": entities_found
        })

    @app.route('/anonymize/docx', methods=['POST'])
    def anonymize_docx():
        """
        Anonymize PII in a .docx file.
        
        Request: multipart/form-data with 'document' file field
        Optional form fields: entities, mode, language, score_threshold
        """
        if 'document' not in request.files:
            return jsonify({"error": "No document file provided"}), 400
        
        file = request.files['document']
        
        if not file.filename.endswith('.docx'):
            return jsonify({"error": "Only .docx files are supported"}), 400
        
        try:
            from docx import Document
            doc = Document(io.BytesIO(file.read()))
            text = '\n'.join([para.text for para in doc.paragraphs])
        except ImportError:
            return jsonify({
                "error": "python-docx not installed. Run: pip install python-docx"
            }), 500
        except Exception as e:
            return jsonify({"error": f"Failed to read document: {str(e)}"}), 400
        
        language = request.form.get('language', 'en')
        entities_param = request.form.get('entities', '')
        entities = entities_param.split(',') if entities_param else SUPPORTED_ENTITIES
        mode = request.form.get('mode', DEFAULT_MODE)
        score_threshold = float(request.form.get('score_threshold', DEFAULT_SCORE_THRESHOLD))
        
        results = analyzer.analyze(
            text=text,
            entities=entities,
            language=language,
            score_threshold=score_threshold
        )
        
        anonymized_result = anonymizer.anonymize(
            text=text,
            analyzer_results=results,
            operators=get_operators(mode)
        )
        
        entities_found = [
            {
                "type": r.entity_type,
                "text": text[r.start:r.end],
                "start": r.start,
                "end": r.end,
                "score": round(r.score, 3)
            }
            for r in results
        ]
        
        return jsonify({
            "anonymized_text": anonymized_result.text,
            "entities_found": entities_found
        })

    @app.route('/analyze', methods=['POST'])
    def analyze_only():
        """
        Analyze text for PII without anonymizing.
        
        Request JSON:
            {
                "text": "Contact john@example.com",
                "entities": ["EMAIL_ADDRESS"],  # optional
                "language": "en",
                "score_threshold": 0.4
            }
        """
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({"error": "Missing 'text' field"}), 400
        
        text = data['text']
        language = data.get('language', 'en')
        entities = data.get('entities', SUPPORTED_ENTITIES)
        score_threshold = data.get('score_threshold', DEFAULT_SCORE_THRESHOLD)
        
        results = analyzer.analyze(
            text=text,
            entities=entities,
            language=language,
            score_threshold=score_threshold
        )
        
        return jsonify({
            "text": text,
            "contains_pii": len(results) > 0,
            "entities_found": [
                {
                    "type": r.entity_type,
                    "text": text[r.start:r.end],
                    "start": r.start,
                    "end": r.end,
                    "score": round(r.score, 3)
                }
                for r in results
            ]
        })

    @app.route('/entities', methods=['GET'])
    def list_entities():
        """List all supported PII entity types."""
        return jsonify({
            "supported_entities": SUPPORTED_ENTITIES,
            "modes": ANONYMIZATION_MODES,
            "categories": {
                "personal": [
                    "PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER", 
                    "US_SSN", "US_PASSPORT", "US_DRIVER_LICENSE", "ADDRESS"
                ],
                "financial": [
                    "CREDIT_CARD", "IBAN_CODE", "BANK_ACCOUNT", 
                    "TAX_ID", "CRYPTO", "US_BANK_NUMBER"
                ],
                "organizational": [
                    "ORGANIZATION", "DOMAIN", "ACCOUNT_ID", "SALESFORCE_ID"
                ],
                "legal": ["CASE_NUMBER", "CONTRACT_NUMBER"],
                "technical": ["IP_ADDRESS", "URL", "API_KEY"],
                "other": ["DATE_TIME", "LOCATION", "NRP", "MEDICAL_LICENSE"]
            }
        })
    
    return app
