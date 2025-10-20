"""Base64 encoding and decoding utilities."""

import base64


class Converter:
    """Converter utilities for Base64 encoding/decoding."""
    
    @staticmethod
    def bytes_to_hex(data: bytes) -> str:
        """
        Convert bytes to hexadecimal string.
        
        Args:
            data: Bytes to convert
            
        Returns:
            Hexadecimal string
        """
        return data.hex()
    
    @staticmethod
    def bytes_to_base64(data: bytes) -> str:
        """
        Convert bytes to Base64 string.
        
        Args:
            data: Bytes to convert
            
        Returns:
            Base64 encoded string
        """
        return base64.b64encode(data).decode('utf-8')
    
    @staticmethod
    def string_to_base64(data: str) -> str:
        """
        Convert string to Base64 string.
        
        Args:
            data: String to convert
            
        Returns:
            Base64 encoded string
        """
        return Converter.bytes_to_base64(data.encode('utf-8'))
    
    @staticmethod
    def base64_to_bytes(base64_str: str) -> bytes:
        """
        Convert Base64 string to bytes.
        
        Args:
            base64_str: Base64 encoded string
            
        Returns:
            Decoded bytes
        """
        return base64.b64decode(base64_str.encode('utf-8'))
    
    @staticmethod
    def base64_to_string(base64_str: str) -> str:
        """
        Convert Base64 string to original string.
        
        Args:
            base64_str: Base64 encoded string
            
        Returns:
            Decoded string
        """
        return Converter.base64_to_bytes(base64_str).decode('utf-8')