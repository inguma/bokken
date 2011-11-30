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

import os
import gio
import platform

import gtk
import gtksourceview2

#import ui.rightcombo as rightcombo
import ui.treeviews as treeviews
import ui.rightnotebook as rightnotebook
import ui.right_textview as right_textview
import ui.strings_textview as strings_textview
import ui.repr_textview as repr_textview
import ui.hexdump_view as hexdump_view
import ui.interactive_textview as interactive_textview
import ui.bindiff as bindiff
import ui.html_tree as html_tree
import ui.info_tree as info_tree
import ui.left_buttons as left_buttons

'''
Layout:

---------------------------- HBox ------------------------------
Left Buttons | ---------------------Paned ----------------------
             | Left Treeview | ----------- Notebook ------------
'''

class TextViews(gtk.HBox):
    '''Main TextView elements'''

    def __init__(self, core, main):
        super(TextViews,self).__init__(False, 1)

        self.uicore = core
        self.main = main

        self.match_start = None
        self.match_end = None

        #################################################################
        # Main HBox (self) and HPaned
        #################################################################

        # Left and right Vertical Boxes
        self.left_paned = gtk.HPaned()
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
        self.left_scrolled_window = gtk.ScrolledWindow()
        self.left_scrolled_window.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        self.left_scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
