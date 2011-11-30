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

    def __init__(self, uicore, main):
        super(XrefsMenu,self).__init__()

        self.uicore = uicore
        self.main = main

        self.fcn_img = gtk.Image()
        self.fcn_img.set_from_file(os.path.dirname(__file__) + os.sep + 'data' + os.sep + 'function.png')

    def create_menu(self, fcn, refs, xrefs, pack=True):
        # Function Menu
        xrefmenu = gtk.Menu()

        self.fcnm = gtk.ImageMenuItem(fcn)
        self.fcnm.set_image(self.fcn_img)
        label = self.fcnm.get_children()[0]
        label.set_markup('<b>' + fcn + '</b>')
        if pack:
            xrefmenu.append(self.fcnm)

        # Separator
        sep = gtk.SeparatorMenuItem()
        xrefmenu.append(sep)

        # Xrefs to menu
        if refs:
            tmp_refs = []
            tomenu = gtk.Menu()

            self.xtomenu = gtk.ImageMenuItem(gtk.STOCK_INDENT)
            self.xtomenu.get_children()[0].set_label('Xrefs To')
            self.xtomenu.set_submenu(tomenu)

            for ref in refs:
                addr = self.uicore.core.num.get(ref)
                fcn = self.uicore.core.anal.get_fcn_at(addr)
                if fcn.name:
                    if not fcn.name in tmp_refs:
                        tmp_refs.append(fcn.name)
                        xtoi = gtk.MenuItem(fcn.name, use_underline=False)
                        xtoi.connect("activate", self._get_fcn)
                        tomenu.append(xtoi)
            if pack:
                xrefmenu.append(self.xtomenu)

        # Xrefs from menu
        if xrefs:
            tmp_xrefs = []
            frommenu = gtk.Menu()

            self.xfrommenu = gtk.ImageMenuItem(gtk.STOCK_UNINDENT)
            self.xfrommenu.get_children()[0].set_label('Xrefs From')
            self.xfrommenu.set_submenu(frommenu)

            for xref in xrefs:
                addr = self.uicore.core.num.get(xref)
                fcn = self.uicore.core.anal.get_fcn_at(addr)
                if fcn.name:
                    if not fcn.name in tmp_xrefs:
                        tmp_xrefs.append(fcn.name)
                        xfromi = gtk.MenuItem(fcn.name, use_underline=False)
                        xfromi.connect("activate", self._get_fcn)
                        frommenu.append(xfromi)
            if pack:
                xrefmenu.append(self.xfrommenu)

        return xrefmenu

    def _get_fcn(self, widget):
        address = widget.get_label()
        addr = self.uicore.core.num.get(address)
        fcn = self.uicore.core.anal.get_fcn_at(addr)
        #if 'fcn' in fcn.name:
        #self.main.tviews.update_graph(widget, address)
        self.main.tviews.search(widget, "0x%08x" % addr)
        self.main.tviews.update_graph(widget, "0x%08x" % addr)
