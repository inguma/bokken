#       bindiff.py
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
import re
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
import xdot
import tempfile
from r2.r_core import *

# workaround a bug in valabind or swig here..
try:
   FcnType_FCN
except:
   FcnType_FCN          =   1
   FcnType_SYM          =   4
   BlockDiff_NULL       =   0
   BlockDiff_MATCH      =   'm'
   BlockDiff_UNMATCH    =   'u'

class DiffView(Gtk.VBox):
    ui = '''
    <ui>
        <toolbar name="ToolBar">
            <toolitem action="ZoomIn"/>
            <toolitem action="ZoomOut"/>
            <toolitem action="ZoomFit"/>
            <toolitem action="Zoom100"/>
        </toolbar>
    </ui>
    '''

    def __init__(self):
        GObject.GObject.__init__(self)

        # XDotWidget
        xdotwidget = self.xdotwidget = xdot.DotWidget()
        # Toolbar
        uimanager = Gtk.UIManager()
        actiongroup = Gtk.ActionGroup('Actions')
        actiongroup.add_actions((
            ('ZoomIn', Gtk.STOCK_ZOOM_IN, None, None, None, self.xdotwidget.on_zoom_in),
            ('ZoomOut', Gtk.STOCK_ZOOM_OUT, None, None, None, self.xdotwidget.on_zoom_out),
            ('ZoomFit', Gtk.STOCK_ZOOM_FIT, None, None, None, self.xdotwidget.on_zoom_fit),
            ('Zoom100', Gtk.STOCK_ZOOM_100, None, None, None, self.xdotwidget.on_zoom_100),
        ))
        uimanager.insert_action_group(actiongroup, 0)
        uimanager.add_ui_from_string(self.ui)
        toolbar = uimanager.get_widget('/ToolBar')
        toolbar.set_icon_size(Gtk.IconSize.SMALL_TOOLBAR)
        toolbar.set_style(Gtk.ToolbarStyle.ICONS)
        toolbar.set_show_arrow(False)
        label = self.label = Gtk.Label()
        hbox = Gtk.HBox(False, 5)
        hbox.pack_start(toolbar, False, True, 0)
        hbox.pack_start(label, False, True, 0)
        self.pack_start(hbox, False, True, 0)
        self.pack_start(xdotwidget, True, True, 0)

    def set_filename(self, name):
        self.label.set_text(name)

    def set_code(self, code, fit):
        code = code.replace('graph [bgcolor=white];', 'graph [color=white, bgcolor="invis"];')
        code = code.replace('fontsize="8"', 'fontsize="14"')
        #code = re.sub('style=filled ', 'style="rounded,filled" fillcolor="white" ', code)
        code = code.replace('color="yellow"', 'color="yellow" fillcolor="lightyellow" ')
        code = code.replace('color="red"', 'color="red" fillcolor="lightpink" ')
        code = code.replace('color="lightgray"', 'color="blue" fillcolor="white" ')
        code = code.replace('color=lightgray', 'color="blue" fillcolor="white" ')
        code = re.sub('style=filled ', 'style="rounded,filled" ', code)
        self.xdotwidget.set_dotcode(code)
        if (fit):
            self.xdotwidget.zoom_to_fit()

class DiffWidget(Gtk.VPaned):
    def __init__(self):
        GObject.GObject.__init__(self)
        self.set_position (500)
        # Graph viewers
        hbox = Gtk.HBox(True, 5)
        dw = self.dw = DiffView()
        dw2 = self.dw2 = DiffView()
        hbox.pack_start(dw, True, True, 0)
        hbox.pack_start(dw2, True, True, 0)
        self.add(hbox)
        # Function list
        scrolledwin = Gtk.ScrolledWindow()
        scrolledwin.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        liststore = self.liststore = Gtk.ListStore(str, str, str, str, str)
        treeview = Gtk.TreeView(liststore)
        # Column Address L
        tvcolumn0 = Gtk.TreeViewColumn('Function L')
        treeview.append_column(tvcolumn0)
        cell0 = Gtk.CellRendererText()
        tvcolumn0.pack_start(cell0, True)
        tvcolumn0.add_attribute(cell0, 'text', 0)
        tvcolumn0.set_sort_column_id(0)
        # Column Function L
        tvcolumn1 = Gtk.TreeViewColumn('Address L')
        treeview.append_column(tvcolumn1)
        cell1 = Gtk.CellRendererText()
        tvcolumn1.pack_start(cell1, True)
        tvcolumn1.add_attribute(cell1, 'text', 1)
        tvcolumn1.set_sort_column_id(1)
        # Column Address R
        tvcolumn2 = Gtk.TreeViewColumn('Function R')
        treeview.append_column(tvcolumn2)
        cell2 = Gtk.CellRendererText()
        tvcolumn2.pack_start(cell2, True)
        tvcolumn2.add_attribute(cell2, 'text', 2)
        tvcolumn2.set_sort_column_id(2)
        # Column Function R
        tvcolumn3 = Gtk.TreeViewColumn('Address R')
        treeview.append_column(tvcolumn3)
        cell3 = Gtk.CellRendererText()
        tvcolumn3.pack_start(cell3, True)
        tvcolumn3.add_attribute(cell3, 'text', 3)
        tvcolumn3.set_sort_column_id(3)
        # Column Diff
        tvcolumn4 = Gtk.TreeViewColumn('Diff')
        treeview.append_column(tvcolumn4)
        cell4 = Gtk.CellRendererText()
        tvcolumn4.pack_start(cell4, True)
        tvcolumn4.add_attribute(cell4, 'text', 4)
        tvcolumn4.set_sort_column_id(4)
        # Set treeview options and add it to scrolledwin
        treeview.set_reorderable(True)
        scrolledwin.add(treeview)
        self.add2(scrolledwin)
        treeview.connect('row-activated', self.on_row_activated)

    def on_row_activated(self, treeview, row, col):
        model = treeview.get_model()
        self.row_handler(self, model[row][1], model[row][3])

    def set_row_handler(self, handler):
        self.row_handler = handler

    def set_filename_l(self, name):
        self.dw.set_filename(name)

    def set_filename_r(self, name):
        self.dw2.set_filename(name)

    def set_code_l(self, code, fit):
        self.dw.set_code(code, fit)

    def set_code_r(self, code, fit):
        self.dw2.set_code(code, fit)

    def add_function(self, row):
        self.liststore.append(row)

    def clear_functions(self):
        self.liststore.clear()

