import sys
from cx_Freeze import setup, Executable
from cx_Freeze.dist import build_exe
 
build_exe_options = {'packages': ['os'], 'includes': ['PySimpleGUI', 'selenium', 'time', 're'], 'include_files': ['chromedriver.exe','ics.txt', 'icon.ico','chamados_concluidos.txt']}
 
base = None
if sys.platform == 'win32':
    base = 'Win32GUI'
 
setup(
    name = 'Bumblebee',
    version = '1.3.2',
    description = 'Automação para incerção de ICs',
    options = {'build_exe': build_exe_options},
    executables = [Executable(script='Bumblebee.py', base = base, icon = 'icon.ico')]
)
