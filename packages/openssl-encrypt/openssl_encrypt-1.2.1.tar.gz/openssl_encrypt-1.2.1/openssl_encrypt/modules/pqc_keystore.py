#!/usr/bin/env python3
"""
Post-Quantum Cryptography Keystore Module

Provides functionality for secure storage and management of PQC keys with
hybrid password approach (master password for keystore, optional per-key passwords).
"""

import base64
import datetime
import hashlib
import json
import os
import secrets
import time
import uuid
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

from .crypt_errors import AuthenticationError, InternalError, KeyDerivationError, ValidationError
from .secure_memory import SecureBytes, secure_memzero

# Check for Argon2 support
try:
    import argon2
    from argon2 import PasswordHasher
    from argon2.exceptions import VerifyMismatchError

    ARGON2_AVAILABLE = True
except ImportError:
    ARGON2_AVAILABLE = False


class KeystoreSecurityLevel(Enum):
    """Security levels for keystore protection"""

    STANDARD = "standard"
    HIGH = "high"
    PARANOID = "paranoid"


class KeystoreProtectionMethod(Enum):
    """Methods used to protect keys in the keystore"""

    ARGON2ID_AES_GCM = "argon2id+aes-256-gcm"
    SCRYPT_CHACHA20 = "scrypt+chacha20-poly1305"
    PBKDF2_AES_GCM = "pbkdf2+aes-256-gcm"  # Fallback if Argon2 not available


class KeyUseFlags(Enum):
    """Usage flags for keys"""

    ENCRYPTION = "encryption"
    DECRYPTION = "decryption"
    SIGNING = "signing"
    VERIFICATION = "verification"


