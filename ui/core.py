#!/usr/bin/python

#       core.py
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
import sys
import sqlite3

from hashlib import md5, sha1, sha256
from config import DATABASE_PATH

from pyew_core import CPyew

class Core():

    def __init__(self):

        self.fulldasm = ''
        self.text_dasm = ''     # Dasm of the .text section
        self.pythondasm = ''
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
        self.http_dot = ''
        self.checked_urls = []
        self.bad_urls = []

        self.pyew = CPyew()
        if os.getenv("PYEW_DEBUG"):
            self.pyew.debug=True
        else:
            self.pyew.debug = False

        self.pyew.offset = 0
        self.pyew.previousoffset = []

        self.pyew.case = 'low'

    def clean_fullvars(self):
        self.fulldasm = ''
        self.text_dasm = ''     # Dasm of the .text section
        self.pythondasm = ''
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
        self.http_dot = ''
        self.checked_urls = []
        self.bad_urls = []

    def load_file(self, file):
        # Set default file format to raw
        self.pyew.format = 'raw'

        self.pyew.loadFile(file, "rb")

        # Add global object's references for easier usage
        self.pe = self.pyew.pe
        self.elf = self.pyew.elf

        # Check if file name is an URL, pyew stores it as 'raw'
        self.is_url(file)

        if self.pyew.format in ["PE", "ELF"]:
            self.saveAndCompareInDatabase(self.pyew)
        elif self.pyew.format in ["PDF"]:
            import ui.plugins.pdfinfo as pdfinfo
            self.pdfinfo = pdfinfo.get_pdfinfo(file)
        elif self.pyew.format in ['URL']:
            #print "URL! We've got URL!"
            self.search_http_src()
            self.parse_http_locals()
        elif self.pyew.format in ["raw"]:
            #print "We've got RAW!"
            self.pyew.format = 'Plain Text'

        self.pyew.bsize = self.pyew.maxsize
        self.pyew.seek(0)

    def is_url(self, file):
        print "Checking if is URL..."
        self.filename = file
        if self.filename.lower().startswith("http://") or \
           self.filename.lower().startswith("https://") or \
           self.filename.lower().startswith("ftp://"):
            self.pyew.format = 'URL'

    def get_strings(self):
        if not self.allstrings:
            self.allstrings = self.pyew.strings(self.pyew.buf)
            strings = ''
            FILTER=''.join([(len(repr(chr(x)))==3) and chr(x) or '.' for x in range(256)])
            for element in self.allstrings:
                for key in element.keys():
                    strings += "0x%08x:\t%s\n" % (key, element[key].translate(FILTER))
            self.allstrings = strings
        return self.allstrings

    def get_functions(self):
        if not self.allfuncs:
            for func in self.pyew.functions:
                 self.allfuncs.append(self.pyew.names[func])
        return self.allfuncs

    def get_hexdump(self):
        if self.fullhex == '':
            hexdump = self.pyew.hexdump(self.pyew.buf, self.pyew.hexcolumns, baseoffset=0, bsize=self.pyew.bsize)
            self.fullhex = hexdump
        return self.fullhex

    def get_text_dasm(self):
        if not self.text_dasm:
            self.pyew.lines = 100*100
            for section in self.pe.sections:
                # Let's store text section information
                if 'text' in section.Name:
                    self.text_rsize = section.SizeOfRawData
                    break
            dis = self.pyew.disassemble(self.pyew.buf, self.pyew.processor, self.pyew.type, self.pyew.lines, self.text_rsize, baseoffset=self.pyew.ep)
            self.text_dasm = dis
        return self.text_dasm

    def get_fulldasm(self):
        if not self.fulldasm:
            self.pyew.lines = 100*100
            dis = self.pyew.disassemble(self.pyew.buf, self.pyew.processor, self.pyew.type, self.pyew.lines, self.pyew.bsize, baseoffset=self.pyew.offset)
            self.fulldasm = dis
        return self.fulldasm

    def get_python_dasm(self):
        if not self.pythondasm:
            try:
                import dis
                self.pyew.lines = 100*100
                self.pythondasm = dis.dis(self.pyew.buf)
            except:
                pass
        return self.pythondasm

    def get_repr(self):
        if not self.fullstr:
            self.fullstr = repr(self.pyew.buf)
        return self.fullstr

    def get_sections(self):
        if self.pyew.format == 'PE':
            if self.allsections == []:
                for section in self.pe.sections:
                    self.allsections.append( [section.Name.split('\x00')[0], hex(section.VirtualAddress), hex(section.Misc_VirtualSize), hex(section.SizeOfRawData)] )
