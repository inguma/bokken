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
    summary = 'Instruction listings contain at least a mnemonic, which is the operation to be performed. Many instructions will take operands. Instructions with multiple operands list the destination operand first and the source operand second (&lt;dest&gt;, &lt;source&gt;). Assembler directives may also be listed which appear similar to instructions.'

    assembler_directives = [
            ("DB <byte>", "Define Byte. Reserves an explicit byte of memory at the current location. Initialized to <byte> value."),
            ("DW <word>", "Define Word. 2 bytes."),
            ("DD <dword>", "Define DWord. 4 bytes."),
        ]

    operand_types = [
            ("Immediate", "A numeric operand, hard coded."),
            ("Register", "A numeric operand, hard coded."),
            ("Memory", "A general purpose register."),
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
            ("RVA‐>Raw Conversion", "Raw = (RVA ‐ SectionStartRVA) + (SectionStartRVA ‐ SectionStartPtrToRaw)"),
            ("RVA‐>VA Conversion", "VA = RVA + BaseAddress"),
            ("VA‐>RVA Conversion", "RVA = VA ‐ BaseAddress"),
            ("Raw‐>VA Conversion", "VA = (Raw ‐ SectionStartPtrToRaw) + (SectionStartRVA + ImageBase)"),
        ]

    instructions = [
            ("ADD <dest>, <source>", "Adds <source> to <dest>. <dest> may be a register or memory. <source> may be a register, memory or immediate value."),
            ("CALL <loc>", "Call a function and return to the next instruction when finished. <proc> may be a relative offset from the current location, a register or memory addr."),
            ("CMP <dest>, <source>", "Compare <source> with <dest>. Similar to SUB instruction but does not modify the <dest> operand with the result of the subtraction."),
            ("DEC <dest>", "Subtract 1 from <dest>. <dest> may be a register or memory."),
            ("DIV <divisor>", "Divide the EDX:EAX registers (64‐bit combo) by <divisor>. <divisor> may be a register or memory."),
            ("INC <dest>", "Add 1 to <dest>. <dest> may be a register or memory."),
            ("JE <loc>", "Jump if Equal (ZF=1) to <loc>."),
            ("JGE <loc>", "Jump if Greater or Equal (SF=OF) to <loc>."),
            ("JG <loc>", "Jump if Greater (ZF=0 and SF=OF) to <loc>."),
            ("JLE <loc>", "Jump is Less or Equal (SF<>OF) to <loc>."),
            ("JMP <loc>", "Jump to <loc>. Unconditional."),
            ("JNE <loc>", "Jump if Not Equal (ZF=0) to <loc>."),
            ("JNZ <loc>", "Jump if Not Zero (ZF=0) to <loc>."),
            ("JZ <loc>", "Jump if Zero (ZF=1) to <loc>."),
            ("LEA <dest>, <source>", "Load Effective Address. Gets a pointer to the memory expression <source> and stores it in <dest>."),
            ("MOV <dest>, <source>", "Move data from <source> to <dest>. <source> may be an immediate value, register, or a memory address. Dest may be either a memory address or a register. Both <source> and <dest> may not be memory addresses."),
            ("MUL <source>","Multiply the EDX:EAX registers (64‐bit combo) by <source>. <source> may be a register or memory."),
            ("POP <dest>", "Take a 32‐bit value from the stack and store it in <dest>. ESP is incremented by 4. <dest> may be a register, including segment registers, or memory."),
            ("PUSH <value>", "Adds a 32‐bit value to the top of the stack. Decrements ESP by 4. <value> may be a register, segment register, memory or immediate value."),
            ("ROL <dest>, <count>", "Bitwise Rotate Left the value in <dest> by <count> bits. <dest> may be a register or memory address. <count> may be immediate or CL register."),
            ("ROR <dest>, <count>", "Bitwise Rotate Right the value in <dest> by <count> bits. <dest> may be a register or memory address. <count> may be immediate or CL register."),
            ("SHL <dest>, <count>", "Bitwise Shift Left the value in <dest> by <count> bits. Zero bits added to the least significant bits. <dest> may be reg. or mem. <count> is imm. or CL."),
            ("SHR <dest>, <count>","Bitwise Shift Right the value in <dest> by <count> bits. Zero bits added to the least significant bits. <dest> may be reg. or mem. <count> is imm. or CL."),
            ("SUB <dest>, <source>", "Subtract <source> from <dest>. <source> may be immediate, memory or a register. <dest> may be memory or a register. (source = dest)‐>ZF=1, (source > dest)‐>CF=1, (source < dest)‐>CF=0 and ZF=0"),
            ("TEST <dest>, <source>","Performs a logical OR operation but does not modify the value in the <dest> operand. (source = dest)‐>ZF=1, (source <> dest)‐>ZF=0."),
            ("XCHG <dest, <source>", "Exchange the contents of <source> and <dest>. Operands may be register or memory. Both operands may not be memory."),
            ("XOR <dest>, <source>", "Bitwise XOR the value in <source> with the value in <dest>, storing the result in <dest>. <dest> may be reg or mem and <source> may be reg, mem or imm."),
        ]

    def __init__(self, title='Reference Sheet for x86 Assembler'):
        super(CheatsheetDialog,self).__init__(title, None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, (gtk.STOCK_OK,gtk.RESPONSE_ACCEPT))

        import pango

        # The Cancel button.
        self.butt_cancel = self.action_area.get_children()[0]
        self.butt_cancel.connect("clicked", lambda x: self.destroy())

        # Positions
        self.resize(600, 700)
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_icon_from_file(os.path.dirname(__file__)+os.sep+'data'+os.sep+'bokken.svg')

        vbox_summary = gtk.VBox(False, 1)
        vbox_summary.pack_start(self.create_h1_label('Assembly language'), False, False, 4)
        label_summary = gtk.Label()
        label_summary.set_markup(self.summary)
        label_summary.set_line_wrap(True)
        label_summary.set_alignment(0, 0)
        vbox_summary.add(label_summary)

        vbox_summary.pack_start(self.create_h2_label('Assembly directives'), False, False, 4)
        assembler_directives_tv = self.populate_treeview(self.assembler_directives)
        sw = gtk.ScrolledWindow()
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)

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
        vbox_summary.add(sw)

        vbox_terminology = gtk.VBox(False, 1)
        vbox_terminology.pack_start(self.create_h1_label('Terminology and Functions'), False, False, 4)
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

        self.hbox = gtk.HBox(False, 1)
        self.hbox.add(vbox_summary)
        self.hbox.add(vbox_terminology)

        self.sw = gtk.ScrolledWindow()
        self.sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        self.sw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)

        self.treeview = self.populate_treeview(self.instructions)
        renderer_text = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Instruction", renderer_text, text=0)
        column.set_sort_column_id(0)
        self.treeview.append_column(column)

        renderer_text = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Description", renderer_text, text=1)
        renderer_text.set_property("wrap_width", 700)
        renderer_text.set_property("wrap_mode", pango.WRAP_WORD_CHAR)

        self.treeview.append_column(column)

        self.sw.add(self.treeview)

        self.vbox.pack_start(self.hbox, False, False, 1)
        self.vbox.add(self.sw)
        self.show_all()

    def populate_treeview(self, rows):
        """ Accepts an array of n rows made of 2 elements each, and returns a TreeView."""

        store = gtk.ListStore(str, str)
        for row in rows:
            store.append([row[0], row[1]])

        tv = gtk.TreeView(store)
        tv.set_rules_hint(True)

        return tv

    def create_h1_label(self, string):
        """ Accepts a string and return a label formatted with black background and larger bold white font size."""

        label = gtk.Label()
        label.set_markup('<span background="black" color="white" font_weight="bold" size="larger">' + string + '</span>')
        label.set_alignment(0, 0)

        return label

    def create_h2_label(self, string):
        """ Accepts a string and return a label formatted with grey background and larger font size."""

        label = gtk.Label()
        label.set_markup('<span background="grey" size="larger">' + string + '</span>')
        label.set_alignment(0, 0)

        return label
