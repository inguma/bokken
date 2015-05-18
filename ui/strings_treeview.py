#       strings_treeview.py
#       
#       Copyright 2015 Hugo Teso <hugo.teso@gmail.com>
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

import gtk, pango

class StringsView(gtk.ScrolledWindow):

    def __init__(self, uicore, textviews):
        super(StringsView,self).__init__()

        self.uicore = uicore

        self.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

        self.strings_tree = StringsTreeView(self.uicore, textviews)

        # Add Textview to Scrolled Window
        self.add(self.strings_tree)
        self.show_all()


    def add_content(self):
        strings = self.uicore.get_strings()
        for string in strings:
            if len(string) == 3:
                self.strings_tree.store.append(string)

    def remove_content(self):
        self.strings_tree.store.clear()

class StringsTreeView(gtk.TreeView):
    '''Strings TextView elements'''

    def __init__(self, core, textviews):
        self.store = gtk.ListStore(str, str, str)
        super(StringsTreeView ,self).__init__(self.store)

        self.uicore = core
        self.textviews = textviews

        self.set_rules_hint(True)
        self.set_has_tooltip(True)

        self.create_strings_columns()

        # Connect right click popup search menu
        self.popup_handler = self.connect('row-activated', self.popup_menu)

    def create_strings_columns(self):

        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Address", rendererText, text=0)
        column.set_sort_column_id(0)
        self.append_column(column)

        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Size", rendererText, text=1)
        #self.store.set_sort_column_id(2,gtk.SORT_ASCENDING)
        column.set_sort_column_id(1)
        self.append_column(column)

        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("String", rendererText, text=2)
        column.set_sort_column_id(2)
        self.append_column(column)

    def popup_menu(self, tv, event, row=None):
        '''Controls the behavior of the treeview click event

        Double-click or Enter: Goes to the corresponding address

        @param tv: The treeview.
        @parameter event: The GTK event (gtk.gdk.Event) in case this is a mouse
            click.  Otherwise it's the activated row index in format (n,).
        @parameter row: A gtk.TreeViewColumn object in case it's a keypress,
            otherwise None.

        '''
        # Let's get the row clicked whether it was by mouse or keyboard.
        if row:
            # Keyboard.
            path = event
            primary_action = True
        else:
            # Mouse.
            # I do this to return fast (and to avoid leaking memory in 'e io.va' for now).
            if (event.button != 1) and (event.button !=3):
                return False
            elif event.button == 1:
                # Left-click.
                primary_action = True
            else:
                primary_action = False
    
            coordinates = tv.get_path_at_pos(int(event.x), int(event.y))
            # coordinates is None if the click is outside the rows but inside
            # the widget.
            if not coordinates:
                return False
            (path, column, x, y) = coordinates
    
        # FIXME: We should do this on the uicore, possibly in every operation.
        if self.uicore.backend == 'radare':
            if self.uicore.use_va:
                self.uicore.core.cmd0('e io.va=0')
            else:
                self.uicore.core.cmd0('e io.va=1')
    
        # Main loop, deciding whether to take an action or display a pop-up.
        if primary_action:
            # It's a left click or Enter on a row.
            # Is it over a plugin name?
            # Get the information about the row.
            link_name = self.store[path][2]
    
            self.textviews.search(self, link_name)
            self.nb = self.textviews.right_notebook
            num = self.nb.page_num(self.textviews.right_textview)
            self.nb.set_current_page(num)
