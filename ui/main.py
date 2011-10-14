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

import os, sys, threading

# Add plugins directory to the path
BOKKEN_PATH = os.getcwd() + os.sep + 'plugins' + os.sep
sys.path.append(BOKKEN_PATH)

# Perform the GTK UI dependency check here
import ui.dependency_check as dependency_check
dependency_check.check_all()

# Now that I know that I have them, import them!
import gtk, gobject

# This is just general info, to help people knowing their system
print "Starting bokken, running on:"
print "  Python version:"
print "\n".join("    "+x for x in sys.version.split("\n"))
print "  GTK version:", ".".join(str(x) for x in gtk.gtk_version)
print "  PyGTK version:", ".".join(str(x) for x in gtk.pygtk_version)
print

import ui.menu_bar as menu_bar
import ui.textviews as textviews
import ui.statusbar as statusbar
import ui.file_dialog as file_dialog

# Threading initializer
if sys.platform == "win32":
    gobject.threads_init()
else:
    gtk.gdk.threads_init()

MAINTITLE = "Bokken, a GUI for pyew and radare2!"
VERSION = "1.5-dev"

FAIL = '\033[91m'
OKGREEN = '\033[92m'
ENDC = '\033[0m'

class MainApp:
    '''Main GTK application'''

    def __init__(self, target, backend):

        self.dependency_check = dependency_check

        self.target = target
        self.backend = backend
        self.empty_gui = False

        # Check if we have, at least, one core; else: exit
        if not dependency_check.HAS_PYEW and not dependency_check.HAS_RADARE:
            md = gtk.MessageDialog(None, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE, None)
            md.set_markup("<big><b>No backend engines found!</b></big>")
            md.format_secondary_markup("Install either pyew or radare to run bokken:\n\n<b>Pyew:</b>\t\t<a href=\"http://code.google.com/p/pyew/\">http://code.google.com/p/pyew/</a>\n<b>Radare:</b>\t<a href=\"http://radare.org/\">http://radare.org</a>")
            md.run()
            md.destroy()
            sys.exit(1)

        # Launch file selection dialog
        dialog = file_dialog.FileDialog(dependency_check.HAS_PYEW, dependency_check.HAS_RADARE, self.backend, self.target)
        resp = dialog.run()
        if resp == gtk.RESPONSE_DELETE_EVENT:
            sys.exit(1)
        # Get dialog selected file, backend and options
        self.target = dialog.file
        self.backend = dialog.backend

        # Load selected core
        if self.backend == 'pyew':
            import ui.core as core
            self.uicore = core.Core(dialog.case, dialog.deep)
        elif self.backend == 'radare':
            import ui.r2_core as r2_core
            self.uicore = r2_core.Core(dialog.radare_lower, dialog.analyze_bin, dialog.asm_syn ,dialog.use_va, dialog.asm_byt)
        self.uicore.backend = self.backend

        # Check if target name is an URL, pyew stores it as 'raw'
        self.uicore.is_url(self.target)

        if self.target:
            # Just open the target if path is correct or an url
            if self.uicore.core.format != 'URL' and not os.path.isfile(self.target):
                print "Incorrect file argument:", FAIL, self.target, ENDC
                sys.exit(1)
    
            # Use threads to avoid freezing the GUI load
            thread = threading.Thread(target=self.load_file, args=(self.target,))
            thread.start()
            # This call must not depend on load_file data
            gobject.timeout_add(500, self.show_file_data, thread)
        else:
            self.empty_gui = True

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_focus = True
        self.window.connect("delete_event", self.quit)
        self.window.set_icon_from_file('ui' + os.sep + 'data' + os.sep + 'icon.png')
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

        # Menu bar
        self.mbar = menu_bar.MenuBar(self)

        self.supervb.pack_start(self.mbar, False, False, 1)

        # Create top buttons and add to VBox
        if self.backend == 'pyew':
            import ui.pyew_toolbar as toolbar
            self.topbuttons = toolbar.TopButtons(self.uicore, self)
        elif self.backend == 'radare':
            import ui.radare_toolbar as toolbar
            self.topbuttons = toolbar.TopButtons(self.uicore, self)
        self.supervb.pack_start(self.topbuttons, False, True, 1)

        # Create VBox to contain textviews and statusbar
        self.mainvb = gtk.VBox(False, 1)
        self.supervb.pack_start(self.mainvb, True, True, 1)

        # Initialize and add TextViews
        self.tviews = textviews.TextViews(self.uicore, self)
        # Create toolbar show/hide tabs menu
        self.mbar.create_view_menu()

        # Initialize and add Statusbar
        self.sbar = statusbar.Statusbar(self.uicore, self.tviews)

        # Add textviews and statusbar to the VBox
        self.mainvb.pack_start(self.tviews, True, True, 1)
        self.mainvb.pack_start(self.sbar, False, True, 1)

        self.window.add(self.supervb)

        # Start the throbber while the thread is running...
        self.topbuttons.throbber.running(True)

        # Disable all until file loads
        self.disable_all()

        if self.empty_gui:
            self.show_empty_gui()

        self.window.show_all()

        gtk.main()

    # Do all the core stuff of parsing file
    def load_file(self, target):

        print "Loading file: %s..." % (target)
        self.uicore.load_file(target)
        if self.uicore.core.format in ['PE', 'Elf', 'ELF', 'Program']:
            self.uicore.get_sections()
        print 'File successfully loaded' + OKGREEN + "\tOK" + ENDC

    def show_empty_gui(self):
        self.topbuttons.throbber.running('')

    # Once we have the file info, let's create the GUI
    def show_file_data(self, thread):
        if thread.isAlive() == True:
            return True
        else:
            #print "File format detected: %s" % (self.uicore.core.format)
            # Create left combo depending on file format
            #self.tviews.update_left_combo()
            self.tviews.update_left_buttons()

            # Add data to RIGHT TextView
            if self.uicore.core.format in ["PE", "ELF", "Program"]:
                self.tviews.update_righttext('Disassembly')
            elif self.uicore.core.format in ["PYC"]:
                self.tviews.update_righttext('Python')
            elif self.uicore.core.format in ['URL']:
                self.tviews.update_righttext('URL')
            elif self.uicore.core.format in ['Plain Text']:
                self.tviews.update_righttext('Plain Text')
            else:
                self.tviews.update_righttext('Hexdump')

            # Add data to INTERACTIVE TextView
            self.tviews.update_interactive()

            # Load data to LEFT Tree
            if self.uicore.core.format in ["PE", "ELF", "Program"]:
                self.tviews.create_model('Functions')
                self.tviews.left_combo.set_active(0)
        
            elif self.uicore.core.format in ["PDF"]:
                # Why?! Oh why in the name of God....!!
                self.tviews.create_model('PDF')
        
            elif self.uicore.core.format in ["URL"]:
                self.tviews.create_model('URL')

            # Update statusbar with file info
            info = self.uicore.get_file_info()
            self.sbar.add_text(info, '')

            # Create seek entry autocompletion of function names...
            self.tviews.create_completion()

            # Enable GUI
            self.enable_all()
            self.topbuttons.throbber.running('')

            if 'radare' in self.uicore.backend:
                if self.uicore.core.format == 'Program':
                    self.tviews.update_graph(self, 'entry0')
                    link_name = "0x%08x" % self.uicore.core.num.get('entry0')
                    if link_name:
                        self.tviews.search(self, link_name)
            elif 'pyew' in self.uicore.backend:
                if self.uicore.core.format in ['PE', 'ELF']:
                    if self.uicore.core.ep:
                        link_name = "0x%08x" % self.uicore.core.ep
                        if link_name:
                            if not self.tviews.search(self, link_name):
                                link_name = "0x%08x" % self.uicore.text_address
                                self.tviews.search(self, link_name)

    def disable_all(self):
        if self.target:
            self.sbar.add_text({'Please wait while loading file':self.target}, VERSION)
        else:
            self.sbar.add_text({'Open a new file to start':''}, VERSION)
        self.topbuttons.disable_all()
        self.tviews.set_sensitive(False)

    def enable_all(self):
        self.topbuttons.set_sensitive(True)
        self.topbuttons.enable_all()
        self.tviews.set_sensitive(True)

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
        return True

def main(target, backend):
    MainApp(target, backend)
