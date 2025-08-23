"""Core watermark functionality using blind_watermark."""

import os
import io
import tempfile
from pathlib import Path
from typing import Union, List, Optional
from PIL import Image

from blind_watermark import WaterMark
from contextlib import contextmanager

from .watermark_utils import WatermarkInitializer
from .config import get_config


@contextmanager
def suppress_output():
    """Context manager to suppress stdout/stderr output from blind_watermark."""
    import sys
    from io import StringIO
    
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    stdout_buffer = StringIO()
    stderr_buffer = StringIO()
    
    try:
        sys.stdout = stdout_buffer
        sys.stderr = stderr_buffer
        yield
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr


class WatermarkEmbedder:
    """Embeds watermarks into images using blind_watermark."""
    
    def __init__(self, password_img: int = 1, password_wm: int = 1, fixed_length: int = 128) -> None:
        """Initialize watermark embedder.
        
        Args:
            password_img: Password for image encryption
            password_wm: Password for watermark encryption
            fixed_length: Fixed length for watermark strings (default: 128)
        """
        self.password_img = password_img
        self.password_wm = password_wm
        self.fixed_length = fixed_length
        
        # Load quality settings from config
        config = get_config()
        quality_config = config.get('watermark', {}).get('quality', {})
        self.d1 = quality_config.get('d1', 36)
        self.d2 = quality_config.get('d2', 20)

    def _encode_watermark(self, buyer_id: str) -> str:
        """Encode watermark string to fixed byte length."""
        # Get current timestamp for date
        from datetime import datetime
        date_str = datetime.now().strftime("%y%m%d%H")
        
        # Create watermark string
        watermark = f"{buyer_id}:{date_str}"
        
        # Ensure we don't exceed fixed_length
        if len(watermark.encode('utf-8')) > self.fixed_length:
            # Truncate if necessary
            watermark_bytes = watermark.encode('utf-8')[:self.fixed_length]
            watermark = watermark_bytes.decode('utf-8', errors='ignore')
        
        # Re-encode to ensure we have correct byte length
        watermark_bytes = watermark.encode('utf-8')
        
        # Pad with null bytes to reach fixed length
        padding_needed = self.fixed_length - len(watermark_bytes)
        padded_bytes = watermark_bytes + b'\x00' * padding_needed
        
        # Convert back to string for blind-watermark
        return padded_bytes.decode('utf-8', errors='ignore')

    def _load_image(self, image: Union[str, Path, bytes]) -> str:
        """Load image from various input types and return file path."""
        if isinstance(image, (str, Path)):
            return str(image)
        elif isinstance(image, bytes):
            # Save bytes to temporary file
            temp_path = Path("temp_image.png")
            img = Image.open(io.BytesIO(image))
            img.save(temp_path)
            return str(temp_path)
        else:
            raise ValueError("Unsupported image type")

    def embed(
        self, 
        image: Union[str, Path, bytes], 
        buyer_id: Optional[str] = None
    ) -> bytes:
        """Embed a latent watermark into an image."""
        if not buyer_id:
            raise ValueError("buyer_id is required for embedding")

        # Encode watermark to fixed byte length
        watermark = self._encode_watermark(buyer_id)
        
        # Verify the byte length is exactly fixed_length
        watermark_bytes = watermark.encode('utf-8')
        if len(watermark_bytes) != self.fixed_length:
            # Adjust padding if needed
            watermark_bytes = watermark_bytes[:self.fixed_length]
            if len(watermark_bytes) < self.fixed_length:
                watermark_bytes += b'\x00' * (self.fixed_length - len(watermark_bytes))
            watermark = watermark_bytes.decode('utf-8', errors='ignore')
        
        # Load image
        img_path = self._load_image(image)
        
        # Create temporary output file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_out:
            try:
                # Initialize watermark embedder with quality settings
                with suppress_output():
                    bwm = WatermarkInitializer.init_watermark(
                        password_img=self.password_img,
                        password_wm=self.password_wm,
                        d1=self.d1,
                        d2=self.d2
                    )
                
                # Read image
                bwm.read_img(img_path)
                
                # Embed watermark using string mode
                bwm.read_wm(watermark, mode='str')
                
                # Calculate the actual bit length needed for extraction
                # Each byte becomes 8 bits in the watermark
                self._extraction_bit_length = len(watermark.encode('utf-8')) * 8
                
                # Embed watermark
                bwm.embed(tmp_out.name)
                
                # Read result
                with open(tmp_out.name, 'rb') as f:
                    result = f.read()
                
                return result
                
            finally:
                # Clean up temporary file
                try:
                    os.unlink(tmp_out.name)
                except OSError:
                    pass
                # Clean up temporary image file
                if str(img_path).startswith("temp_image"):
                    Path(img_path).unlink(missing_ok=True)

    def embed_batch(
        self, 
        images: List[Union[str, Path, bytes]], 
        buyer_id: Optional[str] = None
    ) -> List[bytes]:
        """Embed watermarks into multiple images."""
        return [self.embed(img, buyer_id) for img in images]


