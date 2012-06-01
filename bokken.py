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

import argparse
import sys, os

# Go with GTK, but first check the DISPLAY environment variable
if sys.platform != "win32":
    display = os.getenv("DISPLAY").strip()
    if not display:
        print "The DISPLAY environment variable is not set! You can not use any graphical program without it..."
        sys.exit(1)

parser = argparse.ArgumentParser()
parser.add_argument('-r', '--radare', action='store_true',
                    help='Use by default the radare2 core')
parser.add_argument('-p', '--pyew', action='store_true',
                    help='Use by default the pyew core')
parser.add_argument('-w', '--web', action='store_true',
                    help='Start up the web server on port 4546')
args = parser.parse_args()

if args.radare and args.pyew:
    args.radare = False
    args.pyew = False

import ui.main as main

main.main('',
          'radare' if args.radare else ('pyew' if args.pyew else ''),
          'web' if args.web else '')

