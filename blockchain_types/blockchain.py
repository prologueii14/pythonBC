"""Blockchain core implementation with P2P networking."""

import time
from datetime import datetime, timezone
from typing import List, Optional
import json

from blockchain_types.wallet import Wallet
from blockchain_types.block import Block
from blockchain_types.transaction import Transaction
from blockchain_types.network_node import NetworkNode
from blockchain_types.message_type import MessageType
from blockchain_types.transaction_merkle_tree import TransactionMerkleTree
from tools.converter import Converter
from tools.hash_maker import HashMaker
from tools.nonce_maker import NonceMaker
from tools.instant_maker import InstantMaker
from tools.security import Security
from tools.io import IO
from config.blockchain_config import BlockchainConfig
from config.security_config import SecurityConfig


class Blockchain:
    """
    Blockchain core implementation.
    
    Manages blockchain state, mining, transaction validation, and P2P networking.
    """
    
    def __init__(self, wallet_name: str):
        """
        Initialize blockchain with wallet.
        
        Args:
            wallet_name: Name of wallet to use
        """
        self.wallet = Wallet(wallet_name)
        IO.outln(f"Account: {self.wallet.get_account()} loaded.")
        IO.outln(f"Algorithm: {SecurityConfig.PUBLIC_KEY_ALGORITHM}")
        
        self.difficulty = BlockchainConfig.INIT_DIFFICULTY
        self.mining = True
        self.network_nodes: List[NetworkNode] = []
        self.chain: List[Block] = []
        self.pending_transactions: List[Transaction] = []
        
        self._create_genesis()
    
    def _create_genesis(self) -> None:
        """Create genesis block if chain is empty."""
        if not self.chain:
            IO.outln("Creating Genesis Block...")
            self.mine_block()
            IO.outln("Your Genesis Block is: ")
            IO.outln(str(self.chain[0]))
        else:
            IO.errln("Chain already init, cannot form genesis block.")
    
    def mine_block(self) -> None:
        """
        Mine a new block.
        
        Performs proof-of-work mining and adds block to chain.
        """
        if not self.mining:
            return
        
        start_time = time.time()
        
        # Create difficulty string (e.g., "000" for difficulty 3)
        prefix_zero = "0" * self.difficulty
        
        # Create new block
        new_block = Block()
        new_block.set_difficulty(self.difficulty)
        new_block.set_miner(self.wallet.get_account())
        new_block.set_miner_rewards(BlockchainConfig.MINING_REWARDS)
        
        if len(self.chain) == 0:
            new_block.set_previous_hash("0")
        else:
            last_block = self.chain[-1]
            new_block.set_previous_hash(last_block.get_hash())
            new_block = self._add_transactions_to_block(new_block)
        
        # Mining loop - find valid nonce
        while True:
            new_block.set_nonce(NonceMaker.get_nonce())
            new_block.set_timestamp(InstantMaker.get_now_long())
            temp_hash = HashMaker.hash_string(new_block.to_base64_with_content_only())
            
            if temp_hash.startswith(prefix_zero):
                new_block.set_hash(temp_hash)
                break
        
        end_time = time.time()
        time_cost = int(end_time - start_time)
        IO.outln(f"Hash Found: {new_block.get_hash()} @ Difficulty: {new_block.get_difficulty()}, Time Cost: {time_cost}s")
        
        # Check if chain changed during mining (race condition prevention)
        if self.chain:
            last_block = self.chain[-1]
            if last_block.get_hash() != new_block.get_previous_hash():
                # Chain changed, handle orphaned transactions
                new_block_transactions = new_block.get_transactions()
                
                # Find where chain diverged
                different_from = 0
                for i in range(len(self.chain)):
                    if self.chain[i].get_hash() == new_block.get_previous_hash():
                        different_from = i
                
                # Remove already included transactions
                for i in range(different_from, len(self.chain)):
                    during_block = self.chain[i]
                    for transaction_in_during_block in during_block.get_transactions():
                        for new_block_transaction in new_block_transactions[:]:  # Copy list for safe removal
                            if new_block_transaction.to_hash() == transaction_in_during_block.to_hash():
                                new_block_transactions.remove(new_block_transaction)
                
                # Add remaining transactions back to pending
                if new_block_transactions:
                    for new_block_transaction in new_block_transactions:
                        self.pending_transactions.append(new_block_transaction)
                
                return  # Don't add this block
        
        # Add block to chain and broadcast
        self.chain.append(new_block)
        self.broadcast_network_message(
            MessageType.BCAST_BLOCK,
            new_block.to_base64()
        )
    
    def start_mine(self) -> None:
        """Start mining."""
        self.mining = True
    
    def stop_mine(self) -> None:
        """Stop mining."""
        self.mining = False
    
    def receive_block(self, new_block: Block) -> bool:
        """
        Receive and validate block from network.
        
        Args:
            new_block: Block to validate and add
            
        Returns:
            True if block is valid and added, False otherwise
        """
        # Check for duplicate
        for block in self.chain:
            if new_block.get_hash() == block.get_hash():
                IO.outln(new_block.to_string_with_content_only())
                IO.outln("Is a duplicated block.")
                return False
        
        # Ensure hash matches previous block
        if new_block.get_previous_hash() != self.chain[-1].get_hash():
            IO.errln(new_block.to_string_with_content_only())
            IO.errln("Is not a valid block. Discarding...")
            return False
        
        IO.outln(new_block.to_string_with_content_only())
        
        # Validate difficulty
        if new_block.get_difficulty() != self.difficulty:
            IO.errln("Difficulty does not match, Blockchain might be out of sync.")
            return False
        
        # Validate hash meets difficulty
        prefix_zeros = "0" * self.difficulty
        if not new_block.get_hash().startswith(prefix_zeros):
            IO.errln("Hash value does not match with difficulty")
            return False
        
        # Validate hash calculation (FIXED: should be != not ==)
        calculated_hash = HashMaker.hash_string(new_block.to_base64_with_content_only())
        if new_block.get_hash() != calculated_hash:
            IO.errln("Claimed hash does not match with calculated result.")
            return False
        
        # Validate Merkle root (FIXED: should be != not ==)
        calculated_merkle = TransactionMerkleTree(new_block.get_transactions()).get_merkle_root()
        if new_block.get_merkle_root() != calculated_merkle:
            IO.errln("MerkleTree result doesn't match with transactions within the block.")
            return False
        
        # Validate all transaction signatures
        for transaction in new_block.get_transactions():
            if not Security.is_signature_valid(
                transaction.get_sender(),
                transaction.to_base64_with_content_only(),
                transaction.get_signature()
            ):
                IO.errln(f"Transaction {transaction.to_string_with_content_only()}")
                IO.errln("Has a tampered signature.")
                return False
        
        # Remove included transactions from pending
        for transaction in new_block.get_transactions():
            for pending_transaction in self.pending_transactions[:]:  # Copy for safe removal
                if transaction.to_hash() == pending_transaction.to_hash():
                    self.pending_transactions.remove(pending_transaction)
        
        # Block is valid
        IO.outln(f"Block {new_block.to_string_with_content_only()}")
        IO.outln("Is a valid block")
        self.chain.append(new_block)
        self.broadcast_network_message(MessageType.BCAST_BLOCK, new_block.to_base64())
        return True
    
    def receive_transaction(self, new_transaction: Transaction) -> bool:
        """
        Receive and validate transaction from network.
        
        Args:
            new_transaction: Transaction to validate and add
            
        Returns:
            True if transaction is valid and added, False otherwise
        """
        if not Security.validate_signature_format(
            new_transaction.get_sender(),
            new_transaction.get_signature()
        ):
            IO.errln("Invalid signature format for transaction.")
            return False

        if not Security.is_signature_valid(
            new_transaction.get_sender(),
            new_transaction.to_base64_with_content_only(),
            new_transaction.get_signature()
        ):
            IO.errln(new_transaction.to_string_with_content_only())
            IO.errln("Does not have a valid signature. Discarding...")
            return False
        
        IO.outln(new_transaction.to_string_with_content_only())
        IO.outln("Has a valid signature.")

        total_cost = new_transaction.get_fee() + new_transaction.get_amount()
        sender_balance = self.get_account_balance(new_transaction.get_sender())
        
        if total_cost > sender_balance:
            IO.errln(f"Sender has insufficient funds. Required: {total_cost}, Available: {sender_balance}")
            return False

        for pending_transaction in self.pending_transactions:
            if pending_transaction.to_hash() == new_transaction.to_hash():
                IO.errln(f"Transaction: {new_transaction} is already within pending transaction.")
                return False

        for block in self.chain:
            for transaction in block.get_transactions():
                if transaction.to_hash() == new_transaction.to_hash():
                    IO.errln("Transaction already exists in blockchain.")
                    return False

        self.pending_transactions.append(new_transaction)
        IO.outln("Transaction Accepted.")
        self.broadcast_network_message(MessageType.BCAST_TRANSACT, new_transaction.to_base64())
        return True
    
    def receive_network_node(self, new_node: NetworkNode) -> bool:
        """
        Receive new network node from network.
        
        Args:
            new_node: Network node to add
            
        Returns:
            True if node is new and added, False if duplicate
        """
        if self.add_network_nodes(new_node):
            self.broadcast_network_message(
                MessageType.BCAST_NEWNODE,
                new_node.to_base64()
            )
            return True
        else:
            IO.outln(str(new_node))
            IO.outln("Is a duplicated networkNode")
            return False
    
    def get_blockchain_from(self, target_node: NetworkNode) -> bool:
        """
        Clone blockchain from another node.
        
        Args:
            target_node: Node to clone from
            
        Returns:
            True if successful, False otherwise
        """
        self.mining = False  # Stop mining first
        
        if self.chain:
            IO.errln("Warning! Your Chain Storage is not empty!")
            IO.errln("Proceed to do chain cloning will result in your existing chain storage being erased!")
            self.chain.clear()
            self.pending_transactions.clear()
        
        IO.outln(f"Cloning Blockchain from {target_node.get_inet_address()}:{target_node.get_inet_port()}")
        
        try:
            target_node.connect()
            if target_node.is_connected():
                target_socket = target_node.get_node_socket()
                
                # Send clone request
                message = MessageType.CLONE_CHAIN + "\n"
                target_socket.sendall(message.encode('utf-8'))
                
                # Receive response
                response = target_socket.recv(65536).decode('utf-8').strip()
                self.from_base64_of_exchange(response)
                
                # Validate cloned chain integrity
                if len(self.chain) > 2:
                    for i in range(len(self.chain) - 2):
                        # Check hash continuity
                        if self.chain[i + 1].get_previous_hash() != self.chain[i].get_hash():
                            IO.errln(f"Expecting previousHash value in Block {i+1} to be {self.chain[i].get_hash()}")
                            IO.errln(f"But it returns: {self.chain[i + 1].get_previous_hash()}")
                            return False
                        
                        # Check timestamp ordering
                        if self.chain[i + 1].get_timestamp() < self.chain[i].get_timestamp():
                            IO.errln(f"It is impossible for Block {i + 1} to have a smaller timestamp than Block {i}")
                            return False
                
                IO.outln("Cloning Complete.")
                target_node.disconnect()
                return True
            return False
        except Exception as e:
            IO.errln(f"Cannot clone Blockchain from {target_node.get_inet_address()}:{target_node.get_inet_port()}")
            print(e)
            return False
    
    def _add_transactions_to_block(self, new_block: Block) -> Block:
        """
        Add pending transactions to block (prioritized by fee).
        
        Args:
            new_block: Block to add transactions to
            
        Returns:
            Block with transactions added
        """
        # Sort by fee (highest first)
        self.pending_transactions.sort(key=lambda tx: tx.get_fee(), reverse=True)
        
        max_tx = BlockchainConfig.MAX_TRANSACTIONS_IN_BLOCK
        
        if len(self.pending_transactions) > max_tx:
            for _ in range(max_tx):
                new_block.add_transaction(self.pending_transactions.pop(0))
        else:
            while self.pending_transactions:
                new_block.add_transaction(self.pending_transactions.pop(0))
        
        return new_block
    
    def adjust_difficulty(self) -> None:
        """Adjust mining difficulty based on average block time."""
        if not self.mining:
            return
        
        adjust_every = BlockchainConfig.ADJUST_DIFFICULTY_IN_EVERY
        target_time = BlockchainConfig.BLOCK_TIME_IN_EVERY
        
        if len(self.chain) % adjust_every == 1 and len(self.chain) > adjust_every:
            timestamp_start = self.chain[len(self.chain) - adjust_every - 1].get_timestamp()
            timestamp_end = self.chain[-1].get_timestamp()
            
            seconds_in_between = (timestamp_end - timestamp_start) // 1000  # Convert ms to s
            average_block_time = seconds_in_between / adjust_every
            
            if average_block_time > target_time:
                if self.difficulty > 1:
                    IO.outln(f"Average Block Time: {average_block_time}s. Decrease difficulty.")
                    self.difficulty -= 1
                else:
                    self.difficulty = 1
            else:
                IO.outln(f"Average Block Time: {average_block_time}s. Increase difficulty.")
                self.difficulty += 1
    
    def get_account_balance(self, account: str) -> float:
        """
        Calculate account balance.
        
        Args:
            account: Account address
            
        Returns:
            Balance
        """
        balance = 0.0
        
        for block in self.chain:
            is_miner = False
            
            # Miner receives rewards
            if block.get_miner() == account:
                is_miner = True
                balance += block.get_miner_rewards()
            
            # Process transactions
            for transaction in block.get_transactions():
                # Miner receives fees
                if is_miner:
                    balance += transaction.get_fee()
                
                # Sender pays amount + fee
                if transaction.get_sender() == account:
                    balance -= transaction.get_fee()
                    balance -= transaction.get_amount()
                
                # Receiver receives amount
                if transaction.get_receiver() == account:
                    balance += transaction.get_amount()
        
        return balance
    
    def _compare_addresses(self, address1: str, address2: str) -> bool:
        """
        Compare two addresses for equality with multi-algorithm support.
        
        Args:
            address1: First address
            address2: Second address
            
        Returns:
            True if addresses represent the same account
        """
        if address1 == address2:
            return True

        type1 = Security.detect_address_type(address1)
        type2 = Security.detect_address_type(address2)

        if type1 != type2:
            return False

        if type1 in ["ECDSA", "DPECDSA"]:
            try:
                data1 = json.loads(Converter.base64_to_bytes(address1).decode('utf-8'))
                data2 = json.loads(Converter.base64_to_bytes(address2).decode('utf-8'))
                return data1['x'] == data2['x'] and data1['y'] == data2['y']
            except:
                return False

        return address1 == address2

    def get_network_status(self) -> dict:
        """
        Get network status with algorithm information.
        
        Returns:
            Dictionary with network status
        """
        status = {
            'chain_length': len(self.chain),
            'pending_transactions': len(self.pending_transactions),
            'network_nodes': len(self.network_nodes),
            'mining': self.mining,
            'difficulty': self.difficulty,
            'wallet_algorithm': SecurityConfig.PUBLIC_KEY_ALGORITHM,
            'wallet_address': self.wallet.get_account()
        }
        
        algo_info = Security.get_algorithm_info()
        status.update(algo_info)
        
        return status

    def get_network_nodes(self) -> List[NetworkNode]:
        """Get list of network nodes."""
        return self.network_nodes
    
    def add_network_nodes(self, new_network_node: NetworkNode) -> bool:
        """
        Add network node to list.
        
        Args:
            new_network_node: Node to add
            
        Returns:
            True if added, False if duplicate
        """
        for network_node in self.network_nodes:
            if network_node.to_hash() == new_network_node.to_hash():
                return False
        
        self.network_nodes.append(new_network_node)
        return True
    
    def remove_network_nodes(self, index: int = None, to_remove_node: NetworkNode = None) -> bool:
        """
        Remove network node from list.
        
        Args:
            index: Index of node to remove
            to_remove_node: Node object to remove
            
        Returns:
            True if removed, False otherwise
        """
        if index is not None:
            if index < len(self.network_nodes):
                self.network_nodes.pop(index)
                return True
            return False
        elif to_remove_node is not None:
            try:
                self.network_nodes.remove(to_remove_node)
                return True
            except ValueError:
                return False
        return False
    
    def broadcast_network_message(self, message_type: str, message: str) -> None:
        """
        Broadcast message to all network nodes.
        
        Args:
            message_type: Type of message (from MessageType)
            message: Message content (already Base64 encoded in most cases)
        """
        IO.outln(f"Broadcasting {message_type}, {message[:50]}...")
        
        # Work on a copy of the list to allow safe removal
        nodes_to_remove = []
        
        for node in self.network_nodes:
            if not node.is_connected():
                node.connect()
            
            if not node.is_null():
                try:
                    node_socket = node.get_node_socket()
                    
                    # Send message (FIXED: no double encoding)
                    full_message = f"{message_type}, {message}\n"
                    node_socket.sendall(full_message.encode('utf-8'))
                    
                    IO.outln(f"Broadcasted to {node.get_inet_address()}:{node.get_inet_port()}")
                    
                    # Read response
                    response = node_socket.recv(4096).decode('utf-8').strip()
                    IO.outln(f"It response {response}")
                    
                    node.disconnect()
                except Exception as e:
                    IO.errln(f"Exception occurred when trying to send message to {node}")
                    print(e)
                    nodes_to_remove.append(node)
            else:
                nodes_to_remove.append(node)
        
        # Remove failed nodes
        for node in nodes_to_remove:
            self.remove_network_nodes(to_remove_node=node)
    
    def __str__(self) -> str:
        """String representation."""
        network_nodes_string = ""
        chain_string = ""
        pending_transactions_string = ""
        
        if self.network_nodes:
            network_nodes_string = ":".join(str(node) for node in self.network_nodes)
        
        if self.chain:
            chain_string = ":".join(str(block) for block in self.chain)
        
        if self.pending_transactions:
            pending_transactions_string = ":".join(str(tx) for tx in self.pending_transactions)
        
        return (
            f"Blockchain [wallet:{self.wallet.get_name()}, difficulty:{self.difficulty}, "
            f"mining:{self.mining}, networkNodes:{network_nodes_string}, "
            f"chain:{chain_string}, pendingTransactions:{pending_transactions_string}]"
        )
    
    def to_string_for_exchange(self) -> str:
        """String representation for exchange (no pending transactions)."""
        chain_string = ""
        if self.chain:
            chain_string = ":".join(str(block) for block in self.chain)
        
        return (
            f"Blockchain [wallet:{self.wallet.get_name()}, difficulty:{self.difficulty}, "
            f"mining:{self.mining}, chain:{chain_string}]"
        )
    
    def to_base64(self) -> str:
        """
        Serialize to Base64 (complete state).
        
        Returns:
            Base64 encoded string
        """
        encoded_network_nodes = ""
        encoded_chain = ""
        encoded_pending_transactions = ""
        
        if self.network_nodes:
            encoded_list = [Converter.string_to_base64(node.to_base64()) for node in self.network_nodes]
            encoded_network_nodes = ", ".join(encoded_list)
        
        if self.chain:
            encoded_list = [Converter.string_to_base64(block.to_base64()) for block in self.chain]
            encoded_chain = ", ".join(encoded_list)
        
        if self.pending_transactions:
            encoded_list = [Converter.string_to_base64(tx.to_base64()) for tx in self.pending_transactions]
            encoded_pending_transactions = ", ".join(encoded_list)
        
        return (
            f"Blockchain [wallet:{Converter.string_to_base64(self.wallet.get_name())}, "
            f"difficulty:{Converter.string_to_base64(str(self.difficulty))}, "
            f"mining:{Converter.string_to_base64(str(self.mining))}, "
            f"networkNodes:{Converter.string_to_base64(encoded_network_nodes)}, "
            f"chain:{Converter.string_to_base64(encoded_chain)}, "
            f"pendingTransactions:{Converter.string_to_base64(encoded_pending_transactions)}]"
        )
    
    def from_base64(self, encoded_blockchain: str) -> bool:
        """
        Deserialize from Base64 (complete state).
        
        Args:
            encoded_blockchain: Base64 encoded blockchain string
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Remove "Blockchain [" and "]"
            handling_string = encoded_blockchain[12:-1]
            
            # Split by ", "
            attributes = handling_string.split(", ")
            
            for attribute in attributes:
                # Split by first ":"
                parts = attribute.split(":", 1)
                if len(parts) != 2:
                    continue
                
                item = parts[0]
                value = parts[1]
                
                if item == "wallet":
                    self.wallet = Wallet(Converter.base64_to_string(value))
                elif item == "difficulty":
                    self.difficulty = int(Converter.base64_to_string(value))
                elif item == "mining":
                    self.mining = Converter.base64_to_string(value).lower() == "true"
                elif item == "networkNodes":
                    decoded = Converter.base64_to_string(value)
                    if decoded:
                        encoded_nodes = decoded.split(", ")
                        for encoded_node in encoded_nodes:
                            decoded_node = Converter.base64_to_string(encoded_node)
                            node = NetworkNode(b64_encoded_node=decoded_node)
                            self.network_nodes.append(node)
                elif item == "chain":
                    decoded = Converter.base64_to_string(value)
                    if decoded:
                        encoded_blocks = decoded.split(", ")
                        for encoded_block in encoded_blocks:
                            decoded_block = Converter.base64_to_string(encoded_block)
                            block = Block(b64_encoded_block=decoded_block)
                            self.chain.append(block)
                elif item == "pendingTransactions":
                    decoded = Converter.base64_to_string(value)
                    if decoded:
                        encoded_txs = decoded.split(", ")
                        for encoded_tx in encoded_txs:
                            decoded_tx = Converter.base64_to_string(encoded_tx)
                            tx = Transaction(b64_encoded_string=decoded_tx)
                            self.pending_transactions.append(tx)
            
            return True
        except Exception as e:
            IO.errln(f"Cannot restore Blockchain from {encoded_blockchain}.")
            print(e)
            return False
    
    def to_base64_for_exchange(self) -> str:
        """
        Serialize to Base64 (for chain cloning, no pending transactions).
        
        Returns:
            Base64 encoded string
        """
        encoded_network_nodes = ""
        encoded_chain = ""
        
        if self.network_nodes:
            encoded_list = [Converter.string_to_base64(node.to_base64()) for node in self.network_nodes]
            encoded_network_nodes = ", ".join(encoded_list)
        
        if self.chain:
            encoded_list = [Converter.string_to_base64(block.to_base64()) for block in self.chain]
            encoded_chain = ", ".join(encoded_list)
        
        return (
            f"Blockchain [difficulty:{Converter.string_to_base64(str(self.difficulty))}, "
            f"networkNodes:{Converter.string_to_base64(encoded_network_nodes)}, "
            f"chain:{Converter.string_to_base64(encoded_chain)}]"
        )
    
    def from_base64_of_exchange(self, encoded_blockchain: str) -> bool:
        """
        Deserialize from Base64 (for chain cloning).
        
        Args:
            encoded_blockchain: Base64 encoded blockchain string
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Remove "Blockchain [" and "]"
            handling_string = encoded_blockchain[12:-1]
            
            # Split by ", "
            attributes = handling_string.split(", ")
            
            for attribute in attributes:
                # Split by first ":"
                parts = attribute.split(":", 1)
                if len(parts) != 2:
                    continue
                
                item = parts[0]
                value = parts[1]
                
                if item == "difficulty":
                    self.difficulty = int(Converter.base64_to_string(value))
                elif item == "networkNodes":
                    decoded = Converter.base64_to_string(value)
                    if decoded:
                        encoded_nodes = decoded.split(", ")
                        for encoded_node in encoded_nodes:
                            decoded_node = Converter.base64_to_string(encoded_node)
                            node = NetworkNode(b64_encoded_node=decoded_node)
                            self.add_network_nodes(node)
                elif item == "chain":
                    decoded = Converter.base64_to_string(value)
                    if decoded:
                        encoded_blocks = decoded.split(", ")
                        for encoded_block in encoded_blocks:
                            decoded_block = Converter.base64_to_string(encoded_block)
                            block = Block(b64_encoded_block=decoded_block)
                            self.chain.append(block)
            
            return True
        except Exception as e:
            IO.errln(f"Cannot load cloned chain from {encoded_blockchain}.")
            print(e)
            return False