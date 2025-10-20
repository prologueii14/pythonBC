"""Timestamp utilities."""

import time
from datetime import datetime, timezone


class InstantMaker:
    """Timestamp creation and conversion utilities."""
    
    @staticmethod
    def get_now_instant() -> datetime:
        """
        Get current datetime in UTC.
        
        Returns:
            Current datetime object in UTC
        """
        return datetime.now(timezone.utc)
    
    @staticmethod
    def get_now_long() -> int:
        """
        Get current timestamp in milliseconds.
        
        Returns:
            Current timestamp in milliseconds (Unix epoch)
        """
        return InstantMaker.get_long_from_instant(InstantMaker.get_now_instant())
    
    @staticmethod
    def get_instant_from_digits(year: int, month: int, day: int, 
                                hour: int, minute: int, second: int) -> datetime:
        """
        Create datetime from individual components.
        
        Args:
            year: Year
            month: Month (1-12)
            day: Day (1-31)
            hour: Hour (0-23)
            minute: Minute (0-59)
            second: Second (0-59)
            
        Returns:
            Datetime object in UTC
        """
        iso_string = f"{year:04d}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:{second:02d}.00Z"
        return InstantMaker.get_instant_from_iso_string(iso_string)
    
    @staticmethod
    def get_long_from_digits(year: int, month: int, day: int,
                            hour: int, minute: int, second: int) -> int:
        """
        Create timestamp from individual components.
        
        Args:
            year: Year
            month: Month (1-12)
            day: Day (1-31)
            hour: Hour (0-23)
            minute: Minute (0-59)
            second: Second (0-59)
            
        Returns:
            Timestamp in milliseconds
        """
        instant = InstantMaker.get_instant_from_digits(year, month, day, hour, minute, second)
        return InstantMaker.get_long_from_instant(instant)
    
    @staticmethod
    def get_instant_from_iso_string(iso_date_string: str) -> datetime:
        """
        Parse ISO format datetime string.
        
        Args:
            iso_date_string: ISO format datetime string (e.g., "2024-01-01T00:00:00.00Z")
            
        Returns:
            Datetime object
        """
        return datetime.fromisoformat(iso_date_string.replace('Z', '+00:00'))
    
    @staticmethod
    def get_long_from_iso_string(iso_date_string: str) -> int:
        """
        Parse ISO format datetime string to timestamp.
        
        Args:
            iso_date_string: ISO format datetime string
            
        Returns:
            Timestamp in milliseconds
        """
        instant = InstantMaker.get_instant_from_iso_string(iso_date_string)
        return InstantMaker.get_long_from_instant(instant)
    
    @staticmethod
    def get_instant_from_long(timestamp: int) -> datetime:
        """
        Convert timestamp to datetime.
        
        Args:
            timestamp: Timestamp in milliseconds
            
        Returns:
            Datetime object in UTC
        """
        return datetime.fromtimestamp(timestamp / 1000.0, tz=timezone.utc)
    
    @staticmethod
    def get_long_from_instant(instant: datetime) -> int:
        """
        Convert datetime to timestamp.
        
        Args:
            instant: Datetime object
            
        Returns:
            Timestamp in milliseconds
        """
        return int(instant.timestamp() * 1000)