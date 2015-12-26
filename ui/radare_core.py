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

import lib.common as common
import lib.backend
import os
import re
import tempfile

from r2.r_core import *
from r2.r_bin import *

class Core(lib.backend.BasicBackend):

    def __init__(self, dialog):

        # We init just basic things, then create all the rest.
        self.corename = 'radare'
        self.backend = 'radare'
        self.version = R2_VERSION
        self.debug = False

        self.clean_fullvars()

        self.set_options(dialog)

    def send_cmd(self, string):
        '''This function is in the middle of the communication of the core and
        Bokken to be able to intercept input and output.'''
        if self.debug:
            print('DEBUG IN : %s' % string)
        output = self.core.cmd0(string)
        if self.debug:
            print('DEBUG OUT: %s' % output)
        return output

    def send_cmd_str(self, string):
        '''This function is in the middle of the communication of the core and
        Bokken to be able to intercept input and output.'''
        if self.debug:
            print('DEBUG IN : %s' % string)
        output = self.core.cmd_str(string)
        if self.debug:
            print('DEBUG OUT: %s' % output)
        return output

    def clean_fullvars(self):
        '''Function to initialize members in the Core class.  Common (i.e.
        non-r2) variables should be migrated to the BasicCore class.'''

        self.fulldasm = ''
        self.text_dasm = ''     # Dasm of the .text section
        self.pythondasm = ''
        self.textsize= 0
        self.fullhex = ''
        self.allstrings = []
        self.allrelocs = []
        self.allfuncs = []
        self.allsections = []
        self.execsections = []
        self.sections_size = []
        self.sections_lines = []
        self.allimports = {}
        self.allexports = []
        self.alllinks = []
        self.filename = ''
        self.file_loaded = False
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

    def load_file(self, filename):
        self.update_progress_bar("Loading file", 0.1)
        self.filename = filename
        open_result = self.core.file_open(filename, 0, 0)
        if open_result is None:
            self.file_loaded = False
            return
        self.file_loaded = True
        self.core.bin_load(None, 0)
        self.send_cmd("e scr.interactive=false")
        self.send_cmd('e asm.lines=false')
        self.send_cmd('e scr.color=0')
        self.send_cmd('e asm.demangle=true')

        # Improve asm format
        self.send_cmd('e asm.bytespace=true')
        self.send_cmd('e asm.cmtright=true')
        self.send_cmd('e asm.xrefs=false')          # Show xrefs in disassembly
        self.send_cmd('e asm.cmtflgrefs=false')     # Show comment flags associated to branch reference
        self.send_cmd('e asm.fcnlines=false')
        self.send_cmd('e asm.linesright=true')
        self.send_cmd('e asm.cmtcol=50')

        if not self.lower_case:
            self.send_cmd('e asm.ucase=true')
        else:
            self.send_cmd('e asm.ucase=false')
        if self.use_va:
            self.send_cmd("e io.va=0")
        else:
            self.send_cmd("e io.va=1")
        if self.asm_syntax:
            # TODO: fix until r2 fixes ATT with capstone
            # once this happens, remove next line
            self.send_cmd("e asm.arch=x86.udis")
            self.send_cmd("e asm.syntax=att")
        else:
            self.send_cmd("e asm.syntax=intel")
        if self.asm_bytes:
            self.send_cmd("e asm.bytes=false")
        else:
            self.send_cmd("e asm.bytes=true")
        if self.do_anal:
            self.send_cmd("aa")
            self.send_cmd("aac")
            self.send_cmd("aaa")
            self.send_cmd("af;ac@$S")
        if self.start_addr:
            self.send_cmd('af @ %s' % self.start_addr)
        if self.arch:
            self.send_cmd('e asm.arch=%s' % self.arch)
        if self.bits:
            self.send_cmd('e asm.bits=%s' % self.bits)
        if self.flow_lines:
            self.send_cmd('e asm.lines=true')
            self.send_cmd('e asm.lineswidth=%s' % self.flow_lines_w)
        if self.pseudo:
            self.send_cmd('e asm.pseudo=true')
        if self.stack:
            self.send_cmd('e asm.stackptr=true')
        self.send_cmd('e anal.depth=%s' % self.anal_depth)

        self.bin = self.core.bin
        self.info = self.bin.get_info()
        if not self.info:
            output = self.send_cmd_str('i').split('\n')
            for line in output:
                if line:
                    line = line.split('\t')
                    if line[0] == 'size':
                        self.size = line[1]
                    elif line[0] == 'uri':
                        self.info_file = line[1]

        self.baddr = self.bin.get_baddr()
        self.size = hex(self.core.io.size())
        self.send_cmd('e search.flags=false')
        if self.do_anal:
            self.core.format = 'Program'
        else:
            self.core.format = 'Hexdump'
        # Check if file is a supported program
        if not hasattr(self.info, 'type'):
            self.core.format = 'Hexdump'

    def set_options(self, dialog):
        """Method to load all the options from a client."""
        """TODO: I know that I'm passing a UI component, but until the progress
        bar goes away and I just pass a dialog.options structure with just the
        data, there's no real point into splitting them up."""

        self.lower_case = dialog.opt_case
        self.do_anal = dialog.opt_analyze_bin
        self.asm_syntax = dialog.opt_asm_syntax
        self.use_va = dialog.opt_use_va
        self.asm_bytes = dialog.opt_asm_bytes
        self.start_addr = dialog.opt_start_addr
        self.arch = dialog.opt_arch
        self.bits = dialog.opt_bits
        self.flow_lines = dialog.opt_flow_lines
        self.flow_lines_w = dialog.opt_flow_lines_w
        self.pseudo = dialog.opt_pseudo
        self.stack = dialog.opt_stack
        self.anal_depth = dialog.opt_anal_depth
        self.progress_bar = dialog.progress_bar

    def restore_va(self):
        if self.use_va:
            self.send_cmd("e io.va=0")
        else:
            self.send_cmd("e io.va=1")

    def get_strings(self):
        if not self.allstrings:
            self.update_progress_bar("Getting strings", 0.6)
            if self.use_va:
                self.send_cmd('e io.va=0')
            else:
                self.send_cmd('e io.va=1')
            strings = ''
            self.send_cmd('fs strings')
            strings = self.send_cmd_str('f')
            strings = strings.split('\n')
            for string in strings:
                string = string.split(' ')
                self.allstrings.append(string)
        return self.allstrings

    def get_relocs(self):
        if not self.allrelocs:
            self.update_progress_bar("Getting relocs", 0.7)
            if self.use_va:
                self.send_cmd('e io.va=0')
            else:
                self.send_cmd('e io.va=1')
            relocs = ''
            self.send_cmd('fs relocs')
            relocs = self.send_cmd_str('f')
            relocs = relocs.split('\n')
            for reloc in relocs:
                reloc = reloc.split(' ')
                if len(reloc) == 3:
                    self.allrelocs.append(reloc)
        return self.allrelocs

    def get_functions(self):
        if not self.allfuncs:
            self.update_progress_bar("Getting functions", 0.8)
            #self.send_cmd('aa')
            #self.send_cmd('fs functions')
            #if self.bin.get_sym(0):
            #    self.allfuncs.append('entry0')
            if self.bin.get_sym(1):
                self.allfuncs.append('sym._init')
            if self.bin.get_sym(2):
                self.allfuncs.append('main')
            if self.bin.get_sym(3):
                self.allfuncs.append('sym._fini')
            for fcn in self.send_cmd_str('afl').split('\n'):
                if fcn:
                    #print ' 0x%08x' % fcn.addr, fcn.name
                    fcn = fcn.split(' ')[-1]
                    self.allfuncs.append(fcn)
        return self.allfuncs

    def get_hexdump(self):
        self.update_progress_bar("Getting hexdump", 0.75)
        #self.send_cmd('e io.va=0')
        hexdump = self.send_cmd_str('px')
        #self.send_cmd('e io.va=1')
        return hexdump

    def get_full_hexdump(self):
        if self.fullhex == '' and self.size != '0x0':
            self.update_progress_bar("Getting full hexdump", 0.5)
            self.send_cmd('e io.va=0')
            self.send_cmd('s 0')
            self.send_cmd('b ' + str(self.size))
            hexdump = self.send_cmd_str('px')
            self.send_cmd('s ' + str(self.baddr))
            self.send_cmd('b 512')
            #self.send_cmd('e io.va=1')
            self.fullhex = hexdump
        return self.fullhex

    def get_dasm(self):
        self.update_progress_bar("Getting dasm",0.25)
        dasm = self.send_cmd_str('pd')
        return dasm

    def get_text_dasm(self):
        base_percent = 0.3
        step = 0.01

        if not self.text_dasm:
            #self.update_progress_bar("Getting text dasm",base_percent)
            percent = base_percent
            for section in self.execsections:
                percent += step
                dasm = ''
                self.send_cmd('s section.' + section[0])
                self.send_cmd('b ' + str(section[1]))
                #print "\t* Let's get the dasm for %s..." % section[0],
                #self.update_progress_bar("Reading assembler for section %s..." % section[0], percent)
                dasm = self.send_cmd_str('pD')
                # In radare 0.9.6 even with clean output sometimes you get an
                # ANSI code.
                dasm = re.sub('\x1b\[[0-9;]+m', '', dasm)
                self.sections_lines.append(len(dasm.split('\n')))
                self.send_cmd('b 512')
                #print " OK!"
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
            self.send_cmd('s ' + str(self.baddr))
            self.send_cmd('b ' + str(self.size))
            dasm = self.send_cmd_str('pd')
            self.send_cmd('b 512')
            self.fulldasm = dasm
        return self.fulldasm

    def get_fulldasm_through_queue(self, queue, event):
        queue.put(self.get_fulldasm())
        event.set()

    def get_sections(self):
        if self.allsections == [] and self.core.format != 'Hexdump':
            self.update_progress_bar("Getting sections", 0.15)
            for section in self.bin.get_sections():
                if common.version_ge(self.version, '0.9.8'):
                    self.allsections.append([section.name, hex(self.baddr+section.vaddr), hex(section.size), hex(section.paddr)])
                else:
                    self.allsections.append([section.name, hex(self.baddr+section.rva), hex(section.size), hex(section.offset)])
                if section.srwx & 1 == 1 and section.name != "phdr0":
                    self.execsections.append([section.name, section.size])
                    self.sections_size.append(section.size)
                if '.text' in section.name:
                    self.textsize = section.size
            self.sections_size.append(sum(self.sections_size))

        return self.allsections

    def get_elf_imports(self):
        if not self.allimports:
            #print "[*] Get ELF imports"
            for imp in self.bin.get_imports():
                if not 'Imports' in self.allimports.keys():
                    self.allimports['Imports'] = []
                if not self.use_va:
                    self.allimports['Imports'].append([str(imp.ordinal), imp.name])
                else:
                    self.allimports['Imports'].append([str(imp.ordinal), imp.name])
        return self.allimports

    def get_imports(self):
        if not self.allimports:
            #print "[*] Get imports"
            for imp in self.bin.get_imports():
                if '__' in imp.name:
                    dll, imp_name = imp.name.split('__', 1)
                else:
                    dll, imp_name = imp.name.split('_', 1)
                if not dll in self.allimports.keys():
                    self.allimports[dll] = []
                if not self.use_va:
                    self.allimports[dll].append([str(imp.ordinal), imp_name])
                else:
                    self.allimports[dll].append([str(imp.ordinal), imp.name])
        return self.allimports

    def get_exports(self):
        if not self.allexports:
            #print "[*] Get exports"
            for sym in self.bin.get_symbols():
                if not self.use_va:
                    if common.version_ge(self.version, '0.9.8'):
                        self.allexports.append([hex(self.baddr+sym.vaddr), "sym." + sym.name, '', ''])
                    else:
                        self.allexports.append([hex(self.baddr+sym.rva), "sym." + sym.name, '', ''])
                else:
                    if common.version_ge(self.version, '0.9.8'):
                        self.allexports.append([hex(sym.vaddr), "sym." + sym.name, '', ''])
                    else:
                        self.allexports.append([hex(sym.rva), "sym." + sym.name, '', ''])
        return self.allexports

    def get_callgraph(self, addr=''):
        self.update_progress_bar("Loading callgraph", 0.4)

        # We have to call it with False because otherwise the UAC in Win7 won't allow us to access the
        # temporary file from two different processes.  So we will need to remove the file after closing it.
        file = tempfile.NamedTemporaryFile(delete=False)

        if self.graph_layout == 'flow':
            cmd = 'ag '
        else:
            cmd = 'agc '

        if not addr:
            sct = False
            for section in self.execsections:
                if '.text' in section:
                    self.send_cmd(cmd + 'section..text > ' + file.name)
                    sct = False
                    break
                else:
                    sct = True
            if sct:
                self.send_cmd(cmd + 'section' + self.execsections[0][0] +' > ' + file.name)
            #self.send_cmd_str('aga > ' + file.name)
        else:
            self.send_cmd(cmd + addr + ' > ' + file.name)
        file.close()
        f = open(file.name, 'r')
        self.dot = f.read()
        f.close()
        os.unlink(file.name)
        self.dot = self.dot.replace('graph [bgcolor=white];', 'graph [color=white, bgcolor="invis"];')
        self.dot = self.dot.replace('fontsize="8"', 'fontsize="14"')
        return re.sub('style=filled ', 'style="rounded,filled" fillcolor="white" ', self.dot)

    def get_file_info(self):
        self.update_progress_bar("Getting additional file info", 0.9)

        size_string = '%s (%d bytes)' % (self.size, int(self.size[:-1], 16))
        if self.info:
            self.fileinfo = {'Name':self.info.file, 'Format':self.info.rclass, 'Arch':self.info.machine, 'OS':self.info.os, 'Size':size_string}
        else:
            self.fileinfo = {'Name':self.info_file, 'Size':size_string}

        return self.fileinfo

    def get_full_file_info(self):
        self.update_progress_bar("Loading full file structure", 0.2)
        if not self.full_fileinfo:
            # get binary info
            file_info = self.send_cmd_str('iI')
            if file_info:
                self.full_fileinfo['bin'] = []
                for line in file_info.split('\n'):
                    line = line.split(' ')
                    self.full_fileinfo['bin'].append(line)
            # Get imports
            imports = self.send_cmd_str('ii')
            if imports:
                self.full_fileinfo['imports'] = []
                for line in imports.split('\n'):
                    line = line.split(' ')
                    if len(line) == 5:
                        self.full_fileinfo['imports'].append(line)
            # Get entry points
            entryp = self.send_cmd_str('iej')
            if entryp:
                self.full_fileinfo['eps'] = []
                for line in entryp.split('\n'):
                    line = line.strip('[').strip(']')
                    self.full_fileinfo['eps'].append(['Entry0', hex(int(line))])
            # Get symbols
            symbols = self.send_cmd_str('is')
            if symbols:
                self.full_fileinfo['symbols'] = []
                for line in symbols.split('\n'):
                    line = line.split(' ')
                    self.full_fileinfo['symbols'].append(line)
            # Get sections
            sections = self.send_cmd_str('iS')
            if sections:
                self.full_fileinfo['sections'] = []
                for line in sections.split('\n'):
                    line = line.split(' ')
                    self.full_fileinfo['sections'].append(line)
            # Get strings
            strings = self.send_cmd_str('iz')
            if strings:
                self.full_fileinfo['strings'] = []
                for line in strings.split('\n'):
                    line = line.split(' ')
                    self.full_fileinfo['strings'].append(line)

    def get_magic(self):
        self.send_cmd('e io.va=0')
        self.ars_magica = self.send_cmd_str('pm')
        #self.send_cmd('e io.va=true')
        #print self.ars_magica

    def set_bsize(self, size):
        self.send_cmd('b ' + str(size))
        return True

    def execute_command(self, command):
        res = self.send_cmd_str(command)
        return res

    def add_comment(self, offset, comment):
        self.send_cmd('CC 1 ' + comment + ' @ ' + offset)
        return True

    def string_search(self, text, type):
        '''Searches an arbitrary string text in the analyzed content.'''
        self.send_cmd('e io.va=0')
        self.send_cmd('s 0')
        results = {}

        hits = self.send_cmd_str('/' + type + text).rstrip().split('\n')
        # The first line is 'fs hits', so discard it.
        hits = hits[1:]
        # The output is:
        # f hit4_0 1 0x0000023a
        # f hit4_1 1 0x00000243
        # ...
        # We get just the last word from every line.
        # What we do is to make every element a list.  Theoretically it should
        # be (address, address_text) but radare returns just the first one, so
        # for the time being we put an empty string as the second element.
        results = map(lambda x: (x.split(' ')[0], x.split(' ')[1]), hits)

        #self.send_cmd('e io.va=1')
        self.restore_va()
        return results

    def update_progress_bar(self, text, percent):
        """ Easy function to clean up the event queue and force a repaint. """
        import ui.gtk3.common

        if not self.progress_bar:
            return
        self.progress_bar.set_fraction(percent)
        self.progress_bar.set_text(text)
        ui.gtk3.common.repaint()

    @staticmethod
    def get_plugins():
        core = RCore()
        try:
            return core.assembler.get_plugins()
        except AttributeError:
            from collections import namedtuple
            Plugin = namedtuple('Plugin',['name', 'arch', 'bits', 'desc'])
            return [Plugin('arm',  'arm',  0x70, 'Capstone ARM disassembler'),
                    Plugin('java', 'java', 0x20, 'Java bytecode'),
                    Plugin('mips', 'mips', 0x70, 'Capstone MIPS disassembler'),
                    Plugin('ppc',  'ppc',  0x60, 'PowerPC'),
                    Plugin('sparc','sparc',0x60, 'Scalable Processor Architecture'),
                    Plugin('x86',  'x86',  0x70, 'udis86 x86-16,32,64')]
