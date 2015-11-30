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

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
import ui.gtk3.common
from lib.common import datafile_path

import lib.bokken_globals as glob

class FileDialog(Gtk.Dialog):
    '''Window popup to select file'''

    def __init__(self, main, file='', first_run=False):
        super(FileDialog,self).__init__('Select file', main.window, Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT, (Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT, Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT))

        self.file = file

        self.timer_id = None

        # Set dialog resizeable and auto-shrink
        self.set_resizable(False)
        ui.gtk3.common.set_bokken_icon(self)

        # The Ok Button.
        self.butt_ok = self.action_area.get_children()[1]
        self.butt_ok.connect("clicked", self.fast_start)
        self.butt_ok.set_sensitive(False)
        # The Cancel button.
        self.butt_cancel = self.action_area.get_children()[0]
        self.butt_cancel.connect("clicked", self.cancel)

        # Window position
        self.set_position(Gtk.WindowPosition.CENTER)

        # Main Vertical Box
        self.main_vbox = Gtk.VBox(False, 2)
        self.main_vbox.set_border_width(7)

        # Logo
        self.logo = Gtk.Image()
        self.logo.set_from_file(datafile_path('bokken.svg'))
        # Logo label
        self.logo_text = Gtk.Label()
        self.logo_text.set_markup('<span size=\'12000\'>Welcome to <b>Bokken '+glob.version+'</b></span>')

        # Common label
        self.label = Gtk.Label(label='Select a target or enter the path manually.')
        self.label.set_padding(0, 3)
        self.label.set_alignment(0, 0.5)

        # Radare targets label
        self.radare_label = Gtk.Label()
        self.radare_label.set_markup('Valid inputs are: <b>PE, ELF and mach0</b> files')
        self.radare_label.set_padding(0, 2)

        # Horizontal Separator
        self.hseparator1 = Gtk.HSeparator()

        self.plugins = []

        from ui.radare_core import Core as UICore
        self.plugins = UICore.get_plugins()

        # Horizontal Separator
        self.hseparator2 = Gtk.HSeparator()

        # File selection Horizontal Box
        self.hbox = Gtk.HBox(False, 0)
        # TextEntry
        self.model = Gtk.ListStore(str)
        self.input_entry = Gtk.ComboBox.new_with_model_and_entry(self.model)
        self.input_entry.get_child().connect("activate", self.fast_start)
        self.input_entry.connect("changed", self._validate_cb)
        #self.input_entry = Gtk.Entry(100)
        if self.file:
            self.input_entry.get_child().set_text(self.file)
        # Recent file manager
        self.manager = Gtk.RecentManager.get_default()
        items = self.manager.get_items()
        for element in items[:10]:
            if element.get_uri_display():
                self.model.append([element.get_uri_display()])
        # Select file button
        icon = Gtk.Image()
        icon.set_from_stock(Gtk.STOCK_OPEN, Gtk.IconSize.MENU)
        self.select_button = Gtk.Button()
        self.select_button.set_image(icon)
        self.select_button.connect("clicked", self.select_file)
        # Pack elements into hbox
        self.hbox.pack_start(self.input_entry, True, True, 2)
        self.hbox.pack_start(self.select_button, False, False, 2)

        # File options Horizontal Box
        self.options_hbox = Gtk.HBox(False, 2)

        # Radare option Vertical Box
        self.radare_box = Gtk.VBox(False, 0)
        self.vseparator = Gtk.VSeparator()
        self.radare_box_2 = Gtk.VBox(False, 0)
        self.radare_box_3 = Gtk.VBox(False, 0)
        # pack the boxes
        self.options_hbox.pack_start(self.radare_box, True, True, 0)
        self.options_hbox.pack_start(self.vseparator, False, False, 5)
        self.options_hbox.pack_start(self.radare_box_2, True, True, 0)

        # HSeparator
        self.hseparator3 = Gtk.HSeparator()
        # Analysis options label
        self.anal_label = Gtk.Label()
        self.anal_label.set_markup("<b>Analysis options:</b>")
        # Advanced Analysis options label
        self.adv_anal_label = Gtk.Label()
        self.adv_anal_label.set_markup("<b>Advanced options:</b>")

        # Radare options
        self.anal_bin = Gtk.CheckButton(label='Analyze program')
        self.anal_bin.set_active(True)
        self.anal_bin.connect("toggled", self._no_anal)
        self.anal_depth_label = Gtk.Label(label='Max analysis depth: ')
        self.anal_depth_entry = Gtk.Entry()
        self.anal_depth_entry.set_max_length(3)
        self.anal_depth_entry.set_width_chars(3)
        self.anal_depth_entry.set_max_width_chars(3)
        self.anal_depth_entry.set_text('16')
        self.radare_dasm = Gtk.CheckButton(label='Lower case disassembly')
        self.radare_dasm.set_active(True)
        self.io_va = Gtk.CheckButton(label='Don\'t use VA')
        self.asm_syntax = Gtk.CheckButton(label='Use AT&T syntax')
        self.asm_bytes = Gtk.CheckButton(label='Don\'t show asm bytes')

        # Bottom radare2 options
        self.hseparator5 = Gtk.HSeparator()
        self.bits_label = Gtk.Label(label='Bits:')
        self.bits = Gtk.ComboBoxText()
        #self.bits.set_size_request(70, -1)
        self.arch_label = Gtk.Label(label='Architecture:')
        self.arch = Gtk.ComboBoxText()
        self.arch.connect("changed", self._arch_changed)
        self.arch.append_text('Auto')
        for plugin in self.plugins:
            self.arch.append_text('%s (%s)' % (plugin.name, plugin.arch))
            #self.arch.append_text('%s (%s) - %s' % (plugin.name, plugin.arch, plugin.desc))
        self.arch.set_active(0)
        self.start_addr = Gtk.CheckButton(label='Start address: ')
        self.start_addr.connect("toggled", self._start_addr_ctl)
        self.start_addr_label = Gtk.Label()
        self.start_addr_label.set_markup('<b>0x</b>')
        self.start_addr_label.set_padding(0, 5)
        self.start_addr_address = Gtk.Entry()
        self.start_addr_address.set_max_length(12)
        self.start_addr_address.set_width_chars(12)
        self.start_addr_address.set_sensitive(False)

        # More radare2 options
        self.stack_check = Gtk.CheckButton(label='Show stack pointer')
        self.pseudo_check = Gtk.CheckButton(label='Enable pseudo syntax')
        self.flow_lines = Gtk.CheckButton(label='Show flow lines')
        self.flow_lines.connect("toggled", self._flow_lines_ctl)
        self.flow_lines_label = Gtk.Label(label='Columns for flow lines: ')
        self.flow_lines_entry = Gtk.Entry()
        self.flow_lines_entry.set_max_length(3)
        self.flow_lines_entry.set_width_chars(3)
        self.flow_lines_entry.set_max_width_chars(3)
        self.flow_lines_entry.set_text('20')
        self.flow_lines_entry.set_sensitive(False)

        # Pack them
        self.flow_hbox = Gtk.HBox(False)
        self.depth_hbox = Gtk.HBox(False)
        self.radare_box_2.pack_start(self.pseudo_check, False, False, 2)
        self.radare_box_2.pack_start(self.stack_check, False, False, 2)
        self.radare_box_2.pack_start(self.asm_bytes, False, False, 2)
        self.radare_box_2.pack_start(self.flow_lines, False, False, 2)
        self.flow_hbox.pack_start(self.flow_lines_label, False, False, 2)
        self.flow_hbox.pack_start(self.flow_lines_entry, False, False, 2)
        self.radare_box_2.pack_start(self.flow_hbox, False, False, 2)
        self.depth_hbox.pack_start(self.anal_depth_label, False, False, 2)
        self.depth_hbox.pack_start(self.anal_depth_entry, False, False, 2)

        self.radare_box.pack_start(self.anal_bin, False, False, 2)
        self.radare_box.pack_start(self.depth_hbox, False, False, 2)
        self.radare_box.pack_start(self.radare_dasm, False, False, 2)
        self.radare_box.pack_start(self.io_va, False, False, 2)
        self.radare_box.pack_start(self.asm_syntax, False, False, 2)
        self.start_addr_hbox = Gtk.HBox(False, 0)
        self.start_addr_hbox.pack_start(self.start_addr, False, False, 0)
        self.start_addr_hbox.pack_start(self.start_addr_label, False, False, 2)
        self.start_addr_hbox.pack_start(self.start_addr_address, True, True, 2)
        self.radare_box_3.pack_start(self.hseparator5, False, False, 5)
        self.radare_box_3.pack_start(self.adv_anal_label, False, False, 5)
        self.radare_box_3.pack_start(self.start_addr_hbox, False, False, 2)
        self.arch_hbox = Gtk.HBox(False, 0)
        self.arch_hbox.pack_start(self.arch_label, False, False, 2)
        self.arch_hbox.pack_start(self.arch, True, True, 2)
        self.radare_box_3.pack_start(self.arch_hbox, False, False, 2)
        self.bits_hbox = Gtk.HBox(False, 0)
        self.bits_hbox.pack_start(self.bits_label, False, False, 2)
        self.bits_hbox.pack_start(self.bits, False, False, 2)
        #self.radare_box_3.pack_start(self.bits_hbox, False, False, 2)
        self.arch_hbox.pack_start(self.bits_hbox, False, False, 2)

        # Pack elements into main_vbox
        self.main_vbox.pack_start(self.logo, False, False, 0)
        self.main_vbox.pack_start(self.logo_text, False, False, 0)
        self.main_vbox.pack_start(self.hseparator1, False, False, 2)
        #self.main_vbox.pack_start(self.hseparator2, False, False, 2)
        self.main_vbox.pack_start(self.label, False, False, 2)
        self.main_vbox.pack_start(self.radare_label, False, False, 1)
        self.main_vbox.pack_start(self.hbox, False, False, 2)
        self.main_vbox.pack_start(self.hseparator3, False, False, 2)
        self.main_vbox.pack_start(self.anal_label, False, False, 2)
        self.main_vbox.pack_start(self.options_hbox, False, False, 2)
        self.main_vbox.pack_start(self.radare_box_3, False, False, 2)

        self.vbox.pack_start(self.main_vbox, True, True, 0)
        self.set_focus(self.input_entry.get_child())
        self.show_all()

    def cancel(self, widget):
        self.destroy()

    def get_file(self, widget):
        import re
        import ui.gtk3.common

        # Disable all the interface and Ok button.
        self.hbox.set_sensitive(False)
        self.options_hbox.set_sensitive(False)
        self.butt_ok.set_sensitive(False)

        # Progress bar
        self.progress_box = Gtk.VBox(False, 0)
        self.hseparator4 = Gtk.HSeparator()
        self.progress_bar = Gtk.ProgressBar()
        self.progress_box.pack_start(self.hseparator4, False, False, 0)
        self.progress_box.pack_start(self.progress_bar, False, False, 0)

        self.main_vbox.pack_start(self.progress_box, False, False, 2)
        self.progress_box.show_all()

        ui.gtk3.common.repaint()

        self.file = self.input_entry.get_child().get_text()
        if not re.match('^[a-z]+://', self.file):
            # It's a local file.
            self.manager.add_item('file://' + self.file)
        self.get_options()
        self.response(0)

    def fast_start(self, widget):
        self.file = self.input_entry.get_child().get_text()
        if self.file:
            self.get_file(widget)
        else:
            self.select_file(widget)

    def get_options(self):
        self.opt_analyze_bin = self.anal_bin.get_active()
        self.opt_case = self.radare_dasm.get_active()
        self.opt_use_va = self.io_va.get_active()
        self.opt_asm_syntax = self.asm_syntax.get_active()
        self.opt_asm_bytes = self.asm_bytes.get_active()
        self.opt_start_addr = self.start_addr_address.get_text()
        self.opt_arch = None
        self.opt_bits = None
        self.opt_pseudo = self.pseudo_check.get_active()
        self.opt_stack = self.stack_check.get_active()
        self.opt_flow_lines = self.flow_lines.get_active()
        self.opt_flow_lines_w = self.flow_lines_entry.get_text()
        self.opt_anal_depth = self.anal_depth_entry.get_text()
        if self.arch.get_active_text() is not None:
            index = self._find_active_index(self.arch)
            if index >= 0:
                self.opt_arch = self.plugins[index].name
        if self.bits.get_active_text() is not None and self.bits.get_active_text() != 'Auto':
            self.opt_bits = self.bits.get_active_text()

    def select_file(self, widget):
        chooser = Gtk.FileChooserDialog(title="Select target",action=Gtk.FileChooserAction.OPEN,
                              buttons=(Gtk.STOCK_CANCEL,Gtk.ResponseType.CANCEL,Gtk.STOCK_OPEN,Gtk.ResponseType.OK))
        self.resp = chooser.run()
        if self.resp == Gtk.ResponseType.OK:
            self.file_name = chooser.get_filename()
            self.input_entry.get_child().set_text(self.file_name)
        chooser.destroy()

    def _find_active_index(self, combobox):
        index = combobox.get_active()
        if combobox.get_model()[0][0] == 'Auto':
            index -= 1
        return index

    def _validate_cb(self, widget):
        # We create a timeout object to avoid fast lookups on disk when typing.
        self.timer_id = GObject.timeout_add(500, self._validate, widget.get_child())

    def _validate(self, widget):
        text = widget.get_text()
        core = 'radare'
        #colormap = widget.get_colormap()
        #bg_ok = colormap.alloc_color("white")
        parse, bg_ok = Gdk.Color.parse('white')
        #bg_not_valid = colormap.alloc_color("red")
        parse, bg_not_valid = Gdk.Color.parse('red')
        if len(text)==0:
            widget.modify_base(Gtk.StateType.NORMAL, bg_ok)
            self.butt_ok.set_sensitive(False)
        elif not os.path.isfile(text):
            widget.modify_base(Gtk.StateType.NORMAL, bg_not_valid)
            self.butt_ok.set_sensitive(False)
        else:
            widget.modify_base(Gtk.StateType.NORMAL, bg_ok)
            self.butt_ok.set_sensitive(True)

    def _start_addr_ctl(self, widget):
        if widget.get_active():
            self.start_addr_address.set_sensitive(True)
        else:
            self.start_addr_address.set_text('')
            self.start_addr_address.set_sensitive(False)

    def _flow_lines_ctl(self, widget):
        if widget.get_active():
            self.flow_lines_entry.set_sensitive(True)
        else:
            self.flow_lines_entry.set_sensitive(False)

    def _no_anal(self, widget):
        if widget.get_active():
            self.io_va.set_sensitive(True)
            self.asm_bytes.set_sensitive(True)
            self.start_addr.set_sensitive(True)
            self.pseudo_check.set_sensitive(True)
            self.stack_check.set_sensitive(True)
            self.flow_lines.set_sensitive(True)
            self.anal_depth_entry.set_sensitive(True)
            self.arch.set_sensitive(True)
        else:
            self.io_va.set_active(False)
            self.io_va.set_sensitive(False)
            self.asm_bytes.set_active(False)
            self.asm_bytes.set_sensitive(False)
            self.start_addr.set_active(False)
            self.start_addr.set_sensitive(False)
            self.pseudo_check.set_sensitive(False)
            self.stack_check.set_sensitive(False)
            self.flow_lines.set_sensitive(False)
            self.anal_depth_entry.set_sensitive(False)
            self.arch.set_sensitive(False)
            self._start_addr_ctl(self.start_addr)
            self._flow_lines_ctl(self.flow_lines)

    def _arch_changed(self, combobox):
        if combobox.get_active_text() != 'Auto':
            plugin_bits = self.plugins[self._find_active_index(combobox)].bits
            self.bits.set_sensitive(True)
            self.bits.get_model().clear()
            count = 0
            for bit in [8, 16, 32, 64]:
                if plugin_bits & bit == bit:
                    self.bits.append_text(str(bit))
                    count += 1
            if count >= 2:
                self.bits.prepend_text('Auto')
            self.bits.set_active(0)
        else:
            self.bits.get_model().clear()
            self.bits.set_sensitive(False)
