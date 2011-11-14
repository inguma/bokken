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

import os
import gtk

class CommentsDialog(gtk.Dialog):
    '''Window to popup search input'''

    def __init__(self, title='Add comment'):
        super(CommentsDialog,self).__init__(title, None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT, gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))

        # the cancel button
        self.butt_cancel = self.action_area.get_children()[1]
        self.butt_cancel.connect("clicked", lambda x: self.destroy())

        # Positions
        self.resize(400, 200)
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_icon_from_file(os.path.dirname(__file__)+os.sep+'data'+os.sep+'bokken.svg')

        # Log TextView
        #################################################################
        self.input_text = gtk.TextView(buffer=None)
        self.input_text.set_wrap_mode(gtk.WRAP_NONE)
        self.input_text.set_left_margin(10)
        self.input_buffer = self.input_text.get_buffer()

        self.scrolled_window = gtk.ScrolledWindow()
        self.scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.scrolled_window.is_visible = True

        # Add Textview to Scrolled Window
        self.scrolled_window.add_with_viewport(self.input_text)

        #self.vbox.pack_start(self.input_text)
        self.vbox.pack_start(self.scrolled_window)
        self.show_all()
