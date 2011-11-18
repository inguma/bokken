##      cheatsheet_dialog.py
#       -*- coding: utf-8 -*
#
#       Copyright 2011 David Martínez Moreno <ender@debian.org>
#       This software is not affiliated in any way with Facebook, my current employer.
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

class CheatsheetDialog(gtk.Dialog):
    '''Window to popup cheatsheet output'''

    # Just x86 instructions for now.
    summary = 'Instruction listings contain at least a <b>mnemonic</b>, which is <i>the operation to be performed</i>.\nMany instructions will take operands. Instructions with multiple operands list the <b>destination operand first and the source operand second</b> (&lt;dest&gt;, &lt;source&gt;).\nAssembler directives may also be listed which appear similar to instructions.'

    assembler_directives = [
            ("DB <byte>", "Define Byte. Reserves an explicit byte of memory at the current location. Initialized to <byte> value."),
            ("DW <word>", "Define Word. 2 bytes."),
            ("DD <dword>", "Define DWord. 4 bytes."),
        ]

    operand_types = [
            ("Immediate", "A numeric operand, hard coded."),
            ("Register", "A general purpose register."),
            ("Memory", "Memory address w/ brackets [ ]."),
        ]

    terms = [
            ("Pointer to Raw Data", "Offset of section data within the executable file."),
            ("Size of Raw Data", "Amount of section data within the executable file."),
            ("RVA", "Relative Virtual Address. Memory offset from the beginning of the executable."),
            ("Virtual Address (VA)", "Absolute Memory Address (RVA + Base). The PE Header fields named VirtualAddress actually contain Relative Virtual Addresses."),
            ("Virtual Size", "Amount of section data in memory."),
            ("Base Address", "Offset in memory that the executable module is loaded."),
            ("ImageBase", "Base Address requested in the PE header of a module."),
            ("Module", "A PE-formatted file loaded into memory. Typically EXE, DLL or ELF."),
            ("Pointer", "A memory address."),
            ("Entry Point", "The address of the first instruction to be executed when the module is loaded."),
            ("Import", "Library functions required for use by an executable module."),
            ("Export", "Functions provided by a library which may be Imported by another module."),
            ("RVA ‐> Raw Conversion", "Raw = (RVA ‐ SectionStartRVA) + (SectionStartRVA ‐ SectionStartPtrToRaw)"),
            ("RVA ‐> VA Conversion", "VA = RVA + BaseAddress"),
            ("VA ‐> RVA Conversion", "RVA = VA ‐ BaseAddress"),
            ("Raw ‐> VA Conversion", "VA = (Raw ‐ SectionStartPtrToRaw) + (SectionStartRVA + ImageBase)"),
        ]

    general_registers = [
            ("EAX", "Contains the return value of a function call"),
            ("ECX", "Used as a loop counter. \"this\" pointer in C++"),
            ("EBX", "General Purpose"),
            ("EDX", "General Purpose"),
            ("ESI", "Source index pointer"),
            ("EDI", "Destination index pointer"),
            ("ESP", "Stack pointer"),
            ("EBP", "Stack base pointer")
        ]

    segment_registers = [
            ("CS", "Code segment"),
            ("SS", "Stack segment"),
            ("DS", "Data segment"),
            ("ES", "Extra data segment"),
            ("FS", "Points to Thread Information Block (TIB)"),
            ("GS", "Extra data segment")
        ]

    misc_registers = [
            ("EIP", "Instruction pointer"),
            ("EFLAGS", "Processor status flags")
        ]

    status_flags = [
            ("ZF", "Zero: Operation resulted in Zero"),
            ("CF", "Carry: source > destination in subtract"),
            ("SF", "Sign: Operation resulted in a negative #"),
            ("OF", "Overflow: result too large for destination")
        ]

    all_registers = ['general_registers', 'segment_registers', 'misc_registers', 'status_flags']

    instructions = [
            ("ADD <dst>, <src>", "Adds <src> to <dst>. <dst> may be a register or memory. <src> may be a register, memory or immediate value."),
            ("CALL <loc>", "Call a function and return to the next instruction when finished. <proc> may be a relative offset from the current location, a register or memory addr."),
            ("CMP <dst>, <src>", "Compare <src> with <dst>. Similar to SUB instruction but does not modify the <dst> operand with the result of the subtraction."),
            ("DEC <dst>", "Subtract 1 from <dst>. <dst> may be a register or memory."),
            ("DIV <divisor>", "Divide the EDX:EAX registers (64‐bit combo) by <divisor>. <divisor> may be a register or memory."),
            ("INC <dst>", "Add 1 to <dst>. <dst> may be a register or memory."),
            ("JE <loc>", "Jump if Equal (ZF=1) to <loc>."),
            ("JGE <loc>", "Jump if Greater or Equal (SF=OF) to <loc>."),
            ("JG <loc>", "Jump if Greater (ZF=0 and SF=OF) to <loc>."),
            ("JLE <loc>", "Jump is Less or Equal (SF<>OF) to <loc>."),
            ("JMP <loc>", "Jump to <loc>. Unconditional."),
            ("JNE <loc>", "Jump if Not Equal (ZF=0) to <loc>."),
            ("JNZ <loc>", "Jump if Not Zero (ZF=0) to <loc>."),
            ("JZ <loc>", "Jump if Zero (ZF=1) to <loc>."),
            ("LEA <dst>, <src>", "Load Effective Address. Gets a pointer to the memory expression <src> and stores it in <dst>."),
            ("MOV <dst>, <src>", "Move data from <src> to <dst>. <src> may be an immediate value, register, or a memory address. Dest may be either a memory address or a register. Both <src> and <dst> may not be memory addresses."),
            ("MUL <src>","Multiply the EDX:EAX registers (64‐bit combo) by <src>. <src> may be a register or memory."),
            ("POP <dst>", "Take a 32‐bit value from the stack and store it in <dst>. ESP is incremented by 4. <dst> may be a register, including segment registers, or memory."),
            ("PUSH <value>", "Adds a 32‐bit value to the top of the stack. Decrements ESP by 4. <value> may be a register, segment register, memory or immediate value."),
            ("ROL <dst>, <count>", "Bitwise Rotate Left the value in <dst> by <count> bits. <dst> may be a register or memory address. <count> may be immediate or CL register."),
            ("ROR <dst>, <count>", "Bitwise Rotate Right the value in <dst> by <count> bits. <dst> may be a register or memory address. <count> may be immediate or CL register."),
            ("SHL <dst>, <count>", "Bitwise Shift Left the value in <dst> by <count> bits. Zero bits added to the least significant bits. <dst> may be reg. or mem. <count> is imm. or CL."),
            ("SHR <dst>, <count>","Bitwise Shift Right the value in <dst> by <count> bits. Zero bits added to the least significant bits. <dst> may be reg. or mem. <count> is imm. or CL."),
            ("SUB <dst>, <src>", "Subtract <src> from <dst>. <src> may be immediate, memory or a register. <dst> may be memory or a register. (src = dst)‐>ZF=1, (src > dst)‐>CF=1, (src < dst)‐>CF=0 and ZF=0"),
            ("TEST <dst>, <src>","Performs a logical OR operation but does not modify the value in the <dst> operand. (src = dst)‐>ZF=1, (src <> dst)‐>ZF=0."),
            ("XCHG <dst, <src>", "Exchange the contents of <src> and <dst>. Operands may be register or memory. Both operands may not be memory."),
            ("XOR <dst>, <src>", "Bitwise XOR the value in <src> with the value in <dst>, storing the result in <dst>. <dst> may be reg or mem and <src> may be reg, mem or imm."),
        ]

    def __init__(self, title='Reference Sheet for x86 Assembler'):
        super(CheatsheetDialog,self).__init__(title, None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, (gtk.STOCK_ABOUT, gtk.RESPONSE_ACCEPT, gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))

        import pango

        # The Cancel button.
        self.butt_cancel = self.action_area.get_children()[0]
        self.butt_cancel.connect("clicked", lambda x: self.destroy())

        self.butt_about = self.action_area.get_children()[1]
        self.butt_about.connect("clicked", self._show_about)

        self.vbox.set_spacing(3)

        # Positions
        self.resize(600, 700)
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_icon_from_file(os.path.dirname(__file__)+os.sep+'data'+os.sep+'bokken.svg')
        self.pix = gtk.gdk.pixbuf_new_from_file(os.path.dirname(__file__) + os.sep + 'data' + os.sep + 'block.png')

        # Font
        font_desc = pango.FontDescription("FreeSans 9")

        # Assembly Summary
        vbox_summary = gtk.VBox(False, 1)
        hbox_summary = gtk.HBox(False, 1)

        summ_icon = gtk.image_new_from_stock(gtk.STOCK_INFO, gtk.ICON_SIZE_MENU)
        label_summary = gtk.Label()
        label_summary.set_markup(self.summary)
        #label_summary.modify_font(font_desc)
        #label_summary.set_line_wrap(True)
        label_summary.set_alignment(0, 0)

        # Pack icon and title
        hbox_summary.pack_start(summ_icon, False, False, 2)
        hbox_summary.pack_start(self.create_h1_label('Assembly language'), True, True, 2)

        # Pack contents
        vbox_summary.pack_start(hbox_summary, False, False, 2)
        vbox_summary.pack_start(label_summary, True, True, 2)
        self.vbox.pack_start(vbox_summary, False, False, 2)

        # Directives and operands VBox
        lang_vbox = gtk.VBox(False, 2)

        # Assembly directives
        directives_vbox = gtk.VBox(False, 2)
        directives_hbox = gtk.HBox(False, 1)
        directives_icon = gtk.image_new_from_stock(gtk.STOCK_EXECUTE, gtk.ICON_SIZE_MENU)
        directives_hbox.pack_start(directives_icon, False, False, 2)
        directives_hbox.pack_start(self.create_h2_label('Assembly directives'), True, True, 2)
        directives_vbox.pack_start(directives_hbox, False, False, 2)
        assembler_directives_tv = self.populate_treeview(self.assembler_directives)
        sw = gtk.ScrolledWindow()
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_NEVER)

        assembler_directives_tv = self.populate_treeview(self.assembler_directives)
        renderer_text = gtk.CellRendererText()
        column = gtk.TreeViewColumn("", renderer_text, text=0)
        assembler_directives_tv.append_column(column)

        renderer_text = gtk.CellRendererText()
        column = gtk.TreeViewColumn("", renderer_text, text=1)
        renderer_text.set_property("wrap_width", 300)
        renderer_text.set_property("wrap_mode", pango.WRAP_WORD_CHAR)
        assembler_directives_tv.append_column(column)
        assembler_directives_tv.set_headers_visible(False)

        sw.add(assembler_directives_tv)
        directives_vbox.add(sw)

        # Operand types
        operands_vbox = gtk.VBox(False, 2)
        operands_hbox = gtk.HBox(False, 1)
        operands_icon = gtk.image_new_from_stock(gtk.STOCK_PROPERTIES, gtk.ICON_SIZE_MENU)
        operands_hbox.pack_start(operands_icon, False, False, 2)
        operands_hbox.pack_start(self.create_h2_label('Operand Types'), True, True, 2)
        operands_vbox.pack_start(operands_hbox, False, False, 2)
        assembler_operands_tv = self.populate_treeview(self.operand_types)
        sw = gtk.ScrolledWindow()
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_NEVER)

        assembler_operands_tv = self.populate_treeview(self.operand_types)
        renderer_text = gtk.CellRendererText()
        column = gtk.TreeViewColumn("", renderer_text, text=0)
        assembler_operands_tv.append_column(column)

        renderer_text = gtk.CellRendererText()
        column = gtk.TreeViewColumn("", renderer_text, text=1)
        renderer_text.set_property("wrap_width", 300)
        renderer_text.set_property("wrap_mode", pango.WRAP_WORD_CHAR)
        assembler_operands_tv.append_column(column)
        assembler_operands_tv.set_headers_visible(False)

        sw.add(assembler_operands_tv)
        operands_vbox.add(sw)

        # Terminology
        vbox_terminology = gtk.VBox(False, 1)
        terminology_hbox = gtk.HBox(False, 1)
        terminology_icon = gtk.image_new_from_stock(gtk.STOCK_INDEX, gtk.ICON_SIZE_MENU)
        terminology_hbox.pack_start(terminology_icon, False, False, 2)
        terminology_hbox.pack_start(self.create_h1_label('Terminology and Functions'), True, True, 2)
        vbox_terminology.pack_start(terminology_hbox, False, False, 2)
        sw = gtk.ScrolledWindow()
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)

        terminology_tv = self.populate_treeview(self.terms)
        renderer_text = gtk.CellRendererText()
        column = gtk.TreeViewColumn("", renderer_text, text=0)
        terminology_tv.append_column(column)

        renderer_text = gtk.CellRendererText()
        column = gtk.TreeViewColumn("", renderer_text, text=1)
        renderer_text.set_property("wrap_width", 300)
        renderer_text.set_property("wrap_mode", pango.WRAP_WORD_CHAR)
        terminology_tv.append_column(column)
        terminology_tv.set_headers_visible(False)

        sw.add(terminology_tv)
        vbox_terminology.add(sw)

        self.hbox = gtk.HBox(False, 3)
        lang_vbox.pack_start(directives_vbox, False, False, 0)
        lang_vbox.pack_start(operands_vbox, False, False, 0)
        self.hbox.add(lang_vbox)
        self.hbox.pack_start(gtk.VSeparator(), False, False, 0)
        self.hbox.add(vbox_terminology)

        # Hbox for instructions and registers
        self.bottom_hbox = gtk.HBox(False, 3)

        # Instructions
        instructions_vbox = gtk.VBox(False, 0)
        instructions_hbox = gtk.HBox(False, 0)
        instructions_icon = gtk.image_new_from_stock(gtk.STOCK_INDENT, gtk.ICON_SIZE_MENU)
        info_icon = gtk.image_new_from_stock(gtk.STOCK_SORT_ASCENDING, gtk.ICON_SIZE_MENU)
        stack_button = gtk.Button()
        stack_button.set_tooltip_text("Stack diagram")
        stack_button.set_image(info_icon)
        stack_button.set_label('The stack')
        stack_button.connect('clicked', self.popup_stack)
        instructions_hbox.pack_start(instructions_icon, False, False, 2)
        instructions_label = self.create_h1_label('Instructions')
        instructions_label.set_padding(0, 5)
        instructions_hbox.pack_start(instructions_label, True, True, 2)
        instructions_hbox.pack_end(stack_button, False, False, 2)

        self.sw = gtk.ScrolledWindow()
        self.sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        self.sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

        self.treeview = self.populate_treeview(self.instructions)
        renderer_text = gtk.CellRendererText()
