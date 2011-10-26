#       hexdump_view.py
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
import gtk
import pango
import gtksourceview2

class HexdumpView(gtk.HBox):

    '''Right TextView elements'''

    def __init__(self, core):
        super(HexdumpView,self).__init__(False, 0)

        #################################################################
        # Hexdump
        #################################################################

        self.uicore = core
        if self.uicore.backend == 'pyew':
            from pydistorm import Decode, Decode16Bits, Decode32Bits, Decode64Bits
            self.Decode = Decode
            if self.uicore.core.type == 16:
                self.decode = Decode16Bits
            elif self.uicore.core.type == 32:
                self.decode = Decode32Bits
            elif self.uicore.core.type == 64:
                self.decode = Decode64Bits

        # Scrolledwindow for Offsets
        self.offset_sw = gtk.ScrolledWindow()
        self.offset_sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        self.offset_sw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        sb = self.offset_sw.get_vscrollbar()
        sb.set_child_visible(False)

        # Scrolledwindow for Hexdump
        self.hex_sw = gtk.ScrolledWindow()
        self.hex_sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        self.hex_sw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        sb = self.hex_sw.get_vscrollbar()
        sb.set_child_visible(False)

        # Scrolledwindow for ASCII
        self.ascii_sw = gtk.ScrolledWindow()
        self.ascii_sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        self.ascii_sw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)

        # Scrolledwindow for DASM
        self.asm_sw = gtk.ScrolledWindow()
        self.asm_sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        self.asm_sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

        # Scrolling signals and callbacks
        self.offset_sw.connect("scroll-event", self._sync_vscroll_offset_scroll)
        self.hex_sw.connect("scroll-event", self._sync_vscroll_hex_scroll)
        self.ascii_sw.get_vadjustment().connect("value-changed", self._sync_vscroll_ascii_mouse)
        self.hex_sw.get_vadjustment().connect("value-changed", self._sync_vscroll_hex_mouse)
        self.offset_sw.get_vadjustment().connect("value-changed", self._sync_vscroll_offset_mouse)

        # Textviews and buffers
        self.offset_buffer = gtksourceview2.Buffer()
        self.hex_buffer = gtksourceview2.Buffer()
        self.ascii_buffer = gtksourceview2.Buffer()

        self.asm_buffer = gtksourceview2.Buffer()
        # Add ui dir to language paths
        lm = gtksourceview2.LanguageManager()
        paths = lm.get_search_path()
        paths.append(os.path.dirname(__file__) + os.sep + 'data' + os.sep)
        lm.set_search_path(paths)
        self.asm_buffer.set_data('languages-manager', lm)
        self.asm_buffer.set_highlight_syntax(True)
        manager = self.asm_buffer.get_data('languages-manager')
        language = manager.get_language('hex-ascii')
        self.hex_buffer.set_language(language)
        language = manager.get_language('ascii')
        self.ascii_buffer.set_language(language)
        language = manager.get_language('asm')
        self.asm_buffer.set_language(language)

        self.offset_view = gtksourceview2.View(self.offset_buffer)
        self.hex_view = gtksourceview2.View(self.hex_buffer)
        self.hex_view.connect("button-release-event", self.get_selected_text)
        self.ascii_view = gtksourceview2.View(self.ascii_buffer)
        self.asm_view = gtksourceview2.View(self.asm_buffer)

        # Margins for eye candy
        self.offset_view.set_show_right_margin(True)
        self.offset_view.set_right_margin(10)
        self.offset_view.set_editable(False)
        self.hex_view.set_show_right_margin(True)
        self.hex_view.set_right_margin(10)
        self.hex_view.set_left_margin(10)
        self.hex_view.set_editable(False)
        self.ascii_view.set_editable(False)
        self.ascii_view.set_left_margin(10)
        self.ascii_view.set_right_margin(10)
        self.asm_view.set_left_margin(10)

        font_desc = pango.FontDescription('monospace 9')
        if font_desc:
            self.offset_view.modify_font(font_desc)
            self.hex_view.modify_font(font_desc)
            self.ascii_view.modify_font(font_desc)
            self.asm_view.modify_font(font_desc)

        #print self.hex_buffer.get_line_count()

        # Pack everything
        self.offset_sw.add(self.offset_view)
        self.hex_sw.add(self.hex_view)
        self.ascii_sw.add(self.ascii_view)
        self.asm_sw.add(self.asm_view)

        self.pack_start(self.offset_sw, False, False, 0)
        self.pack_start(self.hex_sw, False, False, 0)
        self.pack_start(self.ascii_sw, False, False, 0)
        self.pack_start(self.asm_sw, True, True, 0)

    def add_content(self):
        hexdump = self.uicore.get_full_hexdump()
        self.set_hexdump(hexdump)
        self.asm_buffer.set_text(';; Select some hex bytes on the left\n;; to see them disassembled here')

    def remove_content(self):
        self.offset_buffer.set_text('')
        self.hex_buffer.set_text('')
        self.ascii_buffer.set_text('')

    def update_theme(self, theme):
        self.offset_buffer.set_style_scheme(theme)
        self.hex_buffer.set_style_scheme(theme)
        self.ascii_buffer.set_style_scheme(theme)
        self.asm_buffer.set_style_scheme(theme)

    def set_hexdump(self, dump):
        DUMP = dump
        OFFSET_DUMP = ''
        HEX_DUMP = ''
        ASCII_DUMP = ''

        DUMP_LINES = DUMP.split('\n')
        if self.uicore.backend == 'radare':
            for line in DUMP_LINES[1:]:
                line = line.split('  ')
                if len(line) > 1:
                    OFFSET_DUMP += line[0] +'\n'
                    HEX_DUMP += line[1] + '\n'
                    ASCII_DUMP += line[-1] + '\n'
        elif self.uicore.backend == 'pyew':
            for line in DUMP_LINES:
                line = line.split('   ')
                if len(line) > 1:
                    OFFSET_DUMP += line[0] +'\n'
                    HEX_DUMP += line[1] + '\n'
                    ASCII_DUMP += line[-1][1:] + '\n'

        self.offset_buffer.set_text(OFFSET_DUMP)
        self.hex_buffer.set_text(HEX_DUMP)
        self.ascii_buffer.set_text(ASCII_DUMP)

    def _sync_vscroll_offset_scroll(self, sw, event):
        direction = event.direction.value_name
        hex_adj = sw.get_vadjustment()
        if direction == 'GDK_SCROLL_DOWN':
            hex_adj.set_value(hex_adj.get_value() + hex_adj.get_step_increment())
        elif direction == 'GDK_SCROLL_UP':
            hex_adj.set_value(hex_adj.get_value() - hex_adj.get_step_increment())
        ascii_adj = self.ascii_sw.get_vadjustment()
        if direction == 'GDK_SCROLL_DOWN':
            ascii_adj.set_value(ascii_adj.get_value() + ascii_adj.get_step_increment())
        elif direction == 'GDK_SCROLL_UP':
            ascii_adj.set_value(ascii_adj.get_value() - ascii_adj.get_step_increment())
        offset_adj = self.offset_sw.get_vadjustment()
        if direction == 'GDK_SCROLL_DOWN':
            offset_adj.set_value(offset_adj.get_value() + offset_adj.get_step_increment())
        elif direction == 'GDK_SCROLL_UP':
            offset_adj.set_value(offset_adj.get_value() - offset_adj.get_step_increment())

    def _sync_vscroll_hex_scroll(self, sw, event):
        direction = event.direction.value_name
        hex_adj = sw.get_vadjustment()
        if direction == 'GDK_SCROLL_DOWN':
            hex_adj.set_value(hex_adj.get_value() + hex_adj.get_step_increment())
        elif direction == 'GDK_SCROLL_UP':
            hex_adj.set_value(hex_adj.get_value() - hex_adj.get_step_increment())
        ascii_adj = self.ascii_sw.get_vadjustment()
        if direction == 'GDK_SCROLL_DOWN':
            ascii_adj.set_value(ascii_adj.get_value() + ascii_adj.get_step_increment())
        elif direction == 'GDK_SCROLL_UP':
            ascii_adj.set_value(ascii_adj.get_value() - ascii_adj.get_step_increment())
        offset_adj = self.offset_sw.get_vadjustment()
        if direction == 'GDK_SCROLL_DOWN':
            offset_adj.set_value(offset_adj.get_value() + offset_adj.get_step_increment())
        elif direction == 'GDK_SCROLL_UP':
            offset_adj.set_value(offset_adj.get_value() - offset_adj.get_step_increment())

    def _sync_vscroll_ascii_mouse(self, adjustment):
        value = adjustment.get_value()
        hex_adj = self.hex_sw.get_vadjustment()
        hex_adj.set_value(value)
        hex_adj.changed()
        offset_adj = self.offset_sw.get_vadjustment()
        offset_adj.set_value(value)
        offset_adj.changed()

    def _sync_vscroll_hex_mouse(self, adjustment):
        value = adjustment.get_value()
        ascii_adj = self.ascii_sw.get_vadjustment()
        ascii_adj.set_value(value)
        ascii_adj.changed()
        offset_adj = self.offset_sw.get_vadjustment()
        offset_adj.set_value(value)
        offset_adj.changed()

    def _sync_vscroll_offset_mouse(self, adjustment):
        value = adjustment.get_value()
        ascii_adj = self.ascii_sw.get_vadjustment()
        ascii_adj.set_value(value)
        ascii_adj.changed()
        hex_adj = self.hex_sw.get_vadjustment()
        hex_adj.set_value(value)
        hex_adj.changed()

    def get_selected_text(self, widget, event):
        start, end = self.hex_buffer.get_selection_bounds()
        hex = self.hex_buffer.get_text(start, end, include_hidden_chars=True)
        tmp_hex = hex.replace(' ', '')
        tmp_hex = tmp_hex.replace('\n', '')
        if self.uicore.backend == 'radare':
            dasm = self.uicore.core.assembler.mdisassemble_hexstr(hex)
            if dasm:
                self.asm_buffer.set_text(hex + '\n\n' + dasm.buf_asm)
        elif self.uicore.backend == 'pyew':
            dasm = ''
            for i in self.Decode(0, tmp_hex, self.decode):
                mn = "%s " % i.mnemonic
                op = "%s" % i.operands
                dasm += mn.lower() + op.lower() + '\n'
            self.asm_buffer.set_text(hex + '\n\n' + dasm)
