"""
PIICloak - Enterprise-grade PII detection and anonymization API.

Optimized for Salesforce data and legal documents.
"""

__version__ = "1.2.1"  # x-release-please-version
__author__ = "Dmitry Marinov"
__license__ = "MIT"

from .engine import create_analyzer, create_anonymizer, create_detector_backend
from .recognizers import SUPPORTED_ENTITIES

__all__ = [
    "PIICloak",
    "create_analyzer",
    "create_detector_backend",
    "create_anonymizer",
    "SUPPORTED_ENTITIES",
    "__version__",
]


# PIICloak SDK class for easy usage
class PIICloak:
    """
    PIICloak client for detecting and anonymizing PII.

    Example:
        >>> from piicloak import PIICloak
        >>> cloak = PIICloak()
        >>> result = cloak.anonymize("Contact John at john@acme.com")
        >>> print(result.anonymized)
        "Contact <PERSON> at <EMAIL_ADDRESS>"
    """

    def __init__(self, score_threshold=0.4, detector_backend="presidio"):
        """
        Initialize PIICloak.

        Args:
            score_threshold: Minimum confidence score (0-1) for detection
            detector_backend: Detection backend, either "presidio" or "privacy-filter"
        """
        self.analyzer = create_detector_backend(detector_backend)
        self.anonymizer = create_anonymizer()
        self.score_threshold = score_threshold

    def anonymize(self, text, mode="replace", entities=None, safe_response=False):
        """
        Anonymize PII in text.

        Args:
            text: Text to anonymize
            mode: Anonymization mode (replace, mask, redact, hash)
            entities: List of entity types to detect (None = all)
            safe_response: Omit raw input and matched entity text from the result

        Returns:
            Result object with .anonymized and .entities_found attributes
        """
        from .recognizers import SUPPORTED_ENTITIES as DEFAULT_ENTITIES
        from presidio_anonymizer.entities import OperatorConfig

        entities = entities or DEFAULT_ENTITIES

        results = self.analyzer.analyze(
            text=text, entities=entities, language="en", score_threshold=self.score_threshold
        )

        if mode == "redact":
            operators = {"DEFAULT": OperatorConfig("redact")}
        elif mode == "hash":
            operators = {"DEFAULT": OperatorConfig("hash", {"hash_type": "sha256"})}
        elif mode == "mask":
            operators = {
                "DEFAULT": OperatorConfig(
                    "mask", {"chars_to_mask": 100, "masking_char": "*", "from_end": False}
                )
            }
        else:
            operators = {"DEFAULT": OperatorConfig("replace")}

        anonymized_result = self.anonymizer.anonymize(
            text=text, analyzer_results=results, operators=operators
        )

        class Result:
            def __init__(self, original, anonymized, entities):
                self.original = original
                self.anonymized = anonymized
                self.entities_found = entities

        entities_found = []
        for result in results:
            entity = {
                "type": result.entity_type,
                "start": result.start,
                "end": result.end,
                "score": round(result.score, 3),
            }
            if not safe_response:
                entity["text"] = text[result.start : result.end]
            entities_found.append(entity)

        return Result(None if safe_response else text, anonymized_result.text, entities_found)

    def analyze(self, text, entities=None, safe_response=False):
        """
        Detect PII without anonymizing.

        Args:
            text: Text to analyze
            entities: List of entity types to detect (None = all)
            safe_response: Omit raw input and matched entity text from the result

        Returns:
            Result object with .contains_pii and .entities_found attributes
        """
        from .recognizers import SUPPORTED_ENTITIES as DEFAULT_ENTITIES

        entities = entities or DEFAULT_ENTITIES

        results = self.analyzer.analyze(
            text=text, entities=entities, language="en", score_threshold=self.score_threshold
        )

        class Result:
            def __init__(self, text, contains_pii, entities):
                self.text = text
                self.contains_pii = contains_pii
                self.entities_found = entities

        entities_found = []
        for result in results:
            entity = {
                "type": result.entity_type,
                "start": result.start,
                "end": result.end,
                "score": round(result.score, 3),
            }
            if not safe_response:
                entity["text"] = text[result.start : result.end]
            entities_found.append(entity)

        return Result(None if safe_response else text, len(results) > 0, entities_found)
