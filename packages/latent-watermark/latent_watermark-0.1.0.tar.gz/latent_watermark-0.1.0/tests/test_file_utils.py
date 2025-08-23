"""Tests for file utilities with safe filename handling."""

import os
import tempfile
import pytest
from pathlib import Path

from latent_watermark.file_utils import SafeFileManager


class TestSafeFileManager:
    """Test cases for SafeFileManager class."""
    
    def test_get_unique_filename_no_conflict(self):
        """Test filename generation when no conflicts exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test.jpg"
            result = SafeFileManager.get_unique_filename(filepath)
            assert result == filepath
    
    def test_get_unique_filename_with_conflict(self):
        """Test filename generation when conflicts exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create existing file
            filepath = Path(tmpdir) / "test.jpg"
            filepath.touch()
            
            # Should get test-1.jpg
            result = SafeFileManager.get_unique_filename(filepath)
            expected = Path(tmpdir) / "test-1.jpg"
            assert result == expected
    
    def test_get_unique_filename_multiple_conflicts(self):
        """Test filename generation with multiple existing files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create existing files
            filepath = Path(tmpdir) / "test.jpg"
            filepath.touch()
            
            conflict1 = Path(tmpdir) / "test-1.jpg"
            conflict1.touch()
            
            conflict2 = Path(tmpdir) / "test-2.jpg"
            conflict2.touch()
            
            # Should get test-3.jpg
            result = SafeFileManager.get_unique_filename(filepath)
            expected = Path(tmpdir) / "test-3.jpg"
            assert result == expected
    
    def test_get_unique_filename_custom_separator(self):
        """Test filename generation with custom separator."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test.jpg"
            filepath.touch()
            
            result = SafeFileManager.get_unique_filename(filepath, separator="_")
            expected = Path(tmpdir) / "test_1.jpg"
            assert result == expected
    
    def test_get_unique_filename_with_pattern(self):
        """Test filename generation with custom pattern."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test.jpg"
            filepath.touch()
            
            result = SafeFileManager.get_unique_filename_with_pattern(
                filepath, pattern="{stem}_copy{counter}{suffix}")
            expected = Path(tmpdir) / "test_copy1.jpg"
            assert result == expected
    
    def test_ensure_directory_exists(self):
        """Test directory creation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            new_dir = Path(tmpdir) / "new" / "nested" / "dir"
            filepath = new_dir / "test.jpg"
            
            result = SafeFileManager.ensure_directory(filepath)
            assert result.parent.exists()
            assert result == filepath
    
    def test_safe_save_no_conflict(self):
        """Test safe file saving without conflicts."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test.txt"
            data = b"test content"
            
            result = SafeFileManager.safe_save(data, filepath)
            assert result == filepath
            assert result.exists()
            assert result.read_bytes() == data
    
    def test_safe_save_with_conflict(self):
        """Test safe file saving with conflicts."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test.txt"
            filepath.write_text("existing")
            
            data = b"new content"
            result = SafeFileManager.safe_save(data, filepath)
            
            expected = Path(tmpdir) / "test-1.txt"
            assert result == expected
            assert result.exists()
            assert result.read_bytes() == data
    
    def test_safe_save_overwrite_allowed(self):
        """Test safe file saving with overwrite enabled."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test.txt"
            filepath.write_text("existing")
            
            data = b"new content"
            result = SafeFileManager.safe_save(data, filepath, ensure_unique=False)
            
            assert result == filepath
            assert result.read_bytes() == data
    
    def test_safe_save_nested_directory(self):
        """Test safe file saving in nested directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            nested_path = Path(tmpdir) / "deep" / "nested" / "path" / "test.txt"
            data = b"nested content"
            
            result = SafeFileManager.safe_save(data, nested_path)
            assert result.exists()
            assert result.read_bytes() == data
    
    def test_filename_edge_cases(self):
        """Test edge cases for filename handling."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # No extension
            filepath = Path(tmpdir) / "test"
            filepath.touch()
            
            result = SafeFileManager.get_unique_filename(filepath)
            expected = Path(tmpdir) / "test-1"
            assert result == expected
            
            # Multiple dots in filename
            filepath = Path(tmpdir) / "test.file.name.jpg"
            filepath.touch()
            
            result = SafeFileManager.get_unique_filename(filepath)
            expected = Path(tmpdir) / "test.file.name-1.jpg"
            assert result == expected
    
    def test_safety_limit(self):
        """Test safety limit for counter generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test.txt"
            
            # Create many files to test safety limit
            for i in range(10000):
                (Path(tmpdir) / f"test-{i}.txt").touch()
            
            # Should raise RuntimeError due to safety limit
            with pytest.raises(RuntimeError):
                SafeFileManager.get_unique_filename(filepath)