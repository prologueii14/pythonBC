"""
Blockchain P2P node with socket server.

This is the main entry point for running a blockchain node.
"""

import sys
import threading
import socket
from blockchain_types.blockchain import Blockchain
from blockchain_types.transaction import Transaction
from blockchain_types.block import Block
from blockchain_types.network_node import NetworkNode
from blockchain_types.message_type import MessageType
from tools.converter import Converter
from tools.io import IO
from config.network_config import NetworkConfig


def network_server(blockchain: Blockchain, port: int = None):
    """
    Start network server to handle incoming connections.
    
    Args:
        blockchain: Blockchain instance to manage
        port: Port to listen on (default from config)
    """
    if port is None:
        port = NetworkConfig.SOCKET_PORT
    
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('0.0.0.0', port))
        server_socket.listen(5)
        
        IO.outln(f"Network Ready on port {port}")
        
        while True:
            client_socket, client_address = server_socket.accept()
            
            # Handle each client in a separate thread
            client_thread = threading.Thread(
                target=client_handler,
                args=(client_socket, client_address, blockchain)
            )
            client_thread.daemon = True
            client_thread.start()
    except Exception as e:
        IO.errln("Cannot startup network server.")
        print(e)
        sys.exit(1)


def client_handler(client_socket: socket.socket, client_address: tuple, blockchain: Blockchain):
    """
    Handle client connection and process messages.
    
    Args:
        client_socket: Client socket
        client_address: Client address tuple
        blockchain: Blockchain instance
    """
    try:
        IO.outln(f"{client_address[0]}:{client_address[1]} Connected.")
        
        # Receive message
        data = client_socket.recv(65536)
        if not data:
            return
        
        received_message = data.decode('utf-8').strip()
        IO.outln(f"Received: {received_message}")
        
        # Parse message
        if ", " in received_message:
            # Format: "messageType, base64Content"
            parts = received_message.split(", ", 1)
            request = parts[0]
            request_content = parts[1] if len(parts) > 1 else ""
            
            # Decode content
            if request_content:
                try:
                    request_content = Converter.base64_to_string(request_content)
                except:
                    pass  # If decode fails, use as-is
            
            # Handle different message types
            if request == MessageType.GET_BALANCE:
                # Get account balance
                balance = blockchain.get_account_balance(request_content)
                response = Converter.string_to_base64(str(balance))
                client_socket.sendall((response + "\n").encode('utf-8'))
            
            elif request == MessageType.DO_TRANSACT:
                # Receive transaction
                transaction = Transaction(b64_encoded_string=request_content)
                if blockchain.receive_transaction(transaction):
                    response = Converter.string_to_base64("Ok")
                else:
                    response = Converter.string_to_base64("Error")
                client_socket.sendall((response + "\n").encode('utf-8'))
            
            elif request == MessageType.GET_CLONE_CHAIN_FROM:
                # Clone chain from another node
                target_node = NetworkNode(b64_encoded_node=request_content)
                if blockchain.get_blockchain_from(target_node):
                    response = Converter.string_to_base64("Ok")
                else:
                    response = Converter.string_to_base64("Error")
                client_socket.sendall((response + "\n").encode('utf-8'))
            
            elif request == MessageType.JOIN_NETWORK:
                # Add network node
                new_node = NetworkNode(b64_encoded_node=request_content)
                if blockchain.receive_network_node(new_node):
                    response = Converter.string_to_base64("Ok")
                else:
                    response = Converter.string_to_base64("Dup")
                client_socket.sendall((response + "\n").encode('utf-8'))
            
            elif request == MessageType.BCAST_BLOCK:
                # Receive broadcasted block
                block = Block(b64_encoded_block=request_content)
                if blockchain.receive_block(block):
                    response = Converter.string_to_base64("Ok")
                else:
                    response = Converter.string_to_base64("Duplicated or Tampered")
                client_socket.sendall((response + "\n").encode('utf-8'))
            
            elif request == MessageType.BCAST_TRANSACT:
                # Receive broadcasted transaction
                transaction = Transaction(b64_encoded_string=request_content)
                if blockchain.receive_transaction(transaction):
                    response = Converter.string_to_base64("Ok")
                else:
                    response = Converter.string_to_base64("Duplicated")
                client_socket.sendall((response + "\n").encode('utf-8'))
            
            elif request == MessageType.BCAST_NEWNODE:
                # Receive broadcasted new node
                new_node = NetworkNode(b64_encoded_node=request_content)
                if blockchain.add_network_nodes(new_node):
                    response = Converter.string_to_base64("Ok")
                else:
                    response = Converter.string_to_base64("Dup")
                client_socket.sendall((response + "\n").encode('utf-8'))
            
            else:
                IO.errln("Client sent a command that the server could not understand.")
                response = Converter.string_to_base64("Error")
                client_socket.sendall((response + "\n").encode('utf-8'))
        
        else:
            # Single command without content
            if received_message == MessageType.MINE_START:
                blockchain.start_mine()
                response = Converter.string_to_base64("Ok")
                client_socket.sendall((response + "\n").encode('utf-8'))
            
            elif received_message == MessageType.MINE_STOP:
                blockchain.stop_mine()
                response = Converter.string_to_base64("Ok")
                client_socket.sendall((response + "\n").encode('utf-8'))
            
            elif received_message == MessageType.CLONE_CHAIN:
                # Send blockchain for cloning
                response = blockchain.to_base64_for_exchange()
                client_socket.sendall((response + "\n").encode('utf-8'))
            
            else:
                IO.errln("Client sent a command that the server could not understand.")
                response = Converter.string_to_base64("Error")
                client_socket.sendall((response + "\n").encode('utf-8'))
    
    except Exception as e:
        IO.errln(f"Socket: {client_address} failed.")
        print(e)
    
    finally:
        try:
            client_socket.close()
        except:
            pass


def mining_loop(blockchain: Blockchain):
    """
    Continuous mining loop.
    
    Args:
        blockchain: Blockchain instance to mine
    """
    while True:
        blockchain.mine_block()
        blockchain.adjust_difficulty()


def main():
    """Main entry point."""
    # Parse command line arguments
    wallet_name = "DefaultNode"
    port = NetworkConfig.SOCKET_PORT
    
    if len(sys.argv) > 1:
        wallet_name = sys.argv[1]
    if len(sys.argv) > 2:
        try:
            port = int(sys.argv[2])
        except ValueError:
            IO.errln("Invalid port number. Using default.")
    
    # Create blockchain
    IO.outln(f"Starting blockchain node: {wallet_name}")
    blockchain = Blockchain(wallet_name)
    
    # Start network server in separate thread
    network_thread = threading.Thread(target=network_server, args=(blockchain, port))
    network_thread.daemon = True
    network_thread.start()
    
    # Start mining in main thread
    try:
        mining_loop(blockchain)
    except KeyboardInterrupt:
        IO.outln("\nShutting down...")
        sys.exit(0)


if __name__ == "__main__":
    main()