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

import gtk

import ui.graph as graph

class RightNotebook(gtk.Notebook):
    '''Right Notebook elements'''

    def __init__(self, tviews, scrolled_window, strings_textview, repr_textview, interactive_scrolled, bindiff, html_elements, info_elements, uicore, main):
        super(RightNotebook,self).__init__()

        self.last_fcn = ''

        self.tviews = tviews
        self.scrolled_window = scrolled_window
        self.strings_textview = strings_textview
        self.repr_textview = repr_textview
        self.interactive_scrolled = interactive_scrolled
        self.hexdump_view = self.tviews.hexdump_view
        self.bindiff = bindiff
        self.html_elements = html_elements
        self.info_elements = info_elements
        self.uicore = uicore
        self.main = main

        self.xdot_box = graph.MyDotWidget(self.uicore, self.main)
        self.xdot_widget = self.xdot_box.dot_widget

        self.set_scrollable(True)
        self.create_tabs()

    def create_tabs(self):

        #################################################
        # Code view TAB
        self.append_page(self.scrolled_window)
        if self.uicore.backend == 'radare' and platform.system() != 'Windows':
            text = 'Loading dasm...'
        else:
            text = 'Code'
        self.code_tab = self.create_tab(text, self.scrolled_window, 'SORT_DESCENDING')

        self.set_tab_label_packing(self.scrolled_window, False, False, gtk.PACK_START)
        self.set_tab_label(self.scrolled_window, self.code_tab)
        if self.uicore.backend == 'radare':
            self.code_tab.get_children()[0].set_sensitive(False)

        #################################################
        # Graph map TAB
        self.append_page(self.xdot_box)

        if self.uicore.backend == 'pyew':
            label = 'Callgraph'
        else:
            label = 'Flowgraph'

        tab = self.create_tab(label, self.xdot_box, 'ZOOM_FIT')

        self.set_tab_label_packing(self.xdot_box, False, False, gtk.PACK_START)
        self.set_tab_label(self.xdot_box, tab)

        #################################################
        # Hexdump TAB
        self.append_page(self.hexdump_view)
        tab = self.create_tab('Hexdump', self.hexdump_view, 'INDEX')

        self.set_tab_label_packing(self.hexdump_view, False, False, gtk.PACK_START)
        self.set_tab_label(self.hexdump_view, tab)

        #################################################
        # Strings view TAB
        self.append_page(self.strings_textview)
        tab = self.create_tab('Strings', self.strings_textview, 'JUSTIFY_CENTER')

        self.set_tab_label_packing(self.strings_textview, False, False, gtk.PACK_START)
        self.set_tab_label(self.strings_textview, tab)

        #################################################
        # Repr view TAB
        self.append_page(self.repr_textview)
        tab = self.create_tab('Strings repr', self.repr_textview, 'JUSTIFY_FILL')

        self.set_tab_label_packing(self.repr_textview, False, False, gtk.PACK_START)
        self.set_tab_label(self.repr_textview, tab)

        #################################################
        # Interactive view TAB
        self.append_page(self.interactive_scrolled)
        tab = self.create_tab('Interactive', self.interactive_scrolled, 'EXECUTE')

        self.set_tab_label_packing(self.interactive_scrolled, False, False, gtk.PACK_START)
        self.set_tab_label(self.interactive_scrolled, tab)

        if self.uicore.backend == 'radare':
            self.add_info_elements_tab()

        self.connect("switch-page", self.on_switch)

        #self.set_current_page(0)
        # Hide callgraph for URL, Plain Text and PDF
        if self.uicore.core.format in ['Plain Text', 'PDF', 'Hexdump']:
            self.remove_page(1)
            if self.uicore.core.format != 'Plain Text':
                self.remove_page(0)
            self.set_current_page(0)
        elif self.uicore.core.format in ['Program', 'PE', 'ELF'] and self.uicore.backend == 'radare':
            # Set flowgraph view as default while disassembly finishes
            self.set_current_page(1)

    def on_switch(self, notebook, page, page_num):
        # Tabs to avoid
        avoid = [
                self.page_num(self.scrolled_window),
                self.page_num(self.xdot_box),
                self.page_num(self.interactive_scrolled),
                self.page_num(self.bindiff),
                self.page_num(self.html_elements),
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
        if page_num == self.page_num(self.xdot_box) and self.uicore.backend == 'radare':
            self.xdot_box.set_dot(self.uicore.get_callgraph(self.last_fcn))

    def add_bindiff_tab(self, filename, fcn_thr, bb_thr, bytes):
        #################################################
        # Bindiffing TAB
        if self.uicore.backend == 'radare':
            self.append_page(self.bindiff)
            tab = self.create_tab('Bindiff', self.bindiff, 'REFRESH')
    
            self.set_tab_label_packing(self.bindiff, False, False, gtk.PACK_START)
            self.set_tab_label(self.bindiff, tab)
            self.show_all()
            num = self.page_num(self.bindiff)
            self.set_current_page(num)

            self.tviews.bindiff_widget.set_file(filename, fcn_thr, bb_thr, bytes)
            self.tviews.bindiff_widget.diff()

    def add_html_elements_tab(self):
        #################################################
        # HTML elements TAB
        if self.uicore.core.format == 'URL':
            self.append_page(self.html_elements)
            tab = self.create_tab('Elements', self.html_elements, 'INFO')
    
            self.set_tab_label_packing(self.html_elements, False, False, gtk.PACK_START)
            self.set_tab_label(self.html_elements, tab)
            self.html_elements.html_tree.create_html_tree()
            self.show_all()
            self.set_current_page(0)

    def add_info_elements_tab(self):
        #################################################
        # File info elements TAB
        if self.uicore.backend == 'radare':
            self.uicore.get_full_file_info()
            self.append_page(self.info_elements)
            tab = self.create_tab('File info', self.info_elements, 'INFO')

            self.set_tab_label_packing(self.info_elements, False, False, gtk.PACK_START)
            self.set_tab_label(self.info_elements, tab)
            self.info_elements.info_tree.create_info_tree()
            self.show_all()

#    def hide_tabs(self):
#        self.set_show_tabs(False)
#        self.set_current_page(0)

    def create_tab(self, title, tab_child, icon=''):
        tab_box = gtk.HBox(False, 3)
        close_button = gtk.Button()

        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU)

        label = gtk.Label(title)
        if icon:
            i = gtk.Image()
            i.set_from_stock(eval('gtk.STOCK_' + icon), gtk.ICON_SIZE_MENU)
            tab_box.pack_start(i, False, False)

        close_button.connect("clicked", self.close_tab, tab_child)
        close_button.set_image(image)
        close_button.set_relief(gtk.RELIEF_NONE)
        tab_box.pack_start(label, True, True)
        tab_box.pack_end(close_button, False, False)

        tab_box.show_all()
        if title in ['Loading dasm...', 'Code', 'Callgraph', 'Flowgraph', 'Interactive', 'Strings', 'Strings repr', 'Hexdump', 'Bindiff', 'Elements', 'File info']:
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
