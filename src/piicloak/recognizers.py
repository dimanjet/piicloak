"""
Custom PII recognizers for enhanced detection.

Includes recognizers for:
- Organizations (NER-based)
- Addresses (NER + pattern-based)
- Salesforce IDs
- Legal case numbers
- Tax IDs (EIN/TIN)
- Bank accounts
- Contract numbers
- Account/Customer IDs
- API keys
"""

from typing import List, Optional
from presidio_analyzer import Pattern, PatternRecognizer, RecognizerResult, EntityRecognizer


# ============================================================================
# SUPPORTED ENTITIES
# ============================================================================

SUPPORTED_ENTITIES = [
    # Built-in presidio entities
    "PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER", "CREDIT_CARD",
    "IBAN_CODE", "IP_ADDRESS", "URL", "US_SSN", "US_PASSPORT",
    "US_DRIVER_LICENSE", "CRYPTO", "DATE_TIME", "NRP", "LOCATION",
    "MEDICAL_LICENSE", "US_BANK_NUMBER", "UK_NHS",
    # Custom entities
    "ORGANIZATION",
    "ADDRESS",
    "USERNAME",
    "API_KEY",
    "DOMAIN",
    "ACCOUNT_ID",
    "SALESFORCE_ID",
    "CASE_NUMBER",
    "TAX_ID",
    "BANK_ACCOUNT",
    "CONTRACT_NUMBER",
]


# ============================================================================
# NER-BASED RECOGNIZERS
# ============================================================================

class SpacyOrgRecognizer(EntityRecognizer):
    """Recognizer that uses spaCy NER to detect organizations."""
    
    def __init__(self, nlp):
        super().__init__(
            supported_entities=["ORGANIZATION"],
            supported_language="en",
            name="SpacyOrgRecognizer"
        )
        self.nlp = nlp
    
    def load(self) -> None:
        pass
    
    def analyze(
        self, 
        text: str, 
        entities: List[str], 
        nlp_artifacts: Optional[dict] = None
    ) -> List[RecognizerResult]:
        results = []
        if "ORGANIZATION" not in entities:
            return results
            
        doc = self.nlp(text)
        for ent in doc.ents:
            if ent.label_ == "ORG":
                results.append(
                    RecognizerResult(
                        entity_type="ORGANIZATION",
                        start=ent.start_char,
                        end=ent.end_char,
                        score=0.85
                    )
                )
        return results


class SpacyAddressRecognizer(EntityRecognizer):
    """Recognizer that uses spaCy NER to detect addresses/locations."""
    
    def __init__(self, nlp):
        super().__init__(
            supported_entities=["ADDRESS"],
            supported_language="en",
            name="SpacyAddressRecognizer"
        )
        self.nlp = nlp
    
    def load(self) -> None:
        pass
    
    def analyze(
        self, 
        text: str, 
        entities: List[str], 
        nlp_artifacts: Optional[dict] = None
    ) -> List[RecognizerResult]:
        results = []
        if "ADDRESS" not in entities:
            return results
            
        doc = self.nlp(text)
        for ent in doc.ents:
            if ent.label_ in ["GPE", "LOC", "FAC"]:
                results.append(
                    RecognizerResult(
                        entity_type="ADDRESS",
                        start=ent.start_char,
                        end=ent.end_char,
                        score=0.7
                    )
                )
        return results


# ============================================================================
# PATTERN-BASED RECOGNIZERS
# ============================================================================

def create_ssn_recognizer() -> PatternRecognizer:
    """Create SSN recognizer with multiple formats."""
    patterns = [
        Pattern("SSN_DASHES", r"\b\d{3}-\d{2}-\d{4}\b", 0.85),
        Pattern("SSN_SPACES", r"\b\d{3}\s\d{2}\s\d{4}\b", 0.85),
        Pattern("SSN_NODASH", r"\b\d{9}\b", 0.3),
    ]
    return PatternRecognizer(
        supported_entity="US_SSN",
        patterns=patterns,
        context=["ssn", "social", "security", "number", "social security"]
    )


