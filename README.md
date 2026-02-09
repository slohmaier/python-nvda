# python-nvda

Embedded Python distribution with NVDA libraries for plugin development. Provides code-completion for the NVDA API.

Builds both 32-bit and 64-bit Python environments (NVDA 2025.x uses 32-bit, NVDA 2026.1+ uses 64-bit).

## Requirements

- [SCons](https://scons.org/) (`pip install scons`)
- Internet connection (downloads Python and NVDA on first build)

## Usage

```bash
# Build everything (downloads 32-bit + 64-bit Python, NVDA source, and dependencies)
scons

# Skip 32-bit build (for NVDA 2026.1+ only)
scons --skip-32bit

# Use the embedded Python for development
python32\python.exe your_script.py   # 32-bit (NVDA 2025.x)
python64\python.exe your_script.py   # 64-bit (NVDA 2026.1+)
```

## Build Targets

| Command | Description |
|---------|-------------|
| `scons` | Build everything (both architectures) |
| `scons --skip-32bit` | Build 64-bit only |
| `scons python32` | Download 32-bit embedded Python only |
| `scons python64` | Download 64-bit embedded Python only |
| `scons nvda32` | Download NVDA source into 32-bit env |
| `scons nvda64` | Download NVDA source into 64-bit env |
| `scons deps32` | Install pip dependencies (32-bit) |
| `scons deps64` | Install pip dependencies (64-bit) |
| `scons -c` | Clean generated files |

## Options

| Option | Description |
|--------|-------------|
| `--nvda-version=VERSION` | NVDA version to download (default: `latest`, or `head` for master) |
| `--skip-32bit` | Skip the 32-bit build |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `SSL_CERT_FILE` | Path to custom CA certificate (for ZScaler/corporate proxies) |

### Example with custom SSL certificate

```bash
SSL_CERT_FILE=C:/Apps/Zscaler_Root_CA.pem scons
```

### Example with specific NVDA version

```bash
scons --nvda-version=release-2025.1
```

## What Gets Downloaded

- **Python 3.13.1** (32-bit + 64-bit embeddable) - matches NVDA's Python version
- **NVDA source** - extracted to `pythonXX/Lib/site-packages/` for code completion
- **pip + dependencies** - from NVDA's requirements.txt
