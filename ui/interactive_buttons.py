#       interactive_buttons.py
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

FAIL = '\033[91m'
OKGREEN = '\033[92m'
ENDC = '\033[0m'

class InteractiveButtons(gtk.HBox):
    '''Interactive Buttons'''

    def __init__(self, uicore, buffer):
        super(InteractiveButtons,self).__init__(False, 1)

        self.buffer = buffer
        self.output_type = 'hexadecimal'
        # By default shows hexadecimal so no syntax highlight
        self.buffer.set_highlight_syntax(False)

        self.uicore = uicore
        self.toolbox = self

        self.int_tb = gtk.Toolbar()
        self.int_tb.set_style(gtk.TOOLBAR_ICONS)

        # Previous buffer button
        self.prev_ti = gtk.ToolItem()
        self.prev_align = gtk.Alignment(yalign=0.5)
        self.prev_ti.add(self.prev_align)
        self.prev = gtk.ToolButton(gtk.STOCK_GO_UP)
        self.prev.set_tooltip_text('Previous buffer')
        self.prev.connect("clicked", self.move, 'b')
        self.prev.label = 'Previous'
        self.prev_align.add(self.prev)
        self.int_tb.insert(self.prev_ti, 0)

        # Next buffer button
        self.next_ti = gtk.ToolItem()
        self.next_align = gtk.Alignment(yalign=0.5)
        self.next_ti.add(self.next_align)
        self.next = gtk.ToolButton(gtk.STOCK_GO_DOWN)
        self.next.set_tooltip_text('Next buffer')
        self.next.connect("clicked", self.move, 'f')
        self.next.label = 'Next'
        self.next_align.add(self.next)
        self.int_tb.insert(self.next_ti, 1)

        # Separator
        self.sep = gtk.SeparatorToolItem()
        self.int_tb.insert(self.sep, 2)

        # Seek to...
        self.seek_tb = gtk.ToolItem()
        self.seek_label = gtk.Label(' Seek: ')
        self.seek_tb.add(self.seek_label)
        self.int_tb.insert(self.seek_tb, 3)

        self.seek_entry_tb = gtk.ToolItem()
        self.seek_entry = gtk.Entry(100)
        self.seek_entry.set_icon_from_stock(1, gtk.STOCK_GO_FORWARD)
        self.seek_entry.set_icon_tooltip_text(1, 'Seek to')
        self.seek_entry.connect("activate", self.seek)
        self.seek_entry.connect("icon-press", self.seek)
        self.seek_entry_tb.add(self.seek_entry)
        self.int_tb.insert(self.seek_entry_tb, 4)

        # Separator
        self.sep = gtk.SeparatorToolItem()
        self.int_tb.insert(self.sep, 5)

        # Buffer size
        self.buffer_tb = gtk.ToolItem()
        self.buffer_label = gtk.Label(' Buffer size: ')
        self.buffer_tb.add(self.buffer_label)
        self.int_tb.insert(self.buffer_tb, 6)

        self.buffer_entry_tb = gtk.ToolItem()
        self.buffer_entry = gtk.Entry(100)
        self.buffer_entry.set_icon_from_stock(1, gtk.STOCK_APPLY)
        self.buffer_entry.set_icon_tooltip_text(1, 'Apply')
        self.buffer_entry.connect("activate", self.set_buffer_size)
        self.buffer_entry.connect("icon-press", self.set_buffer_size)
        self.buffer_entry_tb.add(self.buffer_entry)
        self.int_tb.insert(self.buffer_entry_tb, 7)

        # Separator
        self.sep = gtk.SeparatorToolItem()
        self.int_tb.insert(self.sep, 8)

        # Radio buttons (output format)

        self.hex_ti = gtk.ToolItem()
        self.hex_align = gtk.Alignment(yalign=0.5)
        self.hex_ti.add(self.hex_align)
        self.hex_button = gtk.RadioToolButton(None, None)
        self.hex_button.set_label("HEX")
        self.hex_button.connect("toggled", self.callback, "Hexadecimal")
        self.hex_button.set_active(True)
        self.hex_align.add(self.hex_button)
        self.int_tb.insert(self.hex_ti, 9)

        self.dasm_ti = gtk.ToolItem()
        self.dasm_align = gtk.Alignment(yalign=0.5)
        self.dasm_ti.add(self.dasm_align)
        self.dasm_button = gtk.RadioToolButton(self.hex_button, None)
        self.dasm_button.set_label("ASM")
        self.dasm_button.connect("toggled", self.callback, "Disassembly")
        self.dasm_align.add(self.dasm_button)
        self.int_tb.insert(self.dasm_ti, 10)

        if 'radare' in self.uicore.backend:
            # Separator
            self.sep = gtk.SeparatorToolItem()
            self.int_tb.insert(self.sep, 11)

            self.exec_entry_tb = gtk.ToolItem()
            self.exec_entry = gtk.Entry(100)
            self.exec_entry.set_icon_from_stock(1, gtk.STOCK_EXECUTE)
            self.exec_entry.set_icon_tooltip_text(1, 'Execute')
            self.exec_entry.connect("activate", self.r2_exec)
            self.exec_entry.connect("icon-press", self.r2_exec)
            self.exec_entry_tb.add(self.exec_entry)
            self.int_tb.insert(self.exec_entry_tb, 12)

        self.pack_start(self.int_tb, True, True)

        self.uicore.core.bsize = 512

    #
    # Functions
    #
    def callback(self, widget, data=None):
        if widget.get_active() == True:
            self.output_type = data.lower()
            if self.uicore.backend == 'radare':
                addr = int(self.uicore.core.cmd_str('s').rstrip(), 0)
                va = self.uicore.core.cmd_str('e io.va').rstrip()

            # Only highlight syntax for disassembly
            if self.output_type == 'hexadecimal':
                if self.uicore.backend == 'radare':
                    if va == "true":
                        self.uicore.core.cmd0('e io.va=0')
                        addr = self.uicore.core.io.section_vaddr_to_offset(addr)
                    self.uicore.core.cmd0('s ' + str(addr))
                self.buffer.set_highlight_syntax(False)
            else:
                if self.uicore.backend == 'radare':
                    if va == "false":
                        self.uicore.core.cmd0('e io.va=1')
                        if addr != 0:
                            addr = self.uicore.core.io.section_offset_to_vaddr(addr)
                        else:
                            addr = 'section..text'
                    self.uicore.core.cmd0('s ' + str(addr))
                self.buffer.set_highlight_syntax(True)

            self.refresh()

    def move(self, widget, direction):
        data = self.uicore.move(direction, self.output_type)
        if data:
            self.buffer.set_text(data)

    def set_buffer_size(self, widget, icon_pos=None, event=None):
        if self.buffer_entry.get_text().isdigit():
            size = int(self.buffer_entry.get_text())
            if self.uicore.backend == 'pyew':
                self.uicore.core.bsize = size
            elif self.uicore.backend == 'radare':
                self.uicore.set_bsize(size)
            self.buffer_entry.set_text('')
            self.refresh()

    def r2_exec(self, widget, icon_pos=None, event=None):
        command = self.exec_entry.get_text()
        res = self.uicore.execute_command(command)
        self.buffer.set_text(res)
        self.exec_entry.set_text('')
        self.exec_entry.grab_focus()

    def seek(self, widget, icon_pos=None, event=None, action=''):
        if action == '':
            pos = self.seek_entry.get_text()
        else:
            pos = action
    
        if self.uicore.backend == 'pyew':
            if pos.lower() in ["ep", "entrypoint"]:
                if self.uicore.core.ep:
                    pos = self.uicore.core.ep
    
            elif pos.isdigit() and int(pos) < len(self.uicore.core.calls)+1 and int(pos) > 0:
                pos = self.uicore.core.calls[int(pos)-1]
    
            elif pos in self.uicore.core.names.values():
                for x in self.uicore.core.names:
                    if self.uicore.core.names[x] == pos:
                        pos = x
                        break
            elif pos.lower().startswith("0x"):
                pos = int(pos, 16)