def create_api_key_recognizer() -> PatternRecognizer:
    """Create API key recognizer for common platforms."""
    patterns = [
        # OpenAI keys: sk-proj-XXX or sk-XXX (old format)
        Pattern("OPENAI_KEY_NEW", r"\bsk-proj-[a-zA-Z0-9]{32,}\b", 0.95),
        Pattern("OPENAI_KEY", r"\bsk-[a-zA-Z0-9]{32,}\b", 0.95),
        # AWS keys
        Pattern("AWS_ACCESS_KEY", r"\bAKIA[0-9A-Z]{16}\b", 0.95),
        Pattern("AWS_SECRET_KEY", r"\b[a-zA-Z0-9/+=]{40}\b", 0.7),  # Lower score, can be generic
        # GitHub tokens (flexible length)
        Pattern("GITHUB_TOKEN", r"\bghp_[a-zA-Z0-9]{30,100}\b", 0.95),
        Pattern("GITHUB_TOKEN_OLD", r"\bgho_[a-zA-Z0-9]{30,100}\b", 0.95),
        Pattern("GITHUB_FINE_GRAINED", r"\bgithub_pat_[a-zA-Z0-9_]{70,100}\b", 0.95),
        # Stripe keys
        Pattern("STRIPE_KEY", r"\bsk_live_[a-zA-Z0-9]{24,}\b", 0.95),
        Pattern("STRIPE_TEST", r"\bsk_test_[a-zA-Z0-9]{24,}\b", 0.95),
        # Generic patterns
        Pattern("BEARER_TOKEN", r"(?i)bearer\s+[a-zA-Z0-9_\-\.]{20,}", 0.85),
        Pattern("SECRET_GENERIC", r"(?i)(?:api[_-]?key|secret[_-]?key|access[_-]?token|auth[_-]?token)\s*[=:]\s*['\"]?([a-zA-Z0-9_\-]{20,})['\"]?", 0.85),
    ]
    return PatternRecognizer(
        supported_entity="API_KEY",
        patterns=patterns,
        context=["key", "api", "token", "secret", "password", "credential", "auth", "bearer", "authorization"]
    )


def create_domain_recognizer() -> PatternRecognizer:
    """Create domain name recognizer."""
    patterns = [
        Pattern("DOMAIN", r"\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+(?:com|org|net|io|co|ai|dev|app|edu|gov|mil|info|biz|xyz|online|site|tech|cloud)\b", 0.7),
    ]
    return PatternRecognizer(
        supported_entity="DOMAIN",
        patterns=patterns
    )


def create_address_recognizer() -> PatternRecognizer:
    """Create street address recognizer."""
    patterns = [
        Pattern("STREET_ADDRESS", r"\b\d{1,5}\s+(?:[A-Z][a-z]+\s*){1,3}(?:Street|St\.?|Avenue|Ave\.?|Boulevard|Blvd\.?|Road|Rd\.?|Drive|Dr\.?|Lane|Ln\.?|Way|Court|Ct\.?|Place|Pl\.?|Circle|Cir\.?|Trail|Trl\.?|Parkway|Pkwy\.?)\b", 0.85),
        Pattern("PO_BOX", r"(?i)\bP\.?O\.?\s*Box\s+\d+\b", 0.9),
        Pattern("ZIP_CODE", r"\b\d{5}(?:-\d{4})?\b", 0.6),
        Pattern("FULL_ADDRESS", r"\b\d{1,5}\s+[\w\s]+,\s*[\w\s]+,\s*[A-Z]{2}\s+\d{5}(?:-\d{4})?\b", 0.95),
    ]
    return PatternRecognizer(
        supported_entity="ADDRESS",
        patterns=patterns,
        context=["address", "street", "city", "state", "zip", "located", "location", "office", "headquarters", "residence", "home", "mailing"]
    )


