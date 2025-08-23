"""Comprehensive tests for configuration validation and edge cases."""

import pytest
import tempfile
import os
from pathlib import Path
from typing import Dict, Any

from latent_watermark.config_validator import ConfigValidator, ConfigValidationError
from latent_watermark.config import ConfigManager


class TestConfigValidation:
    """Test comprehensive configuration validation."""
    
    def test_valid_config_passes(self):
        """Test that valid configuration passes validation."""
        config = {
            "security": {
                "default_password": "secure_password_123",
                "hash_algorithm": "sha256",
                "key_length": 32,
            },
            "watermark": {
                "author": "test_author",
                "max_total_length": 128,
                "quality": {"d1": 36, "d2": 20},
                "fields": {
                    "author": {"min_length": 1, "max_length": 20},
                    "buyer": {"min_length": 1, "max_length": 30},
                    "date": {"format": "yyMMddHH"},
                    "hash": {"last_n_digits": 4}
                }
            },
            "output": {
                "directory": "./output",
                "format": "png",
                "quality": 95,
            }
        }
        
        # Should not raise any exception
        ConfigValidator.validate_config(config)
    
    def test_invalid_output_format(self):
        """Test invalid output format raises error."""
        config = ConfigManager.get_default_config()
        config["output"]["format"] = "invalid_format"
        
        with pytest.raises(ConfigValidationError) as exc_info:
            ConfigValidator.validate_config(config)
        
        error_str = str(exc_info.value)
        assert "output.format 'invalid_format' is invalid" in error_str
        assert "bmp" in error_str and "jpeg" in error_str and "png" in error_str
    
    def test_output_quality_negative(self):
        """Test negative output quality raises error."""
        config = ConfigManager.get_default_config()
        config["output"]["quality"] = -10
        
        with pytest.raises(ConfigValidationError) as exc_info:
            ConfigValidator.validate_config(config)
        
        assert "output.quality -10 is invalid" in str(exc_info.value)
        assert "Must be between 1 and 100" in str(exc_info.value)
    
    def test_output_quality_over_100(self):
        """Test output quality over 100 raises error."""
        config = ConfigManager.get_default_config()
        config["output"]["quality"] = 150
        
        with pytest.raises(ConfigValidationError) as exc_info:
            ConfigValidator.validate_config(config)
        
        assert "output.quality 150 is invalid" in str(exc_info.value)
        assert "Must be between 1 and 100" in str(exc_info.value)
    
    def test_jpeg_format_accepted(self):
        """Test that 'jpeg' format is accepted (case insensitive)."""
        config = ConfigManager.get_default_config()
        config["output"]["format"] = "JPEG"
        
        # Should not raise any exception
        ConfigValidator.validate_config(config)
    
    def test_jpg_format_accepted(self):
        """Test that 'jpg' format is accepted."""
        config = ConfigManager.get_default_config()
        config["output"]["format"] = "jpg"
        
        # Should not raise any exception
        ConfigValidator.validate_config(config)
    
    def test_invalid_hash_algorithm(self):
        """Test invalid hash algorithm raises error."""
        config = ConfigManager.get_default_config()
        config["security"]["hash_algorithm"] = "invalid_hash"
        
        with pytest.raises(ConfigValidationError) as exc_info:
            ConfigValidator.validate_config(config)
        
        error_str = str(exc_info.value)
        assert "security.hash_algorithm 'invalid_hash' is invalid" in error_str
        assert "sha256" in error_str and "md5" in error_str
    
    def test_key_length_too_low(self):
        """Test key length below minimum raises error."""
        config = ConfigManager.get_default_config()
        config["security"]["key_length"] = 8
        
        with pytest.raises(ConfigValidationError) as exc_info:
            ConfigValidator.validate_config(config)
        
        assert "security.key_length 8 is invalid" in str(exc_info.value)
        assert "Must be between 16 and 64" in str(exc_info.value)
    
    def test_key_length_too_high(self):
        """Test key length above maximum raises error."""
        config = ConfigManager.get_default_config()
        config["security"]["key_length"] = 100
        
        with pytest.raises(ConfigValidationError) as exc_info:
            ConfigValidator.validate_config(config)
        
        assert "security.key_length 100 is invalid" in str(exc_info.value)
        assert "Must be between 16 and 64" in str(exc_info.value)
    
    def test_short_password(self):
        """Test short password raises error."""
        config = ConfigManager.get_default_config()
        config["security"]["default_password"] = "short"
        
        with pytest.raises(ConfigValidationError) as exc_info:
            ConfigValidator.validate_config(config)
        
        assert "security.default_password must be at least 8 characters" in str(exc_info.value)
    
    def test_invalid_date_format(self):
        """Test invalid date format raises error."""
        config = ConfigManager.get_default_config()
        config["watermark"]["fields"]["date"]["format"] = "invalid_format"
        
        with pytest.raises(ConfigValidationError) as exc_info:
            ConfigValidator.validate_config(config)
        
        assert "watermark.fields.date.format 'invalid_format' is invalid" in str(exc_info.value)
    
    def test_hash_last_n_digits_too_low(self):
        """Test hash last_n_digits too low raises error."""
        config = ConfigManager.get_default_config()
        config["watermark"]["fields"]["hash"]["last_n_digits"] = 0
        
        with pytest.raises(ConfigValidationError) as exc_info:
            ConfigValidator.validate_config(config)
        
        assert "watermark.fields.hash.last_n_digits 0 is invalid" in str(exc_info.value)
        assert "Must be between 1 and 16" in str(exc_info.value)
    
    def test_hash_last_n_digits_too_high(self):
        """Test hash last_n_digits too high raises error."""
        config = ConfigManager.get_default_config()
        config["watermark"]["fields"]["hash"]["last_n_digits"] = 20
        
        with pytest.raises(ConfigValidationError) as exc_info:
            ConfigValidator.validate_config(config)
        
        assert "watermark.fields.hash.last_n_digits 20 is invalid" in str(exc_info.value)
        assert "Must be between 1 and 16" in str(exc_info.value)
    
    def test_author_min_length_negative(self):
        """Test negative author min_length raises error."""
        config = ConfigManager.get_default_config()
        config["watermark"]["fields"]["author"] = {"min_length": -5}
        
        with pytest.raises(ConfigValidationError) as exc_info:
            ConfigValidator.validate_config(config)
        
        assert "watermark.fields.author.min_length -5 is invalid" in str(exc_info.value)
        assert "Must be between 0 and 50" in str(exc_info.value)
    
    def test_buyer_max_length_too_high(self):
        """Test buyer max_length too high raises error."""
        config = ConfigManager.get_default_config()
        config["watermark"]["fields"]["buyer"] = {"max_length": 200}
        
        with pytest.raises(ConfigValidationError) as exc_info:
            ConfigValidator.validate_config(config)
        
        assert "watermark.fields.buyer.max_length 200 is invalid" in str(exc_info.value)
        assert "Must be between 1 and 100" in str(exc_info.value)
    
    def test_invalid_field_name(self):
        """Test invalid field name raises error."""
        config = ConfigManager.get_default_config()
        config["watermark"]["fields"]["invalid_field"] = {"min_length": 1}
        
        with pytest.raises(ConfigValidationError) as exc_info:
            ConfigValidator.validate_config(config)
        
        assert "watermark.fields contains invalid field 'invalid_field'" in str(exc_info.value)
    
    def test_watermark_max_length_too_low(self):
        """Test watermark max_total_length too low raises error."""
        config = ConfigManager.get_default_config()
        config["watermark"]["max_total_length"] = 5
        
        with pytest.raises(ConfigValidationError) as exc_info:
            ConfigValidator.validate_config(config)
        
        assert "watermark.max_total_length 5 is invalid" in str(exc_info.value)
        assert "Must be between 10 and 512" in str(exc_info.value)
    
    def test_quality_d1_negative(self):
        """Test quality d1 negative raises error."""
        config = ConfigManager.get_default_config()
        config["watermark"]["quality"]["d1"] = -10
        
        with pytest.raises(ConfigValidationError) as exc_info:
            ConfigValidator.validate_config(config)
        
        assert "watermark.quality.d1 -10 is invalid" in str(exc_info.value)
        assert "Must be between 1 and 100" in str(exc_info.value)
    
    def test_quality_d2_over_100(self):
        """Test quality d2 over 100 raises error."""
        config = ConfigManager.get_default_config()
        config["watermark"]["quality"]["d2"] = 150
        
        with pytest.raises(ConfigValidationError) as exc_info:
            ConfigValidator.validate_config(config)
        
        assert "watermark.quality.d2 150 is invalid" in str(exc_info.value)
        assert "Must be between 1 and 100" in str(exc_info.value)
    
    def test_empty_config(self):
        """Test empty configuration raises appropriate errors."""
        config = {}
        
        with pytest.raises(ConfigValidationError) as exc_info:
            ConfigValidator.validate_config(config)
        
        error_str = str(exc_info.value)
        assert "Missing required section: security" in error_str
        assert "Missing required section: watermark" in error_str
        assert "Missing required section: output" in error_str
        assert "Please edit the configuration file directly" in error_str
    
    def test_non_dict_security(self):
        """Test non-dictionary security section raises error."""
        config = ConfigManager.get_default_config()
        config["security"] = "invalid"
        
        with pytest.raises(ConfigValidationError) as exc_info:
            ConfigValidator.validate_config(config)
        
        assert "security must be a dictionary" in str(exc_info.value)
    
    def test_non_dict_watermark(self):
        """Test non-dictionary watermark section raises error."""
        config = ConfigManager.get_default_config()
        config["watermark"] = "invalid"
        
        with pytest.raises(ConfigValidationError) as exc_info:
            ConfigValidator.validate_config(config)
        
        assert "watermark must be a dictionary" in str(exc_info.value)
    
    def test_non_dict_output(self):
        """Test non-dictionary output section raises error."""
        config = ConfigManager.get_default_config()
        config["output"] = "invalid"
        
        with pytest.raises(ConfigValidationError) as exc_info:
            ConfigValidator.validate_config(config)
        
        assert "output must be a dictionary" in str(exc_info.value)
    
    def test_invalid_field_configuration_type(self):
        """Test invalid field configuration type raises error."""
        config = ConfigManager.get_default_config()
        config["watermark"]["fields"]["author"] = "invalid"
        
        with pytest.raises(ConfigValidationError) as exc_info:
            ConfigValidator.validate_config(config)
        
        assert "watermark.fields.author must be a dictionary" in str(exc_info.value)
    
    def test_multiple_errors_reported(self):
        """Test multiple validation errors are all reported."""
        config = ConfigManager.get_default_config()
        config["output"]["format"] = "invalid"
        config["output"]["quality"] = 150
        config["security"]["hash_algorithm"] = "invalid"
        
        with pytest.raises(ConfigValidationError) as exc_info:
            ConfigValidator.validate_config(config)
        
        error_str = str(exc_info.value)
        assert "output.format 'invalid' is invalid" in error_str
        assert "output.quality 150 is invalid" in error_str
        assert "security.hash_algorithm 'invalid' is invalid" in error_str


