##      assemble_dialog.py
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
import gtksourceview2

class AssembleDialog(gtk.Dialog):
    '''Assembler plugin dialog'''

    def __init__(self, core):
        super(AssembleDialog,self).__init__('Assembler plugin', None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, (gtk.STOCK_OK,gtk.RESPONSE_ACCEPT))

        self.uicore = core

        # the cancel button
        self.butt_cancel = self.action_area.get_children()[0]
        self.butt_cancel.connect("clicked", lambda x: self.destroy())

        # Positions
        self.resize(400, 400)
        self.set_position(gtk.WIN_POS_CENTER)

        self.vbox.set_spacing(3)
        self.set_border_width(3)

        # Log TextView
        #################################################################
        # Add ui dir to language paths
        lm = gtksourceview2.LanguageManager()
        paths = lm.get_search_path()
        paths.append(os.getcwd() + os.sep + 'ui' + os.sep + 'data' + os.sep)
        lm.set_search_path(paths)

        self.output_buffer = gtksourceview2.Buffer()
        self.output_view = gtksourceview2.View(self.output_buffer)
        self.output_view.set_show_right_margin(True)
        self.output_view.set_right_margin(10)
        self.output_view.set_editable(False)

        self.output_buffer.set_data('languages-manager', lm)
        self.output_buffer.set_highlight_syntax(True)

        manager = self.output_buffer.get_data('languages-manager')
        language = manager.get_language('asm')
        self.output_buffer.set_language(language)

        self.scrolled_window = gtk.ScrolledWindow()
        self.scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
        self.scrolled_window.is_visible = True

        # Add Textview to Scrolled Window
        self.scrolled_window.add_with_viewport(self.output_view)

        self.vbox.pack_start(self.scrolled_window)

        # Bytes text entry
        self.bytes_hb = gtk.HBox(False, False)
        self.bytes_entry = gtk.Entry(100)
        self.bytes_entry.set_tooltip_text('Ex: 9090e900000000')
        self.bytes_entry.connect('activate', self.disasm)

        self.bytes_hb.add(self.bytes_entry)
        self.bytes_button = gtk.Button(label="Disassemble")
        self.bytes_button.connect('clicked', self.disasm)
        w,h = self.bytes_button.size_request()
        self.bytes_button.set_size_request(85, h)

        self.bytes_hb.pack_start(self.bytes_button, False, False)
        self.vbox.pack_start(self.bytes_hb, False, False)

        # Offset text entry
        self.offset_hb = gtk.HBox(False, False)
        self.offset_entry = gtk.Entry(100)
        self.offset_entry.set_tooltip_text('Ex: nop; nop; jmp 0x10')
        self.offset_entry.connect('activate', self.assemble)

        self.offset_hb.add(self.offset_entry)
        self.offset_button = gtk.Button(label="Assemble")
        self.offset_button.connect('clicked', self.assemble)
        w,h = self.offset_button.size_request()
        self.offset_button.set_size_request(85, h)

        self.offset_hb.pack_start(self.offset_button, False, False)
        self.vbox.pack_start(self.offset_hb, False, False)

        self.show_all()

    #
    # Methods

    def assemble(self, widget):
        offset = self.offset_entry.get_text()
        #a.set_pc( int(offset) )
        code = self.uicore.core.assembler.massemble(offset)
        if code:
            self.output_buffer.set_text( ";; HEX:\n%s" % code.buf_hex )
        # TODO self.core.cmd0(wx HEX @ ADDR)
        # TODO refresh disasm/hex buffers :(

    def disasm(self, widget):
        bytes = self.bytes_entry.get_text()
        #a.set_pc( int(bytes) )
        code = self.uicore.core.assembler.mdisassemble_hexstr(bytes)
        if code:
            #print "ASM: %s" % code.buf_asm
            self.output_buffer.set_text( ";; ASM:\n%s" % code.buf_asm )
        # TODO: show popup with disasm stuff