#            elif pos == 'b':
#                data = self.uicore.move('b', self.output_type)
#                print data
#                if data:
#                    self.buffer.set_text(data)
#                self.refresh()
            else:
                pos = int(pos)
            self.uicore.seek(pos)
    
        elif self.uicore.backend == 'radare':
            self.uicore.seek(pos)

        if widget.get_name() == 'GtkEntry':
            self.seek_entry.set_text('')
            self.seek_entry.grab_focus()

        self.refresh()

    def refresh(self):
        if self.output_type == 'hexadecimal':
            hexdump = self.uicore.get_hexdump()
            self.buffer.set_text(hexdump)
        else:
            dasm = self.uicore.get_dasm()
            self.buffer.set_text(dasm)

    def set_completion(self):
        # Seek entry EntryCompletion
        self.completion = gtk.EntryCompletion()
        self.liststore = gtk.ListStore(str)
        # Add function names to the list
        for function in self.uicore.allfuncs:
            self.liststore.append([function])

        self.completion.set_model(self.liststore)
        self.seek_entry.set_completion(self.completion)
        self.completion.set_text_column(0)
        #self.completion.connect('match-selected', self.match_cb)
        #self.seek_entry.connect('activate', self.activate_cb)

# Used to create most of the buttons
#
class SemiStockButton(gtk.Button):
    '''Takes the image from the stock, but the label which is passed.
    
    @param text: the text that will be used for the label
    @param image: the stock widget from where extract the image
    @param tooltip: the tooltip for the button

    @author: Facundo Batista <facundobatista =at= taniquetil.com.ar>
    '''
    def __init__(self, text, image, tooltip=None):
        super(SemiStockButton,self).__init__(stock=image)
        align = self.get_children()[0]
        box = align.get_children()[0]
        (self.image, self.label) = box.get_children()
        self.label.set_text(text)
        if tooltip is not None:
            self.set_tooltip_text(tooltip)
            
    def changeInternals(self, newtext, newimage, tooltip=None):
        '''Changes the image and label of the widget.
    
        @param newtext: the text that will be used for the label
        @param newimage: the stock widget from where extract the image
        @param tooltip: the tooltip for the button
        '''
        self.label.set_text(newtext)
        self.image.set_from_stock(newimage, gtk.ICON_SIZE_BUTTON)
        if tooltip is not None:
            self.set_tooltip_text(tooltip)
