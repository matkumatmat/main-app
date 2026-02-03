from __future__ import annotations
import k_services_crypto # type: ignore
from pydantic import BaseModel
from shared.backend.config.settings import settings
from shared.backend.loggingFactory import LoggerFactory

# Bind context 'system' dan 'security' karena ini modul crypto
logger = LoggerFactory.getSystemLogger("CryptoModule").bind(type="security")


class CryptoOutput(BaseModel):
    ciphertext: str
    salt: str
    nonce: str

class CryptoFactory:
    """
    Wrapper for Rust-based high-performance cryptography module.
    Algorithm: AES-256-GCM + Argon2id Key Derivation.
    Supports Flexible Context Binding (AAD).
    """

    def __init__(self) -> None:
        self.master_key = settings.crypto_master_key
        if len(self.master_key) < 32:
            raise ValueError("CRYPTO_MASTER_KEY must be at least 32 characters")

    def encryptSensitive(self, data: str, context: str) -> CryptoOutput:
        """
        Encrypt data bound to a specific context (AAD).
        
        Args:
            data: The plain string to encrypt.
            context: Any arbitrary string to bind to the encrypted data.
                     (e.g., user_id, transaction_ref, session_id, or custom tag).
                     MUST be exactly the same during decryption.
        
        Returns:
            CryptoOutput containing base64 encoded strings.
        """
        try:
            # Inject context string directly to Rust module
            result = k_services_crypto.encrypt_with_context(
                data, 
                self.master_key, 
                context
            )
            return CryptoOutput(**result)
        except Exception as e:
            logger.info("encryption_success", context_length=len(context))
            logger.error("encryption_failed", error=str(e))
            raise ValueError("Encryption operation failed") from e

    def decryptSensitive(self, encrypted: CryptoOutput, context: str) -> str:
        """
        Decrypt data verifying the specific context (AAD).
        
        Args:
            encrypted: The CryptoOutput object (ciphertext, salt, nonce).
            context: The exact AAD string used during encryption.
            
        Returns:
            The original plaintext string.
            
        Raises:
            ValueError: If decryption fails (wrong key or context mismatch).
        """
        try:
            plaintext = k_services_crypto.decrypt_with_context(
                encrypted.ciphertext,
                encrypted.salt,
                encrypted.nonce,
                self.master_key,
                context
            )
            return plaintext
        except Exception as e:
            logger.info("encryption_success", context_length=len(context))
            logger.error("encryption_failed", error=str(e))
            raise ValueError("Decryption failed: Invalid key or context mismatch") from e

# Singleton
crypto = CryptoFactory()