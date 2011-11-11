#       pyew_core.py
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
import cookielib
import urllib2

import ui.html_parser as html_parser
from hashlib import md5, sha1, sha256
from config import DATABASE_PATH

from pyew_core import CPyew

class Core():

    def __init__(self, case, deep_anal, progress_bar=None):

        self.low_case = case
        self.deep_anal = deep_anal
        self.progress_bar = progress_bar

        self.fulldasm = ''
        self.text_dasm = ''     # Dasm of the .text section
        self.pythondasm = ''
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
        self.pdfinfo = ''
        self.alllinks = []
        self.parsed_links = {'remotes':[], 'locals':[]}
        self.links_struct = []
        self.url_headers = {}
        self.url_cookies = []
        self.http_dot = ''
        self.checked_urls = []
        self.bad_urls = []
        self.cmd = ''
        self.last_cmd = ''
        self.corename = 'pyew'

        self.core = CPyew()
        if os.getenv("PYEW_DEBUG"):
            self.core.debug=True
        else:
            self.core.debug = False

        self.backend = 'pyew'

        self.core.offset = 0
        self.core.previousoffset = []
        if self.deep_anal:
            self.core.deepcodeanalysis = True

        if self.low_case:
           self.core.case = 'low'
        self.core.physical = False
        self.core.virtual = True

    def clean_fullvars(self):
        self.fulldasm = ''
        self.text_dasm = ''     # Dasm of the .text section
        self.pythondasm = ''
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
        self.pdfinfo = ''
        self.alllinks = []
        self.parsed_links = {'remotes':[], 'locals':[]}
        self.links_struct = []
        self.url_headers = {}
        self.url_cookies = []
        self.http_dot = ''
        self.checked_urls = []
        self.bad_urls = []
        self.cmd = ''
        self.last_cmd = ''

    def set_options(self, low_case, deep_anal, progress_bar):
        if deep_anal:
            self.core.deepcodeanalysis = True
        else:
            self.core.deepcodeanalysis = False

        if low_case:
            self.core.case = 'low'
        else:
            self.core.case = 'high'

        self.progress_bar = progress_bar

    def load_file(self, file):
        self.update_progress_bar("Loading file", 0.1)
        # Set default file format to raw
        self.core.format = 'raw'

        self.core.loadFile(file, "rb")

        # Add global object's references for easier usage
        self.pe = self.core.pe
        self.elf = self.core.elf

        # Check if file name is an URL, pyew stores it as 'raw'
        self.is_url(file)

        if self.core.format in ["PE", "ELF"]:
            self.saveAndCompareInDatabase(self.core)
        elif self.core.format in ["PDF"]:
            import ui.plugins.pdfinfo as pdfinfo
            self.pdfinfo = pdfinfo.get_pdfinfo(file)
        elif self.core.format in ['URL']:
            #print "URL! We've got URL!"
            self.search_http_src()
            self.parse_http_locals()
            self.get_headers_cookies()
        elif self.core.format in ["raw"]:
            #print "We've got RAW!"
            self.core.format = 'Plain Text'

        #self.core.bsize = self.core.maxsize
        self.core.seek(0)

    def is_url(self, file):
        #print "Checking if is URL..."
        self.filename = file
        if self.filename.lower().startswith("http://") or \
           self.filename.lower().startswith("https://") or \
           self.filename.lower().startswith("ftp://"):
            self.core.format = 'URL'

    def get_strings(self):
        if not self.allstrings:
            self.update_progress_bar("Getting strings", 0.6)
            self.allstrings = self.core.strings(self.core.buf)
            strings = ''
            FILTER=''.join([(len(repr(chr(x)))==3) and chr(x) or '.' for x in range(256)])
            for element in self.allstrings:
                for key in element.keys():
                    strings += "0x%08x:\t%s\n" % (key, element[key].translate(FILTER))
            self.allstrings = strings
        return self.allstrings

    def get_functions(self):
        if not self.allfuncs:
            self.update_progress_bar("Getting functions", 0.8)
            for func in self.core.functions:
                 #print "0x%08x" % (func)
                 self.allfuncs.append(self.core.names[func])
        return self.allfuncs

    def get_hexdump(self):
        self.update_progress_bar("Getting hexdump", 0.75)
        hexdump = self.core.hexdump(self.core.buf, self.core.hexcolumns, baseoffset=self.core.offset, bsize=self.core.bsize)
        return hexdump

    def get_full_hexdump(self):
        if self.fullhex == '':
            self.update_progress_bar("Getting full hexdump", 0.5)
            self.core.bsize = self.core.maxsize
            self.core.seek(0)
            hexdump = self.core.hexdump(self.core.buf, self.core.hexcolumns, baseoffset=0, bsize=self.core.bsize)
            self.fullhex = hexdump
        self.core.bsize = 512
        return self.fullhex

    def get_dasm(self):
        self.update_progress_bar("Getting dasm",0.25)
        dis = self.core.disassemble(self.core.buf, self.core.processor, self.core.type, self.core.lines, self.core.bsize, baseoffset=self.core.offset)
        return dis

    def get_text_dasm(self):
        self.core.bsize = self.core.maxsize

        base_percent = 0.3
        step = 0.01

        #self.seek(0)
        if not self.text_dasm:
            #self.update_progress_bar("Getting text dasm",base_percent)
            percent = base_percent
            self.core.lines = 100*100
            if self.core.format == 'PE':
                #dasm = ''
                for section in self.execsections:
                    percent += step
                    # Let's store text section information
                    #print hex(self.core.pe.OPTIONAL_HEADER.ImageBase + section.VirtualAddress)
                    #self.update_progress_bar("Reading assembler for section %s..." % section[0][0], percent)
                    self.text_rsize = section[1]
                    self.text_address = section[2]
                    self.seek(self.text_address)
                    dis = self.core.disassemble(self.core.buf, self.core.processor, self.core.type, self.core.lines, self.text_rsize, baseoffset=self.text_address)
                    self.sections_lines.append( len(dis.split('\n')) )
                    self.text_dasm += ';; ------------------------\n;; Section: %s\n;; ------------------------\n' % section[0][0]
                    self.text_dasm += dis
                    #print "OK"
                    if percent == base_percent + step * 10:
                        percent -= step
                self.sections_lines.append(sum(self.sections_lines))
            elif self.core.format == 'ELF':
                for section in self.execsections:
                    percent += step
                    #print "\t* Let's get the dasm for %s..." % section[0][0],
                    #self.update_progress_bar("Reading assembler for section %s..." % section[0][0], percent)
                    # Let's store text section information
                    self.text_rsize = section[1]
                    self.text_address = section[2]
                    self.seek(self.text_address)
                    dis = self.core.disassemble(self.core.buf, self.core.processor, self.core.type, self.core.lines, self.text_rsize, baseoffset=self.text_address)
                    self.sections_lines.append( len(dis.split('\n')) )
                    self.text_dasm += ';; ------------------------\n;; Section: %s\n;; ------------------------\n' % section[0]
                    self.text_dasm += dis
                    #print "OK"
                    if percent == base_percent + step * 10:
                        percent -= step
                self.sections_lines.append(sum(self.sections_lines))
        self.core.bsize = 512
        self.core.lines = 40
        #return self.text_dasm, self.sections_lines, self.text_address, self.text_rsize
        return self.text_dasm

    def get_text_dasm_through_queue(self, queue, event):
        queue.put(self.get_text_dasm())
        event.set()

    def get_fulldasm(self):
        #self.update_progress_bar("Getting text dasm", 0.3)
        self.core.bsize = self.core.maxsize
        self.seek(0)
        if not self.fulldasm:
            self.core.lines = 100*100
            dis = self.core.disassemble(self.core.buf, self.core.processor, self.core.type, self.core.lines, self.core.bsize, baseoffset=self.core.offset)
            self.fulldasm = dis
        self.core.bsize = 512
        self.core.lines = 40
        return self.fulldasm

    def get_fulldasm_through_queue(self, queue, event):
        queue.put(self.get_fulldasm())
        event.set()

    def seek(self, pos):
        data = ''
        if pos > self.core.maxsize:
            data = 'End of file reached'
            self.core.offset = self.core.maxsize
        elif pos < 0:
            data = 'Begin of file reached'
            self.core.offset = 0
        else:
            self.core.offset = pos
        if len(self.core.previousoffset) > 0:
            if self.core.previousoffset[ len(self.core.previousoffset)-1 ] != self.core.offset:
                self.core.previousoffset.append(self.core.offset)
        else:
            self.core.previousoffset.append(self.core.offset)
        
        self.core.f.seek(self.core.offset)
        self.core.buf = self.core.f.read(self.core.bsize)

        return data

    def move(self, direction, output):

        #self.core.bsize = 512
        self.cmd = direction
        limit = ''

        if len(self.core.previousoffset) > 0:
            if self.core.previousoffset[ len(self.core.previousoffset)-1 ] != self.core.offset:
                self.core.previousoffset.append(self.core.offset)
        else:
            self.core.previousoffset.append(self.core.offset)
        