#        font = pango.FontDescription('Bitstream Charter 9')
#        renderer_text.set_property('font-desc', font)
        column = gtk.TreeViewColumn("Instruction", renderer_text, text=0)
        column.set_sort_column_id(0)
        self.treeview.append_column(column)

        renderer_text = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Description", renderer_text, text=1)
        renderer_text.set_property("wrap_width", 390)
        renderer_text.set_property("wrap_mode", pango.WRAP_WORD_CHAR)

        self.treeview.append_column(column)

        self.sw.add(self.treeview)

        instructions_vbox.pack_start(instructions_hbox, False, False, 1)
        instructions_vbox.pack_start(self.sw, True, True, 1)

        # Registers
        registers_vbox = gtk.VBox(False, 0)
        registers_hbox = gtk.HBox(False, 0)
        registers_icon = gtk.image_new_from_stock(gtk.STOCK_UNINDENT, gtk.ICON_SIZE_MENU)
        info_icon = gtk.image_new_from_stock(gtk.STOCK_LEAVE_FULLSCREEN, gtk.ICON_SIZE_MENU)
        registers_button = gtk.Button()
        registers_button.set_tooltip_text("16 and 8 bits registers")
        registers_button.set_image(info_icon)
        registers_button.set_label('16/8 Bits')
        registers_button.connect('clicked', self.popup_registers)
        registers_hbox.pack_start(registers_icon, False, False, 2)
        registers_label = self.create_h1_label('Registers')
        registers_label.set_padding(0, 5)
        registers_hbox.pack_start(registers_label, True, True, 2)
        registers_hbox.pack_end(registers_button, False, False, 2)

        sw = gtk.ScrolledWindow()
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)

        treeview = self.populate_tree(self.all_registers)

        rendererPix = gtk.CellRendererPixbuf()
        renderer_text = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Register")
        column.pack_start(rendererPix, False)
        column.pack_start(renderer_text, True)
        column.set_attributes(renderer_text, text=1)
        column.set_attributes(rendererPix, pixbuf=0)
        column.set_sort_column_id(0)
