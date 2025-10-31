"""Wallet class for managing RSA/ECDSA/DPECDSA key pairs and signing."""

from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
import json

from tools.converter import Converter
from tools.io import IO
from config.security_config import SecurityConfig

from ecdsa.ecdsa import StandardCurves as ECDSA_Curves
from ecdsa.dpecdsa import StandardCurves as DPECDSA_Curves


class Wallet:
    """
    Wallet class for managing RSA/ECDSA/DPECDSA key pairs.
    
    Handles key generation, persistence, signing, and decryption.
    """
    
    def __init__(self, name: str):
        """
        Initialize wallet with given name.
        
        If keys don't exist, generates new key pair and saves to disk.
        If keys exist, loads them from disk.
        
        Args:
            name: Wallet name (used as directory name)
        """
        self.wallet_name = name
        self.public_key = None
        self.private_key = None
        self.key_algorithm = SecurityConfig.PUBLIC_KEY_ALGORITHM
        
        try:
            wallet_dir = Path("wallets") / self.wallet_name
            public_key_path = wallet_dir / "publicKey.key"
            private_key_path = wallet_dir / "privateKey.key"
            algorithm_path = wallet_dir / "algorithm.info"
            
            if not IO.file_exist(str(public_key_path)) or not IO.file_exist(str(private_key_path)):
                # Generate new key pair
                IO.create_directory(str(wallet_dir))
                
                if self.key_algorithm == "RSA":
                    self._generate_rsa_keys(public_key_path, private_key_path)
                elif self.key_algorithm == "ECDSA":
                    self._generate_ecdsa_keys(public_key_path, private_key_path)
                elif self.key_algorithm == "DPECDSA":
                    self._generate_dpecdsa_keys(public_key_path, private_key_path)
                else:
                    raise ValueError(f"Unsupported algorithm: {self.key_algorithm}")
                
                # Save algorithm info
                IO.write_file(str(algorithm_path), self.key_algorithm, "c")
                IO.outln(f"{self.key_algorithm} Key Generation Done.")
            else:
                # Load existing keys
                if IO.file_exist(str(algorithm_path)):
                    saved_algorithm = IO.read_file(str(algorithm_path)).decode('utf-8')
                    self.key_algorithm = saved_algorithm
                
                if self.key_algorithm == "RSA":
                    self._load_rsa_keys(public_key_path, private_key_path)
                elif self.key_algorithm in ["ECDSA", "DPECDSA"]:
                    self._load_ec_keys(public_key_path, private_key_path)
                else:
                    raise ValueError(f"Unsupported algorithm: {self.key_algorithm}")
                    
        except Exception as e:
            IO.errln("Cannot load key pairs.")
            print(e)
    
    def _generate_rsa_keys(self, public_key_path, private_key_path):
        """Generate RSA key pair."""
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
    
    def _generate_ecdsa_keys(self, public_key_path, private_key_path):
        """Generate ECDSA key pair."""
        self.ecdsa_instance = ECDSA_Curves.secp256k1()
        self.private_key, self.public_key = self.ecdsa_instance.generate_keypair()
        
        # Serialize keys for storage
        key_data = {
            'private_key': self.private_key,
            'public_key_x': self.public_key.x,
            'public_key_y': self.public_key.y
        }
        
        IO.write_file(str(public_key_path), json.dumps({'x': key_data['public_key_x'], 'y': key_data['public_key_y']}), "c")
        IO.write_file(str(private_key_path), json.dumps({'private_key': key_data['private_key']}), "c")
    
    def _generate_dpecdsa_keys(self, public_key_path, private_key_path):
        """Generate DPECDSA key pair."""
        self.dpecdsa_instance = DPECDSA_Curves.secp256k1()
        self.private_key, self.public_key = self.dpecdsa_instance.generate_keypair()
        
        # Serialize keys for storage
        key_data = {
            'private_key': self.private_key,
            'public_key_x': self.public_key.x,
            'public_key_y': self.public_key.y
        }
        
        IO.write_file(str(public_key_path), json.dumps({'x': key_data['public_key_x'], 'y': key_data['public_key_y']}), "c")
        IO.write_file(str(private_key_path), json.dumps({'private_key': key_data['private_key']}), "c")
    
    def _load_rsa_keys(self, public_key_path, private_key_path):
        """Load RSA keys from disk."""
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
    
    def _load_ec_keys(self, public_key_path, private_key_path):
        """Load elliptic curve keys from disk."""
        # Load public key
        public_key_data = json.loads(IO.read_file(str(public_key_path)).decode('utf-8'))
        
        # Load private key
        private_key_data = json.loads(IO.read_file(str(private_key_path)).decode('utf-8'))
        
        self.private_key = private_key_data['private_key']
        
        # Recreate the appropriate curve instance
        if self.key_algorithm == "ECDSA":
            self.ecdsa_instance = ECDSA_Curves.secp256k1()
            self.public_key = self.ecdsa_instance.curve.ECPoint(
                public_key_data['x'], 
                public_key_data['y']
            )
        else:  # DPECDSA
            self.dpecdsa_instance = DPECDSA_Curves.secp256k1()
            self.public_key = self.dpecdsa_instance.curve.ECPoint(
                public_key_data['x'], 
                public_key_data['y']
            )
    
    def sign(self, data: str) -> str:
        """
        Sign data with private key.
        
        Args:
            data: String data to sign
            
        Returns:
            Base64 encoded signature
        """
        try:
            if self.key_algorithm == "RSA":
                return self._sign_rsa(data)
            elif self.key_algorithm == "ECDSA":
                return self._sign_ecdsa(data)
            elif self.key_algorithm == "DPECDSA":
                return self._sign_dpecdsa(data)
            else:
                raise ValueError(f"Unsupported algorithm: {self.key_algorithm}")
        except Exception as e:
            IO.outln("Something went wrong when trying to sign.")
            print(e)
            return ""
    
    def _sign_rsa(self, data: str) -> str:
        """RSA signing implementation."""
        hash_algo = self._get_hash_algorithm()
        
        signature = self.private_key.sign(
            data.encode('utf-8'),
            padding.PKCS1v15(),
            hash_algo
        )
        
        return Converter.bytes_to_base64(signature)
    
    def _sign_ecdsa(self, data: str) -> str:
        """ECDSA signing implementation."""
        signature = self.ecdsa_instance.sign(data, self.private_key, deterministic=True)
        r, s = signature
        
        # Combine r and s into single bytes for storage
        sig_bytes = r.to_bytes(32, 'big') + s.to_bytes(32, 'big')
        return Converter.bytes_to_base64(sig_bytes)
    
    def _sign_dpecdsa(self, data: str) -> str:
        """DPECDSA signing implementation."""
        signature = self.dpecdsa_instance.sign(data, self.private_key)
        r, s, k2 = signature
        
        # Combine r, s, and k2 into single bytes for storage
        sig_bytes = r.to_bytes(32, 'big') + s.to_bytes(32, 'big') + k2.to_bytes(32, 'big')
        return Converter.bytes_to_base64(sig_bytes)
    
    def get_name(self) -> str:
        """Get wallet name."""
        return self.wallet_name
    
    def get_account(self) -> str:
        """
        Get account address (Base64 encoded public key or coordinates).
        """
        if self.key_algorithm == "RSA":
            public_key_bytes = self.public_key.public_bytes(
                encoding=serialization.Encoding.DER,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            return Converter.bytes_to_base64(public_key_bytes)
        else:
            # For ECDSA/DPECDSA, use compressed public key coordinates
            public_key_data = json.dumps({
                'x': self.public_key.x,
                'y': self.public_key.y,
                'algorithm': self.key_algorithm
            })
            return Converter.bytes_to_base64(public_key_data.encode('utf-8'))
    
    def decrypt(self, encoded_data: str) -> str:
        """
        Decrypt data with private key (RSA only).
        """
        if self.key_algorithm != "RSA":
            IO.outln("Decryption only supported for RSA keys.")
            return ""
            
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
        """Get hash algorithm based on configuration."""
        sig_algo = SecurityConfig.SIGNATURE_ALGORITHM
        hash_name = sig_algo.split('with')[0].upper()
        
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