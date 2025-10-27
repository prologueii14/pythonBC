# -*- encoding: utf-8 -*-
"""
Elliptic Curve Arithmetic over Finite Fields
Ep(a, b): y^2 = x^3 + ax + b (mod p)
"""

class ECPoint:
    """A point on an Elliptic Curve"""

    def __init__(self, x, y, curve):
        self.x = x
        self.y = y
        self.curve = curve

        # Verify that the point lies on the curve
        if (x is not None) and (y is not None):
            if not curve.is_on_curve(x, y):
                raise ValueError(f"Point ({x}, {y}) is not on the curve")

    def is_infinity(self):
        """Check if this point is the point at infinity (the identity element)"""
        return self.x is None and self.y is None

    def __eq__(self, other):
        """Check point equality"""
        return self.x == other.x and self.y == other.y and self.curve == other.curve

    def __neg__(self):
        """Return the inverse point: (x, y) -> (x, -y mod p)"""
        if self.is_infinity():
            return self
        return ECPoint(self.x, (-self.y) % self.curve.p, self.curve)

    def __add__(self, other):
        """Elliptic curve point addition"""
        if self.curve != other.curve:
            raise ValueError("Points must be on the same curve")

        # Identity: P + O = P
        if self.is_infinity():
            return other
        
        # Identity: O + P = P
        if other.is_infinity():
            return self

        # Inverse: P + (-P) = O
        if self.x == other.x and self.y == (-other.y) % self.curve.p:
            return ECPoint(None, None, self.curve)  # Point at infinity

        # Compute slope d
        if self.x == other.x and self.y == other.y:
            # Point Doubling: P + P = 2P
            numerator = (3 * self.x * self.x + self.curve.a) % self.curve.p
            denominator = (2 * self.y) % self.curve.p
        else:
            # Point Addition: P + Q
            numerator = (other.y - self.y) % self.curve.p
            denominator = (other.x - self.x) % self.curve.p

        # Compute modular multiplicative inverse using Extended Euclidean Algorithm
        d = (numerator * self.curve.multiplicative_inverse(denominator)) % self.curve.p

        # Compute resulting coordinates
        xr = (d * d - self.x - other.x) % self.curve.p
        yr = (d * (self.x - xr) - self.y) % self.curve.p

        return ECPoint(xr, yr, self.curve)

    def __mul__(self, scalar):
        """Scalar multiplication: P * k (using double-and-add algorithm)"""
        if scalar == 0: # P * 0 = O
            return ECPoint(None, None, self.curve)  # Point at infinity O

        if scalar < 0: # P * (-k) = (-P) * k 
            return (-self) * (-scalar) # Return the negative point multiplied by positive scalar

        # Double-and-add method
        result = ECPoint(None, None, self.curve)  # Start from infinity O
        addend = self

        while scalar:
            if scalar & 1:  # If the least significant bit is 1
                result = result + addend
            addend = addend + addend  # Point doubling
            scalar >>= 1  # Shift right by one bit

        return result

    def __rmul__(self, scalar):
        """Right scalar multiplication to support k * P"""
        return self.__mul__(scalar)

    def __str__(self):
        if self.is_infinity():
            return "O"
        return f"Point({self.x}, {self.y})"

    def __repr__(self):
        return self.__str__()


