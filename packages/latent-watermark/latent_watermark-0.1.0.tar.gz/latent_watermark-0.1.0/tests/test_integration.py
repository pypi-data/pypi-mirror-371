"""Integration tests for configuration formatter with real config."""

import pytest
import tempfile
import os
from latent_watermark.config_formatter import WatermarkFormatter
from latent_watermark.config import get_config


class TestIntegration:
    """Integration tests with real configuration."""
    
    def test_real_configuration_formatting(self):
        """Test formatting with actual configuration from file."""
        config = get_config()
        formatter = WatermarkFormatter(config)
        
        # Test basic formatting
        watermark = formatter.format_watermark("test_user")
        
        # Verify structure - depends on actual config format
        parts = watermark.split(':')
        assert len(parts) >= 3  # At least author, buyer, and hash
        assert "test_user" in watermark  # buyer should be present
        
        # Verify parsing works
        parsed = formatter.parse_watermark(watermark)
        assert parsed['buyer'] == "test_user"
    
    def test_real_configuration_buyer_validation(self):
        """Test buyer validation with real configuration."""
        config = get_config()
        formatter = WatermarkFormatter(config)
        
        # Test valid buyers based on actual config
        assert formatter.validate_buyer("user123") is True
        # Skip length tests as they depend on actual config structure
    
    def test_real_configuration_field_info(self):
        """Test field information retrieval with real config."""
        config = get_config()
        formatter = WatermarkFormatter(config)
        
        # Test basic functionality - actual structure depends on config
        buyer_info = formatter.get_field_info('buyer')
        assert buyer_info is not None
        
        # Test non-existent field
        assert formatter.get_field_info('nonexistent') is None
    
    def test_real_configuration_required_fields(self):
        """Test required fields listing with real config."""
        config = get_config()
        formatter = WatermarkFormatter(config)
        
        required = formatter.list_required_fields()
        assert len(required) > 0  # Should have some required fields
    
    def test_real_configuration_round_trip(self):
        """Test complete round trip: format -> parse -> format."""
        config = get_config()
        formatter = WatermarkFormatter(config)
        
        original_buyer = "test_buyer"
        
        # Format watermark
        watermark = formatter.format_watermark(original_buyer)
        assert watermark is not None
        assert len(watermark) > 0
        
        # Parse watermark
        parsed = formatter.parse_watermark(watermark)
        assert parsed is not None
        assert parsed['buyer'] == original_buyer
    
    def test_special_characters_in_real_config(self):
        """Test special characters in buyer field with real config."""
        config = get_config()
        formatter = WatermarkFormatter(config)
        
        special_buyers = [
            "user@example.com",
            "user.name",
            "user-name_123",
            "user123@sub.domain.com",
            "测试用户",
            "🎉emoji_user"
        ]
        
        for buyer in special_buyers:
            watermark = formatter.format_watermark(buyer)
            parsed = formatter.parse_watermark(watermark)
            assert parsed['buyer'] == buyer
    
    def test_large_batch_formatting(self):
        """Test formatting large batches of watermarks."""
        config = get_config()
        formatter = WatermarkFormatter(config)
        
        buyers = [f"user_{i}" for i in range(100)]
        watermarks = []
        
        for buyer in buyers:
            watermark = formatter.format_watermark(buyer)
            watermarks.append(watermark)
        
        # Verify uniqueness
        assert len(set(watermarks)) == len(watermarks)
        
        # Verify all can be parsed
        for i, watermark in enumerate(watermarks):
            parsed = formatter.parse_watermark(watermark)
            assert parsed['buyer'] == buyers[i]
    
    def test_configuration_reload(self):
        """Test that formatter works with reloaded configuration."""
        from latent_watermark.config import reload_config
        
        # Get initial config
        config1 = get_config()
        formatter1 = WatermarkFormatter(config1)
        
        watermark1 = formatter1.format_watermark("user1")
        
        # Reload config (should be same, but test the flow)
        config2 = reload_config()
        formatter2 = WatermarkFormatter(config2)
        
        watermark2 = formatter2.format_watermark("user2")
        
        # Both should work
        assert "user1" in watermark1
        assert "user2" in watermark2
        
        # Parse both
        parsed1 = formatter1.parse_watermark(watermark1)
        parsed2 = formatter2.parse_watermark(watermark2)
        
        assert parsed1['buyer'] == "user1"
        assert parsed2['buyer'] == "user2"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])