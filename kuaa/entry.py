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
# 2015.05.20
# -- Group heads require a '_', at the beginning for unanalyzed words, following the
#    root for words to analyze: guata_v_i.

import copy, itertools
import yaml
import re

from kuaa.morphology.fs import *

LEXEME_CHAR = '_'
CAT_CHAR = '$'
ATTRIB_SEP = ';'
WITHIN_ATTRIB_SEP = ','
## Regular expressions for reading groups from text files
# non-empty form string followed by possibly empty FS string
FORM_FV = re.compile("([$<'\w]+)\s*((?:\[.+\])?)$")
# possibly empty form string followed by possibly empty FS string, for MorphoSyn pattern
MS_FORM_FV = re.compile("([$<'\w]*)\s*((?:\[.+\])?)$")
HEAD = re.compile("\s*\^\s*([<'\w]+)\s+(\d)$")
# Within agreement spec
# 1=3 n,p
WITHIN_AGR = re.compile("\s*(\d)\s*=\s*(\d)\s*(.+)$")
# Translation agreement spec
# 1==3 ns:n,ps:p
TRANS_AGR = re.compile("\s*(\d)\s*==\s*(\d)\s*(.+)$")
ALIGNMENT = re.compile("\s*\|\|\s*(.+)$")

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

    def get_translations(self):
        """Changed 2015.05.22. translations is not a list of group, dict pairs
        for the target language, no longer a dict with language abbrev keys."""
        
#        if self.trans is None:
#            self.trans = {}
#        if language not in self.trans and create:
#            self.trans[language] = {}
#        return self.trans.get(language)
        return self.trans

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
            if head_index == -1:
                if head in tokens:
                    self.head_index = tokens.index(head)
                else:
                    self.head_index = tokens.index(root)
            else:
                self.head_index = head_index
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

    @staticmethod
    def from_string(string, language, trans_strings=None, target=None, trans=False):
        """Convert a group string and possibly a set of translation group strings
        to one or more groups."""
#        print("Creating group from {} and trans strings {} [trans={}]".format(string, trans_strings, trans))
        # Separate the tokens from any group attributes
        tokens_attribs = string.split(ATTRIB_SEP)
        tokens = tokens_attribs[0].strip().split()
        attribs = tokens_attribs[1:]
        within_agrs = []
        trans_agrs = alignment = None
        if trans:
            trans_agrs = []
            alignment = []
        # Go through tokens separating off features, if any, and assigning head
        # based on presence of '_'
        head_index = -1
        head = None
        features = None
        if '[' in string:
            hasfeats = True
            features = []
        else:
            hasfeats = False
        # Go through attribs, finding head and head index if provided and making agreement lists
        for attrib in attribs:
            # Root and root index
            match = HEAD.match(attrib)
            if match:
                head, head_index = match.groups()
                head_index = int(head_index)
            else:
                match = WITHIN_AGR.match(attrib)
                if match:
                    i1, i2, feats = match.groups()
                    feat_pairs = []
                    for f in feats.split(WITHIN_ATTRIB_SEP):
                        if ':' in f:
                            f1, f2 = f.split(':')
                            feat_pairs.append((f1, f2))
                        else:
                            feat_pairs.append((f, f))
                    within_agrs.append([int(i1), int(i2)] + feat_pairs)
                    continue
                elif trans:
                    match = TRANS_AGR.match(attrib)
                    if match:
                        if not trans_agrs:
                            trans_agrs = [False] * len(tokens)
                        si, ti, feats = match.groups()
                        feat_pairs = []
                        for f in feats.split(WITHIN_ATTRIB_SEP):
                            if ':' in f:
                                sf, tf = f.split(':')
                                feat_pairs.append((sf, tf))
                            else:
                                feat_pairs.append((f, f))
                        trans_agrs[int(si)] = feat_pairs
    #                    trans_agrs.append([int(si), int(ti)] + feat_pairs)
                        continue
                    match = ALIGNMENT.match(attrib)
                    if match:
                        align = match.groups()
                        for index in align.split(WITHIN_ATTRIB_SEP):
                            alignment.append(int(index))
                        continue
                    print("Something wrong with attribute string {}".format(attrib))
                else:
                    print("Something wrong with attribute string {}".format(attrib))
            
        for index, token in enumerate(tokens):
            foundfeats = False
            # separate features if any
