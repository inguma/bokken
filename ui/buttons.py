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

        # New file button
        b = SemiStockButton("", gtk.STOCK_NEW, 'Open New file')
        b.connect("clicked", self.new_file)
        b.label.label = 'New'
        self.toolbox.pack_start(b, False, False)
        # Separator
        self.sep = gtk.HSeparator()
        self.toolbox.pack_start(self.sep, False, False)

        # PDF Streams search
        b = SemiStockButton("", gtk.STOCK_INDEX, 'Find PDF Streams')
        b.connect("clicked", self.search_pdfstreams)
        b.set_sensitive(False)
        self.toolbox.pack_start(b, False, False)
        # Separator
        self.sep = gtk.HSeparator()
        self.toolbox.pack_start(self.sep, False, False)

        # URL related buttons
        b = gtk.Button()
        i = gtk.Image()
        pixbuf = gtk.gdk.pixbuf_new_from_file(self.img_path + 'response-headers.png')
        scaled_buf = pixbuf.scale_simple(24,24,gtk.gdk.INTERP_BILINEAR)
        i.set_from_pixbuf(scaled_buf)
        b.set_image(i)
        b.set_tooltip_text('URL')
        b.connect("clicked", self.show_urls)
        b.set_sensitive(False)
        self.toolbox.pack_start(b, False, False)

        b = gtk.Button()
        i = gtk.Image()
        pixbuf = gtk.gdk.pixbuf_new_from_file(self.img_path  + 'response-body.png')
        scaled_buf = pixbuf.scale_simple(24,24,gtk.gdk.INTERP_BILINEAR)
        i.set_from_pixbuf(scaled_buf)
        b.set_image(i)
        b.set_tooltip_text('Check URL')
        b.connect("clicked", self.check_urls)
        b.set_sensitive(False)
        self.toolbox.pack_start(b, False, False)

        b = gtk.Button()
        i = gtk.Image()
        pixbuf = gtk.gdk.pixbuf_new_from_file(self.img_path  + 'request-body.png')
        scaled_buf = pixbuf.scale_simple(24,24,gtk.gdk.INTERP_BILINEAR)
        i.set_from_pixbuf(scaled_buf)
        b.set_image(i)
        b.set_tooltip_text('Check bad URL')
        b.connect("clicked", self.check_bad_urls)
        b.set_sensitive(False)
        self.toolbox.pack_start(b, False, False)
        # Separator
        self.sep = gtk.HSeparator()
        self.toolbox.pack_start(self.sep, False, False)

        # Visualizatin buttons
        b = SemiStockButton("", gtk.STOCK_ZOOM_FIT, 'Visualize Binary')
        b.connect("clicked", self.execute, 'binvi')
        b.set_sensitive(False)
        self.toolbox.pack_start(b, False, False)
        # Separator
        self.sep = gtk.HSeparator()
        self.toolbox.pack_start(self.sep, False, False)

        # Binary analysis buttons
        b = SemiStockButton("", gtk.STOCK_CONNECT, 'Send to VirusTotal')
        b.connect("clicked", self.send_to_virustotal)
        b.set_sensitive(False)
        self.toolbox.pack_start(b, False, False)
        b = SemiStockButton("", gtk.STOCK_JUMP_TO, 'Search in Threat Expert')
        b.connect("clicked", self.execute, 'threat')
        b.set_sensitive(False)
        self.toolbox.pack_start(b, False, False)
        b = SemiStockButton("", gtk.STOCK_FIND, 'Search for Shellcode')
        b.connect("clicked", self.search_shellcode)
        b.set_sensitive(False)
        self.toolbox.pack_start(b, False, False)
        b.set_sensitive(False)      # not yet working properly
        b = SemiStockButton("", gtk.STOCK_FIND_AND_REPLACE, 'Search antivm tricks')
        b.connect("clicked", self.search_antivm)
        b.set_sensitive(False)
        self.toolbox.pack_start(b, False, False)
        b = SemiStockButton("", gtk.STOCK_CONVERT, 'Check if the PE file is packed')
        b.connect("clicked", self.check_packer)
        b.set_sensitive(False)
        self.toolbox.pack_start(b, False, False)
        # Separator
        self.sep = gtk.HSeparator()
        self.toolbox.pack_start(self.sep, False, False)

        # Search components
        self.search_label = gtk.Label('     Search:')
        self.toolbox.pack_start(self.search_label, False, False)
        self.search_combo = gtk.combo_box_new_text()
        options = ['Hexadecimal', 'String', 'String no case', 'Regexp', 'Unicode', 'Unicode no case']
        for option in options:
            self.search_combo.append_text(option)

        self.toolbox.pack_start(self.search_combo, False, False)
        self.search_entry = gtk.Entry(100)
        self.toolbox.pack_start(self.search_entry, False, False)
        b = SemiStockButton("", gtk.STOCK_FIND, 'Search')
        b.connect("clicked", self.search)
        b.set_sensitive(False)
        self.toolbox.pack_start(b, False, False)

        # Separator
        self.sep = gtk.HSeparator()
        self.toolbox.pack_start(self.sep, False, False)
        # Exit button
        b = SemiStockButton("", gtk.STOCK_QUIT, 'Have a nice day ;-)')
        b.label.label = 'Quit'
        b.connect("clicked", self._bye)
        self.toolbox.pack_start(b, False, False)

        # Separator
        self.sep = gtk.HSeparator()
        self.toolbox.pack_start(self.sep, False, False)
        # Throbber
        self.throbber = throbber.Throbber()
        self.toolbox.pack_end(self.throbber, False, False)
        # About button
        b = SemiStockButton("", gtk.STOCK_ABOUT, 'About')
        b.label.label = 'About'
        b.connect("clicked", self.create_about_dialog)
        self.toolbox.pack_end(b, False, False)
        
#        # Grayed?
#        self.toolbox.set_sensitive(True)

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
        for child in self:
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

# Used to create most of the buttons
#
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
