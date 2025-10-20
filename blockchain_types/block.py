"""Block class for blockchain blocks."""

from typing import List, Optional
from tools.converter import Converter
from tools.hash_maker import HashMaker
from tools.instant_maker import InstantMaker
from tools.io import IO
from blockchain_types.transaction import Transaction
from blockchain_types.transaction_merkle_tree import TransactionMerkleTree


class Block:
    """
    Block class representing a blockchain block.
    
    Contains transactions, mining proof, and links to previous block.
    """
    
    def __init__(
        self,
        previous_hash: str = "",
        hash_value: str = "",
        difficulty: int = 0,
        nonce: int = 0,
        timestamp: int = 0,
        transactions: Optional[List[Transaction]] = None,
        miner: str = "",
        miner_rewards: float = 0.0,
        b64_encoded_block: Optional[str] = None
    ):
        """
        Initialize block.
        
        Args:
            previous_hash: Hash of previous block
            hash_value: Hash of this block
            difficulty: Mining difficulty
            nonce: Proof of work nonce
            timestamp: Unix timestamp in milliseconds (0 = now)
            transactions: List of transactions
            miner: Miner's account address
            miner_rewards: Mining reward amount
            b64_encoded_block: If provided, restore from Base64 string
        """
        if b64_encoded_block:
            self.from_base64(b64_encoded_block)
        else:
            self.previous_hash = previous_hash
            self.hash = hash_value
            self.difficulty = difficulty
            self.nonce = nonce
            if timestamp == 0:
                self.timestamp = InstantMaker.get_now_long()
            else:
                self.timestamp = timestamp
            self.miner = miner
            self.miner_rewards = miner_rewards
            self.transactions = transactions if transactions is not None else []
            self.merkle_tree = TransactionMerkleTree(self.transactions)
    
    def get_previous_hash(self) -> str:
        """Get previous block hash."""
        return self.previous_hash
    
    def set_previous_hash(self, previous_hash: str) -> None:
        """Set previous block hash."""
        self.previous_hash = previous_hash
    
    def get_hash(self) -> str:
        """Get block hash."""
        return self.hash
    
    def set_hash(self, hash_value: str) -> None:
        """Set block hash."""
        self.hash = hash_value
    
    def get_difficulty(self) -> int:
        """Get mining difficulty."""
        return self.difficulty
    
    def set_difficulty(self, difficulty: int) -> None:
        """Set mining difficulty."""
        self.difficulty = difficulty
    
    def get_nonce(self) -> int:
        """Get nonce."""
        return self.nonce
    
    def set_nonce(self, nonce: int) -> None:
        """Set nonce."""
        self.nonce = nonce
    
    def get_timestamp(self) -> int:
        """Get timestamp."""
        return self.timestamp
    
    def set_timestamp(self, timestamp: int) -> None:
        """Set timestamp."""
        self.timestamp = timestamp
    
    def get_transactions(self) -> List[Transaction]:
        """Get list of transactions."""
        return self.transactions
    
    def add_transaction(self, new_transaction: Transaction) -> bool:
        """
        Add transaction to block.
        
        Args:
            new_transaction: Transaction to add
            
        Returns:
            True if added, False if duplicate
        """
        # Check for duplicates
        for transaction in self.transactions:
            if transaction.to_hash() == new_transaction.to_hash():
                IO.errln(new_transaction.to_string_with_content_only())
                IO.errln("Is already within this Block")
                return False
        
        self.transactions.append(new_transaction)
        self.merkle_tree = TransactionMerkleTree(self.transactions)
        return True
    
    def del_transaction(self, location: int = None, bad_transaction: Transaction = None) -> bool:
        """
        Delete transaction from block.
        
        Args:
            location: Index of transaction to remove
            bad_transaction: Transaction object to remove
            
        Returns:
            True if removed, False otherwise
        """
        if location is not None:
            if 0 <= location < len(self.transactions):
                self.transactions.pop(location)
                self.merkle_tree = TransactionMerkleTree(self.transactions)
                return True
            return False
        elif bad_transaction is not None:
            try:
                self.transactions.remove(bad_transaction)
                self.merkle_tree = TransactionMerkleTree(self.transactions)
                return True
            except ValueError:
                return False
        return False
    
    def get_merkle_root(self) -> str:
        """Get Merkle root hash."""
        return self.merkle_tree.get_merkle_root()
    
    def get_miner(self) -> str:
        """Get miner address."""
        return self.miner
    
    def set_miner(self, miner: str) -> None:
        """Set miner address."""
        self.miner = miner
    
    def get_miner_rewards(self) -> float:
        """Get mining rewards."""
        return self.miner_rewards
    
    def set_miner_rewards(self, miner_rewards: float) -> None:
        """Set mining rewards."""
        self.miner_rewards = miner_rewards
    
    def __str__(self) -> str:
        """String representation with all fields."""
        transactions_string = ""
        if self.transactions:
            transactions_string = ":".join(str(t) for t in self.transactions)
        
        return (
            f"Block [previousHash:{self.previous_hash}, hash:{self.hash}, "
            f"difficulty:{self.difficulty}, nonce:{self.nonce}, "
            f"timestamp:{self.timestamp}, transactions:{transactions_string}, "
            f"merkleTree:{self.merkle_tree.get_merkle_root()}, miner:{self.miner}, "
            f"minerRewards:{self.miner_rewards}]"
        )
    
    def to_string_with_content_only(self) -> str:
        """String representation without hash."""
        transactions_string = ""
        if self.transactions:
            transactions_string = ":".join(str(t) for t in self.transactions)
        
        return (
            f"Block [previousHash:{self.previous_hash}, "
            f"difficulty:{self.difficulty}, nonce:{self.nonce}, "
            f"timestamp:{self.timestamp}, transactions:{transactions_string}, "
            f"merkleTree:{self.merkle_tree.get_merkle_root()}, miner:{self.miner}, "
            f"minerRewards:{self.miner_rewards}]"
        )
    
    def to_base64(self) -> str:
        """
        Serialize to Base64 string with all fields.
        
        Returns:
            Base64 encoded string
        """
        encoded_transactions = ""
        if self.transactions:
            encoded_list = [Converter.string_to_base64(t.to_base64()) for t in self.transactions]
            encoded_transactions = ", ".join(encoded_list)
        
        return (
            f"Block [previousHash:{Converter.string_to_base64(self.previous_hash)}, "
            f"hash:{Converter.string_to_base64(self.hash)}, "
            f"difficulty:{Converter.string_to_base64(str(self.difficulty))}, "
            f"nonce:{Converter.string_to_base64(str(self.nonce))}, "
            f"timestamp:{Converter.string_to_base64(str(self.timestamp))}, "
            f"transactions:{Converter.string_to_base64(encoded_transactions)}, "
            f"merkleTree:{Converter.string_to_base64(self.merkle_tree.get_merkle_root())}, "
            f"miner:{Converter.string_to_base64(self.miner)}, "
            f"minerRewards:{Converter.string_to_base64(str(self.miner_rewards))}]"
        )
    
    def to_base64_with_content_only(self) -> str:
        """
        Serialize to Base64 string without hash.
        
        Used for mining (hash should not include itself).
        
        Returns:
            Base64 encoded string without hash
        """
        encoded_transactions = ""
        if self.transactions:
            encoded_list = [t.to_base64() for t in self.transactions]
            encoded_transactions = ", ".join(encoded_list)
        
        return (
            f"Block [previousHash:{Converter.string_to_base64(self.previous_hash)}, "
            f"difficulty:{Converter.string_to_base64(str(self.difficulty))}, "
            f"nonce:{Converter.string_to_base64(str(self.nonce))}, "
            f"timestamp:{Converter.string_to_base64(str(self.timestamp))}, "
            f"transactions:{Converter.string_to_base64(encoded_transactions)}, "
            f"merkleTree:{Converter.string_to_base64(self.merkle_tree.get_merkle_root())}, "
            f"miner:{Converter.string_to_base64(self.miner)}, "
            f"minerRewards:{Converter.string_to_base64(str(self.miner_rewards))}]"
        )
    
    def from_base64(self, b64_block_string: str) -> bool:
        """
        Deserialize from Base64 string.
        
        Args:
            b64_block_string: Base64 encoded block string
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Remove "Block [" and "]"
            handling_string = b64_block_string[7:-1]
            
            # Split by ", "
            attributes = handling_string.split(", ")
            
            # Initialize transactions list
            self.transactions = []
            
            for attribute in attributes:
                # Split by first ":"
                parts = attribute.split(":", 1)
                if len(parts) != 2:
                    continue
                
                item = parts[0]
                value = parts[1]
                
                if item == "previousHash":
                    self.previous_hash = Converter.base64_to_string(value)
                elif item == "hash":
                    self.hash = Converter.base64_to_string(value)
                elif item == "difficulty":
                    self.difficulty = int(Converter.base64_to_string(value))
                elif item == "nonce":
                    self.nonce = int(Converter.base64_to_string(value))
                elif item == "timestamp":
                    self.timestamp = int(Converter.base64_to_string(value))
                elif item == "miner":
                    self.miner = Converter.base64_to_string(value)
                elif item == "minerRewards":
                    self.miner_rewards = float(Converter.base64_to_string(value))
                elif item == "transactions":
                    encoded_transactions_string = Converter.base64_to_string(value)
                    if encoded_transactions_string:
                        split_encoded_transactions = encoded_transactions_string.split(", ")
                        for encoded_transaction in split_encoded_transactions:
                            decoded_transaction = Converter.base64_to_string(encoded_transaction)
                            to_restore = Transaction(b64_encoded_string=decoded_transaction)
                            self.add_transaction(to_restore)
                elif item == "merkleTree":
                    # Merkle tree is recalculated, no need to restore
                    pass
            
            return True
        except Exception as e:
            IO.errln(f"Cannot restore Block from {b64_block_string}.")
            print(e)
            return False
    
    def to_hash(self) -> str:
        """
        Calculate hash of block with all fields.
        
        Returns:
            Hash string
        """
        return HashMaker.hash_string(self.to_base64())
    
    def to_hash_with_content_only(self) -> str:
        """
        Calculate hash of block without hash field.
        
        Used for mining.
        
        Returns:
            Hash string
        """
        return HashMaker.hash_string(self.to_base64_with_content_only())