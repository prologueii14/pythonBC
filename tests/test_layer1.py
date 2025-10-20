"""Layer 1 tests: Foundation tools."""

import pytest
import tempfile
import shutil
from pathlib import Path

from tools.converter import Converter
from tools.hash_maker import HashMaker
from tools.instant_maker import InstantMaker
from tools.nonce_maker import NonceMaker
from tools.io import IO


class TestConverter:
    """Test Base64 encoding/decoding."""
    
    def test_bytes_to_hex(self):
        """Test bytes to hex conversion."""
        data = b'\x01\x02\x03\x0a\x0b\x0c'
        result = Converter.bytes_to_hex(data)
        assert result == '0102030a0b0c'
    
    def test_bytes_to_base64(self):
        """Test bytes to base64 encoding."""
        data = b'Hello World'
        result = Converter.bytes_to_base64(data)
        assert result == 'SGVsbG8gV29ybGQ='
    
    def test_string_to_base64(self):
        """Test string to base64 encoding."""
        data = 'Hello World'
        result = Converter.string_to_base64(data)
        assert result == 'SGVsbG8gV29ybGQ='
    
    def test_base64_to_bytes(self):
        """Test base64 to bytes decoding."""
        data = 'SGVsbG8gV29ybGQ='
        result = Converter.base64_to_bytes(data)
        assert result == b'Hello World'
    
    def test_base64_to_string(self):
        """Test base64 to string decoding."""
        data = 'SGVsbG8gV29ybGQ='
        result = Converter.base64_to_string(data)
        assert result == 'Hello World'
    
    def test_roundtrip_string(self):
        """Test string encoding and decoding roundtrip."""
        original = 'Test String 測試字串 123!@#'
        encoded = Converter.string_to_base64(original)
        decoded = Converter.base64_to_string(encoded)
        assert decoded == original


class TestHashMaker:
    """Test hash calculation."""
    
    def test_hash_string(self):
        """Test string hashing."""
        data = 'Hello World'
        result = HashMaker.hash_string(data)
        # SHA3-256 hash of "Hello World"
        expected = 'e167f68d6563d75bb25f3aa49c29ef612d41352dc00606de7cbd630bb2665f51'
        assert result == expected
    
    def test_hash_bytes(self):
        """Test bytes hashing."""
        data = b'Hello World'
        result = HashMaker.hash_bytes(data)
        expected = 'e167f68d6563d75bb25f3aa49c29ef612d41352dc00606de7cbd630bb2665f51'
        assert result == expected
    
    def test_validate_string_correct(self):
        """Test string hash validation (correct)."""
        data = 'Hello World'
        hash_value = HashMaker.hash_string(data)
        assert HashMaker.validate_string(hash_value, data) is True
    
    def test_validate_string_incorrect(self):
        """Test string hash validation (incorrect)."""
        data = 'Hello World'
        wrong_hash = 'wrong_hash_value'
        assert HashMaker.validate_string(wrong_hash, data) is False
    
    def test_different_inputs_different_hashes(self):
        """Test that different inputs produce different hashes."""
        hash1 = HashMaker.hash_string('Hello')
        hash2 = HashMaker.hash_string('World')
        assert hash1 != hash2


class TestInstantMaker:
    """Test timestamp utilities."""
    
    def test_get_now_long(self):
        """Test getting current timestamp."""
        timestamp = InstantMaker.get_now_long()
        assert isinstance(timestamp, int)
        assert timestamp > 0
    
    def test_get_instant_from_digits(self):
        """Test creating instant from digits."""
        instant = InstantMaker.get_instant_from_digits(2024, 1, 1, 0, 0, 0)
        assert instant is not None
    
    def test_get_long_from_digits(self):
        """Test creating timestamp from digits."""
        timestamp = InstantMaker.get_long_from_digits(2024, 1, 1, 0, 0, 0)
        assert isinstance(timestamp, int)
        # Jan 1, 2024 00:00:00 UTC in milliseconds
        assert timestamp == 1704067200000
    
    def test_roundtrip_instant_long(self):
        """Test instant to long and back conversion."""
        original_timestamp = InstantMaker.get_now_long()
        instant = InstantMaker.get_instant_from_long(original_timestamp)
        converted_timestamp = InstantMaker.get_long_from_instant(instant)
        assert converted_timestamp == original_timestamp
    
    def test_iso_string_parsing(self):
        """Test ISO string parsing."""
        iso_string = "2024-01-01T00:00:00.00Z"
        instant = InstantMaker.get_instant_from_iso_string(iso_string)
        timestamp = InstantMaker.get_long_from_instant(instant)
        assert timestamp == 1704067200000


