#       treeviews.py
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

class TreeViews(gtk.TreeView):
    '''Main TextView elements'''

    def __init__(self, core, textviews):
        self.store = gtk.ListStore(str, str, str, str)
        super(TreeViews,self).__init__(self.store)

        self.uicore = core
        self.textviews = textviews

        self.set_rules_hint(True)

        # Connect right click popup search menu
        self.pupoup_handler = self.connect('button-press-event', self.popup_menu)

#        self.create_functions_columns()

    def create_functions_columns(self):
    
#        self.store = gtk.ListStore(str)

        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Function", rendererText, text=0)
        column.set_sort_column_id(0)
        self.append_column(column)
        self.set_model(self.store)

    def create_sections_columns(self):
    
#        self.store = gtk.ListStore(str, str, str, str)

        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Section", rendererText, text=0)
        column.set_sort_column_id(0)
        self.append_column(column)
    
        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Virtual Address", rendererText, text=1)
        column.set_sort_column_id(1)
        self.append_column(column)

        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Virtual Size", rendererText, text=2)
        column.set_sort_column_id(2)
        self.append_column(column)

        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Raw Size", rendererText, text=3)
        column.set_sort_column_id(3)
        self.append_column(column)
        self.set_model(self.store)

    def create_exports_columns(self):

        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Offset", rendererText, text=0)
        column.set_sort_column_id(0)
        self.append_column(column)
    
        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Name", rendererText, text=1)
        column.set_sort_column_id(1)
        self.append_column(column)

        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Ordinal", rendererText, text=2)
        column.set_sort_column_id(2)
        self.append_column(column)
        self.set_model(self.store)

    def remove_columns(self):
        columns = self.get_columns()
        for column in columns:
            self.remove_column(column)

    def create_pdf_tree(self, pdfinfo):
        # Create the column
        pdfs = gtk.TreeViewColumn()
        pdfs.set_title("PDF Header")

        cell = gtk.CellRendererText()
        pdfs.pack_start(cell, True)
        pdfs.add_attribute(cell, "text", 0)

        cell = gtk.CellRendererText()
        pdfs.pack_start(cell, True)
        pdfs.add_attribute(cell, "text", 1)

        self.treestore = gtk.TreeStore(str, str)

        # Iterate PDF info and add to the tree
        header = ' '.join(pdfinfo[0][0:])
        it = self.treestore.append(None, [header, ''])
        for element in pdfinfo[1:-1]:
            col0 = element[0].strip("'")
            col1 = ' '.join(element[1:]).strip(' ')
            self.treestore.append( it, [col0, col1] )

        # Add column to tree
        self.append_column(pdfs)
        self.set_model(self.treestore)
        self.expand_all()

    def create_url_tree(self, links):
        # Create the column
        imports = gtk.TreeViewColumn()
        imports.set_title("URL")

        cell = gtk.CellRendererText()
        imports.pack_start(cell, True)
        imports.add_attribute(cell, "text", 0)

        self.treestore = gtk.TreeStore(str)

        # Iterate links and add to the tree
        it = self.treestore.append(None, ['Remote links'])
        for element in links['remotes']:
            self.treestore.append(it, [element + '\t' + ''])
        it = self.treestore.append(None, ['Local resources'])
        for element in links['locals']:
            self.treestore.append(it, [element + '\t' + ''])

        # Add column to tree
        self.append_column(imports)
        self.set_model(self.treestore)
        self.expand_all()

    def create_tree(self, imps):
        # Create the column
        imports = gtk.TreeViewColumn()
        imports.set_title("Imports")

        cell = gtk.CellRendererText()
        imports.pack_start(cell, True)
        imports.add_attribute(cell, "text", 0)

        self.treestore = gtk.TreeStore(str)

        # Iterate imports and add to the tree
        for element in imps.keys():
            it = self.treestore.append(None, [element])
            for imp in imps[element]:
                self.treestore.append(it, [imp[0] + '\t' + imp[1]])

        # Add column to tree
        self.append_column(imports)
        self.set_model(self.treestore)
        self.expand_all()

    def popup_menu(self, tv, event):
        '''Shows a menu when you right click on a plugin.
        
        @param tv: the treeview.
        @parameter event: The GTK event 
        '''
        if event.button == 3:
            # It's a right click !
            _time = event.time
            (path, column) = tv.get_cursor()
            # Is it over a plugin name ?
            # Get the information about the click
            if path is not None and len(path) == 1:
                link_name = self.store[path][0]
            elif path is not None and len(path) == 2:
                link_name = self.treestore[path][0]

            # Detect if search string is from URL or PE/ELF
            link_name = link_name.split("\t")
            # Elf/PE (function)
            if len( link_name ) == 1:
                link_name = 'FUNCTION ' + link_name[0]
            # Elf/PE (import/export)
            elif len( link_name ) == 2 and link_name[1] != '':
                link_name = link_name[1]
            # URL
            else:
                link_name = link_name[0]

            # Ok, now I show the popup menu !
            # Create the popup menu
            gm = gtk.Menu()

            # And the items
            e = gtk.MenuItem("Search")
            e.connect('activate', self.textviews.search, link_name)
            gm.append( e )
            if 'radare' in self.uicore.backend:
                e = gtk.MenuItem("Show graph")
                e.connect('activate', self.textviews.update_graph, link_name)
                gm.append( e )
            gm.show_all()

            gm.popup( None, None, None, event.button, _time)

        elif event.button == 1 and event.type == gtk.gdk._2BUTTON_PRESS:
            # It's a double click !
            (path, column) = tv.get_cursor()
            # Is it over a plugin name ?
            # Ge the information about the click
            if path is not None and len(path) == 1:
                link_name = self.store[path][0]
            elif path is not None and len(path) == 2:
                link_name = self.treestore[path][0]

            # Detect if search string is from URL or PE/ELF
            link_name = link_name.split("\t")
            # Elf/PE (function)
            if len( link_name ) == 1:
                link_name = 'FUNCTION ' + link_name[0]
            # Elf/PE (import/export)
            elif len( link_name ) == 2 and link_name[1] != '':
                link_name = link_name[1]
            # URL
            else:
                link_name = link_name[0]

            self.textviews.search(self, link_name)
