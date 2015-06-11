#       rightnotebook.py
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

import platform
from gi.repository import Gtk
import ui.graph

class RightNotebook(Gtk.Notebook):
    '''Right Notebook elements'''

    def __init__(self, tviews):
        super(RightNotebook,self).__init__()

        self.last_fcn = ''

        self.tviews = tviews
        self.scrolled_window = self.tviews.right_textview
        self.strings_treeview = self.tviews.strings_treeview
        self.sections_treeview = self.tviews.sections_treeview
        self.hexdump_view = self.tviews.hexdump_view
        self.bindiff = self.tviews.bindiff
        self.info_elements = self.tviews.info_widget
        self.uicore = self.tviews.uicore
        self.main = self.tviews.main

        self.xdot_box = ui.graph.MyDotWidget(self.uicore, self.main)
        self.xdot_widget = self.xdot_box.dot_widget

        self.set_scrollable(True)
        self.create_tabs()

    def create_tabs(self):

        #################################################
        # Code view TAB
        self.append_page(self.scrolled_window)
        if platform.system() != 'Windows':
            text = 'Loading dasm...'
        else:
            text = 'Code'
        self.code_tab = self.create_tab(text, self.scrolled_window, 'SORT_DESCENDING')

        self.set_tab_label_packing(self.scrolled_window, False, False, Gtk.PACK_START)
        self.set_tab_label(self.scrolled_window, self.code_tab)
        self.code_tab.get_children()[0].set_sensitive(False)

        #################################################
        # Graph map TAB
        self.append_page(self.xdot_box)

        label = 'Flowgraph'

        tab = self.create_tab(label, self.xdot_box, 'ZOOM_FIT')

        self.set_tab_label_packing(self.xdot_box, False, False, Gtk.PACK_START)
        self.set_tab_label(self.xdot_box, tab)

        #################################################
        # Hexdump TAB
        self.append_page(self.hexdump_view)
        tab = self.create_tab('Hexdump', self.hexdump_view, 'INDEX')

        self.set_tab_label_packing(self.hexdump_view, False, False, Gtk.PACK_START)
        self.set_tab_label(self.hexdump_view, tab)

        #################################################
        # Strings view TAB
        self.append_page(self.strings_treeview)
        tab = self.create_tab('Strings', self.strings_treeview, 'JUSTIFY_CENTER')

        self.set_tab_label_packing(self.strings_treeview, False, False, Gtk.PACK_START)
        self.set_tab_label(self.strings_treeview, tab)

        #################################################
        # Sections view TAB
        self.append_page(self.sections_treeview)
        tab = self.create_tab('Sections', self.sections_treeview, 'JUSTIFY_FILL')

        self.set_tab_label_packing(self.sections_treeview, False, False, Gtk.PACK_START)
        self.set_tab_label(self.sections_treeview, tab)

        self.add_info_elements_tab()

        self.connect("switch-page", self.on_switch)

        #self.set_current_page(0)
        # Hide callgraph for URL, Plain Text and PDF
        if self.uicore.core.format == 'Hexdump':
            self.remove_page(1)
            self.remove_page(0)
            self.remove_page(2)
            self.set_current_page(0)
        elif self.uicore.core.format in ['Program', 'PE', 'ELF']:
            # Set flowgraph view as default while disassembly finishes
            self.set_current_page(1)

    def on_switch(self, notebook, page, page_num):
        # Tabs to avoid
        avoid = [
                self.page_num(self.scrolled_window),
                self.page_num(self.xdot_box),
                self.page_num(self.bindiff),
                self.page_num(self.info_elements)
                ]
        #avoid = [0, 1, 5]
        # walk through tabs and remove all content but the active one
        for page in range(self.get_n_pages()):
            if page != page_num and page not in avoid:
                widget = self.get_nth_page(page)
                widget.remove_content()
            elif page == page_num and page not in avoid:
                widget = self.get_nth_page(page)
                widget.add_content()
        if page_num == self.page_num(self.xdot_box):
            self.xdot_box.set_dot(self.uicore.get_callgraph(self.last_fcn))

    def add_bindiff_tab(self, filename, fcn_thr, bb_thr, bytes):
        #################################################
        # Bindiffing TAB
        self.append_page(self.bindiff)
        tab = self.create_tab('Bindiff', self.bindiff, 'REFRESH')

        self.set_tab_label_packing(self.bindiff, False, False, Gtk.PACK_START)
        self.set_tab_label(self.bindiff, tab)
        self.show_all()
        num = self.page_num(self.bindiff)
        self.set_current_page(num)

        self.tviews.bindiff_widget.set_file(filename, fcn_thr, bb_thr, bytes)
        self.tviews.bindiff_widget.diff()

    def add_info_elements_tab(self):
        #################################################
        # File info elements TAB
        # Only on radare for now.
        self.uicore.get_full_file_info()
        self.append_page(self.info_elements)
        tab = self.create_tab('File info', self.info_elements, 'INFO')

        self.set_tab_label_packing(self.info_elements, False, False, Gtk.PACK_START)
        self.set_tab_label(self.info_elements, tab)
        self.info_elements.info_tree.create_info_tree()
        self.show_all()

#    def hide_tabs(self):
#        self.set_show_tabs(False)
#        self.set_current_page(0)

    def create_tab(self, title, tab_child, icon=''):
        tab_box = Gtk.HBox(False, 3)
        close_button = Gtk.Button()

        image = Gtk.Image()
        image.set_from_stock(Gtk.STOCK_CLOSE, Gtk.IconSize.MENU)

        label = Gtk.Label(label=title)
        if icon:
            i = Gtk.Image()
            i.set_from_stock(eval('Gtk.STOCK_' + icon), Gtk.IconSize.MENU)
            tab_box.pack_start(i, False, False, 0)

        close_button.connect("clicked", self.close_tab, tab_child)
        close_button.set_image(image)
        close_button.set_relief(Gtk.ReliefStyle.NONE)
        tab_box.pack_start(label, True, True, 0)
        tab_box.pack_end(close_button, False, False, 0)

        tab_box.show_all()
        if title in ['Loading dasm...', 'Code', 'Callgraph', 'Flowgraph', 'Interactive', 'Strings', "Sections", 'Hexdump', 'Bindiff', 'File info']:
            close_button.hide()

        return tab_box

    def close_tab(self, widget, child):
        pagenum = self.page_num(child)

        if pagenum != -1:
            self.remove_page(pagenum)
            child.destroy()

        child.destroy()

    def remove_tabs(self):
        for tab in range(self.get_n_pages()):
            self.remove_page(-1)

    def finish_dasm(self):
        self.code_tab.get_children()[0].set_sensitive(True)
        self.code_tab.get_children()[1].set_text('Code')
