#       url.py
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


import re

def extract(pyew):

    from plugins.url import doFind

    urlfinders = [
        re.compile("((http|ftp|mailto|telnet|ssh)(s){0,1}\:\/\/[\w|\/|\.|\#|\?|\&|\=|\-|\%]+)+", re.IGNORECASE | re.MULTILINE)
    ]

    moffset = pyew.offset
    pyew.offset = 0
    pyew.seek(0)
    buf = pyew.buf
    ret = []
    
    for x in urlfinders:
        ret += doFind(x, buf)

    buf = buf.replace("\x00", "")
    uniret = []
    for x in urlfinders:
        uniret += doFind(x, buf)

    tmp = {}
    for x in ret:
        tmp[x] = x
    ret = tmp.values()

    pyew.seek(moffset)
    return ret

def check(pyew):
    """ Check URLs of the current file """

    import sys, urllib

    oks = []
    urls = extract(pyew)
    
    if len(urls) == 0:
        print "***No URLs found"
        return

    for url in urls:
        try:
            r = urllib.urlopen(url)
            
            oks.append(url)
        except KeyboardInterrupt:
            print "Aborted"
            break
        except:
            sys.stdout.write("DOWN\n")
            sys.stdout.flush()
        
    return oks

def check_bad(pyew):
    """ Check for known bad URLs """

    import sys, urllib
    returls = []
    
    url = "http://www.malware.com.br/cgi/submit?action=list_adblock"
    try:
        l = urllib.urlopen(url).readlines()
    except:
        print "***Error fetching URL list from www.malware.com.br:", sys.exc_info()[1]
        return

    urls = extract(pyew)
    
    if len(urls) == 0:
        print "***No URLs found"
        return

    for url in urls:
        for badurl in l:
            if badurl.startswith("["):
                continue
            badurl = badurl.strip("\n").strip("\r")
            if url.lower().find(badurl) > -1:
                print "***Found bad URL: %s" % url
                
                returls.append(url)
                break

    return returls
