#       strings_textview.py
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

class StringsTextView(gtk.VBox, Searchable):
    '''Strings TextView elements'''

    def __init__(self, core, textviews):
        super(StringsTextView,self).__init__(False, 1)

        #################################################################
        # Right Textview
        #################################################################

        self.uicore = core
        self.textviews = textviews

        self.press_coords = []

        # Use GtkSourceView to add eye candy :P
        # create buffer
        lm = gtksourceview2.LanguageManager()
        # Add ui dir to language paths
        paths = lm.get_search_path()
        paths.append(os.path.dirname(__file__) + os.sep + 'data' + os.sep)
        lm.set_search_path(paths)
        self.buffer = gtksourceview2.Buffer()
        self.buffer.create_tag("green-background", background="green", foreground="black")
        self.buffer.set_data('languages-manager', lm)
        self.view = gtksourceview2.View(self.buffer)
        self.view.connect("button-press-event", self._get_press)
        self.view.connect("button-release-event", self._get_release)

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
        self.strings_scrolled_window = gtk.ScrolledWindow()
        self.strings_scrolled_window.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        self.strings_scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.strings_scrolled_window.show()
        # Add Textview to Scrolled Window
        self.strings_scrolled_window.add(self.view)
        self.pack_start(self.strings_scrolled_window, expand=True, fill=True)

        # Create the search widget
        Searchable.__init__(self, self.view, small=True)

        # Used for code navidation on _search function
        self.match_start = None
        self.match_end = None
        self.search_string = ''

    def add_content(self):
        strings = self.uicore.get_strings()
        self.buffer.set_text(strings)

    def remove_content(self):
        self.buffer.set_text('')

    def _get_press(self, widget, event):
        x, y = event.get_coords()
        self.press_coords = [x, y]

    def _get_release(self, widget, event):
        x, y = event.get_coords()
        if [x, y] == self.press_coords:
            self._get_clicked_word()

    def _get_clicked_word(self):
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

        self.textviews.right_textview._search(text[soffset:eoffset])
        if self.uicore.backend == 'radare':
            self.nb = self.textviews.right_notebook
            num = self.nb.page_num(self.textviews.right_textview)
            self.nb.set_current_page(num)
