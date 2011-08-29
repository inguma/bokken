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

import gtk

class AssembleDialog(gtk.Dialog):
    '''Window to popup search output'''

    def __init__(self, core):
        super(AssembleDialog,self).__init__('Search results', None, gtk.DIALOG_DESTROY_WITH_PARENT, (gtk.STOCK_OK,gtk.RESPONSE_ACCEPT))

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
        self.output_text = gtk.TextView(buffer=None)
        self.output_text.set_wrap_mode(gtk.WRAP_NONE)
        self.output_text.set_editable(True)
        self.output_buffer = self.output_text.get_buffer()
        self.output_buffer.set_text('Not yet working!')

        self.scrolled_window = gtk.ScrolledWindow()
        self.scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
        self.scrolled_window.is_visible = True

        # Add Textview to Scrolled Window
        self.scrolled_window.add_with_viewport(self.output_text)

        #self.vbox.pack_start(self.output_text)
        self.vbox.pack_start(self.scrolled_window)

        # Bytes text entry
        self.bytes_hb = gtk.HBox(False, False)
        self.bytes_entry = gtk.Entry(100)
        self.bytes_hb.add(self.bytes_entry)
        self.bytes_button = gtk.Button(label="disassemble")
        self.bytes_button.connect('clicked', self.disasm)
        self.bytes_hb.pack_start(self.bytes_button, False, False)
        self.vbox.pack_start(self.bytes_hb, False, False)

        # Offset text entry
        self.offset_hb = gtk.HBox(False, False)
        self.offset_entry = gtk.Entry(100)
        self.offset_hb.add(self.offset_entry)
        self.offset_button = gtk.Button(label="write")
        self.offset_button.connect('clicked', self.assemble)
        self.offset_hb.pack_start(self.offset_button, False, False)
        self.vbox.pack_start(self.offset_hb, False, False)

        self.show_all()

    #
    # Methods

    def assemble(self, widget, opcode):
        a = self.uicore.assembler
        a.set_pc(int(self.offset_entry.get_text()))
        code = a.massemble(opcode)
        if code:
            print "HEX: %s" % code.buf_hex
        # TODO self.core.cmd0(wx HEX @ ADDR)
        # TODO refresh disasm/hex buffers :(

    def disasm(self, widget, bytes):
        a = self.uicore.assembler
        a.set_pc(int(self.offset_entry.get_text()))
        code = a.mdisassemnble_hexstr(bytes)
        if code:
            print "ASM: %s" % code.buf_asm
        # TODO: show popup with disasm stuff
