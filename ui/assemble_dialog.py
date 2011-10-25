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
import gobject
import gtksourceview2

class AssembleDialog(gtk.Dialog):
    '''Assembler plugin dialog'''

    def __init__(self, core):
        super(AssembleDialog,self).__init__('Assembler plugin', None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, (gtk.STOCK_OK,gtk.RESPONSE_ACCEPT))

        self.uicore = core
        self.timer_id = None

        self.butt_ok = self.action_area.get_children()[0]
        self.butt_ok.connect("clicked", self._bye)

        self.original_arch = self.uicore.core.cmd_str('e asm.arch')
        self.original_bits = self.uicore.core.cmd_str('e asm.bits')

        self.hex_tip = '; Example of hexadecimal input\n; Comments will be ignored\n905851e93ff1bfff\n; Look that the asm code for this hexadecimal\n; has appeared on the other text area'
        self.asm_tip = '; Example of assembly input\n; Comments will be ignored\nnop\npush eax\npop ecx\njmp 0x200\ncall 0x100\n; Look that the hex code for this assembly\n; has appeared on the other text area'
        self.action = 'hex'

        # the cancel button
        self.butt_cancel = self.action_area.get_children()[0]
        self.butt_cancel.connect("clicked", lambda x: self.destroy())

        # Positions
        self.resize(600, 400)
        self.set_position(gtk.WIN_POS_CENTER)

        self.vbox.set_spacing(3)
        self.set_border_width(3)

        # Main HBox to contain both columns (VBoxes)
        self.main_hb = gtk.HBox(True, 5)

        # Info icon and some help text
        #################################################################
        self.info_hb = gtk.HBox(False, 3)
        self.info_icon = gtk.Image()
        self.info_icon.set_from_stock(gtk.STOCK_INFO, gtk.ICON_SIZE_MENU)
        self.info_label = gtk.Label()
        self.info_label.set_markup('Just type your asm/hex in the appropiate text area to get it assembled on the other')
        self.info_label.set_alignment(0.02, 0.5)

        self.info_hb.pack_start(self.info_icon, False, False, 1)
        self.info_hb.pack_start(self.info_label, True, True, 1)
        self.vbox.pack_start(self.info_hb, False, False, 1)

        sep = gtk.HSeparator()
        self.vbox.pack_start(sep, False, False, 1)

        self.vbox.pack_start(self.main_hb, True, True, 1)

        # ASM/HEX Labels and Info buttons
        #################################################################

        # Two VBoxes, one for each "column": hex and dasm
        self.hex_vb = gtk.VBox(False, 3)
        self.asm_vb = gtk.VBox(False, 3)

        self.main_hb.pack_start(self.asm_vb, True, True, 1)
        self.main_hb.pack_start(self.hex_vb, True, True, 1)

        # HBoxes for the label/info of each column
        self.hex_hb = gtk.HBox(False, 1)
        self.asm_hb = gtk.HBox(False, 1)

        self.hex_vb.pack_start(self.hex_hb, False, False, 1)
        self.asm_vb.pack_start(self.asm_hb, False, False, 1)

        self.hex_label = gtk.Label("")
        self.hex_label.set_markup("<b>Hexadecimal</b>")
        self.hex_label.set_alignment(0.05, 0.5)
        self.asm_label = gtk.Label("Assembly")
        self.asm_label.set_markup("<b>Assembly</b>")
        self.asm_label.set_alignment(0.05, 0.5)

        self.hex_info = gtk.Button('')
        self.hex_info.set_tooltip_text('Fill the text area with example code.\nWARNING: This will remove actual text area contents!')
        self.hex_info.connect('clicked', self._help, 'hex')
        i = gtk.Image()
        i.set_from_stock(gtk.STOCK_HELP, gtk.ICON_SIZE_MENU)
        self.hex_info.set_image(i)
        l = self.hex_info.get_children()[0]
        l = l.get_children()[0].get_children()[1]
        l = l.set_label('')

        self.asm_info = gtk.Button('')
        self.asm_info.set_tooltip_text('Fill the text area with example code.\nWARNING: This will remove actual text area contents!')
        self.asm_info.connect('clicked', self._help, 'asm')
        i = gtk.Image()
        i.set_from_stock(gtk.STOCK_HELP, gtk.ICON_SIZE_MENU)
        self.asm_info.set_image(i)
        l = self.asm_info.get_children()[0]
        l = l.get_children()[0].get_children()[1]
        l = l.set_label('')

        self.arch_combo = gtk.combo_box_new_text()
        self.arch_combo.set_tooltip_text('Select the architecture to use')
        options = ['x86', 'x86.olly', 'ppc', 'mips', 'arm']
        for option in options:
            self.arch_combo.append_text(option)
        self.arch_combo.set_active(0)

        self.bits_combo = gtk.combo_box_new_text()
        self.bits_combo.set_tooltip_text('Select the bits to use')
        options = ['16', '32', '64']
        for option in options:
            self.bits_combo.append_text(option)
        self.bits_combo.set_active(1)

        # Packing...
        self.hex_hb.pack_start(self.hex_label, True, True, 1)
        self.hex_hb.pack_start(self.hex_info, False, False, 1)
        self.asm_hb.pack_start(self.asm_label, True, True, 1)
        self.asm_hb.pack_start(self.arch_combo, False, False, 1)
        self.asm_hb.pack_start(self.bits_combo, False, False, 1)
        self.asm_hb.pack_start(self.asm_info, False, False, 1)
        
        # Add ui dir to language paths
        lm = gtksourceview2.LanguageManager()
        paths = lm.get_search_path()
        paths.append(os.path.dirname(__file__) + os.sep + 'data' + os.sep)
        lm.set_search_path(paths)

        # HEX textview
        #################################################################

        self.hex_buffer = gtksourceview2.Buffer()
        self.hex_view = gtksourceview2.View(self.hex_buffer)
        self.hex_view.set_show_right_margin(True)
        self.hex_view.set_left_margin(10)
        self.hex_view.set_editable(True)
        self.hex_view.set_wrap_mode(gtk.WRAP_WORD_CHAR)
        self.hex_handler = self.hex_buffer.connect("changed", self._update, "hex")

        self.hex_buffer.set_data('languages-manager', lm)
        self.hex_buffer.set_highlight_syntax(True)

        manager = self.hex_buffer.get_data('languages-manager')
        language = manager.get_language('asm')
        self.hex_buffer.set_language(language)

        self.hex_scrolled = gtk.ScrolledWindow()
        self.hex_scrolled.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.hex_scrolled.is_visible = True

        # Add Textview to Scrolled Window
        self.hex_scrolled.add_with_viewport(self.hex_view)

        self.hex_vb.pack_start(self.hex_scrolled, True, True, 1)

        # Connect once created hex_buffer to avoid warnings
        self.arch_combo.connect("changed", self._update_arch_bits, "arch")
        self.bits_combo.connect("changed", self._update_arch_bits, "bits")

        # ASM TextView
        #################################################################
        self.asm_buffer = gtksourceview2.Buffer()
        self.asm_view = gtksourceview2.View(self.asm_buffer)
        self.asm_view.set_show_right_margin(True)
        self.asm_view.set_left_margin(10)
        self.asm_view.set_editable(True)
        self.asm_handler = self.asm_buffer.connect("changed", self._update, "asm")

        self.asm_buffer.set_data('languages-manager', lm)
        self.asm_buffer.set_highlight_syntax(True)

        manager = self.asm_buffer.get_data('languages-manager')
        language = manager.get_language('asm')
        self.asm_buffer.set_language(language)

        self.asm_scrolled = gtk.ScrolledWindow()
        self.asm_scrolled.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.asm_scrolled.is_visible = True

        # Add Textview to Scrolled Window
        self.asm_scrolled.add_with_viewport(self.asm_view)

        self.asm_vb.pack_start(self.asm_scrolled, True, True, 1)

        sep = gtk.HSeparator()
        self.vbox.pack_start(sep, False, False, 1)

        # Export buttons
        self.export_hb = gtk.HBox(False, 3)

        self.export_label = gtk.Label('Select the export format:')

        self.export_combo = gtk.combo_box_new_text()

        options = ['Python buffer', 'C Array']
        for option in options:
            self.export_combo.append_text(option)
        self.export_combo.set_active(0)

        self.export_bt = gtk.Button('')
        self.export_bt.set_tooltip_text('Export the generated code in the selected format')
        self.export_bt.connect('clicked', self._export)
        i = gtk.Image()
        i.set_from_stock(gtk.STOCK_CONVERT, gtk.ICON_SIZE_MENU)
        self.export_bt.set_image(i)
        l = self.export_bt.get_children()[0]
        l = l.get_children()[0].get_children()[1]
        l = l.set_label('Export')

        self.export_hb.pack_start(self.export_label, False, False, 1)
        self.export_hb.pack_start(self.export_combo, False, False, 1)
        self.export_hb.pack_start(self.export_bt, False, False, 1)

        halign = gtk.Alignment(0, 1, 0, 0)
        halign.add(self.export_hb)

        self.vbox.pack_start(halign, False, False, 1)

        self.show_all()

    #
    # Methods

    def _help(self, widget, data):
        if data == 'hex':
            self.hex_buffer.set_text(self.hex_tip)
        else:
            self.asm_buffer.set_text(self.asm_tip)

    def _update_arch_bits(self, widget, data):
        model = widget.get_model()
        active = widget.get_active()
        value = model[active][0]

        if data == 'arch':
            self.uicore.core.cmd_str('e asm.arch = ' + value)
        else:
            self.uicore.core.cmd_str('e asm.bits = ' + value)

        self.hex_buffer.emit("changed")

    def _export(self, widget):
        model = self.export_combo.get_model()
        active = self.export_combo.get_active()
        option = model[active][0]

        start, end = self.hex_buffer.get_bounds()
        data = self.hex_buffer.get_text(start, end, False)

        # Remove comments from input
        clean_data = []
        data = data.split('\n')
        for x in data:
            if x:
                if x[0] != ';':
                    clean_data.append(x)
        data = ''.join(clean_data)

        if data:
            if 'Python' in option:
                output = 'buf = ""\n'
                data = [data[x:x+2] for x in xrange(0,len(data),2)]
                # Group every 10 elements
                for x in [data[i:i+10] for i in xrange(0, len(data), 10)]:
                    x = ["\\x"+str(i) for i in x]
                    output += "buf += '" + "".join(x) + "'\n"
            else:
                output = 'char buf[] =\n'
                data = [data[x:x+2] for x in xrange(0,len(data),2)]
                # Group every 10 elements
                for x in [data[i:i+10] for i in xrange(0, len(data), 10)]:
                    x = ["\\x"+str(i) for i in x]
                    output += '\t"' + "".join(x) + '"\n'
                output = output[:-1]
                output += ';\n'

            import search_dialog
            self.search_dialog = search_dialog.SearchDialog('Exported ' + option)
            self.search_dialog.output_buffer.set_text(output)

    def _update(self, widget, data=None):
        # This loop makes sure that we only call _find every 500 ms .
        if self.timer_id:
            # We destroy the last event source and create another one.
            gobject.source_remove(self.timer_id)

        self.timer_id = gobject.timeout_add(500, self._refresh, widget, data)

    def _refresh(self, widget, type):

        if type == 'hex':
            start, end = self.hex_buffer.get_bounds()
            data = self.hex_buffer.get_text(start, end, False)
        else:
            start, end = self.asm_buffer.get_bounds()
            data = self.asm_buffer.get_text(start, end, False)

        if data:
            # Remove comments from input
            clean_data = []
            data = data.split('\n')
            for x in data:
                if x:
                    if x[0] != ';':
                        clean_data.append(x)
            data = '\n'.join(clean_data)
    
            if type == 'hex':
                self.disasm(data)
            else:
                data = data.replace('\n', '; ')
                self.assemble(data)

        return False

    def assemble(self, data):
        offset = data
        # FIXME
        self.uicore.core.assembler.set_pc(0)
        code = self.uicore.core.assembler.massemble(offset)
        if code:
            self.hex_buffer.handler_block(self.hex_handler)
            self.hex_buffer.set_text( code.buf_hex )
            self.hex_buffer.handler_unblock(self.hex_handler)

    def disasm(self, data):
        bytes = data
        # FIXME
        self.uicore.core.assembler.set_pc(0)
        code = self.uicore.core.assembler.mdisassemble_hexstr(bytes)
        if code:
            self.asm_buffer.handler_block(self.asm_handler)
            self.asm_buffer.set_text( code.buf_asm )
            self.asm_buffer.handler_unblock(self.asm_handler)

    def _bye(self, widget):
        # Restore original arch and bits values
        self.uicore.core.cmd_str("e asm.arch = " + self.original_arch)
        self.uicore.core.cmd_str("e asm.bits = " + self.original_bits)
