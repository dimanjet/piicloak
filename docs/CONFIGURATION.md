# PIICloak Configuration Guide

Complete configuration reference for PIICloak.

---

## Environment Variables

All configuration uses the `PIICLOAK_` prefix for clarity and consistency.

### Server Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `PIICLOAK_HOST` | `0.0.0.0` | Server bind address |
| `PIICLOAK_PORT` | `8000` | Server port (standard REST API port) |
| `PIICLOAK_DEBUG` | `false` | Enable debug mode (not for production) |
| `PIICLOAK_WORKERS` | `4` | Number of Gunicorn worker processes |

**Example:**
```bash
export PIICLOAK_HOST=127.0.0.1
export PIICLOAK_PORT=9000
export PIICLOAK_WORKERS=8
python -m piicloak
```

---

### Logging Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `PIICLOAK_LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `PIICLOAK_LOG_FORMAT` | `json` | Log format (json or text) |

**Example:**
```bash
export PIICLOAK_LOG_LEVEL=DEBUG
export PIICLOAK_LOG_FORMAT=json
```

---

### NLP Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `PIICLOAK_SPACY_MODEL` | `en_core_web_lg` | spaCy model name |
| `PIICLOAK_DEFAULT_LANGUAGE` | `en` | Default language for analysis |

**Supported spaCy Models:**
- `en_core_web_sm` - Small (faster, less accurate)
- `en_core_web_md` - Medium (balanced)
- `en_core_web_lg` - Large (slower, most accurate) ✅ Recommended

**Example:**
```bash
# Use smaller model for faster inference
export PIICLOAK_SPACY_MODEL=en_core_web_md
python -m piicloak
```

---

### Detection Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `PIICLOAK_SCORE_THRESHOLD` | `0.4` | Minimum confidence score (0.0-1.0) |
| `PIICLOAK_DEFAULT_MODE` | `replace` | Default anonymization mode |

**Score Threshold Guidelines:**
- `0.3-0.4` - High recall (catch more, some false positives)
- `0.5-0.6` - Balanced
- `0.7-1.0` - High precision (fewer false positives, may miss some)

**Anonymization Modes:**
- `replace` - Replace with `<ENTITY_TYPE>`
- `mask` - Replace with `****`
- `redact` - Remove completely
- `hash` - Replace with SHA256 hash

**Example:**
```bash
export PIICLOAK_SCORE_THRESHOLD=0.6
export PIICLOAK_DEFAULT_MODE=mask
```

---

### Security Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `PIICLOAK_API_KEY` | `""` (empty) | API key for authentication (empty = no auth) |
| `PIICLOAK_CORS_ORIGINS` | `*` | CORS allowed origins |
| `PIICLOAK_RATE_LIMIT` | `100/minute` | Rate limiting |

**Production Security:**
```bash
# Generate strong API key
export PIICLOAK_API_KEY=$(openssl rand -hex 32)

# Restrict CORS
export PIICLOAK_CORS_ORIGINS="https://yourdomain.com,https://app.yourdomain.com"

# Set rate limit
export PIICLOAK_RATE_LIMIT="200/minute"
```

**Using API Key:**
```bash
curl -H "Authorization: Bearer your-api-key" \
  -X POST http://localhost:8000/anonymize \
  -d '{"text": "..."}'
```

---

### Metrics Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `PIICLOAK_ENABLE_METRICS` | `true` | Enable Prometheus metrics endpoint |

**Example:**
```bash
# Disable metrics
export PIICLOAK_ENABLE_METRICS=false
```

---

## Configuration Files

### gunicorn.conf.py

Production server configuration for Gunicorn:

```python
# Server socket
bind = "0.0.0.0:8000"

# Worker processes
workers = 4
worker_class = 'sync'
timeout = 120

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'
```

**Custom Configuration:**
```bash
gunicorn -c gunicorn.conf.py "piicloak.app:create_application()"
```

---

## Docker Configuration

### docker-compose.yml

```yaml
services:
  piicloak:
    image: dimanjet/piicloak
    ports:
      - "8000:8000"
    environment:
      - PIICLOAK_API_KEY=${API_KEY}
      - PIICLOAK_WORKERS=8
      - PIICLOAK_SCORE_THRESHOLD=0.5
    deploy:
      resources:
        limits:
          memory: 2G
```

**Run:**
```bash
docker-compose up -d
```

---

## Kubernetes Configuration

### ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: piicloak-config
data:
  PIICLOAK_HOST: "0.0.0.0"
  PIICLOAK_PORT: "8000"
  PIICLOAK_WORKERS: "4"
  PIICLOAK_LOG_LEVEL: "INFO"
  PIICLOAK_SCORE_THRESHOLD: "0.4"
```

### Secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: piicloak-secret
type: Opaque
data:
  PIICLOAK_API_KEY: <base64-encoded-key>
```

---

## Performance Tuning

### Memory

- Small model (`en_core_web_sm`): ~200MB
- Medium model (`en_core_web_md`): ~350MB
- Large model (`en_core_web_lg`): ~500MB

**Recommended:**
- Development: `en_core_web_md` with 2 workers
- Production: `en_core_web_lg` with 4-8 workers

### Workers

**Formula:** `workers = (2 x CPU cores) + 1`

**Examples:**
- 2 CPU cores → 5 workers
- 4 CPU cores → 9 workers
- 8 CPU cores → 17 workers

**Resource Requirements per Worker:**
- CPU: ~0.5 core
- Memory: ~500MB (with large model)

### Timeout

Default: 120 seconds

Adjust based on:
- Document size
- Number of entities to detect
- Server load

```bash
export PIICLOAK_TIMEOUT=180  # 3 minutes
```

---

## Environment-Specific Configs

### Development

```bash
export PIICLOAK_DEBUG=true
export PIICLOAK_LOG_LEVEL=DEBUG
export PIICLOAK_SPACY_MODEL=en_core_web_md
export PIICLOAK_WORKERS=2
```

### Staging

```bash
export PIICLOAK_DEBUG=false
export PIICLOAK_LOG_LEVEL=INFO
export PIICLOAK_SPACY_MODEL=en_core_web_lg
export PIICLOAK_WORKERS=4
export PIICLOAK_API_KEY=staging-secret-key
export PIICLOAK_CORS_ORIGINS="https://staging.example.com"
```

### Production

```bash
export PIICLOAK_DEBUG=false
export PIICLOAK_LOG_LEVEL=WARNING
export PIICLOAK_SPACY_MODEL=en_core_web_lg
export PIICLOAK_WORKERS=8
export PIICLOAK_API_KEY=production-secret-key
export PIICLOAK_CORS_ORIGINS="https://app.example.com"
export PIICLOAK_RATE_LIMIT="500/minute"
export PIICLOAK_ENABLE_METRICS=true
```

---

## Troubleshooting

### High Memory Usage

1. Reduce workers
2. Use smaller spaCy model
3. Increase server resources

### Slow Response Times

1. Increase workers
2. Lower score_threshold
3. Filter entities to only needed types
4. Enable request caching at load balancer

### False Positives

1. Increase score_threshold (0.6-0.8)
2. Filter specific entity types
3. Custom recognizers for domain-specific patterns

### False Negatives

1. Lower score_threshold (0.3-0.4)
2. Use larger spaCy model
3. Add custom recognizers
