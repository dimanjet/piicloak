# PIICloak

<div align="center">

[![PyPI version](https://badge.fury.io/py/piicloak.svg)](https://pypi.org/project/piicloak/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-dimanjet%2Fpiicloak-blue?logo=docker)](https://hub.docker.com/r/dimanjet/piicloak)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

**Enterprise-grade PII detection and anonymization API**

Fast · Accurate · GDPR/CCPA Ready · 31 Entity Types

[Quick Start](#-quick-start) · [Documentation](#-documentation) · [Use Cases](#-use-cases) · [API Reference](#-api-reference)

</div>

---

## 🎯 What is PIICloak?

PIICloak is a production-ready REST API service for **detecting and anonymizing Personally Identifiable Information (PII)** in text and documents. Built on Microsoft's [Presidio](https://github.com/microsoft/presidio) with custom recognizers optimized for:

- 🏢 **Salesforce data** (Account/Contact/Case IDs)
- ⚖️ **Legal documents** (Case numbers, contracts)
- 💰 **Financial data** (Bank accounts, tax IDs)
- 🏥 **Healthcare** (Medical records, HIPAA compliance)
- 💻 **Technical data** (API keys, IP addresses)

### Why PIICloak?

| Feature | PIICloak | Alternatives |
|---------|----------|--------------|
| **Entity Types** | 31 (including custom business entities) | 10-15 standard types |
| **Organization Detection** | ✅ NER-based (works with ANY company name) | ❌ Pattern-only |
| **Salesforce Support** | ✅ Native (Account/Contact/Case/Lead IDs) | ❌ Not included |
| **Legal Document Support** | ✅ Case numbers, contracts, dockets | ❌ Not included |
| **API Keys Detection** | ✅ OpenAI, AWS, GitHub, Stripe, generic | ⚠️ Limited |
| **SDK** | ✅ Python SDK included | ❌ API only |
| **One-Line Install** | ✅ `pip install piicloak` | ⚠️ Complex setup |
| **Docker Ready** | ✅ Production-grade image | ⚠️ Basic |
| **Metrics** | ✅ Prometheus built-in | ❌ None |
| **Auth** | ✅ Optional API key | ❌ None |

---

## 🚀 Quick Start

### 30-Second Setup

```bash
# Install
pip install piicloak

# Run
python -m piicloak
```

Server starts on `http://localhost:8000` 🎉

### Instant Test

```bash
curl -X POST http://localhost:8000/anonymize \
  -H "Content-Type: application/json" \
  -d '{"text": "Email john@acme.com, SSN 123-45-6789"}'
```

**Response:**
```json
{
  "anonymized": "Email <EMAIL_ADDRESS>, SSN <US_SSN>",
  "entities_found": [
    {"type": "EMAIL_ADDRESS", "text": "john@acme.com", "score": 1.0},
    {"type": "US_SSN", "text": "123-45-6789", "score": 0.85}
  ]
}
```

### Docker

```bash
docker run -p 8000:8000 dimanjet/piicloak
```

### Python SDK

```python
from piicloak import PIICloak

cloak = PIICloak()
result = cloak.anonymize("Contact John Smith at john@acme.com")
print(result.anonymized)  # "Contact <PERSON> at <EMAIL_ADDRESS>"
```

---

## ✨ Features

### Supported Entity Types (31)

| Entity Type | Description | Example |
|-------------|-------------|---------|
| **👤 PERSONAL IDENTIFIABLE INFORMATION** |||
| `PERSON` | Names of individuals (NER-based) | "John Smith", "Jane Doe" |
| `EMAIL_ADDRESS` | Email addresses | "john@example.com" |
| `PHONE_NUMBER` | Phone numbers (multiple formats) | "+1-555-123-4567", "(555) 123-4567" |
| `US_SSN` | US Social Security Numbers | "123-45-6789" |
| `US_PASSPORT` | US Passport numbers | "123456789" |
| `US_DRIVER_LICENSE` | US Driver's License numbers | "D1234567" |
| `ADDRESS` | Physical addresses (NER + patterns) | "123 Main St, New York, NY 10001" |
| **💳 FINANCIAL INFORMATION** |||
| `CREDIT_CARD` | Credit card numbers (all major brands) | "4532-1234-5678-9010" |
| `IBAN_CODE` | International Bank Account Numbers | "GB82 WEST 1234 5698 7654 32" |
| `US_BANK_NUMBER` | US bank account numbers | "123456789012" |
| `BANK_ACCOUNT` | Generic bank account patterns | "ACC-123456789" |
| `TAX_ID` | Tax IDs (EIN/TIN) | "12-3456789" |
| `CRYPTO` | Cryptocurrency addresses | "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa" |
| **🏢 ORGANIZATIONAL DATA** |||
| `ORGANIZATION` | Company names (NER-based) | "Acme Corp", "Tech Industries Inc" |
| `DOMAIN` | Internet domains | "example.com", "company.io" |
| `SALESFORCE_ID` | Salesforce record IDs (Account/Contact/Case/Lead) | "0015000000AbcDEF", "5005000000XyzABC" |
| `ACCOUNT_ID` | Generic account identifiers | "ACC-123456", "A-987654" |
| **⚖️ LEGAL DOCUMENTS** |||
| `CASE_NUMBER` | Court case numbers (Federal/State) | "1:24-cv-12345", "CR-2024-001234" |
| `CONTRACT_NUMBER` | Contract and agreement numbers | "CONT-2024-001", "AGR-123456" |
| **💻 TECHNICAL & SECURITY** |||
| `USERNAME` | Usernames and login IDs | "john_smith123", "@johndoe", "admin" |
| `API_KEY` | API keys (OpenAI, AWS, GitHub, Stripe, generic) | "sk-1234567890abcdef...", "ghp_abc..." |
| `IP_ADDRESS` | IPv4 and IPv6 addresses | "192.168.1.1", "2001:0db8::1" |
| `URL` | Web URLs | "https://example.com/page" |
| **🏥 HEALTHCARE & OTHER** |||
| `MEDICAL_LICENSE` | Medical license numbers | "MD-123456" |
| `UK_NHS` | UK NHS numbers | "123 456 7890" |
| `NRP` | Número de Registro de Personas (Spanish ID) | "12345678A" |
| `LOCATION` | Geographic locations (NER-based) | "New York", "San Francisco" |
| `DATE_TIME` | Dates and timestamps | "2024-01-20", "January 20th, 2024" |

**Total: 31 entity types** covering personal, financial, organizational, legal, technical, and healthcare data.

### Anonymization Modes

```python
# Replace with entity type (default)
{"mode": "replace"} → "Contact <PERSON> at <EMAIL_ADDRESS>"

# Mask with asterisks
{"mode": "mask"} → "Contact ******** at ****************"

# Redact (remove completely)
{"mode": "redact"} → "Contact  at "

# Hash (SHA256)
{"mode": "hash"} → "Contact a1b2c3d4... at e5f6g7h8..."
```

---

## 💼 Use Cases

### Salesforce Data Protection

```bash
curl -X POST http://localhost:8000/anonymize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Account: 0015000000AbcDEFG, Contact: Jane Doe (jane@company.com), Case: 5005000000XyzABC"
  }'
```

**Output:**
```
Account: <SALESFORCE_ID>, Contact: <PERSON> (<EMAIL_ADDRESS>), Case: <SALESFORCE_ID>
```

### Legal Documents

```bash
curl -X POST http://localhost:8000/anonymize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Case No. 1:24-cv-12345 - Plaintiff John Doe (SSN: 123-45-6789) vs. Acme Corp (EIN: 12-3456789)"
  }'
```

**Output:**
```
Case No. <CASE_NUMBER> - Plaintiff <PERSON> (SSN: <US_SSN>) vs. <ORGANIZATION> (EIN: <TAX_ID>)
```

### API Keys & Secrets

```bash
curl -X POST http://localhost:8000/anonymize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "OpenAI key: sk-1234567890abcdefghijklmnopqrstuv, GitHub: ghp_abcdefghijklmnopqrstuvwxyz1234567890"
  }'
```

**Output:**
```
OpenAI key: <API_KEY>, GitHub: <API_KEY>
```

### .docx Files

```bash
curl -X POST http://localhost:8000/anonymize/docx \
  -F "document=@contract.docx" \
  -F "mode=replace"
```

---

## 📖 Documentation

### Installation

```bash
# Basic installation
pip install piicloak

# Download NLP model (required)
python -m spacy download en_core_web_lg

# Or install everything at once
pip install piicloak && python -m spacy download en_core_web_lg
```

### Configuration

All settings use the `PIICLOAK_` prefix and have sensible defaults:

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `PIICLOAK_HOST` | `0.0.0.0` | Server host |
| `PIICLOAK_PORT` | `8000` | Server port (standard) |
| `PIICLOAK_DEBUG` | `false` | Debug mode |
| `PIICLOAK_WORKERS` | `4` | Gunicorn workers |
| `PIICLOAK_LOG_LEVEL` | `INFO` | Logging level |
| `PIICLOAK_SPACY_MODEL` | `en_core_web_lg` | spaCy model |
| `PIICLOAK_SCORE_THRESHOLD` | `0.4` | Min confidence score (0-1) |
| `PIICLOAK_DEFAULT_MODE` | `replace` | Default anonymization mode |
| `PIICLOAK_CORS_ORIGINS` | `*` | CORS allowed origins |
| `PIICLOAK_API_KEY` | `""` | Optional API key (empty = no auth) |
| `PIICLOAK_RATE_LIMIT` | `100/minute` | Rate limiting |
| `PIICLOAK_ENABLE_METRICS` | `true` | Prometheus metrics |

Example:
```bash
export PIICLOAK_PORT=9000
export PIICLOAK_API_KEY=your-secret-key
python -m piicloak
```

---

## 🔌 API Reference

### Endpoints

#### POST `/anonymize` - Anonymize Text

**Request:**
```json
{
  "text": "Contact John at john@acme.com",
  "entities": ["PERSON", "EMAIL_ADDRESS"],  // optional
  "mode": "replace",                        // optional
  "language": "en",                         // optional
  "score_threshold": 0.4                    // optional
}
```

**Response:**
```json
{
  "original": "Contact John at john@acme.com",
  "anonymized": "Contact <PERSON> at <EMAIL_ADDRESS>",
  "entities_found": [...]
}
```

#### POST `/analyze` - Detect PII Only

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Contact john@example.com"}'
```

#### GET `/entities` - List Supported Entities

```bash
curl http://localhost:8000/entities
```

#### GET `/metrics` - Prometheus Metrics

```bash
curl http://localhost:8000/metrics
```

#### GET `/health` - Health Check

```bash
curl http://localhost:8000/health
```

---

## 🐳 Deployment

### Docker

```bash
# Build
docker build -t piicloak .

# Run
docker run -p 8000:8000 piicloak

# With environment variables
docker run -p 8000:8000 \
  -e PIICLOAK_API_KEY=your-key \
  -e PIICLOAK_WORKERS=8 \
  piicloak
```

### Docker Compose

```bash
docker-compose up -d
```

### Production (Gunicorn)

```bash
pip install gunicorn
gunicorn -c gunicorn.conf.py "piicloak.app:create_application()"
```

### Kubernetes

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for Kubernetes deployment guide.

---

## 🛠️ Development

### Setup

```bash
# Clone repository
git clone https://github.com/dimanjet/piicloak.git
cd piicloak

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dev dependencies
pip install -e ".[dev]"

# Download spaCy model
python -m spacy download en_core_web_lg

# Run tests
pytest

# Run with coverage
pytest --cov=piicloak --cov-report=html

# Format code
black src/ tests/

# Lint
flake8 src/ tests/
```

### Project Structure

```
piicloak/
├── src/piicloak/
│   ├── __init__.py          # PIICloak SDK class
│   ├── __main__.py          # CLI entry point
│   ├── app.py               # Application factory
│   ├── api.py               # REST API endpoints
│   ├── config.py            # Configuration
│   ├── engine.py            # Analyzer/Anonymizer setup
│   ├── recognizers.py       # Custom PII recognizers
│   ├── middleware.py        # Auth, CORS, logging
│   └── metrics.py           # Prometheus metrics
├── tests/                   # Comprehensive test suite
├── docs/                    # Documentation
├── Dockerfile               # Production Docker image
├── docker-compose.yml       # Docker Compose config
├── gunicorn.conf.py         # Gunicorn configuration
└── requirements.txt         # Dependencies
```

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Adding New Recognizers

To add a new PII recognizer:

1. Add pattern(s) to `src/piicloak/recognizers.py`
2. Create a factory function
3. Add to `SUPPORTED_ENTITIES`
4. Write tests in `tests/test_recognizers.py`
5. Update README

Example:
```python
def create_license_plate_recognizer() -> PatternRecognizer:
    patterns = [
        Pattern("US_PLATE", r"\b[A-Z]{2,3}[-\s]?\d{3,4}\b", 0.7),
    ]
    return PatternRecognizer(
        supported_entity="LICENSE_PLATE",
        patterns=patterns
    )
```

---

## 📊 Performance

- **Throughput:** ~100 requests/second (single worker)
- **Latency:** <100ms per request (average)
- **Memory:** ~500MB (with spaCy model loaded)
- **Scalability:** Stateless design, horizontally scalable

---

## 🔒 Security

- Optional API key authentication
- CORS configuration
- Rate limiting support
- Security headers included
- No data retention
- Stateless operation

Report security vulnerabilities to: marinovdk@gmail.com

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Acknowledgments

PIICloak is built on top of these excellent open-source projects:

- [Microsoft Presidio](https://github.com/microsoft/presidio) (MIT License)
- [spaCy](https://spacy.io/) (MIT License)
- [Flask](https://flask.palletsprojects.com/) (BSD-3-Clause License)
- [python-docx](https://github.com/python-openxml/python-docx) (MIT License)

---

## 🌟 Star History

If you find PIICloak useful, please consider giving it a star ⭐

[![Star History Chart](https://api.star-history.com/svg?repos=dimanjet/piicloak&type=Date)](https://star-history.com/#dimanjet/piicloak&Date)

---

## 📫 Contact & Support

- **Author:** Dmitry Marinov
- **Email:** marinovdk@gmail.com
- **GitHub:** [@dimanjet](https://github.com/dimanjet)
- **Issues:** [GitHub Issues](https://github.com/dimanjet/piicloak/issues)

---

<div align="center">

**Made with ❤️ for the privacy-conscious developer community**

[⬆ Back to Top](#piicloak)

</div>
