#!/usr/bin/python

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

import gtk
import gtksourceview2

import ui.rightcombo as rightcombo
import ui.treeviews as treeviews
import ui.rightnotebook as rightnotebook
import ui.right_textview as right_textview
import ui.interactive_textview as interactive_textview

class TextViews(gtk.HBox):
    '''Main TextView elements'''

    def __init__(self, core):
        super(TextViews,self).__init__(False, 1)

        self.uicore = core

        self.match_start = None
        self.match_end = None

        #################################################################
        # Main HBox (self) and VBoxes
        #################################################################

        # Left and right Vertical Boxes
        self.leftvb = gtk.VBox(False, 1)
        rightvb = gtk.VBox(False, 1)
        self.pack_start(self.leftvb, True, True, 1)
        self.pack_start(rightvb, True, True, 1)

        #################################################################
        # Left ListView and TreeView
        #################################################################

        # Scrolled Window
        left_scrolled_window = gtk.ScrolledWindow()
        left_scrolled_window.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        left_scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        left_scrolled_window.show()

        # Create left TreeView
        self.left_treeview = treeviews.TreeViews(self.uicore, self)

        left_scrolled_window.add(self.left_treeview)

        #################################################################
        # Left ComboBox
        #################################################################
        self.left_combo = gtk.combo_box_new_text()
        # Set grayed by default
        self.left_combo.set_sensitive(False)
        self.connect = self.left_combo.connect("changed", self.update_left_content)

        # Add combo and textview to leftvb
        self.leftvb.pack_start(self.left_combo, False, True, 2)
        self.leftvb.pack_start(left_scrolled_window, True, True, 2)

        #################################################################
        # Right Textview
        #################################################################

        self.right_textview = right_textview.RightTextView()
        self.buffer = self.right_textview.buffer
        self.view = self.right_textview.view
        self.mgr = self.right_textview.mgr

        #################################################################
        # Right ComboBox
        #################################################################
        self.right_combo = rightcombo.RightCombo(self, self.uicore)

        #################################################################
        # Right Interactive Textview
        #################################################################

        self.interactive_textview = interactive_textview.InteractiveTextView(self.uicore)
        self.interactive_buffer = self.interactive_textview.buffer
        self.interactive_view = self.interactive_textview.view
        self.interactive_mgr = self.interactive_textview.mgr

        #################################################################
        # Right NoteBook
        #################################################################
        self.right_notebook = rightnotebook.RightNotebook(self, self.right_textview, self.interactive_textview, self.uicore)
        #self.right_notebook = rightnotebook.RightNotebook(self, self.right_scrolled_window, self.uicore)

        # Add combo and textview to rightvb
        rightvb.pack_start(self.right_combo, False, True, 2)
        #rightvb.pack_start(self.right_scrolled_window, True, True, 2)
        rightvb.pack_start(self.right_notebook, True, True, 2)
        self.right_notebook.show_all()

    def update_lefttext(self, text):
        self.leftbuffer.set_text(text)

    def update_theme(self, theme):
        theme = theme.lower()
        style_scheme = self.mgr.get_scheme(theme)
        self.buffer.set_style_scheme(style_scheme)
        self.interactive_buffer.set_style_scheme(style_scheme)

    def update_righttext(self, option):
        # Fill right textview with selected content
        if option == 'Disassembly':
            #self.uicore.get_sections()
            try:
                self.dasm = self.uicore.get_text_dasm()
            except:
                self.dasm = self.uicore.get_fulldasm()
            try:
                self.right_notebook.xdot_widget.set_dot(self.uicore.get_callgraph())
            except:
                pass

            self.buffer.set_text(self.dasm)
        elif option == 'Python':
            self.dasm = self.uicore.get_python_dasm()
        elif option == 'String Repr':
            self.repr = self.uicore.get_repr()
            self.buffer.set_text(self.repr)
        elif option == 'Hexdump':
            self.hexdump = self.uicore.get_full_hexdump()
            self.buffer.set_text(self.hexdump)
        elif option == 'Strings':
            self.strings = self.uicore.get_strings()
            self.buffer.set_text(self.strings)
        elif option == 'URL':
            language = 'http'
            try:
                code = "%s" % ( self.format_html(self.uicore.pyew.buf) )
            except:
                code = unicode(self.uicore.pyew.buf, 'iso8859-15')
                #code = self.uicore.pyew.buf
            self.buffer.set_text(code)
            self.right_notebook.xdot_widget.set_dot(self.uicore.http_dot)
        elif option == 'Plain Text':
            language = self.get_language()
            data = self.uicore.get_file_text()

            if language:
                self.buffer.set_text(data)
            else:
                self.buffer.set_highlight_syntax(False)
                #self.buffer.set_text('This is not a plain text file, could not show :(')
                self.uicore.format = 'Hexdump'
                option = 'Hexdump'
                self.buffer.set_highlight_syntax(False)
                self.hexdump = self.uicore.get_full_hexdump()
                self.buffer.set_text(self.hexdump)

        # Highlight syntax just for 'Disassembly', 'URL' and 'Plain text'
        if option in ['Disassembly', 'URL', 'Plain Text', 'Python']:
            self.buffer.set_highlight_syntax(True)
        else:
            self.buffer.set_highlight_syntax(False)

        # Wrap text only for 'String Repr'
        if option != 'String Repr':
            self.view.set_wrap_mode(gtk.WRAP_NONE)
        else:
            self.view.set_wrap_mode(gtk.WRAP_WORD)

        # Hide left content for 'Plain Text'
        if option != 'Plain Text':
            self.leftvb.show()
        else:
            self.leftvb.hide()

        self.update_tabs(option)

    def update_interactive(self):
        self.uicore.pyew.offset = 0
        dump = self.uicore.pyew.hexdump(self.uicore.pyew.buf, self.uicore.pyew.hexcolumns)
        self.interactive_buffer.set_text(dump)

    def update_right_combo(self):
        self.right_combo.create_options()

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
                self.left_treeview.store.append([function, '', '', ''])
        elif mode == 'Sections':
            self.left_treeview.create_sections_columns()
            for section in self.uicore.get_sections():
                tmp = []
                for element in section:
                    tmp.append(element)
                self.left_treeview.store.append(tmp)
        elif mode == 'Imports':
            self.left_treeview.create_tree( self.uicore.get_imports() )
        elif mode == 'Exports':
            self.left_treeview.create_exports_columns()
            for export in self.uicore.get_exports():
                self.left_treeview.store.append(export)
        elif mode == 'PDF':
            self.left_treeview.create_pdf_tree( self.uicore.get_pdf_info() )
        elif mode == 'URL':
            self.left_treeview.create_url_tree( self.uicore.parsed_links )

    def update_tabs(self, mode):
        if mode == 'Disassembly':
            self.right_notebook.set_show_tabs(True)
        elif mode == 'URL':
            self.right_notebook.set_show_tabs(True)
        else:
            self.right_notebook.set_show_tabs(False)
            self.right_notebook.set_current_page(0)

    def update_left_content(self, widget):
        model = self.left_combo.get_model()
        active = self.left_combo.get_active()
        option = model[active][0]
        self.create_model(option)

    def update_left_combo(self):
        self.left_combo.disconnect(self.connect)
        # Empty the combo before adding new contents
        model = self.left_combo.get_model()
        model.clear()

        # Add combo content depending on file format
        if self.uicore.pyew.format in ['PE']:
            options = ['Functions', 'Sections', 'Imports', 'Exports']
        elif self.uicore.pyew.format in ['ELF']:
            options = ['Functions', 'Sections']
        elif self.uicore.pyew.format in ['PDF']:
            options = ['PDF Info']
        elif self.uicore.pyew.format in ['URL']:
            options = ['Links']
        else:
            options = ['']

        for option in options:
            self.left_combo.append_text(option)
        # Set First element by default
        self.left_combo.set_active(0)

        self.connect = self.left_combo.connect("changed", self.update_left_content)

        self.left_combo.set_sensitive(True)
        # FIXME: Really necessary?? looks like not...
#        self.update_left_content(self)

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
                self.view.scroll_to_iter(self.match_start, 0, False, 0, 0)
                self.last_search_iter = self.match_end
                self.buffer.apply_tag_by_name('green-background', self.match_start, self.match_end)

            else:
                self.search_string = None      
                self.last_search_iter = None

    def get_language(self):
        if 'http' in self.uicore.pyew.filename:
            language = 'http'
        else:
            if os.path.isabs(self.uicore.pyew.filename):
                path = self.uicore.pyew.filename
            else:
                path = os.path.abspath(self.uicore.pyew.filename)
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
                print 'Couldn\'t get mime type for file "%s"' % self.uicore.pyew.filename
    
            self.buffer.set_language(language)

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


