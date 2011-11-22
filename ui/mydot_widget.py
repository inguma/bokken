#       mydot_widgetmydot_widgetmydot_widget.py
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

import xdot
import ui.xrefs_menu as xrefs_menu

class MyDotWidget(xdot.DotWidget):
    def __init__(self, core, main):
        self.uicore = core
        self.main = main

        xdot.DotWidget.__init__(self)
        self.xmenu = xrefs_menu.XrefsMenu(self.uicore, self.main)

#
# Removed until the next release due to problems with the radare bindings
#

    def on_area_button_release(self, area, event):
        if event.button == 3:

            refs = []
            xrefs = []

            x, y = int(event.x), int(event.y)
            url = self.get_url(x, y)
            if url is not None:
                address = url.url.split('/')[0]
                addr = self.uicore.core.num.get(address)
                fcn = self.uicore.core.anal.get_fcn_at(addr)

                for ref in fcn.get_refs():
                    if not "0x%08x" % ref.addr in refs:
                        refs.append("0x%08x" % ref.addr)
                for xref in fcn.get_xrefs():
                    if not "0x%08x" % xref.addr in xrefs:
                        xrefs.append("0x%08x" % xref.addr)

                menu = self.xmenu.create_menu(address, refs, xrefs)
                menu.popup(None, None, None, 1, event.time)
                menu.show_all()

#            jump = self.get_jump(x, y)
#            if jump is not None and url is not None:
#                #Right Click on Node!!
#                # Check if it's an OSVDB node
#                if url.url.split(':')[0] == 'OSVDB':
#                    self.context.show_browser('action', url.url.split(':')[1])
#                elif 'poc_' in url.url:
#                    self.context.show_browser('action', url.url)
#                else:
#                    # If not is a target node
#                    self.context.set_data(url.url)
#                    self.context.popmenu.popup(None, None, None, 1, event.time)
        else:
            super(MyDotWidget, self).on_area_button_release(area, event)
