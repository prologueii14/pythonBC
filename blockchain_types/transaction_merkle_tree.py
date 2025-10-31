"""Transaction Merkle Tree for efficient transaction verification."""

from typing import List, Optional
from tools.hash_maker import HashMaker


class TransactionMerkleTree:
    """
    Merkle Tree implementation for transactions.
    
    Provides efficient verification of transaction integrity.
    """
    
    class _MerkleNode:
        """Internal Merkle Tree node."""
        
        def __init__(
            self,
            hash_value: str,
            left: Optional['TransactionMerkleTree._MerkleNode'] = None,
            right: Optional['TransactionMerkleTree._MerkleNode'] = None
        ):
            self.hash = hash_value
            self.left = left
            self.right = right
    
    def __init__(self, transactions: List['Transaction']):
        """
        Initialize Merkle Tree from list of transactions.
        
        Args:
            transactions: List of Transaction objects
        """
        try:
            self.root = self._build_tree(transactions)
        except Exception:
            # Empty transaction list
            self.root = None
    
    def _build_tree(self, transactions: List['Transaction']) -> Optional[_MerkleNode]:
        """
        Build Merkle Tree from transactions.
        
        Args:
            transactions: List of Transaction objects
        
        Returns:
            Root node of Merkle Tree
        """
        if not transactions:
            return None
        
        # Create leaf nodes from transaction hashes
        current_level_nodes = [
            self._MerkleNode(transaction.to_hash())
            for transaction in transactions
        ]
        
        # Build tree bottom-up
        while len(current_level_nodes) > 1:
            next_level_nodes = []
            
            # Process pairs of nodes
            for i in range(0, len(current_level_nodes), 2):
                left = current_level_nodes[i]
                
                # If odd number of nodes, duplicate the last one
                if i + 1 < len(current_level_nodes):
                    right = current_level_nodes[i + 1]
                else:
                    right = left
                
                # Combine hashes and create parent node
                combined_hashes = left.hash + right.hash
                parent_hash = HashMaker.hash_string(combined_hashes)
                next_level_nodes.append(self._MerkleNode(parent_hash, left, right))
            
            current_level_nodes = next_level_nodes
        
        return current_level_nodes[0] if current_level_nodes else None
    
    def get_merkle_root(self) -> str:
        """
        Get Merkle root hash.
        
        Returns:
            Root hash, or hash of empty string if tree is empty
        """
        if self.root is None:
            return HashMaker.hash_string("")
        else:
            return self.root.hash