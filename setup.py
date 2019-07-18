'''This script prepare the environment to use the project'''

import os
import sys
import pathlib
import subprocess

if sys.platform.lower().startswith('win'):
    separator = '\\'
    path = pathlib.Path(__file__).parent / 'venv' / 'Scripts'

else:
    separator = '/'
    path = pathlib.Path(__file__).parent / 'venv' / 'bin'

python_version = sys.argv[1:] or ''
FNULL = open(os.devnull, 'w')

if not os.path.exists(str(path.absolute())):
    print('Creating environment...')

    try:
        subprocess.call(['virtualenv', 'venv'], stdout=FNULL, stderr=subprocess.STDOUT)
    except FileNotFoundError:
        try:
            subprocess.call([f'pip{python_version}', 'install', 'virtualenv'], stdout=FNULL, stderr=subprocess.STDOUT)
            subprocess.call(['virtualenv', 'venv'], stdout=FNULL, stderr=subprocess.STDOUT)
        except FileNotFoundError:
            exit('Verify your python version and try again.')

print('Installing requirements...')

requirements_path = pathlib.Path(__file__).parent / 'requirements.txt'
subprocess.call(
    [f'{str(path.absolute())}{separator}pip{python_version}', 'install', '-r', str(requirements_path.absolute())],
    stdout=FNULL, stderr=subprocess.STDOUT)

print('Initializing project...')

module_path = pathlib.Path(__file__).parent / 'src' / 'main.py'
subprocess.call([f'{str(path.absolute())}{separator}python{python_version}', str(module_path.absolute())])

print('GoodBye :D')