class TestConfigFileValidation:
    """Test configuration file validation with real files."""
    
    def test_load_invalid_config_file(self):
        """Test loading invalid config file raises proper error."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir) / "test_config"
            config_dir.mkdir()
            
            # Create invalid config file
            config_file = config_dir / "config.yml"
            with open(config_file, 'w') as f:
                f.write("""
security:
  hash_algorithm: invalid_algorithm
  key_length: 1000
output:
  format: invalid_format
  quality: 200
""")
            
            # Load and validate - this should raise ConfigValidationError
            from latent_watermark.config import set_config_dir
            set_config_dir(config_dir)
            
            with pytest.raises(ConfigValidationError) as exc_info:
                ConfigManager.ensure_config()
            
            error_str = str(exc_info.value)
            assert "invalid_algorithm" in error_str
            assert "1000" in error_str
            assert "invalid_format" in error_str
            assert "200" in error_str
            assert "Please edit the configuration file directly" in error_str
    
    def test_load_valid_config_file(self):
        """Test loading valid config file works correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir) / "test_config"
            config_dir.mkdir()
            
            # Create valid config file
            config_file = config_dir / "config.yml"
            with open(config_file, 'w') as f:
                f.write("""
security:
  default_password: "test_password_123"
  hash_algorithm: "sha256"
  key_length: 32
watermark:
  author: "test_author"
  max_total_length: 100
  quality:
    d1: 40
    d2: 25
  fields:
    author:
      min_length: 1
      max_length: 20
    buyer:
      min_length: 1
      max_length: 30
    date:
      format: "yyMMddHH"
    hash:
      last_n_digits: 6
output:
  directory: "./test_output"
  format: "jpg"
  quality: 85
""")
            
            # Load and validate
            from latent_watermark.config import set_config_dir
            set_config_dir(config_dir)
            
            config = ConfigManager.ensure_config()
            
            # Should not raise any exception
            ConfigValidator.validate_config(config)
            
            # Verify values are loaded correctly
            assert config["security"]["hash_algorithm"] == "sha256"
            assert config["output"]["format"] == "jpg"
            assert config["output"]["quality"] == 85