##      diff_dialog.py
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

class DiffDialog(Gtk.Dialog):
    '''Window popup to select files'''

    def __init__(self, core):
        super(DiffDialog,self).__init__('Select file', None, Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT, (Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT, Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT))

        self.core = core
        self.file = self.core.filename

        # Set dialog resizeable and auto-shrink
        # MEOW
        #self.set_policy(False, False, True)
        ui.gtk2.common.set_bokken_icon(self)

        # the cancel button
        self.butt_ok = self.action_area.get_children()[1]
        self.butt_ok.connect("clicked", self.select_file)

        # Window position
        self.set_position(Gtk.WindowPosition.CENTER)

        # Main Vertical Box
        self.main_vbox = Gtk.VBox(False, 2)
        self.main_vbox.set_border_width(7)

        self.label = Gtk.Label(label='Select the file to diff against:')

        # File selection Horizontal Box 1
        self.hbox1 = Gtk.HBox(False, 0)
        # TextEntry
        self.input_entry = Gtk.Entry()
        self.input_entry.set_max_length(100)
        #self.input_entry.get_child().connect("activate", self.fast_start)
        self.input_entry.set_text(self.file)
        self.input_entry.set_sensitive(False)
        # Pack elements into hbox
        self.hbox1.pack_start(self.input_entry, True, True, 2)

        # File selection Horizontal Box 2
        self.hbox2 = Gtk.HBox(False, 0)
        # TextEntry
        self.input_entry2 = Gtk.Entry()
        self.input_entry2.set_max_length(100)
        # Select file button
        self.input_entry2.set_icon_from_stock(1, Gtk.STOCK_OPEN)
        self.input_entry2.set_icon_tooltip_text(1, 'Select file')
        self.input_entry2.connect("activate", self.select_file)
        self.input_entry2.connect("icon-press", self.select_file)
        # Pack elements into hbox
        self.hbox2.pack_start(self.input_entry2, True, True, 2)

        #########################################################
        # Options elements
        self.options_box = Gtk.VBox(False, 2)

        self.sep = Gtk.HSeparator()
        self.options_exp = Gtk.Expander.new("Binary diffing options:")

        # HScale for function matching threshold
        self.thresh_label = Gtk.Label(label="Function matching threshold:")
        self.thresh_label.set_alignment(0, 0.5)
        self.scale = Gtk.HScale()
        self.scale.set_range(0, 100)
        self.scale.set_increments(1, 10)
        self.scale.set_digits(0)
        self.scale.set_value_pos(Gtk.PositionType.RIGHT)
        self.scale.set_value(70)
        self.scale.add_mark(0, Gtk.PositionType.BOTTOM, "0")
        self.scale.add_mark(50, Gtk.PositionType.BOTTOM, "50")
        self.scale.add_mark(100, Gtk.PositionType.BOTTOM, "100")

        # HScale for basic block matching threshold
        self.bb_thresh_label = Gtk.Label(label="Basic block matching threshold:")
        self.bb_thresh_label.set_alignment(0, 0.5)
        self.bb_scale = Gtk.HScale()
        self.bb_scale.set_range(0, 100)
        self.bb_scale.set_increments(1, 10)
        self.bb_scale.set_digits(0)
        self.bb_scale.set_value_pos(Gtk.PositionType.RIGHT)
        self.bb_scale.set_value(70)
        self.bb_scale.add_mark(0, Gtk.PositionType.BOTTOM, "0")
        self.bb_scale.add_mark(50, Gtk.PositionType.BOTTOM, "50")
        self.bb_scale.add_mark(100, Gtk.PositionType.BOTTOM, "100")

        self.bytes_check = Gtk.CheckButton("Do code diffing with all bytes", use_underline=True)

        self.options_box.pack_start(self.thresh_label, False, False, 1)
        self.options_box.pack_start(self.scale, False, False, 1)
        self.options_box.pack_start(self.bb_thresh_label, False, False, 1)
        self.options_box.pack_start(self.bb_scale, False, False, 1)
        self.options_box.pack_start(self.bytes_check, False, False, 1)

        self.options_exp.add(self.options_box)

        # Pack elements into main_vbox
        self.main_vbox.pack_start(self.label, False, False, 2)
        self.main_vbox.pack_start(self.hbox1, False, False, 2)
        self.main_vbox.pack_start(self.hbox2, False, False, 2)
        self.main_vbox.pack_start(self.sep, False, False, 2)
        self.main_vbox.pack_start(self.options_exp, False, False, 2)

        self.vbox.pack_start(self.main_vbox, True, True, 0)
        self.show_all()

    def get_file(self, widget):
        self.hide()
        self.file = self.input_entry2.get_text()

    def select_file(self, widget, icon_pos='', event=''):
        if self.input_entry2.get_text():
            self.get_file(self.input_entry2)
            self.response(0)
        else:
            chooser = Gtk.FileChooserDialog(title=None,action=Gtk.FileChooserAction.OPEN,
                      buttons=(Gtk.STOCK_CANCEL,Gtk.ResponseType.CANCEL,Gtk.STOCK_OPEN,Gtk.ResponseType.OK))
            self.resp = chooser.run()
            if self.resp == Gtk.ResponseType.DELETE_EVENT or self.resp == Gtk.ResponseType.REJECT or self.resp == Gtk.ResponseType.CANCEL:
                chooser.destroy()
            else:
                self.file_name = chooser.get_filename()
                self.input_entry2.set_text(self.file_name)
                chooser.destroy()
