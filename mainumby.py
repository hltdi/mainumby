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
# -- Simplified shortcut functions by including many of them in __init__.py

__version__ = 2.0

import kuaa

## Bases de datos

def db_texts():
    texts = [kuaa.Text.read("prueba", title="Prueba", segment=True),
             kuaa.Text.read("pajarito", domain="Cuentos", title="Pajarito Perezoso", segment=True),
             kuaa.Text.read("abejas", domain="Ciencia", title="Reducción de Abejas", segment=True),
             kuaa.Text.read("maiz", domain="Infantil", title="Maíz", segment=True),
             kuaa.Text.read("pimienta", domain="Infantil", title="Pimienta que Huye", segment=True),
             kuaa.Text.read("chaco", domain="Ciencia", title="Chaco Boreal", segment=True),
             kuaa.Text.read("tiwanaku", domain="Historia", title="Imperio Tiahuanaco-Huari", segment=True)]
    kuaa.db.session.add_all(texts)

def db_users():
    db_create_admin()
    db_create_anon()
    db_create_old_users()

def db_reinit():
    kuaa.db.create_all()
    kuaa.db.session = kuaa.db.create_scoped_session()

def db_create_admin():
    admin = kuaa.Human(username='admin', email='gasser@indiana.edu', name="administrador",
                       pw_hash='pbkdf2:sha256:50000$emvjKpZe$1d7a96e2375857a689b66ea66e6496f9e9d5c3bb6c9db95d5e99827aa915bf04')
    db_add(admin)

def db_create_anon():
    anon = kuaa.Human(username='anon', email='onlyskybl@gmail.com', name="anónimo",
                      pw_hash='pbkdf2:sha256:50000$U0Ls5bk2$81e2e46cd121cd8145317535c7d0a5e08726c09bba439c945e3b4a8975db053b')
    db_add(anon)

def db_create_old_users():
    humans = []
    with open("notes/tmp.txt") as file:
        for line in file:
            username, pw_hash, email, name, level = line.strip().split(';')
            humans.append(kuaa.Human(username=username, pw_hash=pw_hash,
                                     email=email, name=name, level=level))
    kuaa.db.session.add_all(humans)

def db_serialize_class(klass):
    """Return a list of dicts, one for each member of DB class."""
    return [obj.to_dict() for obj in db_list(klass)]

#def db_recreate_session():
#    kuaa.db.session = kuaa.db.create_scoped_session()

#def db_create(db=None):
#    """db puede ser también 'text' o 'lex'."""
#    kuaa.db.create_all(bind=db)

#def db_destroy(db=None):
#    """db puede ser también 'text' o 'lex'."""
#    kuaa.db.drop_all(bind=db)

def db_list(klass):
    """klass is something like kuaa.Text."""
    return kuaa.db.session.query(klass).all()

def db_add(instance):
    kuaa.db.session.add(instance)

def db_delete(instance):
    kuaa.db.session.delete(instance)
                                   
## Atajos

## Creación y traducción de oración simple. Después de la segmentación inicial,
## se combinan los segmentos, usando patrones gramaticales ("joins") y grupos
## adicionales.

def tra(oracion, html=False, user=None, verbosity=0):
    return ora(oracion, user=user, max_sols=2, translate=True,
               connect=True, generate=True, html=html, verbosity=verbosity)

## Creación (y opcionalmente traducción) de oración simple y de documento.

def ora(text, user=None, max_sols=2, translate=True,
        connect=True, generate=False, html=False, verbosity=0):
    return kuaa.oración(text, user=user, max_sols=max_sols, translate=translate,
                        connect=connect, generate=generate, html=html,
                        verbosity=verbosity)

def anal(sentence, user=None, verbosity=0):
    """Analizar una oración castellana."""
    return kuaa.oración(sentence, user=user, translate=False, verbosity=verbosity)

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

O = \
  ["El hombre que fue hasta la ciudad.",
   "El hombre vio a la mujer.",
   "El buen gato duerme.",
   "El gato negro duerme.",
   "Los pasajeros se murieron ayer.",
   "Me acordé de ese hombre feo.",
   "La profesora encontró a su marido en la calle."]

O1 = \
   ["La economía de Paraguay se caracteriza por la predominancia de los sectores agroganaderos, comerciales y de servicios.",
    "La economía paraguaya es la décimo cuarta economía de América Latina en términos de producto interno bruto (PIB) nominal."]

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