#                    print "  ", section.Name, hex(section.VirtualAddress), hex(section.Misc_VirtualSize), section.SizeOfRawData
        elif self.pyew.format == 'ELF':
            if self.allsections == []:
                for section in self.pyew.elf.secnames:
                    self.allsections.append( [self.pyew.elf.secnames[section].getName(), "0x%08x" % (self.pyew.elf.secnames[section].sh_addr), "N/A", "N/A"] )

        return self.allsections

    def get_imports(self):
        try:
            if not self.allimports:
                if self.pyew.format == "PE":
                    for entry in self.pe.DIRECTORY_ENTRY_IMPORT:
#                        print entry.dll
                        self.allimports[entry.dll] = []
                        for imp in entry.imports:
                            self.allimports[entry.dll].append( [hex(imp.address), imp.name] )
#                            print '\t', hex(imp.address), imp.name
            return self.allimports
#            print self.allimports
        except:
            self.allimports.append(['No imports found', ''])
            print 'No imports found'

    def get_exports(self):
        try:
            if not self.allexports:
                if self.pyew.format == "PE":
                    for exp in self.pe.DIRECTORY_ENTRY_EXPORT.symbols:
#                        print hex(self.pyew.pe.OPTIONAL_HEADER.ImageBase + exp.address), exp.name, exp.ordinal
                        self.allexports.append( [hex(self.pyew.pe.OPTIONAL_HEADER.ImageBase + exp.address), exp.name, str(exp.ordinal), ''] )
#            print self.allexports
            return self.allexports
        except:
            self.allexports.append(['No exports found', '', '', ''])

            print 'No exports found'
            return self.allexports

    def get_virtual_address(self):
        if  self.pyew.format in ["PE"]:
            x = self.pe.OPTIONAL_HEADER.AddressOfEntryPoint
            for s in self.pe.sections:
                if x >= s.VirtualAddress and x <= s.VirtualAddress + s.SizeOfRawData:
                    break
    
            x = x - s.VirtualAddress
            x += s.PointerToRawData
            ep = x
#            print "Entry Point at 0x%x" % x
            try:
