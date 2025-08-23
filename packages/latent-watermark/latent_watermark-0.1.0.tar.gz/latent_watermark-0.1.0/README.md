# Latent Watermark

A robust latent watermark system for tracking image distribution. This package provides tools for embedding and extracting invisible watermarks in images to track buyer information and prevent unauthorized distribution.

## Installation

Install via pip:

```bash
pip install latent-watermark
```

Or install from source:

```bash
git clone https://github.com/yourusername/latent-watermark.git
cd latent-watermark
pip install -e .
```

## Quick Start

### Embed Watermark

Embed a watermark with buyer information:

```bash
# Basic usage
latent_watermark --embed --buyer 'john snow' example/

# With custom output directory
latent_watermark --embed --buyer 'john snow' example/ -o output_example/

# Single file
latent_watermark --embed --buyer 'john snow' image.jpg -o watermarked.jpg
```

### Extract Watermark

Extract watermark information from watermarked files:

```bash
# From directory
latent_watermark --extract example/

# From single file
latent_watermark --extract watermarked.jpg
```

### View Configuration

Show current watermark configuration:

```bash
latent_watermark --config
```

## Usage Examples

### Directory Processing

Process entire directories:

```bash
# Embed watermarks in all images in a directory
latent_watermark --embed --buyer 'alice@company.com' photos/

# Extract watermarks from all files in a directory
latent_watermark --extract watermarked_photos/
```

### Complex Buyer Names

Handle special characters and Unicode:

```bash
# Unicode names
latent_watermark --embed --buyer '测试用户' images/

# Names with spaces and special characters
latent_watermark --embed --buyer "O'Brien & Co." assets/

# Email addresses
latent_watermark --embed --buyer 'user@example.com' documents/
```

## Command Line Interface

### Options

- `--embed`: Embed watermark into files
- `--extract`: Extract watermark from files
- `--config`: Show current configuration
- `--buyer`: Buyer name for watermark embedding (required with --embed)
- `-o, --output`: Output directory/file path
- `input`: Input file or directory path

### Examples

```bash
# Help
latent_watermark --help

# Embed with output specification
latent_watermark --embed --buyer 'john snow' input.jpg -o watermarked.jpg

# Batch processing
latent_watermark --embed --buyer 'batch_user' images/ -o watermarked_images/

# Extraction
latent_watermark --extract watermarked_images/
```

## Development

### Setup Development Environment

```bash
git clone https://github.com/yourusername/latent-watermark.git
cd latent-watermark
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=latent_watermark

# Run specific test files
pytest tests/test_config_formatter.py -v
```

### Code Formatting

```bash
# Format code
black .
isort .

# Type checking
mypy latent_watermark/
```

## Architecture

### Core Components

- **WatermarkEmbedder**: Handles watermark embedding with fixed-length encoding
- **WatermarkExtractor**: Extracts watermarks using optimized bit length calculation
- **Configuration**: YAML-based configuration system with fixed-length settings
- **CLI**: Command-line interface for embedding and extraction
- **Validation**: Robust input validation and error handling

### Simplified Watermark Format

The system uses a **streamlined watermark format** optimized for essential information:

- **Format**: `author:buyer:date:hash` (4 fields)
- **Date**: 8-digit format `yyMMddHH` (e.g., `25082000` = Aug 20, 2025, 00:00)
- **Hash**: Last 4 digits of MD5 hash for compact verification
- **Author**: Optional, falls back to config default
- **Buyer**: Mandatory parameter for each watermark
- **Fixed Length**: All watermarks padded to consistent length for reliable extraction

### Configuration

Configure author and length via YAML:

```yaml
watermark:
  author: "your_author_name"  # Default author when not specified
  encoding:
    fixed_length: 32  # Fixed length for all watermarks
    max_total_length: 128  # Increased from 32 for better flexibility
  quality:
    d1: 36  # d1/d2 越大鲁棒性越强,但输出图片的失真越大
    d2: 20  # d1/d2 越大鲁棒性越强,但输出图片的失真越大
```

## Quality Configuration

Adjust watermark robustness vs image quality trade-offs:

```yaml
watermark:
  quality:
    d1: 36  # Higher values increase robustness but may increase image distortion
    d2: 20  # Higher values increase robustness but may increase image distortion
```

- **d1/d2**: Control watermark embedding strength
- **Higher values**: More robust against attacks, but may cause visible artifacts
- **Lower values**: Less visible artifacts, but potentially less robust
- **Default**: d1=36, d2=20 provides good balance

## Watermark Format Details

### Field Structure
- **Author**: 1-16 characters (configurable default)
- **Buyer**: 1-16 characters (mandatory parameter)
- **Date**: 8 digits exactly (yyMMddHH format)
- **Hash**: 4 hex digits exactly (last 4 of MD5)

### Example Watermarks
- `john_doe:alice_smith:25082000:7a3f`
- `default_author:bob_jones:25082000:e4d2`

### Usage Examples
```bash
# Basic usage
latent_watermark --embed --buyer "alice_smith" images/

# With custom author
latent_watermark --embed --buyer "alice_smith" --author "john_doe" images/

# Extract watermark
latent_watermark --extract watermarked/
```

## Error Handling

The system provides comprehensive error handling:

- **Invalid buyer names**: Rejected with clear error messages
- **Malformed watermarks**: Detected during extraction
- **Missing files**: Handled gracefully with helpful messages
- **Configuration errors**: Validated on startup

## Security Features

- **Unique buyer tracking**: Each watermark contains buyer-specific information
- **Tamper detection**: Watermark integrity validation
- **Format validation**: Strict format checking prevents injection attacks
- **Unicode support**: Handles international buyer names safely

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Submit a pull request

## Support

For issues and questions:
- GitHub Issues: https://github.com/yourusername/latent-watermark/issues
- Documentation: https://latent-watermark.readthedocs.io