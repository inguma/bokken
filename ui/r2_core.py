#!/usr/bin/python

#       r2_core.py
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

import os
import tempfile

from r2.r_core import *
from r2.r_bin import *

class Core():

    def __init__(self):

        self.fulldasm = ''
        self.text_dasm = ''     # Dasm of the .text section
        self.pythondasm = ''
        self.textsize= 0
        self.fullhex = ''
        self.fullstr = ''
        self.allstrings = ''
        self.allfuncs = []
        self.allsections = []
        self.allimports = {}
        self.allexports = []
        self.fileinfo = ''
        self.pdfinfo = ''
        self.alllinks = []
        self.parsed_links = {'remotes':[], 'locals':[]}
        self.links_struct = []
        self.dot = ''
        self.http_dot = ''
        self.checked_urls = []
        self.bad_urls = []
        self.cmd = ''
        self.last_cmd = ''
        self.corename = 'radare'

        self.core = RCore()
        self.core.format = ''

    def clean_fullvars(self):
        self.fulldasm = ''
        self.text_dasm = ''     # Dasm of the .text section
        self.pythondasm = ''
        self.textsize= 0
        self.fullhex = ''
        self.fullstr = ''
        self.allstrings = ''
        self.allfuncs = []
        self.allsections = []
        self.allimports = {}
        self.allexports = []
        self.fileinfo = ''
        self.pdfinfo = ''
        self.alllinks = []
        self.parsed_links = {'remotes':[], 'locals':[]}
        self.links_struct = []
        self.dot = ''
        self.http_dot = ''
        self.checked_urls = []
        self.bad_urls = []
        self.cmd = ''
        self.last_cmd = ''

    def load_file(self, file):
        # Init core
        self.core.file_open(file, 0, 0)
        self.core.bin_load(None)
        #self.core.config.set_i("io.va", 1)
        #self.core.config.set_i("anal.split", 1)
        #self.core.cmd0("af@entry0");
        self.core.config.set("asm.bytes", "false")
        self.core.cmd0("aa")
        #self.core.config.set_i("asm.decode", 1)
        #self.core.gdiff(self.core)

        self.bin = self.core.bin
        self.info = self.bin.get_info()
        #bin.load(sys.argv[1], None)
        self.baddr = self.bin.get_baddr()
        self.size = hex(self.core.file.size)
        self.core.format = self.info.rclass.upper()

        # Check if file name is an URL, pyew stores it as 'raw'
        self.is_url(file)

    def is_url(self, file):
        #print "Checking if is URL..."
        self.filename = file
        if self.filename.lower().startswith("http://") or \
           self.filename.lower().startswith("https://") or \
           self.filename.lower().startswith("ftp://"):
            self.core.format = 'URL'

    def get_strings(self):
        if not self.allstrings:
            strings = ''
