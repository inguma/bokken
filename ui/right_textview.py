#       right_textview.py
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

import gtk, pango
import gtksourceview2

from ui.searchable import Searchable

class RightTextView(gtk.VBox, Searchable):
    '''Right TextView elements'''

    def __init__(self, core):
        super(RightTextView,self).__init__(False, 1)

        #################################################################
        # Right Textview
        #################################################################

        self.uicore = core

        # Use GtkSourceView to add eye candy :P
        # create buffer
        lm = gtksourceview2.LanguageManager()
        # Add ui dir to language paths
        paths = lm.get_search_path()
        paths.append(os.getcwd() + os.sep + 'ui' + os.sep + 'data' + os.sep)
        lm.set_search_path(paths)
        self.buffer = gtksourceview2.Buffer()
        self.buffer.create_tag("green-background", background="green", foreground="black")
        self.buffer.set_data('languages-manager', lm)
        self.view = gtksourceview2.View(self.buffer)
        self.view.connect("button-release-event", self._get_clicked_word)

        # FIXME options must be user selectable (statusbar)
        self.view.set_editable(False)
        self.view.set_highlight_current_line(True)
        # posible values: gtk.WRAP_NONE, gtk.WRAP_CHAR, gtk.WRAP_WORD...
        self.view.set_wrap_mode(gtk.WRAP_NONE)
        
        # setup view
        font_desc = pango.FontDescription('monospace 9')
        if font_desc:
            self.view.modify_font(font_desc)

        self.buffer.set_highlight_syntax(True)
        manager = self.buffer.get_data('languages-manager')
        language = manager.get_language('asm')
        self.buffer.set_language(language)

        self.mgr = gtksourceview2.style_scheme_manager_get_default()

        # Scrolled Window
        self.right_scrolled_window = gtk.ScrolledWindow()
        self.right_scrolled_window.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        self.right_scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.right_scrolled_window.show()
        # Add Textview to Scrolled Window
        self.right_scrolled_window.add(self.view)
        self.pack_start(self.right_scrolled_window, expand=True, fill=True)

        # XXX POC XXX
        #self.right_scrolled_window.get_vadjustment().connect("value-changed", self._miau )

        # Create the search widget
        Searchable.__init__(self, self.view, small=True)

        # Used for code navidation on _search function
        self.match_start = None
        self.match_end = None
        self.search_string = ''

    def _get_clicked_word(self, widget, event):
        # Get textbuffer coordinates from texview ones
        x, y = self.view.get_pointer()
        x, y = self.view.window_to_buffer_coords(gtk.TEXT_WINDOW_WIDGET, x, y)
        # Get text iter and offset at coordinates
        iter = self.view.get_iter_at_location(x, y)
        offset = iter.get_offset()
        # Get complete buffer text
        siter, eiter = self.buffer.get_bounds()
        text = self.buffer.get_text(siter, eiter)

        # Get clicked word
        word_seps = [' ', ',', "\t", "\n", '(', ')']

        # Get end word offset
        temp_offset = offset
        while not text[temp_offset:temp_offset+1] in word_seps:
            temp_offset += 1
        else:
            eoffset = temp_offset

        # Get start word offset
        temp_offset = offset
        while not text[temp_offset-1:temp_offset] in word_seps:
            temp_offset -= 1
        else:
            soffset = temp_offset

        self._search(text[soffset:eoffset])

    def _search(self, search_string, iter = None):

        self.search_string = ''
        if search_string:
            # If is an address, search lines begining by this address
            if '[' in search_string:
                search_string = search_string.strip('[').strip(']')
            if '0x' in search_string:
                integer = int(search_string, 16)
                hex_addr = "0x%08x" % integer
                self.search_string = hex_addr
            elif 'loc.' in search_string:
                self.search_string = "0x%08x" % self.uicore.core.num.get(search_string)
            elif 'fcn.' in search_string:
                self.search_string = "0x%08x" % self.uicore.core.num.get(search_string)
            elif 'imp.' in search_string:
                self.search_string = "0x%08x" % self.uicore.core.num.get(search_string)
            elif 'sub_' in search_string:
                self.search_string = '0x' + search_string[4:]
            elif '.' in search_string:
                if '[' in search_string:
                    search_string = search_string.strip('[').strip(']')
                self.search_string = "0x%08x" % self.uicore.core.num.get(search_string)
#                if 'ELF' in self.uicore.core.format:
#                    self.search_string = '; ' + search_string
#                else:
#                    self.search_string = search_string + ':'
            else:
                pass

            if self.search_string:
                startIter =  self.textbuf.get_start_iter()
                # find the positions where the phrase is found
                res = []
                while True:
                    result = startIter.forward_search(self.search_string, gtk.TEXT_SEARCH_TEXT_ONLY, None)
                    if result:
                        res.append((result[0], result[1]))
                        startIter = result[1]
                    else:
                        break

                if res:
                    # Remove previous marks if exist
                    if self.match_start != None and self.match_end != None:
                        self.buffer.remove_tag_by_name('green-background', self.match_start, self.match_end)
                    for iter in res:
                        if iter[0].get_line_offset() < 16:
                            self.match_start, self.match_end = iter

                        if self.match_start:
                            self.buffer.place_cursor(self.match_start)
                            self.view.scroll_to_iter(self.match_start, 0, True, 0, 0)
                            self.last_search_iter = self.match_end
                            self.buffer.apply_tag_by_name('green-background', self.match_start, self.match_end)
    
                else:
                    self.search_string = None      
                    self.last_search_iter = None
