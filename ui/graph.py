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

import ui.mydot_widget as mydot_widget
import graph_bar

class MyDotWidget(gtk.HBox):
    '''Working'''

    def __init__(self, core, main):

        self.uicore = core
        self.main = main
        self.last_fcn = ''

        #dotcode = self.uicore.get_callgraph()
        gtk.HBox.__init__(self, False, 1)

        #self.dot_widget = DotWidget()
        self.dot_widget = mydot_widget.MyDotWidget(self.uicore, self.main)
        self.create_tree()
        self.pack_start(self.dot_widget, True, True, 0)
        self.bar = graph_bar.GraphBar(self.dot_widget, self, self.uicore)
        self.pack_start(self.bar, False, False, 0)
        if self.uicore.backend == 'radare':
            self.pack_start(self.sw, False, False, 4)

    def set_dot(self, dotcode):
        dotcode = dotcode.replace('color=lightgray, style=filled', 'color=blue')
        dotcode = dotcode.replace('color="lightgray"', 'color="blue"')
        dotcode = dotcode.replace('color="green"', 'color="green" fontname="Courier" fontsize="8"')
        self.dot_widget.set_dotcode(dotcode)
        if self.uicore.backend == 'radare':
            self.nodes = {}
            function = ''
            for node in self.dot_widget.graph.nodes:
                function = ''
                if node.url:
                    function, node_name = node.url.split('/')
                    self.nodes[node_name] = [node.x, node.y]
            if function:
                self.update_tree(function)
        self.dot_widget.on_zoom_fit(None)

    def create_tree(self):
        # Scrolled Window
        self.sw = gtk.ScrolledWindow()
        self.sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        self.sw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)

        self.store = gtk.ListStore(str, str)
        self.tree = gtk.TreeView(self.store)

        self.sw.add(self.tree)

        self.tree.set_rules_hint(True)

        # Connect right click popup search menu
        self.popup_handler = self.tree.connect('button-press-event', self.popup_menu)

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
        nodes = self.nodes.keys()
        nodes.sort()
        for element in nodes:
            self.treestore.append(it, [element])

        self.tree.set_model(self.treestore)
        self.tree.expand_all()

    def popup_menu(self, tree, event):
        if event.button == 1:
            #(path, column) = tree.get_cursor()
            (path, column, x, y) = tree.get_path_at_pos(int(event.x), int(event.y))
            # Is it over a plugin name ?
            # Ge the information about the click
            if path is not None and len(path) == 2 and self.nodes:
                node = self.treestore[path][0]
                self.dot_widget.animate_to( int(self.nodes[node][0]), int(self.nodes[node][1]) )
