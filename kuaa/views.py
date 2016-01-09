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
#
# Created 2015.06.12
# 2015.07
# -- Views for loading languages, entering document, sentence, and translation.

from flask import request, session, g, redirect, url_for, abort, render_template, flash
from kuaa import app, make_document, load, seg_trans, quit

# Global variables for views; probably a better way to do this...
SPA = GRN = DOC = SENT = None
SINDEX = 0
# SOLINDEX = 0

def load_languages():
    """Load Spanish and Guarani data."""
    global GRN, SPA
    SPA, GRN = load()

def make_doc(text):
    """Create a Document object from the text."""
    global DOC
    DOC = make_document(SPA, GRN, text)

def get_sentence():
    global SINDEX
    global SENTENCE
    global DOC
    if SINDEX >= len(DOC):
        SENTENCE = None
        # Save DOC in database or translation cache here
        DOC = None
        SINDEX = 0
        return
    SENTENCE = DOC[SINDEX]
    SINDEX += 1

# def get_solution():
#    global SOLINDEX
#    if SOLINDEX >= len(SENTENCE.solutions):
#        SOLINDEX = 0
#        get_sentence()
#        return
#    solution = SENTENCE.solutions[0]

@app.route('/')
def index():
    print("In index...")
    return redirect(url_for('base'))

@app.route('/base', methods=['GET', 'POST'])
def base():
    print("In base...")
    if request.method == 'POST' and 'Cargar' in request.form:
        return render_template('doc.html')
    return render_template('base.html')

# View for document entry
@app.route('/doc', methods=['GET', 'POST'])
def doc():
    print("In doc...")
    # Load Spanish and Guarani if they're not loaded.
    if not SPA:
        load_languages()
    return render_template('doc.html')

# View for displaying parsed sentence and sentence translation
@app.route('/sent', methods=['GET', 'POST'])
def sent():
    print("In sent...")
    form = request.form
    print("Form for sent: {}".format(form))
    if 'text' in form and not DOC:
        # Create a new document
        make_doc(form['text'])
        print("Created document {}".format(DOC))
    # Get the next sentence in the document
    get_sentence()
    print("Current sentence {}".format(SENTENCE))
    if not SENTENCE:
        # No more sentences, return to doc.html for a new document
        return render_template('doc.html')
    else:
        # Translate and segment the sentence
        segs = seg_trans(SENTENCE, SPA, GRN)
    print("Found segs {}".format(segs))
    # Show segmented sentence
    return render_template('sent.html', sentence=segs)

@app.route('/fin', methods=['GET', 'POST'])
def fin():
    print("In fin...")
    quit()
    return render_template('fin.html')

# View for displaying segment translation (not currently used)
#@app.route('/tra', methods=['GET', 'POST'])
#def tra():
#    print("In tra...")
#    form = request.form
#    print("Form for tra: {}".format(form))
#    if form.get('next') == 'tra':
#        t = translate(SENTENCE, SPA, GRN)
#        print("Translations {}".format(t))
#        return render_template('tra.html', sentence=SENTENCE, translation=t)
#    elif form.get('next') == 'enter':
#        return render_template('tra.html', sentence=None, translation=None)
#    elif form.get('next') == 'sent':
#        return render_template('sent.html', sentence=None, translation=None)
#    return render_template('tra.html', sentence=None, translation=None)

# Not needed because this is in runserver.py and mainumby.py.
if __name__ == "__main__":
    kuaa.app.run(host='0.0.0.0')


