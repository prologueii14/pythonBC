#!/usr/bin/env python3
"""
Test script to verify ECDSA integration with the blockchain.
"""

import sys
import os

# Add the current directory to the path
sys.path.append(os.path.dirname(__file__))

from blockchain_types.wallet import Wallet
from blockchain_types.transaction import Transaction
from tools.security import Security
from tools.io import IO


def test_wallet_creation():
    """Test ECDSA wallet creation and key generation."""
    print("=== Testing ECDSA Wallet Creation ===")

    try:
        wallet = Wallet("test_ecdsa_wallet")
        print(f"✓ Wallet created successfully: {wallet.get_name()}")

        account = wallet.get_account()
        print(f"✓ Account address generated: {account[:50]}...")

        return wallet
    except Exception as e:
        print(f"✗ Wallet creation failed: {e}")
        return None


def test_signing_and_verification(wallet):
    """Test ECDSA signing and verification."""
    print("\n=== Testing ECDSA Signing and Verification ===")

    if wallet is None:
        print("✗ Cannot test signing: wallet is None")
        return False

    try:
        # Test data
        test_data = "Hello, ECDSA Blockchain!"
        print(f"Data to sign: {test_data}")

        # Sign the data
        signature = wallet.sign(test_data)
        print(f"✓ Data signed successfully")
        print(f"Signature: {signature[:50]}...")

        # Verify the signature
        account = wallet.get_account()
        is_valid = Security.is_signature_valid(account, test_data, signature)
        print(f"✓ Signature verification: {'Valid' if is_valid else 'Invalid'}")

        # Test with tampered data
        tampered_data = "Hello, ECDSA Blockchain?"
        is_tampered_valid = Security.is_signature_valid(account, tampered_data, signature)
        print(f"✓ Tampered data verification: {'Valid' if is_tampered_valid else 'Invalid'}")

        return is_valid and not is_tampered_valid
    except Exception as e:
        print(f"✗ Signing/verification failed: {e}")
        return False


def test_transaction_signing():
    """Test transaction signing with ECDSA."""
    print("\n=== Testing Transaction Signing ===")

    try:
        # Create wallets
        sender_wallet = Wallet("sender_test")
        receiver_wallet = Wallet("receiver_test")

        # Create transaction
        transaction = Transaction(
            sender=sender_wallet.get_account(),
            receiver=receiver_wallet.get_account(),
            amount=10.5,
            fee=0.1,
            message="Test ECDSA transaction"
        )

        print(f"✓ Transaction created")
        print(f"Sender: {transaction.get_sender()[:50]}...")
        print(f"Receiver: {transaction.get_receiver()[:50]}...")
        print(f"Amount: {transaction.get_amount()}")

        # Sign transaction
        data_to_sign = transaction.to_base64_with_content_only()
        signature = sender_wallet.sign(data_to_sign)
        transaction.set_signature(signature)

        print(f"✓ Transaction signed")
        print(f"Signature: {signature[:50]}...")

        # Verify transaction signature
        is_valid = Security.is_signature_valid(
            transaction.get_sender(),
            transaction.to_base64_with_content_only(),
            transaction.get_signature()
        )

        print(f"✓ Transaction signature verification: {'Valid' if is_valid else 'Invalid'}")

        return is_valid
    except Exception as e:
        print(f"✗ Transaction signing failed: {e}")
        return False


