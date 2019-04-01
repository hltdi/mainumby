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
from kuaa import app, make_document, load, seg_trans, quit, start, init_users, get_user, create_user
from . import gui

# Global variable for the container holding all the gui-related variables that need to
# persist between calls to render_template()
GUI = None

def create_gui():
    global GUI
    GUI = gui.GUI()

def end_gui():
    global GUI
    if GUI:
        quit(GUI.session)
        GUI = None

def init_session(create_memory=False, use_anon=False):
    if not GUI.source:
        load(gui=GUI)
#        load_languages()
    # Load users and create session if there's a user
    # or if USE_ANON is True
    if not GUI.session:
        start(GUI, use_anon=use_anon, create_memory=create_memory)

def solve_and_segment(isdoc=False, index=0):
    GUI.segs, GUI.seg_html = seg_trans(GUI, single=True, process=True)
#    print("Solved segs: {}, html: {}".format(SEGS, SEG_HTML))
    GUI.init_sent()
    if isdoc:
        GUI.update_doc(index)

#def doc_solve_and_segment(index):
#    # Solve the current sentence
#    solve_and_segment(True)
#    # Update the document translation
#    GUI.update_doc(index)

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
    if not GUI:
        create_gui()
    form = request.form
#    print("Form for login: {}".format(form))
    if not GUI.users_initialized:
        init_users(GUI)
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
    if not GUI:
        create_gui()
    form = request.form
    print("**FORM DICT FOR tra.html: {}**".format(form))
    if not GUI.session:
        print("Ninguna memoria")
        init_session(create_memory=True)
    if 'ocultar' in form:
        GUI.props['ocultar'] = form.get('ocultar') == 'true'
    if 'nocorr' in form:
        GUI.props['nocorr'] = form.get('nocorr') == 'true'
    username = GUI.user.username if GUI.user else ''
#    if 'ayuda' in form and form['ayuda'] == 'true':
#        # Opened help window. Keep everything else as is.
#        return render_template(...)
    if 'modo' in form:
        # Mode (sentence vs. document) has changed
        subir = form.get('modo') == 'documento'
        if 'documento' in form and form['documento']:
            make_document(GUI, form['documento'], single=False, html=True)
            print("Procesando texto {}".format(GUI.doc))
            return render_template('tra.html', documento=GUI.doc.html, doc=True,
                                   tfuente="90%", props=GUI.props)
        else:
            return render_template('tra.html', doc=subir, props=GUI.props)
    if form.get('borrar') == 'true':
        GUI.clear(form.get('registrar') == 'true', form.get('ometa'))
        # Start over with no current sentence or translation (translating sentence)
        return render_template('tra.html', oracion=None, translation=None,
                               user=username, tfuente="120%", props=GUI.props)
    # Translating document?
    isdoc = form.get('isdoc') == 'true'
    GUI.props['isdoc'] = isdoc

    if 'oindex' not in form and GUI.of_html and GUI.sentence:
        print("SENTENCE ALREADY TRANSLATED")
        # (translating sentence) Sentence already translated; don't read in a new one until this one gets deleted.
        return render_template('tra.html', oracion=GUI.of_html, doc=isdoc,
                               translation=GUI.seg_html, trans1=GUI.om1,
                               tfuente=form.get('tfuente', "120%"),
                               user=username, props=GUI.props)
    if not 'ofuente' in form:
        # No sentence entered or selected
        print("NO SENTENCE ENTERED")
        return render_template('tra.html', user=username, props=GUI.props, doc=isdoc)
    if not GUI.doc:
        # Create a new document
        print("CREANDO NUEVO DOCUMENTO.")
        make_document(GUI, form['ofuente'], single=True, html=False)
        if len(GUI.doc) == 0:
            print(" pero documento está vacío.")
            return render_template('tra.html', error=True, tfuente="120%", user=username, doc=isdoc, props=GUI.props)
    oindex = int(form.get('oindex', 0))
    print("GOT TO HERE WITH isdoc={}, ofuente={}, oindex={}".format(isdoc, form['ofuente'], oindex))
    if 'tacept' in form and form['tacept']:
        # A new translation to be added to the accepted sentence translations.
        aceptado = GUI.accept_sent(oindex, form['tacept'])
        return render_template('tra.html', oracion='', doc=True, translation='', trans1='', oindex=-1,
                               documento=GUI.doc_html, tfuente="90%", aceptado=GUI.doc_trans_str,
                               user=username, props=GUI.props)
    if GUI.doc_trans[oindex]:
        print("SENTENCE PREVIOUSLY SELECTED")
        return render_template('tra.html', oracion=GUI.of_html, doc=isdoc,
                               translation=GUI.seg_html, trans1=GUI.om1,
                               documento=GUI.doc_html, tfuente="90%",
                               user=username, props=GUI.props)
    # Get the sentence, the only one in GUI.doc is isdoc is False.
    GUI.sentence = GUI.doc[oindex]
    print("CURRENT SENTENCE {}".format(GUI.sentence))
    # Translate and segment the sentence, assigning GUI.segs
    solve_and_segment(isdoc=isdoc, index=oindex)
    # Pass the sentence segmentation, the raw sentence, and the final punctuation to the page
    return render_template('tra.html', oracion=GUI.of_html, translation=GUI.seg_html, trans1=GUI.om1,
                           documento=GUI.doc_html, tfuente=form.get('tfuente', "120%"),
                           taccept=GUI.get_accepted_t(), doc=isdoc, oindex=oindex,
                           user=username, props=GUI.props)

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
    end_gui()
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
