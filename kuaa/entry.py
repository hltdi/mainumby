#   
#   Ñe'ẽasa entries: words, grammatical morphemes, lexemes, lexical classes
#
########################################################################
#
#   This file is part of the HLTDI L^3 project
#   for parsing, generation, translation, and computer-assisted
#   human translation.
#
#   Copyright (C) 2014, 2015, HLTDI <gasser@cs.indiana.edu>
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

# 2014.02.10
# -- Created
#    Possible subclasses: Lex (word, lexeme, class), Gram
# 2014.02.12
# -- Inheritance (class to word/lexeme): completed except for government.
#    (But possible conflicts in order are not handled yet.)
# 2014.02.15
# -- Methods for making dicts from entries and entries from dict, used
#    in serialization.
# 2014.02.16-18
# -- Class for groups (multi-word expressions).
# 2014.02.18
# -- Cloning of Lex instances (for groups and L3 nodes).
# 2014.03.18
# -- Lots of changes and additions to groups.
# 2014.03.24
# -- words attribute in Group is a list of [word, feat_dict] pairs.
# 2014.04.16
# -- Created simpler Group (with no dependency types), renamed old Group to MWE.
# 2014.04.20
# -- Matching of group and sentence nodes.
# 2014.04.30
# -- Eliminated everything but Groups.
# 2014.05.01
# -- Group/node matching fixed.
# 2014.05.06
# -- Group entry indices need to distinguish ambiguous words/lexemes.
#    Indices can be things like "end_n", with POS or other identifiers after "_".
#    "end_n" and "end_v" would be different roots of "end" in the forms dict.

import copy, itertools
import yaml

from kuaa.morphology.fs import *

LEXEME_CHAR = '_'
CAT_CHAR = '$'

class Entry:
    """Superclass for Group and possibly other lexical classes."""

    ID = 1
    dflt_dep = 'dflt'
    
    def __init__(self, name, language, id=0, trans=None):
        """Initialize name and basic features: language, trans, count, id."""
        self.name = name
        self.language = language
        self.trans = trans
        self.count = 1
        if id:
            self.id = id
        else:
            self.id = Entry.ID
            Entry.ID += 1

    def __repr__(self):
        """Print name."""
        return '<{}:{}>'.format(self.name, self.id)

    @staticmethod
    def is_cat(name):
        """Is this the name of a category?"""
        return CAT_CHAR in name

    @staticmethod
    def is_lexeme(name):
        """Is this the name of a lexeme?"""
        return LEXEME_CHAR in name

    ## Serialization

    def to_dict(self):
        """Convert the entry to a dictionary to be serialized in a yaml file."""
        d = {}
        d['name'] = self.name
#        d['language'] = self.language
        d['count'] = self.count
        if self.trans:
            d['trans'] = self.trans
        d['id'] = self.id
        return d

    @staticmethod
    def from_dict(d, language):
        """Convert a dict (loaded from a yaml file) to an Entry object."""
        e = Entry(d.get('name'), language)
        e.count = d.get('count', 1)
        e.id = d.get('id', 1)
        e.trans = d.get('trans')
        return e

    def update_count(self, count=1):
        """Update count on the basis of data from somewhere."""
        self.count += count

    ### Translations (word, gram, lexeme, group entries)
    ###
    ### Translations are stored in a language-id-keyed dict.
    ### Values are dicts with target entry names as ids.
    ### Values are dicts with correspondence ('cor'), count ('cnt'), etc.
    ### as keys.

    def get_translations(self, language, create=True):
        """Get the translation dict for language in word/lexeme/gram entry.
        Create it if it doesn't exist and create is True."""
        if self.trans is None:
            self.trans = {}
        if language not in self.trans and create:
            self.trans[language] = {}
        return self.trans.get(language)

    def add_trans(self, language, trans, count=1):
        """Add translation to the translation dictionary for language,
        initializing its count."""
        transdict = self.get_translations(language, create=True)
        transdict[trans] = {'c': count}

    def update_trans(self, language, trans, count=1):
        """Update the count of translation."""
        transdict = self.get_translations(language)
        if trans not in transdict:
            s = "Attempting to update non-existent translation {} for {}"
            raise(EntryError(s.format(trans, self.name)))
        transdict[trans]['c'] += count

