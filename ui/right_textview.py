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

import ui.sections_bar as sections_bar
from ui.searchable import Searchable

class RightTextView(gtk.VBox, Searchable):
    '''Right TextView elements'''

    def __init__(self, core, textviews):
        super(RightTextView,self).__init__(False, 1)

        #################################################################
        # Right Textview
        #################################################################

        self.uicore = core
        self.textviews = textviews

        self.seek_index = 0
        self.seeks = []

        #################################################
        # Move buttons
        self.move_buttons = self.create_seek_buttons()
        self.pack_start(self.move_buttons, False, False, 1)

        self.sec_bar = sections_bar.SectionsBar(self.uicore)
        self.hbox = gtk.HBox(False, 0)

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
        self.hbox.pack_start(self.right_scrolled_window, expand=True, fill=True)
        self.hbox.pack_start(self.sec_bar, False, False, 0)
        self.pack_start(self.hbox, expand=True, fill=True)

        # Create the search widget
        Searchable.__init__(self, self.view, small=True)

        # Setup sections bar
        vscrollbar = self.right_scrolled_window.get_vscrollbar()
        self.sec_bar.setup(vscrollbar)

        # Used for code navidation on _search function
        self.match_start = None
        self.match_end = None
        self.search_string = ''

    def do_seek(self, widget, direction):
        if self.seek_index <= 1 and direction == 'b':
            pass
        elif self.seek_index == len(self.seeks) and direction == 'f':
            pass
        else:
            if direction == 'b':
                self.seek_index -= 1
            elif direction == 'f':
                self.seek_index += 1
            #print "Nuevo indice %d" % self.seek_index

            #print "Me muevo al indice %d de %d" % (self.seek_index-1, self.seek_index)
            mark = self.buffer.create_mark(None, self.seeks[self.seek_index-1], False)
            self.view.scroll_to_mark(mark, 0.0, True, 0, 0.03)
            #self.view.scroll_to_iter(self.seeks[self.seek_index-1], 0, True, 0, 0)

    def set_completion(self):
        # Seek entry EntryCompletion
        self.completion = gtk.EntryCompletion()
        self.liststore = gtk.ListStore(str)
        # Add function names to the list
        for function in self.uicore.allfuncs:
            self.liststore.append([function])

        self.completion.set_model(self.liststore)
        self.seek.set_completion(self.completion)
        self.completion.set_text_column(0)

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
#        if self.uicore.backend == 'radare':
#            self.textviews.update_graph(self, text[soffset:eoffset])

    def create_seek_buttons(self):
        self.hbox = gtk.HBox(False, 1)

        self.back = gtk.Button()
        self.back_img = gtk.Image()
        self.back_img.set_from_stock(gtk.STOCK_GO_BACK, gtk.ICON_SIZE_MENU)
        self.back.set_image(self.back_img)
        self.back.connect('clicked', self.do_seek, 'b')

        self.forward = gtk.Button()
        self.forward_img = gtk.Image()
        self.forward_img.set_from_stock(gtk.STOCK_GO_FORWARD, gtk.ICON_SIZE_MENU)
        self.forward.set_image(self.forward_img)
        self.forward.connect('clicked', self.do_seek, 'f')

        self.seek = gtk.Entry(30)
        self.seek.set_icon_from_stock(1, gtk.STOCK_JUMP_TO)
        self.seek.set_activates_default(True)
        self.seek.connect("activate", self.goto)
        self.seek.connect("icon-press", self.goto)
        self.seek.set_icon_tooltip_text(1, 'Go')

        self.hbox.pack_start(self.back, False, False)
        self.hbox.pack_start(self.forward, False, False)
        self.hbox.pack_start(self.seek, True, True)

        return self.hbox

    def goto(self, widget, icon_pos=None, event=None):
        text = self.seek.get_text()
        self._search(text)

    def _search(self, search_string, iter = None):

        self.dograph = False
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
                self.dograph = True
            elif 'imp.' in search_string:
                self.search_string = "0x%08x" % self.uicore.core.num.get(search_string)
            elif 'reloc.' in search_string:
                self.search_string = "0x%08x" % self.uicore.core.num.get(search_string)
            elif 'sub_' in search_string:
                self.search_string = '0x' + search_string[4:]
            elif '.' in search_string:
                if '[' in search_string:
                    search_string = search_string.strip('[').strip(']')
                if self.uicore.backend == 'radare':
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
                            #self.view.scroll_to_iter(self.match_start, 0, True, 0, 0)
                            mark = self.buffer.create_mark(None, self.match_start, False)
                            self.view.scroll_to_mark(mark, 0.0, True, 0, 0.03)
                            self.last_search_iter = self.match_end
                            self.buffer.apply_tag_by_name('green-background', self.match_start, self.match_end)

                    # Update seeks
                    if self.match_start != self.seeks[-1]:
                        self.seeks.insert(self.seek_index, self.match_start)
                        self.seek_index += 1
                        if len(self.seeks) != self.seek_index:
                            self.seeks = self.seeks[:self.seek_index]
    
                else:
                    self.search_string = None      
                    self.last_search_iter = None
                if self.uicore.backend == 'radare' and self.dograph:
                    self.textviews.update_graph(self, self.search_string)
