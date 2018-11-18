#!/usr/bin/env python3

# Mainumby: Parsing and translation with minimal dependency grammars.
#
########################################################################
#
#   This file is part of the PLoGS project
#   for parsing, generation, translation, and computer-assisted
#   human translation.
#
#   Copyleft 2014, 2015, 2016, 2017, 2018; HLTDI, PLoGS <gasser@indiana.edu>
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

# 2014.02.09
# -- Created (as Hiiktuu)
# 2015.05.20
# -- Changed to Ñe'ẽasa, after incorporating morphological analysis/generation
# 2015.06.12
# -- Started Web app
# 2015.07.04
# -- Changed name to Mbojereha
# 2015.12.07
# -- Changed name of repository and folder to Mainumby
# 2016
# -- Sessions, users
# 2017.3
# -- Bilingual documents and training
# 2018
# -- Web app
#    Joins and SuperSegs

__version__ = 2.0

import kuaa

## Atajos

## Creación (y opcionalmente traducción) de oración simple y de documento.
## Por defecto, las palabras en segmentos no se generan morfológicamente.
def ora(sentence, ambig=False, solve=True, user=None, segment=True, max_sols=1,
        single=False, translate=True, delay_gen=True, verbosity=0):
    e, g = cargar()
    session = kuaa.start(e, g, user, create_memory=single)
    d = kuaa.Document(e, g, sentence, True, single=single, session=session)
    if len(d) == 0:
        print("Parece que falta puntuación final en el documento.")
        return
    s = d[0]
    s.initialize(ambig=ambig, verbosity=verbosity)
    if solve or segment:
        s.solve(all_sols=ambig or max_sols > 1, max_sols=max_sols,
                translate=translate, delay_gen=delay_gen)
        if s.solutions:
            if translate and segment:
                for sol in s.solutions:
                    sol.get_segs(delay_gen=delay_gen)
                solution = s.solutions[0]
                for segment in solution.segments:
                    print("{}: {}".format(segment, segment.cleaned_trans))
                return solution
            return s.solutions
    return s

def ora1(sentence):
    """A sentence prior to solution, segmentation, translation."""
    return ora(sentence, solve=False, segment=False, single=True, translate=False,
               delay_gen=True)

## Aprendizaje de nuevos grupos

def aprender(source, target):
    l = kuaa.Learner(source, target)
    return l

def doc(text, proc=True, single=False):
    e, g = cargar()
    d = kuaa.Document(e, g, text, proc=proc, single=single)
    return d

def generate(language, stem, feats=None, pos='v'):
    if not feats:
        feats = kuaa.FeatStruct("[]")
    else:
        feats = kuaa.FeatStruct(feats)
    return language.generate(stem, feats, pos)

def solve1(sentence):
    """Solve; print and return solutions."""
    sentence.solve()
    output_sols(sentence)
    return sentence.solutions

def output_sols(sentence):
    """Show target outputs for all solutions for sentence."""
    for sol in sentence.solutions:
        for x in sol.get_ttrans_outputs():
            print(x)

def ley_bidoc(init=True, train=True):
    d = eg_arch_doc("../LingData/EsGn/Corp/FromCarlos/ley4251_e0.txt",
                    ruta_meta="../LingData/EsGn/Corp/FromCarlos/ley4251_g0.txt")
    if init:
        d.initialize()
    if train:
        trainer = kuaa.Trainer(d)
        return trainer
    return d

def arch_doc(ruta, proc=True, reinit=False, user=None, session=None,
                ruta_meta=None):
    """Crear un documento del contenido de un archivo."""
    e, g = cargar_eg(train=ruta_meta)
    session = session or kuaa.start(e, g, user)
    arch = open(ruta, encoding='utf8')
    texto = arch.read()
    if ruta_meta:
        arch_meta = open(ruta_meta, encoding='utf8')
        texto_meta = arch_meta.read()
        d = kuaa.Document(e, g, texto, proc=proc, reinitid=reinit, session=session,
                          biling=True, target_text=texto_meta)
    else:
        d = kuaa.Document(e, g, texto, proc=proc, reinitid=reinit, session=session)
    return d

def arch_doc(lengua, ruta, session=None, user=None, proc=False):
    """Crear un documento del contenido de un archivo, solo para análisis."""
    l = cargar(lengua)
    session = session or kuaa.start(l, None, user)
    arch = open(ruta, encoding='utf8')
    texto = arch.read()
    d = kuaa.Document(l, None, texto, proc=proc, session=session)
    return d

