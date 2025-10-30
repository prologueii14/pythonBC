"""Security utilities for ECDSA signature verification."""

import sys
import os

# Add the ecdsa_with_rfc6979 module to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ecdsa_with_rfc6979'))

from ecdsa_with_rfc6979.ecdsa import ECDSA, StandardCurves
from tools.converter import Converter
from tools.io import IO
from config.security_config import SecurityConfig


class Security:
    """Security utilities for ECDSA signature verification."""

    @staticmethod
    def _get_ecdsa_instance():
        """
        Get ECDSA instance based on configuration.

        Returns:
            ECDSA instance
        """
        if SecurityConfig.CURVE_NAME == "secp256k1":
            return StandardCurves.secp256k1()
        elif SecurityConfig.CURVE_NAME == "secp256r1":
            return StandardCurves.secp256r1()
        else:
            raise ValueError(f"Unsupported curve: {SecurityConfig.CURVE_NAME}")

    @staticmethod
    def _restore_public_key_from_address(address: str):
        """
        Restore ECDSA public key from Base64 encoded address.

        Args:
            address: Base64 encoded public key

        Returns:
            ECPoint public key object, or None if error
        """
        try:
            ecdsa = Security._get_ecdsa_instance()
            public_key = ecdsa.deserialize_public_key(address)
            return public_key
        except Exception as e:
            IO.errln(f"Cannot restore ECDSA public key from: {address}")
            print(e)
            return None

    @staticmethod
    def _get_hash_function():
        """
        Get hash function based on configuration.

        Returns:
            Hash function from hashlib
        """
        import hashlib

        # Parse signature algorithm (e.g., "SHA256withECDSA" -> "SHA256")
        sig_algo = SecurityConfig.SIGNATURE_ALGORITHM
        hash_name = sig_algo.split('with')[0].upper()

        # Map to hashlib functions
        hash_map = {
            'MD5': hashlib.md5,
            'SHA1': hashlib.sha1,
            'SHA224': hashlib.sha224,
            'SHA256': hashlib.sha256,
            'SHA384': hashlib.sha384,
            'SHA512': hashlib.sha512,
            'SHA3-224': hashlib.sha3_224,
            'SHA3-256': hashlib.sha3_256,
            'SHA3-384': hashlib.sha3_384,
            'SHA3-512': hashlib.sha3_512,
        }

        return hash_map.get(hash_name, hashlib.sha256)

    @staticmethod
    def is_signature_valid(address: str, data: str, encoded_signature: str) -> bool:
        """
        Verify ECDSA signature validity.

        Args:
            address: Base64 encoded public key (account address)
            data: Original data that was signed
            encoded_signature: Base64 encoded signature

        Returns:
            True if signature is valid, False otherwise
        """
        try:
            ecdsa = Security._get_ecdsa_instance()
            public_key = Security._restore_public_key_from_address(address)
            if public_key is None:
                return False

            signature = ecdsa.deserialize_signature(encoded_signature)
            hash_func = Security._get_hash_function()

            # Verify ECDSA signature
            return ecdsa.verify(data, signature, public_key, hash_func=hash_func)

        except Exception as e:
            IO.errln("Something went wrong when validating ECDSA signature")
            print(e)
            return False
