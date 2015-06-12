"""Ñe'ẽasa: Create simple bilingual lexicons and grammars for language pairs."""

__all__ = ['language', 'entry', 'ui', 'constraint', 'variable', 'sentence', 'cs', 'learn', 'utils']

from flask import Flask, url_for, render_template

from .sentence import *
from .learn import *
from .morphology import *

## Instantiate the Flask class to get the application
app = Flask(__name__)
app.config.from_object(__name__)

import kuaa.views

def quit():
    """Quit the program, cleaning up in various ways."""
    for language in Language.languages:
        language.quit()
    
