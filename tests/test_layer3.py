"""Layer 3 tests: Data Structures (Transaction, Block, Merkle Tree)."""

import pytest
import shutil
from pathlib import Path

from blockchain_types.wallet import Wallet
from blockchain_types.transaction import Transaction
from blockchain_types.transaction_merkle_tree import TransactionMerkleTree
from blockchain_types.block import Block
from tools.instant_maker import InstantMaker


class TestTransaction:
    """Test Transaction class."""
    
    def test_transaction_creation(self):
        """Test transaction creation."""
        tx = Transaction(
            sender="Alice",
            receiver="Bob",
            amount=100.0,
            fee=1.0,
            timestamp=123456789,
            message="Test",
            signature="sig123"
        )
        
        assert tx.get_sender() == "Alice"
        assert tx.get_receiver() == "Bob"
        assert tx.get_amount() == 100.0
        assert tx.get_fee() == 1.0
        assert tx.get_timestamp() == 123456789
        assert tx.get_message() == "Test"
        assert tx.get_signature() == "sig123"
    
    def test_transaction_default_timestamp(self):
        """Test transaction with automatic timestamp."""
        tx = Transaction(sender="Alice", receiver="Bob", amount=100.0)
        assert tx.get_timestamp() > 0
    
    def test_transaction_serialization(self):
        """Test transaction serialization to Base64."""
        tx = Transaction(
            sender="Alice",
            receiver="Bob",
            amount=100.0,
            fee=1.0,
            timestamp=123456789,
            message="Test",
            signature="sig123"
        )
        
        b64 = tx.to_base64()
        assert isinstance(b64, str)
        assert "Transaction [" in b64
    
    def test_transaction_deserialization(self):
        """Test transaction deserialization from Base64."""
        tx1 = Transaction(
            sender="Alice",
            receiver="Bob",
            amount=100.0,
            fee=1.0,
            timestamp=123456789,
            message="Test",
            signature="sig123"
        )
        
        b64 = tx1.to_base64()
        tx2 = Transaction(b64_encoded_string=b64)
        
        assert tx2.get_sender() == "Alice"
        assert tx2.get_receiver() == "Bob"
        assert tx2.get_amount() == 100.0
        assert tx2.get_fee() == 1.0
        assert tx2.get_timestamp() == 123456789
        assert tx2.get_message() == "Test"
        assert tx2.get_signature() == "sig123"
    
    def test_transaction_hash(self):
        """Test transaction hash calculation."""
        tx = Transaction(sender="Alice", receiver="Bob", amount=100.0)
        hash_value = tx.to_hash()
        
        assert isinstance(hash_value, str)
        assert len(hash_value) == 64  # SHA3-256 produces 64 hex characters
    
    def test_transaction_hash_consistency(self):
        """Test that same transaction produces same hash."""
        tx1 = Transaction(
            sender="Alice",
            receiver="Bob",
            amount=100.0,
            fee=1.0,
            timestamp=123456789
        )
        tx2 = Transaction(
            sender="Alice",
            receiver="Bob",
            amount=100.0,
            fee=1.0,
            timestamp=123456789
        )
        
        assert tx1.to_hash() == tx2.to_hash()
    
    def test_transaction_content_only_hash(self):
        """Test transaction hash without signature."""
        tx = Transaction(
            sender="Alice",
            receiver="Bob",
            amount=100.0,
            signature="sig123"
        )
        
        hash_with_sig = tx.to_hash()
        hash_without_sig = tx.to_hash_with_content_only()
        
        # Should be different
        assert hash_with_sig != hash_without_sig


class TestTransactionMerkleTree:
    """Test TransactionMerkleTree class."""
    
    def test_merkle_tree_empty(self):
        """Test Merkle tree with no transactions."""
        tree = TransactionMerkleTree([])
        root = tree.get_merkle_root()
        
        # Should return hash of empty string
        assert isinstance(root, str)
        assert len(root) == 64
    
    def test_merkle_tree_single_transaction(self):
        """Test Merkle tree with one transaction."""
        tx = Transaction(sender="Alice", receiver="Bob", amount=100.0)
        tree = TransactionMerkleTree([tx])
        root = tree.get_merkle_root()
        
        # Root should be hash of the transaction
        assert root == tx.to_hash()
    
    def test_merkle_tree_multiple_transactions(self):
        """Test Merkle tree with multiple transactions."""
        tx1 = Transaction(sender="Alice", receiver="Bob", amount=100.0, timestamp=1)
        tx2 = Transaction(sender="Bob", receiver="Charlie", amount=50.0, timestamp=2)
        tx3 = Transaction(sender="Charlie", receiver="Alice", amount=25.0, timestamp=3)
        
        tree = TransactionMerkleTree([tx1, tx2, tx3])
        root = tree.get_merkle_root()
        
        assert isinstance(root, str)
        assert len(root) == 64
    
    def test_merkle_tree_consistency(self):
        """Test that same transactions produce same Merkle root."""
        tx1 = Transaction(sender="Alice", receiver="Bob", amount=100.0, timestamp=1)
        tx2 = Transaction(sender="Bob", receiver="Charlie", amount=50.0, timestamp=2)
        
        tree1 = TransactionMerkleTree([tx1, tx2])
        tree2 = TransactionMerkleTree([tx1, tx2])
        
        assert tree1.get_merkle_root() == tree2.get_merkle_root()
    
    def test_merkle_tree_order_matters(self):
        """Test that transaction order affects Merkle root."""
        tx1 = Transaction(sender="Alice", receiver="Bob", amount=100.0, timestamp=1)
        tx2 = Transaction(sender="Bob", receiver="Charlie", amount=50.0, timestamp=2)
        
        tree1 = TransactionMerkleTree([tx1, tx2])
        tree2 = TransactionMerkleTree([tx2, tx1])
        
        # Different order should produce different root
        assert tree1.get_merkle_root() != tree2.get_merkle_root()


