##      file_dialog.py
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

class FileDialog(gtk.Dialog):
    '''Window popup to select file'''

    def __init__(self):
        super(FileDialog,self).__init__('Select file', None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, (gtk.STOCK_OK,gtk.RESPONSE_ACCEPT, gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT))

        # the cancel button
        self.butt_ok = self.action_area.get_children()[1]
        self.butt_ok.connect("clicked", self.get_file)
        self.butt_cancel = self.action_area.get_children()[0]
        self.butt_cancel.connect("clicked", lambda x: self.destroy())

        # Positions
#        self.resize(200, 200)
        self.set_position(gtk.WIN_POS_CENTER)

        # Table to contain elements
        self.table = gtk.Table(3, 2, False)
        # Label
        self.label = gtk.Label('\nSelect a file or enter the path manually.\nValid inputs are: PE/Elf, PDF, plain text files and URLs\n')
        # Horizontal Separator
        self.hseparator = gtk.HSeparator()
        # TextEntry
        self.input_entry = gtk.Entry(100)
        # Select file button
        self.select_button = gtk.Button(label=None, stock=gtk.STOCK_OPEN)
        self.select_button.connect("clicked", self.select_file)

        # Add elements to the table
        self.table.attach(self.label, 0, 2, 0, 1)
        self.table.attach(self.hseparator, 0, 2, 1, 2)
        self.table.attach(self.input_entry, 0, 1, 2, 3)
        self.table.attach(self.select_button, 1, 2, 2, 3)


        self.vbox.pack_start(self.table)
        self.show_all()

    def get_file(self, widget):
        self.file = self.input_entry.get_text()
        self.destroy()

    def select_file(self, widget):
        chooser = gtk.FileChooserDialog(title=None,action=gtk.FILE_CHOOSER_ACTION_OPEN,
                              buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
        self.response = chooser.run()
        if self.response == gtk.RESPONSE_OK:
            self.file_name = chooser.get_filename()
        chooser.destroy()
        self.input_entry.set_text(self.file_name)
