"""File I/O and logging utilities."""

import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
from config.io_config import IOConfig


class IO:
    """File I/O and logging utilities."""
    
    @staticmethod
    def _format_message(message: str, timestamp: bool, verbose: bool, func_name: str) -> str:
        """Format message with optional timestamp and function name."""
        parts = []
        if verbose:
            parts.append(f"[{func_name}]")
        if timestamp:
            parts.append(f"[{datetime.now().isoformat()}]")
        parts.append(f": {message}")
        return "".join(parts)
    
    @staticmethod
    def _get_caller_name() -> str:
        """Get the name of the calling function."""
        import inspect
        frame = inspect.currentframe()
        if frame and frame.f_back and frame.f_back.f_back:
            caller_frame = frame.f_back.f_back
            return f"{caller_frame.f_code.co_filename}:{caller_frame.f_code.co_name}"
        return "unknown"
    
    @staticmethod
    def out(message: str, timestamp: Optional[bool] = None, 
            verbose: Optional[bool] = None, func_name: Optional[str] = None) -> None:
        """
        Print message to stdout.
        
        Args:
            message: Message to print
            timestamp: Whether to include timestamp (default: from config)
            verbose: Whether to include function name (default: from config)
            func_name: Function name to display (default: auto-detect)
        """
        if timestamp is None:
            timestamp = IOConfig.MUST_TIMESTAMP
        if verbose is None:
            verbose = IOConfig.MUST_VERBOSE
        if func_name is None:
            func_name = IO._get_caller_name()
        
        formatted = IO._format_message(message, timestamp, verbose, func_name)
        print(formatted, end='', file=sys.stdout)
    
    @staticmethod
    def outln(message: str, timestamp: Optional[bool] = None,
              verbose: Optional[bool] = None, func_name: Optional[str] = None) -> None:
        """
        Print message to stdout with newline.
        
        Args:
            message: Message to print
            timestamp: Whether to include timestamp (default: from config)
            verbose: Whether to include function name (default: from config)
            func_name: Function name to display (default: auto-detect)
        """
        IO.out(message, timestamp, verbose, func_name)
        print()
    
    @staticmethod
    def err(message: str, timestamp: Optional[bool] = None,
            verbose: Optional[bool] = None, func_name: Optional[str] = None) -> None:
        """
        Print error message to stderr.
        
        Args:
            message: Error message to print
            timestamp: Whether to include timestamp (default: from config)
            verbose: Whether to include function name (default: from config)
            func_name: Function name to display (default: auto-detect)
        """
        if timestamp is None:
            timestamp = IOConfig.MUST_TIMESTAMP
        if verbose is None:
            verbose = IOConfig.MUST_VERBOSE
        if func_name is None:
            func_name = IO._get_caller_name()
        
        formatted = IO._format_message(message, timestamp, verbose, func_name)
        print(formatted, end='', file=sys.stderr)
    
    @staticmethod
    def errln(message: str, timestamp: Optional[bool] = None,
              verbose: Optional[bool] = None, func_name: Optional[str] = None) -> None:
        """
        Print error message to stderr with newline.
        
        Args:
            message: Error message to print
            timestamp: Whether to include timestamp (default: from config)
            verbose: Whether to include function name (default: from config)
            func_name: Function name to display (default: auto-detect)
        """
        IO.err(message, timestamp, verbose, func_name)
        print(file=sys.stderr)
    
    @staticmethod
    def read_file(location: str) -> bytes:
        """
        Read file as bytes.
        
        Args:
            location: File path
            
        Returns:
            File content as bytes, empty bytes if error
        """
        try:
            path = Path(location)
            if path.exists():
                return path.read_bytes()
            else:
                IO.errln(f"File {location} does not exist.")
                return b''
        except Exception as e:
            IO.errln(f"File {location} cannot be accessed.")
            print(e, file=sys.stderr)
            return b''
    
    @staticmethod
    def delete_file(location: str) -> bool:
        """
        Delete file if exists.
        
        Args:
            location: File path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            Path(location).unlink(missing_ok=True)
            return True
        except Exception as e:
            IO.errln(f"File {location} cannot be deleted.")
            print(e, file=sys.stderr)
            return False
    
    @staticmethod
    def write_file(location: str, content: bytes, write_mode: str) -> bool:
        """
        Write bytes to file.
        
        Args:
            location: File path
            content: Bytes to write
            write_mode: Write mode - 'c' (create), 'a' (append), 'o' (overwrite)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            path = Path(location)
            
            if write_mode == 'c':
                if path.exists():
                    IO.errln(f"File {location} exists. Please specify writeMode to Overwrite")
                    return False
                else:
                    path.write_bytes(content)
                    return True
            elif write_mode == 'a':
                if path.exists():
                    with open(path, 'ab') as f:
                        f.write(content)
                else:
                    path.write_bytes(content)
                return True
            elif write_mode == 'o':
                if path.exists():
                    IO.errln(f"Warning! File {location} exists. And you specify to overwrite!")
                    path.unlink()
                path.write_bytes(content)
                return True
            else:
                IO.errln(f"Write Mode: {write_mode} is not supported.")
                return False
        except Exception as e:
            IO.errln(f"File {location} cannot be accessed.")
            print(e, file=sys.stderr)
            return False
    
    @staticmethod
    def create_directory(location: str) -> bool:
        """
        Create directory.
        
        Args:
            location: Directory path
            
        Returns:
            True if successful, False otherwise
        """
        path = Path(location)
        if path.is_dir() and path.exists():
            IO.errln(f"Directory {location} has already been created.")
            return False
        else:
            try:
                path.mkdir(parents=True, exist_ok=False)
                return True
            except Exception as e:
                IO.errln(f"Directory {location} cannot be processed.")
                print(e, file=sys.stderr)
                return False
    
    @staticmethod
    def file_exist(location: str) -> bool:
        """
        Check if file or directory exists.
        
        Args:
            location: File or directory path
            
        Returns:
            True if exists, False otherwise
        """
        return Path(location).exists()
    
    @staticmethod
    def is_directory(location: str) -> bool:
        """
        Check if path is a directory.
        
        Args:
            location: Path to check
            
        Returns:
            True if is directory, False otherwise
        """
        return Path(location).is_dir()