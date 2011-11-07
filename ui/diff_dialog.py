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

import os
import gtk

class DiffDialog(gtk.Dialog):
    '''Window popup to select files'''

    def __init__(self, core):
        super(DiffDialog,self).__init__('Select file', None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT, gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))

        self.core = core
        self.file = self.core.filename

        # Set dialog resizeable and auto-shrink
        self.set_policy(False, False, True)
        self.set_icon_from_file(os.path.dirname(__file__)+os.sep+'data'+os.sep+'bokken.svg')

        # the cancel button
        self.butt_ok = self.action_area.get_children()[0]
        self.butt_ok.connect("clicked", self.select_file)

        # Window position
        self.set_position(gtk.WIN_POS_CENTER)

        # Main Vertical Box
        self.main_vbox = gtk.VBox(False, 2)
        self.main_vbox.set_border_width(7)

        self.label = gtk.Label('Select the file to diff against:')

        # File selection Horizontal Box 1
        self.hbox1 = gtk.HBox(False, 0)
        # TextEntry
        self.input_entry = gtk.Entry(100)
        #self.input_entry.get_child().connect("activate", self.fast_start)
        self.input_entry.set_text(self.file)
        self.input_entry.set_sensitive(False)
        # Pack elements into hbox
        self.hbox1.pack_start(self.input_entry, True, True, 2)

        # File selection Horizontal Box 2
        self.hbox2 = gtk.HBox(False, 0)
        # TextEntry
        self.input_entry2 = gtk.Entry(100)
        # Select file button
        self.input_entry2.set_icon_from_stock(1, gtk.STOCK_OPEN)
        self.input_entry2.set_icon_tooltip_text(1, 'Select file')
        self.input_entry2.connect("activate", self.select_file)
        self.input_entry2.connect("icon-press", self.select_file)
        # Pack elements into hbox
        self.hbox2.pack_start(self.input_entry2, True, True, 2)

        #########################################################
        # Options elements
        self.options_box = gtk.VBox(False, 2)

        self.sep = gtk.HSeparator()
        self.options_exp = gtk.Expander("Binary diffing options:")

        # HScale for function matching threshold
        self.thresh_label = gtk.Label("Function matching threshold:")
        self.thresh_label.set_alignment(0, 0.5)
        self.scale = gtk.HScale()
        self.scale.set_range(0, 100)
        self.scale.set_increments(1, 10)
        self.scale.set_digits(0)
        self.scale.set_value_pos(gtk.POS_RIGHT)
        self.scale.set_value(70)
        self.scale.add_mark(0, gtk.POS_BOTTOM, "0")
        self.scale.add_mark(50, gtk.POS_BOTTOM, "50")
        self.scale.add_mark(100, gtk.POS_BOTTOM, "100")

        # HScale for basic block matching threshold
        self.bb_thresh_label = gtk.Label("Basic block matching threshold:")
        self.bb_thresh_label.set_alignment(0, 0.5)
        self.bb_scale = gtk.HScale()
        self.bb_scale.set_range(0, 100)
        self.bb_scale.set_increments(1, 10)
        self.bb_scale.set_digits(0)
        self.bb_scale.set_value_pos(gtk.POS_RIGHT)
        self.bb_scale.set_value(70)
        self.bb_scale.add_mark(0, gtk.POS_BOTTOM, "0")
        self.bb_scale.add_mark(50, gtk.POS_BOTTOM, "50")
        self.bb_scale.add_mark(100, gtk.POS_BOTTOM, "100")

        self.bytes_check = gtk.CheckButton("Do code diffing with all bytes", use_underline=True)

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

        self.vbox.pack_start(self.main_vbox)
        self.show_all()

    def get_file(self, widget):
        self.hide()
        self.file = self.input_entry2.get_text()

    def select_file(self, widget, icon_pos='', event=''):
        if self.input_entry2.get_text():
            self.get_file(self.input_entry2)
            self.response(0)
        else:
            chooser = gtk.FileChooserDialog(title=None,action=gtk.FILE_CHOOSER_ACTION_OPEN,
                      buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
            self.response = chooser.run()
            if self.response == gtk.RESPONSE_DELETE_EVENT or self.response == gtk.RESPONSE_REJECT or self.response == gtk.RESPONSE_CANCEL:
                chooser.destroy()
            else:
                self.file_name = chooser.get_filename()
                self.input_entry2.set_text(self.file_name)
                chooser.destroy()
