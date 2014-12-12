'''
highword.py

Copyright 2010 Andres Riancho

This file is part of w3af, w3af.sourceforge.net .

w3af is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation version 2 of the License.

w3af is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with w3af; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

'''
import gtk
import gobject

class HighWord(object):
    '''Class that gives the machinery to search to a TextView.

    Just inheritate it from the box that has the textview to extend.

    @param textview: the textview to extend

    @author: Facundo Batista <facundobatista =at= taniquetil.com.ar>
    '''
    def __init__(self, textview):
        self.textview = textview
        # By default, match case
        self._matchCaseValue = True
        # colors for textview and entry backgrounds
        self.textbuf = self.textview.get_buffer()
        self.textbuf.create_tag("blue-background", background="lightgreen")
        self.prev_word = ''

    def _find(self, word):
        '''Actually find the text, and handle highlight and selection.'''
        # Only search if word has changed
        if word == self.prev_word:
            return False
        self.prev_word = word
        self._clean()
        tosearch = word
        if not tosearch:
            return False
        positions = self.highlight(tosearch, "blue-background", self._matchCaseValue)
        if not len(positions):
            return False
        return False

    def highlight(self, text, tag='yellow-background', case_sensitive=True):
        """Find the text, and handle highlight."""

        # Before searching, I clean the text parameter, as it might contain
        # null bytes, which will trigger an error like:
        # TypeError: GtkTextIter.forward_search() argument 1 must be string without null bytes, not str
        text = str(text)
        text = text.replace('\x00','')
        # TODO: Will the highlighting succeed? How's the text with \0's actually
        # printed in the textview?

        flags = gtk.TEXT_SEARCH_VISIBLE_ONLY
        startIter =  self.textbuf.get_start_iter()
        # find the positions where the phrase is found
        positions = []
        while True:
            result = startIter.forward_search(text, flags, None)
            if result:
                positions.append((result[0], result[1]))
                startIter = result[1]
            else:
                break
        # highlight them all
        for (iterini, iterfin) in positions:
            self.textbuf.apply_tag_by_name(tag, iterini, iterfin)
        return positions

    def _clean(self, tag='blue-background'):
        '''Cleans the entry colors.'''
        # highlights
        (ini, fin) = self.textbuf.get_bounds()
        self.textbuf.remove_tag_by_name(tag, ini, fin)
