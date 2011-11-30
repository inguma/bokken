#!/usr/bin/python

#       radare_core.py
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

    def __init__(self, lower_case, do_anal, asm_syn, use_va, asm_bytes, progress_bar=None):

        self.do_anal = do_anal
        self.lower_case = lower_case
        self.use_va = use_va
        self.asm_syn = asm_syn
        self.asm_bytes = asm_bytes
        self.progress_bar = progress_bar

        self.fulldasm = ''
        self.text_dasm = ''     # Dasm of the .text section
        self.pythondasm = ''
        self.textsize= 0
        self.fullhex = ''
        self.fullstr = ''
        self.allstrings = ''
        self.allfuncs = []
        self.allsections = []
        self.execsections = []
        self.sections_size = []
        self.sections_lines = []
        self.allimports = {}
        self.allexports = []
        self.fileinfo = ''
        self.full_fileinfo = {}
        self.pdfinfo = ''
        self.alllinks = []
        self.ars_magica = ''
        self.parsed_links = {'remotes':[], 'locals':[]}
        self.links_struct = []
        self.dot = ''
        self.graph_layout = 'flow'
        self.http_dot = ''
        self.checked_urls = []
        self.bad_urls = []
        self.cmd = ''
        self.last_cmd = ''
        self.corename = 'radare'

        self.core = RCore()
        self.cons = RCons()
        self.assembler = self.core.assembler
        self.core.format = ''

        self.backend = 'radare'

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
        self.execsections = []
        self.sections_size = []
        self.sections_lines = []
        self.allimports = {}
        self.allexports = []
        self.fileinfo = ''
        self.full_fileinfo = {}
        self.pdfinfo = ''
        self.alllinks = []
        self.ars_magica = ''
        self.parsed_links = {'remotes':[], 'locals':[]}
        self.links_struct = []
        self.dot = ''
        self.graph_layout = 'flow'
        self.http_dot = ''
        self.checked_urls = []
        self.bad_urls = []
        self.cmd = ''
        self.last_cmd = ''

        self.core = RCore()
        self.cons = RCons()
        self.assembler = self.core.assembler
        self.core.format = ''

        self.backend = 'radare'

    def load_file(self, file):
        #print "[*] Loading file"
        self.update_progress_bar("Loading file", 0.1)
        self.file = file
        # Init core
        # Returns True/False (check)
        self.core.file_open(file, 0, 0)
        self.core.bin_load(None)
        #self.core.config.set("asm.bytes", "false")
        self.core.cmd0("e scr.interactive=false")
        self.core.cmd0('e asm.lines=false')
        self.core.cmd0('e scr.color=0')
        if not self.lower_case:
            self.core.cmd0('e asm.ucase=true')
        else:
            self.core.cmd0('e asm.ucase=false')
        if self.use_va:
            self.core.cmd0("e io.va=0")
        else:
            self.core.cmd0("e io.va=1")
        if self.asm_syn:
            self.core.cmd0("e asm.syntax=att")
        else:
            self.core.cmd0("e asm.syntax=intel")
        if self.asm_bytes:
            self.core.cmd0("e asm.bytes=false")
        else:
            self.core.cmd0("e asm.bytes=true")
        if self.do_anal:
            self.core.cmd0("aa")

        self.bin = self.core.bin
        self.info = self.bin.get_info()
        if not self.info:
            list = self.core.cmd_str('i').split('\n')
            for line in list:
                if line:
                    line = line.split('\t')
                    if line[0] == 'size':
                        self.size = line[1]
                    elif line[0] == 'uri':
                        self.info_file = line[1]

        self.baddr = self.bin.get_baddr()
        self.size = hex(self.core.file.size)
        self.core.cmd0('e search.flags=false')
        if self.do_anal:
            self.core.format = 'Program'
        else:
            self.core.format = 'Hexdump'
        # Check if file is a supported program
        if not hasattr(self.info, 'type'):
            self.core.format = 'Hexdump'

        # Check if file name is an URL
        self.is_url(file)

    def set_options(self, lower_case, do_anal, asm_syn, use_va, asm_bytes, progress_bar):
        self.do_anal = do_anal
        self.lower_case = lower_case
        self.use_va = use_va
        self.asm_syn = asm_syn
        self.asm_bytes = asm_bytes
        self.progress_bar = progress_bar

    def restore_va(self):
        if self.use_va:
            self.core.cmd0("e io.va=0")
        else:
            self.core.cmd0("e io.va=1")

    def is_url(self, file):
        #print "[*] Checking if is URL"
        self.filename = file
        if self.filename.lower().startswith("http://") or \
           self.filename.lower().startswith("https://") or \
           self.filename.lower().startswith("ftp://"):
            self.core.format = 'URL'

    def get_strings(self):
        if not self.allstrings:
            #print "[*] Get strings"
            self.update_progress_bar("Getting strings", 0.6)
            if self.use_va:
                self.core.cmd0('e io.va=0')
            else:
                self.core.cmd0('e io.va=1')
            strings = ''
            self.core.cmd0('fs strings')
            strings = self.core.cmd_str('f')
            self.allstrings = strings
        return self.allstrings

    def get_functions(self):
        if not self.allfuncs:
            #print "[*] Get functions"
            self.update_progress_bar("Getting functions", 0.8)
            #self.core.cmd0('aa')
            self.core.cmd0('fs functions')
            if self.bin.get_sym(0):
                self.allfuncs.append('entry0')
            if self.bin.get_sym(1):
                self.allfuncs.append('sym._init')
            if self.bin.get_sym(2):
                self.allfuncs.append('main')
            if self.bin.get_sym(3):
                self.allfuncs.append('sym._fini')
            for fcn in self.core.cmd_str('f').split('\n'):
                if fcn:
                    #print ' 0x%08x' % fcn.addr, fcn.name
                    fcn = fcn.split(' ')[-1]
                    self.allfuncs.append(fcn)
        return self.allfuncs

    def get_hexdump(self):
        #print "[*] Get hexdump"
        self.update_progress_bar("Getting hexdump", 0.75)
        #self.core.cmd0('e io.va=0')
        hexdump = self.core.cmd_str('px')
        #self.core.cmd0('e io.va=1')
        return hexdump

    def get_full_hexdump(self):
        if self.fullhex == '':
            #print "[*] Get full hexdump"
            self.update_progress_bar("Getting full hexdump", 0.5)
            self.core.cmd0('e io.va=0')
            self.core.cmd0('s 0')
            self.core.cmd0('b ' + str(self.size))
            hexdump = self.core.cmd_str('px')
            self.core.cmd0('s ' + str(self.baddr))
            self.core.cmd0('b 512')
            #self.core.cmd0('e io.va=1')
            self.fullhex = hexdump
        return self.fullhex

    def get_dasm(self):
        #print "[*] Get dasm"
        self.update_progress_bar("Getting dasm",0.25)
        dasm = self.core.cmd_str('pd')
        return dasm

    def get_text_dasm(self):
        base_percent = 0.3
        step = 0.01

        if not self.text_dasm:
            print "[*] Get text dasm"
            #self.update_progress_bar("Getting text dasm",base_percent)
            percent = base_percent
            for section in self.execsections:
                percent += step
                dasm = ''
                self.core.cmd0('s section.' + section[0])
                self.core.cmd0('b ' + str(section[1]))
                print "\t* Let's get the dasm for %s..." % section[0],
                #self.update_progress_bar("Reading assembler for section %s..." % section[0], percent)
                dasm = self.core.cmd_str('pD')
                self.sections_lines.append( len(dasm.split('\n')) )
                self.core.cmd0('b 512')
                print " OK!"
                self.text_dasm += dasm
                if percent == base_percent + step * 10:
                    percent -= step
            self.sections_lines.append(sum(self.sections_lines))
        return [self.text_dasm, self.sections_lines]

    def get_text_dasm_through_queue(self, queue, event):
        queue.put(self.get_text_dasm())
        event.set()

    def get_fulldasm(self):
        if not self.fulldasm:
            #print "[*] Get full dasm"
            self.core.cmd0('s ' + str(self.baddr))
            self.core.cmd0('b ' + str(self.size))
            dasm = self.core.cmd_str('pd')
            self.core.cmd0('b 512')
            self.fulldasm = dasm
        return self.fulldasm

    def get_fulldasm_through_queue(self, queue, event):
        queue.put(self.get_fulldasm())
        event.set()

    def test_alive(self):
        print "Child alive."
        return False

    def get_repr(self):
        if not self.fullstr:
            #print "[*] Get string repr"
            self.update_progress_bar("Getting string representation", 0.65)
            self.core.cmd0('e io.va=0')
            self.core.cmd0('s 0')
            self.core.cmd0('b ' + str(self.size))
            self.fullstr = self.core.cmd_str('ps ' + str(self.size))
            #self.core.cmd0('b 1024')
            #self.core.cmd0('e io.va=1')
            self.core.cmd0('s section..text')
            self.core.cmd0('b 512')
        return self.fullstr

    def get_sections(self):
        if self.allsections == [] and self.core.format != 'Hexdump':
            #print "[*] Get sections"
            self.update_progress_bar("Getting sections", 0.15)
            for section in self.bin.get_sections():
                self.allsections.append( [section.name, hex(self.baddr+section.rva), hex(section.size), hex(section.offset)] )
                if section.srwx & 1 == 1:
                    self.execsections.append([section.name, section.size])
                    self.sections_size.append(section.size)
                if '.text' in section.name:
                    self.textsize = section.size
            self.sections_size.append(sum(self.sections_size))

        return self.allsections

    def get_elf_imports(self):
        if not self.allimports:
            print "[*] Get ELF imports"
            for imp in self.bin.get_imports():
                if not 'Imports' in self.allimports.keys():
                    self.allimports['Imports'] = []
                if not self.use_va:
                    self.allimports['Imports'].append( [hex(self.baddr+imp.rva), imp.name] )
                else:
                    self.allimports['Imports'].append( [hex(imp.rva), imp.name] )
        return self.allimports

    def get_imports(self):
        if not self.allimports:
            print "[*] Get imports"
            for imp in self.bin.get_imports():
                if '__' in imp.name:
                    dll, imp_name = imp.name.split('__')
                else:
                    dll, imp_name = imp.name.split('_')
                if not dll in self.allimports.keys():
                    self.allimports[dll] = []
                if not self.use_va:
                    self.allimports[dll].append( [hex(self.baddr+imp.rva), imp_name] )
                else:
                    self.allimports[dll].append( [hex(imp.rva), imp.name] )
        return self.allimports

    def get_exports(self):
        if not self.allexports:
            print "[*] Get exports"
            for sym in self.bin.get_symbols():
                if not self.use_va:
                    self.allexports.append( [hex(self.baddr+sym.rva), "sym." + sym.name, '', ''] )
                else:
                    self.allexports.append( [hex(sym.rva), "sym." + sym.name, '', ''] )
        return self.allexports

    def get_callgraph(self, addr=''):
        #if not self.dot:
        #print "[*] Get callgraph"
        self.update_progress_bar("Loading callgraph", 0.4)
        file = tempfile.gettempdir() + os.sep + 'graph.dot'

        if self.graph_layout == 'flow':
            cmd = 'ag '
        else:
            cmd = 'agc '

        if not addr:
            sct = False
            for section in self.execsections:
                if '.text' in section:
                    self.core.cmd0(cmd + 'section..text > ' + file)
                    sct = False
                    break
                else:
                    sct = True
            if sct:
                self.core.cmd0(cmd + 'section' + self.execsections[0][0] +' > ' + file)
            #self.core.cmd_str('aga > ' + file)
        else:
            self.core.cmd0(cmd + addr + ' > ' + file)
        f = open(file, 'r')
        self.dot = f.read()
        f.close()
        os.unlink(file)
        return self.dot

    def get_file_info(self):
        #print "[*] Get file info"
        self.update_progress_bar("Getting additional file info", 0.9)

        if self.info:
            self.fileinfo = {'name':self.info.file, 'format':self.info.rclass, 'processor':self.info.machine, 'OS':self.info.os, 'size':self.size}
        else:
            self.fileinfo = {'name':self.info_file, 'size':self.size}

        return self.fileinfo

    def get_full_file_info(self):
        #print "[*] Get file structure"
        self.update_progress_bar("Loading full file structure", 0.2)
        if not self.full_fileinfo:
            # get binary info
            file_info = self.core.cmd_str('iI')
            if file_info:
                self.full_fileinfo['bin'] = []
                for line in file_info.split('\n'):
                    line = line.split('=')
                    self.full_fileinfo['bin'].append(line)
            # Get imports
            imports = self.core.cmd_str('ii')
            if imports:
                self.full_fileinfo['imports'] = []
                for line in imports.split('\n'):
                    line = line.split(' ')
                    self.full_fileinfo['imports'].append(line)
            # Get entry points
            entryp = self.core.cmd_str('ie')
            if entryp:
                self.full_fileinfo['eps'] = []
                for line in entryp.split('\n'):
                    line = line.split(' ')
                    self.full_fileinfo['eps'].append(line)
            # Get symbols
            symbols = self.core.cmd_str('is')
            if symbols:
                self.full_fileinfo['symbols'] = []
                for line in symbols.split('\n'):
                    line = line.split(' ')
                    self.full_fileinfo['symbols'].append(line)
            # Get sections
            sections = self.core.cmd_str('iS')
            if sections:
                self.full_fileinfo['sections'] = []
                for line in sections.split('\n'):
                    line = line.split(' ')
                    self.full_fileinfo['sections'].append(line)
            # Get strings
            strings = self.core.cmd_str('iz')
            if strings:
                self.full_fileinfo['strings'] = []
                for line in strings.split('\n'):
                    line = line.split(' ')
                    self.full_fileinfo['strings'].append(line)

    def get_magic(self):
        self.core.cmd0('e io.va=0')
        self.ars_magica = self.core.cmd_str('pm')
        #self.core.cmd0('e io.va=true')
        #print self.ars_magica

    def seek(self, pos):
        #print pos
        self.core.cmd0('s ' + str(pos))
        return True

    def set_bsize(self, size):
        self.core.cmd0('b ' + str(size))
        return True

    def execute_command(self, command):
        res = self.core.cmd_str(command)
        return res

    def add_comment(self, offset, comment):
        self.core.cmd0('CC 1 ' + comment + ' @ ' + offset)
        return True

    def move(self, direction, output):
        if direction == 'f':
            direction = ''
        elif direction == 'b':
            direction = '.'

        va = self.core.cmd_str('e io.va').rstrip()

        if output == 'hexadecimal':
            if va == "true":
                self.core.cmd0('e io.va=0')
            self.core._cmd('px', True)
            data = self.core.cmd_str(direction)
            #self.core.cmd0('e io.va=true')
        elif output == 'disassembly':
            if va == "false":
                self.core.cmd0('e io.va=1')
            self.core._cmd('pd', True)
            data = self.core.cmd_str(direction)

        return data

    def search(self, text, type):
        self.core.cmd0('e io.va=0')
        self.core.cmd0('s 0')
        print "Searching %s with format %s" % (text, type)
        hits = self.core.cmd_str('/' + type + text)
        #self.core.cmd0('e io.va=1')
        self.restore_va()
        return hits

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

    def update_progress_bar(self, text, percent):
        """ Easy function to clean up the event queue and force a repaint. """
        import ui.core_functions

        if not self.progress_bar:
            return
        self.progress_bar.set_fraction(percent)
        self.progress_bar.set_text(text)
        ui.core_functions.repaint()
