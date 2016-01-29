#   
#   Mainumby
#   Mbojereha entries: words, grammatical morphemes, lexemes, lexical classes
#
########################################################################
#
#   This file is part of the HLTDI L^3 project
#   for parsing, generation, translation, and computer-assisted
#   human translation.
#
#   Copyright (C) 2014, 2015, 2016 HLTDI <gasser@indiana.edu>
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
# 2015.06.07
# -- This is no longer true. Unanalyzed heads can be strings without '_' (I think...).
# 2015.06.08...
# -- Morphosyn class: patterns that relate syntax to morphology, by modifying FeatStructs
#    in word analyses and deleting free grammatical morphemes that trigger the changes.
# 2015.08.03
# -- Group elements may be "set items" (names beginning with '$$'), implemented as categories
#    but unlike "category items", not intended to merge with nodes in other group instances
#    during sentence analysis.
# 2015.08.13
# -- Forced feature agreement in MorphoSyn matching works with embedded features (doesn't
#    override existing subfeature values)
# 2015.09.26
# -- Groups have a priority method that assigns a score based on the number of tokens and
#    features; used in ordering groups for particular keys.
# 2015.10.01
# -- Morphosyn patterns can swap elements (and make no other changes), for example,
#    lo + [pos=v] --> [pos=v] + lo
# 2015.10.18-20
# -- Morphosyn patterns can include ambiguity, with sentence copied and constraints applied
#    to original or copy (depending on which interpretation is preferred)
# 2015.10.26
# -- Morphosyns can fail if others have succeeded (see **2formal in spa/syn/grn.ms)

import copy, itertools
import yaml
import re

from kuaa.morphology.fs import *

## Group files
LEXEME_CHAR = '_'
CAT_CHAR = '$'
SET_CHAR = '$$'
ATTRIB_SEP = ';'
WITHIN_ATTRIB_SEP = ','
## Regular expressions for reading groups from text files
# non-empty form string followed by possibly empty FS string
FORM_FEATS = re.compile("([$<'¿?¡!\-\w]+)\s*((?:\[.+\])?)$")
# !FS(#1-#2), representing a sequence of #1 to #2 negative FS matches
NEG_FEATS = re.compile("\s*!(\[.+\])(\(\d-\d\))$")
HEAD = re.compile("\s*\^\s*([<'¿?¡!\-\w]+)\s+(\d)\s*$")
# Within agreement spec
# 1=3 n,p
WITHIN_AGR = re.compile("\s*(\d)\s*=\s*(\d)\s*(.+)$")
# Translation agreement spec
# 1==3 ns:n,ps:p
TRANS_AGR = re.compile("\s*(\d)\s*==\s*(\d)\s*(.+)$")
ALIGNMENT = re.compile("\s*\|\|\s*(.+)$")
# Count of source group
COUNT = re.compile("\s*#\s*(\d+)$")
# Count of translation to target group
TRANS_COUNT = re.compile("\s*##\s*(\d+)$")

