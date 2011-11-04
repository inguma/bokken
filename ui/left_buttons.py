#       left_buttons.py
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

class LeftButtons(gtk.VBox):
    '''Left buttons for Treeview change'''

    def __init__(self, main):
        super(LeftButtons,self).__init__(False, 1)

        self.main = main
        self.prev_size = ()

        #################################################################
        # Left mini-toolbar
        #################################################################
        toolbar = gtk.Toolbar()
        toolbar.set_style(gtk.TOOLBAR_ICONS)

    ##################################
    # Methods

    def create_buttons(self, option):
        # Icons
        self.fcn_pix = gtk.Image()
        self.fcn_pix.set_from_file(os.path.dirname(__file__) + os.sep + 'data' + os.sep + 'function.png')
        self.bb_pix = gtk.Image()
        self.bb_pix.set_from_file(os.path.dirname(__file__) + os.sep + 'data' + os.sep + 'block.png')
        self.imp_pix = gtk.Image()
        self.imp_pix.set_from_file(os.path.dirname(__file__) + os.sep + 'data' + os.sep + 'import.png')
        self.exp_pix = gtk.Image()
        self.exp_pix.set_from_file(os.path.dirname(__file__) + os.sep + 'data' + os.sep + 'export.png')

        # Show/hide toolbar and menu
        self.hide_tb = gtk.ToggleButton()
        i = gtk.Image()
        i.set_from_stock(gtk.STOCK_GO_UP, gtk.ICON_SIZE_MENU)
        self.hide_tb.set_image(i)
        handler = self.hide_tb.connect('toggled', self._hide_tb_toggled)
        self.hide_tb.handler = handler

        self.pack_start(self.hide_tb, False, False, 0)

        if 'bin' in option:
            # Functions
            a = gtk.VBox(False, 1)
            fcntb = gtk.ToggleButton()
            fcntb.set_active(True)
            handler = fcntb.connect('toggled', self._on_toggle)
            fcntb.handler = handler
            l = gtk.Label('Functions')
            l.set_angle(90)
            a.pack_start(l, False, False, 1)
            a.pack_start(self.fcn_pix, False, False, 1)
            fcntb.add(a)
    
            # Sections
            sectb = gtk.ToggleButton()
            handler = sectb.connect('toggled', self._on_toggle)
            sectb.handler = handler
            a = gtk.VBox(False, 1)
            l = gtk.Label('Sections')
            l.set_angle(90)
            a.pack_start(l, False, False, 1)
            a.pack_start(self.bb_pix, False, False, 1)
            sectb.add(a)
    
            self.pack_start(fcntb, False, False, 0)
            self.pack_start(sectb, False, False, 0)

            if option == 'full_bin':
                # Imports
                imptb = gtk.ToggleButton()
                handler = imptb.connect('toggled', self._on_toggle)
                imptb.handler = handler
                a = gtk.VBox(False, 1)
                l = gtk.Label('Imports')
                l.set_angle(90)
                a.pack_start(l, False, False, 1)
                a.pack_start(self.imp_pix, False, False, 1)
                imptb.add(a)
        
                # Exports
                exptb = gtk.ToggleButton()
                handler = exptb.connect('toggled', self._on_toggle)
                exptb.handler = handler
                a = gtk.VBox(False, 1)
                l = gtk.Label('Exports')
                l.set_angle(90)
                a.pack_start(l, False, False, 1)
                a.pack_start(self.exp_pix, False, False, 1)
                exptb.add(a)
        
                self.pack_start(imptb, False, False, 0)
                self.pack_start(exptb, False, False, 0)
        elif option == 'pdf':
            # PDF
            pdftb = gtk.ToggleButton()
            pdftb.set_inconsistent(True)
            a = gtk.VBox(False, 1)
            l = gtk.Label('PDF info')
            l.set_angle(90)
            a.pack_start(l, False, False, 1)
            a.pack_start(self.exp_pix, False, False, 1)
            pdftb.add(a)
        
            self.pack_start(pdftb, False, False, 0)
        elif option == 'url':
            # URL
            lnktb = gtk.ToggleButton()
            lnktb.set_active(True)
            handler = lnktb.connect('toggled', self._on_toggle)
            lnktb.handler = handler
            a = gtk.VBox(False, 1)
            l = gtk.Label('URL')
            l.set_angle(90)
            a.pack_start(l, False, False, 1)
            a.pack_start(self.fcn_pix, False, False, 1)
            lnktb.add(a)
        
            hdrtb = gtk.ToggleButton()
            handler = hdrtb.connect('toggled', self._on_toggle)
            hdrtb.handler = handler
            a = gtk.VBox(False, 1)
            l = gtk.Label('Headers')
            l.set_angle(90)
            a.pack_start(l, False, False, 1)
            a.pack_start(self.exp_pix, False, False, 1)
            hdrtb.add(a)
        
            ccktb = gtk.ToggleButton()
            handler = ccktb.connect('toggled', self._on_toggle)
            ccktb.handler = handler
            a = gtk.VBox(False, 1)
            l = gtk.Label('Cookies')
            l.set_angle(90)
            a.pack_start(l, False, False, 1)
            a.pack_start(self.imp_pix, False, False, 1)
            ccktb.add(a)
        
            self.pack_start(lnktb, False, False, 0)
            self.pack_start(hdrtb, False, False, 0)
            self.pack_start(ccktb, False, False, 0)

        self.show_all()

    def _on_toggle(self, widget):
        for x in self:
            if x != self.hide_tb and x != widget:
                x.handler_block(x.handler)
                x.set_active(False)
                x.handler_unblock(x.handler)
            elif x == widget:
                if x.get_active() == True:
                    x.handler_block(x.handler)
                    x.set_active(True)
                    x.handler_unblock(x.handler)
                    option = x.get_children()[0].get_children()[0].get_text()
                    self.main.tviews.create_model(option)
                    self.main.tviews.left_scrolled_window.show()
                else:
                    x.handler_block(x.handler)
                    x.set_active(False)
                    x.handler_unblock(x.handler)
                    self.main.tviews.left_scrolled_window.hide()

    def _hide_tb_toggled(self, widget):
        if widget.get_active():
            self.main.topbuttons.hide()
            self.main.mbar.hide()
            i = gtk.Image()
            i.set_from_stock(gtk.STOCK_GO_DOWN, gtk.ICON_SIZE_MENU)
            widget.set_image(i)
        else:
            self.main.topbuttons.show()
            self.main.mbar.show()
            i = gtk.Image()
            i.set_from_stock(gtk.STOCK_GO_UP, gtk.ICON_SIZE_MENU)
            widget.set_image(i)

    def remove_all(self):
        for child in self.get_children():
            self.remove(child)
