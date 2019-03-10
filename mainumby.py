#!/usr/bin/env python3

# Mainumby: Parsing and translation with minimal dependency grammars.
#
########################################################################
#
#   This file is part of the PLoGS project
#   for parsing, generation, translation, and computer-assisted
#   human translation.
#
#   Copyleft 2014, 2015, 2016, 2017, 2018, 2019; HLTDI, PLoGS <gasser@indiana.edu>
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
# 2019
# -- Limited disambiguation

__version__ = 2.0

import kuaa

## Atajos

## Creación y traducción de oración simple.
def proc(oracion, generate=True, verbosity=0):
    e, g = cargar()
    session = kuaa.start(e, g, user, create_memory=True)
    d = kuaa.Document(e, g, oracion, True, single=True, session=session)
    if len(d) == 0:
        return
    s = d[0]
    s.initialize(ambig=False, constrain_groups=True, verbosity=verbosity)
    s.solve(all_sols=False, constrain_groups=True, verbosity=verbosity)
    if s.segmentations:
        s.process(generate=generate, verbosity=verbosity)
        if generate:
            return s.get_translations()
        else:
            return s

## Creación (y opcionalmente traducción) de oración simple y de documento.
## Por defecto, las palabras en segmentos no se generan morfológicamente.
def ora(sentence, ambig=False, solve=True, user=None, segment=True, max_sols=1,
        single=True, translate=True, constrain_groups=True, generate=False,
        verbosity=0):
    e, g = cargar()
    session = kuaa.start(e, g, user, create_memory=single)
    d = kuaa.Document(e, g, sentence, True, single=single, session=session)
    if len(d) == 0:
        print("Parece que falta puntuación final en el documento.")
        return
    s = d[0]
    s.initialize(ambig=ambig, constrain_groups=constrain_groups,
                 verbosity=verbosity)
    if solve or segment:
        s.solve(all_sols=ambig or max_sols > 1, max_sols=max_sols,
                translate=translate)
        if s.segmentations:
            if translate and segment:
                for seg in s.segmentations:
                    seg.get_segs(html=False, single=single)
                    if generate:
                        seg.generate()
                segmentation = s.segmentations[0]
                for segment in segmentation.segments:
                    print("{}: {}".format(segment, segment.cleaned_trans))
                return segmentation
            return s.segmentations
    return s

def ora1(sentence):
    """A sentence prior to segmentation and translation."""
    return ora(sentence, solve=False, segment=False, single=True, translate=False)

def anal(sentence, verbosity=0):
    """Analyze a Spanish sentence, checking all groups."""
    e, g = cargar()
    session = kuaa.start(e, g, None, create_memory=True)
    d = kuaa.Document(e, g, sentence, True, single=True, session=session)
    s = d[0]
    return s.analyze(verbosity=verbosity)

def g_anal(sentence, single=True, verbosity=0):
    """Analyze a Guarani sentence, checking all groups."""
    e, g = cargar(train=True)
    session = kuaa.start(g, e, None, create_memory=single)
    d = kuaa.Document(g, None, sentence, session=session, single=single)
    if len(d) == 0:
        print("Documento vacío")
        return
    s = d[0]
    return s.analyze(translate=False, verbosity=verbosity)

## Cargar castellano y guaraní. Devuelve las 2 lenguas.
def cargar(train=False):
    spa, grn = kuaa.Language.load_trans('spa', 'grn', train=train)
    return spa, grn

## Cargar una lengua, solo para análisis.
def cargar1(lang='spa'):
    spa = kuaa.Language.load_lang(lang)
    return spa

## Oraciones para evalucación

oraciones = \
          ["Los pasajeros se murieron ayer.",
           "Me acordé de ese hombre feo.",
           "La profesora encontró a su marido en la calle."]

## Procesamiento de corpus.

def biblia2():
    """Lista de oraciones (bilingües) de la Biblia (separadas por tabulador)."""
    with open("../Bitext/EsGn/Biblia/biblia_tab.txt", encoding='utf8') as file:
        return file.readlines()

def dgo():
    with open("../Bitext/EsGn/DGO/dgo_id2_tab.txt", encoding='utf8') as file:
        return file.readlines()

