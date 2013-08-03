# -*- coding: utf-8 -*-
"""
Bokken Disassembler Framework
Copyright (c) 2011, 2013 David Martínez Moreno <ender@debian.org>

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

"""This library provides general functions for the GTK2 UI."""

import gtk
import os

def repaint():
    '''Easy function to clean up the event queue and force a repaint.'''

    # I've been unable to find any other way to repaint the interface. :-(
    while gtk.events_pending():
        gtk.main_iteration_do()

def set_bokken_icon(obj):
    '''Set the Bokken icon in a generic GTK object.  If the method
    set_icon_from_file() doesn't exist in the object, it will print a
    stacktrace.'''
    sep = os.sep
    obj.set_icon_from_file(os.path.dirname(__file__) + sep + '..' + sep + 'data'
        + sep + 'bokken.svg')
