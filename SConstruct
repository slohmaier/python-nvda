"""
SCons build system for python-nvda.

Downloads embedded Python and NVDA source to create a standalone Python
distribution with NVDA libraries for development/testing.

Usage:
    scons              # Build everything
    scons python       # Download embedded Python only
    scons nvda         # Download NVDA source only
    scons deps         # Install pip dependencies only
    scons -c           # Clean generated files

Environment variables:
    SSL_CERT_FILE      # Path to custom CA certificate (for ZScaler etc.)
    NVDA_TAG           # NVDA version tag (default: latest)
"""

import json
import os
import urllib.request
import ssl
from zipfile import ZipFile
from io import BytesIO

# Configuration
PYTHON_VERSION = '3.13.1'
PYTHON_ARCH = '32'  # NVDA uses 32-bit Python
PYTHON_URL = f'https://www.python.org/ftp/python/{PYTHON_VERSION}/python-{PYTHON_VERSION}-embed-win{PYTHON_ARCH}.zip'
PYTHON_DIR = 'python'

NVDA_REPO = 'nvaccess/nvda'
NVDA_SOURCE_URL = 'https://github.com/{}/archive/refs/tags/{}.zip'
NVDA_HEAD_URL = 'https://codeload.github.com/{}/zip/refs/heads/master'
NVDA_API_URL = 'https://api.github.com/repos/{}/releases/latest'

SITE_PACKAGES = os.path.join(PYTHON_DIR, 'Lib', 'site-packages')
VERSION_FILE = '.nvda_version'

PIP_TRUSTED_HOSTS = ['pypi.org', 'pypi.python.org', 'files.pythonhosted.org']

# SSL configuration
SSL_CERT = os.environ.get('SSL_CERT_FILE', None)

def get_ssl_context():
    """Create SSL context with custom cert if specified."""
    if SSL_CERT:
        ctx = ssl.create_default_context(cafile=SSL_CERT)
    else:
        ctx = ssl.create_default_context()
    return ctx

def get_trusted_host_args():
    """Return --trusted-host args for pip if SSL_CERT is set."""
    if SSL_CERT:
        args = []
        for host in PIP_TRUSTED_HOSTS:
            args.extend(['--trusted-host', host])
        return args
    return []

def get_pip_env():
    """Get environment for pip with SSL cert configured."""
    env = os.environ.copy()
    if SSL_CERT:
        env['SSL_CERT_FILE'] = SSL_CERT
        env['PIP_CERT'] = SSL_CERT
        env['REQUESTS_CA_BUNDLE'] = SSL_CERT
    return env

def download_url(url):
    """Download URL content with SSL support."""
    ctx = get_ssl_context()
    req = urllib.request.Request(url, headers={'User-Agent': 'python-nvda/1.0'})
    with urllib.request.urlopen(req, context=ctx) as response:
        return response.read()

def get_latest_nvda_version():
    """Fetch latest NVDA release tag from GitHub API."""
    url = NVDA_API_URL.format(NVDA_REPO)
    data = json.loads(download_url(url))
    return data['tag_name']

# Builder functions
def download_python(target, source, env):
    """Download and extract embedded Python."""
    print(f'Downloading Python {PYTHON_VERSION} ({PYTHON_ARCH}-bit)...')

    data = download_url(PYTHON_URL)

    print('Extracting...')
    os.makedirs(PYTHON_DIR, exist_ok=True)
    with ZipFile(BytesIO(data)) as zf:
        zf.extractall(PYTHON_DIR)

    # Enable site-packages by uncommenting import site in ._pth file
    pth_file = os.path.join(PYTHON_DIR, f'python{PYTHON_VERSION.replace(".", "")[:3]}._pth')
    if os.path.exists(pth_file):
        with open(pth_file, 'r') as f:
            content = f.read()
        content = content.replace('#import site', 'import site')
        with open(pth_file, 'w') as f:
            f.write(content)

    # Create Lib/site-packages directory
    os.makedirs(SITE_PACKAGES, exist_ok=True)

    # Write marker file
    with open(str(target[0]), 'w') as f:
        f.write(PYTHON_VERSION)

    print('Python downloaded successfully.')
    return 0

