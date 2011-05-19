#!/usr/bin/python

#       rightcombo.py
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

class RightCombo(gtk.Table):
    '''Main TextiView elements'''

    def __init__(self, tviews, uicore):
        super(RightCombo,self).__init__(1, 7, False)

        self.tviews = tviews
        self.uicore = uicore

        # Theme Label
        self.theme_label = gtk.Label('Color theme:')
        self.attach(self.theme_label, 0, 1, 0, 1)

        # Theme ComboBox
        self.theme_combo = gtk.combo_box_new_text()
        options = ['Classic', 'Cobalt', 'kate', 'Oblivion', 'Tango']
        for option in options:
            self.theme_combo.append_text(option)
#        # Set first by default
#        self.theme_combo.set_active(0)

        self.theme_combo.connect("changed", self.theme_combo_change)
        self.attach(self.theme_combo, 1, 2, 0, 1)

        # Right Combo Label
        self.rc_label = gtk.Label('Data format:')
        self.attach(self.rc_label, 2, 3, 0, 1)

        # Right ComboBox
        self.right_combo = gtk.combo_box_new_text()
#        options = ['Disassembly', "Hexdump", "String Repr", "Strings", "Plain Text", 'URL']
#        for option in options:
#            self.right_combo.append_text(option)
#        # Set Disassembly by default
#        self.right_combo.set_active(0)
#        self.create_options()

        self.connect = self.right_combo.connect("changed", self.right_combo_change)
        self.attach(self.right_combo, 3, 4, 0, 1)

        #
        # Open File Stuff

        # Open file label
        self.open_label = gtk.Label('File to open:')
        self.attach(self.open_label, 4, 5, 0, 1)

        # Open file text entry
        self.open_entry = gtk.Entry(100)
        self.attach(self.open_entry, 5, 6, 0, 1)

        # Open file button
        self.open_button = gtk.Button()

        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_OPEN, gtk.ICON_SIZE_MENU)

#        self.open_button.connect("clicked", self.open_new_file)
        self.open_button.set_image(image)
        self.open_button.set_relief(gtk.RELIEF_NONE)
        self.open_button.set_sensitive(False)

        self.attach(self.open_button, 6, 7, 0, 1)

    def create_options(self):
        self.right_combo.disconnect(self.connect)
        self.right_combo.get_model().clear()
        main_options = ["Hexdump", "String Repr", "Strings"]
        if self.uicore.pyew.format in ['PE', 'Elf']:
            self.right_combo.append_text('Disassembly')
            # Set Disassembly by default
            self.right_combo.set_active(0)
        for option in main_options:
            self.right_combo.append_text(option)
        if self.uicore.pyew.format == 'URL':
            self.right_combo.append_text('URL')
            # Set URL by default
            self.right_combo.set_active(3)
        elif self.uicore.pyew.format == 'raw':
            self.right_combo.append_text('Plain Text')
            # Set plain text by default
            self.right_combo.set_active(3)

        self.connect = self.right_combo.connect("changed", self.right_combo_change)

    def theme_combo_change(self, widget):
        model = self.theme_combo.get_model()
        active = self.theme_combo.get_active()
        option = model[active][0]
        self.tviews.update_theme(option)

    def right_combo_change(self, widget):
        # Get selected option
        model = self.right_combo.get_model()
        active = self.right_combo.get_active()
        option = model[active][0]
        self.tviews.update_righttext(option)
