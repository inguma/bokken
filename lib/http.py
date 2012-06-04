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

class BokkenHttpServer(threading.Thread):

    def __init__(self, port=4546):
        threading.Thread.__init__(self)
        self.port = port

    def run(self):
        urls = (
                '/', 'Index',
                '/favicon.ico', 'Favicon',
                '/bokken/file/dump', 'FileDump',
                '/bokken/file/exports', 'FileExports',
                '/bokken/file/functions', 'FileFunctions',
                '/bokken/file/imports', 'FileImports',
                '/bokken/file/name', 'FileName',
                '/bokken/file/sections', 'FileSections',
               )

        self.http = web.application(urls, globals())
        web.httpserver.runsimple(self.http.wsgifunc(), self.http, ('0.0.0.0', self.port))

    def terminate(self):
        print('Shutting down HTTP server on port %d.' % self.port)
        self.http.stop()

class Index:
    """Main index, path seems to be optional in GET."""

    def GET(self, path=''):

        index_page = '''
<!DOCTYPE html>
<html>
<head>
  <title>Bokken ''' + glob.version + ''', a GUI for pyew and radare.
  </title>
  <link rel="stylesheet" href="/static/css/bokken.css" type="text/css" media="screen" />
</head>
<body>
    <div id="bokken">
        <div id="brand_header"><h2><img src="/static/img/bokken.svg">Bokken ''' + glob.version + '''</h2></div>
        <div id="filename">Filename: <span class="content"></span></div>
        <div id="asmdump">Assembler dump: <pre class="content"></pre></div>
        <div id="fileexports">Exports: <pre class="content"></pre></div>
        <div id="fileimports">Imports: <pre class="content"></pre></div>
        <div id="filesections">Sections: <pre class="content"></pre></div>
        <div id="filefunctions">Functions: <pre class="content"></pre></div>
    </div>
    <script src="/static/js/jquery-1.7.2.min.js"></script>
    <script src="/static/js/bokken.js"></script>
</body>
</html>'''

        return index_page

class Favicon:
    """Returns the favicon."""

    def GET(self, path=''):
        import os

        web.header('Content-type', 'image/vnd.microsoft.icon')
        return open(os.sep.join([
            os.path.dirname(__file__), '..', 'ui', 'data', 'icons', 'bokken.ico'
            ])).read()

class FileDump:
    """Assembler dump of the .text sections."""

    def GET(self, path=''):

        # See Redmine issue #120.
        if glob.core.backend == 'radare':
            return glob.core.get_text_dasm()[0].replace("\n", "<br/>")
        else:
            return glob.core.get_text_dasm().replace("\n", "<br/>")

class FileExports:
    """Exports in the file."""

    def GET(self, path=''):
        return glob.core.get_exports()

class FileFunctions:
    """File functions."""

    def GET(self, path=''):
        return glob.core.get_functions()

class FileImports:
    """Imports in the file."""

    def GET(self, path=''):
        # Redmine issue #121.
        if glob.core.backend == 'radare':
            # FIXME: Test that the file is ELF before running this, or fix the API.
            glob.core.get_elf_imports()
        return glob.core.get_imports()

class FileName:
    """Retrieve file name."""

    def GET(self, path=''):
        return glob.core.filename

class FileSections:
    """Retrieve file sections."""

    def GET(self, path=''):
        return glob.core.get_sections()
