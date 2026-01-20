"""
PIICloak - Enterprise-grade PII detection and anonymization API.

Optimized for Salesforce data and legal documents.
"""

__version__ = "1.0.1"
__author__ = "Dmitry Marinov"
__license__ = "MIT"

from .engine import create_analyzer, create_anonymizer
from .recognizers import SUPPORTED_ENTITIES

__all__ = [
    "PIICloak",
    "create_analyzer",
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
    
    def __init__(self, score_threshold=0.4):
        """
        Initialize PIICloak.
        
        Args:
            score_threshold: Minimum confidence score (0-1) for detection
        """
        self.analyzer = create_analyzer()
        self.anonymizer = create_anonymizer()
        self.score_threshold = score_threshold
    
    def anonymize(self, text, mode="replace", entities=None):
        """
        Anonymize PII in text.
        
        Args:
            text: Text to anonymize
            mode: Anonymization mode (replace, mask, redact, hash)
            entities: List of entity types to detect (None = all)
            
        Returns:
            Result object with .anonymized and .entities_found attributes
        """
        from .recognizers import SUPPORTED_ENTITIES as DEFAULT_ENTITIES
        from presidio_anonymizer.entities import OperatorConfig
        
        entities = entities or DEFAULT_ENTITIES
        
        results = self.analyzer.analyze(
            text=text,
            entities=entities,
            language="en",
            score_threshold=self.score_threshold
        )
        
        if mode == 'redact':
            operators = {"DEFAULT": OperatorConfig("redact")}
        elif mode == 'hash':
            operators = {"DEFAULT": OperatorConfig("hash", {"hash_type": "sha256"})}
        elif mode == 'mask':
            operators = {"DEFAULT": OperatorConfig("mask", {
                "chars_to_mask": 100, "masking_char": "*", "from_end": False
            })}
        else:
            operators = {"DEFAULT": OperatorConfig("replace")}
        
        anonymized_result = self.anonymizer.anonymize(
            text=text,
            analyzer_results=results,
            operators=operators
        )
        
        class Result:
            def __init__(self, original, anonymized, entities):
                self.original = original
                self.anonymized = anonymized
                self.entities_found = entities
        
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
        
        return Result(text, anonymized_result.text, entities_found)
    
    def analyze(self, text, entities=None):
        """
        Detect PII without anonymizing.
        
        Args:
            text: Text to analyze
            entities: List of entity types to detect (None = all)
            
        Returns:
            Result object with .contains_pii and .entities_found attributes
        """
        from .recognizers import SUPPORTED_ENTITIES as DEFAULT_ENTITIES
        
        entities = entities or DEFAULT_ENTITIES
        
        results = self.analyzer.analyze(
            text=text,
            entities=entities,
            language="en",
            score_threshold=self.score_threshold
        )
        
        class Result:
            def __init__(self, text, contains_pii, entities):
                self.text = text
                self.contains_pii = contains_pii
                self.entities_found = entities
        
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
        
        return Result(text, len(results) > 0, entities_found)
