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
        # Set first by default
        self.theme_combo.set_active(0)

        self.theme_combo.connect("changed", self.theme_combo_change)
        self.attach(self.theme_combo, 1, 2, 0, 1)

    def theme_combo_change(self, widget):
        model = self.theme_combo.get_model()
        active = self.theme_combo.get_active()
        option = model[active][0]
        self.tviews.update_theme(option)