##def split_biblia():
##    """Assuming biblia_tab.txt is in good shape, write the Es and Gn sentences
##    to separate files."""
##    lines = biblia2()
##    with open("../Bitext/EsGn/Biblia/biblia_tab_es.txt", 'w', encoding='utf8') as es:
##        with open("../Bitext/EsGn/Biblia/biblia_tab_gn.txt", 'w', encoding='utf8') as gn:
##            for line in lines:
##                e, g = line.split('\t')
##                print(e.strip(), file=es)
##                print(g.strip(), file=gn)

def biblia_ora(train=True):
    """Lista de pares de oraciones (instancias de Sentence) de la Biblia."""
    oras = biblia2()
    e, g = cargar(train=train)
    o1, o2 = kuaa.Document.proc_preseg(e, g, oras, biling=True)
    return o1, o2

def dgo_ora(train=True):
    oras = dgo()
    e, g = cargar(train=train)
    o1, o2 = kuaa.Document.proc_preseg(e, g, oras, biling=True)
    return o1, o2

def bib_bitext_anal(start=5750, end=-1, n=250, write=True, filename="biblia1"):
    """Separate Bible sentences, superficially analyze them, creating
    pseudosegments, append these to file."""
    o1, o2 = biblia_ora()
    e = o1[0].language
    if n:
        end = start + n
    elif end < 0:
        end = len(o1)
    print("Analizando pares de oraciones desde {} hasta {}".format(start, end))
    a = kuaa.Sentence.bitext_anal(o1, o2, start=start, end=end)
    if write:
        kuaa.Sentence.write_pseudosegs(e, a, filename)

def dgo_bitext_anal(start=0, end=-1, n=400, write=True, filename="dgo"):
    """Separate DGO sentences, superficially analyze them, creating
    pseudosegments, append these to file."""
    o1, o2 = dgo_ora()
    e = o1[0].language
    if n:
        end = start + n
    elif end < 0:
        end = len(o1)
    print("Analizando pares de oraciones desde {} hasta {}".format(start, end))
    a = kuaa.Sentence.bitext_anal(o1, o2, start=start, end=end)
    if write:
        kuaa.Sentence.write_pseudosegs(e, a, filename)

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
    """Solve; print and return segmentations."""
    sentence.solve()
    output_sols(sentence)
    return sentence.segmentations

def output_sols(sentence):
    """Show target outputs for all segmentations for sentence."""
    for sol in sentence.segmentations:
        for x in sol.get_ttrans_outputs():
            print(x)

def usuario(username):
    return kuaa.User.users.get(username)

if __name__ == "__main__":
    print("Tereg̃uahẽporãite Mainumby-pe, versión {}\n".format(__version__))
#    kuaa.app.run(debug=True)

##def ley_bidoc(init=True, train=True):
##    d = eg_arch_doc("../LingData/EsGn/Corp/FromCarlos/ley4251_e0.txt",
##                    ruta_meta="../LingData/EsGn/Corp/FromCarlos/ley4251_g0.txt")
##    if init:
##        d.initialize()
##    if train:
##        trainer = kuaa.Trainer(d)
##        return trainer
##    return d

##def bidoc(ruta="../Bitext/EsGn/Biblia/biblia_tab.txt"):
##    e, g = cargar(train=True)
##    d = kuaa.Document(e, g, text='', biling=True, path=ruta)
##    return d
##
##def arch_doc2(ruta, proc=True, reinit=False, user=None, session=None, ruta_meta=None):
##    """Crear un documento del contenido de un archivo."""
##    e, g = cargar_eg(train=ruta_meta)
##    session = session or kuaa.start(e, g, user)
##    arch = open(ruta, encoding='utf8')
##    texto = arch.read()
##    if ruta_meta:
##        arch_meta = open(ruta_meta, encoding='utf8')
##        texto_meta = arch_meta.read()
##        d = kuaa.Document(e, g, texto, proc=proc, reinitid=reinit, session=session,
##                          biling=True, target_text=texto_meta)
##    else:
##        d = kuaa.Document(e, g, texto, proc=proc, reinitid=reinit, session=session)
##    return d
##
##def arch_doc1(lengua, ruta, session=None, user=None, proc=False):
##    """Crear un documento del contenido de un archivo, solo para análisis."""
##    l = cargar(lengua)
##    session = session or kuaa.start(l, None, user)
##    arch = open(ruta, encoding='utf8')
##    texto = arch.read()
##    d = kuaa.Document(l, None, texto, proc=proc, session=session)
##    return d

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
