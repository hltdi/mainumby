# Mainumby. Parsing and translation with minimal dependency grammars.
#
########################################################################
#
#   This file is part of the HLTDI L^3 project
#   for parsing, generation, translation, and computer-assisted
#   human translation.
#
#   Copyright (C) 2015, 2016, HLTDI <gasser@indiana.edu>
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

__all__ = ['language', 'entry', 'ui', 'constraint', 'db', 'views', 'variable', 'sentence', 'cs', 'learn', 'utils']

from flask import Flask, url_for, render_template

from .sentence import *
from .learn import *
from .morphology import *
from .record import *
from . import db

## Instantiate the Flask class to get the application
app = Flask(__name__)
app.config.from_object(__name__)

def load(source='spa', target='grn'):
    """Load source and target languages for translation."""
    return kuaa.Language.load_trans(source, target)

#def translate(sentence, source, target,
#              all_sols=False, all_trans=True, interactive=False, verbosity=0):
#    """Translate sentence from source to target language. Use only first solution but multiple translation options."""
#    sentence.initialize(verbosity=verbosity)
#    sentence.solve(translate=True,
#                   all_sols=all_sols, all_trans=all_trans, interactive=interactive, verbosity=verbosity)
#    return sentence.complete_trans()[0]

def seg_trans(sentence, source, target, verbosity=0):
    """Translate sentence and return marked-up sentence with segments colored.
    So far only uses first solution."""
    sentence.initialize(ambig=True, verbosity=verbosity)
    sentence.solve(translate=True, all_sols=False, all_trans=True, interactive=False, verbosity=verbosity)
    if sentence.solutions:
        solution = sentence.solutions[0]
        solution.get_segs()
        return solution.get_seg_html()
    else:
        return sentence.get_html()

def make_document(source, target, text):
    """Create an Mbojereha Document object with the text."""
    d = kuaa.Document(source, target, text, True)
    return d

def quit(session=None):
    """Quit the session (and the program), cleaning up in various ways."""
    for language in Language.languages.values():
        # Store new cached analyses or generated forms for
        # each active language.
        language.quit()
    if session:
        session.quit()

def start():
    """Initialize a session."""
    return kuaa.Session()

# Import views. This has to appear after the app is created.
import kuaa.views

