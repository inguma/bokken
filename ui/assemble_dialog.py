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

# TODO: ask the user for the program counter to be used instead of use 0 by default. See the FIXMES below

import os
import gtk
import gtksourceview2

class AssembleDialog(gtk.Dialog):
    '''Assembler plugin dialog'''

    def __init__(self, core):
        super(AssembleDialog,self).__init__('Assembler plugin', None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, (gtk.STOCK_OK,gtk.RESPONSE_ACCEPT))

        self.uicore = core

        self.hex_tip = 'Ex:\n;; Comments will be ignored\n905851e93ff1bfff'
        self.asm_tip = 'Ex:\n;; Comments will be ignored\nnop\npush eax\npop ecx\njmp 0x100'
        self.action = 'hex'

        # the cancel button
        self.butt_cancel = self.action_area.get_children()[0]
        self.butt_cancel.connect("clicked", lambda x: self.destroy())

        # Positions
        self.resize(400, 400)
        self.set_position(gtk.WIN_POS_CENTER)

        self.vbox.set_spacing(3)
        self.set_border_width(3)

        # Info icon and some help text
        #################################################################
        self.info_hb = gtk.HBox(False, 3)
        self.info_icon = gtk.Image()
        self.info_icon.set_from_stock(gtk.STOCK_INFO, gtk.ICON_SIZE_MENU)
        self.info_label = gtk.Label()
        self.info_label.set_markup('<b>Select the input format</b> and fill the first text area\nFinally press the <b>refresh button</b> to get the results')
        self.info_label.set_alignment(0.02, 0.5)

        self.info_hb.pack_start(self.info_icon, False, False, 1)
        self.info_hb.pack_start(self.info_label, True, True, 1)
        self.vbox.pack_start(self.info_hb, False, False, 1)

        sep = gtk.HSeparator()
        self.vbox.pack_start(sep, False, False, 1)

        # ASM/HEX ToggleButtons
        #################################################################

        self.toggle_hb = gtk.HBox(True, 1)

        self.hex_bt = gtk.RadioButton(None, 'Hexadecimal')
        self.hex_bt.set_mode(False)
        self.hex_bt.set_active(True)
        self.hex_bt.connect("toggled", self._update_action, "hex")

        self.asm_bt = gtk.RadioButton(self.hex_bt, 'Assembly')
        self.asm_bt.set_mode(False)
        self.asm_bt.connect("toggled", self._update_action, "asm")

        self.toggle_hb.pack_start(self.hex_bt, True, True, 1)
        self.toggle_hb.pack_start(self.asm_bt, True, True, 1)

        self.vbox.pack_start(self.toggle_hb, False, False, 1)

        # Add ui dir to language paths
        lm = gtksourceview2.LanguageManager()
        paths = lm.get_search_path()
        paths.append(os.getcwd() + os.sep + 'ui' + os.sep + 'data' + os.sep)
        lm.set_search_path(paths)

        # Input textview
        #################################################################

        self.input_buffer = gtksourceview2.Buffer()
        self.input_view = gtksourceview2.View(self.input_buffer)
        self.input_view.set_show_right_margin(True)
        self.input_view.set_left_margin(10)
        self.input_view.set_editable(True)
        self.input_view.set_tooltip_text(self.hex_tip)

        self.input_buffer.set_data('languages-manager', lm)
        self.input_buffer.set_highlight_syntax(True)

        manager = self.input_buffer.get_data('languages-manager')
        language = manager.get_language('asm')
        self.input_buffer.set_language(language)

        self.input_scrolled = gtk.ScrolledWindow()
        self.input_scrolled.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.input_scrolled.is_visible = True

        # Add Textview to Scrolled Window
        self.input_scrolled.add_with_viewport(self.input_view)

        self.vbox.pack_start(self.input_scrolled, True, True, 1)

        # Refresh and button
        #################################################################
        # The box will remain here just in case we decide to add something else
        self.buttons_hb = gtk.HBox(False, 1)
        self.refresh_bt = gtk.Button(None, gtk.STOCK_REFRESH)
        self.refresh_bt.connect('clicked', self._refresh)

        self.align = gtk.Alignment(0.5, 0, 0, 0)
        #self.align.set_padding(0, 0, 100, 100)
        self.align.add(self.refresh_bt)
        self.buttons_hb.pack_start(self.align, True, True, 1)
        self.vbox.pack_start(self.buttons_hb, False, False, 1)

        # Output TextView
        #################################################################
        self.output_buffer = gtksourceview2.Buffer()
        self.output_view = gtksourceview2.View(self.output_buffer)
        self.output_view.set_show_right_margin(True)
        self.output_view.set_left_margin(10)
        self.output_view.set_editable(False)

        self.output_buffer.set_data('languages-manager', lm)
        self.output_buffer.set_highlight_syntax(True)

        manager = self.output_buffer.get_data('languages-manager')
        language = manager.get_language('asm')
        self.output_buffer.set_language(language)

        self.output_scrolled = gtk.ScrolledWindow()
        self.output_scrolled.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.output_scrolled.is_visible = True

        # Add Textview to Scrolled Window
        self.output_scrolled.add_with_viewport(self.output_view)

        self.vbox.pack_start(self.output_scrolled, True, True, 1)

        self.show_all()

    #
    # Methods

    def _update_action(self, widget, data=None):
        self.action = data
        if data == 'hex':
            self.input_view.set_tooltip_text(self.hex_tip)
        elif data == 'asm':
            self.input_view.set_tooltip_text(self.asm_tip)

    def _refresh(self, widget):

        start, end = self.input_buffer.get_bounds()
        data = self.input_buffer.get_text(start, end, False)

        # Remove comments from input
        clean_data = []
        data = data.split('\n')
        for x in data:
            if x[0] != ';':
                clean_data.append(x)
        data = '\n'.join(clean_data)

        if self.action == 'hex':
            self.disasm(data)
        else:
            data = data.replace('\n', '; ')
            self.assemble(data)

    def assemble(self, data):
        offset = data
        # FIXME
        self.uicore.core.assembler.set_pc(0)
        code = self.uicore.core.assembler.massemble(offset)
        if code:
            self.output_buffer.set_text( ";; HEX:\n%s" % code.buf_hex )

    def disasm(self, data):
        bytes = data
        # FIXME
        self.uicore.core.assembler.set_pc(0)
        code = self.uicore.core.assembler.mdisassemble_hexstr(bytes)
        if code:
            self.output_buffer.set_text( ";; ASM:\n%s" % code.buf_asm )
