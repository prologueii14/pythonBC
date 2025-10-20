"""Hash calculation utilities."""

import hashlib
from config.security_config import SecurityConfig
from .converter import Converter


class HashMaker:
    """Hash calculation utilities using configured algorithm."""
    
    @staticmethod
    def hash_bytes(data: bytes) -> str:
        """
        Calculate hash of bytes data.
        
        Args:
            data: Bytes to hash
            
        Returns:
            Hexadecimal hash string
        """
        try:
            algorithm = SecurityConfig.HASH_ALGORITHM
            hasher = hashlib.new(algorithm)
            hasher.update(data)
            return Converter.bytes_to_hex(hasher.digest())
        except Exception as e:
            print(f"Error: Something went wrong when hashing data: {e}")
            return ""
    
    @staticmethod
    def hash_string(data: str) -> str:
        """
        Calculate hash of string data.
        
        Args:
            data: String to hash
            
        Returns:
            Hexadecimal hash string
        """
        return HashMaker.hash_bytes(data.encode('utf-8'))
    
    @staticmethod
    def validate_bytes(hash_value: str, data: bytes) -> bool:
        """
        Validate if hash matches data.
        
        Args:
            hash_value: Expected hash value
            data: Data to validate
            
        Returns:
            True if hash matches, False otherwise
        """
        return hash_value == HashMaker.hash_bytes(data)
    
    @staticmethod
    def validate_string(hash_value: str, data: str) -> bool:
        """
        Validate if hash matches string data.
        
        Args:
            hash_value: Expected hash value
            data: String data to validate
            
        Returns:
            True if hash matches, False otherwise
        """
        return HashMaker.validate_bytes(hash_value, data.encode('utf-8'))