#                print "Virtual Address is 0x%0x" % (self.pe.OPTIONAL_HEADER.ImageBase + self.pe.get_rva_from_offset(x))
                va = self.pe.OPTIONAL_HEADER.ImageBase + self.pe.get_rva_from_offset(x)
                self.offset = x
                self.ep = x
            except:
                print sys.exc_info()[1]
    
            return hex(va), hex(ep)

    def get_file_info(self):
        if self.pyew.format in ["PE"]:
            # pyew.filename        : /home/hteso/Pocs/MRxNet/mrxnet.sys
            # pyew.format          : PE
            # pyew.maxfilesize     : 1073741824
            # pyew.maxsize         : 17400
            # pyew.type            : 32
            # pyew.processor       : intel
            vaddress, ep  = self.get_virtual_address()
            self.fileinfo = {'name':self.pyew.filename, 'format':self.pyew.format, 'size':self.pyew.maxsize, 'processor':self.pyew.processor, 'type':self.pyew.type, 'va':vaddress, 'ep':ep}
    #        print self.fileinfo
        elif self.pyew.format in ["ELF"]:
            self.fileinfo = {'name':self.pyew.filename, 'format':self.pyew.format, 'size':self.pyew.maxsize, 'processor':self.pyew.processor, 'type':self.pyew.type}
        elif self.pyew.format in ["PDF"]:
            self.fileinfo = {'name':self.pyew.filename, 'format':self.pyew.format, 'size':self.pyew.maxsize, 'processor':self.pyew.processor, 'type':self.pyew.type}
        # I plan to add more content here soon so I keep it separated
        elif self.pyew.format in ['URL']:
            self.fileinfo = {'name':self.pyew.filename, 'format':self.pyew.format, 'size':self.pyew.maxsize}
        else:
            self.fileinfo = {'name':self.pyew.filename, 'format':self.pyew.format, 'size':self.pyew.maxsize}

        return self.fileinfo

    def get_pdf_info(self):
        return self.pdfinfo

    def get_pdf_streams(self):
        import ui.plugins.pdfinfo as pdfinfo
        self.streams = pdfinfo.pdfStream(self.pyew)
        return self.streams

    def get_callgraph(self):
        import ui.plugins.cgraph as cgraph
        dot_code = cgraph.showCallGraph(self.pyew)
        return dot_code

    def get_urls(self):
        import ui.plugins.url as url
        urls = url.extract(self.pyew)
        return urls

    def check_urls(self):
        import ui.plugins.url as url
        checked_urls = url.check(self.pyew)
        self.checked_urls = checked_urls

    def bad_urls(self):
        import ui.plugins.url as url
        bad_urls = url.check_bad(self.pyew)
        self.bad_urls = bad_urls

    def sendto_vt(self):
        import ui.plugins.virustotal as virustotal
        vt_results = virustotal.search_vt(self.pyew)
        return vt_results

    def execute_plugin(self, plugin):
        plg = plugin.split(" ")
        if len(plg) == 1:
            self.pyew.plugins[plg[0]](self.pyew)
        else:
            self.pyew.plugins[plg[0]](self.pyew, plg[1:])

    def get_packers(self):
        import ui.plugins.packer as packer
        packers = packer.search_packer(self.pyew)
        return packers

    def dosearch(self, data, type):
        # search types: s, u, r, o, i, x

        results = self.pyew.dosearch(self.pyew.f, type, data, offset=self.pyew.offset, cols=64, doprint=False)
        return results

    def search_http_src(self):
        srcs = self.pyew.dosearch(self.pyew.f, 's', 'src="', offset=self.pyew.offset, cols=100, doprint=False)
        hrefs = self.pyew.dosearch(self.pyew.f, 's', 'href="', offset=self.pyew.offset, cols=100, doprint=False)
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
                root = next(s for s in element if s)
                root_index = element.index(root)
                self.links_struct.append( {root:element[root_index + 1:]} )
            elif len(element) == 1:
                self.links_struct.append( {element[0]:['']} )
        import ui.generate_dot as gendot
        self.http_dot = gendot.generate_dot(self.links_struct, self.pyew.filename)

    def get_file_text(self):
        file = open(self.pyew.filename, 'rb')
        data = file.read()
        file.close()

        return data

    def saveAndCompareInDatabase(self, pyew):
        db = sqlite3.connect(DATABASE_PATH)
        self.createSchema(db)
        cur = db.cursor()
        bcontinue = True
        
        try:
            buf = self.pyew.getBuffer()
            amd5 = md5(buf).hexdigest()
            name = self.pyew.filename
            sql = """ select * from samples where md5 = ? """
            cur.execute(sql, (amd5, ))
            
            for row in cur.fetchall():
                if row[4] != name:
                    print "NOTICE: File was previously analyzed (%s)" % row[4]
                    print
                bcontinue = False
            cur.close()
            
            if bcontinue:
                self.saveSample(db, pyew, buf, amd5)
        except:
            print sys.exc_info()[1]
            raise

    def saveSample(self, db, pyew, buf, amd5):
        try:
            asha1 = sha1(buf).hexdigest()
            asha256 = sha256(buf).hexdigest()
            name = self.pyew.filename
            format = self.pyew.format
            
            cur = db.cursor()
            sql = """ insert into samples (md5, sha1, sha256, filename, type)
                                   values (?, ?, ?, ?, ?)"""
            cur.execute(sql, (amd5, asha1, asha256, name, format))
            rid = cur.lastrowid
            
            sql = """ insert into function_stats (sample_id, addr, nodes, edges, cc)
                                          values (?, ?, ?, ?, ?) """
            for f in self.pyew.function_stats:
                addr = "0x%08x" % f
                nodes, edges, cc = self.pyew.function_stats[f]
                cur.execute(sql, (rid, addr, nodes, edges, cc))
            
            sql = """ insert into antidebugs (sample_id, addr, mnemonic) values (?, ?, ?) """
            for antidbg in self.pyew.antidebug:
                addr, mnem = antidbg
                addr = "0x%08x" % addr
                cur.execute(sql, (rid, addr, mnem))
            
            db.commit()
        except:
            print sys.exc_info()[1]
            pass

    def createSchema(self, db):
        try:
            sql = """create table samples (id integer not null primary key,
                                           md5, sha1, sha256, filename, type)"""
            db.execute(sql)
            
            sql = """create table function_stats (
                            id integer not null primary key,
                            sample_id, addr, nodes, edges, cc)"""
            db.execute(sql)
            
            sql = """create table antidebugs (
                            id integer not null primary key,
                            sample_id, addr, mnemonic
                            )"""
            db.execute(sql)
        except:
            pass
    
