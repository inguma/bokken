# -*- coding: utf-8 -*-
#       core_functions.py
#
#       Copyright (C) 2011 David Martínez Moreno <ender@debian.org>
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

import gtk

def repaint():
    """ Easy function to clean up the event queue and force a repaint. """

    # I've been unable to find any other way to repaint the interface. :-(
    while gtk.events_pending():
        gtk.main_iteration_do()
