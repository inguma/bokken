#       textviews.py
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

#import ui.rightcombo as rightcombo
import ui.treeviews as treeviews
import ui.rightnotebook as rightnotebook
import ui.console_textview as console_textview
import ui.python_textview as python_textview
import ui.right_textview as right_textview
import ui.strings_treeview as strings_treeview
import ui.sections_treeview as sections_treeview
import ui.hexdump_view as hexdump_view
import ui.bindiff as bindiff
import ui.info_tree as info_tree
import ui.left_buttons as left_buttons
from lib.common import datafile_path

'''
Layout:

---------------------------- HBox ------------------------------
Left Buttons | ---------------------Paned ----------------------
             | Left Treeview | ----------- Notebook ------------
             |               | ------------- Paned -------------
             |               | ------------ Console ------------
'''

class TextViews(Gtk.HBox):
    '''Main TextView elements'''

    def __init__(self, main):
        super(TextViews,self).__init__(False, 1)

        self.main = main
        self.uicore = self.main.uicore

        self.match_start = None
        self.match_end = None

        #################################################################
        # Main HBox (self) and HPaned
        #################################################################

        # Left and right Vertical Boxes
        self.left_paned = Gtk.HPaned()
        self.left_paned.set_position(125)

        #################################################################
        # Left mini-toolbar
        #################################################################

        self.left_buttons = left_buttons.LeftButtons(self.main)

        self.pack_start(self.left_buttons, False, False, 1)
        self.pack_start(self.left_paned, True, True, 1)

        #################################################################
        # Left ListView and TreeView
        #################################################################

        # Scrolled Window
        self.left_scrolled_window = Gtk.ScrolledWindow()
        self.left_scrolled_window.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        self.left_scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
