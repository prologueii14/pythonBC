"""Security configuration settings."""


class SecurityConfig:
    """Security parameters configuration."""
    
    # Hash Algorithm
    HASH_ALGORITHM = "sha3_256"
    """
    Supported Algorithms:
    - md5
    - sha1
    - sha224
    - sha256
    - sha384
    - sha512
    - sha3_224
    - sha3_256
    - sha3_384
    - sha3_512
    """
    
    # Public Key Algorithm
    PUBLIC_KEY_ALGORITHM = "RSA"  # Options: "RSA", "ECDSA", "DPECDSA"
    PUBLIC_KEY_LENGTH = 1024 
    """
    Supported Algorithms:
    - RSA: 1024, 2048, 4096
    - ECDSA: 256 (secp256k1)
    - DPECDSA: 256 (secp256k1)
    """
    
    # Signature Algorithm
    SIGNATURE_ALGORITHM = "SHA3-256withRSA"
    """
    Supported Algorithms:
    - For RSA: MD5withRSA, SHA1withRSA, SHA224withRSA, SHA256withRSA, 
               SHA384withRSA, SHA512withRSA, SHA3-224withRSA, SHA3-256withRSA,
               SHA3-384withRSA, SHA3-512withRSA
    - For ECDSA: SHA3256withECDSA
    - For DPECDSA: SHA3256withDPECDSA
    """
    
    # Network Compatibility
    ALLOW_MIXED_ALGORITHMS = True
    """Allow nodes with different algorithms to coexist in the network."""
    
    @staticmethod
    def validate_configuration() -> bool:
        """
        Validate security configuration.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        valid_combinations = {
            "RSA": ["MD5withRSA", "SHA1withRSA", "SHA224withRSA", "SHA256withRSA", 
                   "SHA384withRSA", "SHA512withRSA", "SHA3-224withRSA", "SHA3-256withRSA",
                   "SHA3-384withRSA", "SHA3-512withRSA"],
            "ECDSA": ["SHA3256withECDSA"],
            "DPECDSA": ["SHA3256withDPECDSA"]
        }
        
        pk_algo = SecurityConfig.PUBLIC_KEY_ALGORITHM
        sig_algo = SecurityConfig.SIGNATURE_ALGORITHM
        
        if pk_algo not in valid_combinations:
            print(f"ERROR: Invalid PUBLIC_KEY_ALGORITHM: {pk_algo}")
            return False
            
        if sig_algo not in valid_combinations[pk_algo]:
            print(f"ERROR: Invalid SIGNATURE_ALGORITHM for {pk_algo}: {sig_algo}")
            print(f"Valid options: {valid_combinations[pk_algo]}")
            return False
            
        # Validate key lengths
        if pk_algo == "RSA" and SecurityConfig.PUBLIC_KEY_LENGTH not in [1024, 2048, 4096]:
            print(f"ERROR: Invalid RSA key length: {SecurityConfig.PUBLIC_KEY_LENGTH}")
            return False
        elif pk_algo in ["ECDSA", "DPECDSA"] and SecurityConfig.PUBLIC_KEY_LENGTH != 256:
            print(f"ERROR: {pk_algo} only supports 256-bit keys")
            return False
            
        return True
    
    @staticmethod
    def get_supported_algorithms() -> dict:
        """Get supported algorithms mapping."""
        return {
            'RSA': {
                'key_lengths': [1024, 2048, 4096],
                'signature_formats': [
                    'MD5withRSA', 'SHA1withRSA', 'SHA224withRSA',
                    'SHA256withRSA', 'SHA384withRSA', 'SHA512withRSA',
                    'SHA3-224withRSA', 'SHA3-256withRSA', 
                    'SHA3-384withRSA', 'SHA3-512withRSA'
                ],
                'description': 'Traditional public key algorithm'
            },
            'ECDSA': {
                'key_lengths': [256],
                'signature_formats': ['SHA3256withECDSA'],
                'description': 'Elliptic Curve Digital Signature Algorithm',
                'curve': 'secp256k1'
            },
            'DPECDSA': {
                'key_lengths': [256],
                'signature_formats': ['SHA3256withDPECDSA'],
                'description': 'Double Parameter ECDSA (IEEE 2021)',
                'curve': 'secp256k1'
            }
        }