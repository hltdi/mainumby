# Mainumby. Parsing and translation with minimal dependency grammars.
#
########################################################################
#
#   This file is part of the Mainumby project within the PLoGS metaproject
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

__all__ = ['language', 'entry', 'ui', 'constraint', 'db', 'views', 'variable', 'sentence', 'cs', 'utils', 'record', 'train', 'tag']
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

def load(source='spa', target='grn'):
    """Load source and target languages for translation."""
    return kuaa.Language.load_trans(source, target)

def seg_trans(sentence, source, target, session=None, single=False,
              constrain_groups=None, join=True, verbosity=0):
    """Translate sentence and return marked-up sentence with segments colored.
    So far only uses first segmentation."""
    sentence.initialize(ambig=True, constrain_groups=constrain_groups, verbosity=verbosity)
    sentence.solve(translate=True, all_sols=False, all_trans=True, interactive=False,
                   verbosity=verbosity)
    if sentence.segmentations:
        segmentation = sentence.segmentations[0]
        segmentation.get_segs(single=single, html=False)
        if join:
            segmentation.join(generate=False)
        segmentation.generate()
        segmentation.seg_html(single=single)
        segmentation.get_gui_segments(single=single)
        return segmentation.segments, segmentation.get_gui_segments(single=single)
    else:
        return [], sentence.get_html(single=single)

def make_document(source, target, text, session=None, single=False):
    """Create a Mainumby Document object with the text."""
    if single:
        print("Making sentence from {}".format(source))
    d = kuaa.Document(source, target, text, proc=True, session=session, single=single)
    return d

def quit(session=None):
    """Quit the session (and the program), cleaning up in various ways."""
    for language in Language.languages.values():
        # Store new cached analyses or generated forms for
        # each active language, but only if there is a current session/user.
        language.quit(cache=session)
    if session:
        session.quit()

## Probably only need to read in usernames.
def init_users():
    # Read in current users before login.
    User.read_all()

def start(source, target, user, use_anon=True, create_memory=False):
    """Initialize a run. Create a Session if there's a user, and we're not
    using a Memory."""
#    print("Starting {}, {}, {}".format(source, target, user))
    # Read in current users so that we can find the current user and
    # check for username overlap if a new account is created
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
        return kuaa.Memory.recreate(user=username)
    elif user:
        return kuaa.Session(source=source, target=target, user=user)
#    else:
#        return kuaa.Memory.recreate()

def get_user(username):
    """Find the user with username username."""
    print("Looking for user with username {}".format(username))
    return User.get_user(username)

def create_user(dct):
    """Create a user from the dict of form values from login.html."""
    return User.dict2user(dct)

def clean_sentence(string, capitalize=True):
    """Clean up sentence for display in interface.
    Basically a duplicate of the Javascript function in tra.html and sent.html."""
    string = string.replace("&nbsp;", ' ')
    string = re.sub(r"\s+([.,;?!])", r"\1", string)
    if capitalize:
        string = string[0].upper() + string[1:]
    return string

# Import views. This has to appear after the app is created.
import kuaa.views

