#       statusbar.py
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
import pango

class Statusbar(gtk.Statusbar):
    '''Statusbar for main window'''

    def __init__(self, core, tviews):
        super(Statusbar,self).__init__()

        self.uicore = core
        self.tviews = tviews

        self.icons = {'processor':os.path.dirname(__file__) + os.sep + 'data' + os.sep + 'processor_small.png', 'name':gtk.STOCK_FILE, 
                        'format':gtk.STOCK_EXECUTE, 'size':gtk.STOCK_PREFERENCES, 'OS':gtk.STOCK_INFO, 
                        'type':gtk.STOCK_INFO, 'va':gtk.STOCK_UNINDENT, 'ep': gtk.STOCK_INDENT}

    def create_statusbar(self):
        self._statusbar = gtk.HBox()
        self._status_holder = self
        # OMG
        frame = self._status_holder.get_children()[0]
        box = frame.get_children()[0]
        frame.remove(box)
        frame.add(self._statusbar)

    # Method to add content to the status bar
    def add_text(self, data_dict, version):
        '''data_dict ontains text to be added.
           Key will be the title
           Value will be... well, the value :)'''
        self.box = gtk.HBox(False, 1)
        self._statusbar.pack_start(self.box, False, False, 1)
        ellipsize=pango.ELLIPSIZE_NONE
        for element in data_dict.keys():
            # Element icon
            if element == 'processor':
                _icon = gtk.image_new_from_file(os.path.dirname(__file__) + os.sep + 'data' + os.sep + 'processor_small.png')
                self.box.pack_start(_icon, False, False, 0)
            else:
                _icon = gtk.image_new_from_stock(self.icons[element], gtk.ICON_SIZE_MENU)
                self.box.pack_start(_icon, False, False, 0)
            # Element label
            label = gtk.Label()
            label.set_markup('<b>' + element.capitalize() + ':</b>')
            label.set_padding(1, 5)
            label.set_max_width_chars(len(element) + 1)
            label.set_single_line_mode(True)
            label.set_ellipsize(ellipsize)
            self.box.pack_start(label, True, True, 1)
            # Element content
            label = gtk.Label(str(data_dict[element]))
            label.set_padding(1, 5)
            label.set_max_width_chars(len(str(data_dict[element])))
            label.set_single_line_mode(True)
            label.set_ellipsize(ellipsize)
            self.box.pack_start(label, True, True, 1)
            sep = gtk.VSeparator()
            self.box.pack_start(sep, True, True, 1)

        if version:
            _icon = gtk.image_new_from_file(os.path.dirname(__file__) + os.sep + 'data' + os.sep + 'bokken-small.svg')
            self.pack_start(_icon, False, False, 1)
            label = gtk.Label()
            label.set_markup('<b>Bokken ' + version + '</b> (' + self.uicore.backend.capitalize() + ')')
            label.set_padding(3, 3)
            self.pack_end(label, False)

        self.show_all()

    def remove_all(self):
        for child in self.box.get_children():
            self.box.remove(child)
        for child in self.get_children():
            if type(child) is not gtk.Frame:
                self.remove(child)
