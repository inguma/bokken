#!/usr/bin/python

#       buttons.py
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

import gtk, gobject
import threading

FAIL = '\033[91m'
OKGREEN = '\033[92m'
ENDC = '\033[0m'

# We need it for the "New" button
import ui.file_dialog as file_dialog
import ui.throbber as throbber

class TopButtons(gtk.HBox):
    '''Top Buttons'''

    def __init__(self, core, main):
        super(TopButtons,self).__init__(False, 1)

        self.main = main

        self.uicore = core
        self.toolbox = self

        self.img_path = 'ui' + os.sep + 'data' + os.sep
        self.options_dict = {'Hexadecimal':'x', 'String':'s', 'String no case':'i', 'Regexp':'r', 'Unicode':'u', 'Unicode no case':'U'}

        self.main_tb = gtk.Toolbar()
        self.main_tb.set_style(gtk.TOOLBAR_ICONS)

        # New file button
        self.new_tb = gtk.ToolButton(gtk.STOCK_NEW)
        self.new_tb.set_tooltip_text('Open new file')
        self.new_tb.connect("clicked", self.new_file)
        self.main_tb.insert(self.new_tb, 0)

        # Separator
        self.sep = gtk.SeparatorToolItem()
        self.main_tb.insert(self.sep, 1)

        # PDF Streams search
        self.streams_tb = gtk.ToolButton(gtk.STOCK_INDEX)
        self.streams_tb.set_tooltip_text('Find PDF streams')
        self.streams_tb.connect("clicked", self.search_pdfstreams)
        self.streams_tb.set_sensitive(False)
        self.main_tb.insert(self.streams_tb, 2)
        # Separator
        self.sep = gtk.SeparatorToolItem()
        self.main_tb.insert(self.sep, 3)

        # URL related buttons
        self.url_tb = gtk.ToolButton()
        i = gtk.Image()
        pixbuf = gtk.gdk.pixbuf_new_from_file(self.img_path + 'response-headers.png')
        scaled_buf = pixbuf.scale_simple(24,24,gtk.gdk.INTERP_BILINEAR)
        i.set_from_pixbuf(scaled_buf)
        self.url_tb.set_icon_widget(i)
        self.url_tb.set_tooltip_text('URL')
        self.url_tb.connect("clicked", self.show_urls)
        self.url_tb.set_sensitive(False)
        self.main_tb.insert(self.url_tb, 4)

        self.check_url_tb = gtk.ToolButton()
        i = gtk.Image()
        pixbuf = gtk.gdk.pixbuf_new_from_file(self.img_path  + 'response-body.png')
        scaled_buf = pixbuf.scale_simple(24,24,gtk.gdk.INTERP_BILINEAR)
        i.set_from_pixbuf(scaled_buf)
        self.check_url_tb.set_icon_widget(i)
        self.check_url_tb.set_tooltip_text('Check URL')
        self.check_url_tb.connect("clicked", self.check_urls)
        self.check_url_tb.set_sensitive(False)
        self.main_tb.insert(self.check_url_tb, 5)

        self.bad_url_tb = gtk.ToolButton()
        i = gtk.Image()
        pixbuf = gtk.gdk.pixbuf_new_from_file(self.img_path  + 'request-body.png')
        scaled_buf = pixbuf.scale_simple(24,24,gtk.gdk.INTERP_BILINEAR)
        i.set_from_pixbuf(scaled_buf)
        self.bad_url_tb.set_icon_widget(i)
        self.bad_url_tb.set_tooltip_text('Check bad URL')
        self.bad_url_tb.connect("clicked", self.check_bad_urls)
        self.bad_url_tb.set_sensitive(False)
        self.main_tb.insert(self.bad_url_tb, 6)
        # Separator
        self.sep = gtk.SeparatorToolItem()
        self.main_tb.insert(self.sep, 7)

        # Visualizatin buttons
        self.visbin_tb = gtk.ToolButton(gtk.STOCK_ZOOM_FIT)
        self.visbin_tb.connect("clicked", self.execute, 'binvi')
        self.visbin_tb.set_tooltip_text('Visualize binary')
        self.visbin_tb.set_sensitive(False)
        self.main_tb.insert(self.visbin_tb, 8)
        # Separator
        self.sep = gtk.SeparatorToolItem()
        self.main_tb.insert(self.sep, 9)

        # Binary analysis buttons
        self.vtotal_tb = gtk.ToolButton(gtk.STOCK_CONNECT)
        self.vtotal_tb.connect("clicked", self.send_to_virustotal)
        self.vtotal_tb.set_tooltip_text('Send to VirusTotal')
        self.vtotal_tb.set_sensitive(False)
        self.main_tb.insert(self.vtotal_tb, 10)

        self.threat_tb = gtk.ToolButton(gtk.STOCK_JUMP_TO)
        self.threat_tb.connect("clicked", self.execute, 'threat')
        self.threat_tb.set_tooltip_text('Search in Threat Expert')
        self.threat_tb.set_sensitive(False)
        self.main_tb.insert(self.threat_tb, 11)

        self.shellcode_tb = gtk.ToolButton(gtk.STOCK_FIND)
        self.shellcode_tb.connect("clicked", self.search_shellcode)
        self.shellcode_tb.set_tooltip_text('Search for Shellcode')
        self.shellcode_tb.set_sensitive(False)
        self.main_tb.insert(self.shellcode_tb, 12)

        # not yet working properly
        self.antivm_tb = gtk.ToolButton(gtk.STOCK_FIND_AND_REPLACE)
        self.antivm_tb.connect("clicked", self.search_antivm)
        self.antivm_tb.set_tooltip_text('Search for antivm tricks')
        self.antivm_tb.set_sensitive(False)
        self.main_tb.insert(self.antivm_tb, 13)

        self.packed_tb = gtk.ToolButton(gtk.STOCK_CONVERT)
        self.packed_tb.connect("clicked", self.check_packer)
        self.packed_tb.set_tooltip_text('Check if the PE file is packed')
        self.packed_tb.set_sensitive(False)
        self.main_tb.insert(self.packed_tb, 14)

        # Separator
        self.sep = gtk.SeparatorToolItem()
        self.main_tb.insert(self.sep, 15)

        # Search components
        self.search_tb = gtk.ToolItem()
        self.search_label = gtk.Label('  Search:  ')
        self.search_tb.add(self.search_label)
        self.main_tb.insert(self.search_tb, 16)

        self.search_combo_tb = gtk.ToolItem()
        self.search_combo = gtk.combo_box_new_text()

        options = ['Hexadecimal', 'String', 'String no case', 'Regexp', 'Unicode', 'Unicode no case']
        for option in options:
            self.search_combo.append_text(option)
        self.search_combo_tb.add(self.search_combo)
        self.main_tb.insert(self.search_combo_tb, 17)

        self.search_entry_tb = gtk.ToolItem()
        self.search_entry = gtk.Entry(100)
        self.search_entry_tb.add(self.search_entry)
        self.main_tb.insert(self.search_entry_tb, 18)

        self.search_tb = gtk.ToolButton(gtk.STOCK_FIND)
        self.search_tb.connect("clicked", self.search)
        self.search_tb.set_tooltip_text('Search')
        self.search_tb.set_sensitive(False)
        self.main_tb.insert(self.search_tb, 19)

        # Separator
        self.sep = gtk.SeparatorToolItem()
        self.main_tb.insert(self.sep, 20)

        # Exit button
        self.exit_tb = gtk.ToolButton(gtk.STOCK_QUIT)
        self.exit_tb.connect("clicked", self._bye)
        self.exit_tb.set_tooltip_text('Have a nice day ;-)')
        self.main_tb.insert(self.exit_tb, 21)

        # Separator
        self.sep = gtk.SeparatorToolItem()
        self.sep.set_expand(True)
        self.sep.set_draw(False)
        self.main_tb.insert(self.sep, 22)

        # About button
        self.about_tb = gtk.ToolButton(gtk.STOCK_ABOUT)
        self.about_tb.connect("clicked", self.create_about_dialog)
        self.about_tb.set_tooltip_text('About Bokken')
        self.main_tb.insert(self.about_tb, 23)

        # Throbber
        self.throbber = throbber.Throbber()
        self.throbber_tb = gtk.ToolItem()
        self.throbber_tb.add(self.throbber)
        self.main_tb.insert(self.throbber_tb, 24)

        self.toolbox.pack_start(self.main_tb, True, True)


        self.show_all()

    #
    # Functions
    #

    # Private methods
    #
    def _bye(self, widget):
        msg = ("Do you really want to quit?")
        dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO, msg)
        opt = dlg.run()
        dlg.destroy()

        if opt != gtk.RESPONSE_YES:
            return True

        gtk.main_quit()
        return False

    def disable_all(self):
        for child in self:
            try:
                if child.label.label not in ['New', 'Quit', 'About']:
                    child.set_sensitive(False)
            except:
                pass

    def enable_all(self):
        for toolbar in self:
            for child in toolbar:
                child.set_sensitive(True)

    # New File related methods
    #
    def new_file(self, widget):
        dialog = file_dialog.FileDialog()
        dialog.run()
        self.file = dialog.file

        # Clean full vars where file parsed data is stored as cache
        self.uicore.clean_fullvars()

        # Check if file name is an URL, pyew stores it as 'raw'
        self.uicore.is_url(self.file)

        # Just open the file if path is correct or an url
        if self.uicore.pyew.format != 'URL' and not os.path.isfile(self.file):
            print "Incorrect file argument:", FAIL, self.file, ENDC
            sys.exit(1)

        # Use threads not to freeze GUI while loading
        # FIXME: Same code used in main.py, should be converted into a function
        self.throbber.running(True)
        t = threading.Thread(target=self.main.load_file, args=(self.file,))
        t.start()
        gobject.timeout_add(500, self.load_data, t)

    def load_data(self, thread):
        if thread.isAlive() == True:
            return True
        else:
            self.throbber.running('')
            self.main.show_file_data(thread)
            return False

    # Button callback methods
    #
    def search_pdfstreams(self, widget):
        if self.uicore.pyew.format in 'PDF':
            streams = self.uicore.get_pdf_streams()
    
            self.create_search_dialog()
            enditer = self.search_dialog.output_buffer.get_end_iter()
    
            FILTER=''.join([(len(repr(chr(x)))==3) and chr(x) or '.' for x in range(256)])
    
            for hit in streams:
                hit = ( "HIT [0x%08x]:\t%s\n" % (hit[0], hit[1].translate(FILTER)) )
                self.search_dialog.output_buffer.insert(enditer, hit)
        else:
            md = gtk.MessageDialog(None, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_INFO, gtk.BUTTONS_CLOSE, "The file is not a PDF, could not search for streams")
            md.run()
            md.destroy()

    def search(self, widget):
        data = self.search_entry.get_text()
        model = self.search_combo.get_model()
        active = self.search_combo.get_active()
        option = model[active][0]

        results = self.uicore.dosearch(data, self.options_dict[option])

        self.create_search_dialog()
        enditer = self.search_dialog.output_buffer.get_end_iter()

        FILTER=''.join([(len(repr(chr(x)))==3) and chr(x) or '.' for x in range(256)])
        for element in results:
            hit = ("HIT [0x%08x]: %s\n" % (element.keys()[0], element.values()[0].translate(FILTER)))
            self.search_dialog.output_buffer.insert(enditer, hit)

    def show_urls(self, widget):
        urls = self.uicore.get_urls()
        if urls:
            self.create_search_dialog()
            enditer = self.search_dialog.output_buffer.get_end_iter()
    
            for url in urls:
                self.search_dialog.output_buffer.insert(enditer, url + '\n')
        else:
            md = gtk.MessageDialog(None, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_INFO, gtk.BUTTONS_CLOSE, "No URLs found :(")
            md.run()
            md.destroy()

    def check_urls(self, widget):
        self.throbber.running(True)
        # Use threads to avoid freezing the GUI
        t = threading.Thread(target=self.uicore.check_urls)
        t.start()
        # This call must not depend on load_file data
        gobject.timeout_add(500, self.show_checked_urls, t)

    def show_checked_urls(self, thread):
        if thread.isAlive() == True:
            return True
        else:
            self.throbber.running('')
            self.create_search_dialog()
            enditer = self.search_dialog.output_buffer.get_end_iter()
        
            if self.uicore.checked_urls:
                for url in self.uicore.checked_urls:
                    self.search_dialog.output_buffer.insert(enditer, url + '\t\t[OK]\n')
            else:
                self.search_dialog.output_buffer.insert(enditer, 'No URLs found :(\n')

    def check_bad_urls(self, widget):
        self.throbber.running(True)
        # Use threads to avoid freezing the GUI
        t = threading.Thread(target=self.uicore.bad_urls)
        t.start()
        # This call must not depend on load_file data
        gobject.timeout_add(500, self.show_bad_urls, t)

    def show_bad_urls(self, thread):
        if thread.isAlive() == True:
            return True
        else:
            self.throbber.running('')
            self.create_search_dialog()
            enditer = self.search_dialog.output_buffer.get_end_iter()
        
            if self.uicore.bad_urls:
                for url in self.uicore.bad_urls:
                    self.search_dialog.output_buffer.insert(enditer, url + '\n')
            else:
                self.search_dialog.output_buffer.insert(enditer, 'No bad URLs found :(')
            return False

    def send_to_virustotal(self, widget):
        vt_answer = self.uicore.sendto_vt()
        if vt_answer:
            self.create_search_dialog()
            enditer = self.search_dialog.output_buffer.get_end_iter()
    
            for match in vt_answer:
                self.search_dialog.output_buffer.insert(enditer, match[0] + '\t\t' + match[1] + '\n')
        else:
            md = gtk.MessageDialog(None, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_INFO, gtk.BUTTONS_CLOSE, "No response from VirusTotal :_(")
            md.run()
            md.destroy()

    def search_shellcode(self, widget):
        try:
            import libemu
            has_libemu = True
        except:
            has_libemu = False

        if has_libemu:
            message = 'This plugin has not been ported yet, look at the terminal for the output'
            self.execute(widget, 'sc')
        else:
            message = 'No libemu found, please install it to use this plugin\n\tGet it from: http://libemu.carnivore.it'

        md = gtk.MessageDialog(None, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_INFO, gtk.BUTTONS_CLOSE, message)
        md.run()
        md.destroy()

    def search_antivm(self, widget):

        self.execute(widget, 'antivm')
        message = 'This plugin has not been ported yet, look at the terminal for the output'
        md = gtk.MessageDialog(None, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_INFO, gtk.BUTTONS_CLOSE, message)
        md.run()
        md.destroy()

    def check_packer(self, widget):
        packers = self.uicore.get_packers()
        if packers:
            self.create_search_dialog()
            enditer = self.search_dialog.output_buffer.get_end_iter()
    
            for packer in packers:
                self.search_dialog.output_buffer.insert(enditer, ''.join(packer) + '\n')
        else:
            md = gtk.MessageDialog(None, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_INFO, gtk.BUTTONS_CLOSE, "No packers found")
            md.run()
            md.destroy()

    def create_search_dialog(self):

        import search_dialog
        self.search_dialog = search_dialog.SearchDialog()

        return False

    def create_about_dialog(self, widget):
        about = gtk.AboutDialog()
        about.set_program_name("Bokken")
        about.set_version("1.0")
        about.set_copyright("(c) Hugo Teso <hteso@inguma.eu>")
        about.set_comments("A GUI for pyew and (soon) radare2!")
        about.set_website("http://bokken.inguma.eu")
        about.set_logo(gtk.gdk.pixbuf_new_from_file("ui/data/logo.png"))
        about.run()
        about.destroy()

    # Executes pyew's plugins
    def execute(self, widget, plugin):
        self.uicore.execute_plugin(plugin)

