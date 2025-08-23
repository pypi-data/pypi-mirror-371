"""Configuration validation for latent watermark system."""

from typing import Dict, Any, List
import re


class ConfigValidationError(Exception):
    """Raised when configuration validation fails."""
    
    def __init__(self, message: str, field_path: str = None):
        self.field_path = field_path
        super().__init__(message)


class ConfigValidator:
    """Validates configuration with detailed error messages."""
    
    VALID_OUTPUT_FORMATS = {'png', 'jpg', 'jpeg', 'webp', 'bmp', 'tiff'}
    VALID_HASH_ALGORITHMS = {'sha256', 'sha512', 'md5', 'sha1'}
    VALID_DATE_FORMATS = {'yyMMddHH', 'yyMMdd', 'yyyyMMdd', 'HHmm', 'yyyy-MM-dd', 'dd/MM/yyyy', 'ISO'}
    
    @classmethod
    def validate_config(cls, config: Dict[str, Any]) -> None:
        """Validate entire configuration.
        
        Args:
            config: Configuration dictionary to validate
            
        Raises:
            ConfigValidationError: With detailed error messages for each validation failure
        """
        errors = []
        
        # Check for required sections
        for section_name in ['security', 'watermark', 'output']:
            if section_name not in config:
                errors.append(f"Missing required section: {section_name}")
            elif not isinstance(config[section_name], dict):
                errors.append(f"{section_name} must be a dictionary")
        
        # Only validate sections if they exist and are dicts
        if 'security' in config and isinstance(config['security'], dict):
            errors.extend(cls._validate_security(config['security']))
        
        if 'watermark' in config and isinstance(config['watermark'], dict):
            errors.extend(cls._validate_watermark(config['watermark']))
        
        if 'output' in config and isinstance(config['output'], dict):
            errors.extend(cls._validate_output(config['output']))
        
        if errors:
            error_message = "Configuration validation failed:\n" + "\n".join(f"  - {error}" for error in errors)
            error_message += "\n\nPlease edit the configuration file directly to fix these issues."
            raise ConfigValidationError(error_message)
    
    @classmethod
    def _validate_security(cls, security: Dict[str, Any]) -> List[str]:
        """Validate security configuration."""
        errors = []
        
        if not isinstance(security, dict):
            errors.append("security must be a dictionary")
            return errors
        
        # Validate hash algorithm
        algorithm = security.get('hash_algorithm')
        if algorithm and algorithm not in cls.VALID_HASH_ALGORITHMS:
            errors.append(
                f"security.hash_algorithm '{algorithm}' is invalid. "
                f"Must be one of: {', '.join(sorted(cls.VALID_HASH_ALGORITHMS))}"
            )
        
        # Validate key length
        key_length = security.get('key_length')
        if key_length is not None:
            if not isinstance(key_length, int):
                errors.append("security.key_length must be an integer")
            elif key_length < 16 or key_length > 64:
                errors.append(
                    f"security.key_length {key_length} is invalid. "
                    f"Must be between 16 and 64"
                )
        
        # Validate default password
        password = security.get('default_password')
        if password and not isinstance(password, str):
            errors.append("security.default_password must be a string")
        elif password and len(password) < 8:
            errors.append("security.default_password must be at least 8 characters")
        
        return errors
    
    @classmethod
    def _validate_watermark(cls, watermark: Dict[str, Any]) -> List[str]:
        """Validate watermark configuration."""
        errors = []
        
        if not isinstance(watermark, dict):
            errors.append("watermark must be a dictionary")
            return errors
        
        # Validate max_total_length
        max_length = watermark.get('max_total_length')
        if max_length is not None:
            if not isinstance(max_length, int):
                errors.append("watermark.max_total_length must be an integer")
            elif max_length < 10 or max_length > 512:
                errors.append(
                    f"watermark.max_total_length {max_length} is invalid. "
                    f"Must be between 10 and 512"
                )
        
        # Validate quality settings
        quality = watermark.get('quality', {})
        if isinstance(quality, dict):
            d1 = quality.get('d1')
            d2 = quality.get('d2')
            
            for name, value in [('d1', d1), ('d2', d2)]:
                if value is not None:
                    if not isinstance(value, int):
                        errors.append(f"watermark.quality.{name} must be an integer")
                    elif value < 1 or value > 100:
                        errors.append(
                            f"watermark.quality.{name} {value} is invalid. "
                            f"Must be between 1 and 100"
                        )
        
        # Validate fields
        fields = watermark.get('fields', {})
        if isinstance(fields, dict):
            errors.extend(cls._validate_fields(fields))
        else:
            errors.append("watermark.fields must be a dictionary")
        
        return errors
    
    @classmethod
    def _validate_fields(cls, fields: Dict[str, Dict[str, Any]]) -> List[str]:
        """Validate watermark fields configuration."""
        errors = []
        
        valid_field_names = {'author', 'buyer', 'date', 'hash'}
        
        for field_name, field_config in fields.items():
            if field_name not in valid_field_names:
                errors.append(
                    f"watermark.fields contains invalid field '{field_name}'. "
                    f"Must be one of: {', '.join(sorted(valid_field_names))}"
                )
                continue
            
            if not isinstance(field_config, dict):
                errors.append(f"watermark.fields.{field_name} must be a dictionary")
                continue
            
            # Validate field-specific configurations
            if field_name == 'date':
                date_format = field_config.get('format')
                if date_format and date_format not in cls.VALID_DATE_FORMATS:
                    errors.append(
                        f"watermark.fields.date.format '{date_format}' is invalid. "
                        f"Must be one of: {', '.join(sorted(cls.VALID_DATE_FORMATS))}"
                    )
            
            elif field_name == 'hash':
                last_n = field_config.get('last_n_digits')
                if last_n is not None:
                    if not isinstance(last_n, int):
                        errors.append("watermark.fields.hash.last_n_digits must be an integer")
                    elif last_n < 1 or last_n > 16:
                        errors.append(
                            f"watermark.fields.hash.last_n_digits {last_n} is invalid. "
                            f"Must be between 1 and 16"
                        )
            
            else:  # author or buyer
                for key, value in field_config.items():
                    if key == 'min_length':
                        if not isinstance(value, int):
                            errors.append(f"watermark.fields.{field_name}.min_length must be an integer")
                        elif value < 0 or value > 50:
                            errors.append(
                                f"watermark.fields.{field_name}.min_length {value} is invalid. "
                                f"Must be between 0 and 50"
                            )
                    elif key == 'max_length':
                        if not isinstance(value, int):
                            errors.append(f"watermark.fields.{field_name}.max_length must be an integer")
                        elif value < 1 or value > 100:
                            errors.append(
                                f"watermark.fields.{field_name}.max_length {value} is invalid. "
                                f"Must be between 1 and 100"
                            )
                    elif key == 'default':
                        if not isinstance(value, str):
                            errors.append(f"watermark.fields.{field_name}.default must be a string")
                    else:
                        errors.append(
                            f"watermark.fields.{field_name} contains invalid key '{key}'. "
                            f"Valid keys: min_length, max_length, default"
                        )
        
        return errors
    
    @classmethod
    def _validate_output(cls, output: Dict[str, Any]) -> List[str]:
        """Validate output configuration."""
        errors = []
        
        if not isinstance(output, dict):
            errors.append("output must be a dictionary")
            return errors
        
        # Validate format
        format_val = output.get('format')
        if format_val:
            format_str = str(format_val).lower()
            if format_str not in cls.VALID_OUTPUT_FORMATS:
                errors.append(
                    f"output.format '{format_val}' is invalid. "
                    f"Must be one of: {', '.join(sorted(cls.VALID_OUTPUT_FORMATS))}"
                )
        
        # Validate quality
        quality = output.get('quality')
        if quality is not None:
            if not isinstance(quality, int):
                errors.append("output.quality must be an integer")
            elif quality < 1 or quality > 100:
                errors.append(
                    f"output.quality {quality} is invalid. "
                    f"Must be between 1 and 100"
                )
        
        # Validate directory
        directory = output.get('directory')
        if directory and not isinstance(directory, str):
            errors.append("output.directory must be a string")
        
        return errors