class TestBlock:
    """Test Block class."""
    
    def test_block_creation(self):
        """Test block creation."""
        block = Block(
            previous_hash="0",
            hash_value="abc123",
            difficulty=1,
            nonce=42,
            timestamp=123456789,
            miner="Alice",
            miner_rewards=10.0
        )
        assert block.get_previous_hash() == "0"
        assert block.get_hash() == "abc123"
        assert block.get_difficulty() == 1
        assert block.get_nonce() == 42
        assert block.get_timestamp() == 123456789
        assert block.get_miner() == "Alice"
        assert block.get_miner_rewards() == 10.0
    
    def test_block_default_timestamp(self):
        """Test block with automatic timestamp."""
        block = Block()
        assert block.get_timestamp() > 0
    
    def test_block_add_transaction(self):
        """Test adding transaction to block."""
        block = Block()
        tx = Transaction(sender="Alice", receiver="Bob", amount=100.0)
        
        assert block.add_transaction(tx) is True
        assert len(block.get_transactions()) == 1
    
    def test_block_add_duplicate_transaction(self):
        """Test that duplicate transaction is rejected."""
        block = Block()
        tx1 = Transaction(sender="Alice", receiver="Bob", amount=100.0, timestamp=123)
        tx2 = Transaction(sender="Alice", receiver="Bob", amount=100.0, timestamp=123)
        
        assert block.add_transaction(tx1) is True
        assert block.add_transaction(tx2) is False  # Duplicate
        assert len(block.get_transactions()) == 1
    
    def test_block_delete_transaction_by_index(self):
        """Test deleting transaction by index."""
        block = Block()
        tx1 = Transaction(sender="Alice", receiver="Bob", amount=100.0, timestamp=1)
        tx2 = Transaction(sender="Bob", receiver="Charlie", amount=50.0, timestamp=2)
        
        block.add_transaction(tx1)
        block.add_transaction(tx2)
        
        assert len(block.get_transactions()) == 2
        assert block.del_transaction(location=0) is True
        assert len(block.get_transactions()) == 1
    
    def test_block_delete_transaction_by_object(self):
        """Test deleting transaction by object."""
        block = Block()
        tx1 = Transaction(sender="Alice", receiver="Bob", amount=100.0, timestamp=1)
        tx2 = Transaction(sender="Bob", receiver="Charlie", amount=50.0, timestamp=2)
        
        block.add_transaction(tx1)
        block.add_transaction(tx2)
        
        assert block.del_transaction(bad_transaction=tx1) is True
        assert len(block.get_transactions()) == 1
    
    def test_block_merkle_root(self):
        """Test Merkle root calculation."""
        block = Block()
        tx1 = Transaction(sender="Alice", receiver="Bob", amount=100.0, timestamp=1)
        tx2 = Transaction(sender="Bob", receiver="Charlie", amount=50.0, timestamp=2)
        
        block.add_transaction(tx1)
        block.add_transaction(tx2)
        
        merkle_root = block.get_merkle_root()
        
        # Verify it matches manually calculated Merkle tree
        tree = TransactionMerkleTree([tx1, tx2])
        assert merkle_root == tree.get_merkle_root()
    
    def test_block_serialization(self):
        """Test block serialization to Base64."""
        block = Block(
            previous_hash="0",
            hash_value="abc123",
            difficulty=1,
            nonce=42,
            timestamp=123456789,
            miner="Alice",
            miner_rewards=10.0
        )
        
        b64 = block.to_base64()
        assert isinstance(b64, str)
        assert "Block [" in b64
    
    def test_block_deserialization(self):
        """Test block deserialization from Base64."""
        tx = Transaction(sender="Alice", receiver="Bob", amount=100.0, timestamp=123)
        
        block1 = Block(
            previous_hash="0",
            hash_value="abc123",
            difficulty=1,
            nonce=42,
            timestamp=123456789,
            miner="Alice",
            miner_rewards=10.0
        )
        block1.add_transaction(tx)
        
        b64 = block1.to_base64()
        block2 = Block(b64_encoded_block=b64)
        
        assert block2.get_previous_hash() == "0"
        assert block2.get_hash() == "abc123"
        assert block2.get_difficulty() == 1
        assert block2.get_nonce() == 42
        assert block2.get_timestamp() == 123456789
        assert block2.get_miner() == "Alice"
        assert block2.get_miner_rewards() == 10.0
        assert len(block2.get_transactions()) == 1
    
    def test_block_hash(self):
        """Test block hash calculation."""
        block = Block(previous_hash="0", difficulty=1)
        hash_value = block.to_hash()
        
        assert isinstance(hash_value, str)
        assert len(hash_value) == 64
    
    def test_block_hash_consistency(self):
        """Test that same block produces same hash."""
        block1 = Block(
            previous_hash="0",
            difficulty=1,
            nonce=42,
            timestamp=123456789
        )
        block2 = Block(
            previous_hash="0",
            difficulty=1,
            nonce=42,
            timestamp=123456789
        )
        
        assert block1.to_hash_with_content_only() == block2.to_hash_with_content_only()
    
    def test_block_content_only_hash(self):
        """Test block hash without hash field."""
        block = Block(
            previous_hash="0",
            hash_value="some_hash",
            difficulty=1
        )
        
        hash_with_field = block.to_hash()
        hash_without_field = block.to_hash_with_content_only()
        
        # Should be different
        assert hash_with_field != hash_without_field


