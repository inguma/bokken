# -*- coding: utf-8 -*-
#       about.py
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
import gtk

class AboutDialog():
    '''About dialog'''

    def create_dialog(self):

        about = gtk.AboutDialog()
        about.set_program_name("Bokken")
        about.set_icon_from_file(os.path.dirname(__file__)+os.sep+'data'+os.sep+'bokken.svg')
        about.set_version("1.5")
        about.set_copyright("(c) Hugo Teso <hteso@inguma.eu>")
        about.set_comments("A GUI for pyew and radare2!")
        about.set_website("http://bokken.inguma.eu")
        about.set_authors(["Hugo Teso <hteso@inguma.eu>", "David Martínez <ender@inguma.eu>"])
        about.set_artists(["Ana Muniesa <ana.muniesa@gmail.com>", "Huahe <juanje@gmail.com> twitter: @huahe", "Marcos Gómez <renx67@gmail.com>"])
        about.set_logo(gtk.gdk.pixbuf_new_from_file(os.path.dirname(__file__) + os.sep + 'data' + os.sep + 'bokken.svg'))

        return about
