#!/usr/bin/python

#       main.py
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

import sys, threading

# Perform the GTK UI dependency check here
import ui.dependencyCheck as dependencyCheck
dependencyCheck.check_all()

# Now that I know that I have them, import them!
import gtk, gobject

# This is just general info, to help people knowing their system
print "Starting gyew, running on:"
print "  Python version:"
print "\n".join("    "+x for x in sys.version.split("\n"))
print "  GTK version:", ".".join(str(x) for x in gtk.gtk_version)
print "  PyGTK version:", ".".join(str(x) for x in gtk.pygtk_version)
print

import ui.core as core
import ui.textviews as textviews
import ui.statusbar as statusbar
import ui.buttons as buttons
import ui.file_dialog as file_dialog

# Threading initializer
if sys.platform == "win32":
    gobject.threads_init()
else:
    gtk.gdk.threads_init()

MAINTITLE = "Bokken, a GUI for pyew and (soon) radare2!"
# FIXME Add to a Status Bar
VERSION="1.0-dev"

class MainApp:
    '''Main GTK application'''

    def __init__(self, file):

        self.file = file

        if not self.file:
            dialog = file_dialog.FileDialog()
            dialog.run()
            self.file = dialog.file

        self.uicore = core.Core()

        # Use threads not to freeze GUI load
        t = threading.Thread(target=self.load_file, args=(self.file,))
        t.start()
        gobject.timeout_add(500, self.show_file_data, t)

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_focus = True
        self.window.connect("delete_event", self.quit)
        gtk.settings_get_default().set_long_property("gtk-button-images", True, "main") 

        # Title
        self.window.set_title(MAINTITLE)

        # Positions
        self.window.resize(800, 600)
        self.window.move(25, 25)
        # Maximize window
        self.window.maximize()

        # Create VBox to contain top buttons and other VBox
        self.supervb = gtk.VBox(False, 1)

        # Create top buttons and add to VBox
        self.topbuttons = buttons.TopButtons(self.uicore, self)
        self.supervb.pack_start(self.topbuttons, False, True, 1)

        # Create VBox to contain textviews and statusbar
        self.mainvb = gtk.VBox(False, 1)
        self.supervb.pack_start(self.mainvb, True, True, 1)

        # Initialize and add TextViews
        self.tviews = textviews.TextViews(self.uicore)

        # Initialize and add Statusbar
        self.sbar = statusbar.Statusbar(self.uicore)

        # Add textviews and statusbar to the VBox
        self.mainvb.pack_start(self.tviews, True, True, 1)
        self.mainvb.pack_start(self.sbar, False, True, 1)

        self.window.add(self.supervb)

        # Start the throbber while the thread is running...
        self.topbuttons.throbber.running(True)

        self.window.show_all()

        gtk.main()

    def load_file(self, file):

        OKGREEN = '\033[92m'
        ENDC = '\033[0m'

        print "Loading file: %s..." % (file)
        self.uicore.load_file(file)
        try:
            self.uicore.get_sections()
        except:
            pass
        print 'File successfully loaded' + OKGREEN + "\tOK" + ENDC

    def show_file_data(self, thread):
        if thread.isAlive() == True:
            return True
        else:
            # Left combo content
            self.tviews.update_combo_content()
            # Right combo content
            self.tviews.update_right_combo()

            # Add data to RIGHT TextView
            if self.uicore.pyew.format in ["PE", "ELF"]:
                # Add default startup content
                self.tviews.update_righttext('Disassembly')
            elif self.uicore.pyew.format in ["PYC"]:
                self.tviews.update_righttext('Python')
            elif self.uicore.pyew.format in ['URL']:
                self.tviews.update_righttext('URL')
            elif self.uicore.pyew.format in ['Plain Text']:
                self.tviews.update_righttext('Plain Text')
            else:
                self.tviews.update_righttext('Hexdump')

            # Load data to LEFT Tree
            if self.uicore.pyew.format in ["PE", "ELF"]:
                self.tviews.create_model('Functions')
                self.tviews.left_combo.set_active(0)
        
                # Add file information to the StatusBar
                info = self.uicore.get_file_info()
                self.sbar.add_text(info, VERSION)
            elif self.uicore.pyew.format in ["PDF"]:
                # Why?! Oh why in the name of God....!!
                self.tviews.create_model('PDF')
                #self.tviews.left_combo.set_active(0)
        
                # Add file information to the StatusBar
                info = self.uicore.get_file_info()
                self.sbar.add_text(info, VERSION)
            elif self.uicore.pyew.format in ["URL"]:
                self.tviews.create_model('URL')
            self.topbuttons.throbber.running('')

    def quit(self, widget, event, data=None):
        '''Main quit.

        @param widget: who sent the signal.
        @param event: the event that happened
        @param data: optional data to receive.
        '''
        msg = ("Do you really want to quit?")
        dlg = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL, gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO, msg)
        opt = dlg.run()
        dlg.destroy()

        if opt != gtk.RESPONSE_YES:
            return True

        gtk.main_quit()
        return False

def main(file):
    MainApp(file)