#        self.left_scrolled_window.set_size_request(100, 1)
        self.left_scrolled_window.show()

        # Create left TreeView
        self.left_treeview = treeviews.TreeViews(self.uicore, self)

        self.left_scrolled_window.add(self.left_treeview)
        self.left_paned.pack1(self.left_scrolled_window, True, True)

        #################################################################
        # Right Textview
        #################################################################

        self.right_textview = right_textview.RightTextView(self.uicore, self, self.main)
        self.buffer = self.right_textview.buffer
        self.view = self.right_textview.view
        self.mgr = self.right_textview.mgr

        #################################################################
        # Right Interactive Textview
        #################################################################

        self.interactive_textview = interactive_textview.InteractiveTextView(self.uicore)
        self.interactive_buffer = self.interactive_textview.buffer
        self.interactive_view = self.interactive_textview.view
        self.interactive_mgr = self.interactive_textview.mgr

        #################################################################
        # Hexdump Textview
        #################################################################
        self.hexdump_view = hexdump_view.HexdumpView(self.uicore)

        #################################################################
        # Strings Textview
        #################################################################

        self.strings_textview = strings_textview.StringsTextView(self.uicore, self)
        self.strings_buffer = self.strings_textview.buffer
        self.strings_view = self.strings_textview.view
        self.strings_mgr = self.strings_textview.mgr

        #################################################################
        # Repr Textview
        #################################################################

        self.repr_textview = repr_textview.ReprTextView(self.uicore, self)
        self.repr_buffer = self.repr_textview.buffer
        self.repr_view = self.repr_textview.view
        self.repr_mgr = self.repr_textview.mgr

        #################################################################
        # Bindiff widget
        #################################################################

        self.bindiff_widget = bindiff.Bindiff(self.uicore, self)
        self.bindiff = self.bindiff_widget.dw

        #################################################################
        # HTML elements widget
        #################################################################

        self.html_widget = html_tree.HtmlWindow(self.uicore)

        #################################################################
        # Full file info widget
        #################################################################

        self.info_widget = info_tree.InfoWindow(self.uicore)

        #################################################################
        # Right NoteBook
        #################################################################
        self.right_notebook = rightnotebook.RightNotebook(self, self.right_textview, \
                              self.strings_textview, self.repr_textview, self.interactive_textview, \
                              self.bindiff, self.html_widget, self.info_widget, self.uicore, self.main)

        # Add notebook to the paned
        self.left_paned.pack2(self.right_notebook, True, True)
        self.right_notebook.show()

    def update_lefttext(self, text):
        self.leftbuffer.set_text(text)

    def update_theme(self, theme):
        theme = theme.lower()
        style_scheme = self.mgr.get_scheme(theme)
        self.buffer.set_style_scheme(style_scheme)
        self.strings_buffer.set_style_scheme(style_scheme)
        self.repr_buffer.set_style_scheme(style_scheme)
        self.interactive_buffer.set_style_scheme(style_scheme)
        self.hexdump_view.update_theme(style_scheme)

    def update_righttext(self, option):
        self.dasm = ''
        # Fill right textview with selected content
        if option in ['Disassembly', 'Hexdump', 'Program']:
            # We don't want dasm and graph for not analyzed programs or other files
            if option != 'Hexdump':
                if self.uicore.backend == 'radare' and platform.system() != 'Windows':
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

            # Load hexdump, strings and strings repr
            self.hexdump = self.uicore.get_full_hexdump()
            self.strings = self.uicore.get_strings()
            self.repr = self.uicore.get_repr()

        elif option == 'Python':
            self.dasm = self.uicore.get_python_dasm()
        elif option == 'URL':
            self.uicore.core.bsize = self.uicore.core.maxsize
            self.uicore.core.seek(0)
            language = 'http'
            try:
                code = "%s" % ( self.format_html(self.uicore.core.buf) )
            except:
                code = unicode(self.uicore.core.buf, 'iso8859-15')
            self.uicore.core.bsize = 512
            print "set text to buffer"
            self.buffer.set_text(code)
            self.right_notebook.xdot_box.set_dot(self.uicore.http_dot)
            self.hexdump = self.uicore.get_full_hexdump()
            self.hexdump_view.set_hexdump(self.hexdump)
        elif option == 'Plain Text':
            language = self.get_language()
            data = self.uicore.get_file_text()

            if language:
                self.buffer.set_language(language)
                self.buffer.set_text(data)
            else:
                self.dasm = self.uicore.get_fulldasm()
                self.buffer.set_text(self.dasm)
                self.uicore.core.format = 'Hexdump'
                option = 'Disassembly'

        # Highlight syntax just for 'Disassembly', 'URL' 'Program' and 'Plain text'
        if option in ['Disassembly', 'URL', 'Plain Text', 'Python', 'Program']:
            self.buffer.set_highlight_syntax(True)
        else:
            self.buffer.set_highlight_syntax(False)

        # Wrap text only for 'String Repr'
        if option != 'String Repr':
            self.view.set_wrap_mode(gtk.WRAP_NONE)
        else:
            self.view.set_wrap_mode(gtk.WRAP_WORD)

        # Hide left content for 'Plain Text'
        if self.uicore.core.format not in ['Plain Text', 'Hexdump']:
            self.left_scrolled_window.show()
        else:
            self.left_scrolled_window.hide()
        if self.uicore.core.format == 'URL':
            self.right_notebook.add_html_elements_tab()

        #self.update_tabs(option)

    def update_dasm(self, dasm):
        self.buffer.set_text(dasm)
        self.right_textview.setup_sections_bar()

    def update_interactive(self):
        #print "[*] Update interacive"
        if self.uicore.backend == 'pyew':
            self.uicore.core.offset = 0
        elif self.uicore.backend == 'radare':
            self.uicore.core.cmd0('e io.va=0')

        dump = self.uicore.get_hexdump()
        self.interactive_buffer.set_text(dump)

    def create_completion(self):
        self.interactive_textview.interactive_buttons.set_completion()
        self.right_textview.set_completion()

    def format_html(self, code):
        import tidy
        # Tidy options reference: http://tidy.sourceforge.net/docs/quickref.html
        options = dict(output_xhtml=1, add_xml_decl=1, indent=1, tidy_mark=0, output_encoding='UTF8', wrap=0)
        code = tidy.parseString(code, **options)
        return code

    def create_model(self, mode):
        # Clear before changing contents
        self.left_treeview.store.clear()
        self.left_treeview.remove_columns()

        if mode == 'Functions':
            self.left_treeview.create_functions_columns()
            for function in self.uicore.get_functions():
                if function in ["fcn", "sub"]:
                    self.left_treeview.store.append([self.left_treeview.fcn_pix, function, '', '', ''])
                elif "loc" in function:
                    self.left_treeview.store.append([self.left_treeview.bb_pix, function, '', '', ''])
                else:
                    self.left_treeview.store.append([self.left_treeview.fcn_pix, function, '', '', ''])
        elif mode == 'Sections':
            self.left_treeview.create_sections_columns()
            execs = [x[0] for x in self.uicore.execsections]
            if self.uicore.backend == 'pyew' and self.uicore.core.format != 'ELF':
                execs = [x[0] for x in execs]
            for section in self.uicore.get_sections():
                if section[0] in execs:
                    tmp = [self.left_treeview.fcn_pix]
                else:
                    tmp = [self.left_treeview.data_sec_pix]
                for element in section:
                    tmp.append(element)
                self.left_treeview.store.append(tmp)
        elif mode == 'Imports':
            # FIXME horrible...
            # We have different import format for PE or Elf
            if self.uicore.backend == 'radare':
                if 'elf' in self.uicore.info.rclass:
                    self.left_treeview.create_tree( self.uicore.get_elf_imports() )
                else:
                    self.left_treeview.create_tree( self.uicore.get_imports() )
            else:
                self.left_treeview.create_tree( self.uicore.get_imports() )
        elif mode == 'Exports':
            self.left_treeview.create_exports_columns()
            for export in self.uicore.get_exports():
                if len(export) < 5:
                    export.insert(0, self.left_treeview.exp_pix)
                self.left_treeview.store.append(export)
        elif mode == 'PDF':
            self.left_treeview.create_pdf_tree( self.uicore.get_pdf_info() )
        elif mode == 'URL':
            self.left_treeview.create_url_tree( self.uicore.parsed_links )
        elif mode == 'Headers':
            self.left_treeview.create_url_headers( self.uicore.url_headers )
        elif mode == 'Cookies':
            self.left_treeview.create_cookies_tree( self.uicore.url_cookies )

    def _hide_tb_toggled(self, widget):
        if widget.get_active():
            self.main.topbuttons.hide()
            self.main.mbar.hide()
            i = gtk.Image()
            i.set_from_stock(gtk.STOCK_GO_DOWN, gtk.ICON_SIZE_MENU)
            widget.set_image(i)
        else:
            self.main.topbuttons.show()
            self.main.mbar.show()
            i = gtk.Image()
            i.set_from_stock(gtk.STOCK_GO_UP, gtk.ICON_SIZE_MENU)
            widget.set_image(i)

    def update_left_buttons(self):
        # TODO: Empty the buttons to create new ones on new file open

        # Add combo content depending on file format
        if self.uicore.core.format in ['PE', 'Program']:
            options = 'full_bin'
        elif self.uicore.core.format in ['ELF']:
            # Pyew doesn't has support for Elf Imports/Exports parsing
            if 'pyew' in self.uicore.backend:
                options = 'half_bin'
            else:
                options = 'full_bin'
        elif self.uicore.core.format in ['PDF']:
            options = 'pdf'
        elif self.uicore.core.format in ['URL']:
            options = 'url'
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
            res = start.forward_search(self.search_string, gtk.TEXT_SEARCH_TEXT_ONLY)

            # Search 'function_name' instead of 'FUNCTION function_name'
            if not res and 'FUNCTION' in self.search_string:
                self.search_function_name = self.search_string.split()[1]
                res = start.forward_search(self.search_function_name, gtk.TEXT_SEARCH_TEXT_ONLY)
            # Try lowercase search
            elif not res:
                self.search_lower_string = self.search_string.lower()
                res = start.forward_search(self.search_lower_string, gtk.TEXT_SEARCH_TEXT_ONLY)

            if res:
                # Remove previous marks if exist
                if self.match_start != None and self.match_end != None:
                    self.buffer.remove_tag_by_name('green-background', self.match_start, self.match_end)
                self.match_start, self.match_end = res
                self.buffer.place_cursor(self.match_start)
                #self.view.scroll_to_iter(self.match_start, 0, False, 0, 0)
                mark = self.buffer.create_mark(None, self.match_start, False)
                self.view.scroll_to_mark(mark, 0.0, True, 0, 0.03)
                self.last_search_iter = self.match_end
                self.buffer.apply_tag_by_name('green-background', self.match_start, self.match_end)
                self.right_textview.marks.append([self.match_start, self.match_end])

                self.right_textview.seek_index += 1
                self.right_textview.seeks.insert(self.right_textview.seek_index, [self.match_start, self.match_end])
                #print "Anadida nueva entrada en el indice %d" % self.right_textview.seek_index
                return True

            else:
                self.search_string = None      
                self.last_search_iter = None
                return False

    def get_language(self):
        if 'http' in self.uicore.core.filename:
            language = 'http'
        else:
            if os.path.isabs(self.uicore.core.filename):
                path = self.uicore.core.filename
            else:
                path = os.path.abspath(self.uicore.core.filename)
            f = gio.File(path)
        
            path = f.get_path()
        
            info = f.query_info("*")
    
            mime_type = info.get_content_type()
            language = None
        
            if mime_type:
                language = self.get_language_for_mime_type(mime_type)
                if not language:
                    print 'No language found for mime type "%s"' % mime_type
            else:
                print 'Couldn\'t get mime type for file "%s"' % self.uicore.core.filename
    
            #self.buffer.set_language(language)

        return language

    ######################################################################
    ##### Note this function is silly and wrong, because it ignores mime
    ##### parent types and subtypes.
    def get_language_for_mime_type(self, mime):
        lang_manager = gtksourceview2.language_manager_get_default()
        lang_ids = lang_manager.get_language_ids()
        for i in lang_ids:
            lang = lang_manager.get_language(i)
            for m in lang.get_mime_types():
                if m == mime:
                    return lang
        return None

