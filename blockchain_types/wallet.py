"""Wallet class for managing RSA key pairs and signing."""

from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend

from tools.converter import Converter
from tools.io import IO
from config.security_config import SecurityConfig


class Wallet:
    """
    Wallet class for managing RSA key pairs.
    
    Handles key generation, persistence, signing, and decryption.
    """
    
    def __init__(self, name: str):
        """
        Initialize wallet with given name.
        
        If keys don't exist, generates new RSA key pair and saves to disk.
        If keys exist, loads them from disk.
        
        Args:
            name: Wallet name (used as directory name)
        """
        self.wallet_name = name
        self.public_key = None
        self.private_key = None
        
        try:
            wallet_dir = Path("wallets") / self.wallet_name
            public_key_path = wallet_dir / "publicKey.key"
            private_key_path = wallet_dir / "privateKey.key"
            
            if not IO.file_exist(str(public_key_path)) or not IO.file_exist(str(private_key_path)):
                # Generate new key pair
                IO.create_directory(str(wallet_dir))
                
                self.private_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=SecurityConfig.PUBLIC_KEY_LENGTH,
                    backend=default_backend()
                )
                self.public_key = self.private_key.public_key()
                
                # Serialize and save keys
                public_key_bytes = self.public_key.public_bytes(
                    encoding=serialization.Encoding.DER,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                )
                
                private_key_bytes = self.private_key.private_bytes(
                    encoding=serialization.Encoding.DER,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                )
                
                IO.write_file(str(public_key_path), public_key_bytes, "c")
                IO.write_file(str(private_key_path), private_key_bytes, "c")
                
                IO.outln("Key Generation Done.")
            else:
                # Load existing keys
                public_key_bytes = IO.read_file(str(public_key_path))
                private_key_bytes = IO.read_file(str(private_key_path))
                
                self.public_key = serialization.load_der_public_key(
                    public_key_bytes,
                    backend=default_backend()
                )
                
                self.private_key = serialization.load_der_private_key(
                    private_key_bytes,
                    password=None,
                    backend=default_backend()
                )
        except Exception as e:
            IO.errln("Cannot load key pairs.")
            print(e)
    
    def get_name(self) -> str:
        """
        Get wallet name.
        
        Returns:
            Wallet name
        """
        return self.wallet_name
    
    def get_account(self) -> str:
        """
        Get account address (Base64 encoded public key).
        
        Returns:
            Base64 encoded public key
        """
        public_key_bytes = self.public_key.public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return Converter.bytes_to_base64(public_key_bytes)
    
    def sign(self, data: str) -> str:
        """
        Sign data with private key.
        
        Args:
            data: String data to sign
            
        Returns:
            Base64 encoded signature
        """
        try:
            # Determine hash algorithm from config
            hash_algo = self._get_hash_algorithm()
            
            signature = self.private_key.sign(
                data.encode('utf-8'),
                padding.PKCS1v15(),
                hash_algo
            )
            
            return Converter.bytes_to_base64(signature)
        except Exception as e:
            IO.outln("Something went wrong when trying to sign.")
            print(e)
            return ""
    
    def decrypt(self, encoded_data: str) -> str:
        """
        Decrypt data with private key.
        
        Args:
            encoded_data: Base64 encoded encrypted data
            
        Returns:
            Decrypted string
        """
        try:
            encrypted_bytes = Converter.base64_to_bytes(encoded_data)
            
            decrypted_bytes = self.private_key.decrypt(
                encrypted_bytes,
                padding.PKCS1v15()
            )
            
            return decrypted_bytes.decode('utf-8')
        except Exception as e:
            IO.outln("Something went wrong when trying to decrypt.")
            print(e)
            return ""
    
    def _get_hash_algorithm(self):
        """
        Get hash algorithm object based on configuration.
        
        Returns:
            Hash algorithm object from cryptography library
        """
        # Parse signature algorithm (e.g., "SHA3-256withRSA" -> "SHA3-256")
        sig_algo = SecurityConfig.SIGNATURE_ALGORITHM
        hash_name = sig_algo.split('with')[0].upper()
        
        # Map to cryptography hash algorithms
        hash_map = {
            'MD5': hashes.MD5(),
            'SHA1': hashes.SHA1(),
            'SHA224': hashes.SHA224(),
            'SHA256': hashes.SHA256(),
            'SHA384': hashes.SHA384(),
            'SHA512': hashes.SHA512(),
            'SHA3-224': hashes.SHA3_224(),
            'SHA3-256': hashes.SHA3_256(),
            'SHA3-384': hashes.SHA3_384(),
            'SHA3-512': hashes.SHA3_512(),
        }
        
        return hash_map.get(hash_name, hashes.SHA3_256())