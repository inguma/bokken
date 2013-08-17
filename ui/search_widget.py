# -*- coding: utf-8 -*-
"""
Bokken Disassembler Framework
Copyright (c) 2011 Hugo Teso <hugo.teso@gmail.com>
Copyright (c) 2013 David Martínez Moreno <ender@debian.org>

I am providing code in this repository to you under an open source license.
Because this is a personal repository, the license you receive to my code
is from me and not my employer (Facebook).

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
02110-1301, USA.
"""

'''This library provides a function to create the search widget in a toolbar.'''

import gtk
from lib.common import datafile_path

def create(toolbar):
    '''Set of instructions to create the search widget in a toolbar.'''

    # Search components
    toolbar.search_combo_tb = gtk.ToolItem()
    toolbar.search_combo_align = gtk.Alignment(yalign=0.5)
    store = gtk.ListStore(gtk.gdk.Pixbuf, str)
    toolbar.search_combo = gtk.ComboBox(store)
    rendererText = gtk.CellRendererText()
    rendererPix = gtk.CellRendererPixbuf()
    toolbar.search_combo.pack_start(rendererPix, False)
    toolbar.search_combo.pack_start(rendererText, True)
    toolbar.search_combo.add_attribute(rendererPix, 'pixbuf', 0)
    toolbar.search_combo.add_attribute(rendererText, 'text', 1)

    options = {
        'String':gtk.gdk.pixbuf_new_from_file(datafile_path('icon_string_16.png')),
        'String no case':gtk.gdk.pixbuf_new_from_file(datafile_path('icon_string_no_case_16.png')),
        'Hexadecimal':gtk.gdk.pixbuf_new_from_file(datafile_path('icon_hexadecimal_16.png')),
        'Regexp':gtk.gdk.pixbuf_new_from_file(datafile_path('icon_regexp_16.png'))
    }

    for option in options.keys():
        store.append([options[option], option])
    toolbar.search_combo.set_active(0)
    toolbar.search_combo_align.add(toolbar.search_combo)
    toolbar.search_combo_tb.add(toolbar.search_combo_align)
    toolbar.main_tb.insert(toolbar.search_combo_tb, -1)

    # Separator
    toolbar.sep = gtk.SeparatorToolItem()
    toolbar.sep.set_draw(False)
    toolbar.main_tb.insert(toolbar.sep, -1)

    toolbar.search_entry_tb = gtk.ToolItem()
    toolbar.search_entry = gtk.Entry(100)
    toolbar.search_entry.set_text('Text to search')
    toolbar.search_entry.set_icon_from_stock(1, gtk.STOCK_FIND)
    toolbar.search_entry.set_icon_tooltip_text(1, 'Search')
    toolbar.search_entry.connect("activate", toolbar.search)
    toolbar.search_entry.connect("icon-press", toolbar.search)
    toolbar.search_entry.connect('focus-in-event', toolbar._clean, 'in')
    toolbar.search_entry.connect('focus-out-event', toolbar._clean, 'out')
    toolbar.search_entry_tb.add(toolbar.search_entry)
    # We use the AccelGroup object from the main window.
    my_accel = gtk.accel_groups_from_object(toolbar.main.window)[0]
    key, mod = gtk.accelerator_parse('<Control>F')
    toolbar.search_entry.set_tooltip_text('Control-F to search')
    toolbar.search_entry.add_accelerator('grab-focus', my_accel, key, mod, gtk.ACCEL_MASK)
    toolbar.main_tb.insert(toolbar.search_entry_tb, -1)
