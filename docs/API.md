# PIICloak API Reference

Complete API documentation for PIICloak REST endpoints.

## Base URL

```
http://localhost:8000
```

---

## Authentication

Optional API key authentication can be enabled via `PIICLOAK_API_KEY` environment variable.

When enabled, include the API key in requests:

```bash
curl -H "Authorization: Bearer your-api-key" ...
```

---

## Endpoints

### POST /anonymize

Anonymize PII in text.

**Request:**

```json
{
  "text": "string (required)",
  "entities": ["string"],  // optional, defaults to all
  "mode": "string",        // optional: replace|mask|redact|hash
  "language": "string",    // optional, default: "en"
  "score_threshold": 0.4   // optional, range: 0-1
}
```

**Response:**

```json
{
  "original": "string",
  "anonymized": "string",
  "entities_found": [
    {
      "type": "string",
      "text": "string",
      "start": 0,
      "end": 0,
      "score": 0.0
    }
  ]
}
```

**Example:**

```bash
curl -X POST http://localhost:8000/anonymize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Contact John at john@acme.com",
    "mode": "replace"
  }'
```

---

### POST /anonymize/docx

Anonymize PII in .docx documents.

**Request:**

- Content-Type: `multipart/form-data`
- Fields:
  - `document`: File (required)
  - `entities`: Comma-separated list (optional)
  - `mode`: replace|mask|redact|hash (optional)
  - `language`: Language code (optional)
  - `score_threshold`: Float 0-1 (optional)

**Response:**

```json
{
  "anonymized_text": "string",
  "entities_found": [...]
}
```

**Example:**

```bash
curl -X POST http://localhost:8000/anonymize/docx \
  -F "document=@contract.docx" \
  -F "mode=mask" \
  -F "entities=PERSON,EMAIL_ADDRESS"
```

---

### POST /analyze

Detect PII without anonymizing.

**Request:**

```json
{
  "text": "string (required)",
  "entities": ["string"],  // optional
  "language": "string",    // optional
  "score_threshold": 0.4   // optional
}
```

**Response:**

```json
{
  "text": "string",
  "contains_pii": true,
  "entities_found": [...]
}
```

---

### GET /entities

List all supported entity types.

**Response:**

```json
{
  "supported_entities": ["PERSON", "EMAIL_ADDRESS", ...],
  "modes": ["replace", "redact", "hash", "mask"],
  "categories": {
    "personal": [...],
    "financial": [...],
    ...
  }
}
```

---

### GET /metrics

Prometheus metrics endpoint.

**Response:** Plain text Prometheus format

```
# HELP piicloak_requests_total Total number of HTTP requests
# TYPE piicloak_requests_total counter
piicloak_requests_total 1234
...
```

---

### GET /health

Health check endpoint.

**Response:**

```json
{
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
}
```

---

## Entity Types

### Personal Information

- `PERSON` - Person names
- `EMAIL_ADDRESS` - Email addresses
- `PHONE_NUMBER` - Phone numbers
- `US_SSN` - Social Security Numbers
- `US_PASSPORT` - Passport numbers
- `US_DRIVER_LICENSE` - Driver's licenses
- `ADDRESS` - Physical addresses

### Financial

- `CREDIT_CARD` - Credit card numbers
- `BANK_ACCOUNT` - Bank account/routing numbers
- `TAX_ID` - EIN/TIN numbers
- `IBAN_CODE` - International bank account numbers
- `CRYPTO` - Cryptocurrency addresses
- `US_BANK_NUMBER` - US bank account numbers

### Organizational

- `ORGANIZATION` - Company/organization names
- `SALESFORCE_ID` - Salesforce record IDs
- `ACCOUNT_ID` - Customer/account IDs
- `DOMAIN` - Domain names

### Legal

- `CASE_NUMBER` - Legal case/docket numbers
- `CONTRACT_NUMBER` - Contract/policy numbers

### Technical

- `IP_ADDRESS` - IP addresses
- `URL` - URLs
- `API_KEY` - API keys (OpenAI, AWS, GitHub, Stripe)

### Other

- `DATE_TIME` - Dates and times
- `LOCATION` - Geographic locations
- `NRP` - National registry of persons
- `MEDICAL_LICENSE` - Medical license numbers
- `UK_NHS` - UK NHS numbers

---

## Error Responses

### 400 Bad Request

```json
{
  "error": "Missing 'text' field"
}
```

### 401 Unauthorized

```json
{
  "error": "Unauthorized",
  "message": "Valid API key required"
}
```

### 500 Internal Server Error

```json
{
  "error": "Internal server error",
  "message": "Error description"
}
```

---

## Rate Limiting

Default: 100 requests/minute (configurable via `PIICLOAK_RATE_LIMIT`)

Rate limit headers:
- `X-RateLimit-Limit`
- `X-RateLimit-Remaining`
- `X-RateLimit-Reset`

---

## SDK Usage

### Python

```python
from piicloak import PIICloak

# Initialize
cloak = PIICloak(score_threshold=0.4)

# Anonymize
result = cloak.anonymize(
    "Contact John at john@acme.com",
    mode="replace"
)
print(result.anonymized)
print(result.entities_found)

# Analyze only
result = cloak.analyze("Text to analyze")
print(result.contains_pii)
```

---

## Best Practices

1. **Use appropriate score_threshold** - Higher values (0.7-1.0) for fewer false positives
2. **Filter entities** - Specify only needed entity types for better performance
3. **Batch requests** - Process multiple texts in parallel for higher throughput
4. **Enable API key** - Always use authentication in production
5. **Monitor metrics** - Use `/metrics` endpoint for observability
6. **Handle errors** - Implement retry logic with exponential backoff
