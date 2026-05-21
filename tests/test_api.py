"""Tests for the REST API endpoints."""

import json
from types import SimpleNamespace

from piicloak.api import format_entities_found, parse_bool
from piicloak.api import create_app


class FakeAnalyzer:
    """Minimal analyzer stub for endpoint tests."""

    def analyze(self, text, entities, language, score_threshold):
        return [SimpleNamespace(entity_type="API_KEY", start=15, end=len(text), score=0.95)]


class FakeAnonymizer:
    """Minimal anonymizer stub for endpoint tests."""

    def __init__(self, text):
        self.text = text

    def anonymize(self, text, analyzer_results, operators):
        return SimpleNamespace(text=self.text)


class TestHealthEndpoint:
    """Test /health endpoint."""

    def test_health_check(self, client):
        """Test health check returns OK."""
        response = client.get("/health")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "ok"
        assert data["service"] == "piicloak"


class TestEntitiesEndpoint:
    """Test /entities endpoint."""

    def test_list_entities(self, client):
        """Test listing supported entities."""
        response = client.get("/entities")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "supported_entities" in data
        assert "modes" in data
        assert "categories" in data

    def test_entities_contains_custom(self, client):
        """Test that custom entities are listed."""
        response = client.get("/entities")
        data = json.loads(response.data)
        entities = data["supported_entities"]

        custom_entities = [
            "ORGANIZATION",
            "SALESFORCE_ID",
            "CASE_NUMBER",
            "TAX_ID",
            "BANK_ACCOUNT",
            "CONTRACT_NUMBER",
        ]
        for entity in custom_entities:
            assert entity in entities


