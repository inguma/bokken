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

import gtk

class DiffDialog(gtk.Dialog):
    '''Window popup to select files'''

    def __init__(self, core):
        super(DiffDialog,self).__init__('Select file', None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT, gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))

        self.core = core
        self.file = self.core.filename

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

        # Pack elements into main_vbox
        self.main_vbox.pack_start(self.label, False, False, 2)
        self.main_vbox.pack_start(self.hbox1, False, False, 2)
        self.main_vbox.pack_start(self.hbox2, False, False, 2)

        self.vbox.pack_start(self.main_vbox)
        self.show_all()

    def get_file(self, widget):
        self.hide()
        self.file = self.input_entry2.get_text()

    def select_file(self, widget, icon_pos='', event=''):
        if self.input_entry2.get_text():
            self.get_file(self.input_entry2)
        else:
            chooser = gtk.FileChooserDialog(title=None,action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                  buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
            self.response = chooser.run()
            if self.response == gtk.RESPONSE_OK:
                self.file_name = chooser.get_filename()
                self.input_entry2.set_text(self.file_name)
            chooser.destroy()
