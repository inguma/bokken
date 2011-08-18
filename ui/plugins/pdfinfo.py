#       pdfinfo.py
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

import re
import urllib

from plugins.pdfid_PL import PDFiD2String, PDFiD

FILTER=''.join([(len(repr(chr(x)))==3) and chr(x) or '.' for x in range(256)])

def get_pdfinfo(file):
    '''Get PDF information'''

    parsed_info = []
    info = PDFiD2String(PDFiD(file, False, True, False, False), False)
    info = info.split('\n')
    for element in info:
        if not ':' in element:
            element = element.split(' ')
        else:
            element = element.split(':')
        element = filter(None, element)
        parsed_info.append(element)
    return parsed_info[1:-1]

def pdfStreams(buf):
    """ Get information about the streams """
    tokens = re.split("[,<>;\[\](:)'\r\n\t/ ]", buf)

    bfilters = False
    filters = []
    stream_filters = {}
    streams = 0

    for token in tokens:
        if token == '':
            continue
        
        token = unescape(token)
        
        if token == "Filter":
            bfilters = True
        elif token == "stream":
            streams += 1
        elif token == "endstream":
            bfilters = False
            if filters != []:
                stream_filters[streams] = filters
                filters = []
        elif bfilters and token.lower().find("decode") > -1:
            filters.append(token)

#    for stream in stream_filters:
#        for filter in stream_filters[stream]:
#            print "Stream %d uses %s" % (stream, filter.replace("[", "").replace("]", ""))

    return stream_filters
    #return stream_filters, buf

def pdfStream(pyew):
    """ Show streams list """
    l = []
    hits = pyew.dosearch(pyew.f, "s", "stream", cols=60, doprint=False, offset=0)
    buf = pyew.getBuffer()
    for hit in hits:
        key, value = hit.keys()[0], hit.values()[0]
        if buf[key-1:key] != "d":
            l.append([key, value])
#            print "HINT[0x%08x]: %s" % (key, value.translate(FILTER))

    return l

def unescape(buf):
    buf = buf.replace("#", "%")
    buf = urllib.unquote(buf)
    return buf