class Bindiff():
    def __init__(self, core, tviews):
        #GObject.GObject.__init__(self)
        self.tviews = tviews
        self.c = core
        self.c2 = RCore()
        dw = self.dw = DiffWidget()
        dw.set_row_handler(self.update_graphs)

    def update_graphs(self, dw, addr_l, addr_r):
        if addr_l != '':
            file_l = tempfile.gettempdir()+os.sep+'ragdiff2_l'
            self.c.core.cmd0('agd %s > %s' % (addr_l, file_l))
            fp = file(file_l)
            dw.set_code_l(fp.read(), True)
            fp.close()
            os.unlink(file_l)
        else:
            dw.set_code_l('digraph code { }', False)
        if addr_r != '':
            file_r = tempfile.gettempdir()+os.sep+'ragdiff2_r'
            self.c2.cmd0('agd %s > %s' % (addr_r, file_r))
            fp = file(file_r)
            dw.set_code_r(fp.read(), True)
            fp.close()
            os.unlink(file_r)
        else:
            dw.set_code_r('digraph code { }', False)
    
    def set_file(self, file_r, fcn_thr, bb_thr, bytes):
        # Init cores
        self.c2.cmd0("e scr.interactive=false")
        self.c2.cmd0('e asm.lines=false')
        self.c2.cmd0('e scr.color=0')

        # Improve asm format
        self.c2.cmd0('e asm.bytespace=true')
        self.c2.cmd0('e asm.cmtright=true')
        self.c2.cmd0('e asm.xrefs=false')          # Show xrefs in disassembly
        self.c2.cmd0('e asm.cmtflgrefs=false')     # Show comment flags associated to branch referece
        self.c2.cmd0('e asm.fcnlines=false')
        self.c2.cmd0('e asm.linesright=true')
        self.c2.cmd0('e asm.lineswidth=20')

        self.c2.config.set_i("io.va", 1)
        self.c2.config.set_i("anal.split", 1)
        self.c2.file_open(file_r, 0, 0)
        self.c2.bin_load(None, 0)
        self.c.core.anal.diff_setup_i(bytes, fcn_thr, bb_thr)
        self.c2.anal.diff_setup_i(bytes, fcn_thr, bb_thr)
        # Clear treeview
        self.dw.clear_functions()
        self.dw.set_filename_l(self.c.filename)
        self.dw.set_filename_r(file_r)
    
    def diff(self):
        # Diff
        self.c.core.gdiff(self.c2, True)
        # Fill treeview
        for fcn in self.c.core.anal.get_fcns():
            if (fcn.type == FcnType_FCN or fcn.type == FcnType_SYM):
                diffaddr = '0x%08x' % fcn.diff.addr
                difftype = '%c' % fcn.diff.type
                if (difftype == 'm'): #BlockDiff_MATCH):
                    difftype = "MATCH"
                elif (difftype == BlockDiff_UNMATCH):
                    difftype = "UNMATCH"
                else:
                    difftype = "NEW"
                    diffaddr = ''
                self.dw.add_function([fcn.name, '0x%08x' % fcn.addr, fcn.diff.name, diffaddr, difftype])
        for fcn in self.c2.anal.get_fcns():
            if ((fcn.type == FcnType_FCN or fcn.type == FcnType_SYM) and fcn.diff.type == BlockDiff_NULL):
                self.dw.add_function(['', '', fcn.name, '0x%08x' % fcn.addr, "NEW"])
        #self.dw.show_all()

