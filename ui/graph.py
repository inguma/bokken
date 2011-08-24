#       graph.py
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

from xdot import DotWidget

class MyDotWidget(DotWidget):
    '''Working'''

    def __init__(self, core):

        self.uicore = core
        #dotcode = self.uicore.get_callgraph()
        DotWidget.__init__(self)

    def set_dot(self, dotcode):
        self.set_dotcode(dotcode)
        self.on_zoom_fit(None)