#        va = None
#        if self.core.virtual:
#            va = self.core.getVirtualAddressFromOffset(self.core.offset)
#        
#        if va:
#            prompt = "[0x%08x:0x%08x]> " % (self.core.offset, va)
#        else:
#            prompt = "[0x%08x]> " % self.core.offset

        if self.cmd == "b":
            tmp = self.core.previousoffset.pop()
            
            if len(self.core.previousoffset) > 0:
                tmp = self.core.previousoffset[ len(self.core.previousoffset)-1 ]
            else:
                tmp = 0
                
            self.core.offset = tmp
            self.core.lastasmoffset = tmp

            limit = self.seek(tmp)

        elif self.cmd == "b" and self.last_cmd == "b":
            if len(self.core.previousoffset) < 2:
                return
            
            tmp = self.core.previousoffset.pop()
            tmp = self.core.previousoffset[ len(self.core.previousoffset)-1 ]

            limit = self.seek(tmp)

        elif output == 'disassembly':
            self.core.offset = self.core.lastasmoffset

            self.core.seek(self.core.offset)
#            if last_cmd.isdigit():
#                last_cmd = "c"

        else:
            self.core.offset = self.core.offset + self.core.bsize
            limit = self.seek(self.core.offset)

        self.cmd = self.last_cmd

        if not limit:
            if output == 'hexadecimal':
                data = self.get_hexdump()
            else:
                data = self.get_dasm()
            return data
        else:
            print limit
            return

    def get_python_dasm(self):
        if not self.pythondasm:
            try:
                import dis
                self.core.lines = 100*100
                self.pythondasm = dis.dis(self.core.buf)
            except:
                pass
        return self.pythondasm

    def get_repr(self):
        if not self.fullstr:
            self.update_progress_bar("Getting string representation", 0.65)
            self.fullstr = repr(self.core.buf)
        return self.fullstr

    def get_sections(self):
        self.update_progress_bar("Getting sections", 0.15)
        if self.core.format == 'PE':
            #import pefile
            #image_flags = self.core.pe.retrieve_flags(pefile.SECTION_CHARACTERISTICS, 'IMAGE_SCN_')
            if self.allsections == []:
                for section in self.pe.sections:
                    if section.__dict__.get('IMAGE_SCN_MEM_EXECUTE', False):
                        self.execsections.append([section.Name.split('\x00'[0]), section.SizeOfRawData, section.VirtualAddress])
                    self.sections_size.append(section.SizeOfRawData)
                    self.allsections.append( [section.Name.split('\x00')[0], hex(section.VirtualAddress), hex(section.Misc_VirtualSize), hex(section.SizeOfRawData)] )
