#!/usr/bin/python

#       bokken.py
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

import sys, os

# go with GTK, but first check about DISPLAY environment variable
if sys.platform != "win32":
    display = os.getenv("DISPLAY").strip()
    if not display:
        print "The DISPLAY environment variable is not set! You can not use any graphical program without it..."
        sys.exit(1)

import ui.main as main

if __name__ == "__main__":
    if len(sys.argv) == 1:
        main.main('', '')
    elif len(sys.argv) == 2:
        if '-r' in sys.argv:
            main.main('', 'radare')
        elif '-p' in sys.argv:
            main.main('', 'pyew')
        else:
            main.main(sys.argv[1], '')
    elif len(sys.argv) == 3:
        if '-r' in sys.argv:
            main.main(sys.argv[2], 'radare')
        elif '-p' in sys.argv:
            main.main(sys.argv[2], 'pyew')
        else:
            print "Incorrect arguments"
            main.main('', '')
