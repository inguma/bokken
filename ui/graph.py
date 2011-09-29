#       graph.py
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

from xdot import DotWidget

#class MyDotWidget(DotWidget):
class MyDotWidget(gtk.HBox):
    '''Working'''

    def __init__(self, core):

        self.uicore = core
        #dotcode = self.uicore.get_callgraph()
        gtk.HBox.__init__(self, False, 1)

        self.dot_widget = DotWidget()
        self.create_tree()
        self.pack_start(self.dot_widget, True, True, 0)
        if self.uicore.backend == 'radare':
            self.pack_start(self.tree, False, False, 4)

    def set_dot(self, dotcode):
        self.dot_widget.set_dotcode(dotcode)
        #self.animate_to( self.graph.nodes[-1].x, self.graph.nodes[-1].y)
        if self.uicore.backend == 'radare':
            self.nodes = {}
            for node in self.dot_widget.graph.nodes:
                function, node_name = node.url.split('/')
                self.nodes[node_name] = [node.x, node.y]
            self.update_tree(function)
        self.dot_widget.on_zoom_fit(None)

    def create_tree(self):
        self.store = gtk.ListStore(str, str)
        self.tree = gtk.TreeView(self.store)

        self.tree.set_rules_hint(True)

        # Connect right click popup search menu
        self.pupoup_handler = self.tree.connect('button-press-event', self.popup_menu)

        # Create the column
        bblocks = gtk.TreeViewColumn()
        bblocks.set_title("Basic Blocks")

        cell = gtk.CellRendererText()
        bblocks.pack_start(cell, True)
        bblocks.add_attribute(cell, "text", 0)

        self.treestore = gtk.TreeStore(str)

        # Add column to tree
        self.tree.append_column(bblocks)
        self.tree.set_model(self.treestore)
        self.tree.expand_all()

    def update_tree(self, function):
        # Clear contents
        self.treestore.clear()
        # Iterate bb and add to the tree
        it = self.treestore.append(None, [function])
        for element in self.nodes.keys():
            self.treestore.append(it, [element])

        self.tree.set_model(self.treestore)
        self.tree.expand_all()

    def popup_menu(self, tree, event):
        if event.button == 1:
            (path, column) = tree.get_cursor()
            # Is it over a plugin name ?
            # Ge the information about the click
            if path is not None and len(path) == 2:
                node = self.treestore[path][0]
                self.dot_widget.animate_to( int(self.nodes[node][0]), int(self.nodes[node][1]) )
