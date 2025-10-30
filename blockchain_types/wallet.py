"""Wallet class for managing ECDSA key pairs and signing."""

import sys
import os
from pathlib import Path

# Add the ecdsa_with_rfc6979 module to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ecdsa_with_rfc6979'))

from ecdsa_with_rfc6979.ecdsa import ECDSA, StandardCurves
from tools.converter import Converter
from tools.io import IO
from config.security_config import SecurityConfig


class Wallet:
    """
    Wallet class for managing ECDSA key pairs.

    Handles key generation, persistence, and signing.
    """

    def __init__(self, name: str):
        """
        Initialize wallet with given name.

        If keys don't exist, generates new ECDSA key pair and saves to disk.
        If keys exist, loads them from disk.

        Args:
            name: Wallet name (used as directory name)
        """
        self.wallet_name = name
        self.public_key = None
        self.private_key = None
        self.ecdsa = None

        # Initialize ECDSA with configured curve
        if SecurityConfig.CURVE_NAME == "secp256k1":
            self.ecdsa = StandardCurves.secp256k1()
        elif SecurityConfig.CURVE_NAME == "secp256r1":
            self.ecdsa = StandardCurves.secp256r1()
        else:
            raise ValueError(f"Unsupported curve: {SecurityConfig.CURVE_NAME}")

        try:
            wallet_dir = Path("wallets") / self.wallet_name
            public_key_path = wallet_dir / "publicKey.key"
            private_key_path = wallet_dir / "privateKey.key"

            if not IO.file_exist(str(public_key_path)) or not IO.file_exist(str(private_key_path)):
                # Generate new key pair
                IO.create_directory(str(wallet_dir))

                self.private_key, self.public_key = self.ecdsa.generate_keypair()

                # Serialize and save keys
                public_key_str = self.ecdsa.serialize_public_key(self.public_key)
                private_key_str = self.ecdsa.serialize_private_key(self.private_key)

                IO.write_file(str(public_key_path), public_key_str.encode('utf-8'), "c")
                IO.write_file(str(private_key_path), private_key_str.encode('utf-8'), "c")

                IO.outln("ECDSA Key Generation Done.")
            else:
                # Load existing keys
                public_key_data = IO.read_file(str(public_key_path))
                private_key_data = IO.read_file(str(private_key_path))

                # Convert bytes to string if necessary
                if isinstance(public_key_data, bytes):
                    public_key_str = public_key_data.decode('utf-8')
                else:
                    public_key_str = public_key_data

                if isinstance(private_key_data, bytes):
                    private_key_str = private_key_data.decode('utf-8')
                else:
                    private_key_str = private_key_data

                self.public_key = self.ecdsa.deserialize_public_key(public_key_str)
                self.private_key = self.ecdsa.deserialize_private_key(private_key_str)

        except Exception as e:
            IO.errln("Cannot load ECDSA key pairs.")
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
        return self.ecdsa.serialize_public_key(self.public_key)

    def sign(self, data: str) -> str:
        """
        Sign data with private key using ECDSA.

        Args:
            data: String data to sign

        Returns:
            Base64 encoded signature
        """
        try:
            # Get hash function from config
            hash_func = self._get_hash_function()

            # Sign using ECDSA (with RFC 6979 if configured)
            signature = self.ecdsa.sign(
                data,
                self.private_key,
                hash_func=hash_func,
                deterministic=SecurityConfig.USE_RFC6979
            )

            return self.ecdsa.serialize_signature(signature)
        except Exception as e:
            IO.outln("Something went wrong when trying to sign with ECDSA.")
            print(e)
            return ""

    def decrypt(self, encoded_data: str) -> str:
        """
        Decrypt data with private key.

        Note: ECDSA is for signing only, not encryption.
        This method is kept for compatibility but will return empty string.

        Args:
            encoded_data: Base64 encoded encrypted data

        Returns:
            Empty string (ECDSA doesn't support encryption)
        """
        IO.outln("Warning: ECDSA doesn't support encryption. Use ECIES for encryption.")
        return ""

    def _get_hash_function(self):
        """
        Get hash function based on configuration.

        Returns:
            Hash function from hashlib
        """
        import hashlib

        # Parse signature algorithm (e.g., "SHA256withECDSA" -> "SHA256")
        sig_algo = SecurityConfig.SIGNATURE_ALGORITHM
        hash_name = sig_algo.split('with')[0].upper()

        # Map to hashlib functions
        hash_map = {
            'MD5': hashlib.md5,
            'SHA1': hashlib.sha1,
            'SHA224': hashlib.sha224,
            'SHA256': hashlib.sha256,
            'SHA384': hashlib.sha384,
            'SHA512': hashlib.sha512,
            'SHA3-224': hashlib.sha3_224,
            'SHA3-256': hashlib.sha3_256,
            'SHA3-384': hashlib.sha3_384,
            'SHA3-512': hashlib.sha3_512,
        }

        return hash_map.get(hash_name, hashlib.sha256)