def create_account_id_recognizer() -> PatternRecognizer:
    """Create account/customer ID recognizer."""
    patterns = [
        Pattern("ACCOUNT_PREFIX", r"(?i)\b(?:ACC|ACCT|CUST|CUS|CLIENT|CLT|ID)[_\-#]?\d{4,12}\b", 0.85),
        Pattern("CUSTOMER_ID", r"(?i)\b(?:customer|account|client|member|user)[_\-\s]?(?:id|no|num|number)?[:\s#]*[A-Z0-9]{6,15}\b", 0.8),
        Pattern("FORMATTED_ID", r"\b[A-Z]{2,4}[-_]\d{6,10}\b", 0.7),
    ]
    return PatternRecognizer(
        supported_entity="ACCOUNT_ID",
        patterns=patterns,
        context=["account", "customer", "client", "member", "id", "number", "reference"]
    )


def create_salesforce_id_recognizer() -> PatternRecognizer:
    """Create Salesforce ID recognizer."""
    patterns = [
        Pattern("SF_ID_15", r"\b[a-zA-Z0-9]{15}\b", 0.5),
        Pattern("SF_ID_18", r"\b[a-zA-Z0-9]{18}\b", 0.5),
        Pattern("SF_ACCOUNT", r"\b001[a-zA-Z0-9]{12,15}\b", 0.9),
        Pattern("SF_CONTACT", r"\b003[a-zA-Z0-9]{12,15}\b", 0.9),
        Pattern("SF_LEAD", r"\b00Q[a-zA-Z0-9]{12,15}\b", 0.9),
        Pattern("SF_OPPORTUNITY", r"\b006[a-zA-Z0-9]{12,15}\b", 0.9),
        Pattern("SF_CASE", r"\b500[a-zA-Z0-9]{12,15}\b", 0.9),
        Pattern("SF_USER", r"\b005[a-zA-Z0-9]{12,15}\b", 0.9),
    ]
    return PatternRecognizer(
        supported_entity="SALESFORCE_ID",
        patterns=patterns,
        context=["salesforce", "sf", "sfdc", "record", "id", "object"]
    )


def create_case_number_recognizer() -> PatternRecognizer:
    """Create legal case number recognizer."""
    patterns = [
        Pattern("FEDERAL_CASE", r"\b\d{1,2}:\d{2}-[a-z]{2}-\d{4,6}\b", 0.95),
        Pattern("STATE_CASE", r"(?i)\b(?:CV|CR|CIV|CRIM|FAM|PROB|JUV|BK|AP)[-\s]?\d{2,4}[-\s]?\d{4,8}\b", 0.9),
        Pattern("CASE_GENERIC", r"(?i)\b(?:case|docket|matter|file)[\s#:]*(?:no\.?|number)?[\s#:]*[A-Z0-9\-]{4,15}\b", 0.85),
        Pattern("CASE_YEAR", r"\b(?:19|20)\d{2}[-/]\d{4,8}\b", 0.7),
    ]
    return PatternRecognizer(
        supported_entity="CASE_NUMBER",
        patterns=patterns,
        context=["case", "docket", "matter", "file", "court", "lawsuit", "litigation", "proceeding", "action"]
    )


def create_tax_id_recognizer() -> PatternRecognizer:
    """Create tax ID (EIN/TIN) recognizer."""
    patterns = [
        Pattern("EIN", r"\b\d{2}-\d{7}\b", 0.85),
        Pattern("TIN", r"\b9\d{2}-\d{2}-\d{4}\b", 0.9),
        Pattern("EIN_NODASH", r"\b\d{9}\b", 0.3),
    ]
    return PatternRecognizer(
        supported_entity="TAX_ID",
        patterns=patterns,
        context=["ein", "tin", "itin", "tax", "employer", "identification", "federal", "irs", "w-9", "w9", "1099"]
    )