class PQCKeystore:
    """Handles operations on the PQC keystore file with hybrid password approach"""

    # Current keystore version
    KEYSTORE_VERSION = "1.0"

    # Default metadata cache timeout (in seconds)
    DEFAULT_CACHE_TIMEOUT = 600  # 10 minutes

    def __init__(self, keystore_path: str = None, cache_timeout: int = DEFAULT_CACHE_TIMEOUT):
        """
        Initialize the keystore

        Args:
            keystore_path: Path to the keystore file
            cache_timeout: How long to keep keys in memory after unlocking (in seconds)
        """
        self.keystore_path = keystore_path
        self.keystore_data = None
        self.unlocked_keys = {}  # Cache for unlocked keys
        self.master_key = None  # Cached master key material
        self.master_key_time = 0  # When was the master key last used
        self.cache_timeout = cache_timeout

    def create_keystore(
        self,
        master_password: str,
        security_level: KeystoreSecurityLevel = KeystoreSecurityLevel.STANDARD,
    ) -> bool:
        """
        Create a new keystore file

        Args:
            master_password: Master password for the keystore
            security_level: Security level for key protection

        Returns:
            bool: True if the keystore was created successfully

        Raises:
            ValidationError: If the keystore already exists
            InternalError: If the keystore cannot be created
        """
        if self.keystore_path is None:
            raise ValidationError("No keystore path specified")

        if os.path.exists(self.keystore_path):
            raise ValidationError(f"Keystore already exists at {self.keystore_path}")

        # Initialize empty keystore
        self.keystore_data = {
            "keystore_version": self.KEYSTORE_VERSION,
            "creation_date": datetime.datetime.now().isoformat(),
            "last_modified": datetime.datetime.now().isoformat(),
            "keys": [],
            "default_key_id": None,
            "protection": self._get_protection_params(security_level),
        }

        # Create directory if it doesn't exist
        try:
            # Handle the case where the keystore is in the current directory
            dir_path = os.path.dirname(self.keystore_path)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)
        except Exception as e:
            raise InternalError(f"Failed to create directory: {str(e)}")

        try:
            # Encrypt and save the keystore
            return self.save_keystore(master_password)
        except Exception as e:
            import traceback

            traceback.print_exc()
            raise InternalError(f"Failed to create keystore: {str(e)}")

    def load_keystore(self, master_password: str) -> bool:
        """
        Load the keystore from file

        Args:
            master_password: Master password for the keystore

        Returns:
            bool: True if the keystore was loaded successfully

        Raises:
            ValidationError: If the keystore file doesn't exist
            AuthenticationError: If the master password is incorrect
            InternalError: If the keystore cannot be loaded
        """
        if self.keystore_path is None:
            raise ValidationError("No keystore path specified")

        if not os.path.exists(self.keystore_path):
            raise ValidationError(f"Keystore not found at {self.keystore_path}")

        try:
            with open(self.keystore_path, "rb") as f:
                encrypted_data = f.read()

            # Parse the encrypted data
            header_size = int.from_bytes(encrypted_data[:4], byteorder="big")
            header = json.loads(encrypted_data[4 : 4 + header_size].decode("utf-8"))
            ciphertext = encrypted_data[4 + header_size :]

            # Extract parameters
            protection = header["protection"]
            method = protection["method"]
            params = protection["params"]

            # Derive key from master password
            if method == KeystoreProtectionMethod.ARGON2ID_AES_GCM.value:
                if not ARGON2_AVAILABLE:
                    raise ValidationError("Argon2 is required for this keystore but not available")

                # Derive key with Argon2
                argon2_params = params["argon2_params"]
                ph = PasswordHasher(
                    time_cost=argon2_params["time_cost"],
                    memory_cost=argon2_params["memory_cost"],
                    parallelism=argon2_params["parallelism"],
                    hash_len=32,
                )

                # Encode salt as required by argon2-cffi
                salt_b64 = params["salt"]
                salt = base64.b64decode(salt_b64)

                # Hash the password with Argon2id
                hash_result = ph.hash(master_password + salt_b64)
                derived_key = hashlib.sha256(hash_result.encode("utf-8")).digest()

            elif method == KeystoreProtectionMethod.SCRYPT_CHACHA20.value:
                # Derive key with Scrypt
                salt = base64.b64decode(params["salt"])
                scrypt_params = params["scrypt_params"]

                kdf = Scrypt(
                    salt=salt,
                    length=32,
                    n=scrypt_params["n"],
                    r=scrypt_params["r"],
                    p=scrypt_params["p"],
                )
                derived_key = kdf.derive(master_password.encode("utf-8"))

            elif method == KeystoreProtectionMethod.PBKDF2_AES_GCM.value:
                # Derive key with PBKDF2
                salt = base64.b64decode(params["salt"])
                pbkdf2_params = params["pbkdf2_params"]

                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=salt,
                    iterations=pbkdf2_params["iterations"],
                )
                derived_key = kdf.derive(master_password.encode("utf-8"))

            else:
                raise ValidationError(f"Unsupported protection method: {method}")

            # Decrypt the keystore data
            if method == KeystoreProtectionMethod.SCRYPT_CHACHA20.value:
                # Use ChaCha20Poly1305
                cipher = ChaCha20Poly1305(derived_key)
                nonce = base64.b64decode(params["nonce"])

                # Try multiple approaches for robustness - order matters for backward compatibility
                try:
                    # First try with header as associated_data (recommended approach)
                    plaintext = cipher.decrypt(
                        nonce, ciphertext, associated_data=json.dumps(header).encode("utf-8")
                    )
                except Exception as e1:
                    try:
                        # Then try without associated_data (older versions)
                        plaintext = cipher.decrypt(nonce, ciphertext, associated_data=None)
                    except Exception as e2:
                        try:
                            # Finally try with empty string
                            plaintext = cipher.decrypt(nonce, ciphertext, associated_data=b"")
                        except Exception as e3:
                            # Raise the original error
                            raise e1
            else:
                # Use AES-GCM
                cipher = AESGCM(derived_key)
                nonce = base64.b64decode(params["nonce"])

                # For AES-GCM, associated_data must match exactly between encryption and decryption
                # Try multiple approaches for backward compatibility - order matters
                try:
                    # First try with header JSON as associated_data (matches our save_keystore)
                    header_json = json.dumps(header).encode("utf-8")
                    plaintext = cipher.decrypt(nonce, ciphertext, associated_data=header_json)
                except Exception as e1:
                    try:
                        # Then try with None as associated_data (for older keystores)
                        plaintext = cipher.decrypt(nonce, ciphertext, associated_data=None)
                    except Exception as e2:
                        try:
                            # Finally try with empty bytes (another possible approach)
                            plaintext = cipher.decrypt(nonce, ciphertext, associated_data=b"")
                        except Exception as e3:
                            # Log more details about the error for debugging
                            import traceback

                            traceback.print_exc()
                            # Raise the original error
                            raise e1

            # Parse the decrypted data
            self.keystore_data = json.loads(plaintext.decode("utf-8"))

            # Store the derived key for later use (cached)
            self.master_key = bytes(derived_key)
            self.master_key_time = time.time()

            return True

        except Exception as e:
            # Clear any cached keys
            self._clear_cached_keys()

            if isinstance(e, (KeyError, json.JSONDecodeError)):
                raise InternalError(f"Invalid keystore format: {str(e)}")
            elif "MAC check failed" in str(e) or "Cipher tag does not match" in str(e):
                raise AuthenticationError("Invalid master password or corrupted keystore")
            else:
                raise InternalError(f"Failed to load keystore: {str(e)}")

    def save_keystore(self, master_password: str = None) -> bool:
        """
        Save the keystore to file

        Args:
            master_password: Master password for the keystore, if None uses cached master key

        Returns:
            bool: True if the keystore was saved successfully

        Raises:
            ValidationError: If no keystore data exists
            InternalError: If the keystore cannot be saved
        """
        if self.keystore_data is None:
            raise ValidationError("No keystore data to save")

        try:
            # Prepare the data
            self.keystore_data["last_modified"] = datetime.datetime.now().isoformat()
            plaintext = json.dumps(self.keystore_data).encode("utf-8")

            # Get encryption parameters
            protection = self.keystore_data["protection"]
            method = protection["method"]
            params = protection["params"]

            # Check if we can use the cached master key
            derived_key = None
            if master_password is None:
                if (
                    self.master_key is not None
                    and time.time() - self.master_key_time < self.cache_timeout
                ):
                    derived_key = self.master_key
                else:
                    raise ValidationError("Master password required (cached key expired)")

            # If we don't have a cached key, derive it from the password
            if derived_key is None:
                if method == KeystoreProtectionMethod.ARGON2ID_AES_GCM.value:
                    if not ARGON2_AVAILABLE:
                        raise ValidationError(
                            "Argon2 is required for this keystore but not available"
                        )

                    # Derive key with Argon2
                    argon2_params = params["argon2_params"]
                    ph = PasswordHasher(
                        time_cost=argon2_params["time_cost"],
                        memory_cost=argon2_params["memory_cost"],
                        parallelism=argon2_params["parallelism"],
                        hash_len=32,
                    )

                    # Encode salt as required by argon2-cffi
                    salt_b64 = params["salt"]
                    salt = base64.b64decode(salt_b64)

                    # Hash the password with Argon2id
                    hash_result = ph.hash(master_password + salt_b64)
                    derived_key = hashlib.sha256(hash_result.encode("utf-8")).digest()

                elif method == KeystoreProtectionMethod.SCRYPT_CHACHA20.value:
                    # Derive key with Scrypt
                    salt = base64.b64decode(params["salt"])
                    scrypt_params = params["scrypt_params"]

                    kdf = Scrypt(
                        salt=salt,
                        length=32,
                        n=scrypt_params["n"],
                        r=scrypt_params["r"],
                        p=scrypt_params["p"],
                    )
                    derived_key = kdf.derive(master_password.encode("utf-8"))

                elif method == KeystoreProtectionMethod.PBKDF2_AES_GCM.value:
                    # Derive key with PBKDF2
                    salt = base64.b64decode(params["salt"])
                    pbkdf2_params = params["pbkdf2_params"]

                    kdf = PBKDF2HMAC(
                        algorithm=hashes.SHA256(),
                        length=32,
                        salt=salt,
                        iterations=pbkdf2_params["iterations"],
                    )
                    derived_key = kdf.derive(master_password.encode("utf-8"))

                else:
                    raise ValidationError(f"Unsupported protection method: {method}")

                # Cache the key for future operations
                # Note: Clone the derived key securely
                self.master_key = bytes(derived_key)
                self.master_key_time = time.time()

            # Encrypt the keystore data
            if method == KeystoreProtectionMethod.SCRYPT_CHACHA20.value:
                # Use ChaCha20Poly1305
                cipher = ChaCha20Poly1305(derived_key)
                nonce = base64.b64decode(params["nonce"])
                # Update nonce for each save
                nonce = secrets.token_bytes(12)
                params["nonce"] = base64.b64encode(nonce).decode("utf-8")

                header = {"protection": protection}
                # Use header as associated_data for consistent encryption
                ciphertext = cipher.encrypt(
                    nonce, plaintext, associated_data=json.dumps(header).encode("utf-8")
                )
            else:
                # Use AES-GCM
                cipher = AESGCM(derived_key)
                nonce = base64.b64decode(params["nonce"])
                # Update nonce for each save
                nonce = secrets.token_bytes(12)
                params["nonce"] = base64.b64encode(nonce).decode("utf-8")

                header = {"protection": protection}
                # IMPORTANT: Use header JSON as associated_data for consistency with load_keystore
                header_json = json.dumps(header).encode("utf-8")
                ciphertext = cipher.encrypt(nonce, plaintext, associated_data=header_json)

            # Prepare the final file format
            header_json = json.dumps(header).encode("utf-8")
            header_size = len(header_json)

            with open(self.keystore_path, "wb") as f:
                f.write(header_size.to_bytes(4, byteorder="big"))
                f.write(header_json)
                f.write(ciphertext)

            return True

        except Exception as e:
            raise InternalError(f"Failed to save keystore: {str(e)}")

    def add_key(
        self,
        algorithm: str,
        public_key: bytes,
        private_key: bytes,
        key_password: str = None,
        use_master_password: bool = True,
        description: str = None,
        tags: List[str] = None,
        purposes: List[str] = None,
    ) -> str:
        """
        Add a new key to the keystore

        Args:
            algorithm: PQC algorithm for this key
            public_key: Public key bytes
            private_key: Private key bytes
            key_password: Specific password for this key (only used if use_master_password=False)
            use_master_password: Whether to use the keystore's master password for this key
            description: User-friendly description for this key
            tags: List of tags for this key
            purposes: List of key usage purposes (encryption, decryption, etc.)

        Returns:
            str: The ID of the newly added key

        Raises:
            ValidationError: If required parameters are missing
            InternalError: If the key cannot be added
        """
        if self.keystore_data is None:
            raise ValidationError("Keystore not loaded")

        if public_key is None or private_key is None:
            raise ValidationError("Public and private keys are required")

        # Generate a unique key ID
        key_id = self._generate_key_id()

        # Set default purposes if not provided
        if purposes is None:
            purposes = [KeyUseFlags.ENCRYPTION.value, KeyUseFlags.DECRYPTION.value]

        # Prepare key metadata
        key_entry = {
            "key_id": key_id,
            "algorithm": algorithm,
            "creation_date": datetime.datetime.now().isoformat(),
            "last_used": datetime.datetime.now().isoformat(),
            "purpose": purposes,
            "metadata": {"description": description or f"{algorithm} key", "tags": tags or []},
            "public_key": base64.b64encode(public_key).decode("utf-8"),
            "use_master_password": use_master_password,
        }

        # Encrypt the private key
        if use_master_password:
            # Use the master key to protect this key
            if self.master_key is None:
                raise ValidationError("Master key not available. Load the keystore first.")

            # Get protection parameters from the keystore
            protection_params = self.keystore_data["protection"]

            # Encrypt using the master key
            encrypted_data = self._encrypt_with_derived_key(
                private_key, self.master_key, KeystoreProtectionMethod(protection_params["method"])
            )

        else:
            # Use a key-specific password
            if key_password is None:
                raise ValidationError("Key password is required when not using master password")

            # Get recommended protection level for individual keys
            # (might be different from the keystore's own protection)
            protection_method = self._get_recommended_protection_method()

            # Encrypt with the key-specific password
            encrypted_data = self._encrypt_private_key(private_key, key_password, protection_method)

        # Store the encrypted private key
        key_entry["private_key"] = encrypted_data

        # Add to the keystore
        self.keystore_data["keys"].append(key_entry)

        # If this is the first key, set it as default
        if self.keystore_data["default_key_id"] is None:
            self.keystore_data["default_key_id"] = key_id

        return key_id

    def get_key(self, key_id: str = None, key_password: str = None) -> Tuple[bytes, bytes]:
        """
        Retrieve a key pair from the keystore

        Args:
            key_id: ID of the key to retrieve (if None, uses default key)
            key_password: Password for key-specific encryption (if applicable)

        Returns:
            Tuple[bytes, bytes]: (public_key, private_key)

        Raises:
            ValidationError: If the key is not found
            AuthenticationError: If the password is incorrect
            InternalError: If the key cannot be retrieved
        """
        if self.keystore_data is None:
            raise ValidationError("Keystore not loaded")

        # If key_id is not specified, use the default key
        if key_id is None:
            key_id = self.keystore_data["default_key_id"]
            if key_id is None:
                raise ValidationError("No default key set in keystore")

        # Check if the key is already in the cache
        if key_id in self.unlocked_keys:
            cached_key, cache_time = self.unlocked_keys[key_id]
            # Check if the cache is still valid
            if time.time() - cache_time < self.cache_timeout:
                return cached_key

        # Find the key in the keystore
        key_entry = None
        for key in self.keystore_data["keys"]:
            if key["key_id"] == key_id:
                key_entry = key
                break

        if key_entry is None:
            raise ValidationError(f"Key not found: {key_id}")

        # Decode the public key
        public_key = base64.b64decode(key_entry["public_key"])

        # Get the encrypted private key
        encrypted_private_key = key_entry["private_key"]

        # Determine how to decrypt the private key
        if key_entry.get("use_master_password", False):
            # Key is protected with the master password
            if self.master_key is None:
                raise ValidationError("Master key not available. Load the keystore first.")

            # Decrypt using the master key
            private_key = self._decrypt_with_derived_key(encrypted_private_key, self.master_key)

        else:
            # Key has its own password
            if key_password is None:
                raise ValidationError("Password required for this key")

            # Decrypt with the key-specific password
            private_key = self._decrypt_private_key(encrypted_private_key, key_password)

        # Update last used timestamp
        key_entry["last_used"] = datetime.datetime.now().isoformat()

        # Cache the keys for future use
        self.unlocked_keys[key_id] = ((public_key, bytes(private_key)), time.time())

        return (public_key, private_key)

    def remove_key(self, key_id: str) -> bool:
        """
        Remove a key from the keystore

        Args:
            key_id: ID of the key to remove

        Returns:
            bool: True if the key was removed

        Raises:
            ValidationError: If the key is not found
        """
        if self.keystore_data is None:
            raise ValidationError("Keystore not loaded")

        # Find the key index
        key_index = None
        for i, key in enumerate(self.keystore_data["keys"]):
            if key["key_id"] == key_id:
                key_index = i
                break

        if key_index is None:
            raise ValidationError(f"Key not found: {key_id}")

        # Remove from cache if present
        if key_id in self.unlocked_keys:
            del self.unlocked_keys[key_id]

        # Remove the key
        self.keystore_data["keys"].pop(key_index)

        # If this was the default key, update the default key
        if self.keystore_data["default_key_id"] == key_id:
            if self.keystore_data["keys"]:
                # Set the first available key as default
                self.keystore_data["default_key_id"] = self.keystore_data["keys"][0]["key_id"]
            else:
                # No keys left
                self.keystore_data["default_key_id"] = None

        return True

    def list_keys(self) -> List[Dict]:
        """
        List all keys in the keystore with their metadata

        Returns:
            List[Dict]: List of key metadata (without sensitive information)

        Raises:
            ValidationError: If the keystore is not loaded
        """
        if self.keystore_data is None:
            raise ValidationError("Keystore not loaded")

        # Create a clean list without sensitive information
        result = []
        for key in self.keystore_data["keys"]:
            # Copy the key data without private_key field
            key_info = {
                "key_id": key["key_id"],
                "algorithm": key["algorithm"],
                "creation_date": key["creation_date"],
                "last_used": key["last_used"],
                "purpose": key["purpose"],
                "metadata": key["metadata"],
                "is_default": key["key_id"] == self.keystore_data["default_key_id"],
                "protection": "master_password"
                if key.get("use_master_password", False)
                else "key_password",
            }
            result.append(key_info)

        return result

    def set_default_key(self, key_id: str) -> bool:
        """
        Set the default key for operations

        Args:
            key_id: ID of the key to set as default

        Returns:
            bool: True if the default key was set

        Raises:
            ValidationError: If the key is not found
        """
        if self.keystore_data is None:
            raise ValidationError("Keystore not loaded")

        # Check if the key exists
        key_exists = False
        for key in self.keystore_data["keys"]:
            if key["key_id"] == key_id:
                key_exists = True
                break

        if not key_exists:
            raise ValidationError(f"Key not found: {key_id}")

        # Set as default
        self.keystore_data["default_key_id"] = key_id
        return True

    def rotate_key(
        self,
        key_id: str,
        new_algorithm: str = None,
        new_key_password: str = None,
        new_use_master: bool = None,
    ) -> str:
        """
        Create a new version of an existing key

        Args:
            key_id: ID of the key to rotate
            new_algorithm: New algorithm to use (if None, uses the same as the old key)
            new_key_password: New password for the key (if None, uses the same approach as before)
            new_use_master: Whether to use the master password for the new key

        Returns:
            str: ID of the new key

        Raises:
            ValidationError: If the key is not found
            NotImplementedError: If key generation is not supported for the algorithm
        """
        # This is a placeholder - the actual implementation would depend on
        # algorithm-specific key generation logic, which would be implemented
        # by calling appropriate functions to generate new key pairs
        raise NotImplementedError("Key rotation not implemented yet")

    def import_legacy_key(
        self, keyfile_path: str, key_password: str = None, use_master_password: bool = True
    ) -> str:
        """
        Import a key from a legacy format keyfile

        Args:
            keyfile_path: Path to the legacy keyfile
            key_password: Password for the legacy key (if needed)
            use_master_password: Whether to use the master password for the imported key

        Returns:
            str: ID of the imported key

        Raises:
            ValidationError: If the keyfile cannot be read or is invalid
            NotImplementedError: If the legacy format is not supported
        """
        # This is a placeholder - the actual implementation would depend on
        # the legacy key format
        raise NotImplementedError("Legacy key import not implemented yet")

    def export_key(
        self, key_id: str, output_path: str, key_password: str = None, export_format: str = "modern"
    ) -> bool:
        """
        Export a key to a file

        Args:
            key_id: ID of the key to export
            output_path: Path where to save the exported key
            key_password: Password for the key (if needed)
            export_format: Format to use for the exported key

        Returns:
            bool: True if the key was exported successfully

        Raises:
            ValidationError: If the key is not found
            NotImplementedError: If the export format is not supported
        """
        # This is a placeholder - the actual implementation would depend on
        # the export format
        raise NotImplementedError("Key export not implemented yet")

    def change_key_password(self, key_id: str, old_password: str, new_password: str) -> bool:
        """
        Change the password for a key that has its own password

        Args:
            key_id: ID of the key to modify
            old_password: Current password for the key
            new_password: New password for the key

        Returns:
            bool: True if the password was changed successfully

        Raises:
            ValidationError: If the key is not found or uses master password
            AuthenticationError: If the old password is incorrect
        """
        if self.keystore_data is None:
            raise ValidationError("Keystore not loaded")

        # Find the key
        key_entry = None
        for key in self.keystore_data["keys"]:
            if key["key_id"] == key_id:
                key_entry = key
                break

        if key_entry is None:
            raise ValidationError(f"Key not found: {key_id}")

        # Check if the key uses its own password
        if key_entry.get("use_master_password", False):
            raise ValidationError(
                "This key uses the master password and does not have its own password"
            )

        # Get the current encrypted private key
        encrypted_private_key = key_entry["private_key"]

        # Decrypt with the old password
        private_key = self._decrypt_private_key(encrypted_private_key, old_password)

        # Re-encrypt with the new password
        protection_method = self._get_recommended_protection_method()
        new_encrypted_data = self._encrypt_private_key(private_key, new_password, protection_method)

        # Update the key entry
        key_entry["private_key"] = new_encrypted_data

        # Remove from cache if present
        if key_id in self.unlocked_keys:
            del self.unlocked_keys[key_id]

        return True

    def change_master_password(self, old_password: str, new_password: str) -> bool:
        """
        Change the master password for the keystore

        Args:
            old_password: Current master password
            new_password: New master password

        Returns:
            bool: True if the password was changed successfully

        Raises:
            ValidationError: If the keystore is not loaded
            AuthenticationError: If the old password is incorrect
        """
        if self.keystore_data is None:
            raise ValidationError("Keystore not loaded")

        # First, verify the old password by loading the keystore
        # This will raise AuthenticationError if the password is wrong
        self.load_keystore(old_password)

        # Get the protection method
        protection = self.keystore_data["protection"]
        method = protection["method"]

        # Generate new salt and nonce
        salt = secrets.token_bytes(16)
        nonce = secrets.token_bytes(12)

        # Update the protection parameters
        protection["params"]["salt"] = base64.b64encode(salt).decode("utf-8")
        protection["params"]["nonce"] = base64.b64encode(nonce).decode("utf-8")

        # Re-encrypt all keys that use the master password
        for key in self.keystore_data["keys"]:
            if key.get("use_master_password", False):
                # Get the key pair
                public_key = base64.b64decode(key["public_key"])
                encrypted_private_key = key["private_key"]

                # Decrypt with the old master key
                private_key = self._decrypt_with_derived_key(encrypted_private_key, self.master_key)

                # We'll re-encrypt after we have the new master key
                key["_temp_private_key"] = private_key

        # Save the keystore with the new password
        # This will derive a new master key and update internal caches
        result = self.save_keystore(new_password)

        # Now re-encrypt all keys with the new master key
        for key in self.keystore_data["keys"]:
            if key.get("use_master_password", False) and "_temp_private_key" in key:
                # Re-encrypt with the new master key
                encrypted_data = self._encrypt_with_derived_key(
                    key["_temp_private_key"],
                    self.master_key,
                    KeystoreProtectionMethod(protection["method"]),
                )

                # Update the key entry and remove temp data
                key["private_key"] = encrypted_data
                del key["_temp_private_key"]

        # Save again to persist the re-encrypted keys
        self.save_keystore()

        # Clear all cached keys
        self._clear_cached_keys()

        return result

    def convert_key_to_master_password(self, key_id: str, key_password: str) -> bool:
        """
        Convert a key with its own password to use the master password

        Args:
            key_id: ID of the key to convert
            key_password: Current password for the key

        Returns:
            bool: True if the key was converted successfully

        Raises:
            ValidationError: If the key is not found or already uses master password
            AuthenticationError: If the key password is incorrect
        """
        if self.keystore_data is None:
            raise ValidationError("Keystore not loaded")

        # Check if master key is available
        if self.master_key is None:
            raise ValidationError("Master key not available. Load the keystore first.")

        # Find the key
        key_entry = None
        for key in self.keystore_data["keys"]:
            if key["key_id"] == key_id:
                key_entry = key
                break

        if key_entry is None:
            raise ValidationError(f"Key not found: {key_id}")

        # Check if the key already uses master password
        if key_entry.get("use_master_password", False):
            raise ValidationError("This key already uses the master password")

        # Get the encrypted private key
        encrypted_private_key = key_entry["private_key"]

        # Decrypt with the key password
        private_key = self._decrypt_private_key(encrypted_private_key, key_password)

        # Get protection parameters from the keystore
        protection_params = self.keystore_data["protection"]

        # Re-encrypt with the master key
        new_encrypted_data = self._encrypt_with_derived_key(
            private_key, self.master_key, KeystoreProtectionMethod(protection_params["method"])
        )

        # Update the key entry
        key_entry["private_key"] = new_encrypted_data
        key_entry["use_master_password"] = True

        # Remove from cache if present
        if key_id in self.unlocked_keys:
            del self.unlocked_keys[key_id]

        return True

    def convert_key_to_separate_password(self, key_id: str, new_password: str) -> bool:
        """
        Convert a key using master password to have its own password

        Args:
            key_id: ID of the key to convert
            new_password: New password for the key

        Returns:
            bool: True if the key was converted successfully

        Raises:
            ValidationError: If the key is not found or doesn't use master password
        """
        if self.keystore_data is None:
            raise ValidationError("Keystore not loaded")

        # Check if master key is available
        if self.master_key is None:
            raise ValidationError("Master key not available. Load the keystore first.")

        # Find the key
        key_entry = None
        for key in self.keystore_data["keys"]:
            if key["key_id"] == key_id:
                key_entry = key
                break

        if key_entry is None:
            raise ValidationError(f"Key not found: {key_id}")

        # Check if the key uses master password
        if not key_entry.get("use_master_password", False):
            raise ValidationError("This key already has a separate password")

        # Get the encrypted private key
        encrypted_private_key = key_entry["private_key"]

        # Decrypt with the master key
        private_key = self._decrypt_with_derived_key(encrypted_private_key, self.master_key)

        # Get recommended protection method for individual keys
        protection_method = self._get_recommended_protection_method()

        # Re-encrypt with the new key-specific password
        new_encrypted_data = self._encrypt_private_key(private_key, new_password, protection_method)

        # Update the key entry
        key_entry["private_key"] = new_encrypted_data
        key_entry["use_master_password"] = False

        # Remove from cache if present
        if key_id in self.unlocked_keys:
            del self.unlocked_keys[key_id]

        return True

    def clear_cache(self) -> None:
        """Clear all cached keys and master key"""
        self._clear_cached_keys()

    def _clear_cached_keys(self) -> None:
        """Clear all cached keys"""
        # Clear unlocked keys
        self.unlocked_keys = {}

        # Clear master key
        if self.master_key is not None:
            secure_memzero(self.master_key)
            self.master_key = None

        self.master_key_time = 0

    def _encrypt_private_key(
        self, private_key: bytes, password: str, protection_method: KeystoreProtectionMethod
    ) -> Dict:
        """
        Encrypt a private key using the specified method

        Args:
            private_key: Private key to encrypt
            password: Password to use for encryption
            protection_method: Encryption method to use

        Returns:
            Dict: Encrypted data with all parameters needed for decryption
        """
        # Generate salt and nonce
        salt = secrets.token_bytes(16)
        nonce = secrets.token_bytes(12)

        # Choose protection parameters based on the method
        if protection_method == KeystoreProtectionMethod.ARGON2ID_AES_GCM:
            if not ARGON2_AVAILABLE:
                raise ValidationError("Argon2 is not available")

            # Parameters for Argon2
            time_cost = 3
            memory_cost = 65536  # 64 MB
            parallelism = 4

            # Derive key with Argon2
            ph = PasswordHasher(
                time_cost=time_cost, memory_cost=memory_cost, parallelism=parallelism, hash_len=32
            )

            # Encode salt as required by argon2-cffi
            salt_b64 = base64.b64encode(salt).decode("utf-8")

            # Hash the password with Argon2id
            hash_result = ph.hash(password + salt_b64)
            derived_key = hashlib.sha256(hash_result.encode("utf-8")).digest()

            # Encrypt with AES-GCM
            cipher = AESGCM(derived_key)
            # Create a consistent header for associated data
            header = {
                "method": protection_method.value,
                "params": {"salt": salt_b64, "nonce": base64.b64encode(nonce).decode("utf-8")},
            }
            ciphertext = cipher.encrypt(
                nonce, private_key, associated_data=json.dumps(header).encode("utf-8")
            )

            # Prepare result
            result = {
                "method": protection_method.value,
                "params": {
                    "salt": salt_b64,
                    "nonce": base64.b64encode(nonce).decode("utf-8"),
                    "argon2_params": {
                        "time_cost": time_cost,
                        "memory_cost": memory_cost,
                        "parallelism": parallelism,
                    },
                },
                "ciphertext": base64.b64encode(ciphertext).decode("utf-8"),
            }

        elif protection_method == KeystoreProtectionMethod.SCRYPT_CHACHA20:
            # Parameters for Scrypt
            n = 32768  # 2^15
            r = 8
            p = 1

            # Derive key with Scrypt
            kdf = Scrypt(salt=salt, length=32, n=n, r=r, p=p)
            derived_key = kdf.derive(password.encode("utf-8"))

            # Encrypt with ChaCha20Poly1305
            cipher = ChaCha20Poly1305(derived_key)
            # Create a consistent header for associated data
            header = {
                "method": protection_method.value,
                "params": {
                    "salt": base64.b64encode(salt).decode("utf-8"),
                    "nonce": base64.b64encode(nonce).decode("utf-8"),
                },
            }
            ciphertext = cipher.encrypt(
                nonce, private_key, associated_data=json.dumps(header).encode("utf-8")
            )

            # Prepare result
            result = {
                "method": protection_method.value,
                "params": {
                    "salt": base64.b64encode(salt).decode("utf-8"),
                    "nonce": base64.b64encode(nonce).decode("utf-8"),
                    "scrypt_params": {"n": n, "r": r, "p": p},
                },
                "ciphertext": base64.b64encode(ciphertext).decode("utf-8"),
            }

        elif protection_method == KeystoreProtectionMethod.PBKDF2_AES_GCM:
            # Parameters for PBKDF2
            iterations = 500000

            # Derive key with PBKDF2
            kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=iterations)
            derived_key = kdf.derive(password.encode("utf-8"))

            # Encrypt with AES-GCM
            cipher = AESGCM(derived_key)
            # Create a consistent header for associated data
            header = {
                "method": protection_method.value,
                "params": {"salt": salt_b64, "nonce": base64.b64encode(nonce).decode("utf-8")},
            }
            ciphertext = cipher.encrypt(
                nonce, private_key, associated_data=json.dumps(header).encode("utf-8")
            )

            # Prepare result
            result = {
                "method": protection_method.value,
                "params": {
                    "salt": base64.b64encode(salt).decode("utf-8"),
                    "nonce": base64.b64encode(nonce).decode("utf-8"),
                    "pbkdf2_params": {"iterations": iterations},
                },
                "ciphertext": base64.b64encode(ciphertext).decode("utf-8"),
            }

        else:
            raise ValidationError(f"Unsupported protection method: {protection_method}")

        return result

    def _decrypt_private_key(self, encrypted_data: Dict, password: str) -> bytes:
        """
        Decrypt a private key

        Args:
            encrypted_data: Encrypted data with all parameters
            password: Password to use for decryption

        Returns:
            bytes: Decrypted private key

        Raises:
            AuthenticationError: If the password is incorrect
            ValidationError: If the encryption method is not supported
        """
        try:
            method = encrypted_data["method"]
            params = encrypted_data["params"]
            ciphertext = base64.b64decode(encrypted_data["ciphertext"])

            if method == KeystoreProtectionMethod.ARGON2ID_AES_GCM.value:
                if not ARGON2_AVAILABLE:
                    raise ValidationError("Argon2 is required but not available")

                # Extract parameters
                salt_b64 = params["salt"]
                nonce = base64.b64decode(params["nonce"])
                argon2_params = params["argon2_params"]

                # Derive key with Argon2
                ph = PasswordHasher(
                    time_cost=argon2_params["time_cost"],
                    memory_cost=argon2_params["memory_cost"],
                    parallelism=argon2_params["parallelism"],
                    hash_len=32,
                )

                # Hash the password with Argon2id
                hash_result = ph.hash(password + salt_b64)
                derived_key = hashlib.sha256(hash_result.encode("utf-8")).digest()

                # Decrypt with AES-GCM
                cipher = AESGCM(derived_key)
                # Recreate the header to match encryption
                header = {
                    "method": method,
                    "params": {"salt": salt_b64, "nonce": base64.b64encode(nonce).decode("utf-8")},
                }
                # Try both methods for backward compatibility
                try:
                    plaintext = cipher.decrypt(
                        nonce, ciphertext, associated_data=json.dumps(header).encode("utf-8")
                    )
                except Exception:
                    # Fallback for old encrypted data
                    plaintext = cipher.decrypt(nonce, ciphertext, associated_data=None)

            elif method == KeystoreProtectionMethod.SCRYPT_CHACHA20.value:
                # Extract parameters
                salt = base64.b64decode(params["salt"])
                nonce = base64.b64decode(params["nonce"])
                scrypt_params = params["scrypt_params"]

                # Derive key with Scrypt
                kdf = Scrypt(
                    salt=salt,
                    length=32,
                    n=scrypt_params["n"],
                    r=scrypt_params["r"],
                    p=scrypt_params["p"],
                )
                derived_key = kdf.derive(password.encode("utf-8"))

                # Decrypt with ChaCha20Poly1305
                cipher = ChaCha20Poly1305(derived_key)
                # Recreate the header to match encryption
                header = {
                    "method": method,
                    "params": {
                        "salt": base64.b64encode(salt).decode("utf-8"),
                        "nonce": base64.b64encode(nonce).decode("utf-8"),
                    },
                }
                # Try both methods for backward compatibility
                try:
                    plaintext = cipher.decrypt(
                        nonce, ciphertext, associated_data=json.dumps(header).encode("utf-8")
                    )
                except Exception:
                    # Fallback for old encrypted data
                    plaintext = cipher.decrypt(nonce, ciphertext, associated_data=None)

            elif method == KeystoreProtectionMethod.PBKDF2_AES_GCM.value:
                # Extract parameters
                salt = base64.b64decode(params["salt"])
                nonce = base64.b64decode(params["nonce"])
                pbkdf2_params = params["pbkdf2_params"]

                # Derive key with PBKDF2
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=salt,
                    iterations=pbkdf2_params["iterations"],
                )
                derived_key = kdf.derive(password.encode("utf-8"))

                # Decrypt with AES-GCM
                cipher = AESGCM(derived_key)
                # Recreate the header to match encryption
                header = {
                    "method": method,
                    "params": {"salt": salt_b64, "nonce": base64.b64encode(nonce).decode("utf-8")},
                }
                # Try both methods for backward compatibility
                try:
                    plaintext = cipher.decrypt(
                        nonce, ciphertext, associated_data=json.dumps(header).encode("utf-8")
                    )
                except Exception:
                    # Fallback for old encrypted data
                    plaintext = cipher.decrypt(nonce, ciphertext, associated_data=None)

            else:
                raise ValidationError(f"Unsupported protection method: {method}")

            return plaintext

        except Exception as e:
            if "MAC check failed" in str(e) or "Cipher tag does not match" in str(e):
                raise AuthenticationError("Invalid password or corrupted data")
            else:
                raise InternalError(f"Decryption failed: {str(e)}")

    def _encrypt_with_derived_key(
        self, data: bytes, derived_key: bytes, protection_method: KeystoreProtectionMethod
    ) -> Dict:
        """
        Encrypt data using an already derived key

        Args:
            data: Data to encrypt
            derived_key: Key to use for encryption
            protection_method: Encryption method to use

        Returns:
            Dict: Encrypted data with parameters (except key derivation ones)
        """
        # Generate nonce
        nonce = secrets.token_bytes(12)

        # Prepare the header that will be used for associated_data
        header = {
            "method": protection_method.value,
            "params": {"nonce": base64.b64encode(nonce).decode("utf-8"), "key_source": "master"},
        }

        if protection_method == KeystoreProtectionMethod.SCRYPT_CHACHA20:
            # Encrypt with ChaCha20Poly1305
            cipher = ChaCha20Poly1305(derived_key)
            # BUGFIX: Use the associated_data consistent with load_keystore
            ciphertext = cipher.encrypt(
                nonce, data, associated_data=json.dumps(header).encode("utf-8")
            )

            # Prepare result (without key derivation parameters)
            result = {
                "method": protection_method.value,
                "params": {
                    "nonce": base64.b64encode(nonce).decode("utf-8"),
                    "key_source": "master",
                },
                "ciphertext": base64.b64encode(ciphertext).decode("utf-8"),
            }

        else:
            # Use AES-GCM for all other methods
            cipher = AESGCM(derived_key)
            # BUGFIX: Use the associated_data consistent with load_keystore (header JSON)
            header_json = json.dumps(header).encode("utf-8")
            ciphertext = cipher.encrypt(nonce, data, associated_data=header_json)

            # Prepare result (without key derivation parameters)
            result = {
                "method": protection_method.value,
                "params": {
                    "nonce": base64.b64encode(nonce).decode("utf-8"),
                    "key_source": "master",
                },
                "ciphertext": base64.b64encode(ciphertext).decode("utf-8"),
            }

        return result

    def _decrypt_with_derived_key(self, encrypted_data: Dict, derived_key: bytes) -> bytes:
        """
        Decrypt data using an already derived key

        Args:
            encrypted_data: Encrypted data with parameters
            derived_key: Key to use for decryption

        Returns:
            bytes: Decrypted data

        Raises:
            ValidationError: If the encryption method is not supported
            InternalError: If decryption fails
        """
        try:
            method = encrypted_data["method"]
            params = encrypted_data["params"]
            ciphertext = base64.b64decode(encrypted_data["ciphertext"])
            nonce = base64.b64decode(params["nonce"])

            # Recreate the same header used during encryption to use as associated_data
            header = {"method": method, "params": params}

            if method == KeystoreProtectionMethod.SCRYPT_CHACHA20.value:
                # Decrypt with ChaCha20Poly1305
                cipher = ChaCha20Poly1305(derived_key)
                # BUGFIX: Try methods in consistent order for compatibility
                try:
                    plaintext = cipher.decrypt(
                        nonce, ciphertext, associated_data=json.dumps(header).encode("utf-8")
                    )
                except Exception:
                    try:
                        # Then try with empty bytes
                        plaintext = cipher.decrypt(nonce, ciphertext, associated_data=b"")
                    except Exception:
                        # Finally try with None
                        plaintext = cipher.decrypt(nonce, ciphertext, associated_data=None)

            elif method in [
                KeystoreProtectionMethod.ARGON2ID_AES_GCM.value,
                KeystoreProtectionMethod.PBKDF2_AES_GCM.value,
            ]:
                # Decrypt with AES-GCM
                cipher = AESGCM(derived_key)
                # BUGFIX: Try methods in consistent order for compatibility
                try:
                    plaintext = cipher.decrypt(nonce, ciphertext, associated_data=b"")
                except Exception:
                    try:
                        # Then try with None
                        plaintext = cipher.decrypt(nonce, ciphertext, associated_data=None)
                    except Exception:
                        # Finally try with header
                        plaintext = cipher.decrypt(
                            nonce, ciphertext, associated_data=json.dumps(header).encode("utf-8")
                        )

            else:
                raise ValidationError(f"Unsupported protection method: {method}")

            return plaintext

        except Exception as e:
            if "MAC check failed" in str(e) or "Cipher tag does not match" in str(e):
                raise AuthenticationError("Invalid key or corrupted data")
            else:
                raise InternalError(f"Decryption failed: {str(e)}")

    def _generate_key_id(self) -> str:
        """Generate a unique key ID"""
        return str(uuid.uuid4())

    def _get_protection_params(self, security_level: KeystoreSecurityLevel) -> Dict:
        """
        Get protection parameters based on security level

        Args:
            security_level: Security level to use

        Returns:
            Dict: Protection parameters
        """
        # Generate salt and nonce
        salt = secrets.token_bytes(16)
        nonce = secrets.token_bytes(12)

        # Choose method based on availability
        if ARGON2_AVAILABLE:
            method = KeystoreProtectionMethod.ARGON2ID_AES_GCM
        else:
            # Fallback to Scrypt + ChaCha20
            method = KeystoreProtectionMethod.SCRYPT_CHACHA20

        if method == KeystoreProtectionMethod.ARGON2ID_AES_GCM:
            # Set Argon2 parameters based on security level
            if security_level == KeystoreSecurityLevel.PARANOID:
                # Use more reasonable memory requirements that most systems can handle
                time_cost = 8
                memory_cost = 262144  # 256 MB instead of 1 GB
                parallelism = 4
            elif security_level == KeystoreSecurityLevel.HIGH:
                time_cost = 6
                memory_cost = 131072  # 128 MB
                parallelism = 4
            else:  # STANDARD
                time_cost = 3
                memory_cost = 65536  # 64 MB
                parallelism = 2

            return {
                "method": method.value,
                "params": {
                    "salt": base64.b64encode(salt).decode("utf-8"),
                    "nonce": base64.b64encode(nonce).decode("utf-8"),
                    "argon2_params": {
                        "time_cost": time_cost,
                        "memory_cost": memory_cost,
                        "parallelism": parallelism,
                    },
                },
            }

        elif method == KeystoreProtectionMethod.SCRYPT_CHACHA20:
            # Set Scrypt parameters based on security level
            if security_level == KeystoreSecurityLevel.PARANOID:
                n = 1048576  # 2^20
                r = 16
                p = 2
            elif security_level == KeystoreSecurityLevel.HIGH:
                n = 262144  # 2^18
                r = 8
                p = 1
            else:  # STANDARD
                n = 65536  # 2^16
                r = 8
                p = 1

            return {
                "method": method.value,
                "params": {
                    "salt": base64.b64encode(salt).decode("utf-8"),
                    "nonce": base64.b64encode(nonce).decode("utf-8"),
                    "scrypt_params": {"n": n, "r": r, "p": p},
                },
            }

        else:  # Fallback to PBKDF2
            # Set PBKDF2 parameters based on security level
            if security_level == KeystoreSecurityLevel.PARANOID:
                iterations = 1000000
            elif security_level == KeystoreSecurityLevel.HIGH:
                iterations = 600000
            else:  # STANDARD
                iterations = 310000

            return {
                "method": KeystoreProtectionMethod.PBKDF2_AES_GCM.value,
                "params": {
                    "salt": base64.b64encode(salt).decode("utf-8"),
                    "nonce": base64.b64encode(nonce).decode("utf-8"),
                    "pbkdf2_params": {"iterations": iterations},
                },
            }

    def _get_recommended_protection_method(self) -> KeystoreProtectionMethod:
        """
        Get the recommended protection method based on available algorithms

        Returns:
            KeystoreProtectionMethod: Recommended method
        """
        if ARGON2_AVAILABLE:
            return KeystoreProtectionMethod.ARGON2ID_AES_GCM
        else:
            return KeystoreProtectionMethod.SCRYPT_CHACHA20
