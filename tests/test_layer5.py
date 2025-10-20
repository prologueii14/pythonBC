"""Layer 5 tests: P2P Server integration."""

import pytest
import socket
import threading
import time
import shutil
from pathlib import Path

from blockchain_types.blockchain import Blockchain
from blockchain_types.network_node import NetworkNode
from tools.converter import Converter
from start_blockchain import network_server, client_handler


class TestServer:
    """Test P2P server functionality."""
    
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
    
    def test_server_startup(self):
        """Test that server can start."""
        blockchain = Blockchain("TestNode")
        
        # Start server in thread
        server_thread = threading.Thread(
            target=network_server,
            args=(blockchain, 18300)
        )
        server_thread.daemon = True
        server_thread.start()
        
        # Give server time to start
        time.sleep(0.5)
        
        # Try to connect
        try:
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_socket.settimeout(2)
            test_socket.connect(('127.0.0.1', 18300))
            test_socket.close()
            success = True
        except:
            success = False
        
        assert success is True
    
    def test_client_connection(self):
        """Test client can connect and disconnect."""
        blockchain = Blockchain("TestNode")
        
        # Start server
        server_thread = threading.Thread(
            target=network_server,
            args=(blockchain, 18301)
        )
        server_thread.daemon = True
        server_thread.start()
        time.sleep(0.5)
        
        # Connect client
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(2)
        
        try:
            client.connect(('127.0.0.1', 18301))
            
            # Send simple message
            client.sendall(b"test\n")
            
            # Should get response
            response = client.recv(1024)
            assert response is not None
            
            client.close()
        except Exception as e:
            pytest.fail(f"Client connection failed: {e}")
    
    def test_get_balance_message(self):
        """Test GET_BALANCE message."""
        blockchain = Blockchain("TestNode")
        
        # Start server
        server_thread = threading.Thread(
            target=network_server,
            args=(blockchain, 18302)
        )
        server_thread.daemon = True
        server_thread.start()
        time.sleep(0.5)
        
        # Connect and send message
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(2)
        client.connect(('127.0.0.1', 18302))
        
        # Request balance
        account = blockchain.wallet.get_account()
        message = f"getBalance, {Converter.string_to_base64(account)}\n"
        client.sendall(message.encode('utf-8'))
        
        # Receive response
        response = client.recv(1024).decode('utf-8').strip()
        balance_str = Converter.base64_to_string(response)
        balance = float(balance_str)
        
        # Should have mining reward from genesis block
        assert balance == 10.0
        
        client.close()


class TestIntegration:
    """Integration tests for complete P2P functionality."""
    
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
    
    def test_two_nodes_communication(self):
        """Test two nodes can communicate."""
        # Create two blockchains
        bc1 = Blockchain("Node1")
        bc2 = Blockchain("Node2")
        
        # Start servers
        server1_thread = threading.Thread(
            target=network_server,
            args=(bc1, 18400)
        )
        server1_thread.daemon = True
        server1_thread.start()
        
        server2_thread = threading.Thread(
            target=network_server,
            args=(bc2, 18401)
        )
        server2_thread.daemon = True
        server2_thread.start()
        
        time.sleep(0.5)
        
        # Node1 adds Node2 to its network
        node2 = NetworkNode("127.0.0.1", 18401)
        bc1.add_network_nodes(node2)
        
        assert len(bc1.get_network_nodes()) == 1
    
    def test_blockchain_basics(self):
        """Test basic blockchain operations work end-to-end."""
        bc = Blockchain("TestNode")
        
        # Check genesis block
        assert len(bc.chain) == 1
        
        # Mine a block
        bc.mine_block()
        assert len(bc.chain) == 2
        
        # Check balance
        balance = bc.get_account_balance(bc.wallet.get_account())
        assert balance == 20.0  # Two mining rewards


if __name__ == '__main__':
    pytest.main([__file__, '-v'])