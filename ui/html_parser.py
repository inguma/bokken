#       html_parser.py
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

from HTMLParser import HTMLParser

class MyHTMLParser(HTMLParser):

    def print_contents(self, html):
        self.tag_stack = []
        self.comments = []
        self.scripts = []
        self.forms = []
        self.title = ''

        self.feed(html)

    def handle_starttag(self, tag, attrs):
#        if tag.lower() in ['form', 'input']:
#            print "Encountered the beginning of a %s tag" % tag
        self.tag_stack.append(tag.lower())
        if tag.lower() == 'form':
            attrs.insert(0, 'form')
            self.forms.append(attrs)
#            print "Form:", attrs
        elif tag.lower() == 'input':
            self.forms.append(attrs)
#            print attrs

    def handle_endtag(self, tag):
        self.tag_stack.pop()
#        if tag.lower() in ['form', 'input']:
#            print "Encountered the end of a %s tag" % tag

    def handle_comment(self, data):
        #print "Encountered the comment: %s" % data
        self.comments.append("%s" % data)

    def handle_data(self, data):
        if self.tag_stack:
            if self.tag_stack[-1] in ['script']:
                #print "%s" % data
                self.scripts.append("%s" % data)
            elif self.tag_stack[-1] in ['title']:
                self.title = data