#        self.left_scrolled_window.set_size_request(100, 1)
        self.left_scrolled_window.show()

        # Create left TreeView
        self.left_treeview = treeviews.TreeViews(self.uicore, self)

        self.left_scrolled_window.add(self.left_treeview)
        self.left_paned.pack1(self.left_scrolled_window, True, True)

        #################################################################
        # Right Textview
        #################################################################

        self.right_textview = right_textview.RightTextView(self.main)
        self.buffer = self.right_textview.buffer
        self.view = self.right_textview.view
        self.mgr = self.right_textview.mgr

        #################################################################
        # Hexdump Textview
        #################################################################
        self.hexdump_view = hexdump_view.HexdumpView(self.main)

        #################################################################
        # Strings Treeview
        #################################################################

        self.strings_treeview = strings_treeview.StringsView(self.uicore, self)

        #################################################################
        # Sections Treeview
        #################################################################

        self.sections_treeview = sections_treeview.SectionsView(self.uicore, self)

        #################################################################
        # Bindiff widget
        #################################################################

        self.bindiff_widget = bindiff.Bindiff(self.uicore, self)
        self.bindiff = self.bindiff_widget.dw

        #################################################################
        # Full file info widget
        #################################################################

        self.info_widget = info_tree.InfoWindow(self.uicore)

        #################################################################
        # Right Paned
        #################################################################

        # Paned for the right notebook and the bottom console
        self.right_paned = Gtk.VPaned()
        self.right_paned.set_position(300)

        #################################################################
        # Right NoteBook
        #################################################################
        self.right_notebook = rightnotebook.RightNotebook(self)

        #################################################################
        # Right Paned
        #################################################################

        # Terminals Notebook
        self.term_nb = Gtk.Notebook()
        self.term_nb.set_tab_pos(Gtk.PositionType.LEFT)

        # Console textview
        i = Gtk.Image()
        i.set_from_stock(Gtk.STOCK_EXECUTE, Gtk.IconSize.SMALL_TOOLBAR)
        self.console = console_textview.ConsoleTextView(self.main)

        self.term_nb.insert_page(self.console, i, 0)

        # Python textview
        self.py_pix = Gtk.Image()
        self.py_pix.set_from_file(datafile_path('python-icon.png'))

        self.python = python_textview.PythonTextView(self.main)

        self.term_nb.insert_page(self.python, self.py_pix, 1)

        # Add notebook to the paned
        self.right_paned.pack1(self.right_notebook, True, True)
        self.right_paned.pack2(self.term_nb, True, False)
        self.left_paned.pack2(self.right_paned, True, True)
        self.right_notebook.show()

    def update_lefttext(self, text):
        self.leftbuffer.set_text(text)

    def update_theme(self, theme):
        theme = theme.lower()
        style_scheme = self.mgr.get_scheme(theme)
        self.buffer.set_style_scheme(style_scheme)
        self.console.buffer.set_style_scheme(style_scheme)
        self.hexdump_view.update_theme(style_scheme)
        self.python.buffer.set_style_scheme(style_scheme)
        self.python.py_buffer.set_style_scheme(style_scheme)

    def update_righttext(self, option):
        self.dasm = ''
        # Fill right textview with selected content
        if option in ['Disassembly', 'Hexdump', 'Program']:
            # We don't want dasm and graph for not analyzed programs or other files
            if option != 'Hexdump':
                if platform.system() != 'Windows':
                    from multiprocessing import Process, Queue, Event
                    # These functions are extremely expensive, so we fork a process for them.
                    if self.uicore.allsections:
                        self.main.dasm_callback = self.uicore.get_text_dasm_through_queue
                    else:
                        self.main.dasm_callback = self.uicore.get_fulldasm_through_queue

                    # We fork another process to bypass the GIL because r2/SWIG holds it while inside 'pD'.
                    # We create a queue to receive the dasm result and an event to signal a thread that
                    # the queue is ready to be read.
                    # If the multiprocessing.Queue object is atomic on put(), the Event() won't be necessary.
                    self.main.dasm_event = Event()
                    self.main.dasm_queue = Queue()
                    self.main.dasm_process = Process(target=self.main.dasm_callback, args=(self.main.dasm_queue, self.main.dasm_event))
                    self.main.dasm_process.start()
                else:
                    if self.uicore.allsections:
                        self.uicore.get_text_dasm()
                    else:
                        self.uicore.get_fulldasm()

                try:
                    self.right_notebook.xdot_box.set_dot(self.uicore.get_callgraph())
                except:
                    pass

            # Load hexdump and strings.
            self.hexdump = self.uicore.get_full_hexdump()
            self.strings = self.uicore.get_strings()

        # Highlight syntax just for 'Disassembly', 'URL' 'Program' and 'Plain text'
        if option in ['Disassembly', 'Program']:
            self.buffer.set_highlight_syntax(True)
        else:
            self.buffer.set_highlight_syntax(False)

        self.view.set_wrap_mode(Gtk.WrapMode.WORD)

        # Hide left content for 'Plain Text'
        if self.uicore.core.format not in ['Hexdump']:
            self.left_scrolled_window.show()
        else:
            self.left_scrolled_window.hide()

        #self.update_tabs(option)

    def update_dasm(self, dasm):
        self.buffer.set_text(dasm)
        # MEOW
        #self.right_textview.setup_sections_bar()

    def create_completion(self):
        self.right_textview.set_completion()

    def create_model(self, mode):
        # Clear before changing contents
        self.left_treeview.store.clear()
        self.left_treeview.remove_columns()

        if mode == 'Functions':
            self.left_treeview.create_functions_columns()
            for function in self.uicore.get_functions():
                if function in ["fcn", "sub"]:
                    self.left_treeview.store.append([self.left_treeview.fcn_pix, function, '', '', ''])
                elif "sym." in function:
                    self.left_treeview.store.append([self.left_treeview.bb_pix, function, '', '', ''])
                else:
                    self.left_treeview.store.append([self.left_treeview.fcn_pix, function, '', '', ''])
        elif mode == 'Relocs':
            self.left_treeview.create_relocs_columns()
            for reloc in self.uicore.get_relocs():
                tmp = [self.left_treeview.fcn_pix, reloc[2], reloc[0], reloc[1], '']
                self.left_treeview.store.append(tmp)
        elif mode == 'Imports':
            # FIXME horrible...
            # We have different import format for PE or Elf
            if 'elf' in self.uicore.info.rclass:
                self.left_treeview.create_tree( self.uicore.get_elf_imports() )
            else:
                self.left_treeview.create_tree( self.uicore.get_imports() )
        elif mode == 'Symbols':
            self.left_treeview.create_exports_columns()
            for export in self.uicore.get_exports():
                if len(export) < 5:
                    export.insert(0, self.left_treeview.exp_pix)
                self.left_treeview.store.append(export)

    def _hide_tb_toggled(self, widget):
        if widget.get_active():
            self.main.topbuttons.hide()
            self.main.mbar.hide()
            i = Gtk.Image()
            i.set_from_stock(Gtk.STOCK_GO_DOWN, Gtk.IconSize.MENU)
            widget.set_image(i)
        else:
            self.main.topbuttons.show()
            self.main.mbar.show()
            i = Gtk.Image()
            i.set_from_stock(Gtk.STOCK_GO_UP, Gtk.IconSize.MENU)
            widget.set_image(i)

    def update_left_buttons(self):
        # TODO: Empty the buttons to create new ones on new file open

        # Add combo content depending on file format
        if self.uicore.core.format in ['PE', 'Program']:
            options = 'full_bin'
        elif self.uicore.core.format in ['ELF']:
            options = 'full_bin'
        elif self.uicore.core.format in ['Hexdump']:
            options = ''
        else:
            options = ''

        self.left_buttons.create_buttons(options)

    def update_graph(self, widget, addr):
        if addr:
            addr = addr.split(' ')[-1]
            self.right_notebook.last_fcn = addr
            self.right_notebook.xdot_box.last_fcn = addr
            if self.right_notebook.get_current_page() == 1:
                self.right_notebook.xdot_box.set_dot(self.uicore.get_callgraph(addr))

    def search(self, widget, search_string, iter = None):
        # Clean string to search
        search_string = search_string.strip("\t")

        if iter is None:
            start = self.buffer.get_start_iter()
        else:
            start = iter

        if search_string:
            self.search_string = search_string 
            res = start.forward_search(self.search_string, Gtk.TextSearchFlags.TEXT_ONLY)

            # Search 'function_name' instead of 'FUNCTION function_name'
            if not res and 'FUNCTION' in self.search_string:
                self.search_function_name = self.search_string.split()[1]
                res = start.forward_search(self.search_function_name, Gtk.TextSearchFlags.TEXT_ONLY)
            # Try lowercase search
            elif not res:
                self.search_lower_string = self.search_string.lower()
                res = start.forward_search(self.search_lower_string, Gtk.TextSearchFlags.TEXT_ONLY)

            if res:
                self.match_start, self.match_end = res
                self.buffer.place_cursor(self.match_start)
                #self.view.scroll_to_iter(self.match_start, 0, False, 0, 0)
                mark = self.buffer.create_mark(None, self.match_start, False)
                self.view.scroll_to_mark(mark, 0.0, True, 0, 0.03)
                self.last_search_iter = self.match_end
                self.right_textview.marks.append([self.match_start, self.match_end])

                self.right_textview.seek_index += 1
                self.right_textview.seeks.insert(self.right_textview.seek_index, [self.match_start, self.match_end])
                #print "Anadida nueva entrada en el indice %d" % self.right_textview.seek_index
                return True

            else:
                self.search_string = None      
                self.last_search_iter = None
                return False
