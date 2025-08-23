"""File utilities for safe output handling with automatic filename uniqueness."""

import os
import re
from pathlib import Path
from typing import Union


class SafeFileManager:
    """Manages safe file saving with automatic filename uniqueness."""
    
    @staticmethod
    def get_unique_filename(
        filepath: Union[str, Path], 
        separator: str = "-"
    ) -> Path:
        """
        Generate a unique filename by appending a counter if the file exists.
        
        Args:
            filepath: Original filepath
            separator: Separator between basename and counter (default: "-")
            
        Returns:
            Path to unique filename
            
        Examples:
            >>> SafeFileManager.get_unique_filename("output.jpg")
            Path("output.jpg")  # if doesn't exist
            >>> SafeFileManager.get_unique_filename("output.jpg")
            Path("output-1.jpg")  # if output.jpg exists
            >>> SafeFileManager.get_unique_filename("output.jpg")
            Path("output-2.jpg")  # if output.jpg and output-1.jpg exist
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            return filepath
            
        # Split into stem and suffix
        stem = filepath.stem
        suffix = filepath.suffix
        directory = filepath.parent
        
        # Find the next available counter
        counter = 1
        while True:
            new_filename = f"{stem}{separator}{counter}{suffix}"
            new_path = directory / new_filename
            
            if not new_path.exists():
                return new_path
            
            counter += 1
            
            # Safety limit to prevent infinite loops
            if counter > 9999:
                raise RuntimeError(f"Cannot find unique filename for {filepath}")
    
    @staticmethod
    def get_unique_filename_with_pattern(
        filepath: Union[str, Path],
        pattern: str = "{stem}-{counter}{suffix}"
    ) -> Path:
        """
        Generate unique filename using a custom pattern.
        
        Args:
            filepath: Original filepath
            pattern: Pattern string with {stem}, {counter}, {suffix} placeholders
            
        Returns:
            Path to unique filename
            
        Examples:
            >>> SafeFileManager.get_unique_filename_with_pattern(
            ...     "output.jpg", "{stem}_copy{counter}{suffix}")
            Path("output_copy1.jpg")
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            return filepath
            
        stem = filepath.stem
        suffix = filepath.suffix
        directory = filepath.parent
        
        counter = 1
        while True:
            new_filename = pattern.format(stem=stem, counter=counter, suffix=suffix)
            new_path = directory / new_filename
            
            if not new_path.exists():
                return new_path
            
            counter += 1
            
            if counter > 9999:
                raise RuntimeError(f"Cannot find unique filename for {filepath}")
    
    @staticmethod
    def ensure_directory(filepath: Union[str, Path]) -> Path:
        """
        Ensure the directory for the given filepath exists.
        
        Args:
            filepath: Target filepath
            
        Returns:
            Path to the filepath (directory is created if needed)
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        return filepath
    
    @staticmethod
    def safe_save(
        data: bytes,
        filepath: Union[str, Path],
        ensure_unique: bool = True,
        separator: str = "-"
    ) -> Path:
        """
        Safely save data to file with optional uniqueness guarantee.
        
        Args:
            data: Data to save
            filepath: Target filepath
            ensure_unique: Whether to ensure filename uniqueness
            separator: Separator for counter suffix
            
        Returns:
            Path to the actual saved file
        """
        filepath = Path(filepath)
        
        # Ensure directory exists
        SafeFileManager.ensure_directory(filepath)
        
        # Get unique filename if requested
        if ensure_unique:
            filepath = SafeFileManager.get_unique_filename(filepath, separator)
        
        # Write data
        with open(filepath, 'wb') as f:
            f.write(data)
        
        return filepath