"""
PII Analyzer and Anonymizer engine setup.
"""

import spacy
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine

from .config import SPACY_MODEL, DEFAULT_LANGUAGE
from .recognizers import (
    SpacyOrgRecognizer,
    SpacyAddressRecognizer,
    SpacyUsernameRecognizer,
    get_all_pattern_recognizers,
)


def load_spacy_model(model_name: str = SPACY_MODEL):
    """Load spaCy model for NER."""
    return spacy.load(model_name)


def create_analyzer(nlp=None) -> AnalyzerEngine:
    """
    Create and configure the PII analyzer engine.
    
    Args:
        nlp: Optional pre-loaded spaCy model
        
    Returns:
        Configured AnalyzerEngine instance
    """
    # Load spaCy model if not provided
    if nlp is None:
        nlp = load_spacy_model()
    
    # Configure NLP engine for presidio
    configuration = {
        "nlp_engine_name": "spacy",
        "models": [{"lang_code": DEFAULT_LANGUAGE, "model_name": SPACY_MODEL}],
    }
    provider = NlpEngineProvider(nlp_configuration=configuration)
    nlp_engine = provider.create_engine()
    
    # Create analyzer
    analyzer = AnalyzerEngine(
        nlp_engine=nlp_engine, 
        supported_languages=[DEFAULT_LANGUAGE]
    )
    
    # Register NER-based recognizers
    analyzer.registry.add_recognizer(SpacyOrgRecognizer(nlp))
    analyzer.registry.add_recognizer(SpacyAddressRecognizer(nlp))
    analyzer.registry.add_recognizer(SpacyUsernameRecognizer(nlp))
    
    # Register pattern-based recognizers
    for recognizer in get_all_pattern_recognizers():
        analyzer.registry.add_recognizer(recognizer)
    
    return analyzer


def create_anonymizer() -> AnonymizerEngine:
    """Create the anonymizer engine."""
    return AnonymizerEngine()
