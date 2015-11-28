#       sections_dialog.py
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

from gi.repository import Gtk
import ui.gtk2.common

class SectionsDialog(Gtk.Dialog):
    '''Window to popup sections info'''

    def __init__(self, core, parent_window):
        super(SectionsDialog,self).__init__('Extended sections information', parent_window, Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT, (Gtk.STOCK_OK,Gtk.ResponseType.ACCEPT))

        self.uicore = core
        self.sec_bars = ''

        #self.vbox = Gtk.VBox(False, 0)

        # the cancel button
        self.butt_cancel = self.action_area.get_children()[0]
        self.butt_cancel.connect("clicked", lambda x: self.destroy())

        # Positions
        self.resize(700, 400)
        self.set_position(Gtk.WindowPosition.CENTER)
        ui.gtk2.common.set_bokken_icon(self)

        # Label...
        self.hbox = Gtk.HBox(False, 1)
        self.label = Gtk.Label(label='')
        self.label.set_markup('<big>List of binary sections with their data and size</big>')
        self.label.set_alignment(0.02, 0.5)
        self.icon = Gtk.Image()
        self.icon.set_from_stock(Gtk.STOCK_INFO, Gtk.IconSize.MENU)
        self.hbox.pack_start(self.icon, False, False, 2)
        self.hbox.pack_start(self.label, True, True, 0)

        # ScrolledWindow
        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.scrolled_window.is_visible = True

        # List view
        self.store = Gtk.ListStore(
                # For each section in the binary:
                str, # Start address in hex.
                str, # r2's ASCII representation of the section.
                str, # Final address in hex.
                str, # Section flags.
                str, # Section name.
                int, # Total section size in bytes.
                str, # Initial binary address in hex.
        )
        self.tv = Gtk.TreeView(self.store)
        self.tv.set_rules_hint(True)

        # Columns
        rendererText = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Start offset", rendererText, text=0)
        self.store.set_sort_column_id(0, Gtk.SortType.ASCENDING)
        column.set_sort_column_id(0)
        self.tv.append_column(column)

        # Color Bar
        rendererBar = ColoredBarRenderer()
        # The way this constructor works is:
        # __init__(title, renderer, property_X_in_renderer=column_Y_from_liststore, ...)
        # This means that we are passing column 1 from liststore as 'text', column 0 as 'start'...
        column = Gtk.TreeViewColumn("Section size", rendererBar,
                text=1, start=0, end=2, total_size=5, begin=6)
        column.set_min_width(300)
        column.set_sort_column_id(1)
        self.tv.append_column(column)

        rendererText = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("End offset", rendererText, text=2)
        column.set_sort_column_id(2)
        self.tv.append_column(column)

        rendererText = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Flags", rendererText, text=3)
        column.set_sort_column_id(3)
        self.tv.append_column(column)
        self.tv.set_model(self.store)

        rendererText = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Name", rendererText, text=4)
        column.set_sort_column_id(4)
        self.tv.append_column(column)
        self.tv.set_model(self.store)

        self.vbox.set_spacing(3)
        self.set_border_width(3)

        # Packing
        self.scrolled_window.add(self.tv)
        self.vbox.pack_start(self.hbox, False, False, 0)
        self.vbox.pack_start(self.scrolled_window, True, True, 0)

        self._get_section_bars()
        self.show_all()

    #
    # Methods

    def _get_section_bars(self):
        self.sec_bars = self.uicore.core.cmd_str('S=')
        if self.sec_bars:
            self._parse_ascii_bars()

    def _parse_ascii_bars(self):
        import re

        self.bar_lines = self.sec_bars.split('\n')
        sections_info = []
        for line in self.bar_lines:
            if line == '':
                continue
            if line[0:4] == '=>  ':
                continue
            line = re.split('^\d+[\* ] ', line)[-1]
            line = line.split(' ')
            # Radare sometimes decides to return 0x000000 as part of the
            # addresses and that ruins the calculations, so get rid of it
            # for now.
            if int(line[0], 16) == 0:
                continue
            if len(line) == 3:
                line.append('')
            sections_info.append(line)

        min_address = min([int(x[0], 16) for x in sections_info])
        max_address = max([int(x[2], 16) for x in sections_info])
        size = max_address - min_address

        for line in sections_info:
            # We need to supply the initial address to the renderer to
            # make proper calculations.
            line.extend((size, hex(min_address)))
            self.store.append(line)

