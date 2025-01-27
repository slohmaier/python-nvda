import json
import os
import requests
import subprocess
import sys
from argparse import ArgumentParser
from io import BytesIO
from zipfile import ZipFile

NVDA_SOURCE_URL='https://github.com/nvaccess/nvda/archive/refs/tags/{0}.zip'
NVDA_HEAD_URL='https://codeload.github.com/nvaccess/nvda/zip/refs/heads/master'
SCRIPTDIR = os.path.dirname(os.path.abspath(__file__))
SITE_DIR='Lib/site-packages'

if __name__ == '__main__':
    argparser = ArgumentParser('python-downloader')
    #optional argument for tag
    argparser.add_argument('-t', '--tag', help='NVDA tag to download', default='latest')
    
    args = argparser.parse_args()

    nvdaUrl = NVDA_SOURCE_URL.format(args.tag)
    if args.tag == 'latest':
        print('Determining NVDA version...')
        nvdaVersion = json.loads(requests.get('https://api.github.com/repos/nvaccess/nvda/releases/latest').content)['tag_name']
        nvdaUrl = NVDA_SOURCE_URL.format(nvdaVersion)
    elif args.tag == 'head':
        nvdaUrl = NVDA_HEAD_URL

    print('Downloading latest NVDA tag: '+nvdaUrl)
    res = requests.get(nvdaUrl)
    print('DONE!\n')


    print ('Unzipping to python-distributions...')
    zipIO = BytesIO(res.content)
    _zipFile = ZipFile(zipIO)
    pythons = []
    for d in os.listdir(SCRIPTDIR):
        if os.path.isdir(d) and d.startswith('python'):
            pythons.append(d)
    
    requirements = ''

    #prefix for nvda-source-files
    sourcePrefix = _zipFile.filelist[0].filename + 'source/'
    for zipInfo in _zipFile.filelist[1:]:
        #store requirements.txt to install in python later
        if zipInfo.filename.endswith('requirements.txt'):
            requirements = _zipFile.read(zipInfo).decode('utf-8')

        #onlty handle nvda source-files now
        if not zipInfo.filename.startswith(sourcePrefix):
            continue

        #genearte path relative to site-packages
        pathInSite = '/'.join(zipInfo.filename.split('/')[2:])
        print(pathInSite)
        
        for python in pythons:
            #genearte filename inside python-site-packages
            path = os.path.join(SCRIPTDIR, python, SITE_DIR, pathInSite)

            if zipInfo.filename[-1] != '/':
                #remove existing file
                if os.path.isfile(path):
                    os.remove(path)

                _bytes = _zipFile.read(zipInfo)

                #write file
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, 'wb+') as _f:
                    _f.write(_bytes)

    print('DONE!\n')

    print('Ensuring pip is installed')
    for python in pythons:
        pycmd = [os.path.join(SCRIPTDIR, python, 'python.exe'), 'get-pip.py']
        print(' '.join(pycmd))
        pyProcess = subprocess.Popen(pycmd)
        pyProcess.wait(60.0)
        if pyProcess.returncode != 0:
            print('ERROR! look at pip-install.log')
            sys.exit(1)
    print('DONE!\n')

    print('Installing pip dependencies')
    for requirement in requirements.split('\n')+['venv']:
        #only handle non-empty and non-comment lines
        requirement = requirement.strip()
        if requirement and not requirement.startswith('#'):
            for python in pythons:
                with open(os.path.join(SCRIPTDIR, python, 'pip-install.log'), 'a+') as logf:
                    pyCmd = [os.path.join(SCRIPTDIR, python, 'python.exe'), '-m', 'pip', 'install', requirement]
                    print(' '.join(pyCmd))
                    pyProcess = subprocess.Popen(pyCmd, stdout=logf, stderr=logf)
                    pyProcess.wait(60.0)
                    if pyProcess.returncode != 0:
                        print('ERROR! look at pip-install.log')              
    print('DONE!')
