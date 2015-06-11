#       python_textview.py
#       
#       Copyright 2015 Hugo Teso <hugo.teso@gmail.com>
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

import gtk
import pango
import gtksourceview2

from threading import Thread
from cStringIO import StringIO

class ScriptThread(Thread):

    def __init__(self, cobj, locals, buff):
        Thread.__init__(self)
        self.setDaemon(True)
        self.cobj = cobj
        self.locals = locals
        self.buff = buff

    def run(self):
        old_stdout = sys.stdout
        redirected_output = sys.stdout = StringIO()
        try:
            exec(self.cobj, self.locals)
        except Exception, e:
            print str(e)
        sys.stdout = old_stdout

        end_iter = self.buff.get_end_iter()
        self.buff.insert(end_iter, redirected_output.getvalue() + '\n')

class PythonTextView(gtk.HBox):
    '''Console TextView elements'''

    def __init__(self, uicore):
        super(PythonTextView,self).__init__(False, 1)

        self.uicore = uicore

        # Set local objects to be accessed from the terminal
        self.exprloc = {}
        self.exprloc['core'] = self.uicore.core
        self.exprloc['bin'] = self.uicore.bin
        self.exprloc['info'] = self.uicore.info
        self.exprloc['baddr'] = self.uicore.baddr
        self.exprloc['size'] = self.uicore.size
        self.exprloc['strings'] = self.uicore.allstrings
        self.exprloc['relocs'] = self.uicore.allrelocs
        self.exprloc['functions'] = self.uicore.allfuncs
        self.exprloc['sections'] = self.uicore.allsections
        self.exprloc['imports'] = self.uicore.allimports
        self.exprloc['symbols'] = self.uicore.allexports
        self.exprloc['file_info'] = self.uicore.fileinfo
        self.exprloc['magic'] = self.uicore.ars_magica

        self.py_hb = gtk.HBox(False)
        self.ou_hb = gtk.HBox(False)

        # Toolbar
        self.py_tb_hb = gtk.HBox(False)
        b = SemiStockButton("", gtk.STOCK_CLEAR, 'Clear code panel')
        b.connect("clicked", self._clear_code)
        self.py_tb_hb.pack_end(b, False, False)
        b = SemiStockButton("", gtk.STOCK_MEDIA_PLAY, 'Execute code')
        b.connect("clicked", self._exec)
        self.py_tb_hb.pack_end(b, False, False)

        self.ou_tb_hb = gtk.HBox(False)

        wrap = gtk.ToggleToolButton(stock_id=gtk.STOCK_JUSTIFY_FILL)
        b = SemiStockButton("", gtk.STOCK_CLEAR, 'Clear output panel')
        b.connect("clicked", self._clear)
        self.ou_tb_hb.pack_end(b, False, False)
        wrap.set_active(True)
        wrap.set_tooltip_text('Switch text wrap')
        self.ou_tb_hb.pack_end(wrap, False, False)
        b = SemiStockButton("", gtk.STOCK_HELP, 'Show help')
        b.connect("clicked", self._help)
        self.ou_tb_hb.pack_end(b, False, False)

        # Panels VBoxes
        self.py_vb= gtk.VBox(False)
        self.ou_vb= gtk.VBox(False)

        self.py_vb.pack_start(self.py_tb_hb, False, True, 0)
        self.ou_vb.pack_start(self.ou_tb_hb, False, True, 0)

        self.pack_start(self.py_vb, True, True, 0)
        self.pack_start(self.ou_vb, True, True, 0)

        #################################################################
        # Input GtkSourceView TextView (Python code panel)
        #################################################################

        # Use GtkSourceView to add eye candy :P
        # create buffer
        lm = gtksourceview2.LanguageManager()
        # Add ui dir to language paths
        self.py_buffer = gtksourceview2.Buffer()
        self.py_buffer.set_data('languages-manager', lm)
        self.py_view = gtksourceview2.View(self.py_buffer)
        self.py_view.set_left_margin(5)

        # FIXME options must be user selectable (statusbar)
        self.py_view.set_editable(True)
        self.py_view.set_auto_indent(True)
        self.py_view.set_highlight_current_line(True)
        # posible values: gtk.WRAP_NONE, gtk.WRAP_CHAR, gtk.WRAP_WORD...
        self.py_view.set_wrap_mode(gtk.WRAP_NONE)
        
        # setup view
        font_desc = pango.FontDescription('monospace 9')
        if font_desc:
            self.py_view.modify_font(font_desc)

        self.py_buffer.set_highlight_syntax(True)
        manager = self.py_buffer.get_data('languages-manager')
        language = manager.get_language('python')
        self.py_buffer.set_language(language)

        self.mgr = gtksourceview2.style_scheme_manager_get_default()

        # Scrolled Window
        self.python_scrolled_window = gtk.ScrolledWindow()
        self.python_scrolled_window.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        self.python_scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.python_scrolled_window.show()
        # Add Textview to Scrolled Window
        self.python_scrolled_window.add(self.py_view)
        self.py_vb.pack_start(self.python_scrolled_window, expand=True, fill=True)

        #Always on bottom on change
        self.vajd = self.python_scrolled_window.get_vadjustment()
        self.vajd.connect('changed', lambda a, s=self.python_scrolled_window: self.rescroll(a,s))

        end_iter = self.py_buffer.get_end_iter()
        self.py_buffer.insert(end_iter, "#\n# Your python code goes here\n# Press the run button above to execute\n#\n\n")

        #################################################################
        # Input GtkSourceView TextView (Output panel)
        #################################################################

        # Use GtkSourceView to add eye candy :P
        # create buffer
        lm = gtksourceview2.LanguageManager()
        # Add ui dir to language paths
        paths = lm.get_search_path()
        paths.append(os.path.dirname(__file__) + os.sep + 'data' + os.sep)
        lm.set_search_path(paths)
        self.buffer = gtksourceview2.Buffer()
        self.buffer.create_tag("green-background", background="green", foreground="black")
        self.buffer.set_data('languages-manager', lm)
        self.view = gtksourceview2.View(self.buffer)
        wrap.connect("clicked", self._change_wrap)
        self.view.set_left_margin(5)
        self.view.set_wrap_mode(gtk.WRAP_WORD)

        # FIXME options must be user selectable (statusbar)
        self.view.set_editable(False)
        #self.view.set_highlight_current_line(True)
        # posible values: gtk.WRAP_NONE, gtk.WRAP_CHAR, gtk.WRAP_WORD...
        
        # setup view
        font_desc = pango.FontDescription('monospace 9')
        if font_desc:
            self.view.modify_font(font_desc)

        self.buffer.set_highlight_syntax(False)
        manager = self.buffer.get_data('languages-manager')
        language = manager.get_language('asm')
        self.buffer.set_language(language)

        self.mgr = gtksourceview2.style_scheme_manager_get_default()

        # Scrolled Window
        self.console_scrolled_window = gtk.ScrolledWindow()
        self.console_scrolled_window.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        self.console_scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.console_scrolled_window.show()
        # Add Textview to Scrolled Window
        self.console_scrolled_window.add(self.view)
        self.ou_vb.pack_start(self.console_scrolled_window, expand=True, fill=True)

        #Always on bottom on change
        self.vajd = self.console_scrolled_window.get_vadjustment()
        self.vajd.connect('changed', lambda a, s=self.console_scrolled_window: self.rescroll(a,s))

        self._help(self)

    def rescroll(self, adj, scroll):
        adj.set_value(adj.upper-adj.page_size)
        scroll.set_vadjustment(adj)

    def _clear_code(self, widget):
        self.py_buffer.set_text('')

    def _clear(self, widget):
        self.buffer.set_text('')

    def _help(self, widget):
        end_iter = self.buffer.get_end_iter()
        self.buffer.insert(end_iter, "\nBuiltin objects available\n=========================\n\n")
        for key in self.exprloc.keys():
            end_iter = self.buffer.get_end_iter()
            self.buffer.insert(end_iter, key + '\t\t')
        end_iter = self.buffer.get_end_iter()
        self.buffer.insert(end_iter, "\n\n")

    def _exec(self, widget, icon_pos=None, event=None):
        bounds = self.py_buffer.get_bounds()
        pycode = self.py_buffer.get_text(bounds[0], bounds[1])
        cobj = compile(pycode, "vqpython_exec.py", "exec")
        sthr = ScriptThread(cobj, self.exprloc, self.buffer)
        sthr.start()

    def _change_wrap(self, widget):
        if widget.get_active():
            self.view.set_wrap_mode(gtk.WRAP_WORD)
        else:
            self.view.set_wrap_mode(gtk.WRAP_NONE)

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
