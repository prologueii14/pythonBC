# -*- encoding: utf-8 -*-
"""
Performance Benchmark Main Program:
Compares the performance of standard ECDSA (ecdsa.py) and the paper's DPECDSA (dpecdsa.py).
"""

import timeit
from ecdsa import StandardCurves as ECDSA_Curves
from dpecdsa import StandardCurves as DPECDSA_Curves


BENCHMARK_ROUNDS = 100  # Number of times to run each operation
CURVE_TO_TEST = "secp256k1" # Use secp256k1 for the test
TEST_MESSAGE = b"This is a benchmark message for comparing ECDSA implementations."


def run_benchmark():
    """Run the signing and verification performance benchmark"""
    
    print("=== Algorithm Performance Comparison ===")
    print(f"Curve: {CURVE_TO_TEST}")
    print(f"Test Rounds: {BENCHMARK_ROUNDS}")
    print(f"Test Message: {TEST_MESSAGE.decode('utf-8')}\n")
    print("="*50)

    # --- 1. Initialization ---
    print("Initializing algorithms and generating keypair...")
    
    if CURVE_TO_TEST == "secp256k1":
        ecdsa_std = ECDSA_Curves.secp256k1()
        dpecdsa_paper = DPECDSA_Curves.secp256k1()
    else:
        print("ERROR: Test not configured for this curve.")
        return

    # Generate a shared keypair
    private_key, public_key = ecdsa_std.generate_keypair()
    
    # Sign once beforehand to get signatures needed for verification benchmark
    sig_std = ecdsa_std.sign(TEST_MESSAGE, private_key, deterministic=True)
    sig_paper = dpecdsa_paper.sign(TEST_MESSAGE, private_key)
    
    print("Initialization complete.")
    print("="*50)

    # --- 2. Benchmark Signing ---
    print(f"Testing Signing performance ({BENCHMARK_ROUNDS} rounds each)...")
    
    # Test standard ECDSA (RFC 6979)
    ecdsa_sign_time = timeit.timeit(
        lambda: ecdsa_std.sign(TEST_MESSAGE, private_key, deterministic=True),
        number=BENCHMARK_ROUNDS
    )
    
    # Test paper's DPECDSA
    dpecdsa_sign_time = timeit.timeit(
        lambda: dpecdsa_paper.sign(TEST_MESSAGE, private_key),
        number=BENCHMARK_ROUNDS
    )
    
    avg_ecdsa_sign = (ecdsa_sign_time / BENCHMARK_ROUNDS) * 1000  # convert to milliseconds
    avg_dpecdsa_sign = (dpecdsa_sign_time / BENCHMARK_ROUNDS) * 1000 # convert to milliseconds
    
    print("\n--- Signing Results ---")
    print(f"Standard ECDSA  : {avg_ecdsa_sign:.6f} ms/op")
    print(f"Paper DPECDSA: {avg_dpecdsa_sign:.6f} ms/op")
    
    if avg_dpecdsa_sign < avg_ecdsa_sign:
        diff = (avg_ecdsa_sign - avg_dpecdsa_sign) / avg_ecdsa_sign
        print(f"-> Paper's algorithm is {diff:.2%} faster at Signing")
    else:
        diff = (avg_dpecdsa_sign - avg_ecdsa_sign) / avg_ecdsa_sign
        print(f"-> Paper's algorithm is {diff:.2%} slower at Signing")
        
    print("="*50)

    # --- 3. Benchmark Verification ---
    print(f"Testing Verification performance ({BENCHMARK_ROUNDS} rounds each)...")
    
    # Test standard ECDSA verification
    ecdsa_verify_time = timeit.timeit(
        lambda: ecdsa_std.verify(TEST_MESSAGE, sig_std, public_key),
        number=BENCHMARK_ROUNDS
    )
    
    # Test paper's DPECDSA verification
    dpecdsa_verify_time = timeit.timeit(
        lambda: dpecdsa_paper.verify(TEST_MESSAGE, sig_paper, public_key),
        number=BENCHMARK_ROUNDS
    )
    
    avg_ecdsa_verify = (ecdsa_verify_time / BENCHMARK_ROUNDS) * 1000  # convert to milliseconds
    avg_dpecdsa_verify = (dpecdsa_verify_time / BENCHMARK_ROUNDS) * 1000 # convert to milliseconds
    
    print("\n--- Verification Results ---")
    print(f"Standard ECDSA  : {avg_ecdsa_verify:.6f} ms/op")
    print(f"Paper DPECDSA: {avg_dpecdsa_verify:.6f} ms/op")
    
    if avg_dpecdsa_verify < avg_ecdsa_verify:
        diff = (avg_ecdsa_verify - avg_dpecdsa_verify) / avg_ecdsa_verify
        print(f"-> Paper's algorithm is {diff:.2%} faster at Verification")
    else:
        diff = (avg_dpecdsa_verify - avg_ecdsa_verify) / avg_ecdsa_verify
        print(f"-> Paper's algorithm is {diff:.2%} slower at Verification")
        
    print("="*50)

if __name__ == "__main__":
    run_benchmark()