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
        # Translation HTML for sentences
        self.doc_tra_html = []
        # Translation strings, not necessarily accepted
        self.doc_tra = []
        # List of accepted translations of sentences in current doc
        self.doc_tra_acep = []
        # String concatenating accepted sentences
        self.doc_tra_acep_str = ''
        # Index of current sentence
        self.sindex = -1
        # SENTENCE
        # The current sentence
        self.sentence = None
        # HTML for the current source sentence
        self.fue_seg_html = None
        # Current sentence's segments (NOT ACTUALLY USED FOR ANYTHING CURRENTLY)
        self.segs = None
        # HTML for current sentence's segments
        self.tra_seg_html = None
        # Translation of the current sentence
        self.tra = None
        # TOGGLES: isdoc, nocorr, ocultar
        self.props = {}
        # Default
        self.props['tfuente'] = "120%"

    def init_doc(self):
#        self.doc_html = self.doc.select_html(index, self.fue_seg_html)
        nsent = len(self.doc)
        # List of translation HTML for sentences
        self.doc_tra_html = [""] * nsent
        # List of translation strings for sentences
        self.doc_tra = [""] * nsent
        # List of accepted translation strings for sentences
        self.doc_tra_acep = [""] * nsent
        # List of seg HTML for any selected sentences
        self.doc_select_html = [""] * nsent
        self.doc_html = self.doc.html
        self.props['tfuente'] = "90%" if nsent > 1 else "120%"

#    def get_accepted_t(self):
#        # First re-instate doc_html
#        self.doc_html = self.doc.html
#        # Return a string containing all of the non-empty accepted translations.
#        return "\n".join([t for t in self.doc_tra_acep if t])

    def doc_unselect_sent(self):
        # Revert to version of doc html with nothing segmented.
        self.doc_html = self.doc.html

    def update_doc(self, index):
        self.doc_html = self.doc.select_html(index, self.fue_seg_html)
        self.doc_select_html[index] = self.fue_seg_html
        self.sindex = index

#    def translate_sent(self, index, tsegs, thtml):
#        self.segs = tsegs
#        self.tra_seg_html = thtml

    def accept_sent(self, index, trans):
        """What happens when a sentence translation is accepted."""
        print("+++Adding accepted translation for position {}".format(index))
        # Update the accepted translations
        self.doc_tra_acep[index] = trans
        print("+++New doctrans: {}".format(self.doc_tra_acep))
        # Return a string concatenating all accepted translations
        self.doc_tra_acep_str = self.stringify_doc_tra()
#        "\n".join([t for t in self.doc_tra_acep if t]).strip()
        self.doc_unselect_sent()
        self.props['tfuente'] = "90%"

    def stringify_doc_tra(self):
        """Create a string representation of the currently accepted sentence translations.
        Probably need to make the more efficient by saving series of consecutive sentences
        that have already been stringified."""
        string = ''
        for sent_trans in self.doc_tra_acep:
            if not sent_trans:
                continue
            if "¶" == sent_trans[-1]:
#                print("Paragraph in {}".format(sent_trans))
                # New paragraph after this sentence
                # Replace the ¶ with a newline
                sent_trans = sent_trans.replace("¶", "\n")
            else:
                sent_trans += " "
            string += sent_trans
        return string.strip()

    def init_sent(self, index):
        """What happens after a sentence has been translated."""
        cap = self.sentence.capitalized
        self.props['cap'] = cap
        self.props['punc'] = self.sentence.get_final_punc()
        self.fue_seg_html = ''.join([s[-1] for s in self.tra_seg_html])
        self.tra = GUI.clean_sentence(' '.join([s[4] for s in self.tra_seg_html]), cap)
        self.doc_tra_html[index] = self.tra_seg_html
        self.doc_tra[index] = self.tra

    def clear(self, record=False, translation='', isdoc=False):
        """Clear all document and sentence variables."""
        sentrec = None
        if self.sentence:
            sentrec = self.sentence.record
        self.tra_seg_html = None
        self.sentence = None
        self.doc = None
        self.doc_tra_acep = []
        self.doc_tra_html = []
        self.doc_tra = []
        self.doc_tra_acep_str = ''
        self.doc_html = ''
        self.doc_select_html = []
        self.props['tfuente'] = "90%" if isdoc else "120%"
        if record:
            # Record the sentence translation
            if self.session:
                self.session.record(sentrec, translation=translation)
            else:
                print("NO SESSION SO NOTHING TO RECORD")

    def set_props(self, form, bool_props=None, props=None):
        """Set the property values from the form dict. bool-props and props
        are lists of prop strings."""
        if bool_props:
            for prop in bool_props:
                if prop in form:
                    self.props[prop] = form.get(prop) == 'true'
        if props:
            for prop in props:
                if prop in form:
                    self.props[prop] = form[prop]

    @staticmethod
    def clean_sentence(string, capitalize=True):
        """Clean up sentence for display in interface.
        Basically a duplicate of the Javascript function in tra.html and sent.html."""
        string = string.replace("&nbsp;", ' ')
        string = re.sub(r"\s+([.,;?!])", r"\1", string)
        if capitalize:
            string = string[0].upper() + string[1:]
        return string