##def huesped("Vi al pobre huésped.", solve=True, user=None):
##    e, g = cargar()
##    session = kuaa.start(e, g, user)
##    d = kuaa.Document(e, g, sentence, True, session=session)
##    s = d[0]
##    s.initialize(ambig=False)
##    if solve:
##        s.solve(all_sols=False)
##        if s.solutions and segment:
##            for sol in s.solutions:
##                sol.get_segs()
##        output_sols(s)
##    return s.solutions[0]    

#def eg_bidoc(ruta1, ruta2, proc=True, reinit=False, user=None, docid=''):
#    doc1 = eg_arch_doc(ruta1, user=user)
#    doc2 = eg_arch_doc(ruta2, session=doc1.session, reinit=True)
#    bidoc = kuaa.BiDoc(doc1, doc2, docid=docid)
#    return bidoc

def usuario(username):
    return kuaa.User.users.get(username)

## Cargar castellano y guaraní. Devuelve las 2 lenguas.
def cargar(train=False):
    spa, grn = kuaa.Language.load_trans('spa', 'grn', train=train)
    return spa, grn

## Cargar una lengua, solo para análisis.
def cargar1(lang='spa'):
    spa = kuaa.Language.load_lang(lang)
    return spa

if __name__ == "__main__":
    print("Tereg̃uahẽ porãite Mainumby-me, versión {}\n".format(__version__))
#    kuaa.app.run(debug=True)

##def ui():
##    """Create a UI and two languages."""
##    u = kuaa.UI()
##    e, s = kuaa.Language("English", 'eng'), kuaa.Language("español", 'spa')
##    return u, e, s

## OLD STUFF: Spanish, English, Amharic, Oromo
# Profiling
#import cProfile
#import pstats

### Corpora and patterns

##def corp():
##    return kuaa.Corpus('ep',
##                          tag_map={'n': [('p', 'n'),
##                                         [(1,2), {'s': (('n', 's'),), 'p': (('n', 'p'),)}]],
##                                   'v': [('p', 'v'),
##                                         [(2,4), {'ic': (('tm', 'cnd'),), 'if': (('tm', 'fut'),),
##                                                  'ii': (('tm', 'ipf')), 'ip': (('tm', 'prs'),),
##                                                  'is': (('tm', 'prt'),),
##                                                  'sf': (('tm', 'sft'),),
##                                                  'si': (('tm', 'sbi'),), 'sp': (('tm', 'sbp'),),
##                                                  'g': (('tm', 'ger'),),
##                                                  'n': (('tm', 'inf'),),
##                                                  'p': (('tm', 'prc'),)}]],
##                                   'w': [('p', 'n')]
##                                   },
##                          feat_order={'sj': ['3s', '3p', '1p', '13s', '2p', '1s', '2s'],
##                                      'tm': ['inf', 'prs', 'prt', 'ger', 'prc',
##                                             'fut', 'sbp', 'ipf', 'sbi', 'cnd', 'ipv'],
##                                      'n': ['s', 'p']})
##
##def pos_freq(corpus=None):
##    corpus = corpus or corp()
##    corpus.set_pos_grams('n', {'agua', 'madre', 'comunicación', 'paz', 'futuro', 'fronteras'})
##    corpus.set_pos_grams('v', {'poner', 'querer', 'hacer', 'subir'})
##    corpus.set_pos_grams('a', {'pequeño', 'interesante', 'increíble', 'último', 'corto'})
##
##def europarl_corpus(corpus=None, suffix='0-500', lines=0, posfreq=False, ambig=False):
##    corpus = corpus or corp()
##    corpus.read("../LingData/Es/Europarl/es-en/es-v7-" + suffix, lines=lines)
##    if posfreq:
##        pos_freq(corpus)
##    if ambig:
##        corpus.set_ambig(pos=False)
##    return corpus
##
##def monton():
##    return kuaa.Pattern(['montón', 'de', {('p', 'n')}])
##
##def matar():
##    return kuaa.Pattern([(None, 'matar'), 'a', 2, {('p', 'n')}])
##
##def obligar():
##    return kuaa.Pattern([(None, 'obligar'), 'a', 2, {('p', 'n')},
##                            'a', 2, {('p', 'v')}])
##
##def tc():
##    return kuaa.Pattern([(None, 'tener'), 'en', 'cuenta', (1, 3), (None, 'situación')])
##
##def trans():
##    # ~ se, V, ..., N
##    return kuaa.Pattern([(('~', {'se'}), (None, None)), {('p', 'v')}, 2, {('p', 'n')}])



