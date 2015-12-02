# -*- coding: utf-8 -*-
#       right_textview.py
#
#       Copyright 2011 Hugo Teso <hugo.teso@gmail.com>
#       Copyright 2015 David Martínez Moreno <ender@debian.org>
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

from __future__ import print_function

from gi.repository import Gtk
from gi.repository import Pango
from gi.repository import GtkSource

# MEOW
#import ui.sections_bar as sections_bar
import ui.comments_dialog as comments_dialog
import ui.xrefs_menu as xrefs_menu

from ui.searchable import Searchable
from ui.highword import HighWord
from ui.opcodes import *
from lib.highword_helper import *

class RightTextView(Gtk.VBox, Searchable):
    '''Right TextView elements'''

    def __init__(self, main):
        super(RightTextView, self).__init__(False, 1)

        #################################################################
        # Right Textview
        #################################################################

        self.main = main
        self.uicore = self.main.uicore

        self.seek_index = 0
        self.seeks = []
        self.marks = []
        self.press_coords = []

        #################################################
        # Move buttons
        self.move_buttons = self.create_seek_buttons()
        self.pack_start(self.move_buttons, False, False, 1)

        self.hbox = Gtk.HBox(False, 0)

        self.buffer = GtkSource.Buffer()
        self.view = GtkSource.View.new_with_buffer(self.buffer)
        self.view.connect("button-press-event", self._get_press)
        self.view.connect("button-release-event", self._get_release)
        self.view.connect("key-release-event", self._cursor_moved)
        self.view.connect('motion-notify-event', self.call_tooltip)

        # FIXME options must be user selectable (statusbar)
        self.view.set_editable(False)
        self.view.set_highlight_current_line(True)
        # posible values: Gtk.WrapMode.NONE, Gtk.WrapMode.CHAR, Gtk.WrapMode.WORD...
        self.view.set_wrap_mode(Gtk.WrapMode.NONE)

        # setup view
        font_desc = Pango.FontDescription('monospace 9')
        if font_desc:
            self.view.modify_font(font_desc)

        self.buffer.set_highlight_syntax(True)
        if "ARM" in self.uicore.info.machine or "Thumb" in self.uicore.info.machine:
            language = self.main.lm.get_language('arm-asm')
        else:
            language = self.main.lm.get_language('asm')

        self.buffer.set_language(language)

        self.mgr = GtkSource.StyleSchemeManager.get_default()

        # Scrolled Window
        self.right_scrolled_window = Gtk.ScrolledWindow()
        self.right_scrolled_window.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        self.right_scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.right_scrolled_window.show()
        # Add Textview to Scrolled Window
        self.right_scrolled_window.add(self.view)
        self.hbox.pack_start(self.right_scrolled_window, True, True, 0)
        self.pack_start(self.hbox, True, True, 0)

        # Create the search widget
        Searchable.__init__(self, self.view, small=True)

        self.high_word = HighWord(self.view)

        # Used for code navigation on _search function
        self.match_start = None
        self.match_end = None
        self.search_string = ''

        self.view.connect("populate-popup", self._populate_comments_menu)

    def _cursor_moved(self, widget, event):
        cursor = self.buffer.get_iter_at_mark(self.buffer.get_insert())
        start = find_word_bound(cursor, -1, self.buffer)
        end = find_word_bound(cursor, +1, self.buffer)
        word = self.buffer.get_text(start, end, False)
        self.high_word._find(word)

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

            self.marks = []

            mark = self.buffer.create_mark(None, self.seeks[self.seek_index-1][0], False)
            self.view.scroll_to_mark(mark, 0.0, True, 0, 0.03)
            self.marks.append([self.seeks[self.seek_index-1][0], self.seeks[self.seek_index-1][1]])

    def setup_sections_bar(self):
        # Setup sections bar
        # The check is used to avoid duplicated bars
        # when loading a new file from inside bokken
        if not hasattr(self,"sec_bar"):
            # MEOW
            #self.sec_bar = sections_bar.SectionsBar(self.uicore)
            self.hbox.pack_start(self.sec_bar, False, False, 0)
            self.sec_bar.show()
            vscrollbar = self.right_scrolled_window.get_vscrollbar()
            self.sec_bar.setup(vscrollbar)

    def _populate_comments_menu(self, textview, menu):
        '''Populates the context menu with the Comments item.'''
        # Get textbuffer coordinates from textview ones
        x, y = self.view.get_pointer()
        x, y = self.view.window_to_buffer_coords(Gtk.TextWindowType.WIDGET, x, y)
        iter = self.view.get_line_at_y(y)[0]

        line = self.get_line_on_coords(x, y)

        for opcode in instructions.keys():
            if opcode.split(' ')[0].lower() in line or opcode.split(' ')[0] in line:
                # Add a menu entry with opcode information
                opmenu = Gtk.Menu()

                opcodem = Gtk.ImageMenuItem((Gtk.STOCK_INFO))
                opcodem.set_submenu(opmenu)
                opcodem.get_children()[0].set_markup('Opcode info: <b>' + opcode.split(' ')[0].lower() + '</b>')

                opcode1 = Gtk.ImageMenuItem(Gtk.STOCK_EXECUTE)
                opcode_text = opcode.replace('<', '"').replace('>', '"').lower()
                opcode1.get_children()[0].set_markup('<b>' + opcode_text + '</b>')

                opcode2 = Gtk.MenuItem("")
                opcode2.get_children()[0].set_markup(instructions[opcode].replace('<', '"').replace('>', '"'))

                opmenu.append(opcode1)
                opmenu.append(Gtk.SeparatorMenuItem())
                opmenu.append(opcode2)
                menu.prepend(opcodem)

        # Just show the comment menu if the line has offset/va
        match_address = re.match('\s+(0x[0-9a-z]+)\s', line)
        if match_address:
            addr = match_address.groups()[0]
            # Add comment menu
            opc = Gtk.ImageMenuItem((Gtk.STOCK_ADD))
            opc.get_children()[0].set_label('Add comment')
            menu.prepend(opc)
            opc.connect("activate", self._call_comments_dialog, iter, addr)

            # Add Xrefs menu
            refs = []
            xrefs = []

            xmenu = xrefs_menu.XrefsMenu(self.uicore, self.main)
            addr = self.uicore.core.num.get(addr)
            fcn = self.uicore.core.anal.get_fcn_in(addr, 0)

            if fcn:
                for ref in fcn.get_refs():
                    if not "0x%08x" % ref.addr in refs:
                        refs.append("0x%08x" % ref.addr)
                for xref in fcn.get_xrefs():
                    if not "0x%08x" % xref.addr in xrefs:
                        xrefs.append("0x%08x" % xref.addr)

                refs_menu = xmenu.create_menu("0x%08x" % addr, refs, xrefs, False)
                sep = Gtk.SeparatorMenuItem()
                menu.prepend(sep)
                if hasattr(xmenu, 'xfrommenu'):
                    menu.prepend(xmenu.xfrommenu)
                if hasattr(xmenu, 'xtomenu'):
                    menu.prepend(xmenu.xtomenu)
                menu.prepend(xmenu.fcnm)

        menu.show_all()

    def _call_comments_dialog(self, widget, iter, offset):
        dialog = comments_dialog.CommentsDialog()
        resp = dialog.run()
        if resp == Gtk.ResponseType.ACCEPT:
            start, end = dialog.input_buffer.get_bounds()
            comment = dialog.input_buffer.get_text(start, end)
            tainted_comment = comment.replace('\n', '\n  ; ')
            tainted_comment = '  ; ' + tainted_comment
            dialog.destroy()
            self.buffer.insert(iter, tainted_comment + '\n')
            self.uicore.add_comment(offset, comment)

    def set_completion(self):
        # Seek entry EntryCompletion
        self.completion = Gtk.EntryCompletion()
        self.liststore = Gtk.ListStore(str)
        # Add function names to the list
        for function in self.uicore.allfuncs:
            self.liststore.append([function])

        self.completion.set_model(self.liststore)
        self.seek.set_completion(self.completion)
        self.completion.set_text_column(0)

    def _get_press(self, widget, event):
        x, y = event.get_coords()
        self.press_coords = [x, y]

    def _get_release(self, widget, event):
        x, y = event.get_coords()
        if [x, y] == self.press_coords:
            self._get_clicked_word()

    def _get_clicked_word(self):
        # Get textbuffer coordinates from textview ones
        x, y = self.view.get_pointer()
        x, y = self.view.window_to_buffer_coords(Gtk.TextWindowType.WIDGET, x, y)
        word = self.get_word_on_coords(x, y)
        self._search(word)
        self.high_word._find(word)

    def create_seek_buttons(self):
        self.hbox = Gtk.HBox(False, 1)

        self.back = Gtk.Button()
        self.back_img = Gtk.Image()
        self.back_img.set_from_stock(Gtk.STOCK_GO_BACK, Gtk.IconSize.MENU)
        self.back.set_image(self.back_img)
        self.back.set_relief(Gtk.ReliefStyle.NONE)
        self.back.connect('clicked', self.do_seek, 'b')

        self.forward = Gtk.Button()
        self.forward_img = Gtk.Image()
        self.forward_img.set_from_stock(Gtk.STOCK_GO_FORWARD, Gtk.IconSize.MENU)
        self.forward.set_image(self.forward_img)
        self.forward.set_relief(Gtk.ReliefStyle.NONE)
        self.forward.connect('clicked', self.do_seek, 'f')

        self.seek = Gtk.Entry()
        self.seek.set_max_length(30)
        self.seek.set_icon_from_stock(1, Gtk.STOCK_JUMP_TO)
        self.seek.set_activates_default(True)
        self.seek.connect("activate", self.goto)
        self.seek.connect("icon-press", self.goto)
        self.seek.set_icon_tooltip_text(1, 'Go')

        self.hbox.pack_start(self.back, False, False, 0)
        self.hbox.pack_start(self.forward, False, False, 0)
        self.hbox.pack_start(self.seek, True, True, 0)

        return self.hbox

    def goto(self, widget, icon_pos=None, event=None):
        text = self.seek.get_text()
        self._search(text)

    def call_tooltip(self, widget, event):
        x = int(event.x)
        y = int(event.y)
        x, y = self.view.window_to_buffer_coords(Gtk.TextWindowType.WIDGET, x, y)
        search_string = self.get_word_on_coords(x,y)

        self.addr_tip =''
        if search_string:
            # If it's an address, search lines beginning with it.
            if '[' in search_string:
                search_string = search_string.strip('[').strip(']')
            if '0x' in search_string[0:2]:
                integer = int(search_string, 16)
                hex_addr = "0x%08x" % integer
                self.addr_tip = hex_addr
            elif 'loc.' in search_string:
                self.addr_tip = "0x%08x" % self.uicore.core.num.get(search_string)
            elif any( k in search_string for k in ['fcn.', 'main', 'entry0', '_init', '_fini'] ):
                self.addr_tip = "0x%08x" % self.uicore.core.num.get(search_string)
                self.dograph = True
            elif 'imp.' in search_string:
                self.addr_tip = "0x%08x" % self.uicore.core.num.get(search_string)
            elif 'reloc.' in search_string:
                self.addr_tip = "0x%08x" % self.uicore.core.num.get(search_string)
            elif 'str.' in search_string:
                # Not working until we add strings section into dasm
                #self.addr_tip = "0x%08x" % self.uicore.core.num.get(search_string)
                self.addr_tip = search_string
            elif 'sub_' in search_string:
                self.addr_tip = '0x' + search_string[4:]
            elif '.' in search_string:
                if '[' in search_string:
                    search_string = search_string.strip('[').strip(']')
                self.addr_tip = "0x%08x" % self.uicore.core.num.get(search_string)
            else:
                pass

            if self.addr_tip:
                value = self.uicore.send_cmd_str('pdi 15 @ ' + self.addr_tip)
                widget.set_tooltip_markup("<span font_family=\"monospace\">" + value.rstrip() + "</span>")
            else:
                widget.set_tooltip_markup("")

    def _search(self, search_string, iter = None):

        self.dograph = False
        self.search_string = ''
        if search_string:
            # If it's an address, search lines beginning with it.
            if '[' in search_string:
                search_string = search_string.strip('[').strip(']')
            if '0x' in search_string[0:2]:
                integer = int(search_string, 16)
                hex_addr = "0x%08x" % integer
                self.search_string = hex_addr
            elif 'loc.' in search_string:
                self.search_string = "0x%08x" % self.uicore.core.num.get(search_string)
            elif any( k in search_string for k in ['fcn.', 'main', 'entry0', '_init', '_fini'] ):
                self.search_string = "0x%08x" % self.uicore.core.num.get(search_string)
                self.dograph = True
            elif 'imp.' in search_string:
                self.search_string = "0x%08x" % self.uicore.core.num.get(search_string)
            elif 'reloc.' in search_string:
                self.search_string = "0x%08x" % self.uicore.core.num.get(search_string)
            elif 'str.' in search_string:
                # Not working until we add strings section into dasm
                #self.search_string = "0x%08x" % self.uicore.core.num.get(search_string)
                self.search_string = search_string
            elif 'sub_' in search_string:
                self.search_string = '0x' + search_string[4:]
            elif '.' in search_string:
                if '[' in search_string:
                    search_string = search_string.strip('[').strip(']')
                self.search_string = "0x%08x" % self.uicore.core.num.get(search_string)
            else:
                pass

            if self.search_string:
                startIter =  self.textbuf.get_start_iter()
                # find the positions where the phrase is found
                res = []
                while True:
                    result = startIter.forward_search(self.search_string, Gtk.TextSearchFlags.TEXT_ONLY, None)
                    if result:
                        res.append((result[0], result[1]))
                        startIter = result[1]
                    else:
                        break

                if res:
                    self.marks = []

                    for iter in res:
                        self.match_start, self.match_end = iter

                        if self.match_start:
                            self.buffer.place_cursor(self.match_start)
                            mark = self.buffer.create_mark(None, self.match_start, False)
                            self.view.scroll_to_mark(mark, 0.0, True, 0, 0.03)
                            self.last_search_iter = self.match_end
                            self.marks.append([self.match_start, self.match_end])

                    # Update the browse history list.
                    # It may happen that the self.seeks list is still empty.
                    # Note: This entire code is pretty bad.  We should make a couple
                    # of functions to navigate the history and remove this clowntown
                    # code together with the do_seek() method.
                    if len(self.seeks) == 0 or self.match_start != self.seeks[-1]:
                        self.seeks.insert(self.seek_index, [self.match_start, self.match_end])
                        self.seek_index += 1
                        if len(self.seeks) != self.seek_index:
                            self.seeks = self.seeks[:self.seek_index]

                else:
                    self.search_string = None
                    self.last_search_iter = None
                self.main.tviews.update_graph(self, self.search_string)

    def get_line_on_coords(self, x, y):
        '''This function returns the entire line containing the coordinates
        (x,y) of a TextView.'''

        # Get textiter at coordinates.
        start_iter, _ = self.view.get_line_at_y(y)
        end_iter = start_iter.copy()
        end_iter.forward_line()
        t_buffer = start_iter.get_buffer()

        return t_buffer.get_text(start_iter, end_iter, False)

    def get_word_on_coords(self, x, y):
        '''This function returns the word surrounding the coordinates (x,y) of
        a TextView.  Very useful for clicking on words or doing tooltips.
        I tried to make this work with the Pango functions of the TextIter, but
        it happens that their idea of word separators doesn't correlate very
        well with ASM and r2 output. :o)'''

        def is_word_sep(x, bogus):
            word_separators = [' ', ',', '\t', '\n', '(', ')']
            return x in word_separators

        # Get textiter at coordinates.
        start_iter = self.view.get_iter_at_location(x, y)
        end_iter = start_iter.copy()
        t_buffer = start_iter.get_buffer()

        ret = start_iter.backward_find_char(is_word_sep)
        # We went too far rewinding (off-by-one in fact), so let's forward one
        # character, unless ret is False, which means that we reached the start
        # of the buffer, in which case we won't do anything.
        if ret:
            start_iter.forward_char()
        end_iter.forward_find_char(is_word_sep)

        # MEOW
        return t_buffer.get_text(start_iter, end_iter, True)