class TestNonceMaker:
    """Test nonce generation."""
    
    def test_get_nonce_returns_integer(self):
        """Test that nonce is an integer."""
        nonce = NonceMaker.get_nonce()
        assert isinstance(nonce, int)
    
    def test_get_nonce_positive(self):
        """Test that nonce is non-negative."""
        nonce = NonceMaker.get_nonce()
        assert nonce >= 0
    
    def test_multiple_nonces_different(self):
        """Test that multiple nonces are likely different (random mode)."""
        nonces = [NonceMaker.get_nonce() for _ in range(100)]
        # In random mode, should have many unique values
        unique_count = len(set(nonces))
        assert unique_count > 50  # At least 50% unique


class TestIO:
    """Test file I/O utilities."""
    
    def setup_method(self):
        """Setup test directory."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
    
    def teardown_method(self):
        """Cleanup test directory."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_write_and_read_file(self):
        """Test writing and reading file."""
        file_path = str(self.test_path / "test.bin")
        content = b'Hello World'
        
        # Write file
        assert IO.write_file(file_path, content, 'c') is True
        
        # Read file
        read_content = IO.read_file(file_path)
        assert read_content == content
    
    def test_write_file_create_mode_existing(self):
        """Test create mode with existing file."""
        file_path = str(self.test_path / "test.bin")
        
        # Create file
        IO.write_file(file_path, b'First', 'c')
        
        # Try to create again (should fail)
        assert IO.write_file(file_path, b'Second', 'c') is False
    
    def test_write_file_append_mode(self):
        """Test append mode."""
        file_path = str(self.test_path / "test.bin")
        
        # Write initial content
        IO.write_file(file_path, b'Hello', 'c')
        
        # Append content
        IO.write_file(file_path, b' World', 'a')
        
        # Read and verify
        content = IO.read_file(file_path)
        assert content == b'Hello World'
    
    def test_write_file_overwrite_mode(self):
        """Test overwrite mode."""
        file_path = str(self.test_path / "test.bin")
        
        # Write initial content
        IO.write_file(file_path, b'First', 'c')
        
        # Overwrite content
        IO.write_file(file_path, b'Second', 'o')
        
        # Read and verify
        content = IO.read_file(file_path)
        assert content == b'Second'
    
    def test_delete_file(self):
        """Test file deletion."""
        file_path = str(self.test_path / "test.bin")
        
        # Create file
        IO.write_file(file_path, b'Test', 'c')
        assert IO.file_exist(file_path) is True
        
        # Delete file
        assert IO.delete_file(file_path) is True
        assert IO.file_exist(file_path) is False
    
    def test_create_directory(self):
        """Test directory creation."""
        dir_path = str(self.test_path / "subdir")
        
        assert IO.create_directory(dir_path) is True
        assert IO.file_exist(dir_path) is True
        assert IO.is_directory(dir_path) is True
    
    def test_create_directory_existing(self):
        """Test creating existing directory."""
        dir_path = str(self.test_path / "subdir")
        
        IO.create_directory(dir_path)
        
        # Try to create again (should fail)
        assert IO.create_directory(dir_path) is False
    
    def test_file_exist(self):
        """Test file existence check."""
        file_path = str(self.test_path / "test.bin")
        
        assert IO.file_exist(file_path) is False
        
        IO.write_file(file_path, b'Test', 'c')
        
        assert IO.file_exist(file_path) is True
    
    def test_is_directory(self):
        """Test directory check."""
        dir_path = str(self.test_path / "subdir")
        file_path = str(self.test_path / "test.bin")
        
        IO.create_directory(dir_path)
        IO.write_file(file_path, b'Test', 'c')
        
        assert IO.is_directory(dir_path) is True
        assert IO.is_directory(file_path) is False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])