# -*- coding: utf-8 -*-
"""
Bokken Disssambler Framework
Copyright (c) 2011-2012 David Martínez Moreno <ender@debian.org>

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

""" This library has HTTP functions used in the web UI server. """

import threading
import lib.web as web
import lib.bokken_globals as glob

def html_skeleton(header='', body=''):
    """Defines a basic HTML skeleton for returned HTML."""

    skeleton="""
    <html>
    <head><title>Bokken """ + glob.version
    if header:
        skeleton += ' -' + header
    skeleton += """
    </title></head>
    <body>""" + body + """
    </body>
    </html>
    """
    return skeleton


class BokkenHttpServer(threading.Thread):

    def __init__(self, port=4546):
        threading.Thread.__init__(self)
        self.port = port

    def run(self):
        urls = (
                '/', 'Index',
                '/favicon.ico', 'Favicon',
                '/bokken/file(|/)', 'FileDump',
                #'/bokken/kb/get(|/)', 'RestKB',
               )

        self.http = web.application(urls, globals())
        web.httpserver.runsimple(self.http.wsgifunc(), self.http, ('0.0.0.0', self.port))

    def terminate(self):
        print('Shutting down HTTP server on port %d.' % self.port)
        self.http.stop()

class Index:
    """Main index, path seems to be optional in GET."""

    def GET(self, path=''):
        return html_skeleton(body='Bokken')

class Favicon:
    """Returns the favicon."""

    def GET(self, path=''):
        import os

        return open(os.path.dirname(__file__) + os.sep + '..' +
                    os.sep + 'ui' + os.sep + 'data' + os.sep +
                    'bokken-small.svg').read()

class FileDump:
    """"""

    def GET(self, path=''):
        return glob.core.text_dasm
