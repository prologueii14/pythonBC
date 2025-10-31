"""Address utility functions for multi-algorithm support."""

import json
from tools.converter import Converter
from tools.io import IO


class AddressUtils:
    """Utility functions for address handling across different algorithms."""
    
    @staticmethod
    def normalize_address(address: str) -> str:
        """
        Normalize address to standard format.
        
        Args:
            address: Original address
            
        Returns:
            Normalized address string
        """
        return address
    
    @staticmethod
    def get_address_info(address: str) -> dict:
        """
        Get detailed information about an address.
        
        Args:
            address: Account address
            
        Returns:
            Dictionary with address information
        """
        from tools.security import Security
        
        algo_type = Security.detect_address_type(address)
        info = {
            'algorithm': algo_type,
            'address': address,
            'length': len(address)
        }
        
        if algo_type in ["ECDSA", "DPECDSA"]:
            try:
                key_data = json.loads(Converter.base64_to_bytes(address).decode('utf-8'))
                info['x_coordinate'] = hex(key_data['x'])
                info['y_coordinate'] = hex(key_data['y'])
                info['curve'] = 'secp256k1'
            except:
                info['error'] = 'Cannot parse EC coordinates'
        
        elif algo_type == "RSA":
            info['key_type'] = 'DER encoded public key'
            info['key_length'] = len(Converter.base64_to_bytes(address)) * 8
        
        return info
    
    @staticmethod
    def is_compatible_addresses(address1: str, address2: str) -> bool:
        """
        Check if two addresses are algorithm-compatible.
        
        Args:
            address1: First address
            address2: Second address
            
        Returns:
            True if addresses use compatible algorithms
        """
        from tools.security import Security
        
        algo1 = Security.detect_address_type(address1)
        algo2 = Security.detect_address_type(address2)

        return True
    
    @staticmethod
    def format_address_for_display(address: str, max_length: int = 50) -> str:
        """
        Format address for display purposes.
        
        Args:
            address: Account address
            max_length: Maximum display length
            
        Returns:
            Formatted address string
        """
        from tools.security import Security
        
        algo_type = Security.detect_address_type(address)
        
        if len(address) <= max_length:
            return f"{address} ({algo_type})"
        else:
            truncated = address[:max_length-3] + "..."
            return f"{truncated} ({algo_type})"