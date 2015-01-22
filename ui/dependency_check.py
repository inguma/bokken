#       dependency_check.py
#
#       Copyright 2011 Hugo Teso <hugo.teso@gmail.com>
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

from __future__ import print_function

import lib.bokken_globals as glob
import lib.common as common
import os, sys, platform

def check_all():
    python_version()
    pyew_dependency_check()
    radare_dependency_check()
    cores()
    gtkui_dependency_check()
    psyco_dependency_check()
    tidy_dependency_check()
    graphvix_dependency_check()

def python_version():
    print('\tPython version...', end='')
    if sys.version_info[0] == 3:
        print(common.console_color("\tD'oh!", 'red'))
        sys.stderr.write("Python3 not supported, install python 2.7 to run Bokken")
        exit(1)
    else:
        print(common.console_color('\tOK', 'green'))

def tidy_dependency_check():
    '''Try to use tidy'''

    print('\tTidy availability...', end='')

    try:
        import tidy
        print(common.console_color('\tOK', 'green'))
    except ImportError:
        print(common.console_color("\tD'oh!", 'red'))
        msg = 'No tidy module found. HTTP code won\'t be properly formatted\n'
        print(msg)

def pyew_dependency_check():
    '''We need to verify the presence of pyew'''

    print('Checking:')
    print('\tPyew availability... ', end='')

    try:
        import pyew.pyew
        print(common.console_color('\tOK', 'green'))
        glob.has_pyew = True
    except:
        print(common.console_color("\tD'oh!", 'red'))
        print('You need pyew in order to use the pyew backend in binaries and '
                'PDFs. Download it from its web:\n'
                '    - http://code.google.com/p/pyew/\n')
        return

    if common.version_gt(glob.min_pyew_version, pyew.pyew.HUMAN_VERSION):
        print(common.console_color("\tD'oh!", 'red'))
        print(common.console_color(('Your version of pyew (%s) is not supported! '
                'It must be equal or greater than %s.' %
                (pyew.pyew.HUMAN_VERSION, glob.min_pyew_version)), 'red'))
        print('Everything from here may break at any time.  If you feel that '
                'this check is wrong, please file a bug at '
                'http://bokken.inguma.eu')

def radare_dependency_check():
    '''We need to verify the presence of radare2'''

    '''FIXME: I don't think this is the right way of doing it as we are
    duplicating code here and ui/radare_core.py.  We should just try to init
    an r2 core and then get uicore.version.'''

    print('\tRadare availability...', end='')

    try:
        import r2.r_core
        print(common.console_color('\tOK', 'green'))
        glob.has_radare = True
    except:
        print(common.console_color("\tD'oh!", 'red'))
        print('You need radare and radare2 Python bindings to use the r2 '
                'backend. Download them from its web:\n'
                '    - http://www.radare.org\n')
        return

    if common.version_gt(glob.min_radare_version, r2.r_core.R2_VERSION):
        print(common.console_color("\tD'oh!", 'red'))
        print(common.console_color(('Your version of r2 (%s) is not supported! '
                'It must be equal or greater than %s.' %
                (r2.r_core.R2_VERSION, glob.min_radare_version)), 'red'))
        print('Everything from here may break at any time.  If you feel that '
                'this check is wrong, please file a bug at '
                'http://bokken.inguma.eu')

def cores():
    if not glob.has_pyew and not glob.has_radare:
        print('You need at least one dissasembler core, either pyew or radare:\n'
                '    - http://code.google.com/p/pyew/\n'
                '    - http://www.radare.org')
        sys.exit(1)

def psyco_dependency_check():
    '''Try to use psyco'''

    print('\tPsyco availability...', end='')

    try:
        import psyco
        psyco.log()
        psyco.full()
        print(common.console_color('\tOK', 'green'))
    except ImportError:
        print(common.console_color("\tD'oh!", 'red'))
        print("No psyco module found. It's recommended to use it to improve performance\n")

def gtkui_dependency_check():
    '''
    This function verifies that the dependencies that are needed by the GTK user interface are met.
    '''

    print('\tGTK UI dependencies...', end='')

    # Check Gtk
    try:
        import pygtk
        pygtk.require('2.0')
        import gtk, gobject
        assert gtk.gtk_version >= (2, 12)
        assert gtk.pygtk_version >= (2, 12)
        print(common.console_color('\tOK', 'green'))
    except:
        print(common.console_color("\tD'oh!", 'red'))
        print('You have to install GTK and PyGTK versions >=2.12 to be able to '
                'run the GTK user interface.\n'
                '    - On Debian-based distributions: apt-get install python-gtk2\n'
                '    - On Mac: sudo port install py25-gtk')
        sys.exit(1)

    # Check GtkSourceView2
    try:
        print('\tGtkSourceView2...', end='')
        import gtksourceview2
        print(common.console_color('\tOK', 'green'))
    except:
        print(common.console_color("\tD'oh!", 'red'))
        print('GtkSourceView2 not installed! Install it for your platform:\n'
                '    - On Debian-based distributions: apt-get install python-gtksourceview2')
        sys.exit(1)

def graphvix_dependency_check():
    # Check Graphviz
    print("\tGraphviz binaries...", end="")
    if os.environ.has_key('PATH'):
        for path in os.environ['PATH'].split(os.pathsep):
            progs = __find_executables(path)

            if progs is not None :
                #print(progs)
                print(common.console_color('\tOK', 'green'))
                return

        print(common.console_color("\tD'oh!", 'red'))
        print('Graphviz not installed! Install it for your platform:\n'
                '    - On Debian-based distributions: apt-get install graphviz')
        sys.exit( 1 )

def __find_executables(path):
    # Code borrowed from pydot
    # http://code.google.com/p/pydot/
    # Thanks to Ero Carrera

    """Used by find_graphviz

    path - single directory as a string

    If any of the executables are found, it will return a dictionary
    containing the program names as keys and their paths as values.

    Otherwise returns None
    """

    success = False
    if platform.system() != 'Windows':
        progs = {'dot': '', 'twopi': '', 'neato': '', 'circo': '', 'fdp': '', 'sfdp': ''}
    else:
        progs = {'dot.exe': '', 'twopi.exe': '', 'neato.exe': '', 'circo.exe': '', 'fdp.exe': '', 'sfdp.exe': ''}

    was_quoted = False
    path = path.strip()
    if path.startswith('"') and path.endswith('"'):
        path = path[1:-1]
        was_quoted =  True

    if os.path.isdir(path):

        for prg in progs.iterkeys():

            #print(prg)
            if progs[prg]:
                continue

            if os.path.exists( os.path.join(path, prg) ):

                if was_quoted:
                    progs[prg] = '"' + os.path.join(path, prg) + '"'
                else:
                    progs[prg] = os.path.join(path, prg)

                success = True

    if success:
        return progs

    else:
        return None

