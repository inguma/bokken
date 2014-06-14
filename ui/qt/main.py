# -*- coding: utf-8 -*-
"""
Bokken Disassembler Framework
Copyright (C) 2014 David Martínez Moreno <ender@debian.org>

I am providing code in this repository to you under an open source license.
Because this is a personal repository, the license you receive to my code
is from me and not my employer (Facebook).

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
02110-1301, USA.
"""

"""Qt4 interface for Bokken."""

import os, sys
import lib.bokken_globals as glob

# Add plugins directory to the path
BOKKEN_PATH = os.getcwd() + os.sep + 'plugins' + os.sep
sys.path.append(BOKKEN_PATH)

# Perform the Qt UI dependency check here
# FIXME: Missing dependency code for Qt.
#import ui.dependency_check as dependency_check
#dependency_check.check_all()

# Now that I know that I have them, import them!
from PyQt4 import QtCore, QtGui

# This is just general info, to help people knowing their system.
print "Starting bokken, running on:"
print "  Python version:"
print "\n".join("    " + x for x in sys.version.split("\n"))
print '  Qt version: ' + QtCore.QT_VERSION_STR
print '  PyQt4 version: ' + QtCore.PYQT_VERSION_STR
print

from ui.qt.open_file_dialog import OpenFileDialog

class BokkenQtClient:
    def __init__(self, target, backend):
        self.app = QtGui.QApplication(sys.argv)

        # FIXME: Missing HTTP init code.
        # FIXME: Missing dependency code.
        self.open_file_dialog = OpenFileDialog(('radare'))
        self.app.exec_()

    def quit(self):
        sys.exit(self.app.exec_())

def main(target, backend):
    BokkenQtClient(target, backend)
    if glob.http:
        glob.http.terminate()