def create_bank_account_recognizer() -> PatternRecognizer:
    """Create bank account recognizer."""
    patterns = [
        Pattern("ROUTING_NUMBER", r"\b(?:0[1-9]|[1-2][0-9]|3[0-2])\d{7}\b", 0.7),
        Pattern("ACCOUNT_NUMBER", r"(?i)(?:account|acct)[\s#:]*\d{8,17}\b", 0.85),
        Pattern("IBAN", r"\b[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}(?:[A-Z0-9]?){0,16}\b", 0.95),
        Pattern("ACCOUNT_ROUTING", r"\b\d{9}\s*[/\-]\s*\d{8,17}\b", 0.9),
        Pattern("SWIFT_BIC", r"\b[A-Z]{4}[A-Z]{2}[A-Z0-9]{2}(?:[A-Z0-9]{3})?\b", 0.8),
    ]
    return PatternRecognizer(
        supported_entity="BANK_ACCOUNT",
        patterns=patterns,
        context=["bank", "account", "routing", "aba", "swift", "bic", "iban", "wire", "transfer", "deposit", "checking", "savings"]
    )


def create_contract_number_recognizer() -> PatternRecognizer:
    """Create contract/policy number recognizer."""
    patterns = [
        Pattern("CONTRACT_PREFIX", r"(?i)\b(?:CTR|CONTRACT|CNTR|CON|AGR|AGREEMENT)[-_#]?\d{2,4}[-_]?\d{3,8}\b", 0.9),
        Pattern("POLICY_NUMBER", r"(?i)\b(?:POL|POLICY|PLY)[-_#]?\d{2,4}[-_]?\d{3,8}\b", 0.9),
        Pattern("ORDER_NUMBER", r"(?i)\b(?:ORD|ORDER|INV|INVOICE|PO|PURCHASE)[-_#]?\d{4,12}\b", 0.85),
        Pattern("CONTRACT_REF", r"(?i)\b(?:contract|agreement|order|invoice|policy)[\s#:]+[A-Z0-9\-]{6,20}\b", 0.8),
        Pattern("MSA_SOW", r"(?i)\b(?:MSA|SOW|SLA|NDA|MOU)[-_#]?\d{2,4}[-_]?\d{2,6}\b", 0.9),
    ]
    return PatternRecognizer(
        supported_entity="CONTRACT_NUMBER",
        patterns=patterns,
        context=["contract", "agreement", "policy", "order", "invoice", "purchase", "msa", "sow", "sla", "nda"]
    )


