# -*- coding: utf-8 -*-
"""
Bokken Disassembler Framework
Copyright (c) 2013-2014 David Martínez Moreno <ender@debian.org>

I am providing code in this repository to you under an open source license.
Because this is a personal repository, the license you receive to my code
is from me and not my employer (Facebook).

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
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

""" This library provides generic functions. """

import os.path

def version_conversion(func):

    def inner(ver1, ver2):
        '''Decorator for converting versions strings (passed as arguments) to
        tuples.'''
        '''FIXME: For now it considers a.b.c-rc3 as (a, b, c, 3) to be able to
        match radare2's RC versions (e.g. 0.9.8-rc3).'''

        version_tuple = []

        for ver in (ver1, ver2):
            # Horrible version mangling.  I know that it's awful but I don't
            # want to do proper version handling now.
            # Let's remove '.git' in case it's a git version.
            ver = ver.replace('.git', '')
            ver = ver.replace('-git', '')
            # If we get something like 0.9.8-rc1, let's treat it as 0.9.8.1
            # just for now.
            ver = ver.replace('-rc', '.')
            try:
                version_tuple.append(tuple(map(int, (ver.split(".")))))
            except ValueError:
                '''The version number contains letters, so we return all 0s.'''
                version_tuple.append(tuple(map(lambda x: 0, ver.split('.'))))

        return func(version_tuple[0], version_tuple[1])

    return inner

@version_conversion
def version_ge(ver1, ver2):
    '''Function to compare e.g. 0.9.1 >= 0.9.3.
    Returns True if ver1 >= ver2, otherwise False.'''

    return ver1 >= ver2

@version_conversion
def version_le(ver1, ver2):
    '''Function to compare e.g. 0.9.1 <= 0.9.3.
    Returns True if ver1 <= ver2, otherwise False.'''

    return ver1 <= ver2

@version_conversion
def version_gt(ver1, ver2):
    '''Function to compare e.g. 0.9.1 > 0.9.3.
    Returns True if ver1 > ver2, otherwise False.'''

    return ver1 > ver2

@version_conversion
def version_lt(ver1, ver2):
    '''Function to compare e.g. 0.9.1 < 0.9.3.
    Returns True if ver1 < ver2, otherwise False.'''

    return ver1 < ver2

def console_color(string='', color='white'):
    '''This function returns a properly ANSI-escaped string for display into a
    terminal with color capabilities.'''
    import sys

    ansi_code = {
            'green': '\033[92m',
            'yellow': '\033[93m',
            'red': '\033[91m',
            'white': '\033[0m',
    }
    if sys.platform == "win32":
        # No color for you today!
        return string

    return('%s%s%s' % (ansi_code[color], string, ansi_code['white']))

def datafile_path(filename=''):
    '''Returns the full path for a file in the ui/data/ directory.  In absence
    of arguments, just returns the UI datadir.'''
    datadir = '%s/../ui/data/' % os.path.dirname(__file__)

    return os.path.normpath(datadir + filename)
