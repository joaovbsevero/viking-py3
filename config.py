"""This script prepare the environment to use the project"""

import os
import sys
import pathlib
import subprocess

if sys.platform.startswith('win'):
    path = pathlib.Path(__file__).parent / 'venv' / 'Scripts' / 'activate_this.py'

else:
    path = pathlib.Path(__file__).parent / 'venv' / 'bin'

if not os.path.exists(str(path.absolute())):
    subprocess.call(['pip3', 'install', 'virtualenv'])
    subprocess.call(['virtualenv', 'venv'])

if sys.platform.startswith('win'):
    print('Navigate to "venv/Scripts" and use the "activate.bat" file to activate the environment')
else:
    print('Navigate to "venv/bin" and use the "source activate" command to activate the environment')
