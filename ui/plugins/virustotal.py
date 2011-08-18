#       virustotal.py
#       
#       copyright 2011 hugo teso <hugo.teso@gmail.com>
#       
#       this program is free software; you can redistribute it and/or modify
#       it under the terms of the gnu general public license as published by
#       the free software foundation; either version 2 of the license, or
#       (at your option) any later version.
#       
#       this program is distributed in the hope that it will be useful,
#       but without any warranty; without even the implied warranty of
#       merchantability or fitness for a particular purpose.  see the
#       gnu general public license for more details.
#       
#       you should have received a copy of the gnu general public license
#       along with this program; if not, write to the free software
#       foundation, inc., 51 franklin street, fifth floor, boston,
#       ma 02110-1301, usa.

import hashlib

import plugins.virustotal as vt

def search_vt(pyew):
    """ Search the sample in Virus Total """
    buf = pyew.getBuffer()
    x = hashlib.md5(buf).hexdigest()
    
    scanner = vt.CVirusTotalScanner()
    scanner.printResults = False
    matches = scanner.scan(pyew.filename, argmd5=x)

    return matches
