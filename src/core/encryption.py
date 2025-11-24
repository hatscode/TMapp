from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os
import base64

class EncryptionService:
    """
    Provides AES-256-GCM encryption with PBKDF2 key derivation.
    Security Controls: Information Disclosure, Tampering
    """
    
    def __init__(self, password: str, salt: bytes = None):
        self.salt = salt or os.urandom(16)
        self.key = self._derive_key(password, self.salt)
        self.aesgcm = AESGCM(self.key)
        
    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """Derive encryption key using PBKDF2-HMAC-SHA256."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,  # OWASP 2023 recommendation
            backend=default_backend()
        )
        return kdf.derive(password.encode('utf-8'))
    
    def encrypt(self, plaintext: str) -> str:
        """Encrypt plaintext with AES-256-GCM."""
        if not plaintext:
            return ""
        
        nonce = os.urandom(12)
        ciphertext = self.aesgcm.encrypt(nonce, plaintext.encode('utf-8'), None)
        combined = nonce + ciphertext
        return base64.b64encode(combined).decode('utf-8')
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt AES-256-GCM encrypted data."""
        if not encrypted_data:
            return ""
        
        try:
            combined = base64.b64decode(encrypted_data.encode('utf-8'))
            nonce = combined[:12]
            ciphertext = combined[12:]
            plaintext = self.aesgcm.decrypt(nonce, ciphertext, None)
            return plaintext.decode('utf-8')
        except Exception as e:
            raise ValueError("Decryption failed - data may be corrupted or tampered") from e
    
    def get_salt(self) -> str:
        """Return base64-encoded salt for storage."""
        return base64.b64encode(self.salt).decode('utf-8')
    
    def __del__(self):
        """Attempt to zero sensitive data on cleanup."""
        if hasattr(self, 'key'):
            self.key = b'\x00' * len(self.key)