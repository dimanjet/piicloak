# Changelog

All notable changes to PIICloak will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-01-20

### Added

#### Core Features
- **27+ PII Entity Types** - Comprehensive PII detection including:
  - Personal: PERSON, EMAIL_ADDRESS, PHONE_NUMBER, US_SSN, US_PASSPORT, US_DRIVER_LICENSE, ADDRESS
  - Financial: CREDIT_CARD, BANK_ACCOUNT, TAX_ID (EIN/TIN), IBAN_CODE, CRYPTO
  - Organizational: ORGANIZATION (NER-based), SALESFORCE_ID, ACCOUNT_ID, DOMAIN
  - Legal: CASE_NUMBER (Federal/State), CONTRACT_NUMBER
  - Technical: IP_ADDRESS, URL, API_KEY (OpenAI/AWS/GitHub/Stripe)
  - Other: DATE_TIME, LOCATION, MEDICAL_LICENSE, UK_NHS

#### API Endpoints
- `POST /anonymize` - Anonymize PII in text
- `POST /anonymize/docx` - Anonymize .docx files
- `POST /analyze` - Detect PII without anonymizing
- `GET /entities` - List all supported entity types
- `GET /metrics` - Prometheus metrics
- `GET /health` - Health check with detailed status

#### Python SDK
- `PIICloak` class for easy integration
- `.anonymize()` method with multiple modes
- `.analyze()` method for detection only
- Support for custom score thresholds

#### Anonymization Modes
- **replace** - Replace with entity type placeholders
- **mask** - Replace with asterisks
- **redact** - Remove completely
- **hash** - Replace with SHA256 hash

#### Custom Recognizers
- **SpacyOrgRecognizer** - NER-based organization detection (works with ANY company name)
- **SpacyAddressRecognizer** - NER-based address detection
- **SSN Recognizer** - Multiple SSN formats (dashes, spaces, no dashes)
- **API Key Recognizer** - Detects OpenAI, AWS, GitHub, Stripe, generic keys
- **Salesforce ID Recognizer** - Account, Contact, Case, Lead, Opportunity IDs
- **Case Number Recognizer** - Federal and state court case numbers
- **Tax ID Recognizer** - EIN, TIN formats
- **Bank Account Recognizer** - Routing numbers, account numbers, IBAN, SWIFT
- **Contract Number Recognizer** - Contracts, policies, orders, MSAs

#### Enterprise Features
- **Authentication** - Optional API key support (`PIICLOAK_API_KEY`)
- **CORS Configuration** - Configurable origins (`PIICLOAK_CORS_ORIGINS`)
- **Rate Limiting** - Built-in rate limiting support
- **Security Headers** - X-Content-Type-Options, X-Frame-Options, HSTS
- **Request ID Tracking** - X-Request-ID header for tracing
- **Structured Logging** - JSON and text formats
- **Prometheus Metrics** - Request counts, duration, errors, entities detected

#### Configuration
- Standard port **8000** (Django/FastAPI default)
- `PIICLOAK_` prefix for all environment variables
- 12 configurable settings with sensible defaults
- Support for multiple spaCy models

#### Deployment
- **Docker** - Production-ready multi-stage Dockerfile
- **Docker Compose** - Ready-to-use compose file
- **Gunicorn** - Production WSGI server configuration
- **Kubernetes** - Complete manifests with HPA
- Non-root user execution for security
- Health checks and graceful shutdown

#### Documentation
- Comprehensive README with quickstart
- API reference with examples
- Configuration guide
- Deployment guide (Docker, K8s, AWS, GCP, Azure)
- Contributing guidelines
- Code of Conduct
- Security policy

#### Developer Experience
- **One-line install**: `pip install piicloak && python -m piicloak`
- **One-line Docker**: `docker run -p 8000:8000 dimanjet/piicloak`
- Command-line entry point: `python -m piicloak`
- Comprehensive test suite (pytest)
- Type hints throughout
- Black code formatting
- Flake8 linting

#### CI/CD
- GitHub Actions workflows for CI
- Automated testing on Python 3.9-3.12
- CodeQL security scanning
- Automated PyPI publishing on release
- Code coverage reporting

#### Community
- GitHub issue templates (bug report, feature request)
- Pull request template
- Contributing guidelines
- Security vulnerability reporting process
- Code of Conduct (Contributor Covenant)
- CITATION.cff for academic citations

### Technical Details

- **Base Framework**: Flask 3.1+
- **NLP Engine**: spaCy 3.8+ with en_core_web_lg model
- **PII Detection**: Microsoft Presidio 2.2+
- **Python**: 3.9, 3.10, 3.11, 3.12 support
- **License**: MIT
- **Architecture**: Stateless, horizontally scalable

### Performance

- ~100 requests/second (single worker)
- <100ms average latency
- ~500MB memory footprint (with large spaCy model)
- Supports horizontal scaling

### Security

- Optional API key authentication
- CORS configuration
- Security headers
- No data retention
- Stateless operation
- Non-root container execution

---

## [Unreleased]

### Planned Features

- Support for additional languages (Spanish, French, German)
- Batch processing endpoint for multiple texts
- Webhook support for async processing
- PDF document support
- Custom entity training interface
- Web UI for testing
- CLI tool for file processing
- Redis caching for improved performance
- OpenTelemetry tracing
- More fine-grained entity filtering

---

## Release Notes Format

### Types of Changes

- **Added** - New features
- **Changed** - Changes in existing functionality
- **Deprecated** - Soon-to-be removed features
- **Removed** - Removed features
- **Fixed** - Bug fixes
- **Security** - Vulnerability fixes

---

## Version History

| Version | Release Date | Highlights |
|---------|--------------|------------|
| 1.0.0 | 2026-01-20 | Initial release with 27+ entity types, enterprise features |

---

## Upgrade Guide

### To 1.0.0

First release - no migration needed.

---

## Support

- **Issues**: https://github.com/dimanjet/piicloak/issues
- **Discussions**: https://github.com/dimanjet/piicloak/discussions
- **Security**: marinovdk@gmail.com
