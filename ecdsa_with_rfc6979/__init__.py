"""
ECDSA with RFC 6979 implementation module.

This module provides a complete implementation of ECDSA (Elliptic Curve Digital Signature Algorithm)
with support for RFC 6979 deterministic signatures.

Classes:
    EllipticCurve: Elliptic curve arithmetic over finite fields
    ECPoint: Point on an elliptic curve
    ECDSA: ECDSA digital signature algorithm
    StandardCurves: Standard elliptic curves (secp256k1, secp256r1)
"""

from .elliptic_curve import EllipticCurve, ECPoint
from .ecdsa import ECDSA, StandardCurves

__all__ = ['EllipticCurve', 'ECPoint', 'ECDSA', 'StandardCurves']
__version__ = '1.0.0'
