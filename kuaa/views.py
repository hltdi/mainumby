# Ñe'ẽasa. Parsing and translation with minimal dependency grammars.
#
########################################################################
#
#   This file is part of the HLTDI L^3 project
#   for parsing, generation, translation, and computer-assisted
#   human translation.
#
#   Copyright (C) 2015, HLTDI <gasser@cs.indiana.edu>
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
# 2015.08.02

from flask import request, session, g, redirect, url_for, abort, render_template, flash
from kuaa import app, translate, make_document, load, seg_trans

SPA = GRN = DOC = SENT = None
SINDEX = 0

def load_languages():
    global GRN, SPA
    SPA, GRN = load()

def make_doc(text):
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

@app.route('/')
def index():
    print("In index...")
    return redirect(url_for('base'))

@app.route('/base', methods=['GET', 'POST'])
def base():
#    if not SPA:
#        print("Cargando idiomas...")
#        load_languages()
#    return render_template('doc.html')
    print("In base...")
    if request.method == 'POST' and 'Cargar' in request.form:
        return render_template('doc.html')
    return render_template('base.html')

@app.route('/doc', methods=['GET', 'POST'])
def doc():
    print("In doc...")
    if not SPA:
        load_languages()
#    global DOC
#    if request.method == 'POST' and 'text' in request.form:
#        print("Form for doc: {}".format(request.form))
#        sindex = 0
#        DOC = make_document(SPA, GRN, request.form.get('text'))
#        print("Created document {}".format(DOC))
#        sentence = DOC[sindex]
#        print("First sentence {}".format(sentence))
#        return render_template('tra.html', translation=None, sindex=sindex, sentence=sentence, next=False)
    return render_template('doc.html')

@app.route('/tra', methods=['GET', 'POST'])
def tra():
    print("In tra...")
    form = request.form
    print("Form for tra: {}".format(form))
    if form.get('next') == 'tra':
#    if 'tra' in form:
        t = translate(SENTENCE, SPA, GRN)
        print("Translations {}".format(t))
        return render_template('tra.html', sentence=SENTENCE, translation=t)
    elif form.get('next') == 'enter':
        return render_template('tra.html', sentence=None, translation=None)
    elif form.get('next') == 'sent':
        return render_template('sent.html', sentence=None, translation=None)
    return render_template('tra.html', sentence=None, translation=None)

@app.route('/sent', methods=['GET', 'POST'])
def sent():
    print("In sent...")
    form = request.form
    print("Form for sent: {}".format(form))
    if 'text' in form and not DOC:
        make_doc(form['text'])
        print("Created document {}".format(DOC))
    get_sentence()
    print("Current sentence {}".format(SENTENCE))
    if not SENTENCE:
        return render_template('doc.html')
    else:
        segs = seg_trans(SENTENCE, SPA, GRN)
    print("Found segs {}".format(segs))
#    if 'tra' in form:
#        print("Translating sentence {}".format(sentence.raw))
#        return render_template('tra.html', sentence=sentence, translation=['foo', 'bar', 'baz'], next=False)
    return render_template('sent.html', sentence=segs)
#    if request.method == 'POST':
#        sindex = form.get('sindex', 0)
#        if form.get('next'):
#            sentence = DOC[sindex+1]
#            return render_template('tra.html', sindex=sindex+1, sentence=sentence, translation=None, next=False)
#        elif form.get('sentence'):
#            s = form['sentence']
#            print("Sentence {}".format(s))
#            t = translate(s, SPA, GRN)
#            print("Translations {}".format(t))
#            return render_template('tra.html', translation=t, sentence=s, sindex=sindex, next=False)

