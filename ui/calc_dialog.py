##      calc_dialog.py
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

import gtk

class CalcDialog(gtk.Dialog):
    '''Window popup to select files'''

    def __init__(self, core):
        super(CalcDialog,self).__init__('Calculator', None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))

        self.uicore = core

        # the cancel button
        self.butt_ok = self.action_area.get_children()[0]
        self.butt_ok.connect("clicked", lambda x: self.destroy())

        # Window position
        self.set_position(gtk.WIN_POS_CENTER)

        # Main Vertical Box
        self.main_vbox = gtk.VBox(False, 2)
        self.main_vbox.set_border_width(7)

        self.label = gtk.Label('Enter expression to calculate:')

        # File selection Horizontal Box 1
        self.hbox1 = gtk.HBox(False, 0)
        # TextEntry
        self.input_entry = gtk.Entry(100)
        self.input_entry.set_icon_from_stock(1, gtk.STOCK_INFO)
        self.input_entry.set_icon_tooltip_text(1, 'Enter expression')
        self.input_entry.connect("activate", self._do_calc)
        self.input_entry.connect("icon-press", self._do_calc)
        #self.input_entry.set_sensitive(False)
        # Pack elements into hbox
        self.hbox1.pack_start(self.input_entry, True, True, 2)

        # File selection Horizontal Box 2
        self.hbox2 = gtk.HBox(False, 0)
        # TextEntry
        self.input_entry2 = gtk.Entry(100)
        # Select file button
        # Pack elements into hbox
        self.hbox2.pack_start(self.input_entry2, True, True, 2)

        # Pack elements into main_vbox
        self.main_vbox.pack_start(self.label, False, False, 2)
        self.main_vbox.pack_start(self.hbox1, False, False, 2)
        self.main_vbox.pack_start(self.hbox2, False, False, 2)

        self.vbox.pack_start(self.main_vbox)
        self.show_all()

    def _do_calc(self, widget, icon_pos=None, event=None):
        res = self.uicore.core.num.math(self.input_entry.get_text())
        self.input_entry2.set_text(str(res))
