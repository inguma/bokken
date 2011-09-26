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

import gtk

import ui.graph as graph

class RightNotebook(gtk.Notebook):
    '''Right Notebook elements'''

    def __init__(self, tviews, scrolled_window, strings_textview, repr_textview, interactive_scrolled, uicore):
        super(RightNotebook,self).__init__()

        self.tviews = tviews
        self.scrolled_window = scrolled_window
        self.strings_textview = strings_textview
        self.repr_textview = repr_textview
        self.interactive_scrolled = interactive_scrolled
        self.hexdump_view = self.tviews.hexdump_view
        self.uicore = uicore

        #################################################
        # Code view TAB
        self.append_page(self.scrolled_window)
        tab = self.create_tab('Code', self.scrolled_window)

        self.set_tab_label_packing(self.scrolled_window, False, False, gtk.PACK_START)
        self.set_tab_label(self.scrolled_window, tab)

        #################################################
        # Graph map TAB
        self.xdot_widget = graph.MyDotWidget(self.uicore)
        self.append_page(self.xdot_widget)

        if self.uicore.backend == 'pyew':
            label = 'Callgraph'
        else:
            label = 'Graph'

        tab = self.create_tab(label, self.xdot_widget)

        self.set_tab_label_packing(self.xdot_widget, False, False, gtk.PACK_START)
        self.set_tab_label(self.xdot_widget, tab)

        #################################################
        # Hexdump TAB
        self.append_page(self.hexdump_view)
        tab = self.create_tab('Hexdump', self.hexdump_view)

        self.set_tab_label_packing(self.hexdump_view, False, False, gtk.PACK_START)
        self.set_tab_label(self.hexdump_view, tab)

        #################################################
        # Strings view TAB
        self.append_page(self.strings_textview)
        tab = self.create_tab('Strings', self.strings_textview)

        self.set_tab_label_packing(self.strings_textview, False, False, gtk.PACK_START)
        self.set_tab_label(self.strings_textview, tab)

        #################################################
        # Repr view TAB
        self.append_page(self.repr_textview)
        tab = self.create_tab('Strings repr', self.repr_textview)

        self.set_tab_label_packing(self.repr_textview, False, False, gtk.PACK_START)
        self.set_tab_label(self.repr_textview, tab)

        #################################################
        # Interactive view TAB
        self.append_page(self.interactive_scrolled)
        tab = self.create_tab('Interactive', self.interactive_scrolled)

        self.set_tab_label_packing(self.interactive_scrolled, False, False, gtk.PACK_START)
        self.set_tab_label(self.interactive_scrolled, tab)

        #################################################
        # Move buttons
        self.move_buttons = self.create_seek_buttons()
        #self.set_action_widget(self.move_buttons, gtk.PACK_END)
        #self.move_buttons.show_all()

        self.connect("switch-page", self.on_switch)

        # Hide callgraph for URL, Plain Text and PDF
        if self.uicore.core.format in ['URL', 'Plain Text', 'PDF']:
            self.remove_page(1)

    def on_switch(self, notebook, page, page_num):
        # Tabs to avoid
        avoid = [
                self.page_num(self.scrolled_window),
                self.page_num(self.xdot_widget),
                self.page_num(self.interactive_scrolled)
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

    def hide_tabs(self):
        self.set_show_tabs(False)
        self.set_current_page(0)

    def create_tab(self, title, tab_child):
        tab_box = gtk.HBox()
        close_button = gtk.Button()

        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU)

        label = gtk.Label(title)

        close_button.connect("clicked", self.close_tab, tab_child)
        close_button.set_image(image)
        close_button.set_relief(gtk.RELIEF_NONE)
        tab_box.pack_start(label, True, True)
        tab_box.pack_end(close_button, False, False)

        tab_box.show_all()
        if title in ['Code', 'Callgraph', 'Graph', 'Interactive', 'Strings', 'Strings repr', 'Hexdump']:
            close_button.hide()

        return tab_box

    def close_tab(self, widget, child):
        pagenum = self.page_num(child)

        if pagenum != -1:
            self.remove_page(pagenum)
            child.destroy()

        child.destroy()

    def create_seek_buttons(self):
        self.vbox = gtk.HBox(False, 1)

        self.back = gtk.Button()
        self.back_img = gtk.Image()
        self.back_img.set_from_stock(gtk.STOCK_GO_BACK, gtk.ICON_SIZE_MENU)
        self.back.set_image(self.back_img)

        self.forward = gtk.Button()
        self.forward_img = gtk.Image()
        self.forward_img.set_from_stock(gtk.STOCK_GO_FORWARD, gtk.ICON_SIZE_MENU)
        self.forward.set_image(self.forward_img)

        self.seek = gtk.Entry(10)
        self.seek.set_icon_from_stock(1, gtk.STOCK_JUMP_TO)

        self.vbox.pack_start(self.back, False, False)
        self.vbox.pack_start(self.forward, False, False)
        self.vbox.pack_start(self.seek, False, False)

        return self.vbox
