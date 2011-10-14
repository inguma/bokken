#       menu_bar.py
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

import gtk, gobject
import threading

FAIL = '\033[91m'
OKGREEN = '\033[92m'
ENDC = '\033[0m'

# We need it for the "New" button
import ui.file_dialog as file_dialog

class MenuBar(gtk.MenuBar):
    '''Main TextView elements'''

    def __init__(self, main):
        super(MenuBar,self).__init__()
        self.main = main
        self.uicore = self.main.uicore
        self.dependency_check = self.main.dependency_check

        # File Menu
        filemenu = gtk.Menu()
        filem = gtk.MenuItem("_File")
        filem.set_submenu(filemenu)
       
        agr = gtk.AccelGroup()
        self.main.window.add_accel_group(agr)

        newi = gtk.ImageMenuItem(gtk.STOCK_NEW, agr)
        newi.connect("activate", self.new_file)
        key, mod = gtk.accelerator_parse("<Control>N")
        newi.add_accelerator("activate", agr, key, 
            mod, gtk.ACCEL_VISIBLE)
        filemenu.append(newi)

        savem = gtk.ImageMenuItem(gtk.STOCK_SAVE, agr)
        key, mod = gtk.accelerator_parse("<Control>S")
        savem.add_accelerator("activate", agr, key, 
            mod, gtk.ACCEL_VISIBLE)
        filemenu.append(savem)

        sep = gtk.SeparatorMenuItem()
        filemenu.append(sep)

        exit = gtk.ImageMenuItem(gtk.STOCK_QUIT, agr)
        key, mod = gtk.accelerator_parse("<Control>Q")
        exit.add_accelerator("activate", agr, key, 
            mod, gtk.ACCEL_VISIBLE)

        exit.connect("activate", self._bye)
        
        filemenu.append(exit)

        self.append(filem)

        # Edit Menu
        editmenu = gtk.Menu()
        editm = gtk.MenuItem("Edit")
        editm.set_submenu(editmenu)

        self.append(editm)

        tmenu = gtk.Menu()

        themem = gtk.ImageMenuItem(gtk.STOCK_SELECT_COLOR)
        themem.get_children()[0].set_label('Themes')
        themem.set_submenu(tmenu)

        themes = ['Classic', 'Cobalt', 'kate', 'Oblivion', 'Tango']
        for theme in themes:
            themei = gtk.MenuItem(theme)
            themei.connect("activate", self._on_theme_change)
            tmenu.append(themei)

        editmenu.append(themem)

        # View Menu
        viewmenu = gtk.Menu()
        viewm = gtk.MenuItem("_View")
        viewm.set_submenu(viewmenu)

        self.append(viewm)

        self.vmenu = gtk.Menu()

        tabsm = gtk.ImageMenuItem(gtk.STOCK_PREFERENCES)
        tabsm.get_children()[0].set_label('Show tabs')
        tabsm.set_submenu(self.vmenu)

        viewmenu.append(tabsm)

        # Help Menu
        helpmenu = gtk.Menu()
        helpm = gtk.MenuItem("_Help")
        helpm.set_submenu(helpmenu)
       
        helpi = gtk.ImageMenuItem(gtk.STOCK_HELP, agr)
        key, mod = gtk.accelerator_parse("<Control>H")
        helpi.add_accelerator("activate", agr, key, 
            mod, gtk.ACCEL_VISIBLE)
        helpmenu.append(helpi)

        aboutm = gtk.ImageMenuItem(gtk.STOCK_ABOUT, agr)
        aboutm.connect("activate", self.create_about_dialog)
        key, mod = gtk.accelerator_parse("<Control>A")
        aboutm.add_accelerator("activate", agr, key, 
            mod, gtk.ACCEL_VISIBLE)
        helpmenu.append(aboutm)

        self.append(helpm)

    #
    # Functions
    #

    # Private methods
    #

    def create_view_menu(self):
        self.nb = self.main.tviews.right_notebook
        for x in self.nb.get_children():
            box = self.nb.get_tab_label(x)
            element = box.get_children()[1].get_text().lower()
            item = gtk.CheckMenuItem("Show " + element)
            if element != 'full info':
                item.set_active(True)
            item.connect("activate", self._on_status_view)
            self.vmenu.append(item)
        self.vmenu.show_all()

    def _on_status_view(self, widget):
        target = widget.get_label().split(' ')[1]
        for x in self.nb.get_children():
            y = self.nb.get_tab_label(x)
            if target in y.get_children()[1].get_text().lower():
                target = x
                break
        if widget.active:
            x.show()
        else:
            x.hide()

    def _on_theme_change(self, widget):
        theme = widget.get_label()
        self.main.tviews.update_theme(theme)

    def _bye(self, widget):
        msg = ("Do you really want to quit?")
        dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO, msg)
        opt = dlg.run()
        dlg.destroy()

        if opt != gtk.RESPONSE_YES:
            return True

        gtk.main_quit()
        return False

    # New File related methods
    #
    def new_file(self, widget, file=''):
        if not file:
            dialog = file_dialog.FileDialog(False, self.dependency_check.HAS_RADARE, 'radare', '')
            dialog.run()
            self.file = dialog.file
        else:
            self.file = file

        # Check if file name is an URL, pyew stores it as 'raw'
        self.uicore.is_url(self.file)

        #self.manager.add_item('file://' + self.file)

        # Just open the file if path is correct or an url
        if self.uicore.core.format != 'URL' and not os.path.isfile(self.file):
            print "Incorrect file argument:", FAIL, self.file, ENDC
            return False

        # Clean full vars where file parsed data is stored as cache
        self.uicore.clean_fullvars()

        # Use threads not to freeze GUI while loading
        # FIXME: Same code used in main.py, should be converted into a function
        self.throbber = self.main.topbuttons.throbber
        self.throbber.running(True)
        t = threading.Thread(target=self.main.load_file, args=(self.file,))
        t.start()
        gobject.timeout_add(500, self.load_data, t)

    def recent_kb(self, widget):
        """Activated when an item from the recent projects menu is clicked"""

        uri = widget.get_current_item().get_uri()
        # Strip 'file://' from the beginning of the uri
        file_to_open = uri[7:]
        self.new_file(None, file_to_open)

    def load_data(self, thread):
        if thread.isAlive() == True:
            return True
        else:
            self.throbber.running('')
            self.main.show_file_data(thread)
            return False

    def create_about_dialog(self, widget):
        import ui.about as about

        about_dlg = about.AboutDialog()
        dialog = about_dlg.create_dialog()

        dialog.run()
        dialog.destroy()
