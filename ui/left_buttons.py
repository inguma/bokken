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

from gi.repository import Gtk
from lib.common import datafile_path

class LeftButtons(Gtk.VBox):
    '''Left buttons for Treeview change'''

    def __init__(self, main):
        super(LeftButtons,self).__init__(False, 1)

        self.main = main
        self.prev_size = ()

        #################################################################
        # Left mini-toolbar
        #################################################################
        toolbar = Gtk.Toolbar()
        toolbar.set_style(Gtk.ToolbarStyle.ICONS)

    ##################################
    # Methods

    def create_buttons(self, option):
        # Icons
        self.fcn_pix = Gtk.Image()
        self.fcn_pix.set_from_file(datafile_path('function.png'))
        self.bb_pix = Gtk.Image()
        self.bb_pix.set_from_file(datafile_path('block.png'))
        self.imp_pix = Gtk.Image()
        self.imp_pix.set_from_file(datafile_path('import.png'))
        self.exp_pix = Gtk.Image()
        self.exp_pix.set_from_file(datafile_path('export.png'))

        # Show/hide toolbar and menu
        self.hide_tb = Gtk.ToggleButton()
        i = Gtk.Image()
        i.set_from_stock(Gtk.STOCK_GO_UP, Gtk.IconSize.MENU)
        self.hide_tb.set_image(i)
        self.hide_tb.set_tooltip_text('Toggle visibility of the top toolbar')
        handler = self.hide_tb.connect('toggled', self._hide_tb_toggled)
        self.hide_tb.handler = handler

        self.pack_start(self.hide_tb, False, False, 0)

        if 'bin' in option:
            # Functions
            a = Gtk.VBox(False, 1)
            fcntb = Gtk.ToggleButton()
            fcntb.set_active(True)
            fcntb.set_tooltip_text('List of function entrypoints in the binary')
            handler = fcntb.connect('toggled', self._on_toggle)
            fcntb.handler = handler
            l = Gtk.Label(label='Functions')
            l.set_angle(90)
            a.pack_start(l, False, False, 1)
            a.pack_start(self.fcn_pix, False, False, 1)
            fcntb.add(a)

            self.pack_start(fcntb, False, False, 0)

            if option == 'full_bin':
                # Imports
                imptb = Gtk.ToggleButton()
                imptb.set_tooltip_text('List of imported symbols')
                handler = imptb.connect('toggled', self._on_toggle)
                imptb.handler = handler
                a = Gtk.VBox(False, 1)
                l = Gtk.Label(label='Imports')
                l.set_angle(90)
                a.pack_start(l, False, False, 1)
                a.pack_start(self.imp_pix, False, False, 1)
                imptb.add(a)

                # Symbols
                exptb = Gtk.ToggleButton()
                exptb.set_tooltip_text('List of exported symbols')
                handler = exptb.connect('toggled', self._on_toggle)
                exptb.handler = handler
                a = Gtk.VBox(False, 1)
                l = Gtk.Label(label='Symbols')
                l.set_angle(90)
                a.pack_start(l, False, False, 1)
                a.pack_start(self.exp_pix, False, False, 1)
                exptb.add(a)

                # Relocs
                sectb = Gtk.ToggleButton()
                sectb.set_tooltip_text('List of relocs in the binary')
                handler = sectb.connect('toggled', self._on_toggle)
                sectb.handler = handler
                a = Gtk.VBox(False, 1)
                l = Gtk.Label(label='Relocs')
                l.set_angle(90)
                a.pack_start(l, False, False, 1)
                a.pack_start(self.bb_pix, False, False, 1)
                sectb.add(a)

                self.pack_start(imptb, False, False, 0)
                self.pack_start(exptb, False, False, 0)
                self.pack_start(sectb, False, False, 0)

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
            self.main.topbuttons.main_tb.hide()
            i = Gtk.Image()
            i.set_from_stock(Gtk.STOCK_GO_DOWN, Gtk.IconSize.MENU)
            widget.set_image(i)
        else:
            self.main.topbuttons.main_tb.show()
            i = Gtk.Image()
            i.set_from_stock(Gtk.STOCK_GO_UP, Gtk.IconSize.MENU)
            widget.set_image(i)

    def remove_all(self):
        for child in self.get_children():
            self.remove(child)