#            FILTER=''.join([(len(repr(chr(x)))==3) and chr(x) or '.' for x in range(256)])
#            for str in self.bin.get_strings():
#                strings += "0x%08x:\t%s\n" % (self.baddr+str.rva, str.string.translate(FILTER))
            self.core.cmd0('fs strings')
            strings = self.core.cmd_str('f')
            self.allstrings = strings
        return self.allstrings

    def get_functions(self):
        if not self.allfuncs:
            self.core.cmd0('aa')
            self.core.cmd0('e asm.lines=false')
            self.core.cmd0('fs functions')
            for fcn in self.core.cmd_str('f').split('\n'):
                if fcn:
                    #print ' 0x%08x' % fcn.addr, fcn.name
                    fcn = fcn.split(' ')[-1]
                    self.allfuncs.append(fcn)
        return self.allfuncs

    def get_hexdump(self):
        hexdump = self.core.cmd_str('px')
        return hexdump

    def get_full_hexdump(self):
        if self.fullhex == '':
            self.core.cmd_str('s section..text')
            self.core.cmd_str('x ' + self.size)
            #self.core.cmd0('b 1024')
            hexdump = self.core.cmd_str('px')
            self.fullhex = hexdump
        return self.fullhex

    def get_dasm(self):
        self.core.cmd0('e scr.color=0')
        self.core.cmd0('e asm.lines=false')
        dasm = self.core.cmd_str('pd')
        return dasm

    def get_text_dasm(self):
        if not self.text_dasm:
            self.core.cmd0('b ' + str(self.textsize))
            self.core.cmd0('e scr.color=0')
            self.core.cmd0('e asm.lines=false')
            dasm = self.core.cmd_str('pd')
            self.text_dasm = dasm
        return self.text_dasm

    def get_fulldasm(self):
        if not self.fulldasm:
            self.core.cmd0('s section..text')
            self.core.cmd0('b ' + str(self.textsize))
            self.core.cmd0('e scr.color=0')
            self.core.cmd0('e asm.lines=false')
            dasm = self.core.cmd_str('pd')
            self.fulldasm = dasm
        return self.fulldasm

    def get_repr(self):
        if not self.fullstr:
            self.core.cmd0('s section..text')
            self.fullstr = self.core.cmd_str('ps ' + str(self.size))
        return self.fullstr

    def get_sections(self):
        if self.allsections == []:
             for section in self.bin.get_sections():
                 self.allsections.append( [section.name, hex(self.baddr+section.rva), hex(section.size), hex(section.offset)] )
                 if '.text' in section.name:
                    self.textsize = section.size

        return self.allsections

    def get_imports(self):
        if not self.allimports:
            for imp in self.bin.get_imports():
                if '__' in imp.name:
                    dll, imp_name = imp.name.split('__')
                else:
                    dll, imp_name = imp.name.split('_')
                if not dll in self.allimports.keys():
                    self.allimports[dll] = []
                self.allimports[dll].append( [hex(self.baddr+imp.rva), imp_name] )
        return self.allimports

    def get_exports(self):
        if not self.allexports:
            for sym in self.bin.get_symbols():
                self.allexports.append( [hex(self.baddr+sym.rva), sym.name, '', ''] )
        return self.allexports

    def get_callgraph(self, addr=''):
        if not self.dot:
            file = tempfile.gettempdir() + os.sep + 'miau.dot'
            if not addr:
                self.core.cmd_str('ag > ' + file)
            else:
                self.core.cmd_str('ag ' + addr + ' > ' + file)
            f = open(file, 'r')
            self.dot = f.read()
            f.close()
            os.unlink(file)
        return self.dot

    def get_file_info(self):
        # core.filename        : /home/hteso/Pocs/MRxNet/mrxnet.sys
        # core.format          : PE
        # core.maxfilesize     : 1073741824
        # core.maxsize         : 17400
        # core.type            : 32
        # core.processor       : intel
        #info = self.bin.get_info()
        self.fileinfo = {'name':self.info.file, 'format':self.info.rclass, 'processor':self.info.machine}
    #   print self.fileinfo

        return self.fileinfo

    def search_http_src(self):
        srcs = self.core.dosearch(self.core.f, 's', 'src="', offset=self.core.offset, cols=100, doprint=False)
        hrefs = self.core.dosearch(self.core.f, 's', 'href="', offset=self.core.offset, cols=100, doprint=False)
        results = srcs + hrefs
        for element in results:
            link = element.values()[0].split('"')[1]
            if link.startswith('http://') or link.startswith('https://') and link != '':
                self.parsed_links['remotes'].append(link)
            else:
                if link != '':
                   self.parsed_links['locals'].append(link)

    # Parse http resources to create graph
    def parse_http_locals(self):
        for element in self.parsed_links['locals']:
            element = element.strip(' ').split('/')
            if len(element) > 1:
                try:
                    root = next(s for s in element if s)
                    root_index = element.index(root)
                    self.links_struct.append( {root:element[root_index + 1:]} )
                except:
                    pass
            elif len(element) == 1:
                self.links_struct.append( {element[0]:['']} )
        import ui.generate_dot as gendot
        self.http_dot = gendot.generate_dot(self.links_struct, self.core.filename)

