"""Shared utilities for watermark operations."""

from blind_watermark import WaterMark
from typing import Optional


class WatermarkInitializer:
    """Shared utility for initializing watermark instances with quality settings."""
    
    @staticmethod
    def init_watermark(
        password_img: int = 1,
        password_wm: int = 1,
        d1: Optional[int] = None,
        d2: Optional[int] = None
    ) -> WaterMark:
        """Initialize watermark instance with consistent quality settings.
        
        Args:
            password_img: Password for image encryption
            password_wm: Password for watermark encryption
            d1: D1 parameter for watermark robustness (default: 36)
            d2: D2 parameter for watermark robustness (default: 20)
            
        Returns:
            Configured WaterMark instance ready for embedding/extraction
        """
        bwm = WaterMark(
            password_img=password_img,
            password_wm=password_wm
        )
        
        # Set quality parameters - use provided values or defaults
        bwm.bwm_core.d1 = d1 if d1 is not None else 36
        bwm.bwm_core.d2 = d2 if d2 is not None else 20
        
        return bwm