from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature
import json

from tools.converter import Converter
from tools.io import IO
from config.security_config import SecurityConfig

# 導入 ECDSA 模組
from ecdsa.ecdsa import StandardCurves as ECDSA_Curves
from ecdsa.dpecdsa import StandardCurves as DPECDSA_Curves


class Security:
    """Security utilities for signature verification with multi-algorithm support."""
    
    @staticmethod
    def _restore_public_key_from_address(address: str):
        """
        Restore public key from Base64 encoded address.
        
        Args:
            address: Base64 encoded public key or coordinates
            
        Returns:
            Public key object or ECPoint, or None if error
        """
        try:
            # 先嘗試檢測地址類型
            address_type = Security.detect_address_type(address)
            
            if address_type == "RSA":
                return Security._restore_rsa_public_key(address)
            elif address_type == "ECDSA":
                return Security._restore_ec_public_key(address, "ECDSA")
            elif address_type == "DPECDSA":
                return Security._restore_ec_public_key(address, "DPECDSA")
            else:
                # 使用配置的預設演算法
                algorithm = SecurityConfig.PUBLIC_KEY_ALGORITHM
                if algorithm == "RSA":
                    return Security._restore_rsa_public_key(address)
                elif algorithm == "ECDSA":
                    return Security._restore_ec_public_key(address, "ECDSA")
                elif algorithm == "DPECDSA":
                    return Security._restore_ec_public_key(address, "DPECDSA")
                else:
                    IO.errln(f"Unsupported algorithm: {algorithm}")
                    return None
                
        except Exception as e:
            IO.errln(f"Cannot restore public key from: {address}")
            print(e)
            return None
    
    @staticmethod
    def _restore_rsa_public_key(address: str):
        """Restore RSA public key from DER encoded Base64 string."""
        public_key_bytes = Converter.base64_to_bytes(address)
        public_key = serialization.load_der_public_key(
            public_key_bytes,
            backend=default_backend()
        )
        return public_key
    
    @staticmethod
    def _restore_ec_public_key(address: str, algorithm: str):
        """Restore elliptic curve public key from JSON encoded coordinates."""
        # 解析公鑰座標 JSON
        public_key_data = json.loads(Converter.base64_to_bytes(address).decode('utf-8'))
        x = public_key_data['x']
        y = public_key_data['y']
        
        # 根據演算法創建對應的曲線實例和公鑰點
        if algorithm == "ECDSA":
            ecdsa = ECDSA_Curves.secp256k1()
            return ecdsa.curve.ECPoint(x, y)
        else:  # DPECDSA
            dpecdsa = DPECDSA_Curves.secp256k1()
            return dpecdsa.curve.ECPoint(x, y)
    
    @staticmethod
    def detect_address_type(address: str) -> str:
        """
        Detect the type of address (RSA, ECDSA, DPECDSA).
        
        Args:
            address: Base64 encoded address
            
        Returns:
            Algorithm type or "UNKNOWN"
        """
        try:
            # 嘗試解析為 RSA
            public_key_bytes = Converter.base64_to_bytes(address)
            serialization.load_der_public_key(public_key_bytes, backend=default_backend())
            return "RSA"
        except:
            try:
                # 嘗試解析為橢圓曲線地址
                public_key_data = json.loads(Converter.base64_to_bytes(address).decode('utf-8'))
                if 'x' in public_key_data and 'y' in public_key_data:
                    if 'algorithm' in public_key_data:
                        return public_key_data['algorithm']
                    else:
                        return "ECDSA"  # 預設為 ECDSA
                return "UNKNOWN"
            except:
                return "UNKNOWN"
    
    @staticmethod
    def _get_hash_algorithm():
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
    
    @staticmethod
    def is_signature_valid(address: str, data: str, encoded_signature: str) -> bool:
        """
        Verify signature validity with multi-algorithm support.
        
        Args:
            address: Base64 encoded public key (account address)
            data: Original data that was signed
            encoded_signature: Base64 encoded signature
            
        Returns:
            True if signature is valid, False otherwise
        """
        try:
            # 檢測地址類型
            address_type = Security.detect_address_type(address)
            
            if address_type == "RSA":
                return Security._verify_rsa_signature(address, data, encoded_signature)
            elif address_type in ["ECDSA", "DPECDSA"]:
                return Security._verify_ec_signature(address, data, encoded_signature, address_type)
            else:
                # 使用配置的預設演算法
                algorithm = SecurityConfig.PUBLIC_KEY_ALGORITHM
                if algorithm == "RSA":
                    return Security._verify_rsa_signature(address, data, encoded_signature)
                elif algorithm == "ECDSA":
                    return Security._verify_ecdsa_signature(address, data, encoded_signature)
                elif algorithm == "DPECDSA":
                    return Security._verify_dpecdsa_signature(address, data, encoded_signature)
                else:
                    IO.errln(f"Unsupported algorithm: {algorithm}")
                    return False
                
        except Exception as e:
            IO.errln("Something went wrong when validating signature")
            print(e)
            return False
    
    @staticmethod
    def _verify_rsa_signature(address: str, data: str, encoded_signature: str) -> bool:
        """Verify RSA signature."""
        try:
            public_key = Security._restore_rsa_public_key(address)
            if public_key is None:
                return False
            
            signature = Converter.base64_to_bytes(encoded_signature)
            hash_algo = Security._get_hash_algorithm()
            
            # Verify RSA signature
            public_key.verify(
                signature,
                data.encode('utf-8'),
                padding.PKCS1v15(),
                hash_algo
            )
            
            return True
        except InvalidSignature:
            return False
        except Exception as e:
            IO.errln(f"RSA signature verification error: {e}")
            return False
    
    @staticmethod
    def _verify_ec_signature(address: str, data: str, encoded_signature: str, algorithm: str) -> bool:
        """Verify elliptic curve signature (ECDSA or DPECDSA)."""
        try:
            # 恢復公鑰點
            public_key_point = Security._restore_ec_public_key(address, algorithm)
            if public_key_point is None:
                return False
            
            signature_bytes = Converter.base64_to_bytes(encoded_signature)
            
            if algorithm == "ECDSA":
                # ECDSA 簽章 (r + s = 64 bytes)
                if len(signature_bytes) != 64:
                    IO.errln(f"Invalid ECDSA signature length: {len(signature_bytes)} bytes, expected 64")
                    return False
                    
                r = int.from_bytes(signature_bytes[:32], 'big')
                s = int.from_bytes(signature_bytes[32:], 'big')
                signature = (r, s)
                
                ecdsa = ECDSA_Curves.secp256k1()
                return ecdsa.verify(data, signature, public_key_point)
                
            else:  # DPECDSA
                # DPECDSA 簽章 (r + s + k2 = 96 bytes)
                if len(signature_bytes) != 96:
                    IO.errln(f"Invalid DPECDSA signature length: {len(signature_bytes)} bytes, expected 96")
                    return False
                    
                r = int.from_bytes(signature_bytes[:32], 'big')
                s = int.from_bytes(signature_bytes[32:64], 'big')
                k2 = int.from_bytes(signature_bytes[64:], 'big')
                signature = (r, s, k2)
                
                dpecdsa = DPECDSA_Curves.secp256k1()
                return dpecdsa.verify(data, signature, public_key_point)
            
        except Exception as e:
            IO.errln(f"{algorithm} signature verification error: {e}")
            return False
    
    @staticmethod
    def _verify_ecdsa_signature(address: str, data: str, encoded_signature: str) -> bool:
        """Verify ECDSA signature (legacy method)."""
        return Security._verify_ec_signature(address, data, encoded_signature, "ECDSA")
    
    @staticmethod
    def _verify_dpecdsa_signature(address: str, data: str, encoded_signature: str) -> bool:
        """Verify DPECDSA signature (legacy method)."""
        return Security._verify_ec_signature(address, data, encoded_signature, "DPECDSA")
    
    @staticmethod
    def get_expected_signature_length(address: str = None) -> int:
        """
        Get expected signature length in bytes.
        
        Args:
            address: If provided, detect from address type
            
        Returns:
            Expected signature length in bytes
        """
        if address:
            address_type = Security.detect_address_type(address)
        else:
            address_type = SecurityConfig.PUBLIC_KEY_ALGORITHM
        
        if address_type == "RSA":
            return SecurityConfig.PUBLIC_KEY_LENGTH // 8  # bytes
        elif address_type == "ECDSA":
            return 64  # r(32) + s(32)
        elif address_type == "DPECDSA":
            return 96  # r(32) + s(32) + k2(32)
        else:
            return SecurityConfig.PUBLIC_KEY_LENGTH // 8  # 預設 RSA
    
    @staticmethod
    def validate_signature_format(address: str, encoded_signature: str) -> bool:
        """
        Validate signature format based on address type.
        
        Args:
            address: Account address
            encoded_signature: Base64 encoded signature
            
        Returns:
            True if signature format is valid, False otherwise
        """
        try:
            signature_bytes = Converter.base64_to_bytes(encoded_signature)
            expected_length = Security.get_expected_signature_length(address)
            
            if len(signature_bytes) != expected_length:
                IO.errln(f"Signature length mismatch for {address}. Expected: {expected_length} bytes, Got: {len(signature_bytes)} bytes")
                return False
                
            return True
        except Exception as e:
            IO.errln(f"Signature format validation error: {e}")
            return False
    
    @staticmethod
    def get_algorithm_info(address: str = None) -> dict:
        """
        Get information about address algorithm.
        
        Args:
            address: Account address
            
        Returns:
            Dictionary with algorithm information
        """
        if address:
            algorithm = Security.detect_address_type(address)
        else:
            algorithm = SecurityConfig.PUBLIC_KEY_ALGORITHM
            
        sig_algo = SecurityConfig.SIGNATURE_ALGORITHM
        
        info = {
            'public_key_algorithm': algorithm,
            'signature_algorithm': sig_algo,
            'expected_signature_length': Security.get_expected_signature_length(address),
            'key_strength': SecurityConfig.PUBLIC_KEY_LENGTH
        }
        
        if algorithm in ["ECDSA", "DPECDSA"]:
            info['curve'] = 'secp256k1'
            
        return info