#       leftcombo.py
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

class LeftCombo:
    '''Left TextView elements'''

    def __init__(self, tviews):

        self.tviews = tviews

        #################################################################
        # Left ComboBox
        #################################################################
        self.left_combo = gtk.combo_box_new_text()
        options = ['Functions', 'Sections', 'Imports', 'Exports', 'PDF Info']
        for option in options:
            self.left_combo.append_text(option)
        # Set Functions by default
        self.left_combo.set_active(0)

        self.left_combo.connect("changed", self.update_left_content)

    def return_combo(self):
        return self.left_combo

    def update_combo_options(self, format):
        pass

    def create_model(self, mode):
        self.treeView.store.clear()
        self.treeView.remove_columns()
        if mode == 'Functions':
            self.treeView.create_functions_columns()
            for function in self.uicore.get_functions():
                self.treeView.store.append([function, '', '', ''])
        elif mode == 'Sections':
            self.treeView.create_sections_columns()
            for section in self.uicore.get_sections():
                tmp = []
                for element in section:
                    tmp.append(element)
                self.treeView.store.append(tmp)
        elif mode == 'Imports':
            self.treeView.create_tree( self.uicore.get_imports() )
        elif mode == 'Exports':
            self.treeView.create_exports_columns()
            for export in self.uicore.get_exports():
                self.treeView.store.append(export)
        elif mode == 'PDF':
            self.treeView.create_pdf_tree( self.uicore.get_pdf_info() )

    def update_left_content(self, widget):
        model = self.left_combo.get_model()
        active = self.left_combo.get_active()
        option = model[active][0]
        self.create_model(option)
