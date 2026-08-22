import os
import json
import base64
from typing import Any, Dict
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from app.core.config import settings

class KeyProvider:
    """Abstract interface for master key retrieval. MVP uses KMS_KEY_ID from config."""
    def get_master_key(self) -> bytes:
        # Derives a 256-bit (32 byte) key from KMS_KEY_ID
        key_hex = settings.KMS_KEY_ID
        if len(key_hex) < 64:
            key_hex = key_hex.ljust(64, '0')
        return bytes.fromhex(key_hex[:64])

class EncryptionService:
    def __init__(self, key_provider: KeyProvider = None):
        self.key_provider = key_provider or KeyProvider()

    def encrypt_bytes(self, data: bytes) -> bytes:
        """Encrypt raw bytes using AES-256-GCM. Returns nonce + ciphertext."""
        master_key = self.key_provider.get_master_key()
        aesgcm = AESGCM(master_key)
        nonce = os.urandom(12)  # 96-bit nonce
        ciphertext = aesgcm.encrypt(nonce, data, None)
        return nonce + ciphertext

    def decrypt_bytes(self, payload: bytes) -> bytes:
        """Decrypt payload (nonce + ciphertext) using AES-256-GCM."""
        master_key = self.key_provider.get_master_key()
        aesgcm = AESGCM(master_key)
        nonce = payload[:12]
        ciphertext = payload[12:]
        return aesgcm.decrypt(nonce, ciphertext, None)

    def encrypt_field(self, data: Any) -> str:
        """Encrypts serializable JSON data into a base64-encoded encrypted payload string."""
        if data is None:
            return None
        json_bytes = json.dumps(data).encode('utf-8')
        encrypted = self.encrypt_bytes(json_bytes)
        return base64.b64encode(encrypted).decode('utf-8')

    def decrypt_field(self, encrypted_str: str) -> Any:
        """Decrypts a base64-encoded encrypted payload string back into deserialized data."""
        if not encrypted_str:
            return None
        payload = base64.b64decode(encrypted_str.encode('utf-8'))
        decrypted_bytes = self.decrypt_bytes(payload)
        return json.loads(decrypted_bytes.decode('utf-8'))

encryption_service = EncryptionService()