#        column.set_attributes(renderer_text, markup=0)
#        column.add_attribute(renderer_text, "markup", 1)
#        renderer_text.set_property("markup", 1)
        treeview.append_column(column)

        renderer_text = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Description", renderer_text, text=2)
        renderer_text.set_property("wrap_width", 300)
        renderer_text.set_property("wrap_mode", pango.WRAP_WORD_CHAR)

        treeview.append_column(column)

        sw.add(treeview)

        registers_vbox.pack_start(registers_hbox, False, False, 1)
        registers_vbox.pack_start(sw, True, True, 1)

        self.bottom_hbox.pack_start(instructions_vbox, True, True, 1)
        self.bottom_hbox.pack_start(gtk.VSeparator(), False, False, 1)
        self.bottom_hbox.pack_start(registers_vbox, False, False, 1)

        # Last packaging
        self.vbox.pack_start(self.hbox, False, False, 1)
        self.vbox.pack_start(self.bottom_hbox, True, True, 1)
        self.show_all()

    def populate_tree(self, groups):
        """ Accepts an array of n rows made of 2 elements each, and returns a TreeView."""

        store = gtk.TreeStore(gtk.gdk.Pixbuf, str, str)

        for group in groups:
            #header = '<span background=\"#5a58ff\" foreground=\"white\"><b> ' + group.replace('_', ' ').capitalize() + '\t</b></span>'
            header = group.replace('_', ' ').capitalize()
            it = store.append(None, [self.pix, header, ''])
            for row in eval('self.' + group):
                store.append(it, [None, row[0], row[1]])

        tv = gtk.TreeView(store)
        #tv.set_rules_hint(True)
        #tv.set_enable_tree_lines(True)
        tv.set_show_expanders(False)
        tv.set_level_indentation(10)
        tv.expand_all()

        return tv

    def populate_treeview(self, rows):
        """ Accepts an array of n rows made of 2 elements each, and returns a ListView."""

        store = gtk.ListStore(str, str)
        for row in rows:
            store.append([row[0], row[1]])

        tv = gtk.TreeView(store)
        tv.set_rules_hint(True)

        return tv

    def create_h1_label(self, string):
        """ Accepts a string and return a label formatted with black background and larger bold white font size."""

        label = gtk.Label()
        label.set_markup('<span background="black" color="white" font_weight="bold" size="larger">  ' + string + '\t\t</span>')
        label.set_alignment(0, 0)

        return label

    def create_h2_label(self, string):
        """ Accepts a string and return a label formatted with grey background and larger font size."""

        label = gtk.Label()
        label.set_markup('<span background="grey" size="larger" font_weight="bold" color="white">  ' + string + '\t\t</span>')
        label.set_alignment(0, 0)

        return label

    def popup_stack(self, widget):
        dialog = gtk.Dialog('The stack', None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, (gtk.STOCK_CLOSE,gtk.RESPONSE_CLOSE))
        dialog.set_icon_from_file(os.path.dirname(__file__)+os.sep+'data'+os.sep+'bokken.svg')
        stack_img = gtk.Image()
        stack_img.set_from_file('ui/data/stack.png')
        dialog.vbox.pack_start(self.create_h1_label("The stack"), False, False, 2)
        dialog.vbox.pack_start(stack_img, True, True, 2)
        dialog.show_all()
        dialog.run()
        dialog.destroy()

    def popup_registers(self, widget):
        dialog = gtk.Dialog('16­bit and 8­bit registers', None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, (gtk.STOCK_CLOSE,gtk.RESPONSE_CLOSE))
        dialog.set_icon_from_file(os.path.dirname(__file__)+os.sep+'data'+os.sep+'bokken.svg')
        reg_img = gtk.Image()
        reg_img.set_from_file('ui/data/registers.png')
        reg_label = gtk.Label("The four primary general purpose registers (EAX, EBX, ECX and EDX)\nhave 16 and 8 bit overlapping aliases.")
        reg_label.set_alignment(0.1, 0.1)
        reg_label.set_padding (0, 3)
        dialog.vbox.pack_start(reg_label, False, False, 2)
        dialog.vbox.pack_start(reg_img, True, True, 2)
        dialog.show_all()
        dialog.run()
        dialog.destroy()

    def _show_about(self, widget):
        md = gtk.MessageDialog(self, 
            gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_INFO, 
            gtk.BUTTONS_CLOSE, "")
        md.set_markup('The data for this cheat sheet\nhas been borrowed from:\n\n<a href="http://www.rnicrosoft.net">http://www.rnicrosoft.net</a>\n\nThe original cheat sheet can be\ndownloaded from <a href="http://www.rnicrosoft.net/docs/X86_Win32_Reverse_Engineering_Cheat_Sheet.pdf">here</a>')
        md.set_icon_from_file(os.path.dirname(__file__)+os.sep+'data'+os.sep+'bokken.svg')
        md.run()
        md.destroy()