## MorphoSyn regex
# Separates elements of MorphoSyn pattern
MS_PATTERN_SEP = ' '
# Separates form alternatives in MorphSyn pattern
FORMALT_SEP = '|'
MS_ATTRIB_SEP = ';'
# possibly empty form string followed by possibly empty FS string, for MorphoSyn pattern
MS_FORM_FEATS = re.compile("\s*([$<'|\w]*)\s*((?:\[.+\])?)$")
# negative features: ![] with only features catpured
MS_NEG_FEATS = re.compile("\s*!(\[.+\])$")
MS_AGR = re.compile("\s*(\d)\s*=>\s*(\d)\s*(.+)$")
MS_DELETE = re.compile("\s*//\s*(.+)$")
MS_ADD = re.compile("\s*\+\+\s*(.+)$")
MS_SWAP = re.compile("\s*><\s*(.+)$")
MS_FAILIF = re.compile("\s*FAILIF\s*(.+)$")
# digit -> [FS], all obligatory
MS_FEATMOD = re.compile("\s*(\d)\s*->\s*(\[.+\])$")

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
    def is_set(name):
        """Is this the name of a set (implemented as a category)?"""
        return SET_CHAR in name

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

    ### Translations of entries

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
                 features=None, agr=None, trans=None, count=0):
        """Either head_index or head (a string) must be specified."""
        # tokens is a list of strings
        # name may be specified explicitly or not
        # head is a string like 'guata' or 'guata_' or 'guata_v'
        if head:
            self.head = head
            root, x, pos = head.partition('_')
            # Either something like 'v', or ''
            self.pos = pos
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
            
        name = name or Group.make_name(tokens)
        Entry.__init__(self, name, language, trans=trans)
        self.tokens = tokens
        # Either None or a list of feat-val dicts for tokens that require them
        # Convert dicts to FeatStruct objects
        if isinstance(features, list):
            features = [FeatStruct(d) if d else None for d in features]
        self.features = features
        # Agr constraints: each a list of form
        # (node_index1, node_index2 . feature_pairs)
        self.agr = agr or None
        # Count in TMs
        self.count = count

    def __repr__(self):
        """Print name."""
        return '{}:{}'.format(self.name, self.id)

    @staticmethod
    def make_name(tokens):
        """Each token is either a string or a (string, feat_dict) pair. In name, they're separated by '.'."""
        return '.'.join(tokens)

    def priority(self):
        """Returns a value that is used in sorting the groups associated with a particular key.
        Groups with more tokens and more features have priority."""
        featscore = .3 * sum([len(f) for f in self.features if f]) if self.features else 0.0
        return len(self.tokens) + featscore

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
        if verbosity > 1:
            print("Does {} match {}".format(self, snodes))
        match_snodes = []
        last_sindex = -1
        last_cat = False
        for index, token in enumerate(self.tokens):
            match_snodes1 = []
            feats = self.features[index] if self.features else None
            if verbosity > 0:
                print(" Attempting to match {} in {}".format(token, self))
            matched = False
            for node in snodes:
                snode_indices = node.raw_indices
                snode_start, snode_end = snode_indices[0], snode_indices[-1]
                if verbosity > 1:
                    print("  Trying {}, token index {}, snode index {}, head index {}, last s index {}".format(node, index, snode_indices, head_sindex, last_sindex))
                if index == self.head_index:
                    # This token is the head of the group
                    if node.index == head_sindex:
                        # This is the token corresponding to the group head
                        node_match = node.match(token, feats)
                        if node_match == False:
                            # This has to match, so fail now
                            if verbosity:
                                print("{} failed to match in token {}".format(self, token))
                            return False
                        else:
                            # Check whether the token is in the right position with respect to others
                            if index > 0 and not last_cat and last_sindex >=0 and snode_start - last_sindex != 1:
                                if verbosity:
                                    print(" Group head token {} in sentence position {} doesn't follow last token at {}".format(token, snode_indices, last_sindex))
                                    print("{} failed to match in token {}".format(self, token))
                                return False
                            match_snodes1.append((node.index, node_match))
                            if verbosity:
                                print(" Group token {} matched node {} in {}, node index {}, last_sindex {}".format(token, node, self, snode_indices, last_sindex))
                            last_sindex = snode_end
                            if verbosity > 1:
                                print("  Head matched already".format(node))
                            matched = True
                            # Don't look further for an snode to match this token
                            break
                else:
                    node_match = node.match(token, feats)
                    if verbosity > 1:
                        print('  Node {} match {}:{}, {}:: {}'.format(node, token, index, feats, node_match))
                    if node_match != False:
                        if not Group.is_cat(token) and not last_cat and index > 0 and last_sindex >= 0 and snode_start - last_sindex != 1:
                            if verbosity:
                                print(" Group token {} in sentence position {} doesn't follow last token at {}".format(token, snode_indices, last_sindex))
                            return False
                        match_snodes1.append((node.index, node_match))
                        if Group.is_cat(token):
                            last_cat = True
                        else:
                            last_cat = False
                        if verbosity:
                            print(" Group token {} matched node {} in {}, node index {}, last_sindex {}".format(token, node, self, snode_indices, last_sindex))
                        last_sindex = snode_end
                        if verbosity > 1:
                            print("  Matched node {}".format(node))
                        matched = True
            if not matched:
                if verbosity > 1:
                    print("  {} not matched; failed".format(token))
                return False
            else:
                match_snodes.append(match_snodes1)
