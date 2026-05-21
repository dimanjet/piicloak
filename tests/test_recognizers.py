"""Tests for custom PII recognizers."""

import pytest
from piicloak.recognizers import (
    SUPPORTED_ENTITIES,
    create_ssn_recognizer,
    SpacyUsernameRecognizer,
    create_api_key_recognizer,
    create_salesforce_id_recognizer,
    create_case_number_recognizer,
    create_tax_id_recognizer,
    create_bank_account_recognizer,
    create_contract_number_recognizer,
    create_address_recognizer,
)


class TestSupportedEntities:
    """Test supported entities list."""

    def test_contains_required_entities(self):
        """Ensure all required entity types are supported."""
        required = [
            "PERSON",
            "EMAIL_ADDRESS",
            "PHONE_NUMBER",
            "ORGANIZATION",
            "ADDRESS",
            "USERNAME",
            "US_SSN",
            "API_KEY",
            "SALESFORCE_ID",
            "CASE_NUMBER",
            "TAX_ID",
            "BANK_ACCOUNT",
            "CONTRACT_NUMBER",
        ]
        for entity in required:
            assert entity in SUPPORTED_ENTITIES, f"Missing entity: {entity}"


class TestSSNRecognizer:
    """Test SSN detection."""

    @pytest.fixture
    def recognizer(self):
        return create_ssn_recognizer()

    def test_ssn_with_dashes(self, recognizer):
        """Test SSN format: 123-45-6789"""
        text = "My SSN is 123-45-6789"
        results = recognizer.analyze(text, ["US_SSN"])
        assert len(results) >= 1
        assert any(r.entity_type == "US_SSN" for r in results)

    def test_ssn_with_spaces(self, recognizer):
        """Test SSN format: 123 45 6789"""
        text = "SSN: 123 45 6789"
        results = recognizer.analyze(text, ["US_SSN"])
        assert len(results) >= 1


class TestUsernameRecognizer:
    """Test username detection."""

    @pytest.fixture
    def recognizer(self):
        return SpacyUsernameRecognizer()

    def test_username_labeled(self, recognizer):
        """Test username with label."""
        text = "Username: john_smith123"
        results = recognizer.analyze(text, ["USERNAME"])
        assert len(results) >= 1
        assert any(r.entity_type == "USERNAME" for r in results)

    def test_username_login(self, recognizer):
        """Test login format."""
        text = "Login: jsmith"
        results = recognizer.analyze(text, ["USERNAME"])
        assert len(results) >= 1

    def test_username_handle(self, recognizer):
        """Test @handle format."""
        text = "Follow @johndoe on Twitter"
        results = recognizer.analyze(text, ["USERNAME"])
        assert len(results) >= 1
        assert any("johndoe" in text[r.start : r.end] for r in results)