class EllipticCurve:
    """Elliptic Curve Ep(a, b): y^2 = x^3 + ax + b (mod p)"""

    def __init__(self, a, b, p):
        """
        Initialize the elliptic curve.
        a, b: curve parameters
        p: prime modulus
        """
        self.a = a
        self.b = b
        self.p = p

        # Check discriminant (4a^3 + 27b^2) (mod p) != 0 (mod p)
        delta = (4 * a**3 + 27 * b**2) % p
        if delta == 0:
            raise ValueError("Invalid curve parameters: discriminant is zero")

    def is_on_curve(self, x, y):
        """Check whether (x, y) lies on the curve"""
        left = (y**2) % self.p
        right = (x**3 + self.a * x + self.b) % self.p
        return left == right

    def multiplicative_inverse(self, a):
        """Compute modular multiplicative inverse: a^(-1) mod p (using Extended Euclidean Algorithm)"""
        if a < 0:
            a = (a % self.p + self.p) % self.p

        def extended_gcd(a, b):
            if a == 0:
                return b, 0, 1
            gcd, x1, y1 = extended_gcd(b % a, a)
            x = y1 - (b // a) * x1
            y = x1
            return gcd, x, y

        gcd, x, _ = extended_gcd(a, self.p)
        if gcd != 1:
            raise ValueError(f"{a} has no modular multiplicative inverse under mod {self.p}")
        return (x % self.p + self.p) % self.p

    def ECPoint(self, x, y):
        """Create a point on the curve"""
        return ECPoint(x, y, self)

    def infinity(self):
        """Return the point at infinity (identity element of the group)"""
        return ECPoint(None, None, self)

    def __eq__(self, other):
        return self.a == other.a and self.b == other.b and self.p == other.p

    def __str__(self):
        return f"EllipticCurve: y^2 = x^3 + {(self.a) != 0 if self.a else ""}x + {self.b} (mod {self.p})"


def demonstrate_abelian_group_properties():
    """Demonstrate the abelian group properties of an elliptic curve"""
    print("=== Demonstration of Elliptic Curve Abelian Group Properties ===\n")

    # Example with a small prime for clarity
    p = 23
    a = 1
    b = 1

    curve = EllipticCurve(a, b, p)
    print(f"Curve: {curve}\n")

    # Create example points
    P = curve.point(3, 10)
    Q = curve.point(9, 7)

    print(f"P = {P}")
    print(f"Q = {Q}\n")

    # 1. Closure
    print("1. Closure:")
    R = P + Q
    print(f"   P + Q = {R}")
    print(f"   Is R on curve: {curve.is_on_curve(R.x, R.y)}\n")

    # 2. Associativity
    print("2. Associativity:")
    S = curve.point(13, 16)
    left = (P + Q) + S
    right = P + (Q + S)
    print(f"   (P + Q) + S = {left}")
    print(f"   P + (Q + S) = {right}")
    print(f"   Equal: {left == right}\n")

    # 3. Identity
    print("3. Identity:")
    O = curve.infinity()
    result = P + O
    print(f"   P + O = {result}")
    print(f"   P + O == P: {result == P}\n")

    # 4. Inverse
    print("4. Inverse:")
    neg_P = -P
    result = P + neg_P
    print(f"   P = {P}")
    print(f"   -P = {neg_P}")
    print(f"   P + (-P) = {result}")
    print(f"   Is point at infinity: {result.is_infinity()}\n")

    # 5. Commutativity
    print("5. Commutativity:")
    left = P + Q
    right = Q + P
    print(f"   P + Q = {left}")
    print(f"   Q + P = {right}")
    print(f"   Equal: {left == right}\n")

    # 6. Scalar Multiplication
    print("6. Scalar Multiplication:")
    for k in range(1, 6):
        result = k * P
        print(f"   {k}P = {result}")
    print()


def demonstrate_real_curve():
    """Demonstrate an example with real-world curve parameters (secp256k1-like)"""
    print("\n=== Demonstration with Larger Prime Curve ===\n")

    # secp256k1 parameters
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    a = 0
    b = 7

    curve = EllipticCurve(a, b, p)
    print(f"Curve: y^2 = x^3 + {b} (mod p)")
    print(f"Prime bit length: {p.bit_length()}\n")

    # secp256k1 generator point G
    Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
    Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8

    G = curve.point(Gx, Gy)
    print("Generator Point G:")
    print(f"  x = {hex(G.x)}")
    print(f"  y = {hex(G.y)}")
    print(f"  On curve: {curve.is_on_curve(G.x, G.y)}\n")

    # Scalar multiplication (core of ECDSA)
    print("Scalar multiplication (Private key * G = Public key):")
    private_key = 12345
    public_key = private_key * G
    print(f"  Private key: {private_key}")
    print(f"  Public key (truncated):")
    print(f"    x = {hex(public_key.x)[:50]}...")
    print(f"    y = {hex(public_key.y)[:50]}...")
    print(f"  On curve: {curve.is_on_curve(public_key.x, public_key.y)}")


if __name__ == "__main__":
    demonstrate_abelian_group_properties()
    demonstrate_real_curve()