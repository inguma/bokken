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

import sys

OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'

def check_all():
    python_version()
    pyew_dependency_check()
    radare_dependency_check()
    cores()
    gtkui_dependency_check()
    psyco_dependency_check()
    tidy_dependency_check()

def python_version():
    print '\tPython version...',
    if sys.version_info[0] == 3:
        print FAIL + "\tD'oh!" + ENDC
        sys.stderr.write("Python3 not supported, install python 2.7 to run Bokken")
        exit(1)
    else:
        print OKGREEN + "\tOK" + ENDC

def tidy_dependency_check():
    '''Try to use tidy'''

    print '\tTidy availability...',

    try:
        import tidy
        print OKGREEN + "\tOK" + ENDC
    except ImportError:
        print FAIL + "\tD'oh!" + ENDC
        msg = 'No tidy module found. HTTP code won\'t be properly formatted\n'
        print msg

def pyew_dependency_check():
    '''We need to verify the presence of pyew'''
    
    print 'Checking:'
    print '\tPyew availability...',

    global HAS_PYEW
    try:
        import pyew
        print OKGREEN + "\tOK" + ENDC
        HAS_PYEW = True
    except:
        print FAIL + "\tD'oh!" + ENDC
        msg = 'You need pyew in order to use pyew backend in binaries and PDFs. Download it from its web:\n'
        msg += '    - http://code.google.com/p/pyew/\n'
        print msg
        HAS_PYEW = False
        #sys.exit( 1 )

def radare_dependency_check():
    '''We need to verify the presence of radare2'''
    
    print '\tRadare availability...',

    global HAS_RADARE
    try:
        import r2
        print OKGREEN + "\tOK" + ENDC
        HAS_RADARE = True
    except:
        print FAIL + "\tD'oh!" + ENDC
        msg = 'You need radare2 bindings to use r2 backend. Download it from its web:\n'
        msg += '    - http://www.radare.org\n'
        print msg
        HAS_RADARE = False

def cores():
    if not HAS_PYEW and not HAS_RADARE:
        print "You need at least one core, either pyew or radare:"
        print '    - http://code.google.com/p/pyew/'
        print '    - http://www.radare.org'
        sys.exit( 1 )

def psyco_dependency_check():
    '''Try to use psyco'''

    print '\tPsyco availability...',

    try:
        import psyco
        psyco.log()
        psyco.full()
        print OKGREEN + "\tOK" + ENDC
    except ImportError:
        print FAIL + "\tD'oh!" + ENDC
        msg = 'No psyco module found. It\'s recomended to use it to improve performance\n'
        print msg

def gtkui_dependency_check():
    '''
    This function verifies that the dependencies that are needed by the GTK user interface are met.
    '''

    print '\tGTK UI dependencies...',

    # Check Gtk
    try:
        import pygtk
        pygtk.require('2.0')
        import gtk, gobject
        assert gtk.gtk_version >= (2, 12)
        assert gtk.pygtk_version >= (2, 12)
        print OKGREEN + "\tOK" + ENDC
    except:
        print FAIL + "\tD'oh!" + ENDC
        msg = 'You have to install GTK and PyGTK versions >=2.12 to be able to run the GTK user interface.\n'
        msg += '    - On Debian-based distributions: apt-get install python-gtk2\n'
        msg += '    - On Mac: sudo port install py25-gtk'        
        print msg
        sys.exit( 1 )

    # Check GtkSourceView2
    try:
        print '\tGtkSourceView2...',
        import gtksourceview2
        print OKGREEN + "\tOK" + ENDC
    except:
        print FAIL + "\tD'oh!" + ENDC
        print "GtkSourceView2 not installed! Install it for your platform:"
        print "    - On Debian-based distributions: apt-get install python-gtksourceview2"
        sys.exit( 1 )