class TestAPIKeyRecognizer:
    """Test API key detection."""

    @pytest.fixture
    def recognizer(self):
        return create_api_key_recognizer()

    def test_openai_key(self, recognizer):
        """Test OpenAI API key detection."""
        text = "API key: sk-1234567890abcdefghijklmnopqrstuv"
        results = recognizer.analyze(text, ["API_KEY"])
        assert len(results) >= 1
        assert any(r.entity_type == "API_KEY" for r in results)

    def test_github_token(self, recognizer):
        """Test GitHub token detection."""
        text = "Token: ghp_abcdefghijklmnopqrstuvwxyz1234567890"
        results = recognizer.analyze(text, ["API_KEY"])
        assert len(results) >= 1

    def test_git_hosting_tokens(self, recognizer):
        """Test popular source-control token detection."""
        samples = [
            "GitHub Actions token: ghs_abcdefghijklmnopqrstuvwxyz1234567890",
            "GitLab token: glpat-abcdefghijklmnopqrstuvwx",
        ]
        for text in samples:
            results = recognizer.analyze(text, ["API_KEY"])
            assert len(results) >= 1, f"Expected API_KEY in: {text}"

    def test_aws_key(self, recognizer):
        """Test AWS access key detection."""
        text = "AWS Key: AKIAIOSFODNN7EXAMPLE"
        results = recognizer.analyze(text, ["API_KEY"])
        assert len(results) >= 1

    def test_ai_provider_keys(self, recognizer):
        """Test AI provider API key detection."""
        samples = [
            "OpenRouter: sk-or-v1-abcdefghijklmnopqrstuvwxyz123456",
            "Anthropic: sk-ant-api03-abcdefghijklmnopqrstuvwxyz123456",
            "Gemini: AIzaSyBabcdefghijklmnopqrstuvwxyz123456789",
            "Hugging Face: hf_abcdefghijklmnopqrstuvwxyz1234567890",
        ]
        for text in samples:
            results = recognizer.analyze(text, ["API_KEY"])
            assert len(results) >= 1, f"Expected API_KEY in: {text}"

    def test_app_and_infrastructure_tokens(self, recognizer):
        """Test application and infrastructure token detection."""
        samples = [
            "Slack token: " + "xox" + "b-123456789012-123456789012-abcdefghijklmnopqrstuvwx",
            "Discord token: "
            + "MjM4NzY1NDMyMTA5ODc2NTQ"
            + ".XyZabc."
            + "abcdefghijklmnopqrstuvwxyz1",
            "Telegram token: 1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghi",
            "npm token: npm_abcdefghijklmnopqrstuvwxyz1234567890",
            "Vercel token: vercel_abcdefghijklmnopqrstuvwxyz123456",
            "Linear key: lin_api_abcdefghijklmnopqrstuvwxyz123456",
            "ClickUp token: pk_abcdefghijklmnopqrstuvwxyz123456",
            "Cloudflare token=abcdefghijklmnopqrstuvwxyz123456",
            "SendGrid key: SG.abcdefghijklmnopqrstuvwx.abcdefghijklmnopqrstuvwxyz1234567890",
            "Sentry DSN: https://0123456789abcdef0123456789abcdef@o123.ingest.sentry.io/456",
        ]
        for text in samples:
            results = recognizer.analyze(text, ["API_KEY"])
            assert len(results) >= 1, f"Expected API_KEY in: {text}"

    def test_jwt_and_private_key_block(self, recognizer):
        """Test JWT and private key block detection."""
        jwt = (
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
            "eyJzdWIiOiIxMjM0NTY3ODkwIiwicm9sZSI6InNlcnZpY2Vfcm9sZSJ9."
            "SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        )
        private_key = (
            "-----BEGIN PRIVATE KEY-----\n"
            "MIIEvQIBADANBgkqhkiG9w0BAQEFAASC\n"
            "-----END PRIVATE KEY-----"
        )
        for text in [f"JWT: {jwt}", private_key]:
            results = recognizer.analyze(text, ["API_KEY"])
            assert len(results) >= 1, f"Expected API_KEY in: {text}"

    def test_does_not_match_common_agent_memory_ids(self, recognizer):
        """Test common agent-memory identifiers are not treated as API keys."""
        samples = [
            "Commit 1eeb16dd9f0c2a3b4d5e6f708192a3b4c5d6e7f8 fixed the issue.",
            "Session 019df702-35e9-7af3-aef3-d3baf62835b6 should stay searchable.",
            "Content hash sha256:9f86d081884c7d659a2feaa0c55ad015 remains useful.",
            "Stripe publishable key pk_live_abcdefghijklmnopqrstuvwxyz is not a secret.",
        ]
        for text in samples:
            results = recognizer.analyze(text, ["API_KEY"])
            assert results == [], f"Unexpected API_KEY in: {text}"


class TestSalesforceIDRecognizer:
    """Test Salesforce ID detection."""

    @pytest.fixture
    def recognizer(self):
        return create_salesforce_id_recognizer()

    def test_account_id(self, recognizer):
        """Test Salesforce Account ID."""
        text = "Account: 0015000000AbcDEFG"
        results = recognizer.analyze(text, ["SALESFORCE_ID"])
        assert len(results) >= 1

    def test_contact_id(self, recognizer):
        """Test Salesforce Contact ID."""
        text = "Contact: 0035000000XyzABCD"
        results = recognizer.analyze(text, ["SALESFORCE_ID"])
        assert len(results) >= 1

    def test_case_id(self, recognizer):
        """Test Salesforce Case ID."""
        text = "Case: 5005000000TestABC"
        results = recognizer.analyze(text, ["SALESFORCE_ID"])
        assert len(results) >= 1


class TestCaseNumberRecognizer:
    """Test legal case number detection."""

    @pytest.fixture
    def recognizer(self):
        return create_case_number_recognizer()

    def test_federal_case(self, recognizer):
        """Test federal case number format."""
        text = "Case No. 1:24-cv-12345"
        results = recognizer.analyze(text, ["CASE_NUMBER"])
        assert len(results) >= 1

    def test_state_case(self, recognizer):
        """Test state case number format."""
        text = "Docket: CV-2024-001234"
        results = recognizer.analyze(text, ["CASE_NUMBER"])
        assert len(results) >= 1


class TestTaxIDRecognizer:
    """Test tax ID (EIN/TIN) detection."""

    @pytest.fixture
    def recognizer(self):
        return create_tax_id_recognizer()

    def test_ein_format(self, recognizer):
        """Test EIN format: 12-3456789"""
        text = "EIN: 12-3456789"
        results = recognizer.analyze(text, ["TAX_ID"])
        assert len(results) >= 1


class TestBankAccountRecognizer:
    """Test bank account detection."""

    @pytest.fixture
    def recognizer(self):
        return create_bank_account_recognizer()

    def test_routing_number(self, recognizer):
        """Test routing number detection."""
        text = "Routing: 021000021"
        results = recognizer.analyze(text, ["BANK_ACCOUNT"])
        assert len(results) >= 1

    def test_account_number(self, recognizer):
        """Test account number with label."""
        text = "Account: 123456789012"
        results = recognizer.analyze(text, ["BANK_ACCOUNT"])
        assert len(results) >= 1


class TestContractNumberRecognizer:
    """Test contract number detection."""

    @pytest.fixture
    def recognizer(self):
        return create_contract_number_recognizer()

    def test_contract_prefix(self, recognizer):
        """Test contract with CTR prefix."""
        text = "Contract #CTR-2024-001234"
        results = recognizer.analyze(text, ["CONTRACT_NUMBER"])
        assert len(results) >= 1

    def test_policy_number(self, recognizer):
        """Test policy number detection."""
        text = "Policy: POL-2024-567890"
        results = recognizer.analyze(text, ["CONTRACT_NUMBER"])
        assert len(results) >= 1


class TestAddressRecognizer:
    """Test address detection."""

    @pytest.fixture
    def recognizer(self):
        return create_address_recognizer()

    def test_street_address(self, recognizer):
        """Test street address detection."""
        text = "Located at 123 Main Street"
        results = recognizer.analyze(text, ["ADDRESS"])
        assert len(results) >= 1

    def test_full_address(self, recognizer):
        """Test full address with ZIP."""
        text = "Address: 456 Oak Avenue, Springfield, IL 62701"
        results = recognizer.analyze(text, ["ADDRESS"])
        assert len(results) >= 1

    def test_po_box(self, recognizer):
        """Test P.O. Box detection."""
        text = "Mail to P.O. Box 12345"
        results = recognizer.analyze(text, ["ADDRESS"])
        assert len(results) >= 1
