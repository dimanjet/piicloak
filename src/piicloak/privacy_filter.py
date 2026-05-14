"""
Optional OpenAI Privacy Filter detector backend.

The backend is imported lazily so normal PIICloak installs do not require the
Privacy Filter runtime or download a checkpoint. Selecting this backend without
an explicit checkpoint requires PIICLOAK_PRIVACY_FILTER_ALLOW_DOWNLOAD=true.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from presidio_analyzer import RecognizerResult

from .config import (
    PRIVACY_FILTER_ALLOW_DOWNLOAD,
    PRIVACY_FILTER_CHECKPOINT,
    PRIVACY_FILTER_DEVICE,
)

LABEL_TO_ENTITY = {
    "account_number": "ACCOUNT_ID",
    "private_address": "ADDRESS",
    "private_email": "EMAIL_ADDRESS",
    "private_person": "PERSON",
    "private_phone": "PHONE_NUMBER",
    "private_url": "URL",
    "private_date": "DATE_TIME",
    "secret": "API_KEY",
}


@dataclass(frozen=True)
class PrivacyFilterConfig:
    checkpoint: str = PRIVACY_FILTER_CHECKPOINT
    allow_download: bool = PRIVACY_FILTER_ALLOW_DOWNLOAD
    device: str = PRIVACY_FILTER_DEVICE


class PrivacyFilterAnalyzer:
    """Adapter exposing OPF spans through the AnalyzerEngine analyze interface."""

    supported_entities = sorted(set(LABEL_TO_ENTITY.values()))

    def __init__(self, config: PrivacyFilterConfig | None = None):
        self.config = config or PrivacyFilterConfig()
        self._redactor = None

    def _checkpoint(self) -> str | None:
        if self.config.checkpoint:
            return self.config.checkpoint
        if os.environ.get("OPF_CHECKPOINT"):
            return None
        if self.config.allow_download:
            return None
        raise RuntimeError(
            "Privacy Filter backend requires PIICLOAK_PRIVACY_FILTER_CHECKPOINT, "
            "OPF_CHECKPOINT, or PIICLOAK_PRIVACY_FILTER_ALLOW_DOWNLOAD=true"
        )

    def _load_redactor(self):
        if self._redactor is not None:
            return self._redactor
        checkpoint = self._checkpoint()
        try:
            from opf import OPF
        except ImportError as exc:
            raise RuntimeError(
                "Privacy Filter backend requires the optional OpenAI opf package. "
                "On Python 3.10+, install OpenAI's official package source from "
                "https://github.com/openai/privacy-filter."
            ) from exc
        self._redactor = OPF(
            model=checkpoint,
            device=self.config.device,
            output_mode="typed",
            output_text_only=False,
        )
        return self._redactor

    def analyze(
        self,
        text: str,
        entities: list[str] | None,
        language: str = "en",
        score_threshold: float = 0.4,
    ) -> list[RecognizerResult]:
        del language
        allowed = set(entities or LABEL_TO_ENTITY.values())
        result = self._load_redactor().redact(text)
        spans = getattr(result, "detected_spans", ())
        recognizer_results: list[RecognizerResult] = []
        for span in spans:
            entity_type = LABEL_TO_ENTITY.get(str(getattr(span, "label", "")))
            if entity_type is None or entity_type not in allowed:
                continue
            score = float(getattr(span, "score", 1.0))
            if score < score_threshold:
                continue
            recognizer_results.append(
                RecognizerResult(
                    entity_type=entity_type,
                    start=int(getattr(span, "start")),
                    end=int(getattr(span, "end")),
                    score=score,
                )
            )
        return recognizer_results


def create_privacy_filter_analyzer(
    checkpoint: str = PRIVACY_FILTER_CHECKPOINT,
    allow_download: bool = PRIVACY_FILTER_ALLOW_DOWNLOAD,
    device: str = PRIVACY_FILTER_DEVICE,
) -> PrivacyFilterAnalyzer:
    """Create a Privacy Filter analyzer adapter without loading the model yet."""
    return PrivacyFilterAnalyzer(
        PrivacyFilterConfig(
            checkpoint=checkpoint,
            allow_download=allow_download,
            device=device,
        )
    )
