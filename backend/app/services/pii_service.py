import re
from typing import Tuple, Dict

class PIIService:
    def __init__(self):
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.phone_pattern = re.compile(r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b')

    def redact_pii(self, text: str) -> Tuple[str, Dict[str, str]]:
        """Redacts sensitive PII patterns in text with placeholder tokens."""
        redaction_map = {}
        counter = {"email": 1, "phone": 1}

        def replace_email(match):
            token = f"[EMAIL_{counter['email']}]"
            redaction_map[token] = match.group(0)
            counter["email"] += 1
            return token

        def replace_phone(match):
            token = f"[PHONE_{counter['phone']}]"
            redaction_map[token] = match.group(0)
            counter["phone"] += 1
            return token

        text = self.email_pattern.sub(replace_email, text)
        text = self.phone_pattern.sub(replace_phone, text)

        return text, redaction_map

    def remap_pii(self, data: any, redaction_map: Dict[str, str]) -> any:
        """Recursively replaces tokens in dict/list/string data back with plaintext PII."""
        if not redaction_map:
            return data

        if isinstance(data, str):
            res = data
            for token, real_val in redaction_map.items():
                res = res.replace(token, real_val)
            return res
        elif isinstance(data, dict):
            return {k: self.remap_pii(v, redaction_map) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.remap_pii(item, redaction_map) for item in data]
        return data

pii_service = PIIService()
