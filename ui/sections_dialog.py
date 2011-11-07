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

import os
import gtk

class SectionsDialog(gtk.Dialog):
    '''Window to popup sections info'''

    def __init__(self, core):
        super(SectionsDialog,self).__init__('Extended sections information', None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, (gtk.STOCK_OK,gtk.RESPONSE_ACCEPT))

        self.uicore = core
        self.sec_bars = ''

        #self.vbox = gtk.VBox(False, 0)

        # the cancel button
        self.butt_cancel = self.action_area.get_children()[0]
        self.butt_cancel.connect("clicked", lambda x: self.destroy())

        # Positions
        self.resize(700, 400)
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_icon_from_file(os.path.dirname(__file__)+os.sep+'data'+os.sep+'bokken.svg')

        # Label...
        self.hbox = gtk.HBox(False, 1)
        self.label = gtk.Label('')
        self.label.set_markup('<big>List of binary sections with their data and size</big>')
        self.label.set_alignment(0.02, 0.5)
        self.icon = gtk.Image()
        self.icon.set_from_stock(gtk.STOCK_INFO, gtk.ICON_SIZE_MENU)
        self.hbox.pack_start(self.icon, False, False, 2)
        self.hbox.pack_start(self.label, True, True, 0)

        # ScrolledWindow
        self.scrolled_window = gtk.ScrolledWindow()
        self.scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.scrolled_window.is_visible = True

        # List view
        self.store = gtk.ListStore(str, str, str, str, str, int)
        self.tv = gtk.TreeView(self.store)
        self.tv.set_rules_hint(True)

        # Columns
        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Start offset", rendererText, text=0)
        self.store.set_sort_column_id(0, gtk.SORT_ASCENDING)
        column.set_sort_column_id(0)
        self.tv.append_column(column)
    
        # Color Bar
        rendererBar = ColoredBarRenderer()
        column = gtk.TreeViewColumn("Section size", rendererBar, text=1, start=0, end=2, size=5)
        column.set_min_width(300)
        column.set_sort_column_id(1)
        self.tv.append_column(column)

        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("End offset", rendererText, text=2)
        column.set_sort_column_id(2)
        self.tv.append_column(column)

        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Flags", rendererText, text=3)
        column.set_sort_column_id(3)
        self.tv.append_column(column)
        self.tv.set_model(self.store)

        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Name", rendererText, text=4)
        column.set_sort_column_id(4)
        self.tv.append_column(column)
        self.tv.set_model(self.store)

        self.vbox.set_spacing(3)
        self.set_border_width(3)

        # Packing
        self.scrolled_window.add(self.tv)
        self.vbox.pack_start(self.hbox, False, False)
        self.vbox.pack_start(self.scrolled_window, True, True)

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
            if len(line) == 3:
                line.append('')
            sections_info.append(line)

        min_address = min([int(x[0], 16) for x in sections_info])
        max_address = max([int(x[2], 16) for x in sections_info])
        size = max_address - min_address
        for line in sections_info:
            line.append(size)
            self.store.append(line)

class ColoredBarRenderer(gtk.GenericCellRenderer):
    import gobject

    __gproperties__ = {
                    'text': (gobject.TYPE_STRING,
                            'Text to be displayed',
                            'Text to be displayed',
                            '',
                            gobject.PARAM_READWRITE
                            ),
                    'start': (gobject.TYPE_STRING,
                            'Starting value',
                            'Starting value',
                            '',
                            gobject.PARAM_READWRITE
                            ),
                    'end': (gobject.TYPE_STRING,
                            'End value',
                            'End value',
                            '',
                            gobject.PARAM_READWRITE
                            ),
                    'size': (gobject.TYPE_INT,       # type
                            'Total size',            # nick name
                            'Total size',            # description
                            0,                       # minimum value
                            100000000,               # maximum value
                            0,                       # default value
                            gobject.PARAM_READWRITE  # flags
                            ),
                    }

    def __init__(self):
        gtk.GenericCellRenderer.__init__(self)

    def on_get_size(self, widget, cell_area):
        return (0, 0, 0, 0) # x,y,w,h

    def on_render(self, window, widget, background_area, cell_area, expose_area, flags):
        context = window.cairo_create()
        (x, y, w, h) = (cell_area.x, cell_area.y, cell_area.width, cell_area.height)

        darken = lambda color: [x * 0.8 for x in color]

        # http://colorschemedesigner.com/#2N42mhWs0g0g0
        context.set_line_width(0.5)
        context.save()

        context.set_source_rgb(*split_color(0xe7c583))
        context.rectangle(x+1, y+1 , w-2, h-2)
        context.fill_preserve()
        context.set_source_rgb(*darken(split_color(0xe7c583)))
        context.stroke_preserve()
        context.clip()
        context.restore()

        begin = int(self.get_property('start'), 16) * (w-2) / self.get_property('size')
        finish = int(self.get_property('end'), 16) * (w-2) / self.get_property('size')

        context.save()
        context.set_source_rgb(*split_color(0x6b82af))
        context.rectangle(x+begin+1, y+1, finish - begin, h-2)
        context.fill_preserve()
        context.set_source_rgb(*darken(split_color(0x6b82af)))
        context.stroke_preserve()
        context.clip()
        context.restore()

    def on_activate(self, event, widget, path, background_area, cell_area, flags):
        pass

    def on_start_editing(self, event, widget, path, background_area, cell_area, flags):
        pass

    def do_set_property(self, key, value):
        setattr(self, key.name , value)

    def do_get_property(self, key):
        return getattr(self, key.name)

def split_color(html_hex):
    """ split_color(html_hex=24 bit color value) return tuple of three colour values being 0-1.
        Assume 0xFFFFFF=White=(1,1,1) 0x000000=Black=(0,0,0) """
    return ((html_hex >> 16)/255.0,(255 & (html_hex >> 8))/255.0,(255 & html_hex)/255.0)
