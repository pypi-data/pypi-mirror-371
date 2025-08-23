"""Configuration management for latent watermark system."""

import os
import yaml
import stat
from pathlib import Path
from typing import Dict, Any

from .config_validator import ConfigValidator, ConfigValidationError


class ConfigManager:
    """Manages configuration loading and creation with validation."""
    
    CONFIG_DIR = Path.home() / ".config" / "latent_watermark"
    CONFIG_FILE = CONFIG_DIR / "config.yml"
    
    @classmethod
    def ensure_config_dir(cls) -> None:
        """Ensure configuration directory exists with proper permissions."""
        cls.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        # Ensure directory is only accessible by owner
        os.chmod(cls.CONFIG_DIR, stat.S_IRWXU)
    
    @classmethod
    def get_default_config(cls) -> Dict[str, Any]:
        """Get default configuration values.
        
        Returns:
            Default configuration dictionary
        """
        return {
            "security": {
                "hash_algorithm": "sha256",
                "key_length": 32,
                "default_password": "latent_watermark_2024"
            },
            "watermark": {
                "max_total_length": 128,
                "quality": {
                    "d1": 15,
                    "d2": 25
                },
                "fields": {
                    "author": {
                        "min_length": 1,
                        "max_length": 20,
                        "default": "unknown"  # Default author name
                    },
                    "buyer": {
                        "min_length": 1,
                        "max_length": 50
                    },
                    "date": {
                        "format": "yyMMddHH"
                    },
                    "hash": {
                        "last_n_digits": 4
                    }
                }
            },
            "output": {
                "format": "png",
                "quality": 95,
                "directory": "./output"
            }
        }
    
    @classmethod
    def get_default_config_yaml(cls) -> str:
        """Get the default configuration as YAML string with comments."""
        config = cls.get_default_config()
        
        return f"""# Latent Watermark Configuration
# This file contains all configuration options for the latent watermark system
# Please edit this file directly to customize your settings

security:
  # Default password for encryption/decryption operations
  default_password: "{config['security']['default_password']}"
  
  # Hash algorithm for generating watermarks
  # Options: sha256, sha512, md5, sha1
  hash_algorithm: "{config['security']['hash_algorithm']}"
  
  # Key length for encryption (16-64 bytes)
  key_length: {config['security']['key_length']}

watermark:
  # Maximum total length of watermark string (10-512 characters)
  max_total_length: {config['watermark']['max_total_length']}
  
  # Quality parameters for watermark embedding
  # d1/d2 ratio affects robustness vs distortion
  quality:
    d1: {config['watermark']['quality']['d1']}  # Higher values = more robust but more image distortion
    d2: {config['watermark']['quality']['d2']}  # Lower values = more robust but more image distortion
  
  # Field configurations for watermark components
  fields:
    author:
      min_length: {config['watermark']['fields']['author']['min_length']}
      max_length: {config['watermark']['fields']['author']['max_length']}
      default: "{config['watermark']['fields']['author']['default']}"
    buyer:
      min_length: {config['watermark']['fields']['buyer']['min_length']}
      max_length: {config['watermark']['fields']['buyer']['max_length']}
    date:
      # Format options: yyMMddHH, yyMMdd, yyyyMMdd, HHmm, yyyy-MM-dd, dd/MM/yyyy, ISO
      format: "{config['watermark']['fields']['date']['format']}"
    hash:
      last_n_digits: {config['watermark']['fields']['hash']['last_n_digits']}  # Number of digits to keep from hash (1-16)

output:
  # Output directory for processed images
  directory: "{config['output']['directory']}"
  
  # Output format for processed images
  # Options: png, jpg, jpeg, webp, bmp, tiff
  format: "{config['output']['format']}"
  
  # Output quality for lossy formats (1-100)
  quality: {config['output']['quality']}
"""
    
    @classmethod
    def ensure_config(cls) -> Dict[str, Any]:
        """Ensure configuration file exists and return validated configuration."""
        cls.ensure_config_dir()
        
        if cls.CONFIG_FILE.exists():
            try:
                with open(cls.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    if config is None:
                        config = {}
            except yaml.YAMLError as e:
                raise ConfigValidationError(
                    f"Failed to parse configuration file: {cls.CONFIG_FILE}\n"
                    f"Error: {e}\n"
                    f"Please check your YAML syntax and try again."
                )
            except OSError as e:
                raise ConfigValidationError(
                    f"Failed to read configuration file: {cls.CONFIG_FILE}\n"
                    f"Error: {e}\n"
                    f"Please check file permissions and try again."
                )
        else:
            # Create default configuration with comments
            config = cls.get_default_config()
            cls.save_config(config)
            
        # Validate the configuration
        try:
            ConfigValidator.validate_config(config)
        except ConfigValidationError as e:
            # Enhance error message with file location
            raise ConfigValidationError(
                f"Configuration validation failed for: {cls.CONFIG_FILE}\n"
                f"{str(e)}\n"
                f"Please edit the configuration file directly to fix these issues."
            )
        
        return config
    
    @classmethod
    def save_config(cls, config: Dict[str, Any]) -> None:
        """Save configuration to file with validation."""
        cls.ensure_config_dir()
        
        # Validate before saving
        try:
            ConfigValidator.validate_config(config)
        except ConfigValidationError as e:
            raise ConfigValidationError(
                f"Cannot save invalid configuration:\n{str(e)}\n"
                f"Please fix the configuration issues before saving."
            )
        
        try:
            # Write default config with comments if it's the default
            if config == cls.get_default_config():
                yaml_content = cls.get_default_config_yaml()
                with open(cls.CONFIG_FILE, 'w', encoding='utf-8') as f:
                    f.write(yaml_content)
            else:
                # Write actual config without comments
                with open(cls.CONFIG_FILE, 'w', encoding='utf-8') as f:
                    yaml.dump(config, f, default_flow_style=False, sort_keys=True)
            
            # Set file permissions to owner read/write only
            os.chmod(cls.CONFIG_FILE, stat.S_IRUSR | stat.S_IWUSR)
            
        except OSError as e:
            raise ConfigValidationError(
                f"Failed to save configuration to: {cls.CONFIG_FILE}\n"
                f"Error: {e}\n"
                f"Please check directory permissions and disk space."
            )


# Global configuration instance
_config_cache: Dict[str, Any] = {}


def get_config() -> Dict[str, Any]:
    """Get the current validated configuration."""
    if not _config_cache:
        try:
            _config_cache.update(ConfigManager.ensure_config())
        except ConfigValidationError as e:
            # Re-raise with clear guidance
            raise ConfigValidationError(
                f"Configuration Error: {str(e)}\n"
                f"Please edit your configuration file at: {ConfigManager.CONFIG_FILE}\n"
                f"You can delete the file to regenerate with defaults."
            )
    return _config_cache.copy()


def reload_config() -> Dict[str, Any]:
    """Reload configuration from file with validation."""
    _config_cache.clear()
    return get_config()


def set_config_dir(config_dir: Path) -> None:
    """Set custom configuration directory (mainly for testing)."""
    ConfigManager.CONFIG_DIR = config_dir
    ConfigManager.CONFIG_FILE = config_dir / "config.yml"
    _config_cache.clear()