# Mainumby. Parsing and translation with minimal dependency grammars.
#
########################################################################
#
#   This file is part of the HLTDI L^3 project
#   for parsing, generation, translation, and computer-assisted
#   human translation.
#
#   Copyleft 2015, 2016, 2017, 2018 HLTDI, PLoGS <gasser@indiana.edu>
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
# 2016.04.05
# -- Login works.
# 2016.04.10
# -- Segment translation selections are added to sentence translation TextArea in sent.html.
#    Sentence translations are added to document TextArea in sent.html.
# 2017.11
# -- Document TextArea gets cleared when "Salir" happens.
# 2018.01-03
# -- Comments in sent, error message for empty Doc in doc.
# 2018.07-08
# -- New GT-like interface: tra.html; OF_HTML, OF1

from flask import request, session, g, redirect, url_for, abort, render_template, flash
from kuaa import app, make_document, load, seg_trans, quit, start, init_users, get_user, create_user, clean_sentence

# Global variables for views; probably a better way to do this...
SESSION = SPA = GRN = DOC = SENTENCE = SEGS = SEG_HTML = USER = OF_HTML = OF1 = None
SINDEX = 0
USERS_INITIALIZED = False

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
    # or if USE_ANON is True
    if not SESSION:
        SESSION = start(SPA, GRN, USER)

def load_languages():
    """Load Spanish and Guarani data."""
    global GRN, SPA
    SPA, GRN = load()

def make_doc(text, single=False):
    """Create a Document object from the text."""
    global DOC
    DOC = make_document(SPA, GRN, text, session=SESSION, single=single)

def get_sentence():
    global SINDEX
    global SENTENCE
    global DOC
#    print("SINDEX {}, len(DOC) {}".format(SINDEX, len(DOC)))
    if SINDEX >= len(DOC):
        SENTENCE = None
        # Save DOC in database or translation cache here
        DOC = None
        SINDEX = 0
        return
    SENTENCE = DOC[SINDEX]
    SINDEX += 1

def solve_and_segment(single=False):
    global SEGS
    global SEG_HTML
    SEGS, SEG_HTML = seg_trans(SENTENCE, SPA, GRN, single=single)
    print("Solved segs: {}".format(SEGS))
    if single:
        global OF_HTML
        global OF1
        cap = SENTENCE.capitalized
        print("Sentence capitalized? {}".format(cap))
        OF_HTML = ''.join([s[-1] for s in SEG_HTML])
        OF1 = clean_sentence(' '.join([s[4] for s in SEG_HTML]), cap)
        print("OF1 {}".format(OF1))
        print("OF HTML {}".format(OF_HTML))

@app.route('/')
def index():
#    print("In index...")
    return redirect(url_for('base'))

