"""Ñe'ẽasa: Create simple bilingual lexicons and grammars for language pairs."""

__all__ = ['language', 'entry', 'ui', 'constraint', 'variable', 'sentence', 'cs', 'learn', 'utils']

from flask import Flask, url_for, render_template

from .sentence import *
from .learn import *
from .morphology import *

## Instantiate the Flask class to get the application
app = Flask(__name__)
app.config.from_object(__name__)

def load(source='spa', target='grn'):
    """Load source and target languages for translation."""
    return kuaa.Language.load_trans(source, target)

def translate(sentence, source, target, all_sols=True):
    """Translate sentence from source to target language."""

def quit():
    """Quit the program, cleaning up in various ways."""
    for language in Language.languages.values():
        # Store new cached analyses or generated forms for
        # each active language.
        language.quit()
    
import kuaa.views

