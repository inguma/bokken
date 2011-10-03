#       sections_dialog.py
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

class SectionsDialog(gtk.Dialog):
    '''Window to popup sections info'''

    def __init__(self, core):
        super(SectionsDialog,self).__init__('Extended sections information', None, gtk.DIALOG_DESTROY_WITH_PARENT, (gtk.STOCK_OK,gtk.RESPONSE_ACCEPT))

        self.uicore = core
        self.sec_bars = ''

        #self.vbox = gtk.VBox(False, 0)

        # the cancel button
        self.butt_cancel = self.action_area.get_children()[0]
        self.butt_cancel.connect("clicked", lambda x: self.destroy())

        # Positions
        self.resize(700, 400)
        self.set_position(gtk.WIN_POS_CENTER)

        # Label...
        self.hbox = gtk.HBox(False, 1)
        self.label = gtk.Label('')
        self.label.set_markup('<big>List of binary sections with their data and size</big>')
        self.label.set_alignment(0.02, 0.5)
        self.icon = gtk.Image()
        self.icon.set_from_stock(gtk.STOCK_INFO, gtk.ICON_SIZE_MENU)
        self.hbox.pack_start(self.icon, False, False, 2)
        self.hbox.pack_start(self.label, True, True, 0)

        # ScrolledWindow
        self.scrolled_window = gtk.ScrolledWindow()
        self.scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.scrolled_window.is_visible = True

        # List view
        self.store = gtk.ListStore(str, int, str, str, str)
        self.tv = gtk.TreeView(self.store)
        self.tv.set_rules_hint(True)

        # Columns
        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Start offset", rendererText, text=0)
        self.store.set_sort_column_id(0, gtk.SORT_ASCENDING)
        column.set_sort_column_id(0)
        self.tv.append_column(column)
    
        rendererBar = gtk.CellRendererProgress()
        column = gtk.TreeViewColumn("Section Size", rendererBar, text=1)
        column.add_attribute(rendererBar, "value", 1)
        column.set_min_width(300)
        column.set_sort_column_id(1)
        self.tv.append_column(column)

        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("End offset", rendererText, text=2)
        column.set_sort_column_id(2)
        self.tv.append_column(column)

        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Flags", rendererText, text=3)
        column.set_sort_column_id(3)
        self.tv.append_column(column)
        self.tv.set_model(self.store)

        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Name", rendererText, text=4)
        column.set_sort_column_id(4)
        self.tv.append_column(column)
        self.tv.set_model(self.store)

        self.vbox.set_spacing(3)
        self.set_border_width(3)

        # Packing
        self.scrolled_window.add(self.tv)
        self.vbox.pack_start(self.hbox, False, False)
        self.vbox.pack_start(self.scrolled_window, True, True)

        self._get_section_bars()
        self.show_all()

    #
    # Methods

    def _get_section_bars(self):
        self.sec_bars = self.uicore.core.cmd_str('S=')
        if self.sec_bars:
            self._parse_ascii_bars()

    def _parse_ascii_bars(self):
        self.bar_lines = self.sec_bars.split('\n')
        sections_info = []
        for line in self.bar_lines:
            if "*" in line:
                line = line.split('* ')[-1]
            else:
                line = line.split('  ')[-1]
            line = line.split(' ')
            sections_info.append(line)
            if len(line) == 5:
                perc = self._get_bar_length(line[1])
                self.store.append([line[0], perc, line[2], line[3], line[4]])

    def _get_bar_length(self, ascii):
        kk = ascii.split('|')[1]
        if '#' in kk:
            if len( kk.split('#-') ) == 2:
                a = len(kk.split('#-')[-1])
                return (50-a)*2
            elif kk[-1] == '#':
                return 100
            else:
                return 0
        else:
            return 0




