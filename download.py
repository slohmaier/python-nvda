import os
import requests
import shutil
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
    
    for f in z.filelist[1:]:
        destf = '/'.join(f.filename.split('/')[1:])
        
        for python in pythons:
            path = os.path.join(SCRIPTDIR, python, SITE_DIR, destf)

            if destf.endswith('/'):
                os.makedirs(path)
            else:
                if os.path.isfile(path):
                    os.remove(path)
                with open(path, 'wb+') as _f:
                    _f.write(z.read(f))

    print('DONE!\n')
