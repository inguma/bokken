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

from gi.repository import Gtk
from gi.repository import Pango
from lib.common import datafile_path

class Statusbar(Gtk.Statusbar):
    '''Statusbar for main window'''

    def __init__(self, core, tviews):
        super(Statusbar,self).__init__()

        self.uicore = core
        self.tviews = tviews

        self.icons = {'processor':datafile_path('processor_small.png'), 'name':Gtk.STOCK_FILE, 
                        'format':Gtk.STOCK_EXECUTE, 'size':Gtk.STOCK_PREFERENCES, 'OS':Gtk.STOCK_INFO, 
                        'type':Gtk.STOCK_INFO, 'va':Gtk.STOCK_UNINDENT, 'ep': Gtk.STOCK_INDENT}

    def create_statusbar(self):
        self._statusbar = Gtk.HBox()
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
        self.box = Gtk.HBox(False, 1)
        self._statusbar.pack_start(self.box, False, False, 1)
        ellipsize=Pango.EllipsizeMode.NONE
        for element in data_dict.keys():
            # Element icon
            if element == 'processor':
                _icon = Gtk.image_new_from_file(datafile_path('processor_small.png'))
                self.box.pack_start(_icon, False, False, 0)
            else:
                _icon = Gtk.Image.new_from_stock(self.icons[element], Gtk.IconSize.MENU)
                self.box.pack_start(_icon, False, False, 0)
            # Element label
            label = Gtk.Label()
            label.set_markup('<b>' + element.capitalize() + ':</b>')
            label.set_padding(1, 5)
            label.set_max_width_chars(len(element) + 1)
            label.set_single_line_mode(True)
            label.set_ellipsize(ellipsize)
            self.box.pack_start(label, True, True, 1)
            # Element content
            label = Gtk.Label(label=str(data_dict[element]))
            label.set_padding(1, 5)
            label.set_max_width_chars(len(str(data_dict[element])))
            label.set_single_line_mode(True)
            label.set_ellipsize(ellipsize)
            self.box.pack_start(label, True, True, 1)
            sep = Gtk.VSeparator()
            self.box.pack_start(sep, True, True, 1)

        if version:
            _icon = Gtk.image_new_from_file(datafile_path('bokken-small.svg'))
            self.pack_start(_icon, False, False, 1)
            label = Gtk.Label()
            label.set_markup('<b>Bokken ' + version + '</b> (' + self.uicore.backend.capitalize() + ' ' + self.uicore.version + ')')
            label.set_padding(3, 3)
            self.pack_end(label, False, True, 0)

        self.show_all()

    def remove_all(self):
        for child in self.box.get_children():
            self.box.remove(child)
        for child in self.get_children():
            if type(child) is not Gtk.Frame:
                self.remove(child)
