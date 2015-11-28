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

from gi.repository import Gtk
import ui.gtk2.common

class CalcDialog(Gtk.Dialog):
    '''Window popup to select files'''

    def __init__(self, core):
        super(CalcDialog,self).__init__('Calculator', None, Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT, (Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT))

        self.uicore = core

        # Set dialog resizeable and auto-shrink
        # MEOW
        #self.set_policy(False, False, True)
        ui.gtk2.common.set_bokken_icon(self)

        self.examples = "Examples:\n0x100\n0x100 + 20\n01001\n01001 + 0x10\n0x10 + 20 * 0101"

        # the cancel button
        self.butt_ok = self.action_area.get_children()[0]
        self.butt_ok.connect("clicked", lambda x: self.destroy())

        # Window position
        self.set_position(Gtk.WindowPosition.CENTER)

        # Main Vertical Box
        self.main_vbox = Gtk.VBox(False, 2)
        self.main_vbox.set_border_width(7)

        self.label = Gtk.Label(label='Enter expression to calculate:')

        # File selection Horizontal Box 1
        self.hbox1 = Gtk.HBox(False, 0)
        # TextEntry
        self.input_entry = Gtk.Entry()
        self.input_entry.set_max_length(100)
        self.input_entry.set_icon_from_stock(1, Gtk.STOCK_INFO)
        self.input_entry.set_icon_tooltip_text(1, self.examples)
        self.input_entry.connect("activate", self._do_calc)
        self.input_entry.connect("icon-press", self._do_calc)
        #self.input_entry.set_sensitive(False)
        # Pack elements into hbox
        self.hbox1.pack_start(self.input_entry, True, True, 2)

        # File selection Horizontal Box 2
        self.hbox2 = Gtk.HBox(False, 0)
        # TextEntry
        self.input_entry2 = Gtk.Entry()
        self.input_entry2.set_max_length(100)
        # Select file button
        # Pack elements into hbox
        self.hbox2.pack_start(self.input_entry2, True, True, 2)

        # Base conversion labels
        self.out_box = Gtk.VBox(False, 1)
        self.hex_lbl = Gtk.Label()
        self.hex_lbl.set_alignment(0, 0.5)
        self.dec_lbl = Gtk.Label()
        self.dec_lbl.set_alignment(0, 0.5)
        self.oct_lbl = Gtk.Label()
        self.oct_lbl.set_alignment(0, 0.5)
        self.bin_lbl = Gtk.Label()
        self.bin_lbl.set_alignment(0, 0.5)
        self.chr_lbl = Gtk.Label()
        self.chr_lbl.set_alignment(0, 0.5)

        self.out_box.pack_start(self.hex_lbl, False, False, 1)
        self.out_box.pack_start(self.dec_lbl, False, False, 1)
        self.out_box.pack_start(self.oct_lbl, False, False, 1)
        self.out_box.pack_start(self.bin_lbl, False, False, 1)
        self.out_box.pack_start(self.chr_lbl, False, False, 1)

        # Pack elements into main_vbox
        self.main_vbox.pack_start(self.label, False, False, 2)
        self.main_vbox.pack_start(self.hbox1, False, False, 2)
        self.main_vbox.pack_start(self.hbox2, False, False, 2)
        self.main_vbox.pack_start(self.out_box, False, False, 2)

        self.vbox.pack_start(self.main_vbox, True, True, 0)
        self.show_all()
        self.out_box.hide()

    def _do_calc(self, widget, icon_pos=None, event=None):
        res = self.uicore.core.num.math(self.input_entry.get_text())
        if res:
            self.input_entry2.set_text(str(res))
    
            self.hex_lbl.set_markup( "<b>Hexadecimal:</b>\t" + hex(res) )
            self.dec_lbl.set_markup( "<b>Decimal</b>:\t\t" + str(int(str(res), 10)) )
            self.oct_lbl.set_markup( "<b>Octal:</b>\t\t" + str(oct(res)) )
            self.bin_lbl.set_markup( "<b>Binary:</b>\t\t" + bin(res)[2:] )
            try:
                self.chr_lbl.set_markup( "<b>Character:</b>\t" + chr(res))
            except:
                self.chr_lbl.set_markup( "<b>Character:</b>\t")
            self.out_box.show_all()
        else:
            self.input_entry2.set_text('')
            self.out_box.hide_all()