#        print("Group {}, s_indices {}".format(self, match_snodes))
        return match_snodes

    @staticmethod
    def from_string(string, language, trans_strings=None, target=None, trans=False,
                    n_src_tokens=1):
        """Convert a group string and possibly a set of translation group strings
        to one or more groups."""
#        print("Creating group from {} and trans strings {} [trans={}]".format(string, trans_strings, trans))
        # Separate the tokens from any group attributes
        tokens_attribs = string.split(ATTRIB_SEP)
        tokens = tokens_attribs[0].strip().split()
        attribs = tokens_attribs[1:]
        within_agrs = []
        trans_agrs = alignment = None
        trans_count = 0
        if trans:
            trans_agrs = []
            alignment = []
        head_index = -1
        head = None
        features = None
        count = 0
        if '[' in string:
            hasfeats = True
            features = []
        else:
            hasfeats = False
        # Go through attribs, finding head and head index if not provided and making agreement lists
        for attrib in attribs:
            # Root and root index
            match = HEAD.match(attrib)
            if match:
                head, head_index = match.groups()
                head_index = int(head_index)
                continue
            match = COUNT.match(attrib)
            if match:
                count = int(match.groups()[0])
            else:
                match = WITHIN_AGR.match(attrib)
                if match:
                    i1, i2, feats = match.groups()
                    feat_pairs = []
                    for f in feats.split(WITHIN_ATTRIB_SEP):
                        f = f.strip()
                        if ':' in f:
                            f1, f2 = f.split(':')
                            feat_pairs.append((f1.strip(), f2.strip()))
                        else:
                            feat_pairs.append((f.strip(), f.strip()))
                    within_agrs.append([int(i1), int(i2)] + feat_pairs)
                    continue
                elif trans:
                    match = TRANS_AGR.match(attrib)
                    if match:
                        if not trans_agrs:
                            trans_agrs = [False] * n_src_tokens
                        si, ti, feats = match.groups()
                        feat_pairs = []
                        for f in feats.split(WITHIN_ATTRIB_SEP):
                            if ':' in f:
                                sf, tf = f.split(':')
                                feat_pairs.append((sf.strip(), tf.strip()))
                            else:
                                feat_pairs.append((f.strip(), f.strip()))
                        # 2016.1.26: changed to tuple so it can be part of a dict index later on
                        feat_pairs = tuple(feat_pairs)
                        # Changed 2015.07.13 to include index of target item
                        trans_agrs[int(si)] = (int(ti), feat_pairs)
                        continue
                    match = ALIGNMENT.match(attrib)
                    if match:
                        align = match.groups()[0]
                        for index in align.split(WITHIN_ATTRIB_SEP):
                            alignment.append(int(index))
                        continue
                    match = TRANS_COUNT.match(attrib)
                    if match:
                        trans_count = int(match.groups()[0])
                        continue
                else:
                    print("Something wrong with attribute string {}".format(attrib))
        # Go through tokens separating off features, if any, and assigning head
        # based on presence of '_'
        name_toks = []
        for index, token in enumerate(tokens):
            name_toks.append(token)
            foundfeats = False
#            negm = NEG_FEATS.match(token)
#            if negm:
#                negfeats, counts = negm.groups()
#                print("Negative match: {}, {}".format(negfeats, counts))
#                continue
            # separate features if any
            m = FORM_FEATS.match(token)
            if not m:
                print("No form/feats match for {}".format(tokens))
            tok, feats = m.groups()
            if feats:
                foundfeats = True
                features.append(FeatStruct(feats))
                tokens[index] = tok
            elif hasfeats:
                features.append(False)
            if not head:
                # Head not set yet
                if '_' in tok or foundfeats:
                    head_index = index
                    head = tok
        if not head:
            # Still no head found; it's just the first token
            head = tokens[0]
            head_index = 0
        tgroups = None
        if target and trans_strings:
            tgroups = []
            for tstring in trans_strings:
                tgroup, tagr, alg, tc = Group.from_string(tstring, target, trans_strings=None, trans=True,
                                                          n_src_tokens=len(tokens))
                tattribs = {'agr': tagr}
                if alg:
                    tattribs['align'] = alg
                if tc:
                    tattribs['count'] = tc
                tgroups.append((tgroup, tattribs))
        g = Group(tokens, head_index=head_index, head=head, features=features, agr=within_agrs,
                  name=Group.make_name(name_toks), count=count)
        if target and not trans:
            g.trans = tgroups
        language.add_group(g)
