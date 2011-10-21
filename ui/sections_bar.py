#       sections_bar.py
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

import gtk
import gobject

class SectionsBar(gtk.DrawingArea):

    __gsignals__ = {
        'expose-event': 'override',
        'button-press-event': 'override',
        'size-request': 'override',
    }

    def __init__(self, core):
        gtk.DrawingArea.__init__(self)
        self.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        self._scrolladj = None
        self._y_offset = 0
        self._h_offset = 0
        self.uicore = core

    def setup(self, scrollbar):
        self.scrollbar = scrollbar
        self._scrolladj = scrollbar.get_adjustment()
        self.on_scrollbar_size_allocate(scrollbar, scrollbar.allocation)
        self.queue_draw()

    def on_scrollbar_size_allocate(self, scrollbar, allocation):
        self._scroll_y = allocation.y
        self._scroll_height = allocation.height
        self.queue_draw()

    def do_expose_event(self, event):
        self._scroll_height = self.scrollbar.allocation.height
        stepper_size = self.scrollbar.style_get_property("stepper-size")
        height = self._scroll_height - (2 * stepper_size)

        context = self.window.cairo_create()
        #context.translate(0, y_start)
        context.translate(0, 0)
        context.set_line_width(1)
        context.rectangle(0, stepper_size, 15, height)
        context.clip()

        darken = lambda color: [x * 0.8 for x in color]

        colors = [ (0.7568627450980392, 1.0, 0.7568627450980392),
                  (0.7568627450980392, 0.7568627450980392, 2.0) ]

        if height == 0:
            return

        sections_size = self.uicore.sections_lines
        if len(sections_size) < 2:
            sections_size = [height, height]
        # Get sections sizes
        total_size = sections_size[-1]
        prev_height = 0
        counter = 0
        # Iterate sections
        for size in sections_size[:-1]:
            # Calculate percentage
            perc_size = (float(size)*100)/float(total_size)
            #print "%d is the %d percentage of %d" % (size, perc_size, total_size)
            # Get height
            tmp_height = height * perc_size / 100
            y1 = tmp_height
    
            # Draw
            color = colors[counter & 1]
            context.set_source_rgb(*color)
            context.set_line_width(1)
            context.rectangle(0, stepper_size + prev_height, 15, y1 + prev_height)
            context.fill_preserve()
            context.set_source_rgb(*darken(color))
            context.stroke()
            prev_height += tmp_height
            counter += 1

    def do_size_request(self, request):
        request.width = self.style_get_property('width')

gtk.widget_class_install_style_property(SectionsBar,
                                        ('width', float,
                                         'Width',
                                         'Width of the bar',
                                         0.0, gobject.G_MAXFLOAT, 20,
                                         gobject.PARAM_READABLE))
gtk.widget_class_install_style_property(SectionsBar,
                                        ('x-padding', float,
                                         'Width-wise padding',
                                         'Padding to be left between left and '
                                         'right edges and change blocks',
                                         0.0, gobject.G_MAXFLOAT, 2.5,
                                         gobject.PARAM_READABLE))
