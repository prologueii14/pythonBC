# Elliptic Curve Cryptography Implementation

## Overview

This module implements elliptic curve arithmetic over finite fields, providing the mathematical foundation for elliptic curve cryptography (ECC). It implements the curve equation **Ep(a, b): y² = x³ + ax + b (mod p)** and all necessary point operations.

## Features

- ✅ Complete elliptic curve point arithmetic
- ✅ Support for point addition and point doubling
- ✅ Efficient scalar multiplication using double-and-add algorithm
- ✅ Modular inverse computation using Extended Euclidean Algorithm
- ✅ Abelian group properties verification

## Mathematical Background

### Elliptic Curve Definition

An elliptic curve over a prime field Fp is defined by the equation:

```
y² = x³ + ax + b (mod p)
```

Where:
- `p` is a large prime number (the field modulus)
- `a`, `b` are curve parameters
- The discriminant Δ = 4a³ + 27b² ≠ 0 (mod p)

### Point Operations

#### 1. Point Addition (P + Q)

For two distinct points P = (xp, yp) and Q = (xq, yq):

```
d = (yq - yp) / (xq - xp) (mod p)
xr = d² - xp - xq (mod p)
yr = d(xp - xr) - yp (mod p)
```

#### 2. Point Doubling (P + P = 2P)

For a point P = (xp, yp):

```
d = (3xp² + a) / (2yp) (mod p)
xr = d² - 2xp (mod p)
yr = d(xp - xr) - yp (mod p)
```

#### 3. Scalar Multiplication (k × P)

Computed using the **double-and-add** algorithm:
- Convert k to binary representation
- For each bit from left to right:
  - Double the current result
  - If bit is 1, add P

Time complexity: O(log k)

### Abelian Group Properties

The set of points on an elliptic curve forms an abelian group with the following properties:

1. **Closure**: If P and Q are on the curve, then P + Q is also on the curve
2. **Associativity**: (P + Q) + R = P + (Q + R)
3. **Identity**: There exists a point O (point at infinity) such that P + O = P
4. **Inverse**: For every point P, there exists -P such that P + (-P) = O
5. **Commutativity**: P + Q = Q + P

## Classes

### `ECPoint`

Represents a point on an elliptic curve.

#### Constructor

```python
ECPoint(x, y, curve)
```

**Parameters:**
- `x`: x-coordinate (integer or None for point at infinity)
- `y`: y-coordinate (integer or None for point at infinity)
- `curve`: EllipticCurve instance the point belongs to

**Raises:**
- `ValueError`: If the point is not on the curve

#### Methods

##### `is_infinity()`
Check if this point is the point at infinity (identity element).

**Returns:** `bool`

##### `__eq__(other)`
Check equality between two points.

**Returns:** `bool`

##### `__neg__()`
Return the inverse point: (x, y) → (x, -y mod p).

**Returns:** `ECPoint`

##### `__add__(other)`
Elliptic curve point addition.

**Parameters:**
- `other`: ECPoint to add

**Returns:** `ECPoint` - The sum of the two points

**Raises:**
- `ValueError`: If points are not on the same curve

##### `__mul__(scalar)`
Scalar multiplication using double-and-add algorithm.

**Parameters:**
- `scalar`: Integer multiplier

**Returns:** `ECPoint` - Result of scalar × point

**Example:**
```python
# Compute 5P
result = 5 * P
# or
result = P * 5
```

### `EllipticCurve`

Represents an elliptic curve over a prime field.

#### Constructor

```python
EllipticCurve(a, b, p)
```

**Parameters:**
- `a`: Curve parameter a
- `b`: Curve parameter b
- `p`: Prime modulus

**Raises:**
- `ValueError`: If discriminant is zero (invalid curve)

#### Methods

##### `is_on_curve(x, y)`
Check whether a point (x, y) lies on the curve.

**Parameters:**
- `x`: x-coordinate
- `y`: y-coordinate

**Returns:** `bool`

##### `multiplicative_inverse(a)`
Compute modular multiplicative inverse using Extended Euclidean Algorithm.

