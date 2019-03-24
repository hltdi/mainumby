# Mainumby. Parsing and translation with minimal dependency grammars.
#
########################################################################
#
#   This file is part of the PLoGS project
#   for parsing, generation, translation, and computer-assisted
#   human translation.
#
#   Copyleft PLoGS <gasser@indiana.edu>
#   
#   This program is free software: you can redistribute it and/or
#   modify it under the terms of the GNU General Public License as
#   published by the Free Software Foundation, either version 3 of
#   the License, or (at your option) any later version.
#   
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#   GNU General Public License for more details.
#   
#   You should have received a copy of the GNU General Public License
#   along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# =========================================================================
#
# Created 2019.03.23
#
# class for storing variables needed in view.py

import re

class GUI:

    def __init__(self):
        self.session = None
        self.source = None
        self.target = None
        self.doc = None
        self.sentence = None
        self.segs = None
        self.seg_html = None
        self.user = None
        self.om1 = None
        self.doc_html = None
        self.of_html = None
        self.doc_om = []
        self.doc_t = []
        self.users_initialized = False

    def init_doc(self):
#        self.doc_html = self.doc.select_html(index, self.of_html)
        # List of translation HTML for sentences
        self.doc_om = [""] * len(self.doc)
        # List of accepted translation strings for sentences
        self.doc_t = [""] * len(self.doc)
        self.doc_html = self.doc.html

    def update_doc(self, index):
        self.doc_html = self.doc.select_html(index, self.of_html)

    def init_sent(self):
        cap = self.sentence.capitalized
        self.of_html = ''.join([s[-1] for s in self.seg_html])
        self.om1 = GUI.clean_sentence(' '.join([s[4] for s in self.seg_html]), cap)

    @staticmethod
    def clean_sentence(string, capitalize=True):
        """Clean up sentence for display in interface.
        Basically a duplicate of the Javascript function in tra.html and sent.html."""
        string = string.replace("&nbsp;", ' ')
        string = re.sub(r"\s+([.,;?!])", r"\1", string)
        if capitalize:
            string = string[0].upper() + string[1:]
        return string
