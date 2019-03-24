# Mainumby. Parsing and translation with minimal dependency grammars.
#
########################################################################
#
#   This file is part of the PLoGS project
#   for parsing, generation, translation, and computer-assisted
#   human translation.
#
#   Copyleft 2015, 2016, 2017, 2018, 2019 HLTDI, PLoGS <gasser@indiana.edu>
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
# -- New GT-like interface: tra.html; OF_HTML, OM1
# 2019.03
# -- GUI class holds variables that used to be global. The one
#    global is the instance of GUI.

from flask import request, session, g, redirect, url_for, abort, render_template, flash
from kuaa import app, make_document, load, seg_trans, quit, start, init_users, get_user, create_user, GUI

# Global variables for views; probably a better way to do this...
# SINDEX = 0

#def initialize():
#    global USERS_INITIALIZED
#    init_users()
#    USERS_INITIALIZED = True

def init_session(create_memory=False, use_anon=False):
    if not GUI.source:
        load(gui=GUI)
#        load_languages()
    # Load users and create session if there's a user
    # or if USE_ANON is True
    if not GUI.session:
        start(GUI, use_anon=use_anon, create_memory=create_memory)

#def load_languages():
#    """Load Spanish and Guarani data."""
#    GUI.source, GUI.target = load()

#def make_doc(text, single=False, html=False):
#    """Create a Document object from the text."""
#    GUI.doc = make_document(GUI, text, session=GUI.session,
#                            single=single, html=html)

##def get_sentence():
##    global SINDEX
##    if SINDEX >= len(GUI.doc):
##        GUI.sentence = None
##        # Save GUI.doc in database or translation cache here
##        GUI.doc = None
##        SINDEX = 0
##        return
##    GUI.sentence = GUI.doc[SINDEX]
##    SINDEX += 1

def solve_and_segment(single=False):
    GUI.segs, GUI.seg_html = seg_trans(GUI, single=single, process=True)
#    print("Solved segs: {}, html: {}".format(SEGS, SEG_HTML))
    if single:
        GUI.init_sent()
#        cap = GUI.sentence.capitalized
#        GUI.of_html = ''.join([s[-1] for s in GUI.seg_html])
#        GUI.om1 = clean_sentence(' '.join([s[4] for s in GUI.seg_html]), cap)

def doc_solve_and_segment(index):
    # Solve the current sentence
    solve_and_segment(True)
    # Update the document translation
    GUI.update_doc(index)
#    GUI.doc_html = GUI.doc.select_html(index, GUI.of_html)
#    # List of translation HTML for sentences
#    GUI.doc_om = [""] * len(GUI.doc)
#    # List of accepted translation strings for sentences
#    GUI.doc_t = [""] * len(GUI.doc)

@app.route('/', methods=['GET', 'POST'])
def index():
    print("In index...")
    return render_template('index.html')

