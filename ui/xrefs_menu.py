#       xrefs_menu.py
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

class XrefsMenu(gtk.MenuBar):
    '''Xrefs Menu'''

    def __init__(self):
        super(XrefsMenu,self).__init__()

        self.fcn_img = gtk.Image()
        self.fcn_img.set_from_file(os.path.dirname(__file__) + os.sep + 'data' + os.sep + 'function.png')

    def create_menu(self, fcn):
        # Function Menu
        xrefmenu = gtk.Menu()

        fcnm = gtk.ImageMenuItem(fcn)
        fcnm.set_image(self.fcn_img)
        label = fcnm.get_children()[0]
        label.set_markup('<b>' + fcn + '</b>')
        #fcnm.set_submenu(xrefmenu)
        xrefmenu.append(fcnm)

        # Separator
        sep = gtk.SeparatorMenuItem()
        xrefmenu.append(sep)

        # Xrefs to menu
        tomenu = gtk.Menu()

        xtomenu = gtk.ImageMenuItem(gtk.STOCK_INDENT)
        xtomenu.get_children()[0].set_label('Xrefs To')
        xtomenu.set_submenu(tomenu)

        xtoi = gtk.ImageMenuItem('WIP...')
        tomenu.append(xtoi)

        xrefmenu.append(xtomenu)

        # Xrefs from menu
        frommenu = gtk.Menu()

        xfrommenu = gtk.ImageMenuItem(gtk.STOCK_UNINDENT)
        xfrommenu.get_children()[0].set_label('Xrefs From')
        xfrommenu.set_submenu(frommenu)

        xfromi = gtk.ImageMenuItem('WIP...')
        frommenu.append(xfromi)

        xrefmenu.append(xfrommenu)

        return xrefmenu
