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
# 2016.03
# -- sent view can either get new sentence or record translation for sentence segment.
# -- SESSION, SEGS, SEG_HTML globals added.
# 2016.04.03
# -- USER added; SESSION created only if there is one.

from flask import request, session, g, redirect, url_for, abort, render_template, flash
from kuaa import app, make_document, load, seg_trans, quit, start, init_users, get_user

# Global variables for views; probably a better way to do this...
SESSION = SPA = GRN = DOC = SENT = SEGS = SEG_HTML = USER = None
SINDEX = 0
USERS_INITIALIZED = False
# SOLINDEX = 0

def initialize():
    global USERS_INITIALIZED
    init_users()
    USERS_INITIALIZED = True

def init_session():
    global SESSION
    global GRN
    global SPA
    if not SPA:
        load_languages()
    # Load users and create session if there's a user
    if USER and not SESSION:
        SESSION = start(SPA, GRN, USER)    

def load_languages():
    """Load Spanish and Guarani data."""
    global GRN, SPA
    SPA, GRN = load()

def make_doc(text):
    """Create a Document object from the text."""
    global DOC
    DOC = make_document(SPA, GRN, text, session=SESSION)

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

def get_segmentation():
    global SENTENCE
    global SPA
    global GRN
    global SEGS
    global SEG_HTML
    SEGS, SEG_HTML = seg_trans(SENTENCE, SPA, GRN)    

@app.route('/')
def index():
#    print("In index...")
    return redirect(url_for('base'))
#    return redirect(url_for('reg'))

@app.route('/base', methods=['GET', 'POST'])
def base():
    print("In base...")
#    if request.method == 'POST' and 'Cargar' in request.form:
#        return render_template('doc.html')
    return render_template('base.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    global USER
    print("In login...")
    form = request.form
    print("Form for login: {}".format(form))
    if not USERS_INITIALIZED:
        initialize()
    if request.method == 'POST' and 'login' in form:
        # Try to find user with username username
        username = form.get('username')
        user = get_user(username)
        if not user:
            print("No such user as {}".format(username))
            return render_template('login.html', error='user')
        else:
            print("Found user {}".format(user))
            password = form.get('password')
            if user.check_password(password):
                USER = user
                return render_template('logged.html', username=username)
            else:
                print("Password doesn't match")
                return render_template('login.html', error='password')
    return render_template('login.html')

@app.route('/logged', methods=['GET', 'POST'])
def logged():
    print("In logged...")
    form = request.form
    print("Form for logged: {}".format(form))
    return render_template('logged.html')

@app.route('/reg', methods=['GET', 'POST'])
def reg():
    print("In reg...")
    form = request.form
    print("Form for reg: {}".format(form))
    return render_template('reg.html')

# Saying account was created
@app.route('/acct', methods=['POST'])
def acct():
    return render_template('acct.html')

# View for document entry
@app.route('/doc', methods=['GET', 'POST'])
def doc():
    print("In doc...")
    print("SESSION {}, USER {}".format(SESSION, USER))
    # Initialize Session if there's a User and no Session
    if not SESSION:
        init_session()
    # Load Spanish and Guarani if they're not loaded.
#    if not SPA:
#        load_languages()
    return render_template('doc.html')

# View for displaying parsed sentence and sentence translation and
# for recording translations selected/entered by user.
@app.route('/sent', methods=['GET', 'POST'])
def sent():
    global SEGS
    global SEG_HTML
    global SENTENCE
    global DOC
#    print("In sent...")
    form = request.form
    print("Form for sent: {}".format(form))
    if 'reg' in form:
        # Register feedback from user to current segment
        print("Registering {}".format(form))
        if SESSION:
            SESSION.record(SENTENCE.record, form)
        return render_template('sent.html', sentence=SEG_HTML)
    if 'text' in form and not DOC:
        # Create a new document
        make_doc(form['text'])
        print("Created document {}".format(DOC))
    # Get the next sentence in the document, assigning SENTENCE
    get_sentence()
    print("Current sentence {}".format(SENTENCE))
    if not SENTENCE:
        # No more sentences, return to doc.html for a new document
        return render_template('doc.html')
    else:
        # Translate and segment the sentence, assigning SEGS
        get_segmentation()
#        segs = seg_trans(SENTENCE, SPA, GRN)
#    print("Found segs {}".format(segs))
    # Show segmented sentence
    return render_template('sent.html', sentence=SEG_HTML)

@app.route('/fin', methods=['POST'])
def fin():
#    print("In fin...")
    if SESSION:
        SESSION.write()
        quit(SESSION)
    return render_template('fin.html')

# Not needed because this is in runserver.py.
if __name__ == "__main__":
    kuaa.app.run(host='0.0.0.0')


