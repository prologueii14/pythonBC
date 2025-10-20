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
    PUBLIC_KEY_ALGORITHM = "RSA"
    PUBLIC_KEY_LENGTH = 1024 
    
    # Signature Algorithm
    SIGNATURE_ALGORITHM = "SHA3-256withRSA"
    """
    Supported Algorithms (Java-style naming, will be converted):
    - MD5withRSA
    - SHA1withRSA
    - SHA224withRSA
    - SHA256withRSA
    - SHA384withRSA
    - SHA512withRSA
    - SHA3-224withRSA
    - SHA3-256withRSA
    - SHA3-384withRSA
    - SHA3-512withRSA
    """