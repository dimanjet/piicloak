"""
Configuration settings for PIICloak.
"""

import os

# Server configuration - Standard port 8000 (same as Django, FastAPI default)
HOST = os.getenv("PIICLOAK_HOST", "0.0.0.0")
PORT = int(os.getenv("PIICLOAK_PORT", "8000"))
DEBUG = os.getenv("PIICLOAK_DEBUG", "false").lower() == "true"
WORKERS = int(os.getenv("PIICLOAK_WORKERS", "4"))

# Logging configuration
LOG_LEVEL = os.getenv("PIICLOAK_LOG_LEVEL", "INFO")
LOG_FORMAT = os.getenv("PIICLOAK_LOG_FORMAT", "json")  # json or text

# NLP configuration
SPACY_MODEL = os.getenv("PIICLOAK_SPACY_MODEL", "en_core_web_lg")
DEFAULT_LANGUAGE = os.getenv("PIICLOAK_DEFAULT_LANGUAGE", "en")

# Detection configuration
DEFAULT_SCORE_THRESHOLD = float(os.getenv("PIICLOAK_SCORE_THRESHOLD", "0.4"))
DEFAULT_MODE = os.getenv("PIICLOAK_DEFAULT_MODE", "replace")

# Security configuration
API_KEY = os.getenv("PIICLOAK_API_KEY", "")  # Empty = no auth required
CORS_ORIGINS = os.getenv("PIICLOAK_CORS_ORIGINS", "*")
RATE_LIMIT = os.getenv("PIICLOAK_RATE_LIMIT", "100/minute")

# Metrics configuration
ENABLE_METRICS = os.getenv("PIICLOAK_ENABLE_METRICS", "true").lower() == "true"

# Supported anonymization modes
ANONYMIZATION_MODES = ["replace", "redact", "hash", "mask"]
