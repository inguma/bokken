#!/usr/bin/python

#       textviews.py
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

class Statusbar(gtk.Statusbar):
    '''Statusbar for main window'''

    def __init__(self, core):
        super(Statusbar,self).__init__()

        self.uicore = core

        self.sbar_context = self.get_context_id('sb')

    # Method to add content to the status bar
    def add_text(self, data_dict, version):
        '''data_dict ontains text to be added.
           Key will be the title
           Value will be... well, the value :)'''
        self.text = ''
        for element in data_dict.keys():
            self.text += element.capitalize() + ': ' + str(data_dict[element]) + ' | '
        self.push(self.sbar_context, self.text)
        self.pack_end(gtk.Label('Bokken ' + version), False)
        self.pack_end(gtk.VSeparator(), False)
        self.show_all()

    # Method to clear the statusbar before adding new content
    def clear_sbar(self):
        self.push(self.sbar_context, '')