#        if trans_agrs:
#            trans_agrs = tuple(trans_agrs)
        return g, trans_agrs, alignment, trans_count

    ### Translations

    ## Alignments: position correspondences, agreement constraints
    ## አድርጎ አያውቅም -> godhe hin beeku
    ## a: {positions: (1, 2),
    ##     agreements: {gen: gen},
    ##     featmaps: {((pers, 2), (num, 2)): ((pers, 3), (num, 2))}
    ##     }

#    def add_alignment(self, trans):
#        pass

    @staticmethod
    def sort_trans(translations):
        """Sort translations by their translation frequency. translations is a list of pairs: group, feature dict."""
        translations.sort(key=lambda x: x[1].get('count', 0), reverse=True)

class MorphoSyn(Entry):
    """Within-language patterns that modify morphology and can delete words on the basis of the occurrence of other words or features."""

    def __init__(self, language, name=None, pattern=None):
        """pattern and change are strings, which get expanded at initialization.
        direction = True is left-to-right matching, False right-to-left matching.
        """
        name = name or MorphoSyn.make_name(pattern)
        Entry.__init__(self, name, language)
        self.direction = True
        # This also sets self.agr, self.del_indices, self.featmod; may also set direction
        self.pattern = self.expand(pattern)

    @staticmethod
    def make_name(pattern):
        """Pattern is a string."""
        return "{{ " + pattern + " }}"

    def is_ambig(self):
        """Is this an optional transformation; that is, is the sentence it succeeds on syntactically ambiguous?"""
        return self.name[0] == '*'

    def is_not_preferred(self):
        """For ambiguous sentences, whether the version to be modified syntactically is not preferred over the non-modified
        version. '**' means not preferred."""
        return self.name.startswith('**')

    def expand(self, pattern):
        """
        Pattern is a string consisting of elements separated by MS_ATTRIB_SEP.
        The first element is the actual pattern, which consists of pattern elements
        separated by PATTERN_SEP. A pattern element may be
        - a word, set of words, or category with or without a FeatStruct
        - a FeatStruct only
        - a gap of some range of words (<l-h> or <g>, where l is minimum, h is maximum and g is exact gap)
          [not yet implemented]
        Other elements are attributes, either agreement, deletion, or feature modification.
        """
        # For now, just split the string into a list of items.
        pattern = pattern.split(MS_ATTRIB_SEP)
        # Actual pattern
        tokens = pattern[0].strip()
        # Attributes: agreement, delete, swap, add
        attribs = pattern[1:]
        self.agr = None
        self.del_indices = []
        self.add_items = []
        self.swap_indices = []
        self.failif = None
        self.featmod = []
        # Wordform token (no features) near left end of pattern (for left-to-right direction)
        self.head_index = -1
        # Expand attributes
        for attrib in attribs:
            attrib = attrib.strip()
            # Within pattern feature agreement
            match = MS_AGR.match(attrib)
            if match:
                if self.agr:
                    print("Only one agreement constraint allowed!")
                    continue
                srci, trgi, feats = match.groups()
                feat_pairs = []
                for f in feats.split(WITHIN_ATTRIB_SEP):
                    f = f.strip()
                    if ':' in f:
                        f1, f2 = f.split(':')
                        feat_pairs.append((f1, f2))
                    else:
                        feat_pairs.append((f, f))
                self.agr = int(srci), int(trgi), feat_pairs
                continue
            # Indices of pattern elements to be marked for deletion
            match = MS_DELETE.match(attrib)
            if match:
                del_string = match.groups()[0]
                for d in del_string.split():
                    self.del_indices.append(int(d))
                continue
            match = MS_ADD.match(attrib)
            if match:
                add_string = match.groups()[0].split(',')
                for item in add_string:
                    add_index, add_item = item.split()
                    add_index = int(add_index)
                    self.add_items.append((add_index, add_item))
                continue
            match = MS_SWAP.match(attrib)
            if match:
                swap_indices = [int(i) for i in match.groups()[0].split()]
                self.swap_indices = swap_indices
                continue
            match = MS_FAILIF.match(attrib)
            if match:
                self.failif = match.groups()[0]
