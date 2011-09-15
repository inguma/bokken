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

    def __init__(self, core='', file=''):
        super(FileDialog,self).__init__('Select file', None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, (gtk.STOCK_OK,gtk.RESPONSE_ACCEPT, gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT))

        self.core = core
        self.file = file

        # the cancel button
        self.butt_ok = self.action_area.get_children()[1]
        self.butt_ok.connect("clicked", self.get_file)
        self.butt_cancel = self.action_area.get_children()[0]
        self.butt_cancel.connect("clicked", lambda x: self.destroy())

        # Window position
        self.set_position(gtk.WIN_POS_CENTER)

        # Main Vertical Box
        self.main_vbox = gtk.VBox(False, 2)

        # Logo
        self.logo = gtk.Image()
        self.logo.set_from_file('ui/data/logo.png')
        # logo label
        self.logo_text = gtk.Label()
        self.logo_text.set_markup('<span size=\'12000\'>Welcome to <b>Bokken 0.5</b></span>')

        # Logo label
        self.label = gtk.Label('Select a file or enter the path manually.\nValid inputs are: PE/Elf, PDF, plain text files and URLs')
        self.label.set_alignment(0, 0.5)
        # Horizontal Separator
        self.hseparator1 = gtk.HSeparator()

        # Core selection label and combo
        self.core_label = gtk.Label('Select backend to use: ')
        self.core_label.set_alignment(0, 0.5)
        self.core_combo = gtk.combo_box_new_text()
        self.core_combo.append_text('Pyew')
        self.core_combo.append_text('Radare')
        self.core_combo.connect("changed", self._on_change)
        if not self.core:
            self.core_combo.set_active(0)
        elif self.core == 'p':
            self.core_combo.set_active(0)
        elif self.core == 'r':
            self.core_combo.set_active(1)

        # Core combo Horizontal Box
        self.core_hbox = gtk.HBox(False, 0)
        self.core_hbox.pack_start(self.core_label, True, True, 2)
        self.core_hbox.pack_start(self.core_combo, False, False, 2)
        # Horizontal Separator
        self.hseparator2 = gtk.HSeparator()

        # File selection Horizontal Box
        self.hbox = gtk.HBox(False, 0)
        # TextEntry
        self.input_entry = gtk.Entry(100)
        if self.file:
            self.input_entry.set_text(self.file)
        # Select file button
        self.select_button = gtk.Button(label=None, stock=gtk.STOCK_OPEN)
        self.select_button.connect("clicked", self.select_file)
        # Pack elements into hbox
        self.hbox.pack_start(self.input_entry, True, True, 2)
        self.hbox.pack_start(self.select_button, False, False, 2)

        # File options Horizontal Box
        self.options_hbox = gtk.HBox(False, 2)
        # Pyew option Vertical Box
        self.pyew_box = gtk.VBox(False, 0)
        # Radare option Vertical Box
        self.radare_box = gtk.VBox(False, 0)
        # pack the boxes
        self.options_hbox.pack_start(self.pyew_box, False, False, 0)
        self.options_hbox.pack_start(self.radare_box, False, False, 0)

        # Pyew options
        self.deep_anal = gtk.CheckButton(label='Deep analysis')
        self.case_dasm = gtk.CheckButton(label='Lower case disassembly')
        self.pyew_box.pack_start(self.deep_anal, False, False, 2)
        self.pyew_box.pack_start(self.case_dasm, False, False, 2)

        # Radare options
        self.anal_bin = gtk.CheckButton(label='Analyze binary')
        self.radare_box.pack_start(self.anal_bin, False, False, 2)

        # Pack elements into main_vbox
        self.main_vbox.pack_start(self.logo, False, False, 0)
        self.main_vbox.pack_start(self.logo_text, False, False, 0)
        self.main_vbox.pack_start(self.hseparator1, False, False, 2)
        self.main_vbox.pack_start(self.core_hbox, False, False, 2)
        self.main_vbox.pack_start(self.hseparator2, False, False, 2)
        self.main_vbox.pack_start(self.label, False, False, 2)
        self.main_vbox.pack_start(self.hbox, False, False, 2)
        self.main_vbox.pack_start(self.options_hbox, False, False, 2)

        self.vbox.pack_start(self.main_vbox)
        self.show_all()
        self.radare_box.set_visible(False)

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

    def _on_change(self, widget):
        active = widget.get_active()
        if active == 0:
            self.pyew_box.set_visible(True)
            self.radare_box.set_visible(False)
        elif active == 1:
            self.pyew_box.set_visible(False)
            self.radare_box.set_visible(True)
