# -*- coding: utf-8 -*-
"""
Bokken Disassembler Framework
Copyright (c) 2015 David Martínez Moreno <ender@debian.org>

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

""" This library provides a generic Backend instance. """

class BasicBackend():
    '''Blank instance of a disassembly engine.'''
    def __init__():
        pass

    def analyze_entropy(self):
        if not self.filename:
            return False
        # TODO: We don't know what to do in case of a URL!
        if self.fileinfo == 'URL':
            return False
