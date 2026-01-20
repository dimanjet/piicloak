.PHONY: help install install-dev test lint format run docker-build docker-run security-scan clean

help:
	@echo "PIICloak - Available commands:"
	@echo ""
	@echo "  make install       Install dependencies"
	@echo "  make install-dev   Install with dev dependencies"
	@echo "  make test          Run tests"
	@echo "  make lint          Run linters"
	@echo "  make format        Format code with black"
	@echo "  make security-scan Run security scans"
	@echo "  make run           Run the service"
	@echo "  make docker-build  Build Docker image"
	@echo "  make docker-run    Run Docker container"
	@echo "  make clean         Clean build artifacts"

install:
	pip install -r requirements.txt
	python -m spacy download en_core_web_lg

install-dev:
	pip install -e ".[dev]"
	python -m spacy download en_core_web_lg

test:
	pytest -v --cov=src/piicloak --cov-report=term-missing tests/

lint:
	flake8 src/ tests/
	mypy src/

format:
	black src/ tests/

security-scan:
	@echo "🔒 Running security scans..."
	@echo ""
	@echo "=== Checking for secrets ==="
	@grep -r -i -E "(password|api[_-]?key|secret|token).*=.*['\"][^'\"]{8,}['\"]" --include="*.py" src/ tests/ 2>/dev/null | grep -v "test" | grep -v "Pattern" | head -10 || echo "✅ No hardcoded secrets found"
	@echo ""
	@echo "=== Scanning dependencies with Safety ==="
	@pip install --quiet safety 2>/dev/null || true
	@safety check -r requirements.txt --json 2>/dev/null | python3 -c "import sys, json; data=json.load(sys.stdin); print(f\"✅ {len(data.get('report',{}).get('vulnerabilities',[]))} vulnerabilities reported\")" || safety check -r requirements.txt 2>&1 | tail -5
	@echo ""
	@echo "=== Running Bandit code security scan ==="
	@pip install --quiet bandit 2>/dev/null || true
	@bandit -r src/ -f screen 2>&1 | tail -20
	@echo ""
	@echo "✅ Security scan complete. See SECURITY_SCAN_REPORT.md for details."

run:
	python -m piicloak

run-gunicorn:
	gunicorn -c gunicorn.conf.py "piicloak.app:create_application()"

docker-build:
	docker build -t piicloak:latest .

docker-run:
	docker run -p 8000:8000 piicloak:latest

docker-compose-up:
	docker-compose up -d

docker-compose-down:
	docker-compose down

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