class TestAnonymizeEndpoint:
    """Test /anonymize endpoint."""

    def test_anonymize_person(self, client):
        """Test anonymizing person name."""
        response = client.post(
            "/anonymize",
            json={"text": "Contact John Smith for details"},
            content_type="application/json",
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "<PERSON>" in data["anonymized"]

    def test_anonymize_email(self, client):
        """Test anonymizing email address."""
        response = client.post(
            "/anonymize", json={"text": "Email: john@example.com"}, content_type="application/json"
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "<EMAIL_ADDRESS>" in data["anonymized"]

    def test_anonymize_organization(self, client):
        """Test anonymizing organization name."""
        response = client.post(
            "/anonymize",
            json={"text": "He works at Acme Corporation"},
            content_type="application/json",
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "<ORGANIZATION>" in data["anonymized"]

    def test_anonymize_ssn(self, client):
        """Test anonymizing SSN."""
        response = client.post(
            "/anonymize", json={"text": "SSN: 123-45-6789"}, content_type="application/json"
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "<US_SSN>" in data["anonymized"]

    def test_anonymize_salesforce_id(self, client):
        """Test anonymizing Salesforce ID."""
        response = client.post(
            "/anonymize",
            json={"text": "Salesforce Account: 0015000000AbcDEFG"},
            content_type="application/json",
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "<SALESFORCE_ID>" in data["anonymized"]

    def test_anonymize_case_number(self, client):
        """Test anonymizing legal case number."""
        response = client.post(
            "/anonymize", json={"text": "Case No. 1:24-cv-12345"}, content_type="application/json"
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "<CASE_NUMBER>" in data["anonymized"]

    def test_mask_mode(self, client):
        """Test mask anonymization mode."""
        response = client.post(
            "/anonymize",
            json={"text": "Email: john@example.com", "mode": "mask"},
            content_type="application/json",
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "****" in data["anonymized"]

    def test_redact_mode(self, client):
        """Test redact anonymization mode."""
        response = client.post(
            "/anonymize",
            json={"text": "Contact John Smith", "mode": "redact", "entities": ["PERSON"]},
            content_type="application/json",
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "John Smith" not in data["anonymized"]

    def test_missing_text_field(self, client):
        """Test error when text field is missing."""
        response = client.post("/anonymize", json={}, content_type="application/json")
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data

    def test_invalid_mode(self, client):
        """Test error for invalid anonymization mode."""
        response = client.post(
            "/anonymize",
            json={"text": "Test", "mode": "invalid_mode"},
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_score_threshold(self, client):
        """Test score threshold filtering."""
        response = client.post(
            "/anonymize",
            json={"text": "Contact John Smith at john@example.com", "score_threshold": 0.9},
            content_type="application/json",
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        # High threshold should still catch high-confidence matches
        assert "<EMAIL_ADDRESS>" in data["anonymized"]


class TestSafeResponseHelpers:
    """Test response helpers for raw-text suppression."""

    def test_parse_bool(self):
        """Test common boolean inputs."""
        assert parse_bool(True) is True
        assert parse_bool("true") is True
        assert parse_bool("  true\n") is True
        assert parse_bool("1") is True
        assert parse_bool(1) is True
        assert parse_bool(False) is False
        assert parse_bool("false") is False
        assert parse_bool(0) is False

    def test_format_entities_found_omits_text_when_safe(self):
        """Test safe responses omit raw matched entity text."""
        text = "OpenAI key: sk-1234567890abcdefghijklmnopqrstuv"
        result = SimpleNamespace(entity_type="API_KEY", start=12, end=len(text), score=0.95)

        entities = format_entities_found(text, [result], include_text=False)

        assert entities == [
            {
                "type": "API_KEY",
                "start": 12,
                "end": len(text),
                "score": 0.95,
            }
        ]

    def test_format_entities_found_includes_text_by_default(self):
        """Test normal responses preserve existing raw match behavior."""
        text = "Email john@example.com"
        result = SimpleNamespace(entity_type="EMAIL_ADDRESS", start=6, end=len(text), score=1.0)

        entities = format_entities_found(text, [result])

        assert entities[0]["text"] == "john@example.com"


class TestSafeResponseEndpoints:
    """Test safe-response behavior at the endpoint boundary."""

    def test_anonymize_safe_response_omits_raw_input_and_matches(self):
        """Test /anonymize safe_response does not echo raw secret material."""
        app = create_app(FakeAnalyzer(), FakeAnonymizer("<API_KEY>"))
        app.config["TESTING"] = True

        response = app.test_client().post(
            "/anonymize",
            json={
                "text": "OpenRouter key sk-or-v1-abcdefghijklmnopqrstuvwxyz123456",
                "entities": ["API_KEY"],
                "safe_response": True,
            },
        )

        data = json.loads(response.data)
        assert response.status_code == 200
        assert data["anonymized"] == "<API_KEY>"
        assert data["safe_response"] is True
        assert "original" not in data
        assert "text" not in data["entities_found"][0]

    def test_analyze_safe_response_omits_raw_input_and_matches(self):
        """Test /analyze safe_response does not echo raw secret material."""
        app = create_app(FakeAnalyzer(), FakeAnonymizer("<API_KEY>"))
        app.config["TESTING"] = True

        response = app.test_client().post(
            "/analyze",
            json={
                "text": "OpenRouter key sk-or-v1-abcdefghijklmnopqrstuvwxyz123456",
                "entities": ["API_KEY"],
                "safe_response": True,
            },
        )

        data = json.loads(response.data)
        assert response.status_code == 200
        assert data["contains_pii"] is True
        assert data["safe_response"] is True
        assert "text" not in data
        assert "text" not in data["entities_found"][0]


class TestAnalyzeEndpoint:
    """Test /analyze endpoint."""

    def test_analyze_detects_pii(self, client):
        """Test analyze endpoint detects PII."""
        response = client.post(
            "/analyze", json={"text": "Contact john@example.com"}, content_type="application/json"
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["contains_pii"] is True
        assert len(data["entities_found"]) > 0

    def test_analyze_no_pii(self, client):
        """Test analyze endpoint with no PII."""
        response = client.post(
            "/analyze", json={"text": "Hello world"}, content_type="application/json"
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        # May or may not detect PII depending on NER
        assert "contains_pii" in data

    def test_analyze_specific_entities(self, client):
        """Test analyze with specific entity filter."""
        response = client.post(
            "/analyze",
            json={"text": "John Smith, john@example.com", "entities": ["EMAIL_ADDRESS"]},
            content_type="application/json",
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        # Should only find EMAIL, not PERSON
        entity_types = [e["type"] for e in data["entities_found"]]
        assert "EMAIL_ADDRESS" in entity_types


class TestComplexDocuments:
    """Test with complex document scenarios."""

    def test_legal_document(self, client):
        """Test anonymizing a legal document."""
        text = """
        LEGAL DOCUMENT - Case No. 1:24-cv-12345

        Parties:
        - John Smith (SSN: 123-45-6789)
        - Acme Corporation (EIN: 12-3456789)

        Contact: john.smith@acme.com, (555) 123-4567
        Address: 123 Main Street, New York, NY 10001
        """

        response = client.post("/anonymize", json={"text": text}, content_type="application/json")
        assert response.status_code == 200
        data = json.loads(response.data)

        # Check multiple entity types were detected
        entity_types = set(e["type"] for e in data["entities_found"])
        assert "CASE_NUMBER" in entity_types
        assert "PERSON" in entity_types
        assert "US_SSN" in entity_types
        assert "EMAIL_ADDRESS" in entity_types

    def test_salesforce_data(self, client):
        """Test anonymizing Salesforce data."""
        text = """
        Salesforce Record:
        - Account ID: 0015000000AbcDEFG
        - Contact: Jane Doe (jane.doe@company.com)
        - Case: 5005000000XyzABCD
        """

        response = client.post("/anonymize", json={"text": text}, content_type="application/json")
        assert response.status_code == 200
        data = json.loads(response.data)

        entity_types = set(e["type"] for e in data["entities_found"])
        assert "SALESFORCE_ID" in entity_types
        assert "EMAIL_ADDRESS" in entity_types