class Group(Entry):
    """Primitive multi-word expression. Default is a head with unlabeled dependencies
    to all other tokens and translations, including alignments, to one or more
    other languages."""

    def __init__(self, tokens, head_index=-1, head='', language=None, name='',
                 features=None, agr=None, trans=None):
        """Either head_index or head (a string) must be specified."""
        # tokens is a list of strings
        # name may be specified explicitly or not
        # head is a string like 'guata' or 'guata_' or 'guata_v'
        root, x, pos = head.partition('_')
        # Either something like 'v', or ''
        self.pos = pos
        name = name or Group.make_name(tokens)
        Entry.__init__(self, name, language, trans=trans)
        self.tokens = tokens
        if head:
            self.head = head
            if head in tokens:
                self.head_index = tokens.index(head)
            else:
                self.head_index = tokens.index(root)
#            self.head_index = tokens.index(head_tokens[0]) or tokens.index(head_tokens[1])
        else:
            self.head = tokens[head_index]
            self.head_index = head_index
        # Either None or a list of feat-val dicts for tokens that require them
        # Convert dicts to FeatStruct objects
        if isinstance(features, list):
            features = [FeatStruct(d) if d else None for d in features]
        self.features = features
        # Agr constraints: each a list of form
        # (node_index1, node_index2 . feature_pairs)
        self.agr = agr or None

    def __repr__(self):
        """Print name."""
        return '{}:{}'.format(self.name, self.id)

    @staticmethod
    def make_name(tokens):
        """Each token is either a string or a (string, feat_dict) pair. In name, they're separated by '.'."""
#        strings = []
#        for token in tokens:
#            if isinstance(token, str):
#                strings.append(token)
#            else:
#                form, feat_dict = token
#                fv = ['{}={}'.format(f, v) for f, v in feat_dict.items()]
#                fv = ','.join(fv)
#                strings.append("{}:{}".format(form, fv))
        return '.'.join(tokens)

    # Serialization

    def to_dict(self):
        """Convert the group to a dictionary to be serialized in a yaml file."""
        d = Entry.to_dict(self)
        d['words'] = self.tokens
        d['features'] = self.features
        d['agr'] = self.agr
        return d

    @staticmethod
    def from_dict(d, language, head):
        """Convert a dict (loaded from a yaml file) to a Group object."""
        tokens = d['words']
        features = d.get('features')
        agr = d.get('agr')
        name = d.get('name', '')
        trans = d.get('trans')
        p = Group(tokens, head=head, language=language, features=features,
                  agr=agr, name=name, trans=trans)
        return p

    def match_nodes(self, snodes, head_sindex, verbosity=0):
        """Attempt to match the group tokens (and features) with snodes from a sentence,
        returning the snode indices and root and unified features if any."""
#        print("Does {} match {}".format(self, snodes))
        match_snodes = []
        for index, token in enumerate(self.tokens):
            match_snodes1 = []
            feats = self.features[index] if self.features else None
            if verbosity:
                print(" Attempting to match {}".format(token))
            matched = False
            for node in snodes:
                if verbosity:
                    print("  Trying {}, token index {}, snode index {} head index {}".format(node, index, node.index, head_sindex))
                if index == self.head_index:
                    # This token is the head of the group
                    if node.index == head_sindex:
                        # This was already matched in lexicalization
#                if index == node.index == head_sindex:
                        # This is the token corresponding to the group head
                        node_match = node.match(token, feats)
                        if node_match == False:
                            # This has to match, so fail now
                            return False
                        else:
                            match_snodes1.append((node.index, node_match))
                            if verbosity:
                                print("  Head matched already".format(node))
                            matched = True
                            # Don't look further for an snode to match this token
                            break
                else:
                    node_match = node.match(token, feats)
                    if verbosity:
                        print('  Node {} match {}:{}, {}:: {}'.format(node, token, index, feats, node_match))
                    if node_match != False:
                        match_snodes1.append((node.index, node_match))
                        if verbosity:
                            print("  Matched node {}".format(node))
                        matched = True
            if not matched:
                if verbosity:
                    print("  {} not matched; failed".format(token))
                return False
            else:
                match_snodes.append(match_snodes1)
#        print("Group {}, s_indices {}".format(self, match_snodes))
        return match_snodes

    ### Translations

    ## Alignments: position correspondences, agreement constraints
    ## አድርጎ አያውቅም -> godhe hin beeku
    ## a: {positions: (1, 2),
    ##     agreements: {gen: gen},
    ##     featmaps: {((pers, 2), (num, 2)): ((pers, 3), (num, 2))}
    ##     }

    def add_alignment(self, trans):
        pass

class EntryError(Exception):
    '''Class for errors encountered when attempting to update an entry.'''

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
    
