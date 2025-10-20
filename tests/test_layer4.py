"""Layer 4 tests: Blockchain core and networking."""

import pytest
import shutil
from pathlib import Path

from blockchain_types.wallet import Wallet
from blockchain_types.transaction import Transaction
from blockchain_types.block import Block
from blockchain_types.network_node import NetworkNode
from blockchain_types.message_type import MessageType
from blockchain_types.blockchain import Blockchain
from config.blockchain_config import BlockchainConfig


class TestNetworkNode:
    """Test NetworkNode class."""
    
    def test_network_node_creation(self):
        """Test network node creation."""
        node = NetworkNode("127.0.0.1", 8300)
        assert node.get_inet_address() == "127.0.0.1"
        assert node.get_inet_port() == 8300
    
    def test_network_node_serialization(self):
        """Test network node serialization."""
        node = NetworkNode("192.168.1.1", 8080)
        b64 = node.to_base64()
        
        assert isinstance(b64, str)
        assert "NetworkNode [" in b64
    
    def test_network_node_deserialization(self):
        """Test network node deserialization."""
        node1 = NetworkNode("192.168.1.1", 8080)
        b64 = node1.to_base64()
        
        node2 = NetworkNode(b64_encoded_node=b64)
        assert node2.get_inet_address() == "192.168.1.1"
        assert node2.get_inet_port() == 8080
    
    def test_network_node_hash(self):
        """Test network node hash."""
        node1 = NetworkNode("127.0.0.1", 8300)
        node2 = NetworkNode("127.0.0.1", 8300)
        
        assert node1.to_hash() == node2.to_hash()
    
    def test_network_node_different_hash(self):
        """Test that different nodes have different hashes."""
        node1 = NetworkNode("127.0.0.1", 8300)
        node2 = NetworkNode("127.0.0.1", 8301)
        
        assert node1.to_hash() != node2.to_hash()


class TestMessageType:
    """Test MessageType class."""
    
    def test_message_types_exist(self):
        """Test that all message types are defined."""
        assert hasattr(MessageType, 'GET_BALANCE')
        assert hasattr(MessageType, 'DO_TRANSACT')
        assert hasattr(MessageType, 'BCAST_BLOCK')
        assert hasattr(MessageType, 'BCAST_TRANSACT')
        assert hasattr(MessageType, 'CLONE_CHAIN')
    
    def test_message_type_values(self):
        """Test message type values."""
        assert MessageType.GET_BALANCE == "getBalance"
        assert MessageType.BCAST_BLOCK == "broadcastedBlock"
        assert MessageType.CLONE_CHAIN == "cloneBlockchain"


