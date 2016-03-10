#!/usr/bin/env python3

# Mainumby: Parsing and translation with minimal dependency grammars.
#
########################################################################
#
#   This file is part of the HLTDI L^3 project
#   for parsing, generation, translation, and computer-assisted
#   human translation.
#
#   Copyright (C) 2014, 2015, 2016, HLTDI <gasser@cs.indiana.edu>
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

__version__ = 1.0

import kuaa

## Creación de oración simple y de documento.
def eg_oracion(sentence, ambig=True, solve=False, session=None):
    if session is True:
        session = kuaa.start()
    e, g = cargar_eg()
    d = kuaa.Document(e, g, sentence, True, session=session)
    s = d[0]
    s.initialize(ambig=ambig)
    if solve:
        s.solve(all_sols=ambig)
    return s

def eg_doc(text, proc=True):
    e, g = cargar_eg()
    d = kuaa.Document(e, g, text, proc=proc)
    return d

## Cargar castellano y guaraní. Devuelve las 2 lenguas.
def cargar_eg():
    spa, grn = kuaa.Language.load_trans('spa', 'grn')
    return spa, grn

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

### Parsing and translating of other language pairs

##def test(verbosity=0):
##    piece_of_mind_parse_ung(verbosity=verbosity)
##    piece_of_mind_trans(verbosity=verbosity)
##    kick_the_bucket(verbosity=verbosity)
##    end_of_world(verbosity=verbosity)
##    never_eaten_fish(verbosity=verbosity)
##    never_eaten_fish_ungr(verbosity=verbosity)
##    cantar_las_cuarenta_I(verbosity=verbosity)
##    cantar_las_cuarenta_she(verbosity=verbosity)
##
##def piece_of_mind_parse_ung(verbosity=0, all_sols=True):
##    """
##    Eng parse.
##    Illustrates
##    (1) within SL agreement (fails because 'my' doesn't agree with 'gives')
##    """
##    eng = kuaa.Language.load('eng')[0]
##    s = kuaa.Sentence(raw='Mary gives them a piece of my mind',
##                         language=eng,
##                         verbosity=verbosity)
###    print("Parsing: {}".format(s.raw))
##    s.initialize(verbosity=verbosity)
##    s.solve(translate=False, verbosity=verbosity, all_sols=all_sols)
##    return s
##
##def piece_of_mind_trans(verbosity=0, all_sols=True):
##    """
##    Eng->Spa
##    Illustrates
##    (1) within SL agreement (succeeds because 'her' agrees with 'gives')
##    (2) SL-TL feature agreement
##    (3) SL-TL word count mismatch (SL > TL)
##    """
##    eng, spa = kuaa.Language.load('eng', 'spa')
##    s = kuaa.Sentence(raw='Mary gives them a piece of her mind',
##                         language=eng, target=spa,
##                         verbosity=verbosity)
###    print("Translating {} to {}".format(s.raw, s.target))
##    s.initialize(verbosity=verbosity)
##    s.solve(translate=True, verbosity=verbosity, all_sols=all_sols)
##    return s
##
##def kick_the_bucket(verbosity=0, all_sols=True):
##    """
##    Eng->Spa
##    Illustrates
##    (1) SL group ambiguity (search for solutions)
##    (2) SL-TL feature agreement
##    """
##    eng, spa = kuaa.Language.load('eng', 'spa')
##    s = kuaa.Sentence(raw='John kicked the bucket', language=eng, target=spa,
##                         verbosity=verbosity)
###    print("Translating {} to {}".format(s.raw, s.target))
##    s.initialize(verbosity=verbosity)
##    s.solve(verbosity=verbosity, all_sols=all_sols)
##    return s
##
##def end_of_world(verbosity=0, all_sols=True):
##    """
##    Eng->Spa
##    it's the end of the world -> es el fin del mundo
##    Illustrates
##    (1) SL-TL word count mismatch (SL > TL)
##    """
##    eng, spa = kuaa.Language.load('eng', 'spa')
##    s = kuaa.Sentence(raw="it's the end of the world", language=eng, target=spa,
##                         verbosity=verbosity)
###    print("Translating {} to {}".format(s.raw, s.target))
##    s.initialize(verbosity=verbosity)
##    s.solve(verbosity=verbosity, all_sols=all_sols)
##    return s
##
##def ate_fish(verbosity=0, all_sols=True):
##    """
##    Amh->Orm
##    አሳ በላ (he ate fish) -> qurxummii nyaate.
##    Illustrates
##    (1) SL-TL feature agreement
##    """
##    amh, orm = kuaa.Language.load('amh', 'orm')
##    s = kuaa.Sentence(raw="አሳ በላ", language=amh, target=orm, verbosity=verbosity)
###    print("Translating {} to {}".format(s.raw, s.target))
##    s.initialize(verbosity=verbosity)
##    s.solve(verbosity=verbosity, all_sols=all_sols)
##    return s
##
##def never_eaten_fish(verbosity=0, trans=True, all_sols=True):
##    """
##    Amh አሳ በልቶ አያውቅም 'he's never eaten fish'
##    Either parse (trans=False) or translate -> Orm: qurxummii nyaate hin beeku.
##    Illustrates
##    (1) SL-TL feature agreement
##    (2) SL-TL word count mismatch (SL < TL)
##    """
##    amh, orm = kuaa.Language.load('amh', 'orm')
##    s = kuaa.Sentence(raw="አሳ በልቶ አያውቅም", language=amh, target=orm,
##                        verbosity=verbosity)
##    s.initialize(verbosity=verbosity)
##    if trans:
###        print("Translating {} to {}".format(s.raw, s.target))
##        s.solve(verbosity=verbosity, all_sols=all_sols)
##    else:
###        print("Parsing: {}".format(s.raw))
##        s.solve(translate=False, verbosity=verbosity, all_sols=all_sols)
##    return s
##
##def never_eaten_fish_ungr(trans=True, verbosity=0, all_sols=True):
##    """
##    Amh አሳ በልተው አያውቅም 'he's never eaten fish' (ungrammatical because the
##    በልተው is 3rd person *plural* so it doesn't agree with አያውቅም).
##    Like the last case except since this is ungrammatical, no solution is
##    found that covers all of the words.
##    """
##    amh, orm = kuaa.Language.load_trans('amh', 'orm')
##    s = kuaa.Sentence(raw="አሳ በልተው አያውቅም", language=amh, target=orm,
##                        verbosity=verbosity)
###    print("Attempting to translate {} to {}".format(s.raw, s.target))
##    s.initialize(verbosity=verbosity)
##    s.solve(verbosity=verbosity, all_sols=all_sols)
##    return s
##
##def cantar_las_cuarenta_she(trans=True, verbosity=0, all_sols=True):
##    """
##    Spa->Eng
##    Paula les cantó las cuarenta -> Paula read them the riot act.
##                                 -> Paula gave them a piece of her mind.
##    Illustrates
##    (1) SL-TL feature agreement
##    (2) SL-TL mismatch in word count (SL < TL)
##    (3) SL-TL mismatch in word order
##    (4) SL word not associated with any group
##    (5) within-TL-group agreement
##    """
##    spa, eng = kuaa.Language.load_trans('spa', 'eng')
##    s = kuaa.Sentence(raw="Paula les cantó las cuarenta",
##                        language=spa, target=eng if trans else None,
##                        verbosity=verbosity)
###    print("Translating {} to {}".format(s.raw, s.target))
##    s.initialize(verbosity=verbosity)
##    s.solve(translate=trans, verbosity=verbosity, all_sols=all_sols)
##    return s
##
##def cantar_las_cuarenta_I(trans=True, verbosity=0, all_sols=True):
##    """
##    Spa->Eng
##    les canté las cuarenta -> read them the riot act.
##                           -> gave them a piece of my mind.
##    Illustrates
##    (1) SL-TL feature agreement
##    (2) SL-TL mismatch in word count (SL < TL)
##    (3) SL-TL mismatch in word order
##    (4) SL word not associated with any group
##    (5) within-TL-group agreement
##    """
##    spa, eng = kuaa.Language.load_trans('spa', 'eng')
##    s = kuaa.Sentence(raw="les canté las cuarenta",
##                        language=spa, target=eng if trans else None,
##                        verbosity=verbosity)
###    print("Translating {} to {}".format(s.raw, s.target))
##    s.initialize(verbosity=verbosity)
##    s.solve(translate=trans, verbosity=verbosity, all_sols=all_sols)
##    return s

##def get_ambig(language, write="../LingData/EsGn/ambig.txt"):
##    ambig = {}
##    groups = language.groups
##    for head, grps in groups.items():
##        for group in grps:
##            if len(group.tokens) == 1:
##                trans = group.trans
##                if len(trans) > 1:
##                    ambig[group.name] = [t.name for t, f in trans]
##    if write:
##        ambig = list(ambig.items())
##        ambig.sort()
##        with open(write, 'w', encoding='utf8') as file:
##            for s, t in ambig:
##                print("{} {}".format(s, ','.join(t)), file=file)
##    else:
##        return ambig