class WatermarkExtractor:
    """Extracts watermarks from images using blind_watermark."""
    
    def __init__(self, password_img: int = 1, password_wm: int = 1, fixed_length: int = 128) -> None:
        """Initialize watermark embedder.
        
        Args:
            password_img: Password for image encryption
            password_wm: Password for watermark encryption
            fixed_length: Fixed length for watermark strings (default: 128)
        """
        self.password_img = password_img
        self.password_wm = password_wm
        self.fixed_length = fixed_length
        
        # Load quality settings from config
        config = get_config()
        quality_config = config.get('watermark', {}).get('quality', {})
        self.d1 = quality_config.get('d1', 36)
        self.d2 = quality_config.get('d2', 20)

    def _load_image(self, image: Union[str, Path, bytes]) -> str:
        """Load image from various input types and return file path."""
        if isinstance(image, (str, Path)):
            return str(image)
        elif isinstance(image, bytes):
            # Save bytes to temporary file
            temp_path = Path("temp_image.png")
            img = Image.open(io.BytesIO(image))
            img.save(temp_path)
            return str(temp_path)
        else:
            raise ValueError("Unsupported image type")

    def extract(self, image: Union[str, Path, bytes]) -> Optional[str]:
        """Extract watermark from a single image."""
        try:
            # Get image path
            img_path = self._load_image(image)

            # Initialize watermark extractor with quality settings
            with suppress_output():
                bwm = WatermarkInitializer.init_watermark(
                    password_img=self.password_img,
                    password_wm=self.password_wm,
                    d1=self.d1,
                    d2=self.d2
                )

                # Calculate the correct bit length for extraction
                # Based on fixed byte length: fixed_length * 8 bits
                extraction_length = self.fixed_length * 8
                
                # Extract watermark using the calculated bit length
                extracted = bwm.extract(str(img_path), wm_shape=extraction_length, mode='str')

                # Clean up temporary file if used
                if str(img_path).startswith("temp_image"):
                    Path(img_path).unlink(missing_ok=True)

                # Clean up the extracted string (remove null bytes and padding)
                if extracted:
                    # Remove null bytes and trim whitespace
                    cleaned = extracted.replace('\x00', '').strip()
                    
                    # Remove padding spaces (added during embedding)
                    cleaned = cleaned.rstrip()
                    
                    # Return None if the result is empty after cleaning
                    if not cleaned or cleaned.isspace():
                        return None
                    
                    # Decode as UTF-8 to handle Chinese characters properly
                    try:
                        # Ensure we have valid UTF-8
                        cleaned.encode('utf-8')
                        return cleaned
                    except UnicodeError:
                        # If we have encoding issues, return raw string
                        return cleaned

                return None

        except Exception as e:
            # Handle extraction errors gracefully
            print(f"Error extracting watermark: {e}")
            return None

    def extract_batch(
        self, 
        images: List[Union[str, Path, bytes]]
    ) -> List[Optional[str]]:
        """Extract watermarks from multiple images."""
        return [self.extract(img) for img in images]