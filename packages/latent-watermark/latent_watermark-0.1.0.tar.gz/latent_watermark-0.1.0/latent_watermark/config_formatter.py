"""Configuration formatter for watermark structure validation and generation."""

import re
from typing import Dict, Any, Optional, List
from datetime import datetime
import hashlib
import base64

from .config_validator import ConfigValidationError


class WatermarkFormatter:
    """Handles watermark structure formatting and validation."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize formatter with configuration.
        
        Args:
            config: Configuration dictionary containing watermark structure
        """
        self.config = config
        self.fields = config.get('watermark', {}).get('fields', {})
        
        # Get default author from field configuration
        author_config = self.fields.get('author', {})
        self.author_default = author_config.get('default', 'unknown')
        
        # Build format string based on configured fields
        field_order = [f for f in ['author', 'buyer', 'date', 'hash'] if f in self.fields]
        self.format_string = ':'.join([f'${field}' for field in field_order])
    
    def format_watermark(self, buyer: str, **kwargs) -> str:
        """Format watermark string according to configured structure with dynamic length calculation.
        
        Args:
            buyer: Buyer identifier (mandatory, supports Chinese characters)
            **kwargs: Additional fields including optional 'author'
            
        Returns:
            Formatted watermark string within max_total_length
            
        Raises:
            ValueError: If validation fails with clear error messages
        """
        # Start with mandatory buyer and author
        author = kwargs.get('author', self.author_default)
        
        # Build data dictionary based on configured fields
        data = {}
        
        # Always include configured fields in order
        for field_name in self.fields:
            if field_name == 'author':
                data['author'] = author
            elif field_name == 'buyer':
                data['buyer'] = buyer
            elif field_name == 'date':
                # Use configured date format
                date_config = self.fields['date']
                date_format = date_config.get('format', 'yyMMddHH')
                now = datetime.now()
                
                # Map format strings to strftime patterns
                format_map = {
                    'yyMMddHH': '%y%m%d%H',
                    'yyMMdd': '%y%m%d',
                    'yyyyMMdd': '%Y%m%d',
                    'HHmm': '%H%M',
                }
                strftime_format = format_map.get(date_format, '%y%m%d%H')
                data['date'] = kwargs.get('date', now.strftime(strftime_format))
            elif field_name == 'hash':
                # Use configured hash truncation
                hash_config = self.fields['hash']
                last_n = hash_config.get('last_n_digits', 4)
                full_hash = kwargs.get('hash', self._generate_hash(buyer))
                data['hash'] = full_hash[-last_n:] if len(full_hash) >= last_n else full_hash
            else:
                # Handle additional fields
                data[field_name] = kwargs.get(field_name, '')
        
        # Calculate total length constraint
        max_total = self.config.get('watermark', {}).get('max_total_length', 128)
        
        # Build format string dynamically based on field order
        field_order = [f for f in ['author', 'buyer', 'date', 'hash'] if f in data]
        
        # Validate empty author/buyer fields
        if 'author' in data and not data['author'].strip() and self.author_default != "":
            raise ValueError(
                f"Author field cannot be empty. Please provide a valid author name "
                f"or configure a default author in the configuration."
            )
        
        if 'buyer' in data and not data['buyer'].strip():
            raise ValueError(
                f"Buyer field cannot be empty. Please provide a valid buyer identifier."
            )

        # Build the actual watermark string
        parts = []
        for field in field_order:
            parts.append(str(data[field]))
        
        result = ':'.join(parts)
        
        # Validate total length and provide clear error message
        if len(result) > max_total:
            author_len = len(str(data.get('author', '')))
            buyer_len = len(str(data.get('buyer', '')))
            date_len = len(str(data.get('date', '')))
            hash_len = len(str(data.get('hash', '')))
            
            raise ValueError(
                f"Watermark too long: {len(result)} characters exceeds maximum {max_total}.\n"
                f"Current breakdown: author({author_len}) + buyer({buyer_len}) + "
                f"date({date_len}) + hash({hash_len}) + colons = {len(result)}\n"
                f"Please shorten author/buyer names or increase max_total_length in config.\n"
                f"Suggested: reduce author to {max(1, author_len - (len(result) - max_total))} chars "
                f"or buyer to {max(1, buyer_len - (len(result) - max_total))} chars"
            )
        
        # Validate all fields
        self._validate_fields(data)
        
        return result
    
    def validate_buyer(self, buyer: str) -> bool:
        """Validate buyer identifier against configuration.
        
        Args:
            buyer: Buyer identifier to validate
            
        Returns:
            True if valid, False otherwise
        """
        buyer_config = self.fields.get('buyer', {})
        min_length = buyer_config.get('min_length', 1)
        
        if not isinstance(buyer, str):
            return False
        
        if len(buyer) < min_length:
            return False
        
        return True
    
    def _validate_fields(self, data: Dict[str, str]) -> None:
        """Validate all fields against configuration.
        
        Args:
            data: Dictionary of field values
            
        Raises:
            ValueError: If any field validation fails with clear messages
        """
        for field_name, value in data.items():
            if field_name not in self.fields:
                continue
                
            field_config = self.fields[field_name]
            self._validate_field(field_name, value, field_config)
    
    def _validate_field(self, field_name: str, value: str, field_config: Dict[str, Any]) -> None:
        """Validate a single field against its configuration.
        
        Args:
            field_name: Name of the field
            value: Value to validate
            field_config: Configuration for this field
            
        Raises:
            ValueError: If validation fails with clear messages
        """
        min_length = field_config.get('min_length', 0)
        
        if len(value) < min_length:
            raise ValueError(
                f"Field '{field_name}' is too short: {len(value)} characters, "
                f"minimum required: {min_length}"
            )
    
    def parse_watermark(self, watermark: str) -> Dict[str, str]:
        """Parse watermark string into components.
        
        Args:
            watermark: Watermark string to parse
            
        Returns:
            Dictionary of parsed components
            
        Raises:
            ValueError: If watermark format is invalid
        """
        if not watermark:
            raise ValueError("Watermark cannot be empty")
        
        # Build pattern string
        pattern_str = self._build_parse_pattern()
        
        # Compile and match
        try:
            pattern = re.compile(pattern_str)
            match = pattern.match(watermark)
            
            if not match:
                raise ValueError(f"Invalid watermark format: {watermark}")
            
            # Get required fields in order
            required_fields = self.list_required_fields()
            groups = match.groups()
            
            if len(groups) != len(required_fields):
                raise ValueError(
                    f"Expected {len(required_fields)} fields, got {len(groups)}"
                )
            
            # Map groups to fields
            result = {}
            for i, field in enumerate(required_fields):
                result[field] = groups[i]
            
            return result
            
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {e}")
    
    def validate_buyer(self, buyer: str) -> bool:
        """Validate buyer identifier against configuration.
        
        Args:
            buyer: Buyer identifier to validate
            
        Returns:
            True if valid, False otherwise
        """
        buyer_config = self.fields.get('buyer', {})
        min_length = buyer_config.get('min_length', 1)
        max_length = buyer_config.get('max_length', 64)
        
        if not isinstance(buyer, str):
            return False
        
        if len(buyer) < min_length:
            return False
            
        if len(buyer) > max_length:
            return False
        
        return True
    
    def _validate_fields(self, data: Dict[str, str]) -> None:
        """Validate all fields against configuration.
        
        Args:
            data: Dictionary of field values
            
        Raises:
            ValueError: If any field validation fails
        """
        for field_name, value in data.items():
            if field_name not in self.fields:
                continue
                
            field_config = self.fields[field_name]
            self._validate_field(field_name, value, field_config)
    
    def _validate_field(self, name: str, value: str, config: Dict[str, Any]) -> None:
        """Validate individual field against configuration.

        Args:
            name: Field name
            value: Field value
            config: Field configuration

        Raises:
            ValueError: If validation fails
        """
        min_length = config.get('min_length', 0)
        max_length = config.get('max_length')
        length = config.get('length')

        if not isinstance(value, str):
            value = str(value)

        # Allow empty values if default is empty and this is the default value
        is_default_author = name == 'author' and value == "" and self.author_default == ""
        
        if min_length and len(value) < min_length and not is_default_author:
            raise ValueError(f"Field {name} is too short: {len(value)} characters, minimum required: {min_length}")

        if max_length and len(value) > max_length:
            raise ValueError(f"Field {name} exceeds max length {max_length}")

        if length is not None and len(value) != length:
            raise ValueError(f"Field {name} must be exactly {length} characters")
    
    def _apply_format(self, data: Dict[str, str]) -> str:
        """Apply format string with field values.
        
        Args:
            data: Dictionary of field values
            
        Returns:
            Formatted string
        """
        result = self.format_string
        for field, value in data.items():
            if field in self.fields:
                result = result.replace(f"${field}", str(value))
        return result
    
    def _build_parse_pattern(self) -> str:
        """Build regex pattern for parsing watermarks.
        
        Returns:
            Regex pattern string
        """
        # Split format string by field placeholders
        parts = []
        current_pos = 0
        
        # Find all field placeholders
        field_pattern = r'\$([a-zA-Z_][a-zA-Z0-9_]*)'
        matches = list(re.finditer(field_pattern, self.format_string))
        
        if not matches:
            # No fields, treat as literal
            return re.escape(self.format_string)
        
        # Build pattern parts
        pattern_parts = []
        last_end = 0
        
        for match in matches:
            field_name = match.group(1)
            if field_name in self.fields:
                # Add literal text before field
                if match.start() > last_end:
                    literal = re.escape(self.format_string[last_end:match.start()])
                    pattern_parts.append(literal)
                
                # Add field pattern
                field_config = self.fields[field_name]
                field_regex = self._get_field_regex(field_name, field_config)
                pattern_parts.append(field_regex)
                last_end = match.end()
        
        # Add remaining literal text
        if last_end < len(self.format_string):
            literal = re.escape(self.format_string[last_end:])
            pattern_parts.append(literal)
        
        return ''.join(pattern_parts)
    
    def _get_field_regex(self, field: str, config: Dict[str, Any]) -> str:
        """Get regex pattern for specific field.
        
        Args:
            field: Field name
            config: Field configuration
            
        Returns:
            Regex pattern string
        """
        field_type = config.get('type', 'string')
        pattern = config.get('pattern')
        max_length = config.get('max_length', 64)
        
        if pattern:
            return f"({pattern})"
        elif field_type == 'string':
            # Create non-greedy capture group that handles various separators
            if max_length:
                return f"([^{{}}\\[\\]|\\s]{{1,{max_length}}})"
            else:
                return f"([^{{}}\\[\\]|\\s]+)"
        else:
            return f"([^{{}}\\[\\]|\\s]+)"  # Default fallback
    
    def _generate_hash(self, content: str) -> str:
        """Generate hash for watermark content.
        
        Args:
            content: Content to hash
            
        Returns:
            MD5 hash string
        """
        return hashlib.md5(content.encode()).hexdigest()
    
    def get_field_info(self, field: str) -> Optional[Dict[str, Any]]:
        """Get configuration for specific field.
        
        Args:
            field: Field name
            
        Returns:
            Field configuration or None
        """
        return self.fields.get(field)
    
    def list_required_fields(self) -> List[str]:
        """List all required fields from format string.
        
        Returns:
            List of required field names
        """
        # Find all $field patterns in format string
        import re
        matches = re.findall(r'\$([a-zA-Z_][a-zA-Z0-9_]*)', self.format_string)
        return [match for match in matches if match in self.fields]