@app.route('/base', methods=['GET', 'POST'])
def base():
#    print("In base...")
    return render_template('base.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    global USER
    form = request.form
#    print("Form for login: {}".format(form))
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
#                print("Password doesn't match")
                return render_template('login.html', error='password')
    return render_template('login.html')

@app.route('/logged', methods=['GET', 'POST'])
def logged():
    form = request.form
#    print("Form for logged: {}".format(form))
    return render_template('logged.html')

@app.route('/reg', methods=['GET', 'POST'])
def reg():
    global USER
    form = request.form
#    print("Form for reg: {}".format(form))
    if request.method == 'POST' and 'username' in form:
        if form.get('cancel') == 'Cancelar':
            return render_template('login.html')
        elif not form.get('username'):
            return render_template('reg.html', error="username")
        elif not form.get('email'):
            return render_template('reg.html', error="email")
        elif form.get('password') != form.get('password2'):
            return render_template('reg.html', error="password")
        else:
            user = create_user(form)
            print("Created user {}".format(user))
            USER = user
            return render_template('acct.html', username=form.get('username'))
    return render_template('reg.html')

@app.route('/acct', methods=['POST'])
def acct():
#    print("In acct...")
    return render_template('acct.html')

# View for quicker version of program that displays sentence and its translation in
# side-by-side windows.
@app.route('/tra', methods=['GET', 'POST'])
def tra():
    global SENTENCE
    global DOC
    global SEG_HTML
    global OF1
    form = request.form
    of = None
    print("Form for tra: {}".format(form))
    if not SPA:
        load_languages()
#   AYUDA
#    if 'ayuda' in form and form['ayuda'] == 'true':
#        # Opened help window. Keep everything else as is.
#        raw = SENTENCE.raw if SENTENCE else None
#        document = form.get('UTraDoc', '')
#        return render_template('sent.html', sentence=SEG_HTML, raw=raw, punc=punc,
#                               document=document, user=USER)
    if form.get('borrar') == 'true':
        DOC = SENTENCE = SEG_HTML = None
        return render_template('tra.html', sentence=None, ofuente=None, translation=None, raw=None, punc=None,
                               mayus='')
    if not 'ofuente' in form:
        return render_template('tra.html', mayus='')
    if not DOC:
        # Create a new document
        of = form['ofuente']
        print("Creando nueva oración de {}".format(of))
        make_doc(of, single=True)
#        print("Created document {}".format(DOC))
        if len(DOC) == 0:
            print(" But document is empty.")
            return render_template('tra.html', error=True)
    # Get the sentence, the only one in DOC
    SENTENCE = DOC[0]
    print("Actual oración {}".format(SENTENCE))
    # Translate and segment the sentence, assigning SEGS
    solve_and_segment(single=True)
    print("Solved and segmented")
    print("SEG HTML")
    for s in SEG_HTML:
        print("  {}".format(s))
    # Pass the sentence segmentation, the raw sentence, and the final punctuation to the page
    punc = SENTENCE.get_final_punc()
    return render_template('tra.html', sentence=OF_HTML, ofuente=of, translation=SEG_HTML, trans1=OF1,
                           raw=SENTENCE.original, punc=punc, mayus=SENTENCE.capitalized)

# View for document entry
@app.route('/doc', methods=['GET', 'POST'])
def doc():
    form = request.form
#    print("Form for doc: {}".format(form))
    # Initialize Session if there's a User and no Session
    # and Spanish and Guarani if they're not loaded.
    if not SESSION:
#        print("Ninguna sesión")
#        if not USER:
#            print("Y ningún usuario")
        init_session()
#    print("Initialized session and languages")
    return render_template('doc.html', user=USER)

# View for displaying parsed sentence and sentence translation and
# for recording translations selected/entered by user.
@app.route('/sent', methods=['GET', 'POST'])
def sent():
    form = request.form
    punc = SENTENCE.get_final_punc() if SENTENCE else None
    print("Form for sent: {}".format(form))
    if 'ayuda' in form and form['ayuda'] == 'true':
        # Opened help window. Keep everything else as is.
        raw = SENTENCE.raw if SENTENCE else None
        document = form.get('UTraDoc', '')
        return render_template('sent.html', sentence=SEG_HTML, raw=raw, punc=punc,
                               document=document, user=USER)
    if 'senttrans' in form:
        # A sentence has been translated and the translation recorded.
        # Really record the translation and the segment translations if any.
        translation = form.get('senttrans')
        segtrans = form.get('segtrans', '')
        document = form.get('UTraDoc', '')
        comments = form.get('UComment', '')
        if SESSION:
            SESSION.record(SENTENCE.record, translation=translation, segtrans=segtrans, comments=comments)
        else:
            print("NO SESSION SO NOTHING TO RECORD")
        # Continue with the next sentence in the document or quit
        return render_template('sent.html', user=USER, document=document)
    if 'text' in form and not DOC:
        # Create a new document
        make_doc(form['text'])
        if len(DOC) == 0:
            return render_template('doc.html', user=USER, error=True)
    # Get the next sentence in the document, assigning SENTENCE
    get_sentence()
    if not SENTENCE:
        # No more sentences, return to doc.html for a new document
        return render_template('doc.html', user=USER)
    else:
        # Translate and segment the sentence, assigning SEGS
        solve_and_segment()
    # Pass the sentence segmentation, the raw sentence, and the final punctuation to the page
    punc = SENTENCE.get_final_punc()
    return render_template('sent.html', sentence=SEG_HTML, raw=SENTENCE.original, document='',
                           record=SENTENCE.record, punc=punc, user=USER)

@app.route('/fin', methods=['GET', 'POST'])
def fin():
    form = request.form
    print("Form for fin: {}".format(form))
    modo = form.get('modo')
    global SESSION
    global DOC
    global SENTENCE
    global SEGS
    global SEG_HTML
    global USER
    global SINDEX
    quit(SESSION)
    SESSION = DOC = SENTENCE = SEGS = SEG_HTML = USER = None
    SINDEX = 0
    return render_template('fin.html', modo=modo)

@app.route('/proyecto')
def proyecto():
    return render_template('proyecto.html')

@app.route('/uso')
def uso():
    return render_template('uso.html')

@app.route('/contacto')
def contacto():
    return render_template('contacto.html')

# Not needed because this is in runserver.py.
if __name__ == "__main__":
    kuaa.app.run(host='0.0.0.0')
