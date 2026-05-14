"""Tests for the optional Privacy Filter detector backend."""

from types import SimpleNamespace

import pytest

from piicloak.privacy_filter import PrivacyFilterAnalyzer, PrivacyFilterConfig
from piicloak.api import create_app


class FakeRedactor:
    """Minimal OPF-compatible redactor for adapter tests."""

    def redact(self, text):
        assert text == "Email jane@example.com with secret token"
        return SimpleNamespace(
            detected_spans=(
                SimpleNamespace(
                    label="private_email",
                    start=6,
                    end=22,
                    text="jane@example.com",
                    placeholder="<PRIVATE_EMAIL>",
                ),
                SimpleNamespace(
                    label="secret",
                    start=35,
                    end=40,
                    text="token",
                    placeholder="<SECRET>",
                ),
            )
        )


def test_privacy_filter_requires_checkpoint_or_explicit_download():
    """Test the backend will not trigger OPF's default download by accident."""
    analyzer = PrivacyFilterAnalyzer(
        PrivacyFilterConfig(checkpoint="", allow_download=False, device="cpu")
    )

    with pytest.raises(RuntimeError, match="PIICLOAK_PRIVACY_FILTER_CHECKPOINT"):
        analyzer.analyze("hello", ["PERSON"])


def test_privacy_filter_maps_spans_to_piicloak_entities():
    """Test OPF labels are mapped to PIICloak entity names."""
    analyzer = PrivacyFilterAnalyzer(
        PrivacyFilterConfig(
            checkpoint="/tmp/fake-opf-checkpoint", allow_download=False, device="cpu"
        )
    )
    analyzer._redactor = FakeRedactor()

    results = analyzer.analyze(
        "Email jane@example.com with secret token",
        ["EMAIL_ADDRESS", "API_KEY"],
        score_threshold=0.4,
    )

    assert [(result.entity_type, result.start, result.end) for result in results] == [
        ("EMAIL_ADDRESS", 6, 22),
        ("API_KEY", 35, 40),
    ]


def test_privacy_filter_respects_entity_filter():
    """Test callers can request a subset of mapped entity types."""
    analyzer = PrivacyFilterAnalyzer(
        PrivacyFilterConfig(
            checkpoint="/tmp/fake-opf-checkpoint", allow_download=False, device="cpu"
        )
    )
    analyzer._redactor = FakeRedactor()

    results = analyzer.analyze(
        "Email jane@example.com with secret token",
        ["API_KEY"],
        score_threshold=0.4,
    )

    assert [result.entity_type for result in results] == ["API_KEY"]


def test_entities_endpoint_uses_privacy_filter_supported_entities():
    """Test /entities reflects the active backend capability."""
    analyzer = PrivacyFilterAnalyzer(
        PrivacyFilterConfig(
            checkpoint="/tmp/fake-opf-checkpoint", allow_download=False, device="cpu"
        )
    )
    app = create_app(analyzer, object())
    app.config["TESTING"] = True

    response = app.test_client().get("/entities")
    data = response.get_json()

    assert response.status_code == 200
    assert data["supported_entities"] == [
        "ACCOUNT_ID",
        "ADDRESS",
        "API_KEY",
        "DATE_TIME",
        "EMAIL_ADDRESS",
        "PERSON",
        "PHONE_NUMBER",
        "URL",
    ]
