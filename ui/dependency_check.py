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
import sys

def check_all():
    python_version()
    pyew_dependency_check()
    radare_dependency_check()
    cores()
    gtkui_dependency_check()
    psyco_dependency_check()
    tidy_dependency_check()

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

    global HAS_PYEW
    try:
        import pyew
        print(common.console_color('\tOK', 'green'))
        HAS_PYEW = True
    except:
        print(common.console_color("\tD'oh!", 'red'))
        print('You need pyew in order to use pyew backend in binaries and '
                'PDFs. Download it from its web:\n'
                '    - http://code.google.com/p/pyew/\n')
        HAS_PYEW = False

def radare_dependency_check():
    '''We need to verify the presence of radare2'''

    print('\tRadare availability...', end='')

    global HAS_RADARE
    try:
        import r2
        print(common.console_color('\tOK', 'green'))
        HAS_RADARE = True
    except:
        print(common.console_color("\tD'oh!", 'red'))
        print('You need radare and radare2 Python bindings to use the r2 '
                'backend. Download them from its web:\n'
                '    - http://www.radare.org\n')
        HAS_RADARE = False

def cores():
    if not HAS_PYEW and not HAS_RADARE:
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
        print('GtkSourceView2 not installed! Install it for your platform:'
                '    - On Debian-based distributions: apt-get install python-gtksourceview2')
        sys.exit(1)