#                print("Found failif {} for {}".format(self.failif, self))
                continue
            # Index of pattern elements whose features are to be modified
            match = MS_FEATMOD.match(attrib)
            if match:
                fm_index, fm_feats = match.groups()
                self.featmod.append((int(fm_index), FeatStruct(fm_feats)))
                continue
            print("Something wrong with MS attribute {}".format(attrib))
        p = []
        for index, item in enumerate(tokens.split(MS_PATTERN_SEP)):
            negmatch = MS_NEG_FEATS.match(item)
            if negmatch:
                negfeats = negmatch.groups()[0]
                print("Found negative match {}".format(negfeats))
            else:
                forms, feats = MS_FORM_FEATS.match(item).groups()
                if feats:
                    feats = FeatStruct(feats)
                forms = [f.strip() for f in forms.split(FORMALT_SEP) if f]
                if not feats and self.head_index == -1:
                    self.head_index = index
                p.append((forms, feats))
        return p

    def pattern_length(self):
        return len(self.pattern)

    def apply(self, sentence, ambig=False, verbosity=0):
        """Apply the MorphoSyn pattern to the sentence if there is at least one match on some portion.
        2015.10.17: if ambig is True and this is an "ambiguous" MorphoSyn, copy the sentence
        before enforcing constraints.
        2015.10.20: constraints can be applied either to sentence or its copy (in altsyns list)
        """
        if verbosity:
            print("Attempting to apply {} to {}".format(self, sentence))
        matches = self.match(sentence, verbosity=verbosity)
        s = sentence
        if matches:
            if ambig and self.is_ambig():
                # Copy the sentence as an altsyn
                copy = sentence.copy()
                if self.is_not_preferred():
                    s = copy
            for match in matches:
                start, end, elements = match
                s.morphosyns.append((self, start, end))
                # Change either the sentence or the latest altsyn copy
                if verbosity:
                    print(" Match {}".format(match))
                self.enforce_constraints(match, verbosity=verbosity)
                self.insert_match(match, s, verbosity=verbosity)
            return True
        return False

    @staticmethod
    def del_token(token):
        return token[0] == '~'

    def match(self, sentence, verbosity=0):
        """
        Match sentence, a list of pairs of words and their analyses, against the MorphoSyn's pattern.
        Match records the index of a matching analysis within the list of analyses for a given
        sentence word.
        """
        results = []
        if verbosity:
            print("{} matching {}".format(self, sentence))
        if self.direction:
            # Left-to-right; index of item within the pattern
            pindex = 0
            # Index of sentence token where successful matching starts
            mindex = -1
            result = []
            for sindex, (stoken, sanals) in enumerate(sentence.analyses):
                if MorphoSyn.del_token(stoken):
                    continue
                # Check next whether this is a FAILIF Morphosysn that should fail because of what
                # MorphoSyns have already succeeded for the sentence
                if self.failif:
                    failed = False
                    for ms, start, end in sentence.morphosyns:
                        if ms.name.startswith(self.failif) and start <= sindex <= end:
                            print("{} fails because {} has already succeeded".format(self, ms))
                            failed = True
                            break
                    if failed:
                        continue
                # sentence.analyses consists of pairs of word tokens and a list of analysis dicts
                match = self.match_item(stoken, sanals, pindex, verbosity=verbosity)
                if match:
                    result.append(match)
