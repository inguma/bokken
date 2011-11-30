##      file_dialog.py
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
import gobject

class FileDialog(gtk.Dialog):
    '''Window popup to select file'''

    def __init__(self, has_pyew, has_radare, core='', file=''):
        super(FileDialog,self).__init__('Select file', None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT, gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))

        self.has_pyew = has_pyew
        self.has_radare = has_radare

        self.core = core
        self.file = file

        self.timer_id = None

        # Set dialog resizeable and auto-shrink
        self.set_policy(False, False, True)
        self.set_icon_from_file(os.path.dirname(__file__)+os.sep+'data'+os.sep+'bokken.svg')

        # the cancel button
        self.butt_ok = self.action_area.get_children()[0]
        self.butt_ok.connect("clicked", self.fast_start)
        self.butt_cancel = self.action_area.get_children()[1]
        #self.butt_cancel.connect("clicked", self.cancel)

        # Window position
        self.set_position(gtk.WIN_POS_CENTER)

        # Main Vertical Box
        self.main_vbox = gtk.VBox(False, 2)
        self.main_vbox.set_border_width(7)

        # Logo
        self.logo = gtk.Image()
        self.logo.set_from_file(os.path.dirname(__file__)+os.sep+'data'+os.sep+'bokken.svg')
        # Logo label
        self.logo_text = gtk.Label()
        self.logo_text.set_markup('<span size=\'12000\'>Welcome to <b>Bokken 1.5</b></span>')

        # Common label
        self.label = gtk.Label('Select a target or enter the path manually.')
        self.label.set_padding(0, 3)
        self.label.set_alignment(0, 0.5)

        # Pyew targets label
        self.pyew_label = gtk.Label()
        self.pyew_label.set_markup('Valid inputs are: <b>PE/ELF, PDF, plain text files and URLs</b>')
        self.pyew_label.set_padding(0, 2)

        # Radare targets label
        self.radare_label = gtk.Label()
        self.radare_label.set_markup('Valid inputs are: <b>PE, ELF, mach0 and java/dex classes</b>')
        self.radare_label.set_padding(0, 2)

        # Horizontal Separator
        self.hseparator1 = gtk.HSeparator()

        # Core selection label and combo
        self.core_label = gtk.Label('Select backend to use: ')
        self.core_label.set_alignment(0, 0.5)
        self.core_combo = gtk.combo_box_new_text()

        if self.has_pyew:
            self.core_combo.append_text('Pyew')
        if self.has_radare:
            self.core_combo.append_text('Radare')

        if not self.core:
            self.core_combo.set_active(0)
        elif self.has_radare != self.has_pyew:
            self.core_combo.set_active(0)
        elif self.core == 'pyew':
            self.core_combo.set_active(0)
        elif self.core == 'radare':
            self.core_combo.set_active(1)
        self.core = self.core_combo.get_active_text().lower()

        # Core combo Horizontal Box
        self.core_hbox = gtk.HBox(False, 0)
        self.core_hbox.pack_start(self.core_label, True, True, 2)
        self.core_hbox.pack_start(self.core_combo, False, False, 2)
        # Horizontal Separator
        self.hseparator2 = gtk.HSeparator()

        # File selection Horizontal Box
        self.hbox = gtk.HBox(False, 0)
        # TextEntry
        self.model = gtk.ListStore(str)
        self.input_entry = gtk.ComboBoxEntry(self.model, column=0)
        self.input_entry.get_child().connect("activate", self.fast_start)
        self.input_entry.connect("changed", self._validate_cb)
        #self.input_entry = gtk.Entry(100)
        if self.file:
            self.input_entry.get_child().set_text(self.file)
        # Recent file manager
        self.manager = gtk.recent_manager_get_default()
        items = self.manager.get_items()
        for element in items[:10]:
            self.model.append( [element.get_display_name()])
        # Select file button
        icon = gtk.Image()
        icon.set_from_stock(gtk.STOCK_OPEN, gtk.ICON_SIZE_MENU)
        self.select_button = gtk.Button()
        self.select_button.set_image(icon)
        self.select_button.connect("clicked", self.select_file)
        # Pack elements into hbox
        self.hbox.pack_start(self.input_entry, True, True, 2)
        self.hbox.pack_start(self.select_button, False, False, 2)

        # File options Horizontal Box
        self.options_hbox = gtk.HBox(False, 2)
        # Pyew option Vertical Box
        self.pyew_box = gtk.VBox(False, 0)
        # Radare option Vertical Box
        self.radare_box = gtk.VBox(False, 0)
        # pack the boxes
        self.options_hbox.pack_start(self.pyew_box, False, False, 0)
        self.options_hbox.pack_start(self.radare_box, False, False, 0)

        # HSeparator
        self.hseparator3 = gtk.HSeparator()
        # Analysis options label
        self.anal_label = gtk.Label()
        self.anal_label.set_markup("<b>Analysis options:</b>")

        # Pyew options
        self.deep_anal = gtk.CheckButton(label='Deep analysis')
        self.case_dasm = gtk.CheckButton(label='Lower case disassembly')
        self.case_dasm.set_active(True)
        self.pyew_box.pack_start(self.deep_anal, False, False, 2)
        self.pyew_box.pack_start(self.case_dasm, False, False, 2)
        # It's here to avoid errors during start up
        self.core_combo.connect("changed", self._on_change)

        # Radare options
        self.anal_bin = gtk.CheckButton(label='Analyze program')
        self.anal_bin.set_active(True)
        self.radare_dasm = gtk.CheckButton(label='Lower case disassembly')
        self.radare_dasm.set_active(True)
        self.io_va = gtk.CheckButton(label='Don\'t use VA')
        self.asm_syntax = gtk.CheckButton(label='Use AT&T syntax')
        self.asm_bytes = gtk.CheckButton(label='Don\'t show asm bytes')
        self.anal_bin.connect("toggled", self._no_anal)
        self.radare_box.pack_start(self.anal_bin, False, False, 2)
        self.radare_box.pack_start(self.radare_dasm, False, False, 2)
        self.radare_box.pack_start(self.io_va, False, False, 2)
        self.radare_box.pack_start(self.asm_syntax, False, False, 2)
        self.radare_box.pack_start(self.asm_bytes, False, False, 2)

        # Pack elements into main_vbox
        self.main_vbox.pack_start(self.logo, False, False, 0)
        self.main_vbox.pack_start(self.logo_text, False, False, 0)
        self.main_vbox.pack_start(self.hseparator1, False, False, 2)
        self.main_vbox.pack_start(self.core_hbox, False, False, 2)
        self.main_vbox.pack_start(self.hseparator2, False, False, 2)
        self.main_vbox.pack_start(self.label, False, False, 2)
        self.main_vbox.pack_start(self.pyew_label, False, False, 1)
        self.main_vbox.pack_start(self.radare_label, False, False, 1)
        self.main_vbox.pack_start(self.hbox, False, False, 2)
        self.main_vbox.pack_start(self.hseparator3, False, False, 2)
        self.main_vbox.pack_start(self.anal_label, False, False, 2)
        self.main_vbox.pack_start(self.options_hbox, False, False, 2)

        self.vbox.pack_start(self.main_vbox)
        self.set_focus(self.input_entry.get_child())
        self.show_all()

        if self.core == 'pyew':
            self.radare_box.set_visible(False)
            self.radare_label.set_visible(False)
        elif self.core == 'radare':
            self.pyew_box.set_visible(False)
            self.pyew_label.set_visible(False)
        else:
            self.radare_box.set_visible(False)
            self.radare_label.set_visible(False)

    def cancel(self, widget):
        import sys
        sys.exit(1)
        self.destroy()

    def get_file(self, widget):
        import re
        import ui.core_functions

        # Disable all the interface and Ok button.
        self.core_hbox.set_sensitive(False)
        self.hbox.set_sensitive(False)
        self.options_hbox.set_sensitive(False)
        self.butt_ok.set_sensitive(False)

        # Progress bar
        self.progress_box = gtk.VBox(False, 0)
        self.hseparator4 = gtk.HSeparator()
        self.progress_bar = gtk.ProgressBar()
        self.progress_box.pack_start(self.hseparator4, False, False, 0)
        self.progress_box.pack_start(self.progress_bar, False, False, 0)

        self.main_vbox.pack_start(self.progress_box, False, False, 2)
        self.progress_box.show_all()

        ui.core_functions.repaint()

        self.file = self.input_entry.get_child().get_text()
        if not re.match('[a-z]+://', self.file):
            # It's a local file.
            self.manager.add_item('file://' + self.file)
        self.get_backend()
        self.get_options()
        self.response(0)

    def fast_start(self, widget):
        self.file = self.input_entry.get_child().get_text()
        if self.file:
            self.get_file(widget)
        else:
            self.select_file(widget)

    def get_backend(self):
        self.backend = self.core_combo.get_active_text().lower()

    def get_options(self):
        active = self.core_combo.get_active_text()
        if active == 'Pyew':
            self.deep = self.deep_anal.get_active()
            self.case = self.case_dasm.get_active()
        if active == 'Radare':
            self.analyze_bin = self.anal_bin.get_active()
            self.radare_lower = self.radare_dasm.get_active()
            self.use_va = self.io_va.get_active()
            self.asm_syn = self.asm_syntax.get_active()
            self.asm_byt = self.asm_bytes.get_active()

    def select_file(self, widget):
        chooser = gtk.FileChooserDialog(title="Select target",action=gtk.FILE_CHOOSER_ACTION_OPEN,
                              buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
        self.resp = chooser.run()
        if self.resp == gtk.RESPONSE_OK:
            self.file_name = chooser.get_filename()
            self.input_entry.get_child().set_text(self.file_name)
        chooser.destroy()

    def _validate_cb(self, widget):
        if self.timer_id:
            # We destroy the last event source and create another one.
            gobject.source_remove(self.timer_id)
        self.timer_id = gobject.timeout_add(500, self._validate, widget.get_child())

    def _validate(self, widget):
        text = widget.get_text()
        core = self.core_combo.get_active_text()
        colormap = widget.get_colormap()
        bg_ok = colormap.alloc_color("white")
        bg_not_valid = colormap.alloc_color("red")
        if 'http' in text:
            if core == 'Radare':
                widget.modify_base(gtk.STATE_NORMAL, bg_not_valid)
            else:
                widget.modify_base(gtk.STATE_NORMAL, bg_ok)
        elif not os.path.isfile(text):
            widget.modify_base(gtk.STATE_NORMAL, bg_not_valid)
        else:
            widget.modify_base(gtk.STATE_NORMAL, bg_ok)

    def _on_change(self, widget):
        active = widget.get_active_text()
        if active == 'Pyew':
            self.pyew_box.set_visible(True)
            self.radare_box.set_visible(False)
            self.pyew_label.set_visible(True)
            self.radare_label.set_visible(False)
        elif active == 'Radare':
            self.pyew_box.set_visible(False)
            self.radare_box.set_visible(True)
            self.pyew_label.set_visible(False)
            self.radare_label.set_visible(True)

        self._validate(self.input_entry.get_child())

    def _no_anal(self, widget):
        if widget.get_active():
            self.radare_dasm.set_sensitive(True)
            self.io_va.set_sensitive(True)
            self.asm_syntax.set_sensitive(True)
            self.asm_bytes.set_sensitive(True)
        else:
            self.radare_dasm.set_sensitive(False)
            self.io_va.set_sensitive(False)
            self.asm_syntax.set_sensitive(False)
            self.asm_bytes.set_sensitive(False)
