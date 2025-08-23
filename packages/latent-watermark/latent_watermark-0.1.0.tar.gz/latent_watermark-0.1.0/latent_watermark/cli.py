#!/usr/bin/env python3
"""
Main CLI interface for latent watermark embedding and extraction.

This is the primary entry point for the latent-watermark package.
Users can install via pip and use:

    latent_watermark --embed --buyer 'john snow' example/ -o output_example/
    latent_watermark --extract example/
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Optional, List

from .config import get_config
from .config_formatter import WatermarkFormatter
from .watermark import WatermarkEmbedder, WatermarkExtractor
from .file_utils import SafeFileManager


class WatermarkService:
    """Main service class for watermark operations using blind_watermark."""
    
    def __init__(self, password_img: int = 1, password_wm: int = 1):
        self.config = get_config()
        self.formatter = WatermarkFormatter(self.config)
        
        # Get fixed length from config
        watermark_config = self.config.get('watermark', {})
        fixed_length = watermark_config.get('max_total_length', 128)
        
        self.embedder = WatermarkEmbedder(
            password_img=password_img, 
            password_wm=password_wm,
            fixed_length=fixed_length
        )
        self.extractor = WatermarkExtractor(
            password_img=password_img, 
            password_wm=password_wm,
            fixed_length=fixed_length
        )
    
    def _get_image_files(self, path: str) -> List[Path]:
        """Get all image files from a path (file or directory)."""
        path_obj = Path(path)
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
        
        if path_obj.is_file():
            return [path_obj] if path_obj.suffix.lower() in image_extensions else []
        elif path_obj.is_dir():
            return [f for f in path_obj.rglob("*") 
                   if f.suffix.lower() in image_extensions and f.is_file()]
        else:
            return []
    
    def embed_watermark(self, input_path: str, buyer: str, output_path: Optional[str] = None, author: Optional[str] = None, overwrite: bool = False) -> str:
        """
        Embed watermark into images using blind_watermark.
        
        Args:
            input_path: Path to input directory/files
            buyer: Buyer name for watermark
            output_path: Output directory (optional)
            author: Optional author name, falls back to config value
            overwrite: Whether to overwrite existing files (default: False)
            
        Returns:
            Generated watermark string (buyer ID)
        """
        # Simple validation - just ensure buyer is not empty
        if not buyer or not buyer.strip():
            raise ValueError("Buyer name cannot be empty")
        
        # Use configured author if not provided
        if author is None:
            author = self.formatter.author_default
        
        # Use configured formatter to generate watermark
        watermark = self.formatter.format_watermark(buyer.strip(), author=author)
        
        # Get image files
        image_files = self._get_image_files(input_path)
        if not image_files:
            raise ValueError(f"No image files found in: {input_path}")
        
        # Determine output directory
        if not output_path:
            input_obj = Path(input_path)
            if input_obj.is_file():
                output_dir = input_obj.parent / f"{input_obj.stem}_watermarked"
            else:
                output_dir = input_obj.parent / f"{input_obj.name}_watermarked"
        else:
            output_dir = Path(output_path)
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Process each image
        processed_count = 0
        print(f"🎯 Embedding watermark for buyer: {buyer}")
        if author:
            print(f"✍️  Author: {author}")
        print(f"📁 Input: {input_path}")
        print(f"📁 Output: {output_dir}")
        print(f"🏷️  Full watermark: '{watermark}'")
        print(f"📊 Processing {len(image_files)} image(s)...")
        
        for img_path in image_files:
            try:
                # Read image
                with open(img_path, 'rb') as f:
                    img_data = f.read()
                
                # Embed watermark
                watermarked_data = self.embedder.embed(img_data, watermark)
                
                # Save watermarked image with optional uniqueness
                output_file = SafeFileManager.safe_save(
                    watermarked_data,
                    output_dir / img_path.name,
                    ensure_unique=not overwrite
                )
                
                print(f"   ✅ {img_path} → {output_file}")
                processed_count += 1
                
            except Exception as e:
                print(f"   ❌ Failed to process {img_path}: {e}")
        
        if processed_count == 0:
            raise RuntimeError("No images were successfully processed")
        
        return watermark
    
    def extract_watermark(self, input_path: str) -> Optional[str]:
        """
        Extract watermark from images using blind_watermark.
        
        Args:\            input_path: Path to input directory/files
            
        Returns:
            Extracted full watermark string or None if not found
        """
        print(f"🔍 Extracting watermark from: {input_path}")
        
        # Get image files
        image_files = self._get_image_files(input_path)
        if not image_files:
            raise ValueError(f"No image files found in: {input_path}")
        
        found_watermarks = []
        
        for img_path in image_files:
            try:
                # Read image
                with open(img_path, 'rb') as f:
                    img_data = f.read()
                
                # Extract watermark
                extracted = self.extractor.extract(img_data)
                
                if extracted:
                    # The extracted value should already be the full formatted watermark
                    found_watermarks.append(extracted)
                    print(f"   📄 Found in: {img_path}")
                    print(f"   🏷️  Full watermark: '{extracted}'")
                    
                    break  # Return first found watermark
                    
            except Exception as e:
                print(f"   ❌ Failed to process {img_path}: {e}")
        
        if found_watermarks:
            watermark = found_watermarks[0]
            print(f"\n✅ Extracted full watermark: '{watermark}'")
            return watermark
        else:
            print("❌ No watermark found")
            return None


def cmd_embed(args):
    """Handle embed command."""
    service = WatermarkService()
    
    try:
        watermark = service.embed_watermark(
            input_path=args.input,
            buyer=args.buyer,
            output_path=args.output,
            author=args.author,
            overwrite=args.overwrite
        )
        
        print(f"\n🎉 Successfully embedded watermark!")
        print(f"Final full watermark: '{watermark}'")
        return 0
        
    except Exception as e:
        print(f"❌ Embed failed: {e}")
        return 1


def cmd_extract(args):
    """Handle extract command."""
    service = WatermarkService()
    
    try:
        watermark = service.extract_watermark(args.input)
        
        if watermark:
            print(f"\n✅ Successfully extracted watermark!")
            print(f"Extracted full watermark: '{watermark}'")
            return 0
        else:
            print("❌ No watermark found in input")
            return 1
            
    except Exception as e:
        print(f"❌ Extract failed: {e}")
        return 1


def create_parser():
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog="latent_watermark",
        description="Latent watermark embedding and extraction tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Embed watermark
  latent_watermark --embed --buyer 'john snow' example/
  latent_watermark --embed --buyer 'john snow' --author 'arya stark' image.jpg -o watermarked.jpg
  
  # Embed with overwrite
  latent_watermark --embed --buyer 'john snow' --overwrite image.jpg
  
  # Extract watermark
  latent_watermark --extract watermarked/
  latent_watermark --extract watermarked.jpg
  
  # Show configuration
  latent_watermark --config
        """
    )
    
    # Main commands
    parser.add_argument(
        "--embed", 
        action="store_true",
        help="Embed watermark into files"
    )
    
    parser.add_argument(
        "--extract",
        action="store_true", 
        help="Extract watermark from files"
    )
    
    parser.add_argument(
        "--config",
        action="store_true",
        help="Show current configuration"
    )
    
    # Arguments for embed
    parser.add_argument(
        "--buyer",
        type=str,
        help="Buyer name for watermark embedding (mandatory)"
    )
    
    parser.add_argument(
        "--author",
        type=str,
        help="Author name (optional, uses config default if not provided)"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Output directory/file path"
    )
    
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow overwriting existing files (default: create unique filenames)"
    )
    
    # Input argument
    parser.add_argument(
        "input",
        nargs="?",
        help="Input file or directory path"
    )
    
    return parser


def cmd_config():
    """Show configuration details."""
    try:
        config = get_config()
        formatter = WatermarkFormatter(config)
        
        print("📋 Current Configuration:")
        print("=" * 50)
        
        # Show format
        format_str = config.get('watermark', {}).get('structure', {}).get('format', 'unknown')
        print(f"Format: {format_str}")
        
        # Show fields
        fields = config.get('watermark', {}).get('structure', {}).get('fields', {})
        print(f"Fields: {len(fields)}")
        for name, config in fields.items():
            print(f"  {name}: {config}")
        
        # Show required fields
        required = formatter.list_required_fields()
        print(f"Required: {required}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error showing config: {e}")
        return 1


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Handle no arguments
    if not any([args.embed, args.extract, args.config]):
        parser.print_help()
        return 1
    
    # Handle config
    if args.config:
        return cmd_config()
    
    # Handle missing input
    if not args.input:
        print("❌ Error: input path is required")
        return 1
    
    # Handle commands
    if args.embed:
        if not args.buyer:
            print("❌ Error: --buyer is required for embedding")
            return 1
        return cmd_embed(args)
    
    elif args.extract:
        return cmd_extract(args)
    
    return 1


if __name__ == "__main__":
    sys.exit(main())