def test_deterministic_signatures():
    """Test RFC 6979 deterministic signatures."""
    print("\n=== Testing RFC 6979 Deterministic Signatures ===")

    try:
        wallet = Wallet("deterministic_test")
        test_data = "Deterministic signature test"

        # Sign the same data multiple times
        signature1 = wallet.sign(test_data)
        signature2 = wallet.sign(test_data)
        signature3 = wallet.sign(test_data)

        print(f"✓ Generated 3 signatures for the same data")
        print(f"Signature 1: {signature1[:50]}...")
        print(f"Signature 2: {signature2[:50]}...")
        print(f"Signature 3: {signature3[:50]}...")

        # Check if signatures are identical (should be with RFC 6979)
        signatures_match = (signature1 == signature2 == signature3)
        print(f"✓ Signatures are {'identical' if signatures_match else 'different'}")
        print(f"  RFC 6979 deterministic signing: {'Working' if signatures_match else 'Not working'}")

        # Verify all signatures
        account = wallet.get_account()
        valid1 = Security.is_signature_valid(account, test_data, signature1)
        valid2 = Security.is_signature_valid(account, test_data, signature2)
        valid3 = Security.is_signature_valid(account, test_data, signature3)

        all_valid = valid1 and valid2 and valid3
        print(f"✓ All signatures valid: {all_valid}")

        return signatures_match and all_valid
    except Exception as e:
        print(f"✗ Deterministic signature test failed: {e}")
        return False


def test_key_persistence():
    """Test key persistence and loading."""
    print("\n=== Testing Key Persistence ===")

    try:
        # Create wallet and get account
        wallet_name = "persistence_test"
        wallet1 = Wallet(wallet_name)
        account1 = wallet1.get_account()

        print(f"✓ First wallet created: {account1[:50]}...")

        # Create another wallet with same name (should load existing keys)
        wallet2 = Wallet(wallet_name)
        account2 = wallet2.get_account()

        print(f"✓ Second wallet loaded: {account2[:50]}...")

        # Check if accounts match
        accounts_match = (account1 == account2)
        print(f"✓ Accounts match: {accounts_match}")

        # Test signing with both wallets
        test_data = "Key persistence test"
        signature1 = wallet1.sign(test_data)
        signature2 = wallet2.sign(test_data)

        # Verify cross-wallet signature validation
        valid_cross1 = Security.is_signature_valid(account2, test_data, signature1)
        valid_cross2 = Security.is_signature_valid(account1, test_data, signature2)

        print(f"✓ Cross-wallet signature validation: {valid_cross1 and valid_cross2}")

        return accounts_match and valid_cross1 and valid_cross2
    except Exception as e:
        print(f"✗ Key persistence test failed: {e}")
        return False


def cleanup_test_files():
    """Clean up test wallet files."""
    import shutil

    test_wallets = [
        "test_ecdsa_wallet",
        "sender_test",
        "receiver_test",
        "deterministic_test",
        "persistence_test"
    ]

    for wallet_name in test_wallets:
        wallet_dir = os.path.join("wallets", wallet_name)
        if os.path.exists(wallet_dir):
            try:
                shutil.rmtree(wallet_dir)
                print(f"✓ Cleaned up {wallet_name}")
            except Exception as e:
                print(f"✗ Failed to clean up {wallet_name}: {e}")


def main():
    """Run all ECDSA integration tests."""
    print("ECDSA Integration Test for PythonBC Blockchain")
    print("=" * 60)

    # Track test results
    results = []

    # Test 1: Wallet Creation
    wallet = test_wallet_creation()
    results.append(wallet is not None)

    # Test 2: Signing and Verification
    results.append(test_signing_and_verification(wallet))

    # Test 3: Transaction Signing
    results.append(test_transaction_signing())

    # Test 4: Deterministic Signatures
    results.append(test_deterministic_signatures())

    # Test 5: Key Persistence
    results.append(test_key_persistence())

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    test_names = [
        "Wallet Creation",
        "Signing & Verification",
        "Transaction Signing",
        "Deterministic Signatures",
        "Key Persistence"
    ]

    passed = 0
    for i, (name, result) in enumerate(zip(test_names, results), 1):
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{i}. {name:<25} {status}")
        if result:
            passed += 1

    print("-" * 60)
    print(f"Results: {passed}/{len(results)} tests passed")

    if passed == len(results):
        print("All tests passed! ECDSA integration is working correctly.")
    else:
        print("Some tests failed. Please check the implementation.")

    # Clean up test files
    print("\nCleaning up test files...")
    cleanup_test_files()

    return passed == len(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