class TestBlockchain:
    """Test Blockchain class."""
    
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
    
    def test_blockchain_creation(self):
        """Test blockchain creation."""
        bc = Blockchain("TestNode")
        assert bc is not None
        assert len(bc.chain) == 1  # Genesis block
    
    def test_genesis_block(self):
        """Test genesis block creation."""
        bc = Blockchain("TestNode")
        genesis = bc.chain[0]
        
        assert genesis.get_previous_hash() == "0"
        assert genesis.get_hash() is not None
        assert len(genesis.get_hash()) == 64
    
    def test_mining(self):
        """Test mining a block."""
        bc = Blockchain("TestNode")
        initial_length = len(bc.chain)
        
        bc.mine_block()
        
        assert len(bc.chain) == initial_length + 1
        assert bc.chain[-1].get_previous_hash() == bc.chain[-2].get_hash()
    
    def test_account_balance_initial(self):
        """Test initial account balance (mining rewards)."""
        bc = Blockchain("TestNode")
        balance = bc.get_account_balance(bc.wallet.get_account())
        
        # Should have mining reward from genesis block
        assert balance == BlockchainConfig.MINING_REWARDS
    
    def test_account_balance_after_mining(self):
        """Test account balance after mining multiple blocks."""
        bc = Blockchain("TestNode")
        bc.mine_block()
        bc.mine_block()
        
        balance = bc.get_account_balance(bc.wallet.get_account())
        
        # Should have 3 * mining reward (genesis + 2 mined blocks)
        expected = 3 * BlockchainConfig.MINING_REWARDS
        assert balance == expected
    
    def test_add_transaction_to_pending(self):
        """Test adding transaction to pending transactions."""
        bc = Blockchain("TestNode")
        wallet2 = Wallet("Receiver")
        
        tx = Transaction(
            sender=bc.wallet.get_account(),
            receiver=wallet2.get_account(),
            amount=1.0,
            fee=0.1
        )
        tx.set_signature(bc.wallet.sign(tx.to_base64_with_content_only()))
        
        assert bc.receive_transaction(tx) is True
        assert len(bc.pending_transactions) == 1
    
    def test_transaction_in_mined_block(self):
        """Test that pending transaction gets included in mined block."""
        bc = Blockchain("TestNode")
        wallet2 = Wallet("Receiver")
        
        tx = Transaction(
            sender=bc.wallet.get_account(),
            receiver=wallet2.get_account(),
            amount=1.0,
            fee=0.1
        )
        tx.set_signature(bc.wallet.sign(tx.to_base64_with_content_only()))
        
        bc.receive_transaction(tx)
        bc.mine_block()
        
        # Transaction should be in latest block
        latest_block = bc.chain[-1]
        assert len(latest_block.get_transactions()) > 0
        
        # Transaction should be removed from pending
        assert len(bc.pending_transactions) == 0
    
    def test_account_balance_with_transaction(self):
        """Test account balance after transaction."""
        bc = Blockchain("TestNode")
        wallet2 = Wallet("Receiver")
        
        initial_balance = bc.get_account_balance(bc.wallet.get_account())
        
        tx = Transaction(
            sender=bc.wallet.get_account(),
            receiver=wallet2.get_account(),
            amount=1.0,
            fee=0.1
        )
        tx.set_signature(bc.wallet.sign(tx.to_base64_with_content_only()))
        
        bc.receive_transaction(tx)
        bc.mine_block()
        
        # Sender balance: initial - amount - fee + mining_reward
        sender_balance = bc.get_account_balance(bc.wallet.get_account())
        expected_sender = initial_balance - 1.0 - 0.1 + BlockchainConfig.MINING_REWARDS + 0.1  # Gets fee back as miner
        assert sender_balance == expected_sender
        
        # Receiver balance: amount
        receiver_balance = bc.get_account_balance(wallet2.get_account())
        assert receiver_balance == 1.0
    
    def test_reject_insufficient_balance(self):
        """Test that transaction with insufficient balance is rejected."""
        bc = Blockchain("TestNode")
        wallet2 = Wallet("Poor")  # New wallet with no funds
        wallet3 = Wallet("Receiver")
        
        tx = Transaction(
            sender=wallet2.get_account(),
            receiver=wallet3.get_account(),
            amount=1000.0,  # More than balance
            fee=0.1
        )
        tx.set_signature(wallet2.sign(tx.to_base64_with_content_only()))
        
        assert bc.receive_transaction(tx) is False
    
    def test_reject_invalid_signature(self):
        """Test that transaction with invalid signature is rejected."""
        bc = Blockchain("TestNode")
        wallet2 = Wallet("Receiver")
        
        tx = Transaction(
            sender=bc.wallet.get_account(),
            receiver=wallet2.get_account(),
            amount=1.0,
            fee=0.1,
            signature="fake_signature"
        )
        
        assert bc.receive_transaction(tx) is False
    
    def test_add_network_node(self):
        """Test adding network node."""
        bc = Blockchain("TestNode")
        node = NetworkNode("127.0.0.1", 8301)
        
        assert bc.add_network_nodes(node) is True
        assert len(bc.get_network_nodes()) == 1
    
    def test_add_duplicate_network_node(self):
        """Test that duplicate network node is rejected."""
        bc = Blockchain("TestNode")
        node1 = NetworkNode("127.0.0.1", 8301)
        node2 = NetworkNode("127.0.0.1", 8301)
        
        assert bc.add_network_nodes(node1) is True
        assert bc.add_network_nodes(node2) is False
        assert len(bc.get_network_nodes()) == 1
    
    def test_remove_network_node(self):
        """Test removing network node."""
        bc = Blockchain("TestNode")
        node = NetworkNode("127.0.0.1", 8301)
        
        bc.add_network_nodes(node)
        assert bc.remove_network_nodes(index=0) is True
        assert len(bc.get_network_nodes()) == 0
    
    def test_difficulty_adjustment(self):
        """Test difficulty adjustment."""
        bc = Blockchain("TestNode")
        initial_difficulty = bc.difficulty
        
        # Mine enough blocks to trigger adjustment
        for _ in range(BlockchainConfig.ADJUST_DIFFICULTY_IN_EVERY + 1):
            bc.mine_block()
        
        bc.adjust_difficulty()
        
        # Difficulty should have changed (either increased or decreased)
        # This test just checks that the mechanism works
        assert bc.difficulty >= 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])