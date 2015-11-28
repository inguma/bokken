##      comments_dialog.py
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

class CommentsDialog(Gtk.Dialog):
    '''Window to popup search input'''

    def __init__(self, title='Add comment'):
        super(CommentsDialog,self).__init__(title, None, Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT, (Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT, Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT))

        # the cancel button
        self.butt_cancel = self.action_area.get_children()[1]
        self.butt_cancel.connect("clicked", lambda x: self.destroy())

        # Positions
        self.resize(400, 200)
        self.set_position(Gtk.WindowPosition.CENTER)
        ui.gtk2.common.set_bokken_icon(self)

        # Log TextView
        #################################################################
        self.input_text = Gtk.TextView(buffer=None)
        self.input_text.set_wrap_mode(Gtk.WrapMode.NONE)
        self.input_text.set_left_margin(10)
        self.input_buffer = self.input_text.get_buffer()

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.scrolled_window.is_visible = True

        # Add Textview to Scrolled Window
        self.scrolled_window.add_with_viewport(self.input_text)

        #self.vbox.pack_start(self.input_text, True, True, 0)
        self.vbox.pack_start(self.scrolled_window, True, True, 0)
        self.show_all()
