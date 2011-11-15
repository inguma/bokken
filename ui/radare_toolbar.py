#       radare_toolbar.py
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

FAIL = '\033[91m'
OKGREEN = '\033[92m'
ENDC = '\033[0m'

# We need it for the "New" button
import ui.file_dialog as file_dialog
import ui.diff_dialog as diff_dialog
import ui.sections_dialog as sections_dialog
import ui.calc_dialog as calc_dialog
import ui.throbber as throbber

class TopButtons(gtk.HBox):
    '''Top Buttons'''

    def __init__(self, core, main):
        super(TopButtons,self).__init__(False, 1)

        self.main = main

        self.uicore = core
        self.toolbox = self
        self.dependency_check = self.main.dependency_check

        self.img_path = os.path.dirname(__file__) + os.sep + 'data' + os.sep
        self.options_dict = {'String':' ', 'String no case':'i ', 'Hexadecimal':'x ', 'Regexp':'e '}

        self.main_tb = gtk.Toolbar()
        self.main_tb.set_style(gtk.TOOLBAR_ICONS)

        # New file button
        self.new_tb = gtk.MenuToolButton(gtk.STOCK_NEW)
        self.new_tb.set_label('New')
        self.new_tb.set_tooltip_text('Open new file')
        self.new_tb.connect("clicked", self.new_file)
        self.main_tb.insert(self.new_tb, 0)

        # Recent files menu
        self.manager = gtk.recent_manager_get_default()
        self.recent_menu = gtk.RecentChooserMenu(self.manager)
        self.new_tb.set_menu(self.recent_menu)
        self.new_tb.set_arrow_tooltip_text('Recent opened files')
        self.recent_menu.connect('item-activated', self.recent_kb)

        # Separator
        self.sep = gtk.SeparatorToolItem()
        self.main_tb.insert(self.sep, 1)

        # Assembler button
        self.asm_tb = gtk.ToolButton(gtk.STOCK_EXECUTE)
        self.asm_tb.set_tooltip_text('Open assembler dialog')
        self.asm_tb.connect("clicked", self._assembler)
        self.main_tb.insert(self.asm_tb, 2)

        # Bindiff button
        self.diff_tb = gtk.ToolButton(gtk.STOCK_REFRESH)
        self.diff_tb.set_tooltip_text('Do binary diffing')
        self.diff_tb.connect("clicked", self._do_diff)
        self.main_tb.insert(self.diff_tb, 3)

        # Section bars button
        self.sections_tb = gtk.ToolButton(gtk.STOCK_SORT_ASCENDING)
        self.sections_tb.set_tooltip_text('Extended sections information')
        self.sections_tb.connect("clicked", self._do_sections)
        self.main_tb.insert(self.sections_tb, 4)

        # Calculator button
        self.image = gtk.Image()
        self.image.set_from_file(os.path.dirname(__file__)+os.sep+'data'+os.sep+'calc.png')
        self.calc_tb = gtk.ToolButton()
        self.calc_tb.set_icon_widget(self.image)
        self.calc_tb.set_tooltip_text('Show calculator')
        self.calc_tb.connect("clicked", self._do_calc)
        self.main_tb.insert(self.calc_tb, 5)

        # File magic button
        self.magic_tb = gtk.ToolButton(gtk.STOCK_INFO)
        self.magic_tb.set_tooltip_text('Show file magic')
        self.magic_tb.connect("clicked", self._do_file_magic)
        self.main_tb.insert(self.magic_tb, 6)

        # Separator
        self.sep = gtk.SeparatorToolItem()
        self.main_tb.insert(self.sep, 7)

        # Search components
        self.search_combo_tb = gtk.ToolItem()
        self.search_combo_align = gtk.Alignment(yalign=0.5)
        store = gtk.ListStore(gtk.gdk.Pixbuf, str)
        self.search_combo = gtk.ComboBox(store)
        rendererText = gtk.CellRendererText()
        rendererPix = gtk.CellRendererPixbuf()
        self.search_combo.pack_start(rendererPix, False)
        self.search_combo.pack_start(rendererText, True)
        self.search_combo.add_attribute(rendererPix, 'pixbuf', 0)
        self.search_combo.add_attribute(rendererText, 'text', 1)

        options = {
            'String':gtk.gdk.pixbuf_new_from_file(os.path.dirname(__file__) + os.sep + 'data' + os.sep + 'icon_string_16.png'),
            'String no case':gtk.gdk.pixbuf_new_from_file(os.path.dirname(__file__) + os.sep + 'data' + os.sep + 'icon_string_no_case_16.png'),
            'Hexadecimal':gtk.gdk.pixbuf_new_from_file(os.path.dirname(__file__) + os.sep + 'data' + os.sep + 'icon_hexadecimal_16.png'),
            'Regexp':gtk.gdk.pixbuf_new_from_file(os.path.dirname(__file__) + os.sep + 'data' + os.sep + 'icon_regexp_16.png')
        }

        for option in options.keys():
            store.append([options[option], option])
        self.search_combo.set_active(0)
        self.search_combo_align.add(self.search_combo)
        self.search_combo_tb.add(self.search_combo_align)
        self.main_tb.insert(self.search_combo_tb, 8)

        # Separator
        self.sep = gtk.SeparatorToolItem()
        self.sep.set_draw(False)
        self.main_tb.insert(self.sep, 9)

        self.search_entry_tb = gtk.ToolItem()
        self.search_entry = gtk.Entry(100)
        self.search_entry.set_text('Text to search')
        self.search_entry.set_icon_from_stock(1, gtk.STOCK_FIND)
        self.search_entry.set_icon_tooltip_text(1, 'Search')
        self.search_entry.connect("activate", self.search)
        self.search_entry.connect("icon-press", self.search)
        self.search_entry.connect('focus-in-event', self._clean, 'in')
        self.search_entry.connect('focus-out-event', self._clean, 'out')
        self.search_entry_tb.add(self.search_entry)
        self.main_tb.insert(self.search_entry_tb, 10)

        # Separator
        self.sep = gtk.SeparatorToolItem()
        self.main_tb.insert(self.sep, 11)

        # Cheatsheet button
        self.cheatsheet_tb = gtk.ToolButton(gtk.STOCK_JUSTIFY_FILL)
        self.cheatsheet_tb.set_tooltip_text('Show assembler reference sheet')
        self.cheatsheet_tb.connect("clicked", self.create_cheatsheet_dialog)
        self.main_tb.insert(self.cheatsheet_tb, 12)

        # Separator
        self.sep = gtk.SeparatorToolItem()
        self.sep.set_expand(True)
        self.sep.set_draw(False)
        self.main_tb.insert(self.sep, 13)

        # Exit button
        self.exit_tb = gtk.ToolButton(gtk.STOCK_QUIT)
        self.exit_tb.set_label('Quit')
        self.exit_tb.connect("clicked", self.main.quit)
        self.exit_tb.set_tooltip_text('Have a nice day ;-)')
        self.main_tb.insert(self.exit_tb, 14)

        # Throbber
        self.throbber = throbber.Throbber()
        self.throbber_tb = gtk.ToolItem()
        self.throbber_tb.add(self.throbber)
        self.main_tb.insert(self.throbber_tb, 15)

        self.toolbox.pack_start(self.main_tb, True, True)

        self.show_all()

    #
    # Functions
    #

    # Private methods
    #

    def _clean(self, widget, event, data):
        if data == 'in':
            if widget.get_text() == 'Text to search':
                widget.set_text('')
        elif data == 'out':
            if widget.get_text() == '':
                widget.set_text('Text to search')

    def _do_diff(self, widget):
        #self.diff_widget = self.main.tviews.bindiff_widget
        chooser = diff_dialog.DiffDialog(self.uicore)
        self.response = chooser.run()
        if self.response in [gtk.RESPONSE_DELETE_EVENT, gtk.RESPONSE_REJECT, -3]:
            chooser.destroy()
        else:
            self.file_name = chooser.input_entry2.get_text()
            self.fcn_thr = int(chooser.scale.get_value())
            self.bb_thr = int(chooser.bb_scale.get_value())
            self.bytes = chooser.bytes_check.get_active()
            chooser.destroy()
            self.main.tviews.right_notebook.add_bindiff_tab(self.file_name, self.fcn_thr, self.bb_thr, self.bytes)
            #self.diff_widget.set_file(self.file_name)
            #self.diff_widget.diff()
            widget.set_sensitive(False)

    def _do_file_info(self, widget):
        self.main.tviews.right_notebook.add_info_elements_tab()
        widget.set_sensitive(False)

    def _do_file_magic(self, widget):
        self.uicore.core.cmd0('e io.va=0')
        self.uicore.core.cmd0('s 0')
        magic = self.uicore.core.cmd_str('pm')
        #self.uicore.core.cmd0('e io.va=1')
        if magic:
            md = gtk.MessageDialog(None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, 
                gtk.MESSAGE_INFO, gtk.BUTTONS_CLOSE, None)
            md.set_icon_from_file(os.path.dirname(__file__)+os.sep+'data'+os.sep+'bokken.svg')
            md.set_markup("<b>Detected file magic:</b>\n\n" + magic)
            md.run()
            md.destroy()

    def _do_sections(self, widget):
        self.sec_dialog = sections_dialog.SectionsDialog(self.uicore)
        return False

    def _do_calc(self, widget):
        self.calc_dialog = calc_dialog.CalcDialog(self.uicore)
        return False

    def _assembler(self, widgets):
        self.create_assemble_dialog()

    def disable_all(self):
        for child in self:
            for button in child:
                try:
                    if button.get_label() not in ['New', 'Quit']:
                        button.set_sensitive(False)
                except:
                    button.set_sensitive(False)

    def enable_all(self):
        for toolbar in self:
            for child in toolbar:
                child.set_sensitive(True)

    # New File related methods
    #
    def new_file(self, widget, file=''):
        dialog = file_dialog.FileDialog(False, self.dependency_check.HAS_RADARE, 'radare', file)
        resp = dialog.run()
        if resp == gtk.RESPONSE_DELETE_EVENT or resp == gtk.RESPONSE_REJECT:
            dialog.destroy()
        else:
            self.file = dialog.file

            self.main.load_new_file(dialog, self.file)
            dialog.destroy()

    def recent_kb(self, widget):
        """Activated when an item from the recent projects menu is clicked"""

        uri = widget.get_current_item().get_uri()
        # Strip 'file://' from the beginning of the uri
        file_to_open = uri[7:]
        self.new_file(None, file_to_open)

    # Button callback methods
    #
    def search(self, widget, icon_pos=None, event=None):
        data = self.search_entry.get_text()
        if data:
            model = self.search_combo.get_model()
            active = self.search_combo.get_active()
            option = model[active][1]
    
            results = self.uicore.search(data, self.options_dict[option])
    
            self.create_search_dialog()
            enditer = self.search_dialog.output_buffer.get_end_iter()
    
            for element in results:
                self.search_dialog.output_buffer.insert(enditer, element)

    def create_assemble_dialog(self):

        import assemble_dialog
        self.assemble_dialog = assemble_dialog.AssembleDialog(self.uicore)

        return False

    def create_search_dialog(self):

        import search_dialog
        self.search_dialog = search_dialog.SearchDialog()

        return False

    def create_cheatsheet_dialog(self, widget):

        import cheatsheet_dialog
        self.cheatsheet_dialog = cheatsheet_dialog.CheatsheetDialog()

        return False
