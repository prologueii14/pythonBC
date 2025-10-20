"""Nonce generation utilities."""

import secrets


class NonceMaker:
    """Nonce generation utilities."""
    
    # Nonce generation mode: 0 = addition, 1 = random
    _NONCE_MODE = 1
    _counter = 0
    
    @staticmethod
    def get_nonce() -> int:
        """
        Generate a nonce value.
        
        Returns:
            Nonce value (integer)
        """
        if NonceMaker._NONCE_MODE == 0:
            return NonceMaker._addition_mode()
        elif NonceMaker._NONCE_MODE == 1:
            return NonceMaker._random_mode()
        else:
            return NonceMaker._addition_mode()
    
    @staticmethod
    def _addition_mode() -> int:
        """
        Generate nonce using incremental counter.
        
        Returns:
            Counter value
        """
        nonce = NonceMaker._counter
        NonceMaker._counter += 1
        return nonce
    
    @staticmethod
    def _random_mode() -> int:
        """
        Generate nonce using secure random.
        
        Returns:
            Random integer between 0 and 2^31-1
        """
        return secrets.randbelow(2**31)