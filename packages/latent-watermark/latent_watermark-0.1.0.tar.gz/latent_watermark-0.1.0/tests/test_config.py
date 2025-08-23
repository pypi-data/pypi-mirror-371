"""Tests for configuration management."""

import pytest
import tempfile
import shutil
from pathlib import Path
from latent_watermark.config import ConfigManager, get_config, reload_config, set_config_dir


class TestConfigManager:
    """Test configuration management functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_config_dir = Path(self.temp_dir) / "test_config"
        set_config_dir(self.test_config_dir)
        
        # Ensure the test directory exists
        self.test_config_dir.mkdir(parents=True, exist_ok=True)
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
        # Reset to default config dir
        from latent_watermark.config import ConfigManager
        ConfigManager.CONFIG_DIR = Path.home() / ".config" / "latent_watermark"
        ConfigManager.CONFIG_FILE = ConfigManager.CONFIG_DIR / "config.yml"
    
    def test_create_default_config(self):
        """Test creation of default configuration file."""
        config_file = self.test_config_dir / "config.yml"
        assert not config_file.exists()
        
        config = ConfigManager.ensure_config()
        
        assert config_file.exists()
        assert isinstance(config, dict)
        assert "security" in config
        assert "watermark" in config
        assert "output" in config
    
    def test_load_existing_config(self):
        """Test loading existing configuration."""
        # Ensure we start with a clean state by removing any existing config
        if ConfigManager.CONFIG_FILE.exists():
            ConfigManager.CONFIG_FILE.unlink()
        
        # Create config first
        original_config = ConfigManager.ensure_config()
        
        # Load it again
        loaded_config = ConfigManager.ensure_config()
        
        assert loaded_config == original_config
    
    def test_config_file_permissions(self):
        """Test configuration file has correct permissions."""
        config_file = self.test_config_dir / "config.yml"
        ConfigManager.ensure_config()
        
        # Check if file exists and is readable
        assert config_file.exists()
        assert config_file.stat().st_mode & 0o777 == 0o600
    
    def test_get_config_global(self):
        """Test global configuration access."""
        config = get_config()
        
        assert isinstance(config, dict)
        assert "security" in config
        assert "default_password" in config["security"]
    
    def test_reload_config(self):
        """Test configuration reloading."""
        original_config = get_config()
        
        # Modify config file manually with complete configuration
        config_file = self.test_config_dir / "config.yml"
        with open(config_file, 'w') as f:
            f.write("""security:
  default_password: modified_password
  hash_algorithm: sha256
  key_length: 32
watermark:
  max_total_length: 128
  quality:
    d1: 15
    d2: 25
    quality: 85
  fields:
    author:
      min_length: 1
      max_length: 20
      default: unknown
    buyer:
      min_length: 1
      max_length: 50
    date:
      format: yyMMddHH
    hash:
      last_n_digits: 4
output:
  directory: ./output
  format: png
  quality: 95
""")
        
        reloaded_config = reload_config()
        
        assert reloaded_config != original_config
        assert reloaded_config["security"]["default_password"] == "modified_password"
    
    def test_custom_config_dir(self):
        """Test custom configuration directory."""
        custom_dir = Path(self.temp_dir) / "custom_config"
        set_config_dir(custom_dir)
        
        config = get_config()
        assert isinstance(config, dict)
        
        # Check that config was created in custom directory
        assert (custom_dir / "config.yml").exists()


if __name__ == "__main__":
    pytest.main([__file__])