#                    print "  ", section.Name, hex(section.VirtualAddress), hex(section.Misc_VirtualSize), section.SizeOfRawData
        elif self.core.format == 'ELF':
            if self.allsections == []:
                for section in self.core.elf.secnames:
                    if self.core.elf.secnames[section].sh_flags == 6:
                        self.execsections.append([self.core.elf.secnames[section].getName(), self.core.elf.secnames[section].sh_size, self.core.elf.secnames[section].sh_offset])
                    self.sections_size.append(self.core.elf.secnames[section].sh_size)
                    self.allsections.append( [self.core.elf.secnames[section].getName(), "0x%08x" % (self.core.elf.secnames[section].sh_addr), "N/A", "N/A"] )

        return self.allsections

    def get_imports(self):
        try:
            if not self.allimports:
                if self.core.format == "PE":
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
                if self.core.format == "PE":
                    for exp in self.pe.DIRECTORY_ENTRY_EXPORT.symbols:
#                        print hex(self.core.pe.OPTIONAL_HEADER.ImageBase + exp.address), exp.name, exp.ordinal
                        self.allexports.append( [hex(self.core.pe.OPTIONAL_HEADER.ImageBase + exp.address), exp.name, str(exp.ordinal), ''] )
#            print self.allexports
            return self.allexports
        except:
            self.allexports.append(['No exports found', '', '', ''])

            print 'No exports found'
            return self.allexports

    def get_virtual_address(self):
        if  self.core.format in ["PE"]:
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
        self.update_progress_bar("Getting additional file info", 0.9)
        if self.core.format in ["PE"]:
            # pyew.filename        : /home/hteso/Pocs/MRxNet/mrxnet.sys
            # pyew.format          : PE
            # pyew.maxfilesize     : 1073741824
            # pyew.maxsize         : 17400
            # pyew.type            : 32
            # pyew.processor       : intel
            vaddress, ep  = self.get_virtual_address()
            self.fileinfo = {'name':self.core.filename, 'format':self.core.format, 'size':self.core.maxsize, 'processor':self.core.processor, 'type':self.core.type, 'va':vaddress, 'ep':ep}
    #        print self.fileinfo
        elif self.core.format in ["ELF"]:
            self.fileinfo = {'name':self.core.filename, 'format':self.core.format, 'size':self.core.maxsize, 'processor':self.core.processor, 'type':self.core.type}
        elif self.core.format in ["PDF"]:
            self.fileinfo = {'name':self.core.filename, 'format':self.core.format, 'size':self.core.maxsize, 'processor':self.core.processor, 'type':self.core.type}
        # I plan to add more content here soon so I keep it separated
        elif self.core.format in ['URL']:
            self.fileinfo = {'name':self.core.filename, 'format':self.core.format, 'size':self.core.maxsize}
        else:
            self.fileinfo = {'name':self.core.filename, 'format':self.core.format, 'size':self.core.maxsize}

        return self.fileinfo

    def get_pdf_info(self):
        return self.pdfinfo

    def get_pdf_streams(self):
        import ui.plugins.pdfinfo as pdfinfo
        self.streams = pdfinfo.pdfStream(self.core)
        return self.streams

    def get_callgraph(self):
        self.update_progress_bar("Loading callgraph", 0.4)
        import ui.plugins.cgraph as cgraph
        dot_code = cgraph.showCallGraph(self.core)
        return dot_code

    def get_urls(self):
        import ui.plugins.url as url
        urls = url.extract(self.core)
        return urls

    def check_urls(self):
        import ui.plugins.url as url
        checked_urls = url.check(self.core)
        self.checked_urls = checked_urls

    def bad_urls(self):
        import ui.plugins.url as url
        bad_urls = url.check_bad(self.core)
        self.bad_urls = bad_urls

    def sendto_vt(self):
        import ui.plugins.virustotal as virustotal
        vt_results = virustotal.search_vt(self.core)
        return vt_results

    def execute_plugin(self, plugin):
        plg = plugin.split(" ")
        if len(plg) == 1:
            self.core.plugins[plg[0]](self.core)
        else:
            self.core.plugins[plg[0]](self.core, plg[1:])

    def get_packers(self):
        import ui.plugins.packer as packer
        packers = packer.search_packer(self.core)
        return packers

    def dosearch(self, data, type):
        # search types: s, u, r, o, i, x

        results = self.core.dosearch(self.core.f, type, data, offset=self.core.offset, cols=64, doprint=False)
        return results

    def search_http_src(self):
        self.update_progress_bar("Parsing HTTP source", 0.2)
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
        self.update_progress_bar("Extracting source links", 0.3)
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

    def get_headers_cookies(self):
        self.update_progress_bar("Extracting headres and cookies", 0.4)
        urlopen = urllib2.urlopen
        cj = cookielib.LWPCookieJar()
        Request = urllib2.Request

        if cj != None:
            if cookielib:
                opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
                urllib2.install_opener(opener)
        
        theurl = self.core.filename
        txdata = None
        txheaders =  {'User-agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}

        req = Request(theurl, txdata, txheaders)
        handle = urlopen(req)

#        print 'Here are the headers of the page :'
        self.url_headers = dict(handle.info())

#        print 'These are the cookies we have received so far :'
        ns_headers = handle.headers.getheaders("Set-Cookie")
        attrs_set = cookielib.parse_ns_headers(ns_headers)
        self.url_cookies = cj._normalized_cookie_tuples(attrs_set)

        parser = html_parser.MyHTMLParser()
        data = handle.read()
        parser.print_contents(data)
        self.scripts = parser.scripts
        self.comments = parser.comments
        self.forms = parser.forms

    def get_file_text(self):
        self.update_progress_bar("Getting plain text", 0.3)
        file = open(self.core.filename, 'rb')
        data = file.read()
        file.close()

        return data

    def saveAndCompareInDatabase(self, pyew):
        db = sqlite3.connect(DATABASE_PATH)
        self.createSchema(db)
        cur = db.cursor()
        bcontinue = True
        
        try:
            buf = self.core.getBuffer()
            amd5 = md5(buf).hexdigest()
            name = self.core.filename
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
            name = self.core.filename
            format = self.core.format
            
            cur = db.cursor()
            sql = """ insert into samples (md5, sha1, sha256, filename, type)
                                   values (?, ?, ?, ?, ?)"""
            cur.execute(sql, (amd5, asha1, asha256, name, format))
            rid = cur.lastrowid
            
            sql = """ insert into function_stats (sample_id, addr, nodes, edges, cc)
                                          values (?, ?, ?, ?, ?) """
            for f in self.core.function_stats:
                addr = "0x%08x" % f
                nodes, edges, cc = self.core.function_stats[f]
                cur.execute(sql, (rid, addr, nodes, edges, cc))
            
            sql = """ insert into antidebugs (sample_id, addr, mnemonic) values (?, ?, ?) """
            for antidbg in self.core.antidebug:
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

    def update_progress_bar(self, text, percent):
        """ Easy function to clean up the event queue and force a repaint. """
        import ui.core_functions

        if not self.progress_bar:
            return
        self.progress_bar.set_fraction(percent)
        self.progress_bar.set_text(text)
        ui.core_functions.repaint()
