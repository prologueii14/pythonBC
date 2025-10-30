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
    PUBLIC_KEY_ALGORITHM = "ECDSA"
    CURVE_NAME = "secp256k1"  # Bitcoin's curve

    # Signature Algorithm
    SIGNATURE_ALGORITHM = "SHA256withECDSA"
    USE_RFC6979 = True  # Use deterministic signatures
    """
    Supported Curves:
    - secp256k1 (Bitcoin's curve)
    - secp256r1 (NIST P-256)

    Supported Hash Algorithms:
    - SHA256
    - SHA3-256
    """
