#       graph_bar.py
#       
#       Copyright 2009 Hugo Teso <hugo.teso@gmail.com>
#       Based on code from w3af by Andres Riancho (w3af.sourceforge.net)
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

class GraphBar(gtk.VBox):
    ''' Bar for the xdot graph widget '''
    def __init__(self, graph, mydot, core):
        gtk.VBox.__init__(self)

        self.graph = graph
        self.mydot = mydot
        self.uicore = core

        self.toolbox = self
        b = SemiStockButton("", gtk.STOCK_ZOOM_IN, 'Zoom In')
        b.connect("clicked", self._zoom, "in")
        self.toolbox.pack_start(b, False, False)
        b = SemiStockButton("", gtk.STOCK_ZOOM_OUT, 'Zoom Out')
        b.connect("clicked", self._zoom, "out")
        self.toolbox.pack_start(b, False, False)
        b = SemiStockButton("", gtk.STOCK_ZOOM_FIT, 'Zoom Fit')
        b.connect("clicked", self._zoom, "fit")
        self.toolbox.pack_start(b, False, False)
        b = SemiStockButton("", gtk.STOCK_ZOOM_100, 'Zoom 100%')
        b.connect("clicked", self._zoom, "100")
        self.toolbox.pack_start(b, False, False)
        # Separator
        self.sep = gtk.HSeparator()
        self.toolbox.pack_start(self.sep, False, False)

        # Change between Callgraph and Flowgraph
        if self.uicore.backend == 'radare':
            self.grpah_layout = gtk.ToggleToolButton(stock_id=gtk.STOCK_FULLSCREEN)
            self.grpah_layout.connect("clicked", self._change_layout)
            self.toolbox.pack_start(self.grpah_layout, False, False)

        # Grayed?
        self.toolbox.set_sensitive(True)
        self.show_all()

    def _zoom(self, widg, what):
        f = getattr(self.graph, "on_zoom_"+what)
        f(None)

    def _change_layout(self, widget):
        if widget.get_active():
            self.uicore.graph_layout = 'call'
            widget.set_stock_id(gtk.STOCK_LEAVE_FULLSCREEN)
        else:
            self.uicore.graph_layout = 'flow'
            widget.set_stock_id(gtk.STOCK_FULLSCREEN)
        self.mydot.set_dot(self.uicore.get_callgraph(self.mydot.last_fcn))

class SemiStockButton(gtk.Button):
    '''Takes the image from the stock, but the label which is passed.
    
    @param text: the text that will be used for the label
    @param image: the stock widget from where extract the image
    @param tooltip: the tooltip for the button

    @author: Facundo Batista <facundobatista =at= taniquetil.com.ar>
    '''
    def __init__(self, text, image, tooltip=None):
        super(SemiStockButton,self).__init__(stock=image)
        align = self.get_children()[0]
        box = align.get_children()[0]
        (self.image, self.label) = box.get_children()
        self.label.set_text(text)
        if tooltip is not None:
            self.set_tooltip_text(tooltip)
            
    def changeInternals(self, newtext, newimage, tooltip=None):
        '''Changes the image and label of the widget.
    
        @param newtext: the text that will be used for the label
        @param newimage: the stock widget from where extract the image
        @param tooltip: the tooltip for the button
        '''
        self.label.set_text(newtext)
        self.image.set_from_stock(newimage, gtk.ICON_SIZE_BUTTON)
        if tooltip is not None:
            self.set_tooltip_text(tooltip)
