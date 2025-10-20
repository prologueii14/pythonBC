"""Security utilities for signature verification."""

from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature

from tools.converter import Converter
from tools.io import IO
from config.security_config import SecurityConfig


class Security:
    """Security utilities for signature verification."""
    
    @staticmethod
    def _restore_public_key_from_address(address: str):
        """
        Restore public key from Base64 encoded address.
        
        Args:
            address: Base64 encoded public key
            
        Returns:
            Public key object, or None if error
        """
        try:
            public_key_bytes = Converter.base64_to_bytes(address)
            public_key = serialization.load_der_public_key(
                public_key_bytes,
                backend=default_backend()
            )
            return public_key
        except Exception as e:
            IO.errln(f"Cannot restore public key from: {address}")
            print(e)
            return None
    
    @staticmethod
    def _get_hash_algorithm():
        """
        Get hash algorithm object based on configuration.
        
        Returns:
            Hash algorithm object from cryptography library
        """
        # Parse signature algorithm (e.g., "SHA3-256withRSA" -> "SHA3-256")
        sig_algo = SecurityConfig.SIGNATURE_ALGORITHM
        hash_name = sig_algo.split('with')[0].upper()
        
        # Map to cryptography hash algorithms
        hash_map = {
            'MD5': hashes.MD5(),
            'SHA1': hashes.SHA1(),
            'SHA224': hashes.SHA224(),
            'SHA256': hashes.SHA256(),
            'SHA384': hashes.SHA384(),
            'SHA512': hashes.SHA512(),
            'SHA3-224': hashes.SHA3_224(),
            'SHA3-256': hashes.SHA3_256(),
            'SHA3-384': hashes.SHA3_384(),
            'SHA3-512': hashes.SHA3_512(),
        }
        
        return hash_map.get(hash_name, hashes.SHA3_256())
    
    @staticmethod
    def is_signature_valid(address: str, data: str, encoded_signature: str) -> bool:
        """
        Verify signature validity.
        
        Args:
            address: Base64 encoded public key (account address)
            data: Original data that was signed
            encoded_signature: Base64 encoded signature
            
        Returns:
            True if signature is valid, False otherwise
        """
        try:
            public_key = Security._restore_public_key_from_address(address)
            if public_key is None:
                return False
            
            signature = Converter.base64_to_bytes(encoded_signature)
            hash_algo = Security._get_hash_algorithm()
            
            # Verify signature
            public_key.verify(
                signature,
                data.encode('utf-8'),
                padding.PKCS1v15(),
                hash_algo
            )
            
            return True
        except InvalidSignature:
            return False
        except Exception as e:
            IO.errln("Something went wrong when validating signature")
            print(e)
            return False