"""Transaction class for blockchain transactions."""

from typing import Optional
from tools.converter import Converter
from tools.hash_maker import HashMaker
from tools.instant_maker import InstantMaker
from tools.io import IO


class Transaction:
    """
    Transaction class representing a blockchain transaction.
    
    Contains sender, receiver, amount, fee, timestamp, message, and signature.
    """
    
    def __init__(
        self,
        sender: str = "",
        receiver: str = "",
        amount: float = 0.0,
        fee: float = 0.0,
        timestamp: int = 0,
        message: str = "",
        signature: str = "",
        b64_encoded_string: Optional[str] = None
    ):
        """
        Initialize transaction.
        
        Args:
            sender: Sender's account address (Base64 public key)
            receiver: Receiver's account address (Base64 public key)
            amount: Transaction amount
            fee: Transaction fee
            timestamp: Unix timestamp in milliseconds (0 = now)
            message: Optional message
            signature: Digital signature (Base64)
            b64_encoded_string: If provided, restore from Base64 string
        """
        if b64_encoded_string:
            self.from_base64(b64_encoded_string)
        else:
            self.sender = sender
            self.receiver = receiver
            self.amount = amount
            self.fee = fee
            if timestamp == 0:
                self.timestamp = InstantMaker.get_now_long()
            else:
                self.timestamp = timestamp
            self.message = message
            self.signature = signature
    
    def get_sender(self) -> str:
        """Get sender address."""
        return self.sender
    
    def set_sender(self, sender: str) -> None:
        """Set sender address."""
        self.sender = sender
    
    def get_receiver(self) -> str:
        """Get receiver address."""
        return self.receiver
    
    def set_receiver(self, receiver: str) -> None:
        """Set receiver address."""
        self.receiver = receiver
    
    def get_amount(self) -> float:
        """Get transaction amount."""
        return self.amount
    
    def set_amount(self, amount: float) -> None:
        """Set transaction amount."""
        self.amount = amount
    
    def get_fee(self) -> float:
        """Get transaction fee."""
        return self.fee
    
    def set_fee(self, fee: float) -> None:
        """Set transaction fee."""
        self.fee = fee
    
    def get_timestamp(self) -> int:
        """Get timestamp."""
        return self.timestamp
    
    def set_timestamp(self, timestamp: int) -> None:
        """Set timestamp."""
        self.timestamp = timestamp
    
    def get_message(self) -> str:
        """Get message."""
        return self.message
    
    def set_message(self, message: str) -> None:
        """Set message."""
        self.message = message
    
    def get_signature(self) -> str:
        """Get signature."""
        return self.signature
    
    def set_signature(self, signature: str) -> None:
        """Set signature."""
        self.signature = signature
    
    def __str__(self) -> str:
        """String representation with all fields."""
        return (
            f"Transaction [sender:{self.sender}, receiver:{self.receiver}, "
            f"amount:{self.amount}, fee:{self.fee}, timestamp:{self.timestamp}, "
            f"message:{self.message}, signature:{self.signature}]"
        )
    
    def to_string_with_content_only(self) -> str:
        """String representation without signature."""
        return (
            f"Transaction [sender:{self.sender}, receiver:{self.receiver}, "
            f"amount:{self.amount}, fee:{self.fee}, timestamp:{self.timestamp}, "
            f"message:{self.message}]"
        )
    
    def to_base64(self) -> str:
        """
        Serialize to Base64 string with all fields.
        
        Returns:
            Base64 encoded string representation
        """
        return (
            f"Transaction [sender:{Converter.string_to_base64(self.sender)}, "
            f"receiver:{Converter.string_to_base64(self.receiver)}, "
            f"amount:{Converter.string_to_base64(str(self.amount))}, "
            f"fee:{Converter.string_to_base64(str(self.fee))}, "
            f"timestamp:{Converter.string_to_base64(str(self.timestamp))}, "
            f"message:{Converter.string_to_base64(self.message)}, "
            f"signature:{Converter.string_to_base64(self.signature)}]"
        )
    
    def to_base64_with_content_only(self) -> str:
        """
        Serialize to Base64 string without signature.
        
        Used for signing (signature should not include itself).
        
        Returns:
            Base64 encoded string without signature
        """
        return (
            f"Transaction [sender:{Converter.string_to_base64(self.sender)}, "
            f"receiver:{Converter.string_to_base64(self.receiver)}, "
            f"amount:{Converter.string_to_base64(str(self.amount))}, "
            f"fee:{Converter.string_to_base64(str(self.fee))}, "
            f"timestamp:{Converter.string_to_base64(str(self.timestamp))}, "
            f"message:{Converter.string_to_base64(self.message)}]"
        )
    
    def from_base64(self, b64_transaction_string: str) -> bool:
        """
        Deserialize from Base64 string.
        
        Args:
            b64_transaction_string: Base64 encoded transaction string
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Remove "Transaction [" and "]"
            handling_string = b64_transaction_string[13:-1]
            
            # Split by ", "
            attributes = handling_string.split(", ")
            
            for attribute in attributes:
                # Split by first ":"
                parts = attribute.split(":", 1)
                if len(parts) != 2:
                    continue
                    
                item = parts[0]
                value = parts[1]
                
                if item == "sender":
                    self.sender = Converter.base64_to_string(value)
                elif item == "receiver":
                    self.receiver = Converter.base64_to_string(value)
                elif item == "amount":
                    self.amount = float(Converter.base64_to_string(value))
                elif item == "fee":
                    self.fee = float(Converter.base64_to_string(value))
                elif item == "timestamp":
                    self.timestamp = int(Converter.base64_to_string(value))
                elif item == "message":
                    self.message = Converter.base64_to_string(value)
                elif item == "signature":
                    self.signature = Converter.base64_to_string(value)
            
            return True
        except Exception as e:
            IO.errln(f"Cannot restore Transaction from {b64_transaction_string}.")
            print(e)
            return False
    
    def to_hash(self) -> str:
        """
        Calculate hash of transaction with all fields.
        
        Returns:
            Hash string
        """
        return HashMaker.hash_string(self.to_base64())
    
    def to_hash_with_content_only(self) -> str:
        """
        Calculate hash of transaction without signature.
        
        Returns:
            Hash string
        """
        return HashMaker.hash_string(self.to_base64_with_content_only())