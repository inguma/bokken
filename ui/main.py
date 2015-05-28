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

import os, sys
import platform
import lib.bokken_globals as glob
import lib.common as common

# Perform the GTK UI dependency check here
import ui.dependency_check as dependency_check
dependency_check.check_all()

# Now that I know that I have them, import them!
import gtk
import gobject

# This is just general info, to help people knowing their system
print("Starting bokken {}, running on:".format(glob.version))
print("  Python version:")
print("\n".join("    "+x for x in sys.version.split("\n")))
print("  GTK version: {}".format(".".join(str(x) for x in gtk.gtk_version)))
print("  PyGTK version: {}\n".format(".".join(str(x) for x in gtk.pygtk_version)))

import ui.gtk2.common
import ui.textviews as textviews
import ui.statusbar as statusbar
import ui.file_dialog as file_dialog

MAINTITLE = "Bokken "

class BokkenGTKClient:
    '''Main GTK application'''

    def __init__(self, target, backend):

        import time

        # Allow only the main thread to touch the GUI (gtk) part, while letting
        # other threads do background work.
        gobject.threads_init()

        self.target = target
        self.backend = backend
        self.empty_gui = False
        # Variable to hold the Process object in case we choose to disassemble a binary.
        self.dasm_process = False

        # Check if we have, at least, one available core; otherwise exit.
        # TODO: Should be removed? now with one core and dependency_check doing the core check... 
        if not glob.has_radare:
            md = gtk.MessageDialog(None, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE, None)
            md.set_markup("<big><b>No backend engine found!</b></big>")
            md.format_secondary_markup((
                    'Install radare to run bokken:\n\n'
                    '<b>Radare:</b>\t<a href="http://radare.org/">'
                    'http://radare.org</a>'))
            md.run()
            md.destroy()
            sys.exit(1)

        # Start up the HTTP server.
        if glob.http_server:
            import lib.http as httpd
            http = httpd.BokkenHttpServer(glob.http_server_bind_address,
                   glob.http_server_port)
            print("\nBringing up HTTP server on %s:%d." %
                   (glob.http_server_bind_address, glob.http_server_port))
            # We start the thread.
            http.start()
            time.sleep(0.2)
            if not http.is_alive():
                print('Unable to bind to %s:%d.' %
                        (glob.http_server_bind_address, glob.http_server_port))
                return None
            # We put the http structure in glob to have it accessible in the
            # global __main__ handler.
            glob.http = http

        # Launch file selection dialog
        dialog = file_dialog.FileDialog(self.target, True)
        resp = dialog.run()
        if resp == gtk.RESPONSE_DELETE_EVENT or resp == gtk.RESPONSE_REJECT:
            return None
        # Get dialog selected file, backend and options
        self.target = dialog.file
        self.backend = 'radare'      # I'm leaving that as may be needed in the future

        # Load core
        import ui.radare_core as core
        self.uicore = core.Core(dialog)

        # Create a global object under glob.
        glob.core = self.uicore

        if self.target:
            # Just open the target if path is correct or an url
            if not os.path.isfile(self.target):
                print(common.console_color('Incorrect file argument: %s' %
                        self.target, 'red'))
                sys.exit(1)

            self.load_file(self.target)
            if not self.uicore.file_loaded:
                error_msg = "Error opening file " + self.target
                md = gtk.MessageDialog(None, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE, None)
                md.set_markup("<big><b>File open error!</b></big>")
                md.format_secondary_markup(error_msg)
                md.run()
                md.destroy()
                print error_msg
                sys.exit(1)

            ui.gtk2.common.repaint()

        else:
            self.empty_gui = True

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_focus = True
        self.window.connect("delete_event", self.quit)
        ui.gtk2.common.set_bokken_icon(self.window)
        gtk.settings_get_default().set_long_property("gtk-button-images", True, "main")

        # Title
        self.window.set_title(MAINTITLE + glob.version + " - " + self.target)

        # Positions
        #self.window.resize(1000, 700)
        #self.window.move(25, 25)
        self.window.set_position(gtk.WIN_POS_CENTER)
        # Maximize window
        #self.window.maximize()

        # Create VBox to contain top buttons and other VBox
        self.supervb = gtk.VBox(False, 1)

        # Create top buttons and add to VBox
        import ui.radare_toolbar as toolbar
        self.topbuttons = toolbar.TopButtons(self.uicore, self)
        self.supervb.pack_start(self.topbuttons, False, True, 1)

        # Create VBox to contain textviews and statusbar
        self.mainvb = gtk.VBox(False, 1)
        self.supervb.pack_start(self.mainvb, True, True, 1)

        # Initialize and add TextViews
        self.tviews = textviews.TextViews(self.uicore, self)
        # Create toolbar show/hide tabs menu
        self.topbuttons.menu.create_view_menu()

        # Initialize and add Statusbar
        self.sbar = statusbar.Statusbar(self.uicore, self.tviews)
        self.sbar.create_statusbar()

        # Add textviews and statusbar to the VBox
        self.mainvb.pack_start(self.tviews, True, True, 1)
        self.mainvb.pack_start(self.sbar, False, True, 1)

        self.window.add(self.supervb)

        # Disable all until file loads
        self.disable_all()

        if self.empty_gui:
            self.show_empty_gui()

        self.show_file_data()
        self.tviews.console.add_message('Bokken ' + glob.version + ' ready')
        self.tviews.console.add_message('Starting background analysis')
        self.window.show_all()

        # Hide left tree for plain or unsupported formats
        if self.uicore.core.format == 'Hexdump':
            self.tviews.left_scrolled_window.hide()
        if not self.uicore.do_anal:
            self.topbuttons.diff_tb.set_sensitive(False)
            self.topbuttons.sections_tb.set_sensitive(False)

        dialog.destroy()
        # We make sure that we remove the reference to the scrollbar to avoid errors.
        self.uicore.core.progress_bar = None
        gtk.main()

    # Do all the core stuff of parsing file
    def load_file(self, target):

        #print "Loading file: %s..." % (target)
        self.uicore.load_file(target)
        if not self.uicore.file_loaded:
            return
        if self.uicore.core.format == 'Program' and self.uicore.do_anal:
            self.uicore.get_sections()
            self.uicore.get_relocs()

    def show_empty_gui(self):
        self.topbuttons.throbber.running('start')

    # Once we have the file info, let's create the GUI
    def show_file_data(self):

        #print "File format detected: %s" % (self.uicore.core.format)
        # Create left buttons depending on file format
        self.tviews.update_left_buttons()

        # Add data to RIGHT TextView
        if self.uicore.core.format == "Program":
            self.tviews.update_righttext('Disassembly')
        else:
            self.tviews.update_righttext('Hexdump')

        if platform.system() != 'Windows':
            gobject.timeout_add(250, self.merge_dasm_rightextview)
        else:
            if self.uicore.text_dasm:
                self.tviews.update_dasm(self.uicore.text_dasm)
            elif self.uicore.fulldasm:
                self.tviews.update_dasm(self.uicore.fulldasm)
            self.uicore.restore_va()
            if self.uicore.core.format == 'Program':
                link_name = "0x%08x" % self.uicore.core.num.get('entry0')
                if not link_name:
                    link_name = "0x%08x" % self.uicore.core.num.get('section..text')
                if not link_name:
                    link_name = "0x%08x" % self.uicore.core.num.get('section.' + self.uicore.execsections[0][0])
                self.tviews.update_graph(self, link_name)
                self.tviews.search(self, link_name)
                self.tviews.right_notebook.finish_dasm()

            self.topbuttons.throbber.running('')

        # Load data to LEFT Tree
        if self.uicore.core.format == "Program":
            self.tviews.create_model('Functions')

        # Update statusbar with file info
        info = self.uicore.get_file_info()
        self.sbar.add_text(info, glob.version)
        self.sbar.hide_all()
        self.sbar._statusbar.show_all()

        # Create seek entry autocompletion of function names...
        self.tviews.create_completion()

        # Enable GUI
        self.enable_all()
        if  platform.system() != 'Windows':
            if self.uicore.core.format != "Program":
                self.topbuttons.throbber.running('')
            else:
                self.tviews.right_textview.right_scrolled_window.set_sensitive(False)
                self.topbuttons.throbber.running('start')

    def merge_dasm_rightextview(self):
        """ Timeout to make sure we join the spawned process for disassembling a binary. """
        if not self.dasm_process:
            # We don't need a process for this file.
            return False
        if not self.dasm_event.is_set():
            # Keep retrying.
            return True

        # Once finished the load, let's fill the UI
        #print "DEBUG: DASM finished, reading from queue!"
        #print "Process state", self.dasm_process.is_alive()
        # We read from the queue the disassembly.
        if self.uicore.do_anal:
            self.uicore.text_dasm, self.uicore.sections_lines = self.dasm_queue.get()
        #print "DEBUG: Got a disassembly of", len(self.uicore.text_dasm), "bytes."
        #print "DEBUG: Section lines created", self.uicore.sections_lines

        if self.uicore.text_dasm:
            self.tviews.update_dasm(self.uicore.text_dasm)
        else:
            self.tviews.update_dasm(self.uicore.fulldasm)

        self.uicore.restore_va()
        link_name = "0x%08x" % self.uicore.core.num.get('entry0')
        if not link_name:
            link_name = "0x%08x" % self.uicore.core.num.get('section..text')
        if not link_name:
            link_name = "0x%08x" % self.uicore.core.num.get('section.' + self.uicore.execsections[0][0])
        self.tviews.update_graph(self, link_name)
        self.tviews.search(self, link_name)
        self.tviews.right_notebook.finish_dasm()
        self.topbuttons.menu._finish_dasm()

        self.tviews.right_textview.right_scrolled_window.set_sensitive(True)
        self.topbuttons.throbber.running('')
        self.tviews.console.add_message('Background analysis finished')
        self.tviews.console.add_message('Happy reversing!')
        # Insert random r2 quote
        self.tviews.console.add_message(self.uicore.execute_command('fo'))
        return False

    def disable_all(self):
        self.topbuttons.disable_all()
        self.tviews.set_sensitive(False)

    def enable_all(self):
        self.topbuttons.set_sensitive(True)
        self.topbuttons.enable_all()
        self.tviews.set_sensitive(True)

    def load_new_file(self, dialog, target):

        self.window.hide()
        self.disable_all()
        self.target = target

        if self.target:
            # Just open the target if path is correct or an url
            if not os.path.isfile(self.target):
                print(common.console_color('Incorrect file argument: ' %
                        self.target, 'red'))
                #sys.exit(1)

            # Get dialog selected file, backend and options
            self.backend = 'radare'

            # Set user selected options
            self.uicore.set_options(dialog)

            self.uicore.backend = self.backend

            self.uicore.clean_fullvars()

            self.load_file(self.target)

            ui.gtk2.common.repaint()

        # Clean UI
        self.topbuttons.menu.delete_view_menu()
        self.tviews.left_buttons.remove_all()
        self.tviews.right_notebook.remove_tabs()
        self.tviews.left_treeview.remove_columns()
        self.sbar.remove_all()

        # Add new content
        self.tviews.right_notebook.create_tabs()
        self.topbuttons.menu.create_view_menu()
        self.show_file_data()

        self.uicore.core.progress_bar = None

        # Hide left tree for plain or unsupported formats
        if self.uicore.core.format == 'Hexdump':
            self.tviews.left_scrolled_window.hide()

        # Show UI
        self.enable_all()
        self.sbar.show_all()
        self.tviews.right_notebook.show_all()

        self.window.show()
        dialog.destroy()

    def quit(self, widget, event=None, data=None):
        '''Main quit.

        @param widget: who sent the signal.
        @param event: the event that happened
        @param data: optional data to receive.
        '''
        msg = ("Do you really want to quit?")
        dlg = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL, gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO, msg)
        dlg.set_default_response(gtk.RESPONSE_YES)
        opt = dlg.run()
        dlg.destroy()

        if opt != gtk.RESPONSE_YES:
            return True

        gtk.main_quit()
        if self.dasm_process:
            self.dasm_process.terminate()
        return True

def main(target, backend):
    BokkenGTKClient(target, backend)
    if glob.http:
        glob.http.terminate()
