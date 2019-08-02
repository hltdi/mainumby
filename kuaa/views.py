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
from docx import Document

# Global variable and basic functions for the container holding all the gui-related variables that need to
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
    # Load users and create session if there's a user
    # or if USE_ANON is True
    if not GUI.session:
        start(GUI, use_anon=use_anon, create_memory=create_memory)

# Attempt to translate the currently selected sentence,
# assigning segmentation and HTML for the translation segmentation visualization
# in GUI
def solve_and_segment(isdoc=False, index=0):
    GUI.segs, GUI.tra_seg_html = seg_trans(GUI, process=True)
#    print("Solved segs: {}, html: {}".format(SEGS, SEG_HTML))
    GUI.init_sent(index)
    if isdoc:
        GUI.update_doc(index)

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

# View for the window that does all the work. Whew.
@app.route('/tra', methods=['GET', 'POST'])
def tra():
    global GUI
    if not GUI:
        create_gui()
    form = request.form
    print("**FORM DICT FOR tra.html: {}**".format(form))
    if not GUI.session:
        print("Ninguna memoria")
        init_session(create_memory=True)
    # Translating document?
    isdoc = form.get('isdoc') == 'true'
    GUI.set_props(form, ['ocultar', 'nocorr', 'isdoc'], ['tfuente'])
#    if 'ocultar' in form:
#        GUI.props['ocultar'] = form.get('ocultar') == 'true'
#    if 'nocorr' in form:
#        GUI.props['nocorr'] = form.get('nocorr') == 'true'
    username = GUI.user.username if GUI.user else ''
    if 'ayuda' in form and form['ayuda'] == 'true':
        # Opened help window. Keep everything else as is.
        return render_template('tra.html', doc=isdoc, documento=GUI.doc_html, props=GUI.props)
    if 'modo' in form:
        if 'docx' in form and form['docx']:
            file = form['docx']
            print("ARCHIVO SUBIDO {}".format(file))
            document = Document(file)
#            GUI.props['tfuente'] = "90%"
            return render_template('tra.html', doc=True, props=GUI.props)
        # Mode (sentence vs. document) has changed
        isdoc = form.get('modo') == 'documento'
        if 'documento' in form and form['documento']:
            make_document(GUI, form['documento'], single=False, html=True)
            print("PROCESANDO TEXTO {}".format(GUI.doc))
            return render_template('tra.html', documento=GUI.doc.html, doc=True, props=GUI.props)
        else:
            GUI.clear(isdoc=isdoc)
            return render_template('tra.html', doc=isdoc, props=GUI.props)
    if form.get('borrar') == 'true':
        print("BORRANDO")
        GUI.clear(form.get('registrar') == 'true', form.get('ometa'))
        # Start over with no current sentence or translation (translating sentence)
        GUI.props['tfuente'] = "120%"
        return render_template('tra.html', oracion=None, tra_seg_html=None,
                               user=username, props=GUI.props)
    GUI.props['isdoc'] = isdoc
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
#            GUI.props['tfuente'] = "120%"
            return render_template('tra.html', error=True, user=username, doc=isdoc, props=GUI.props)
    oindex = int(form.get('oindex', 0))
    docscrolltop = form.get('docscrolltop', 0)
    if 'tacept' in form and form['tacept']:
        # A new translation to be added to the accepted sentence translations.
        print("ACCEPTING NEW TRANSLATION {}".format(form['tacept']))
        GUI.accept_sent(oindex, form['tacept'])
        aceptado = GUI.doc_tra_acep_str
        return render_template('tra.html', oracion='', doc=True, tra_seg_html='', tra='', oindex=-1,
                               documento=GUI.doc_html, aceptado=aceptado,
                               user=username, props=GUI.props)
    if GUI.doc_tra_acep[oindex]:
        print("SENTENCE ALREADY ACCEPTED")
        error = "¡Ya aceptaste esta traducción; por favor seleccioná otra oración para traducir!"
        return render_template('tra.html', oracion='', doc=True, error=error, tra_seg_html='', tra='',
                               aceptado=GUI.doc_tra_acep_str, docscrolltop=docscrolltop,
                               documento=GUI.doc_html, user=username, props=GUI.props)
    if GUI.doc_tra_html[oindex]:
        # Find the previously generated translation
        tra_seg_html = GUI.doc_tra_html[oindex]
        tra = GUI.doc_tra[oindex]
        # Highlight selected source sentence with segments
        GUI.update_doc(oindex, repeat=True)
        print("SENTENCE at {} ALREADY TRANSLATED".format(oindex))
        return render_template('tra.html', oracion=GUI.fue_seg_html, tra_seg_html=tra_seg_html, tra=tra,
                               documento=GUI.doc_html, doc=True, oindex=oindex, docscrolltop=docscrolltop,
                               aceptado=GUI.doc_tra_acep_str, user=username, props=GUI.props)
    
    # Get the sentence, the only one in GUI.doc if isdoc is False.
    GUI.sentence = GUI.doc[oindex]
    print("CURRENT SENTENCE {}".format(GUI.sentence))
    # Translate and segment the sentence, assigning GUI.segs
    solve_and_segment(isdoc=isdoc, index=oindex)
    # Pass the sentence segmentation, the raw sentence, and the final punctuation to the page
#    print("== About to render template with doc={}, documento={}, aceptado={}".format(isdoc, GUI.doc_html, GUI.doc_tra_acep_str))
    return render_template('tra.html', oracion=GUI.fue_seg_html, tra_seg_html=GUI.tra_seg_html, tra=GUI.tra,
                           documento=GUI.doc_html, doc=isdoc, oindex=oindex,
                           aceptado=GUI.doc_tra_acep_str, docscrolltop=docscrolltop,
                           user=username, props=GUI.props)

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
