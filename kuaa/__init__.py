# Mainumby. Parsing and translation with minimal dependency grammars.
#
########################################################################
#
#   This file is part of the Mainumby project within the PLoGS metaproject
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

__all__ = ['language', 'entry', 'ui', 'constraint', 'db', 'views', 'variable', 'sentence', 'cs', 'utils', 'record', 'train', 'tag', 'gui']
#  not needed for now: 'learn'

from flask import Flask, url_for, render_template

## train imports sentence
from .train import *

## sentence imports ui, segment, record
### segment imports cs, utils, entry.Entry, entry.Group, record.SegRecord
### ui imports language (ui not needed for current version)
#### language imports entry, some functions from utils, morphology.morpho, morphology.semiring
#### language also calls function in morphology.strip
##### entry imports morphology.fs

#from .sentence import *
#from .learn import *

## morphology a package; imports morphology.morpho
### which imports morphology.fst
#### which imports morphology.semiring
##### which imports morphology.fs, morphology.utils
###### fs imports morphology.logic, morphology.internals
from .morphology import *
from .record import *

# from . import db

## Instantiate the Flask class to get the application
app = Flask(__name__)
app.config.from_object(__name__)

## Whether to create a session for the anonymous user when user doesn't log in.
# USE_ANON = True

### Funciones que se llaman en views.py al realizar la interfaz.

def start(gui, use_anon=True, create_memory=False):
    """Iniciar una ejecución. Crear una sesión si hay un usuario y si no
    se está usando una Memory."""

#    print("Starting {}, {}, {}".format(source, target, user))
    # Read in current users so that we can find the current user and
    # check for username overlap if a new account is created
    User.read_all()
    if isinstance(gui.user, str):
        # Get the user from their username
        gui.user = User.users.get(user)
    if use_anon and not gui.user:
        gui.user = User.get_anon()
    username = ''
    if gui.user:
        username = gui.user.username
    if create_memory:
        gui.session = kuaa.Memory.recreate(user=username)
    elif user:
        gui.session = kuaa.Session(source=gui.source, target=gui.target, user=user)

def load(source='spa', target='grn', gui=None):
    """Cargar lenguas fuente y meta para traducción."""
    s, t = kuaa.Language.load_trans(source, target)
    if gui:
        gui.source = s
        gui.target = t

def seg_trans(gui, session=None, process=True, verbosity=0):
    """Traducir oración (accesible en gui) y devuelve la oración marcada (HTML) con
    segmentos coloreados."""
    return oración(sentence=gui.sentence, src=gui.source, targ=gui.target, session=gui.session,
                   html=True, verbosity=verbosity)

## Creación y traducción de oración simple fuera de la interfaz web.

def oración(text='', src=None, targ=None, user=None, session=None, sentence=None,
            max_sols=2, translate=True, connect=True, generate=True, html=False,
            verbosity=0):
    """Analizar y talvez también traducir una oración del castellano al guaraní."""
    if not src and not targ:
        src, targ = Language.load_trans('spa', 'grn', train=False)
    if not session:
        session = make_session(src, targ, user, create_memory=True)
    s = Sentence.solve_sentence(src, targ, text=text, session=session, sentence=sentence,
                                max_sols=max_sols, translate=translate, verbosity=verbosity)
    segmentations = s.get_all_segmentations(translate=translate, generate=generate,
                                            connect=connect, html=html)
    if html:
        if segmentations:
            segmentation = segmentations[0]
            return segmentation.segments, segmentation.get_gui_segments()
        return [], s.get_html()
    elif segmentations:
        return segmentations
    return s

def make_document(gui, text, single=False, html=False):
    """Create a Mainumby Document object with the text."""
    session = gui.session
    d = kuaa.Document(gui.source, gui.target, text, proc=True, session=session, single=single)
    if html:
        d.set_html()
    gui.doc = d
    gui.init_doc()
#    return d

def quit(session=None):
    """Quit the session (and the program), cleaning up in various ways."""
    for language in Language.languages.values():
        # Store new cached analyses or generated forms for
        # each active language, but only if there is a current session/user.
        language.quit(cache=session)
    if session:
        session.quit()

## Probably only need to read in usernames.
def init_users(gui=None):
    # Read in current users before login.
    User.read_all()
    if gui:
        gui.users_initialized = True

def make_session(source, target, user, create_memory=False, use_anon=True):
    User.read_all()
    if isinstance(user, str):
        # Get the user from their username
        user = User.users.get(user)
    if use_anon and not user:
        user = User.get_anon()
    username = ''
    if user:
        username = user.username
    if create_memory:
        session = kuaa.Memory.recreate(user=username)
    elif user:
        session = kuaa.Session(source=source, target=target, user=user)
    return session

def get_user(username):
    """Find the user with username username."""
    print("Looking for user with username {}".format(username))
    return User.get_user(username)

def create_user(dct):
    """Create a user from the dict of form values from login.html."""
    return User.dict2user(dct)

#def clean_sentence(string, capitalize=True):
#    """Clean up sentence for display in interface.
#    Basically a duplicate of the Javascript function in tra.html and sent.html."""
#    string = string.replace("&nbsp;", ' ')
#    string = re.sub(r"\s+([.,;?!])", r"\1", string)
#    if capitalize:
#        string = string[0].upper() + string[1:]
#    return string

# Import views. This has to appear after the app is created.
import kuaa.views

