#       html_tree.py
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

class HtmlWindow(gtk.ScrolledWindow):

    def __init__(self, uicore):
        super(HtmlWindow,self).__init__()

        self.uicore = uicore

        self.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

        self.html_tree = HtmlTree(self.uicore)

        # Add Textview to Scrolled Window
        self.add(self.html_tree)
        self.show_all()

class HtmlTree(gtk.TreeView):
    '''HTML elements TreeView'''

    def __init__(self, core):
        self.store = gtk.ListStore(str, str, str, str)
        super(HtmlTree,self).__init__(self.store)

        self.uicore = core

        self.set_rules_hint(True)
        self.show_all()

    def create_html_tree(self):

        form_elements = self.uicore.forms
        comments = self.uicore.comments
        scripts = self.uicore.scripts

        # Create the column
        htmls = gtk.TreeViewColumn()
        htmls.set_title("HTML elements")

        cell = gtk.CellRendererText()
        htmls.pack_start(cell, True)
        htmls.add_attribute(cell, "text", 0)

        cell = gtk.CellRendererText()
        htmls.pack_start(cell, True)
        htmls.add_attribute(cell, "text", 1)

        cell = gtk.CellRendererText()
        htmls.pack_start(cell, True)
        htmls.add_attribute(cell, "text", 2)

        self.treestore = gtk.TreeStore(str, str, str)

        form_it = self.treestore.append(None, ['Forms', '', ''])
        comments_it = self.treestore.append(None, ['Comments', '', ''])
        scripts_it = self.treestore.append(None, ['Scripts', '', ''])

        for element in form_elements:
            if 'form' in element:
                fit = self.treestore.append(form_it, ['Form', '', ''])
                for attr in element[1:]:
                    it = self.treestore.append(fit, [attr[0], attr[1], ''])
            else:
                it = self.treestore.append(fit, ['Input', '', ''])
                for attr in element[1:]:
                    self.treestore.append(it, [attr[0], attr[1], ''])

        for comment in comments:
            self.treestore.append(comments_it, ['', comment, ''])

        for script in scripts:
            self.treestore.append(scripts_it, ['', script, ''])

        # Add column to tree
        self.append_column(htmls)
        self.set_model(self.treestore)
        self.expand_all()

        self.show_all()