def download_nvda(target, source, env):
    """Download and extract NVDA source to site-packages."""
    nvda_tag = os.environ.get('NVDA_TAG', 'latest')

    if nvda_tag == 'latest':
        print('Determining latest NVDA version...')
        nvda_tag = get_latest_nvda_version()

    if nvda_tag == 'head':
        url = NVDA_HEAD_URL.format(NVDA_REPO)
    else:
        url = NVDA_SOURCE_URL.format(NVDA_REPO, nvda_tag)

    print(f'Downloading NVDA {nvda_tag}...')
    data = download_url(url)

    print('Extracting to site-packages...')
    requirements = ''

    with ZipFile(BytesIO(data)) as zf:
        # Find source prefix (first entry is root dir)
        source_prefix = zf.filelist[0].filename + 'source/'

        for info in zf.filelist[1:]:
            # Capture requirements.txt
            if info.filename.endswith('requirements.txt'):
                requirements = zf.read(info).decode('utf-8')

            # Only extract source files
            if not info.filename.startswith(source_prefix):
                continue

            # Generate path relative to site-packages
            rel_path = '/'.join(info.filename.split('/')[2:])
            if not rel_path:
                continue

            dest_path = os.path.join(SITE_PACKAGES, rel_path)

            if info.filename.endswith('/'):
                os.makedirs(dest_path, exist_ok=True)
            else:
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                with open(dest_path, 'wb') as f:
                    f.write(zf.read(info))

    # Write version marker and requirements
    with open(str(target[0]), 'w') as f:
        f.write(nvda_tag)

    with open(os.path.join(PYTHON_DIR, 'requirements.txt'), 'w') as f:
        f.write(requirements)

    print(f'NVDA {nvda_tag} extracted successfully.')
    return 0

def install_pip(target, source, env):
    """Install pip using get-pip.py."""
    import subprocess

    print('Installing pip...')
    python_exe = os.path.join(PYTHON_DIR, 'python.exe')

    cmd = [python_exe, 'get-pip.py'] + get_trusted_host_args()
    result = subprocess.run(cmd, env=get_pip_env())

    if result.returncode != 0:
        return 1

    # Write marker
    with open(str(target[0]), 'w') as f:
        f.write('pip installed')

    print('pip installed successfully.')
    return 0

def install_deps(target, source, env):
    """Install dependencies from requirements.txt."""
    import subprocess

    req_file = os.path.join(PYTHON_DIR, 'requirements.txt')
    if not os.path.exists(req_file):
        print('No requirements.txt found, skipping.')
        with open(str(target[0]), 'w') as f:
            f.write('no deps')
        return 0

    print('Installing dependencies...')
    python_exe = os.path.join(PYTHON_DIR, 'python.exe')

    cmd = [python_exe, '-m', 'pip', 'install', '-r', req_file] + get_trusted_host_args()
    result = subprocess.run(cmd, env=get_pip_env())

    if result.returncode != 0:
        print('Warning: Some dependencies may have failed to install.')

    # Write marker
    with open(str(target[0]), 'w') as f:
        f.write('deps installed')

    print('Dependencies installed.')
    return 0

# Create builders
python_builder = Builder(action=download_python)
nvda_builder = Builder(action=download_nvda)
pip_builder = Builder(action=install_pip)
deps_builder = Builder(action=install_deps)

# Environment setup
env = Environment(
    BUILDERS={
        'DownloadPython': python_builder,
        'DownloadNVDA': nvda_builder,
        'InstallPip': pip_builder,
        'InstallDeps': deps_builder,
    }
)

# Marker files for dependency tracking
python_marker = os.path.join(PYTHON_DIR, '.python_version')
nvda_marker = VERSION_FILE
pip_marker = os.path.join(PYTHON_DIR, '.pip_installed')
deps_marker = os.path.join(PYTHON_DIR, '.deps_installed')

# Define targets with dependencies
python_target = env.DownloadPython(python_marker, [])
nvda_target = env.DownloadNVDA(nvda_marker, python_target)
pip_target = env.InstallPip(pip_marker, [python_target, 'get-pip.py'])
deps_target = env.InstallDeps(deps_marker, [pip_target, nvda_target])

# Aliases for convenience
env.Alias('python', python_target)
env.Alias('nvda', nvda_target)
env.Alias('pip', pip_target)
env.Alias('deps', deps_target)

# Default target builds everything
Default(deps_target)

# Clean targets
Clean(python_target, [PYTHON_DIR])
Clean(nvda_target, [VERSION_FILE])
