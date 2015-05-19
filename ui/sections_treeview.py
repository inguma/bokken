#       sections_treeview.py
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
from lib.common import datafile_path

class SectionsView(gtk.ScrolledWindow):

    def __init__(self, uicore, textviews):
        super(SectionsView ,self).__init__()

        self.uicore = uicore

        self.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

        self.sections_tree = SectionsTreeView(self.uicore, textviews)

        self.fcn_pix = gtk.gdk.pixbuf_new_from_file(datafile_path('function.png'))
        self.data_sec_pix = gtk.gdk.pixbuf_new_from_file(datafile_path('data-sec.png'))

        # Add Textview to Scrolled Window
        self.add(self.sections_tree)
        self.show_all()


    def add_content(self):
        sections = self.uicore.get_sections()

        execs = [x[0] for x in self.uicore.execsections]
        for section in self.uicore.get_sections():
            if section[0] in execs:
                tmp = [self.fcn_pix]
            else:
                tmp = [self.data_sec_pix]
            for element in section:
                tmp.append(element)
            self.sections_tree.store.append(tmp)

    def remove_content(self):
        self.sections_tree.store.clear()

class SectionsTreeView(gtk.TreeView):
    '''Sections TextView elements'''

    def __init__(self, core, textviews):
        self.store = gtk.ListStore(gtk.gdk.Pixbuf, str, str, str, str)
        super(SectionsTreeView ,self).__init__(self.store)

        self.uicore = core
        self.textviews = textviews

        self.set_rules_hint(True)
        self.set_has_tooltip(True)

        self.create_sections_columns()

        # Connect right click popup search menu
        self.popup_handler = self.connect('row-activated', self.popup_menu)

    def create_sections_columns(self):

        rendererPix = gtk.CellRendererPixbuf()
        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Name")
        column.set_spacing(5)
        column.pack_start(rendererPix, False)
        column.pack_start(rendererText, True)
        column.set_attributes(rendererText, text=1)
        column.set_attributes(rendererPix, pixbuf=0)
        column.set_sort_column_id(0)
        self.append_column(column)

        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Virtual Address", rendererText, text=2)
        self.store.set_sort_column_id(2,gtk.SORT_ASCENDING)
        column.set_sort_column_id(2)
        self.append_column(column)

        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Virtual Size", rendererText, text=3)
        column.set_sort_column_id(3)
        self.append_column(column)

        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Raw Size", rendererText, text=4)
        column.set_sort_column_id(4)
        self.append_column(column)
        self.set_model(self.store)

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
            link_name = self.store[path][1]
            link_name = 'section.' + link_name
            link_name = "0x%08x" % self.uicore.core.num.get(link_name)
    
            self.textviews.search(self, link_name)
            self.nb = self.textviews.right_notebook
            num = self.nb.page_num(self.textviews.right_textview)
            self.nb.set_current_page(num)