@app.route('/acerca', methods=['GET', 'POST'])
def acerca():
    print("In acerca...")
    return render_template('acerca.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = request.form
#    print("Form for login: {}".format(form))
    if not GUI.users_initialized:
        init_users(GUI)
#        initialize()
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
                GUI.user = user
                return render_template('logged.html', user=username)
            else:
                return render_template('login.html', error='password')
    return render_template('login.html')

@app.route('/logged', methods=['GET', 'POST'])
def logged():
    form = request.form
#    print("Form for logged: {}".format(form))
    return render_template('logged.html')

@app.route('/reg', methods=['GET', 'POST'])
def reg():
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
            GUI.user = user
            return render_template('acct.html', user=form.get('username'))
    return render_template('reg.html')

@app.route('/acct', methods=['POST'])
def acct():
#    print("In acct...")
    return render_template('acct.html')

# View for the window that does all the work.
@app.route('/tra', methods=['GET', 'POST'])
def tra():
    form = request.form
    of = None
    print("Form for tra: {}".format(form))
    if not GUI.session:
        print("Ninguna memoria")
        init_session(create_memory=True)
    username = GUI.user.username if GUI.user else ''
#    if 'ayuda' in form and form['ayuda'] == 'true':
#        # Opened help window. Keep everything else as is.
#        return render_template(...)
    if 'modo' in form:
        subir = form.get('modo') == 'documento'
        if 'documento' in form and form['documento']:
            # Text for new Document object
            text = form['documento']
            make_document(GUI, text, single=False, html=True)
            doc_html = GUI.doc.html
            print("Procesando texto {}".format(GUI.doc))
            return render_template('tra.html', documento=doc_html, doc=True, tfuente="90%")
        else:
            return render_template('tra.html', doc=subir)
    if form.get('borrar') == 'true':
        sentrec = None
        if GUI.sentence:
            sentrec = GUI.sentence.record
        GUI.seg_html = None
        GUI.sentence = None
        GUI.doc = None
        if form.get('registrar') == 'true':
            if GUI.session:
                recordsrc = sentrec.raw
                translation = form.get('ometa')
                GUI.session.record(sentrec, translation=translation)
            else:
                print("NO SESSION SO NOTHING TO RECORD")
        return render_template('tra.html', oracion=None, ofuente=None, translation=None, punc=None,
                               user=username, mayus='', tfuente="120%")
    isdoc = form.get('isdoc') == 'true'

    if not isdoc and GUI.of_html and GUI.sentence:
        # Sentence already translated; don't read in a new one until this one gets deleted.
        return render_template('tra.html', oracion=GUI.of_html, ofuente=form.get('ofuente', ''), translation=GUI.seg_html, trans1=GUI.om1,
                                punc=GUI.sentence.get_final_punc(), mayus=GUI.sentence.capitalized, tfuente=form.get('tfuente', "120%"),
                                user=username, nocorr=form.get('nocorr', ''))
    if not 'ofuente' in form:
        return render_template('tra.html', user=username, mayus='')
    if not GUI.doc:
        # Create a new document
        of = form['ofuente']
        print("Creando nueva oración de {}".format(of))
        make_document(GUI, of, single=True, html=False)
        if len(GUI.doc) == 0:
            print(" But document is empty.")
            return render_template('tra.html', error=True, tfuente="120%", user=username)
    print("GOT TO HERE WITH isdoc={}, ofuente={}".format(isdoc, of))
    oindex = int(form.get('oindex', 0))
    # Get the sentence, the only one in GUI.doc
    GUI.sentence = GUI.doc[oindex]
    # Translate and segment the sentence, assigning GUI.segs
    if isdoc:
        doc_solve_and_segment(oindex)
    else:
        solve_and_segment(single=True)
    tf = form.get('tfuente', "120%")
    # Whether to do orthographic correction of target
    nocorr = form.get('nocorr', '')
    # Pass the sentence segmentation, the raw sentence, and the final punctuation to the page
    punc = GUI.sentence.get_final_punc()
    return render_template('tra.html', oracion=GUI.of_html, ofuente=of, translation=GUI.seg_html, trans1=GUI.om1, isdoc=isdoc,
                           documento=GUI.doc_html, punc=punc, mayus=GUI.sentence.capitalized, tfuente=tf,
                           user=username, nocorr=nocorr)

# View for document entry
##@app.route('/doc', methods=['GET', 'POST'])
##def doc():
##    form = request.form
##    # Initialize Session if there's a User and no Session
##    # and Spanish and Guarani if they're not loaded.
##    if not GUI.session:
##        init_session()
##    return render_template('doc.html', user=GUI.user)

# View for displaying parsed sentence and sentence translation and
# for recording translations selected/entered by user.
##@app.route('/sent', methods=['GET', 'POST'])
##def sent():
##    form = request.form
##    punc = GUI.sentence.get_final_punc() if GUI.sentence else None
##    print("Form for sent: {}".format(form))
##    if 'ayuda' in form and form['ayuda'] == 'true':
##        # Opened help window. Keep everything else as is.
##        raw = GUI.sentence.raw if GUI.sentence else None
##        document = form.get('UTraDoc', '')
##        return render_template('sent.html', sentence=GUI.seg_html, raw=raw, punc=punc,
##                               document=document, user=GUI.user)
##    if 'senttrans' in form:
##        # A sentence has been translated and the translation recorded.
##        # Really record the translation and the segment translations if any.
##        translation = form.get('senttrans')
##        segtrans = form.get('segtrans', '')
##        document = form.get('UTraDoc', '')
##        comments = form.get('UComment', '')
##        if GUI.session:
##            GUI.session.record(GUI.sentence.record, translation=translation, segtrans=segtrans, comments=comments)
##        else:
##            print("NO SESSION SO NOTHING TO RECORD")
##        # Continue with the next sentence in the document or quit
##        return render_template('sent.html', user=GUI.user, document=document)
##    if 'text' in form and not GUI.doc:
##        # Create a new document
##        make_doc(form['text'])
##        if len(GUI.doc) == 0:
##            return render_template('doc.html', user=GUI.user, error=True)
##    # Get the next sentence in the document, assigning GUI.sentence
##    get_sentence()
##    if not GUI.sentence:
##        # No more sentences, return to doc.html for a new document
##        return render_template('doc.html', user=GUI.user)
##    else:
##        # Translate and segment the sentence, assigning GUI.segs
##        solve_and_segment()
##        print("SEG HTML {}".format(GUI.seg_html))
##    # Pass the sentence segmentation, the raw sentence, and the final punctuation to the page
##    punc = GUI.sentence.get_final_punc()
##    return render_template('sent.html', sentence=GUI.seg_html, raw=GUI.sentence.original, document='',
##                           record=GUI.sentence.record, punc=punc, user=GUI.user)

@app.route('/fin', methods=['GET', 'POST'])
def fin():
    form = request.form
#    print("Form for fin: {}".format(form))
    modo = form.get('modo')
    global SINDEX
    quit(GUI.session)
    GUI.session = GUI.doc = GUI.sentence = None
    GUI.segs = GUI.seg_html = None
    SINDEX = 0
    GUI.user = None
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
