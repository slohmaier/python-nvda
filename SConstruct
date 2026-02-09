"""
SCons build system for python-nvda.

Downloads embedded Python and NVDA source to create a standalone Python
distribution with NVDA libraries for development/testing.

Usage:
    scons                          # Build everything (latest release)
    scons --nvda-version=2025.1    # Use specific NVDA version
    scons --nvda-version=head      # Use development HEAD
    scons --skip-32bit             # Skip 32-bit build (for NVDA 2026.1+)
    scons --list-versions          # Show available NVDA versions
    scons python32                 # Download 32-bit Python only
    scons python64                 # Download 64-bit Python only
    scons nvda32                   # Download NVDA source into 32-bit env
    scons nvda64                   # Download NVDA source into 64-bit env
    scons -c                       # Clean generated files

Environment variables:
    SSL_CERT_FILE      # Path to custom CA certificate (for ZScaler etc.)
"""

import json
import os
import urllib.request
import ssl
from zipfile import ZipFile
from io import BytesIO

# Configuration
PYTHON_VERSION = '3.13.1'

ARCHITECTURES = {
    '32': {'url_suffix': 'win32', 'dir': 'python32'},
    '64': {'url_suffix': 'amd64', 'dir': 'python64'},
}

NVDA_REPO = 'nvaccess/nvda'
NVDA_SOURCE_URL = 'https://github.com/{}/archive/refs/tags/{}.zip'
NVDA_HEAD_URL = 'https://codeload.github.com/{}/zip/refs/heads/master'
NVDA_API_URL = 'https://api.github.com/repos/{}/releases/latest'
NVDA_RELEASES_URL = 'https://api.github.com/repos/{}/releases?per_page=30'

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

def list_nvda_versions():
    """Print available NVDA versions from GitHub releases."""
    import re

    url = NVDA_RELEASES_URL.format(NVDA_REPO)
    releases = json.loads(download_url(url))

    stable = []
    betas = []
    for r in releases:
        tag = r['tag_name']
        if not r['prerelease']:
            stable.append(tag)
        elif re.search(r'beta\d*$', tag):
            betas.append(tag)

    print('\nAvailable NVDA versions:\n')

    print('  Stable releases (latest 5):')
    for tag in stable[:5]:
        print(f'    {tag}')

    if betas:
        print(f'\n  Latest beta:')
        print(f'    {betas[0]}')

    print(f'\n  Development:')
    print(f'    head  (master branch)')

    print(f'\nUsage: scons --nvda-version=<tag>')
    print(f'       scons --nvda-version=head\n')

# Builder factory functions (capture arch-specific paths via closure)

def make_download_python(python_dir, python_url, arch_bits):
    def download_python(target, source, env):
        """Download and extract embedded Python."""
        print(f'Downloading Python {PYTHON_VERSION} ({arch_bits}-bit)...')

        data = download_url(python_url)

        print('Extracting...')
        os.makedirs(python_dir, exist_ok=True)
        with ZipFile(BytesIO(data)) as zf:
            zf.extractall(python_dir)

        # Enable site-packages by uncommenting import site in ._pth file
        pth_file = os.path.join(python_dir, f'python{PYTHON_VERSION.replace(".", "")[:3]}._pth')
        if os.path.exists(pth_file):
            with open(pth_file, 'r') as f:
                content = f.read()
            content = content.replace('#import site', 'import site')
            with open(pth_file, 'w') as f:
                f.write(content)

        # Create Lib/site-packages directory
        site_packages = os.path.join(python_dir, 'Lib', 'site-packages')
        os.makedirs(site_packages, exist_ok=True)

        # Write marker file
        with open(str(target[0]), 'w') as f:
            f.write(PYTHON_VERSION)

        print(f'Python {arch_bits}-bit downloaded successfully.')
        return 0
    return download_python

def make_download_nvda(python_dir, site_packages):
    def download_nvda(target, source, env):
        """Download and extract NVDA source to site-packages."""
        nvda_version = GetOption('nvda_version')
        if not nvda_version:
            nvda_version = 'latest'

        nvda_tag = nvda_version

        if nvda_tag == 'latest':
            print('Determining latest NVDA version...')
            nvda_tag = get_latest_nvda_version()

        if nvda_tag == 'head':
            url = NVDA_HEAD_URL.format(NVDA_REPO)
        else:
            url = NVDA_SOURCE_URL.format(NVDA_REPO, nvda_tag)

        print(f'Downloading NVDA {nvda_tag} -> {python_dir}...')
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

                dest_path = os.path.join(site_packages, rel_path)

                if info.filename.endswith('/'):
                    os.makedirs(dest_path, exist_ok=True)
                else:
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    with open(dest_path, 'wb') as f:
                        f.write(zf.read(info))

        # Write version marker and requirements
        with open(str(target[0]), 'w') as f:
            f.write(nvda_tag)

        with open(os.path.join(python_dir, 'requirements.txt'), 'w') as f:
            f.write(requirements)

        print(f'NVDA {nvda_tag} extracted successfully.')
        return 0
    return download_nvda

