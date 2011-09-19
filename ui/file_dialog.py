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

import os
import gtk

class FileDialog(gtk.Dialog):
    '''Window popup to select file'''

    def __init__(self, has_pyew, has_radare, core='', file=''):
        super(FileDialog,self).__init__('Select file', None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT, gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))


        self.has_pyew = has_pyew
        self.has_radare = has_radare

        self.core = core
        self.file = file

        # the cancel button
        self.butt_ok = self.action_area.get_children()[0]
        self.butt_ok.connect("clicked", self.get_file)
        self.butt_cancel = self.action_area.get_children()[1]
        self.butt_cancel.connect("clicked", self.cancel)

        # Window position
        self.set_position(gtk.WIN_POS_CENTER)

        # Main Vertical Box
        self.main_vbox = gtk.VBox(False, 2)
        self.main_vbox.set_border_width(7)

        # Logo
        self.logo = gtk.Image()
        self.logo.set_from_file('ui/data/logo.png')
        # logo label
        self.logo_text = gtk.Label()
        self.logo_text.set_markup('<span size=\'12000\'>Welcome to <b>Bokken 1.5-dev</b></span>')

        # Logo label
        self.label = gtk.Label('Select a file or enter the path manually.\nValid inputs are: PE/Elf, PDF, plain text files and URLs')
        self.label.set_alignment(0, 0.5)
        # Horizontal Separator
        self.hseparator1 = gtk.HSeparator()

        # Core selection label and combo
        self.core_label = gtk.Label('Select backend to use: ')
        self.core_label.set_alignment(0, 0.5)
        self.core_combo = gtk.combo_box_new_text()

        if self.has_pyew:
            self.core_combo.append_text('Pyew')
        if self.has_radare:
            self.core_combo.append_text('Radare')

        if not self.core:
            self.core_combo.set_active(0)
        elif self.has_radare != self.has_pyew:
            self.core_combo.set_active(0)
        elif self.core == 'pyew':
            self.core_combo.set_active(0)
        elif self.core == 'radare':
            self.core_combo.set_active(1)
        self.core = self.core_combo.get_active_text().lower()

        # Core combo Horizontal Box
        self.core_hbox = gtk.HBox(False, 0)
        self.core_hbox.pack_start(self.core_label, True, True, 2)
        self.core_hbox.pack_start(self.core_combo, False, False, 2)
        # Horizontal Separator
        self.hseparator2 = gtk.HSeparator()

        # File selection Horizontal Box
        self.hbox = gtk.HBox(False, 0)
        # TextEntry
        self.model = gtk.ListStore(str)
        self.input_entry = gtk.ComboBoxEntry(self.model, column=0)
        #self.input_entry = gtk.Entry(100)
        if self.file:
            self.input_entry.get_child().set_text(self.file)
        # Recent file manager
        self.manager = gtk.recent_manager_get_default()
        items = self.manager.get_items()
        for element in items[:10]:
            self.model.append( [element.get_display_name()])
        # Select file button
        icon = gtk.Image()
        icon.set_from_stock(gtk.STOCK_OPEN, gtk.ICON_SIZE_MENU)
        self.select_button = gtk.Button()
        self.select_button.set_image(icon)
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

        # HSeparator
        self.hseparator3 = gtk.HSeparator()
        # Analysis options label
        self.anal_label = gtk.Label()
        self.anal_label.set_markup("<b>Analysis options:</b>")

        # Pyew options
        self.deep_anal = gtk.CheckButton(label='Deep analysis')
        self.case_dasm = gtk.CheckButton(label='Lower case disassembly')
        self.case_dasm.set_active(True)
        self.pyew_box.pack_start(self.deep_anal, False, False, 2)
        self.pyew_box.pack_start(self.case_dasm, False, False, 2)
        # It's here to avoid errors during start up
        self.core_combo.connect("changed", self._on_change)

        # Radare options
        self.anal_bin = gtk.CheckButton(label='Analyze program')
        self.anal_bin.set_active(True)
        self.radare_dasm = gtk.CheckButton(label='Lower case disassembly')
        self.radare_dasm.set_active(True)
        self.radare_box.pack_start(self.anal_bin, False, False, 2)
        self.radare_box.pack_start(self.radare_dasm, False, False, 2)

        # Pack elements into main_vbox
        self.main_vbox.pack_start(self.logo, False, False, 0)
        self.main_vbox.pack_start(self.logo_text, False, False, 0)
        self.main_vbox.pack_start(self.hseparator1, False, False, 2)
        self.main_vbox.pack_start(self.core_hbox, False, False, 2)
        self.main_vbox.pack_start(self.hseparator2, False, False, 2)
        self.main_vbox.pack_start(self.label, False, False, 2)
        self.main_vbox.pack_start(self.hbox, False, False, 2)
        self.main_vbox.pack_start(self.hseparator3, False, False, 2)
        self.main_vbox.pack_start(self.anal_label, False, False, 2)
        self.main_vbox.pack_start(self.options_hbox, False, False, 2)

        self.vbox.pack_start(self.main_vbox)
        self.show_all()
        if self.core == 'pyew':
            self.radare_box.set_visible(False)
        elif self.core == 'radare':
            self.pyew_box.set_visible(False)
        else:
            self.radare_box.set_visible(False)

    def cancel(self, widget):
        import sys
        sys.exit(1)
        self.destroy()

    def get_file(self, widget):
        self.file = self.input_entry.get_child().get_text()
        self.manager.add_item('file://' + os.getcwd() + os.sep + self.file)
        self.get_backend()
        self.get_options()
        self.destroy()

    def get_backend(self):
        self.backend = self.core_combo.get_active_text().lower()

    def get_options(self):
        active = self.core_combo.get_active_text()
        if active == 'Pyew':
            self.deep = self.deep_anal.get_active()
            self.case = self.case_dasm.get_active()
        if active == 'Radare':
            self.analyze_bin = self.anal_bin.get_active()
            self.radare_lower = self.radare_dasm.get_active()

    def select_file(self, widget):
        chooser = gtk.FileChooserDialog(title=None,action=gtk.FILE_CHOOSER_ACTION_OPEN,
                              buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
        self.response = chooser.run()
        if self.response == gtk.RESPONSE_OK:
            self.file_name = chooser.get_filename()
            self.input_entry.get_child().set_text(self.file_name)
        chooser.destroy()

    def _on_change(self, widget):
        active = widget.get_active_text()
        if active == 'Pyew':
            self.pyew_box.set_visible(True)
            self.radare_box.set_visible(False)
        elif active == 'Radare':
            self.pyew_box.set_visible(False)
            self.radare_box.set_visible(True)
