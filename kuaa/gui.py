# Mainumby. Parsing and translation with minimal dependency grammars.
#
########################################################################
#
#   This file is part of the PLoGS project
#   for parsing, generation, translation, and computer-assisted
#   human translation.
#
#   Copyleft 2019 PLoGS <gasser@indiana.edu>
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
# class for storing variables needed in views.py

import re

class GUI:

    def __init__(self):
        self.session = None
        self.user = None
        self.users_initialized = False
        # Source and target languages
        self.source = None
        self.target = None
        # DOCUMENT
        # The current document (if translating document)
        self.doc = None
        # HTML for the current document
        self.doc_html = None
        # HTML for already selected sentences
        self.doc_select_html = None
        self.doc_om = []
        # List of accepted translations of sentences in current doc
        self.doc_trans = []
        # String concatenating accepted sentences
        self.doc_trans_str = ''
        # Index of current sentence
        self.sindex = -1
        # SENTENCE
        # The current sentence
        self.sentence = None
        # HTML for the current source sentence
        self.of_html = None
        # Current sentence's segments
        self.segs = None
        # HTML for current sentence's segments
        self.seg_html = None
        # Translation of the current sentence
        self.om1 = None
        # TOGGLES: isdoc, nocorr, ocultar
        self.props = {}

    def init_doc(self):
#        self.doc_html = self.doc.select_html(index, self.of_html)
        # List of translation HTML for sentences
        self.doc_om = [""] * len(self.doc)
        # List of accepted translation strings for sentences
        self.doc_trans = [""] * len(self.doc)
        # List of seg HTML for any selected sentences
        self.doc_select_html = [""] * len(self.doc)
        self.doc_html = self.doc.html

    def get_accepted_t(self):
        return "\n".join([t for t in self.doc_trans if t])

    def update_doc(self, index):
        self.doc_html = self.doc.select_html(index, self.of_html)
        self.doc_select_html[index] = self.of_html
        self.sindex = index

    def accept_sent(self, index, trans):
        # Update the accepted translations
        self.doc_trans[index] = trans
        # Return a string concatenating all accepted translations
        self.doc_trans_str = "\n".join([t for t in self.doc_trans if t]).strip()

    def init_sent(self):
        cap = self.sentence.capitalized
        self.props['cap'] = cap
        self.props['punc'] = self.sentence.get_final_punc()
        self.of_html = ''.join([s[-1] for s in self.seg_html])
        self.om1 = GUI.clean_sentence(' '.join([s[4] for s in self.seg_html]), cap)

    def clear(self, record=False, translation=''):
        sentrec = None
        if self.sentence:
            sentrec = self.sentence.record
        self.seg_html = None
        self.sentence = None
        self.doc = None
        if record:
            # Record the sentence translation
            if self.session:
                translation = form.get('ometa')
                self.session.record(sentrec, translation=translation)
            else:
                print("NO SESSION SO NOTHING TO RECORD")

    @staticmethod
    def clean_sentence(string, capitalize=True):
        """Clean up sentence for display in interface.
        Basically a duplicate of the Javascript function in tra.html and sent.html."""
        string = string.replace("&nbsp;", ' ')
        string = re.sub(r"\s+([.,;?!])", r"\1", string)
        if capitalize:
            string = string[0].upper() + string[1:]
        return string
