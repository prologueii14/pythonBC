"""Layer 2 tests: Cryptography (Wallet and Security)."""

import pytest
import shutil
from pathlib import Path

from blockchain_types.wallet import Wallet
from tools.security import Security


class TestWallet:
    """Test Wallet class."""
    
    def setup_method(self):
        """Setup: Clean up wallets directory before each test."""
        wallets_dir = Path("wallets")
        if wallets_dir.exists():
            shutil.rmtree(wallets_dir)
    
    def teardown_method(self):
        """Teardown: Clean up wallets directory after each test."""
        wallets_dir = Path("wallets")
        if wallets_dir.exists():
            shutil.rmtree(wallets_dir)
    
    def test_wallet_creation(self):
        """Test wallet creation."""
        wallet = Wallet("TestWallet")
        assert wallet is not None
        assert wallet.get_name() == "TestWallet"
    
    def test_wallet_key_generation(self):
        """Test that wallet generates keys."""
        wallet = Wallet("TestWallet")
        assert wallet.public_key is not None
        assert wallet.private_key is not None
    
    def test_wallet_key_persistence(self):
        """Test that keys are saved and can be loaded."""
        # Create wallet (generates keys)
        wallet1 = Wallet("TestWallet")
        account1 = wallet1.get_account()
        
        # Create another wallet with same name (should load existing keys)
        wallet2 = Wallet("TestWallet")
        account2 = wallet2.get_account()
        
        # Accounts should be identical
        assert account1 == account2
    
    def test_wallet_account_address(self):
        """Test account address generation."""
        wallet = Wallet("TestWallet")
        account = wallet.get_account()
        
        # Account should be a non-empty Base64 string
        assert isinstance(account, str)
        assert len(account) > 0
    
    def test_wallet_sign(self):
        """Test signing data."""
        wallet = Wallet("TestWallet")
        data = "Hello World"
        signature = wallet.sign(data)
        
        # Signature should be a non-empty Base64 string
        assert isinstance(signature, str)
        assert len(signature) > 0
    
    def test_different_data_different_signatures(self):
        """Test that different data produces different signatures."""
        wallet = Wallet("TestWallet")
        sig1 = wallet.sign("Hello")
        sig2 = wallet.sign("World")
        
        assert sig1 != sig2
    
    def test_same_data_same_signature(self):
        """Test that same data produces same signature."""
        wallet = Wallet("TestWallet")
        sig1 = wallet.sign("Hello World")
        sig2 = wallet.sign("Hello World")
        
        assert sig1 == sig2


class TestSecurity:
    """Test Security class."""
    
    def setup_method(self):
        """Setup: Clean up wallets directory before each test."""
        wallets_dir = Path("wallets")
        if wallets_dir.exists():
            shutil.rmtree(wallets_dir)
    
    def teardown_method(self):
        """Teardown: Clean up wallets directory after each test."""
        wallets_dir = Path("wallets")
        if wallets_dir.exists():
            shutil.rmtree(wallets_dir)
    
    def test_signature_validation_correct(self):
        """Test signature validation with correct signature."""
        wallet = Wallet("TestWallet")
        data = "Hello World"
        signature = wallet.sign(data)
        account = wallet.get_account()
        
        # Should validate successfully
        assert Security.is_signature_valid(account, data, signature) is True
    
    def test_signature_validation_wrong_data(self):
        """Test signature validation with wrong data."""
        wallet = Wallet("TestWallet")
        data = "Hello World"
        signature = wallet.sign(data)
        account = wallet.get_account()
        
        # Should fail with different data
        wrong_data = "Hello World!"
        assert Security.is_signature_valid(account, wrong_data, signature) is False
    
    def test_signature_validation_wrong_signature(self):
        """Test signature validation with wrong signature."""
        wallet = Wallet("TestWallet")
        data = "Hello World"
        account = wallet.get_account()
        
        # Create wrong signature
        wrong_signature = wallet.sign("Different Data")
        
        # Should fail with wrong signature
        assert Security.is_signature_valid(account, data, wrong_signature) is False
    
    def test_signature_validation_wrong_account(self):
        """Test signature validation with wrong account."""
        wallet1 = Wallet("Wallet1")
        wallet2 = Wallet("Wallet2")
        
        data = "Hello World"
        signature = wallet1.sign(data)
        
        # Should fail with different wallet's account
        assert Security.is_signature_valid(wallet2.get_account(), data, signature) is False
    
    def test_signature_validation_invalid_base64(self):
        """Test signature validation with invalid Base64."""
        wallet = Wallet("TestWallet")
        data = "Hello World"
        account = wallet.get_account()
        
        # Should fail with invalid signature
        assert Security.is_signature_valid(account, data, "invalid_signature!!!") is False
    
    def test_cross_wallet_verification(self):
        """Test that signature from one wallet can be verified with its account."""
        wallet1 = Wallet("Wallet1")
        wallet2 = Wallet("Wallet2")
        
        data = "Transaction Data"
        
        # Wallet1 signs
        sig1 = wallet1.sign(data)
        
        # Wallet2 signs
        sig2 = wallet2.sign(data)
        
        # Each wallet's signature should only validate with its own account
        assert Security.is_signature_valid(wallet1.get_account(), data, sig1) is True
        assert Security.is_signature_valid(wallet2.get_account(), data, sig2) is True
        assert Security.is_signature_valid(wallet1.get_account(), data, sig2) is False
        assert Security.is_signature_valid(wallet2.get_account(), data, sig1) is False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
