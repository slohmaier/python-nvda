import os
import requests
import subprocess
from io import BytesIO
from zipfile import ZipFile

NVDA_SOURCE_URL='https://github.com/nvaccess/nvda/archive/refs/tags/release-2023.1.zip'
SCRIPTDIR = os.path.dirname(os.path.abspath(__file__))
SITE_DIR='Lib/site-packages'

if __name__ == '__main__':
    print('Downloading latest NVDA tag...')
    res = requests.get(NVDA_SOURCE_URL)
    print('DONE!\n')

    print ('Unzipping to python-distributions...')
    zipIO = BytesIO(res.content)
    z = ZipFile(zipIO)
    pythons = []
    for d in os.listdir(SCRIPTDIR):
        if os.path.isdir(d) and d.startswith('python'):
            pythons.append(d)
    
    requirements = ''

    sourcePrefix = z.filelist[0].filename + 'source/'
    for f in z.filelist[1:]:
        if f.filename.endswith('requirements.txt'):
            requirements = z.read(f).decode('utf-8')

        if not f.filename.startswith(sourcePrefix):
            continue

        destf = '/'.join(f.filename.split('/')[2:])
        print(destf)
        
        for python in pythons:
            path = os.path.join(SCRIPTDIR, python, SITE_DIR, destf)

            if f.filename[-1] != '/':
                print(f)
                if os.path.isfile(path):
                    os.remove(path)
                _bytes = z.read(f)

                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, 'wb+') as _f:
                    _f.write(_bytes)

    print('DONE!\n')

    print('Installing pip dependencies')
    for line in requirements.split('\n'):
        line = line.strip()
        if line and not line.startswith('#'):
            for python in pythons:
                with open(os.path.join(SCRIPTDIR, python, 'pip-install.log'), 'a+') as logf:
                    cmd = [os.path.join(SCRIPTDIR, python, 'python.exe'), '-m', 'pip', 'install', line]
                    print(' '.join(cmd))
                    p = subprocess.Popen(cmd, stdout=logf, stderr=logf)
                    p.wait(60.0)
                    if p.returncode != 0:
                        print('ERROR! look at pip-install.log')
                                     
    print('DONE!')
