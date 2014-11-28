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

import Image
import os, tempfile
from subprocess import *

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
        self.side_vb = gtk.VBox(False, 1)
        self.side_hb = gtk.HBox(False, 1)

        #self.dot_widget = DotWidget()
        self.dot_widget = mydot_widget.MyDotWidget(self.uicore, self.main)
        self.create_tree()
        self.create_preview()
        self.pack_start(self.dot_widget, True, True, 0)
        self.bar = graph_bar.GraphBar(self.dot_widget, self, self.uicore)
        #self.pack_start(self.bar, False, False, 0)
        self.side_hb.pack_start(self.bar, False, False, 1)
        if self.uicore.backend == 'radare':
            self.pack_start(self.side_vb, False, False, 1)
            self.side_hb.pack_start(self.sw, True, True, 1)
            self.side_vb.pack_start(self.side_hb, True, True, 1)
            self.side_vb.pack_start(self.preview, False, False, 0)

    def set_dot(self, dotcode):
        dotcode = dotcode.replace('color=lightgray, style=filled,', 'color=blue')
        dotcode = dotcode.replace('color="lightgray"', 'color="blue"')
        dotcode = dotcode.replace('color=lightgray', 'color=lightgray, bgcolor=white')
        dotcode = dotcode.replace('color="green"', 'color="green", fontname="Courier", fontsize="14"')
        self.dot_widget.set_dotcode(dotcode)
        self.generate_thumbnail(dotcode)
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
        self.dot_widget.on_zoom_100(None)
        # Navigate to first node
        if len(self.nodes) > 1:
            node = self.nodes.keys()[0]
            self.dot_widget.animate_to(int(self.nodes[node][0]), int(self.nodes[node][1]))

    def generate_thumbnail(self, dotcode):
        #size = self.tree.allocation.width
        size = self.side_hb.allocation.width
        tmp_dot = tempfile.NamedTemporaryFile(delete = False)
        tmp_dot.write(dotcode)
        tmp_dot.close()

        cmd = "/usr/bin/dot -Tpng " + tmp_dot.name + " > " + tmp_dot.name + ".png" 
        os.system(cmd)

        im = Image.open(tmp_dot.name + ".png")
        im.convert('RGBA')
        im.thumbnail([size,size], Image.ANTIALIAS)
        #im.save(tmp_dot.name + ".png.thumbnail", "JPEG")

        # Add white backgound as image is transparent
        offset_tuple = (im.size[0], im.size[1])
        final_thumb = Image.new(mode='RGBA',size=offset_tuple, color=(255,255,255,0))
        final_thumb.paste(im)
        final_thumb.save(tmp_dot.name + ".png.thumbnail", "PNG")

        self.fill_preview(tmp_dot.name + ".png.thumbnail")

        os.remove(tmp_dot.name)
        os.remove(tmp_dot.name + ".png")
        os.remove(tmp_dot.name + ".png.thumbnail")

    def create_preview(self):
        # Create Image window for graph preview
        self.preview = gtk.Image()
        self.preview.show()

    def fill_preview(self, path):
        self.preview.set_from_file(path)

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
            coordinates = tree.get_path_at_pos(int(event.x), int(event.y))
            # Get the information about the click.
            # coordinates is None if the click is outside the rows but inside
            # the widget.
            if not coordinates:
                return False
            (path, column, x, y) = coordinates
            if len(path) == 2 and self.nodes:
                node = self.treestore[path][0]
                self.dot_widget.animate_to(int(self.nodes[node][0]), int(self.nodes[node][1]))