def make_install_pip(python_dir):
    def install_pip(target, source, env):
        """Install pip using get-pip.py."""
        import subprocess

        print(f'Installing pip in {python_dir}...')
        python_exe = os.path.join(python_dir, 'python.exe')

        cmd = [python_exe, 'get-pip.py'] + get_trusted_host_args()
        result = subprocess.run(cmd, env=get_pip_env())

        if result.returncode != 0:
            return 1

        # Write marker
        with open(str(target[0]), 'w') as f:
            f.write('pip installed')

        print('pip installed successfully.')
        return 0
    return install_pip

def make_install_deps(python_dir):
    def install_deps(target, source, env):
        """Install dependencies from requirements.txt."""
        import subprocess

        req_file = os.path.join(python_dir, 'requirements.txt')
        if not os.path.exists(req_file):
            print('No requirements.txt found, skipping.')
            with open(str(target[0]), 'w') as f:
                f.write('no deps')
            return 0

        print(f'Installing dependencies in {python_dir}...')
        python_exe = os.path.join(python_dir, 'python.exe')

        cmd = [python_exe, '-m', 'pip', 'install', '-r', req_file] + get_trusted_host_args()
        result = subprocess.run(cmd, env=get_pip_env())

        if result.returncode != 0:
            print('Warning: Some dependencies may have failed to install.')

        # Write marker
        with open(str(target[0]), 'w') as f:
            f.write('deps installed')

        print('Dependencies installed.')
        return 0
    return install_deps

# Command-line options
AddOption('--nvda-version',
          dest='nvda_version',
          type='string',
          default='latest',
          metavar='VERSION',
          help='NVDA version to download (e.g., 2025.1, head, or latest)')

AddOption('--skip-32bit',
          dest='skip_32bit',
          action='store_true',
          default=False,
          help='Skip 32-bit Python build (for NVDA 2026.1+)')

AddOption('--list-versions',
          dest='list_versions',
          action='store_true',
          default=False,
          help='List available NVDA versions and exit')

# Handle --list-versions early
if GetOption('list_versions'):
    list_nvda_versions()
    Exit(0)

# Build per-architecture targets
all_deps_targets = []

for arch, cfg in ARCHITECTURES.items():
    if arch == '32' and GetOption('skip_32bit'):
        continue

    python_dir = cfg['dir']
    python_url = f'https://www.python.org/ftp/python/{PYTHON_VERSION}/python-{PYTHON_VERSION}-embed-{cfg["url_suffix"]}.zip'
    site_packages = os.path.join(python_dir, 'Lib', 'site-packages')

    # Create arch-specific environment with builders
    env_arch = Environment(
        BUILDERS={
            'DownloadPython': Builder(action=make_download_python(python_dir, python_url, arch)),
            'DownloadNVDA': Builder(action=make_download_nvda(python_dir, site_packages)),
            'InstallPip': Builder(action=make_install_pip(python_dir)),
            'InstallDeps': Builder(action=make_install_deps(python_dir)),
        }
    )

    # Marker files for dependency tracking
    python_marker = os.path.join(python_dir, '.python_version')
    nvda_marker = f'.nvda_version_{arch}'
    pip_marker = os.path.join(python_dir, '.pip_installed')
    deps_marker = os.path.join(python_dir, '.deps_installed')

    # Define targets with dependencies
    python_target = env_arch.DownloadPython(python_marker, [])
    nvda_target = env_arch.DownloadNVDA(nvda_marker, python_target)
    pip_target = env_arch.InstallPip(pip_marker, [python_target, 'get-pip.py'])
    deps_target = env_arch.InstallDeps(deps_marker, [pip_target, nvda_target])

    # Aliases for convenience
    env_arch.Alias(f'python{arch}', python_target)
    env_arch.Alias(f'nvda{arch}', nvda_target)
    env_arch.Alias(f'pip{arch}', pip_target)
    env_arch.Alias(f'deps{arch}', deps_target)

    # Clean targets
    Clean(python_target, [python_dir])
    Clean(nvda_target, [nvda_marker])

    all_deps_targets.append(deps_target)

# Default target builds all architectures
Default(all_deps_targets)
