"""Ñe'ẽasa: Create simple bilingual lexicons and grammars for language pairs."""

__all__ = ['language', 'entry', 'ui', 'constraint', 'variable', 'sentence', 'cs', 'learn', 'utils']

from .sentence import *
from .learn import *
from .morphology import *

def quit():
    """Quit the program, cleaning up in various ways."""
    for language in Language.languages:
        language.quit()
    
