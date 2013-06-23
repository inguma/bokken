#!/usr/bin/python
# -*- coding: utf-8 -*-
#       bokken.py
#
#       Copyright 2011 Hugo Teso <hugo.teso@gmail.com>
#       Copyright 2012 David Martínez Moreno <ender@debian.org>
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

import lib.bokken_globals as glob

def bokken():

    import sys, os

    # Go with GTK, but first check the DISPLAY environment variable
    if sys.platform != "win32":
        display = os.getenv("DISPLAY").strip()
        if not display:
            print "The DISPLAY environment variable is not set! You can not use any graphical program without it..."
            sys.exit(1)

    try:
        import argparse
    except ImportError:
        print 'No argparse module found. Install it or use Python 2.7 or later'
        sys.exit(1)

    parser = argparse.ArgumentParser()
    parser.add_argument('file_to_load', nargs='?',
                        help='File to load')
    parser.add_argument('-r', '--radare', action='store_true',
                        help='Select the radare2 core')
    parser.add_argument('-p', '--pyew', action='store_true',
                        help='Select the pyew core')
    parser.add_argument('-w', '--web', action='store_true',
                        help='Start up Mune, the internal web server.')
    parser.add_argument('-l', '--port', nargs='?', default=4546,
                        help='Port for the web server (default: 4546)')
    parser.add_argument('-b', '--bind_address', nargs='?', default='0.0.0.0',
                        help='Local IP address to bind the web server to (default: all)')
    args = parser.parse_args()

    if args.radare and args.pyew:
        args.radare = False
        args.pyew = False

    if args.web:
        glob.http_server = True
        glob.http_server_port = int(args.port)
        glob.http_server_bind_address = args.bind_address

    import ui.main as main

    main.main(args.file_to_load,
              'radare' if args.radare else ('pyew' if args.pyew else ''),
              )

if __name__ == "__main__":
    try:
        bokken()
    except Exception as e:
        # We have to stop the HTTP server just in case.
        if glob.http_server and glob.http:
            glob.http.terminate()

        if not e == SystemExit:
            import traceback
            traceback.print_exc()
