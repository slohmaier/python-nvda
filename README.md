# python-nvda

Embedded Python distribution with NVDA libraries for plugin development. Provides code-completion for the NVDA API.

## Requirements

- [SCons](https://scons.org/) (`pip install scons`)
- Internet connection (downloads Python and NVDA on first build)

## Usage

```bash
# Build everything (downloads Python 3.13, NVDA source, and dependencies)
scons

# Use the embedded Python for development
python\python.exe your_script.py
```

## Build Targets

| Command | Description |
|---------|-------------|
| `scons` | Build everything |
| `scons python` | Download embedded Python only |
| `scons nvda` | Download NVDA source only |
| `scons deps` | Install pip dependencies only |
| `scons -c` | Clean generated files |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `SSL_CERT_FILE` | Path to custom CA certificate (for ZScaler/corporate proxies) |
| `NVDA_TAG` | NVDA version tag to download (default: `latest`, or use `head` for master) |

### Example with custom SSL certificate

```bash
SSL_CERT_FILE=C:/Apps/Zscaler_Root_CA.pem scons
```

### Example with specific NVDA version

```bash
NVDA_TAG=release-2025.1 scons
```

## What Gets Downloaded

- **Python 3.13.1** (32-bit embeddable) - matches NVDA's Python version
- **NVDA source** - extracted to `python/Lib/site-packages/` for code completion
- **pip + dependencies** - from NVDA's requirements.txt
