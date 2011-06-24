#!/usr/bin/python

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

        # Previous buffer button
        b = SemiStockButton("", gtk.STOCK_GO_UP, 'Previous buffer')
        b.connect("clicked", self.move, 'b')
        b.label.label = 'Previous'
        self.toolbox.pack_start(b, False, False)

        # Next buffer button
        b = SemiStockButton("", gtk.STOCK_GO_DOWN, 'Next buffer')
        b.connect("clicked", self.move, 'f')
        b.label.label = 'Next'
        self.toolbox.pack_start(b, False, False)

        # Separator
        self.sep = gtk.HSeparator()
        self.toolbox.pack_start(self.sep, False, False)

        # Seek to...
        self.seek_label = gtk.Label('     Seek:')
        self.toolbox.pack_start(self.seek_label, False, False)

        self.seek_entry = gtk.Entry(20)
        # Default action on pressing Enter
        self.seek_entry.set_activates_default(True)
        self.seek_entry.connect("activate", self.seek)

        self.toolbox.pack_start(self.seek_entry, False, False)
        b = SemiStockButton("", gtk.STOCK_GO_FORWARD, 'Go')
        b.connect("clicked", self.seek)
        self.toolbox.pack_start(b, False, False)

        # Separator
        self.sep = gtk.HSeparator()
        self.toolbox.pack_start(self.sep, False, False)

        # Buffer size
        self.buffer_label = gtk.Label('     Buffer size:')
        self.toolbox.pack_start(self.buffer_label, False, False)

        self.buffer_entry = gtk.Entry(10)
        self.buffer_entry.set_text('512')
        # Default action on pressing Enter
        self.buffer_entry.set_activates_default(True)
        self.buffer_entry.connect("activate", self.set_buffer_size)

        self.toolbox.pack_start(self.buffer_entry, False, False)
        b = SemiStockButton("", gtk.STOCK_APPLY, 'Apply')
        b.connect("clicked", self.set_buffer_size)
        self.toolbox.pack_start(b, False, False)

        # Separator
        self.sep = gtk.HSeparator()
        self.toolbox.pack_start(self.sep, False, False)

        # Radio buttons (output format)
        self.hex_button = gtk.RadioButton(None, "Hexadecimal")
        self.hex_button.connect("toggled", self.callback, "Hexadecimal")
        self.hex_button.set_active(True)
        self.toolbox.pack_start(self.hex_button, False, False)

        self.dasm_button = gtk.RadioButton(self.hex_button, "Disassemby")
        self.dasm_button.connect("toggled", self.callback, "Disassembly")
        self.toolbox.pack_start(self.dasm_button, False, False)

        self.uicore.pyew.bsize = 512

    #
    # Functions
    #
    def callback(self, widget, data=None):
        if widget.get_active() == True:
            self.output_type = data.lower()

            # Only highlight syntax for disassembly
            if self.output_type == 'hexadecimal':
                self.buffer.set_highlight_syntax(False)
            else:
                self.buffer.set_highlight_syntax(True)

            self.refresh()

    def move(self, widget, direction):
        data = self.uicore.move(direction, self.output_type)
        if data:
            self.buffer.set_text(data)

    def set_buffer_size(self, widget):
        size = int(self.buffer_entry.get_text())
        self.uicore.pyew.bsize = size
        self.refresh()

    def seek(self, widget):
        pos = self.seek_entry.get_text()

        if pos.lower() in ["ep", "entrypoint"]:
            if self.uicore.pyew.ep:
                pos = self.uicore.pyew.ep

        elif pos.isdigit() and int(pos) < len(self.uicore.pyew.calls)+1 and int(pos) > 0:
            pos = self.uicore.pyew.calls[int(pos)-1]

        elif pos in self.uicore.pyew.names.values():
            for x in self.uicore.pyew.names:
                if self.uicore.pyew.names[x] == pos:
                    pos = x
                    break
        elif pos.lower().startswith("0x"):
            pos = int(pos, 16)
#        elif pos == 'b':
#            data = self.uicore.move('b', self.output_type)
#            print data
#            if data:
#                self.buffer.set_text(data)
#            self.refresh()
        else:
            pos = int(pos)
        self.uicore.seek(pos)

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