#                    print("Match result {}".format(result))
                    # Is this the end of the pattern? If so, succeed.
                    if self.pattern_length() == pindex + 1:
                        print("MS {} tuvo éxito con resultado {}".format(self, result))
                        if mindex < 0:
                            mindex = sindex
                        results.append((mindex, sindex+1, result))
                        mindex = -1
                        pindex = 0
                        result = []
#                        return (mindex, sindex+1, result)
                    else:
                        # Otherwise move forward in the pattern
                        pindex += 1
                        if mindex < 0:
                            # Start of matching
                            mindex = sindex
                else:
                    # Start over
                    mindex = -1
                    pindex = 0
                    result = []
            if results:
                return results
            return False
        return False

    def match_item(self, stoken, sanals, pindex, verbosity=0):
        """Match a sentence item against a pattern item."""
        pforms, pfeats = self.pattern[pindex]
        if verbosity:
            print("  Matching {}:{} against {}:{}".format(stoken, sanals, pforms, pfeats.__repr__()))
        # No FS to match
        if not pfeats:
            return self.match_token(stoken, sanals, pforms, verbosity=verbosity)
        else:
            if not sanals:
                # No morphological analyses for sentence item; fail
                if verbosity:
                    print("No Feats, match item failed")
                return False
            # pattern FS must match features in one or more anals; record the results in
            # last corresponding to the list of anals in sentence
            anal_matches = []
            for sanal in sanals:
                anal_matches.append(self.match_anal(stoken, sanal, pforms, pfeats, verbosity=verbosity))
            if any(anal_matches):
                return [stoken, anal_matches]
        if verbosity:
            print("Match item failed")
        return False

    def match_token(self, stoken, sanals, pforms, verbosity=0):
        """Match the word or roots in a sentence against the set of forms in a pattern item."""
        if verbosity:
            print("Matching sentence token {} and analyses {} against pattern forms {}".format(stoken, sanals, pforms))
        if any([stoken == f for f in pforms]):
            # Do any of the pattern items match the sentence word?
            if verbosity:
                print(" Succeeded on token")
            return [stoken, False]
        # Do any of the pattern items match a root in any sentence item analysis?
        matched_anals = []
        for anal in sanals:
            root = anal['root']
            if any([root == f for f in pforms]):
                matched_anals.append(anal['features'])
            else:
                matched_anals.append(False)
        if any(matched_anals):
            if verbosity:
                print("Succeeded on root")
            return [stoken, matched_anals]
        return False

    def match_anal(self, stoken, sanal, pforms, pfeats, verbosity=0):
        """Match the sentence analysis against pforms and pfeats in a pattern.
        sanal is either a dict or a pair (root, features)."""
        if isinstance(sanal, dict):
            sfeats = sanal.get('features')
            sroot = sanal.get('root')
        else:
            sroot, sfeats = sanal
        if verbosity:
            s = "Attempting to match pattern forms {} and feats {} against sentence item root {} and feats {}"
            print(s.format(pforms, pfeats.__repr__(), sroot, sfeats.__repr__()))
        if not pforms or any([sroot == f for f in pforms]):
            if verbosity:
                print(" Root matched")
            # root matches
            u = simple_unify(sfeats, pfeats)
            if u != 'fail':
                if verbosity:
                    print(" Feats matched")
                # result could be frozen if nothing changed; we need an unfrozen FS for later changes
                return u.unfreeze()
        if verbosity:
            print(" Failed")
        return False

    def enforce_constraints(self, match, verbosity=0):
        """If there is an agreement contraint, modify the match element features to reflect it.
        Works by mutating the features in match.
        If there are deletion constraints, prefix * to the relevant tokens.
        """
#        if verbosity:
        print(" Enforcing constraints for match {}".format(match))
        start, end, elements = match
        if self.agr:
            srci, trgi, feats = self.agr
            src_elem = elements[srci]
            trg_elem = elements[trgi]
            if verbosity:
                print("Enforcing agreement on features {} from {} to {}".format(feats, src_elem, trg_elem))
            src_tok, src_feats_list = src_elem
            trg_tok, trg_feats_list = trg_elem
            for tf_index, trg_feats in enumerate(trg_feats_list):
                if not trg_feats:
                    # target features could be False
                    continue