class ColoredBarRenderer(Gtk.CellRenderer):
    from gi.repository import GObject

    __gproperties__ = {
                    'text': (GObject.TYPE_STRING,
                            'Text to be displayed',
                            'Text to be displayed',
                            '',
                            GObject.PARAM_READWRITE
                            ),
                    'start': (GObject.TYPE_STRING,
                            'Starting value',
                            'Starting value',
                            '',
                            GObject.PARAM_READWRITE
                            ),
                    'end': (GObject.TYPE_STRING,
                            'End value',
                            'End value',
                            '',
                            GObject.PARAM_READWRITE
                            ),
                    # Size of the binary calculated as max-min address.
                    'total_size': (GObject.TYPE_INT, # type
                            'Total size',            # nick name
                            'Total size',            # description
                            0,                       # minimum value
                            100000000,               # maximum value
                            0,                       # default value
                            GObject.PARAM_READWRITE  # flags
                            ),
                    # Address of the initial section.
                    'begin': (GObject.TYPE_STRING,   # type
                            'Initial binary address',# nick name
                            'Initial binary address',# description
                            '',
                            GObject.PARAM_READWRITE  # flags
                            ),
                    }

    def __init__(self):
        from gi.repository import GObject
        GObject.GObject.__init__(self)

    def do_get_size(self, widget, cell_area):
        return (0, 0, 0, 0) # x,y,w,h

    def do_render(self, context, widget, background_area, cell_area, flags):
        '''The way we will render the sections will be drawing a yellow rectangle occupying
        all the area for the column, and then a blue section on top at the proper start
        and end coordinates'''
        (x, y, w, h) = (cell_area.x, cell_area.y, cell_area.width, cell_area.height)

        darken = lambda color: [x * 0.8 for x in color]

        # http://colorschemedesigner.com/#2N42mhWs0g0g0
        __yellow__ = 0xe7c583
        __blue__ = 0x6b82af
        context.set_line_width(0.5)
        context.save()

        # Yellow rectangle.
        context.set_source_rgb(*split_color(__yellow__))
        context.rectangle(x+1, y+1 , w-2, h-2)
        context.fill_preserve()
        context.set_source_rgb(*darken(split_color(__yellow__)))
        context.stroke_preserve()
        context.clip()
        context.restore()

        # We convert the absolute offsets to differences in pixels.
        first_section_addr = int(self.get_property('begin'), 16)
        binary_size = self.get_property('total_size')
        initial_px = (int(self.get_property('start'), 16) - first_section_addr) * (w-2) / binary_size
        final_px = (int(self.get_property('end'), 16) - first_section_addr) * (w-2) / binary_size

        # Blue rectangle.
        context.save()
        context.set_source_rgb(*split_color(__blue__))
        context.rectangle(x+initial_px+1, y+1, final_px-initial_px, h-2)
        context.fill_preserve()
        context.set_source_rgb(*darken(split_color(__blue__)))
        context.stroke_preserve()
        context.clip()
        context.restore()

    def do_activate(self, event, widget, path, background_area, cell_area, flags):
        pass

    def do_start_editing(self, event, widget, path, background_area, cell_area, flags):
        pass

    def do_set_property(self, key, value):
        setattr(self, key.name , value)

    def do_get_property(self, key):
        return getattr(self, key.name)

def split_color(html_hex):
    """ split_color(html_hex=24 bit color value) return tuple of three colour values being 0-1.
        Assume 0xFFFFFF=White=(1,1,1) 0x000000=Black=(0,0,0) """
    return ((html_hex >> 16)/255.0,(255 & (html_hex >> 8))/255.0,(255 & html_hex)/255.0)