**Parameters:**
- `a`: Integer to find inverse of

**Returns:** `int` - a⁻¹ mod p

**Raises:**
- `ValueError`: If a has no inverse under mod p

##### `ECPoint(x, y)`
Create a point on this curve.

**Parameters:**
- `x`: x-coordinate
- `y`: y-coordinate

**Returns:** `ECPoint`

##### `infinity()`
Return the point at infinity (identity element).

**Returns:** `ECPoint`

## Usage Examples

### Basic Point Operations

```python
from elliptic_curve import EllipticCurve, ECPoint

# Define curve y² = x³ + 7 (mod 23)
curve = EllipticCurve(a=0, b=7, p=23)

# Create points
P = curve.ECPoint(3, 10)
Q = curve.ECPoint(9, 7)

# Point addition
R = P + Q
print(f"P + Q = {R}")

# Point doubling
S = P + P
print(f"2P = {S}")

# Scalar multiplication
T = 5 * P
print(f"5P = {T}")

# Point negation
neg_P = -P
print(f"-P = {neg_P}")

# Verify inverse property
O = P + (-P)
print(f"P + (-P) is infinity: {O.is_infinity()}")
```

### Working with Standard Curves

```python
# secp256k1 (Bitcoin's curve)
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
a = 0
b = 7

curve = EllipticCurve(a, b, p)

# Generator point
Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
G = curve.ECPoint(Gx, Gy)

# Generate public key from private key
private_key = 12345
public_key = private_key * G
print(f"Public Key: {public_key}")
```

### Verifying Abelian Group Properties

```python
# Closure
R = P + Q
assert curve.is_on_curve(R.x, R.y), "Closure property failed"

# Associativity
S = curve.ECPoint(13, 16)
assert (P + Q) + S == P + (Q + S), "Associativity failed"

# Identity
O = curve.infinity()
assert P + O == P, "Identity property failed"

# Inverse
assert (P + (-P)).is_infinity(), "Inverse property failed"

# Commutativity
assert P + Q == Q + P, "Commutativity failed"
```

## Implementation Details

### Extended Euclidean Algorithm

Used for computing modular multiplicative inverse:

```python
def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y
```

This algorithm finds integers x and y such that:
```
ax + by = gcd(a, b)
```

When gcd(a, p) = 1, we have ax ≡ 1 (mod p), so x is the modular inverse.

### Double-and-Add Algorithm

Efficient scalar multiplication in O(log k) time:

```python
def scalar_multiply(k, P):
    result = O  # Point at infinity
    addend = P
    
    while k:
        if k & 1:  # If least significant bit is 1
            result = result + addend
        addend = addend + addend  # Point doubling
        k >>= 1  # Shift right
    
    return result
```

## Performance Considerations

- **Point Addition**: O(1) - Constant time modular arithmetic
- **Scalar Multiplication**: O(log k) - Using double-and-add
- **Modular Inverse**: O(log p) - Using extended Euclidean algorithm

For cryptographic applications with 256-bit curves:
- Point addition: ~0.1 ms
- Scalar multiplication: ~10-50 ms (depending on scalar size)

## Security Notes

⚠️ **This implementation is for educational purposes.**

For production use:
- Use constant-time operations to prevent timing attacks
- Implement proper side-channel attack countermeasures
- Use battle-tested libraries like `cryptography` or `ecdsa`
- Validate all inputs rigorously
- Use secure random number generation

## References

- [Guide to Elliptic Curve Cryptography](https://www.springer.com/gp/book/9780387952734) by Hankerson, Menezes, and Vanstone
- [SEC 2: Recommended Elliptic Curve Domain Parameters](https://www.secg.org/sec2-v2.pdf)
- [NIST FIPS 186-4: Digital Signature Standard](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.186-4.pdf)
- [An Efficient Double Parameter Elliptic Curve Digital Signature Algorithm for Blockchain](https://ieeexplore.ieee.org/document/9438692)
(The last one is the one I just read on this week)