#            m = FORM_FV.match(token)
#            if not m:
#                print("String {}".format(string))
            tok, feats = FORM_FV.match(token).groups()
            if feats:
                foundfeats = True
                features.append(FeatStruct(feats))
#                tokens[index] = tok
            elif hasfeats:
                features.append(False)
            if not head:
                # Head not set yet
                if '_' in tok or foundfeats:
                    head_index = index
                    head = tok
        tgroups = None
        if target and trans_strings:
            tgroups = []
            for tstring in trans_strings:
                tgroup, tg, alg = Group.from_string(tstring, target, trans_strings=None, trans=True)
                tattribs = {'agr': tg}
                if alg:
                    tattribs['align'] = alg
                tgroups.append((tgroup, tattribs))
        g = Group(tokens, head_index=head_index, head=head, features=features, agr=within_agrs)
        if target and not trans:
            g.trans = tgroups
        language.add_group(g)
        return g, trans_agrs, alignment

    ### Translations

    ## Alignments: position correspondences, agreement constraints
    ## አድርጎ አያውቅም -> godhe hin beeku
    ## a: {positions: (1, 2),
    ##     agreements: {gen: gen},
    ##     featmaps: {((pers, 2), (num, 2)): ((pers, 3), (num, 2))}
    ##     }

    def add_alignment(self, trans):
        pass

class MorphoSyn(Entry):
    """Within-language patterns that modify morphology a word/root on the basis of the occurrence of other words."""

    def __init__(self, language, name=None, pattern=None, change=None, direction=True):
        """pattern and change are strings, which get expanded at initialization.
        direction = True is left-to-right matching, False right-to-left matching.
        """
        name = name or MorphoSyn.make_name(pattern)
        Entry.__init__(self, name, language)
        # Expand here?
        self.pattern = self.expand_pattern(pattern)
        self.change = change
        self.direction = direction

    @staticmethod
    def make_name(pattern):
        """Pattern is a string."""
        return "{{ " + pattern + " }}"

    def expand_pattern(self, pattern):
        """
        Pattern is a string consisting of elements separated by spaces. An element may be
        - a word
        - a FeatStruct
        - a category with or without a FeatStruct ($...)
        - a gap of some range of words (<l-h> or <g>, where l is minimum, h is maximum and g is exact gap)
        """
        # For now, just split the string into a list of items.
        p = []
        for item in pattern.split():
            form, fv = MS_FORM_FV.match(item).groups()
            if fv:
                fv = FeatStruct(fv)
            p.append((form, fv))
        return p

    def pattern_length(self):
        return len(self.pattern)

    def match(self, sentence):
        """
        Match sentence, a list of analyzed words, against the MorphoSyn's pattern.
        """
        if self.direction:
            pindex = 0
            mindex = -1
            # left-to-right
            for sindex, sitem in enumerate(sentence):
                if self.match_item(sitem, pindex):
                    # Is this the end of the pattern?
                    if self.pattern_length() == pindex + 1:
                        return mindex, sindex
                    pindex += 1
                    if mindex < 0:
                        # Start of matching
                        mindex = sindex
                else:
                    # Start over
                    mindex = -1
                    pindex = 0
            return False
        return False

    def match_item(self, sitem, pindex):
        pform, pfv = self.pattern[pindex]
        # No FS to match
        if not pfv:
            return pform == sitem
        return False

    def expand_change(self, change):
        """
        Change is the addition of a FeatStruct to a root in the pattern and possibly the deletion of one or more
        other items.
        """
        pass

class EntryError(Exception):
    '''Class for errors encountered when attempting to update an entry.'''

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
    
