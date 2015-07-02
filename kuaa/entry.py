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
# 2015.06.07
# -- This is no longer true. Unanalyzed heads can be strings without '_' (I think...).
# 2015.06.08...
# -- Morphosyn class: patterns that relate syntax to morphology, by modifying FeatStructs
#    in word analyses and deleting free grammatical morphemes that trigger the changes.

import copy, itertools
import yaml
import re

from kuaa.morphology.fs import *

## Group files
LEXEME_CHAR = '_'
CAT_CHAR = '$'
ATTRIB_SEP = ';'
WITHIN_ATTRIB_SEP = ','
## Regular expressions for reading groups from text files
# non-empty form string followed by possibly empty FS string
FORM_FEATS = re.compile("([$<'?\-\w]+)\s*((?:\[.+\])?)$")
HEAD = re.compile("\s*\^\s*([<'\w]+)\s+(\d)\s*$")
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
MS_AGR = re.compile("\s*(\d)\s*=>\s*(\d)\s*(.+)$")
MS_DELETE = re.compile("\s*//\s*(.+)$")
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
            # separate features if any
            m = FORM_FEATS.match(token)
            if not m:
                print("No form/feats match for {}".format(tokens))
            tok, feats = FORM_FEATS.match(token).groups()
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
                tgroup, tg, alg, tc = Group.from_string(tstring, target, trans_strings=None, trans=True)
                tattribs = {'agr': tg}
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
        return g, trans_agrs, alignment, trans_count

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
        tokens = pattern[0].strip()
        # Attributes: agreement, delete
        attribs = pattern[1:]
        self.agr = None
        self.del_indices = []
        self.featmod = None
        for attrib in attribs:
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
            # Index of pattern elements whose features are to be modified
            match = MS_FEATMOD.match(attrib)
            if match:
                fm_index, fm_feats = match.groups()
                self.featmod = int(fm_index), FeatStruct(fm_feats)
                continue
            print("Something wrong with attribute {}".format(attrib))
        p = []
        for item in tokens.split(MS_PATTERN_SEP):
            forms, feats = MS_FORM_FEATS.match(item).groups()
            if feats:
                feats = FeatStruct(feats)
            forms = [f.strip() for f in forms.split(FORMALT_SEP) if f]
            p.append((forms, feats))
        return p

    def pattern_length(self):
        return len(self.pattern)

    def apply(self, sentence, verbosity=0):
        """Apply the MorphoSyn pattern to the sentence if there is a match on some portion."""
        if verbosity:
            print("Attempting to apply {} to {}".format(self, sentence))
        match = self.match(sentence, verbosity=verbosity)
        if match:
            self.enforce_constraints(match, verbosity=verbosity)
            self.insert_match(match, sentence, verbosity=verbosity)

    @staticmethod
    def del_token(token):
        return token[0] == '~'

    def match(self, sentence, verbosity=0):
        """
        Match sentence, a list of pairs of words and their analyses, against the MorphoSyn's pattern.
        Match records the index of a matching analysis within the list of analyses for a given
        sentence word.
        """
        if verbosity:
            print("{} matching {}".format(self, sentence))
        if self.direction:
            pindex = 0
            # Index of sentence token where successful matching starts
            mindex = -1
            result = []
            # left-to-right
            for sindex, (stoken, sanals) in enumerate(sentence.analyses):
                if MorphoSyn.del_token(stoken):
                    continue
                # sentence.analyses consists of pairs of word tokens and a list of analysis dicts
                match = self.match_item(stoken, sanals, pindex, verbosity=verbosity)
                if match:
                    result.append(match)
                    # Is this the end of the pattern? If so, succeed.
                    if self.pattern_length() == pindex + 1:
                        return (mindex, sindex+1, result)
                    # Otherwise move forward in the pattern
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

    def match_item(self, stoken, sanals, pindex, verbosity=0):
        """Match a sentence item against a pattern item."""
        pforms, pfeats = self.pattern[pindex]
        if verbosity:
            print("Matching {}:{} against {}:{}".format(stoken, sanals, pforms, pfeats.__repr__()))
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
            # Do any of th pattern items match the sentence word?
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
        start, end, elements = match
        if self.agr:
            srci, trgi, feats = self.agr
            src_elem = elements[srci]
            trg_elem = elements[trgi]
            if verbosity:
                print("Enforcing agreement on features {} from {} to {}".format(feats, src_elem, trg_elem))
            src_tok, src_feats_list = src_elem
            trg_tok, trg_feats_list = trg_elem
            for trg_feats in trg_feats_list:
                if not trg_feats:
                    # target features could be False
                    continue
#                print("trg_feats {}, frozen? {}".format(trg_feats.__repr__(), trg_feats.frozen()))
                for src_feats in src_feats_list:
                    if src_feats:
                        # source features could be False
                        # Force target to agree with source on feature pairs
                        src_feats.agree(trg_feats, feats, force=True)
#            a = src_feats.agree(trg_feats, feats, force=True)
                        if verbosity:
                            print("Result of agreement: {}".format(trg_feats.__repr__()))
        if self.del_indices:
            for i in self.del_indices:
                if verbosity:
                    print("Recording deletion for match element {}".format(elements[i]))
                elements[i][0] = '~' + elements[i][0]
        if self.featmod:
            # Modify features in indexed element
            fm_index, fm_feats = self.featmod
            elem = elements[fm_index]
            feats_list = elem[1]
            for feats in feats_list:
#                print("Updating feat{} with fm_feats {}".format(feats.__repr__(), fm_feats.__repr__()))
                feats.update_inside(fm_feats)

    def insert_match(self, match, sentence, verbosity=0):
        """Replace matched portion of sentence with elements in match.
        Works by mutating sentence elements (tokens and analyses).
        """
        start, end, m_elements = match
        # start and end are indices with the the sentence; some may have been
        # ignore within the pattern during matching
        m_index = 0
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
    
