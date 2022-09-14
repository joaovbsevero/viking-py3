'''This script prepare the environment to use the project'''

import os
import sys
import pathlib
import subprocess

python_version = sys.argv[1:] or ''
FNULL = open(os.devnull, 'w')

print('Installing requirements...')

requirements_path = pathlib.Path(__file__).parent / 'requirements.txt'
subprocess.call(
    [f'pip{python_version}', 'install', '-r', str(requirements_path.absolute())],
    stdout=FNULL, stderr=subprocess.STDOUT)

print('Initializing project...')

module_path = pathlib.Path(__file__).parent / 'src' / 'main.py'
subprocess.call([f'python{python_version}', str(module_path.absolute())])

print('GoodBye :D')