class TestIntegration:
    """Integration tests with wallet."""
    
    def setup_method(self):
        """Setup: Clean up wallets directory."""
        wallets_dir = Path("wallets")
        if wallets_dir.exists():
            shutil.rmtree(wallets_dir)
    
    def teardown_method(self):
        """Teardown: Clean up wallets directory."""
        wallets_dir = Path("wallets")
        if wallets_dir.exists():
            shutil.rmtree(wallets_dir)
    
    def test_signed_transaction(self):
        """Test creating and verifying signed transaction."""
        from tools.security import Security
        
        wallet = Wallet("Alice")
        
        tx = Transaction(
            sender=wallet.get_account(),
            receiver="Bob",
            amount=100.0,
            fee=1.0
        )
        
        # Sign transaction
        signature = wallet.sign(tx.to_base64_with_content_only())
        tx.set_signature(signature)
        
        # Verify signature
        is_valid = Security.is_signature_valid(
            tx.get_sender(),
            tx.to_base64_with_content_only(),
            tx.get_signature()
        )
        
        assert is_valid is True
    
    def test_block_with_signed_transactions(self):
        """Test block with multiple signed transactions."""
        from tools.security import Security
        
        alice = Wallet("Alice")
        bob = Wallet("Bob")
        
        # Create transactions
        tx1 = Transaction(
            sender=alice.get_account(),
            receiver=bob.get_account(),
            amount=100.0,
            fee=1.0
        )
        tx1.set_signature(alice.sign(tx1.to_base64_with_content_only()))
        
        tx2 = Transaction(
            sender=bob.get_account(),
            receiver=alice.get_account(),
            amount=50.0,
            fee=0.5
        )
        tx2.set_signature(bob.sign(tx2.to_base64_with_content_only()))
        
        # Create block
        block = Block(previous_hash="0", difficulty=1)
        block.add_transaction(tx1)
        block.add_transaction(tx2)
        
        # Verify all signatures
        for tx in block.get_transactions():
            is_valid = Security.is_signature_valid(
                tx.get_sender(),
                tx.to_base64_with_content_only(),
                tx.get_signature()
            )
            assert is_valid is True
    
    def test_block_serialization_with_transactions(self):
        """Test block serialization and deserialization with transactions."""
        wallet = Wallet("Alice")
        
        tx = Transaction(
            sender=wallet.get_account(),
            receiver="Bob",
            amount=100.0
        )
        tx.set_signature(wallet.sign(tx.to_base64_with_content_only()))
        
        block1 = Block(previous_hash="0", difficulty=1, miner=wallet.get_account())
        block1.add_transaction(tx)
        
        # Serialize and deserialize
        b64 = block1.to_base64()
        block2 = Block(b64_encoded_block=b64)
        
        # Verify transaction is preserved
        assert len(block2.get_transactions()) == 1
        tx2 = block2.get_transactions()[0]
        assert tx2.get_sender() == wallet.get_account()
        assert tx2.get_amount() == 100.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])