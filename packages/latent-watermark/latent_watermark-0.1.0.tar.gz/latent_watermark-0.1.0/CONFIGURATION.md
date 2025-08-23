# Configuration Guide

This guide explains how to configure the latent_watermark system using the new YAML-based configuration.

## Overview

The system uses a YAML configuration file located at `~/.config/latent_watermark/config.yml` by default. The configuration is validated on startup, and any errors will be clearly reported with guidance on how to fix them.

## Configuration Sections

### Security Settings (`security`)

Controls security-related aspects of watermark generation.

| Setting | Type | Range | Default | Description |
|---------|------|-------|---------|-------------|
| `hash_algorithm` | string | sha256, sha512, md5, sha1, blake2b | sha256 | Algorithm used for generating unique identifiers |
| `key_length` | integer | 16-64 | 32 | Length of encryption keys in bytes |
| `default_password` | string | min 8 chars | latent_watermark_2024 | Default password for encryption (change this!) |

### Watermark Settings (`watermark`)

Controls how watermarks are generated and formatted.

| Setting | Type | Range | Default | Description |
|---------|------|-------|---------|-------------|
| `max_total_length` | integer | 10-512 | 256 | Maximum total length for watermark string |

#### Quality Settings (`watermark.quality`)

| Setting | Type | Range | Default | Description |
|---------|------|-------|---------|-------------|
| `d1` | integer | 1-100 | 15 | Higher values = more robust but more image distortion |
| `d2` | integer | 1-100 | 75 | Lower values = more robust but more image distortion |

#### Field Configuration (`watermark.fields`)

Each field can be configured individually:

**Author Field (`watermark.fields.author`)**
| Setting | Type | Range | Default | Description |
|---------|------|-------|---------|-------------|
| `min_length` | integer | 0-50 | 1 | Minimum length for author field |
| `max_length` | integer | 1-100 | 30 | Maximum length for author field |

**Buyer Field (`watermark.fields.buyer`)**
| Setting | Type | Range | Default | Description |
|---------|------|-------|---------|-------------|
| `min_length` | integer | 0-50 | 1 | Minimum length for buyer field |
| `max_length` | integer | 1-100 | 50 | Maximum length for buyer field |

**Date Field (`watermark.fields.date`)**
| Setting | Type | Range | Default | Description |
|---------|------|-------|---------|-------------|
| `format` | string | ISO, US, EU, CUSTOM | ISO | Date format to use |

**Hash Field (`watermark.fields.hash`)**
| Setting | Type | Range | Default | Description |
|---------|------|-------|---------|-------------|
| `last_n_digits` | integer | 1-16 | 8 | Number of digits to display from hash |

### Output Settings (`output`)

Controls how processed images are saved.

| Setting | Type | Range | Default | Description |
|---------|------|-------|---------|-------------|
| `format` | string | png, jpg, jpeg, webp, bmp, tiff | png | Output image format |
| `quality` | integer | 1-100 | 95 | Output image quality (only affects lossy formats) |
| `directory` | string | any valid path | "" | Output directory (empty = input directory) |

## Configuration Validation

The system performs comprehensive validation on startup:

- **Required sections**: All sections (security, watermark, output) must be present
- **Valid ranges**: All numeric values must be within specified ranges
- **Valid formats**: String values must match allowed formats
- **Type checking**: All values must be of the correct type

If validation fails, you'll see clear error messages like:

```
Configuration validation failed:
  - output.format 'invalid' is invalid. Must be one of: bmp, jpg, jpeg, png, tiff, webp
  - output.quality 150 is invalid. Must be between 1 and 100

Please edit the configuration file directly to fix these issues.
```

## Common Issues and Solutions

### 1. Missing Configuration Sections

**Error**: `Missing required section: output`

**Solution**: Add the missing section to your config.yml:

```yaml
output:
  format: png
  quality: 95
  directory: ""
```

### 2. Invalid Output Format

**Error**: `output.format 'jpeg' is invalid. Must be one of: bmp, jpg, jpeg, png, tiff, webp`

**Solution**: Use a valid format from the list:

```yaml
output:
  format: jpg  # or jpeg, png, etc.
```

### 3. Quality Out of Range

**Error**: `output.quality 150 is invalid. Must be between 1 and 100`

**Solution**: Adjust quality to be within 1-100:

```yaml
output:
  quality: 95  # Valid range: 1-100
```

### 4. Invalid Hash Algorithm

**Error**: `security.hash_algorithm 'md4' is invalid. Must be one of: blake2b, md5, sha1, sha256, sha512`

**Solution**: Use a supported algorithm:

```yaml
security:
  hash_algorithm: sha256  # or any from the list
```

## Regenerating Configuration

If your configuration is corrupted or you want to start fresh:

1. Delete your current configuration file:
   ```bash
   rm ~/.config/latent_watermark/config.yml
   ```

2. Run any latent_watermark command to regenerate with defaults

## Example Configuration

Here's a complete example configuration:

```yaml
security:
  hash_algorithm: sha256
  key_length: 32
  default_password: "my_secure_password_2024"

watermark:
  max_total_length: 256
  quality:
    d1: 60
    d2: 80
  fields:
    author:
      min_length: 2
      max_length: 25
    buyer:
      min_length: 3
      max_length: 40
    date:
      format: "ISO"
    hash:
      last_n_digits: 10

output:
  format: jpg
  quality: 90
  directory: "/Users/me/watermarked_images"
```

## Environment Variables

You can override the configuration directory using the `LATENT_WATERMARK_CONFIG_DIR` environment variable:

```bash
export LATENT_WATERMARK_CONFIG_DIR="/path/to/config"
```