class SpacyUsernameRecognizer(EntityRecognizer):
    """
    NER-based username recognizer using spaCy and pattern matching.
    Combines NER for person names that might be usernames with strict patterns.
    """
    
    SUPPORTED_ENTITY = "USERNAME"
    
    def __init__(self, nlp_engine=None, supported_language="en", supported_entity="USERNAME"):
        """Initialize with optional spaCy engine."""
        super().__init__(supported_entities=[supported_entity], supported_language=supported_language)
        self.nlp_engine = nlp_engine
        
        # Strict patterns for explicit username contexts
        self.patterns = [
            # Very explicit username labels - HIGH CONFIDENCE
            (r"(?i)(?:username|user\s*name|user[-_]name)[\s:=]+([a-z0-9_\-\.@]{3,30})\b", 0.95),
            (r"(?i)(?:login|log-in|signin|sign-in)[\s:=]+([a-z0-9_\-\.@]{3,30})\b", 0.95),
            (r"(?i)(?:user[-\s]?id|userid|uid)[\s:=]+([a-z0-9_\-\.@]{3,30})\b", 0.95),
            (r"(?i)(?:account[-\s]?name|account[-\s]?id)[\s:=]+([a-z0-9_\-\.@]{3,30})\b", 0.95),
            # @handle style (social media) - HIGH CONFIDENCE
            (r"(?:^|\s)@([a-z0-9_]{3,20})\b", 0.9),
            # Profile/member contexts - MEDIUM CONFIDENCE (strict: must be at word boundary)
            (r"(?i)\b(?:profile|member)[\s:]+([a-z][a-z0-9_\-\.]{2,19})\b", 0.85),
            # "User is X" pattern with NER context
            (r"(?i)\buser\s+(?:is|was)\s+([a-z][a-z0-9_\-\.]{2,19})\b", 0.85),
            # API/URL paths - MEDIUM CONFIDENCE
            (r"/users?/([a-z0-9_\-\.]{3,30})(?:/|$|\?)", 0.8),
        ]
        
        # Common words that are NOT usernames (prevent false positives)
        # Only truly generic words - actual usernames like "admin" should be detected
        self.exclude_words = {
            'user', 'account', 'login', 'username', 'password', 'email', 'name', 'profile',
            'member', 'client', 'customer', 'example', 'sample', 'default',
            'logged', 'created', 'updated', 'deleted', 'modified', 'accessed',
            'valid', 'invalid', 'active', 'inactive', 'enabled', 'disabled'
        }
        
    def load(self) -> None:
        """Load is not required for this recognizer."""
        pass
    
    def analyze(self, text: str, entities: List[str], nlp_artifacts=None) -> List[RecognizerResult]:
        """Detect usernames using patterns and NER."""
        results = []
        
        if self.SUPPORTED_ENTITY not in entities:
            return results
        
        # Pattern-based detection with strict rules
        for pattern, score in self.patterns:
            import re
            for match in re.finditer(pattern, text):
                # Get the captured username (group 1) or full match
                username = match.group(1) if match.groups() else match.group(0).strip('@')
                username_clean = username.lower().strip()
                
                # Skip if it's in exclusion list
                if username_clean in self.exclude_words:
                    continue
                
                # Skip if it's too short or looks like a word
                if len(username_clean) < 3:
                    continue
                
                # Calculate position (use group 1 if available, else full match)
                if match.groups():
                    start = match.start(1)
                    end = match.end(1)
                else:
                    start = match.start()
                    end = match.end()
                    if text[start] == '@':
                        start += 1
                
                results.append(
                    RecognizerResult(
                        entity_type=self.SUPPORTED_ENTITY,
                        start=start,
                        end=end,
                        score=score
                    )
                )
        
        # NER-based detection: Look for PERSON entities near username keywords
        if nlp_artifacts and hasattr(nlp_artifacts, 'entities'):
            username_contexts = ['username', 'user', 'login', 'account', 'profile', 'member']
            text_lower = text.lower()
            
            for ent in nlp_artifacts.entities:
                if ent.label_ == 'PERSON':
                    # Check if there's a username context nearby (within 20 chars)
                    context_start = max(0, ent.start_char - 20)
                    context_text = text_lower[context_start:ent.start_char]
                    
                    if any(keyword in context_text for keyword in username_contexts):
                        # This person name is likely a username
                        results.append(
                            RecognizerResult(
                                entity_type=self.SUPPORTED_ENTITY,
                                start=ent.start_char,
                                end=ent.end_char,
                                score=0.85
                            )
                        )
        
        return results


def create_username_recognizer(nlp_engine=None) -> SpacyUsernameRecognizer:
    """Create NER-enhanced username recognizer."""
    return SpacyUsernameRecognizer(nlp_engine=nlp_engine)


def get_all_pattern_recognizers() -> List[PatternRecognizer]:
    """Get all pattern-based recognizers."""
    return [
        create_ssn_recognizer(),
        create_api_key_recognizer(),
        create_domain_recognizer(),
        create_address_recognizer(),
        create_account_id_recognizer(),
        create_salesforce_id_recognizer(),
        create_case_number_recognizer(),
        create_tax_id_recognizer(),
        create_bank_account_recognizer(),
        create_contract_number_recognizer(),
    ]