#                print("trg_feats {}, frozen? {}".format(trg_feats.__repr__(), trg_feats.frozen()))
                # Because it may be mutated, use a copy of trg_feats
#                trg_feats1 = trg_feats.copy()
#                changed = False
                for src_feats in src_feats_list:
                    if src_feats:
                        # source features could be False
                        # Force target to agree with source on feature pairs
                        src_feats.agree(trg_feats, feats, force=True)
#                        changed = True
#            a = src_feats.agree(trg_feats, feats, force=True)
                        if verbosity:
                            print("Result of agreement: {}".format(trg_feats.__repr__()))
                # Replace original feats with copy
#                if changed:
#                    print("Feature {} replaced with copy".format(trg_feats.__repr__()))
#                    trg_feats_list[tf_index] = trg_feats1
        if self.del_indices:
            for i in self.del_indices:
                if verbosity:
                    print("Recording deletion for match element {}".format(elements[i]))
                elements[i][0] = '~' + elements[i][0]
        if self.add_items:
            print("Warning: Adding items in Morphosyn not yet implemented!")
#            for i, item in self.add_items:
#                print("Adding item {} in position {}".format(item, i))
        if self.swap_indices:
            i1, i2 = self.swap_indices
            elements[i1], elements[i2] = elements[i2], elements[i1]
            
        if self.featmod:
            # Modify features in indexed element
            for fm_index, fm_feats in self.featmod:
                elem = elements[fm_index]
                feats_list = elem[1]
                if not feats_list:
                    elem[1] = [fm_feats.copy()]
                else:
                    for index, feats in enumerate(feats_list):
                        if isinstance(feats, FeatStruct):
#                    print("Updating feat {} with fm_feats {}".format(feats.__repr__(), fm_feats.__repr__()))
#                    feats1 = feats.copy()
#                    print("Feature {} replaced with copy".format(feats.__repr__()))
#                    print("Modifying features {}, {}, {}".format(elem, feats.__repr__(), fm_feats.__repr__()))
                            feats.update_inside(fm_feats)
#                    feats_list[index] = feats1
#                    print("Feature {} after update".format(feats.__repr__()))

    def insert_match(self, match, sentence, verbosity=0):
        """Replace matched portion of sentence with elements in match.
        Works by mutating sentence elements (tokens and analyses).
        """
        if verbosity:
            print(" Inserting match {}".format(match))
        start, end, m_elements = match
        # start and end are indices within the sentence; some may have been
        # ignored within the pattern during matching
        m_index = 0
        # Swap sentence.analyses and tokens elements if there are swap_indices in the MS
        # Note: this only works if there are no other constraints to enforce.
        if self.swap_indices:
            mstart, mend = self.swap_indices
            sstart, send = start+mstart, start+mend
            sentence.analyses[sstart], sentence.analyses[send] = sentence.analyses[send], sentence.analyses[sstart]
            sentence.tokens[sstart], sentence.tokens[send] = sentence.tokens[send], sentence.tokens[sstart]
        else:
            for s_elem in sentence.analyses[start:end]:
                s_token = s_elem[0]
                if MorphoSyn.del_token(s_token):
                    # Skip this sentence element; don't increment m_index
                    continue
                m_elem = m_elements[m_index]
                m_index += 1
                # Replace the token (could have * now)
                s_elem[0] = m_elem[0]
                # Replace the features if match element has any
                m_feats_list = m_elem[1]
                s_anals = s_elem[1]
                new_s_anals = []
                if m_feats_list:
                    if not s_anals:
                        new_s_anals = [{'features': mfl, 'root': s_token} for mfl in m_feats_list]
                    for m_feats, s_anal in zip(m_feats_list, s_anals):
                        if not m_feats:
                            # This anal failed to match pattern; filter it out
                            continue
                        else:
                            s_feats = s_anal['features']
                            if s_feats != m_feats:
                                # Replace sentence features with match features if something
                                # has changed
                                s_anal['features'] = m_feats
                            new_s_anals.append(s_anal)
                s_elem[1] = new_s_anals

class EntryError(Exception):
    '''Class for errors encountered when attempting to update an entry.'''

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
    
