"""Network node for P2P communication."""

import socket
from typing import Optional
from tools.converter import Converter
from tools.hash_maker import HashMaker
from tools.io import IO


class NetworkNode:
    """
    Network node representing a peer in the P2P network.
    
    Handles socket connections to other nodes.
    """
    
    def __init__(
        self,
        inet_address: str = "",
        inet_port: int = 0,
        b64_encoded_node: Optional[str] = None
    ):
        """
        Initialize network node.
        
        Args:
            inet_address: IP address or hostname
            inet_port: Port number
            b64_encoded_node: If provided, restore from Base64 string
        """
        if b64_encoded_node:
            self.from_base64(b64_encoded_node)
        else:
            self.inet_address = inet_address
            self.inet_port = inet_port
        self.socket = None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensure socket is closed."""
        self.close()
    
    def close(self) -> None:
        """Close socket connection."""
        try:
            if self.socket is not None:
                self.socket.close()
                self.socket = None
        except Exception as e:
            IO.errln(f"Cannot terminate {self.inet_address}:{self.inet_port}")
            print(e)
    
    def get_inet_address(self) -> str:
        """Get IP address."""
        return self.inet_address
    
    def get_inet_port(self) -> int:
        """Get port number."""
        return self.inet_port
    
    def set_inet_address(self, inet_address: str) -> None:
        """Set IP address and disconnect."""
        self.inet_address = inet_address
        self.disconnect()
    
    def set_inet_port(self, inet_port: int) -> None:
        """Set port number and disconnect."""
        self.inet_port = inet_port
        self.disconnect()
    
    def connect(self) -> bool:
        """
        Connect to the node.
        
        Returns:
            True if connected successfully, False otherwise
        """
        try:
            if not self.inet_address or self.inet_port == 0:
                IO.errln("Cannot connect to node if both inetAddress and inetPort are empty!")
                return False
            
            if self.socket is None:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((self.inet_address, self.inet_port))
                return True
            else:
                # Already have a socket, check if connected
                return self.is_connected()
        except Exception as e:
            IO.errln(f"Cannot connect to {self.inet_address}:{self.inet_port}")
            print(e)
            self.socket = None
            return False
    
    def disconnect(self) -> bool:
        """
        Disconnect from the node.
        
        Returns:
            True if disconnected successfully, False otherwise
        """
        try:
            if self.socket is None:
                return True
            else:
                self.socket.close()
                self.socket = None
                return True
        except Exception as e:
            IO.errln(f"Cannot disconnect from {self.inet_address}:{self.inet_port}")
            print(e)
            self.socket = None
            return False
    
    def is_connected(self) -> bool:
        """
        Check if socket is connected.
        
        Returns:
            True if connected, False otherwise
        """
        if self.socket is None:
            return False
        
        # Try to check connection status
        try:
            # This is a non-blocking check
            self.socket.getpeername()
            return True
        except:
            return False
    
    def is_null(self) -> bool:
        """
        Check if socket is None.
        
        Returns:
            True if socket is None, False otherwise
        """
        return self.socket is None
    
    def get_node_socket(self) -> Optional[socket.socket]:
        """
        Get socket object.
        
        Returns:
            Socket object, or None if not connected
        """
        if self.socket is None:
            IO.errln("Warning! Empty Socket!")
        return self.socket
    
    def __str__(self) -> str:
        """String representation."""
        return f"NetworkNode [inetAddress:{self.inet_address}, inetPort:{self.inet_port}]"
    
    def to_base64(self) -> str:
        """
        Serialize to Base64 string.
        
        Returns:
            Base64 encoded string
        """
        return (
            f"NetworkNode [inetAddress:{Converter.string_to_base64(self.inet_address)}, "
            f"inetPort:{Converter.string_to_base64(str(self.inet_port))}]"
        )
    
    def from_base64(self, b64_network_node_string: str) -> bool:
        """
        Deserialize from Base64 string.
        
        Args:
            b64_network_node_string: Base64 encoded string
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Remove "NetworkNode [" and "]"
            handling_string = b64_network_node_string[13:-1]
            
            # Split by ", "
            attributes = handling_string.split(", ")
            
            for attribute in attributes:
                # Split by first ":"
                parts = attribute.split(":", 1)
                if len(parts) != 2:
                    continue
                
                item = parts[0]
                value = parts[1]
                
                if item == "inetAddress":
                    self.inet_address = Converter.base64_to_string(value)
                elif item == "inetPort":
                    self.inet_port = int(Converter.base64_to_string(value))
            
            return True
        except Exception as e:
            IO.errln(f"Cannot restore NetworkNode from {b64_network_node_string}")
            print(e)
            return False
    
    def to_hash(self) -> str:
        """
        Calculate hash of network node.
        
        Returns:
            Hash string
        """
        return HashMaker.hash_string(self.to_base64())