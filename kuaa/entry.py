#   MDT/TGS
#     Entry interface
#     Group: basic lexical unit
#     Morphosyn: pattern specifying source-to-target morphosyntactic transformation
#     Join: pattern specifying joining sequence of SolSegs
#
########################################################################
#
#   This file is part of the PLoGS project
#   for parsing, generation, translation, and computer-assisted
#   human translation.
#
#   Copyleft 2014, 2015, 2016, 2017, 2018
#      HLTDI, PLoGS <gasser@indiana.edu>
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
# 2016.2.23
# -- Morphosyns have a further type of ambiguity, exemplified by "la casa": match copies
#    sentence only if there is a set of features that fails to match for a word, and
#    the matching features are deleted in the copy.
# 2016.3.1
# -- Tokens that are deleted in Morphosyns can be assigned to nodes other than the next
#    one, as in <la [adj] [n]>
# 2016.3.6
# -- Groups can include tokens that are deleted in MorphoSyns, e.g., <por (la) noche>
#    (with no indication in the group that they are deleted).
# 2016.5.25
# -- In group matching, once a non-head group token is matched, it doesn't tolerate a gap
#    before matching again.
# 2017.4.10
# -- Fixed a serious bug in MS matching, which came up when two successive sentence elements
#    matched the same pattern element, causing <V them> to fail for "I will see them".
# -- Fixed element swapping in MS application, which wasn't working where there were deleted elements.
# 2017.4.24
# -- Fixed matching for Morphosyn and Group with external tagger. Basically this involves accepting
#    FSSets for features in addition to simple FeatStructs. Later FSSet should be the only possibility.
# 2017.06.22
# -- Character joining items in phrases and numerals is now ~ instead of _.
# 2018.02
# -- Simplification of matching words with categories in groups.
# 2018.03
# -- Gaps (position in group, minimum/maximum tokens) now need to specified to be allowed.
# 2018.08
# -- Fixed ir/ser confusion in morphosyns (I think). So <ser_v adj> now matches "fue malo".
# 2018.10
# -- Join: patterns to join SolSegs into SuperSegs. Later share more in Entry (between
#    Group, Morphosyn, Join).

import copy, itertools
import yaml
import re

from kuaa.morphology.fs import *
from kuaa.morphology.semiring import FSSet

## Group files
LEXEME_CHAR = '_'
CAT_CHAR = '$'
SET_CHAR = '$$'
SPEC_CHAR = '%'
ATTRIB_SEP = ';'
WITHIN_ATTRIB_SEP = ','
## Regular expressions for reading groups from text files
# non-empty form string followed by possibly empty FS string
FORM_FEATS = re.compile("([$%~<'`^*¿?¡!|()\-\w̃]+)\s*((?:\[.+\])?)$")
# !FS(#1-#2), representing a sequence of #1 to #2 negative FS matches
NEG_FEATS = re.compile("\s*!(\[.+\])(\(\d-\d\))$")
# fail if category or feature matches an item that otherwise fails (before cat token)
FAILIF = re.compile("\s*!(.+)$")
## fail if category matches an item that otherwise fails
#FAILIF_CAT = re.compile("\s*(!\$\w+)$")
HEAD = re.compile("\s*\^\s*([~<'¿?¡!|\-\w]+)\s+(\d)\s*$")
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
## Group can have no gaps between elements: -X-
#NO_GAP = re.compile("\s*-X-\s*$")
# Comments for group
COMMENT = re.compile("\s*//\s*(.+)$")
# Intervening elements: position and minimum/maximum number
# (2,-3): after element 2, up to 3 elements
# (1,1-2): after element 1, 1 or 2 elements
INTERVENE = re.compile("\s*\((\d),(\d?)-(\d?)\)$")

## MorphoSyn regex
# Separates elements of MorphoSyn pattern
MS_PATTERN_SEP = ' '
# Separates form alternatives in MorphSyn pattern
FORMALT_SEP = '|'
MS_ATTRIB_SEP = ';'
AMBIG_CHAR = '*'
DISAMBIG_CHAR = '%'
# possibly empty form string followed by zero or more FS strings, for MorphoSyn pattern
# ^prefix means this is head
MS_FORM_FEATS = re.compile("\s*(\^?)([$%<'|\w¿¡?!]*)\s*((?:\*?\[.+\])*)$")
# negative features: ![] with only features catpured
MS_NEG_FEATS = re.compile("\s*!(\[.+\])$")
MS_AGR = re.compile("\s*(\d)\s*=>\s*(\d)\s*(.+)$")
MS_DELETE = re.compile("\s*//\s*(.+)$")
MS_ADD = re.compile("\s*\+\+\s*(.+)$")
MS_SWAP = re.compile("\s*><\s*(.+)$")
MS_FAILIF = re.compile("\s*FAILIF\s*(.+)$")
# digit -> [FS], all obligatory
MS_FEATMOD = re.compile("\s*(\d)\s*->\s*(\[.+\])$")
MS_OPT = re.compile("\s*\((.+)\)$")

class Entry:
    """Superclass for Group, Morphosyn and possibly other lexical classes."""

    ID = 1
    dflt_dep = 'dflt'
    
    def __init__(self, name, language, id=0, trans=None, comment=''):
        """Initialize name and basic features: language, trans, count, id."""
        self.name = name
        self.language = language
        self.trans = trans
        self.count = 1
        self.comment = comment
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
    def is_special(name):
        """Is this a symbol for a special category, like numerals?"""
        return name and name[0] == SPEC_CHAR

    @staticmethod
    def special_prefix(name, check=False):
        """If this is a special token, return its prefix (what precedes ~)."""
        if not check or Entry.is_special(name):
            return name.split('~')[0]
        return ''

    @staticmethod
    def match_special(stoken, ptokens):
        """Does any MS pattern token (%C, %N, etc.) match the sentence token?"""
        prefix = Entry.special_prefix(stoken, check=True)
        return prefix and any([prefix == ptoken for ptoken in ptokens])

    @staticmethod
    def match_special1(stoken, ptoken):
        """Does Join or MS pattern token match sentence token?"""
        prefix = Entry.special_prefix(stoken, check=True)
        return prefix and prefix == ptoken
        
#    @staticmethod
#    def is_negative(name):
#        """Is this a symbol for a negative feature or category?"""
#        return name and name[0] == '!'

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
        for the target language, no lo>nger a dict with language abbrev keys."""
        
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

    def apply(self, obj, ambig=False, verbosity=0, terse=False):
        """Apply this entry to a Sentence or Superseg."""
        raise NotImplementedError()

class Group(Entry):
    """Primitive multi-word expression. Default is a head with unlabeled dependencies
    to all other tokens and translations, including alignments, to one or more
    other languages."""

    def __init__(self, tokens, head_index=-1, head='', language=None, name='',
                 features=None, agr=None, trans=None, count=0, failif=None,
                 string=None, trans_strings=None, cat='', comment='', intervening=None):
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
        else:
            self.head = tokens[head_index]
            self.head_index = head_index
            
        name = name or Group.make_name(tokens)
        Entry.__init__(self, name, language, trans=trans, comment=comment)
        # POS, 'misc', or other
        self.cat = cat
        # The string in a .grp file encoding this Group
        self.string = string
        # The string in a .grp file encoding translations of this Group
        self.trans_strings = trans_strings
        self.capitalized = self.head.istitle()
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
#        # Whether there can be no gap between the tokens
#        self.nogap = nogap
        # Intervening tokens; if not None, a pair of the form (position, (min, max))
        self.intervening = intervening
        # Distance back from sentence node matching head to start in matching group
        self.snode_start = 0
        # If not None, an index where a failif item occurs and either a category a feature structure to match
        self.failif = failif
        # Whether to print out verbose messages
        self.debug = False
        if self.head_index > 0:
            # What was this for? Why does it matter whether any nodes before the head are cats?
#             and not any([Group.is_cat(t) for t in self.tokens[:self.head_index]]):
            self.snode_start = -self.head_index

    def __repr__(self):
        """Print name."""
        return '{}:{}'.format(self.name, self.id)

    @staticmethod
    def make_name(tokens):
        """Each token is either a string or a (string, feat_dict) pair. In name, they're separated by '.'."""
        return '.'.join(tokens)

    @staticmethod
    def get_key(name):
        """Get a group's key into Language.groups from its name or print name."""
        return name.split('.')[0].split('[')[0]

    @staticmethod
    def make_gpair_name(groups):
        """Create a string name for one or two merged group nodes. Each is represented
        by a pair: (group_name, index).
        """
        string = Group.make_node_name(groups[0][0], groups[0][1])
        if len(groups) == 2:
            string += "++{}".format(Group.make_node_name(groups[1][0], groups[1][1]))
        return string

    def make_node_name(group, index):
        """Create a string name for a group node, given group name and index."""
        return "{}:{}".format(group.name, index)

    def priority(self):
        """Returns a value that is used in sorting the groups associated with a particular key.
        Groups with more tokens and more features have priority."""
        featscore = .3 * sum([len(f) for f in self.features if f]) if self.features else 0.0
        return len(self.tokens) + featscore

    # Group properties

    def get_cat_indices(self):
        """Return a list of gnode positions for categories."""
        return [index for index, token in enumerate(self.tokens) if Entry.is_cat(token)]

    def get_nfeatures(self):
        """Sum of the features for all group tokens."""
        if not self.features:
            return 0
        return sum([(len(fs) if fs else 0) for fs in self.features])

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
        """Convert a dict to a Group object."""
        tokens = d['words']
        features = d.get('features')
        agr = d.get('agr')
        name = d.get('name', '')
        trans = d.get('trans')
        p = Group(tokens, head=head, language=language, features=features,
                  agr=agr, name=name, trans=trans)
        return p

    def to_string(self):
        """Convert the group to a string, writable to a file."""
        # First line:
        #   ** tokens ; ^ head head_index
        tokens = []
        feats = self.features
        if feats and any(feats):
            for tok, feat in zip(self.tokens, feats):
                if feat:
                    tokens.append("{}{}".format(tok, feat.__repr__()))
                else:
                    tokens.append(tok)
        else:
            tokens = self.tokens[:]
        failif = self.failif
        if failif:
            failindex, failcats = failif
            failcats = "!{}".format('|'.join(failcats))
            tokens[failindex:failindex] = [failcats]
        string = "** {} ; ^ {} {}\n".format(' '.join(tokens), self.head, self.head_index)
        # Remaining lines:
        #   ->target tokens ; || k, l ; m==n s:t,s:t ; u=v w,x ; -X-
        for trans in self.trans:
            tgroup, tdict = trans
            string += "->{} {}".format(tgroup.language.abbrev, ' '.join(tgroup.tokens))
            
            string += "\n"
        #->amh $n[cs=acc] Tmd_v[as=smp,vc=smp] ; || 1, 0 ; 0==1 tm:tm,rel:rel,sb:sb,ob:ob,neg:neg,ax:ax
        return string

    def match_segments(self, segments, startindex, verbosity=1):
        """Attempt to match a sequence of Segs, starting at start_index, returning the match or False."""
        if verbosity:
            print("Matching {} against {} starting from {}".format(self, segments, startindex))
        matches = []
        matched = True
        patlength = len(self.tokens)
        patindex = 0
        segindex = startindex
        while matched and patindex < patlength:
            patelem = self.tokens[patindex]
            patfeats = self.features[patindex]
            segment = segments[segindex]
            match = segment.match_group_tok(patelem, patfeats, verbosity=verbosity)
            if match:
                if verbosity:
                    print(" {} matched {} with match {}".format(segment, self, match))
                matches.append((segindex, segment, match))
                segindex += 1
                patindex += 1
            else:
                return False
        if verbosity:
            print("{} matched segments {} starting from {}".format(self, segments, startindex))
        return self, matches

    def apply(self, superseg, verbosity=1):
        """Make changes specified in group to superseg containing segments matching it."""
        if verbosity:
            print("Applying {} to {}".format(self, superseg))
        segments = superseg.segments
        # Add translations
        translations = self.trans
        # Once this is set, don't change it (assume all translations involve the same ordering)
        ordered = False
        for tgroup, tfeats in translations:
            ttokens = tgroup.tokens
            ttokfeats = tgroup.features
            tpos = tgroup.pos
            print(" Trans group {}, tokens {}, pos {}, tokfeats {}".format(tgroup, ttokens, tpos, ttokfeats))
#            if tfeats and 'align' in tfeats:
            for tfkey, tfvalue in tfeats.items():
                print("  Constraint {}".format(tfkey))
                print("    {}".format(tfvalue))
                if tfkey == 'align':
                    if ordered:
                        print("   Already ordered")
                        continue
                    to_delete = []
                    sso = superseg.order
                    print("   Ordering {} for superseg order {}".format(tfvalue, sso))
                    sindex = 0
                    for gindex in tfvalue:
                        print("    sindex {}, gindex {}".format(sindex, gindex))
                        if gindex < 0:
                            # Delete this segment
                            print("    deleting {}".format(segments[sindex]))
                            to_delete.append(sindex)
                        else:
                            sindex += 1
                    for deli in to_delete:
                        sso.remove(deli)
                    ordered = True
                    print("    Updated superseg order {}".format(sso))
                    
        # Make source-target features agree
        # Make target-target features agree
        # Set order of segments (superseg.order)
        # Delete segments with no position from superseg.order
                    
#        for change in self.agree_changes:
#            seg1index, seg2index, feat1, feat2 = change
#            if verbosity:
#                print("  Must agree {} {} ; {} {}".format(seg1index, seg2index, feat1, feat2))
#            seg1 = segments[seg1index]
#            seg2 = segments[seg2index]
#            segfeats1 = seg1.get_thead_feats()
#            segfeats2 = seg2.get_thead_feats()
#            if verbosity:
#                print("  Seg1 {} feats {}, seg2 {} feats {}".format(seg1, segfeats1, seg2, segfeats2))
#        if self.targ_feats:
#            for segindex, addfeats in self.targ_feats:
#                # Add targfeats to feats in segindex Seg
#                segment = superseg.segments[segindex]
#                tfeats = segment.get_thead_feats()
#                print("Segment {}, thead {}, tfeats {}".format(segment, segment.thead, tfeats))
#                print("Adding features {} to targ features {}".format(addfeats.__repr__(), tfeats.__repr__()))
#                for ti, th in enumerate(segment.thead):
#                    tf = th[2]
#                    print("th {}".format(th))
#                    newtf = tf.unify_FS(addfeats)
#                    if newtf != 'fail':
#                        th[2] = newtf
#                print("New thead {}".format(segment.thead))
#        if self.segment_order:
#            if verbosity:
#                print("  Swap {}".format(self.segment_order))
#            i1, i2 = self.segment_order
#            sso = superseg.order
#            sso[i1], sso[i2] = sso[i2], sso[i1]
#            to_delete = []
#            for index in sso:
#                if index not in self.segment_order:
#                    to_delete.append(index)
#            for d in to_delete:
#                sso.remove(d)
#            if verbosity:
#                print("  Indices swapped {}".format(sso))

    def match_nodes(self, snodes, head_sindex, verbosity=0):
        """Attempt to match the group tokens (and features) with tokens from a sentence,
        returning the snode indices and root and unified features if any."""
        if verbosity > 1 or self.debug:
            print("Does {} match {} with head index {}".format(self, snodes, head_sindex))
        match_snodes = []
        last_sindex = -1
        last_cat = False
        # Start searching in sentence depending on where candidate head_sindex is
        snindex = head_sindex + self.snode_start
        if snindex < 0:
            # Start of group is before beginning of sentence
            return False
        matcheddel = False
        if self.failif:
            failfrom, failspec = self.failif
        for index, token in enumerate(self.tokens):
            # Whether there's a sentence node gap between this token and the last one that matched
            nodegap = 0
            # Whether a gap is permitted here.
            ingap = False
            gapmin = gapmax = 0
            if self.intervening and index == self.intervening[0]:
                ingap = True
                # Whether this is a position that permits a gap
                gapmin, gapmax = self.intervening[1]
            # Whether this token is the group head
            ishead = (index == self.head_index)
            # Whether this token is a category (starting with $)
            iscat = Entry.is_cat(token)
            match_snodes1 = []
            feats = self.features[index] if self.features else None
            if verbosity > 1 or self.debug:
                print(" Attempting to match {} in {}".format(token, self))
            tryfail = False
            if self.failif and index >= failfrom:
                tryfail = True
            matched = False
            # For each SNode starting with snindex...
            for node in snodes[snindex:]:
                if verbosity > 1 or self.debug:
                    fstring = "  Trying {}, token index {}, nodegap {} (gap max {})"
                    print(fstring.format(node, index, nodegap, gapmax))
                # If this snode is unknown, the group can't include it unless it's in a permitted gap
                if node.is_unk() and gapmax == 0:
                    if verbosity or self.debug:
                        print("  Node is unknown!")
                    break
                # Fail because gap is too long
                if nodegap > gapmax:
                    break
                # If there is a failif condition for the group and the position within the group is right,
                # see if we should fail here
                if tryfail:
                    negm = node.neg_match(failspec, debug=self.debug, verbosity=verbosity)
                    if negm:
                        break
                snode_indices = node.raw_indices
                snode_start, snode_end = snode_indices[0], snode_indices[-1]
                leftdel = None
                rightdel = None
                if node.left_delete:
                    leftdel = node.left_delete
                    matcheddel = False
                    for ld in leftdel:
                        if token == ld:
                            # Current group token matches left deleted sentence node token; advance to next group token
                            matcheddel = True
                            break
                    if matcheddel:
                        match_snodes1.append((node.index, None, token, False))
                        # Matched left deleted token; stop searching through snodes for match
                        break
                if node.right_delete:
                    rightdel = node.right_delete
                if ishead:
                    if self.debug:
                        print("   Matching head, node index {}, head sindex {}".format(node.index, head_sindex))
                    if node.index != head_sindex:
                        # Is there any way this could not fail??
                        return False
                    # This is the token corresponding to the group head
                    # If this is the sentence-initial node and token is capitalized, match with
                    # node's head capitalized.
                    node_verbosity = 0
                    if verbosity > 1 or self.debug:
                        node_verbosity = 2
                    if self.capitalized and head_sindex == 0:
                        if verbosity > 1 or self.debug:
                            print("    Matching capitalized group head with sentence-initial word")
                        node_match = node.match(token.lower(), feats, verbosity=node_verbosity)
                        # Capitalize the node's token if this succeeds
                        if node_match != False:
                            node.token = node.token.capitalize()
                    else:
                        if verbosity > 1 and self.debug:
                            print("    Matching token {} and feats [] against node {}".format(token, feats, node))
                        node_match = node.match(token, feats, verbosity=node_verbosity)
                    if node_match == False:
                        # This has to match, so fail now
                        if verbosity or self.debug:
                            print("   {} failed to find match for head token {} with node {}".format(self, token, node))
                        return False
                    else:
                        # If the last token was not a category, this has to follow immediately; if it doesn't fail
                        if index > 0 and not last_cat and last_sindex >=0 and nodegap:
                            if verbosity > 1 or self.debug:
                                fstring = " Group head token {} in sentence position {} doesn't follow last token at {}"
                                print(fstring.format(token, snode_indices, last_sindex))
                                print("   {} failed to match in token {}".format(self, token))
                            return False
                        match_snodes1.append((node.index, node_match, token, True))
                        if verbosity > 1 or self.debug:
                            fstring = " Group head {} matched node {} in {}, node index {}, last_sindex {}"
                            print(fstring.format(token, node, self, snode_indices, last_sindex))
                        last_sindex = snode_end
#                        if verbosity > 1 or self.debug:
#                            print("  Head matched already".format(node))
                        matched = True
                        snindex = node.index + 1
                        # Don't look further for an snode to match this token
                        break
                else:
                    # Match a group token that's not the head
                    node_match = node.match(token, feats, verbosity=verbosity, debug=self.debug)
                    if verbosity > 1 or self.debug:
                        print('  Node {} match {}:{}, {}:: {}'.format(node, token, index, feats, node_match))
                    if node_match != False:
                        if Entry.is_special(token):
                            token = node.token
                        match_snodes1.append((node.index, node_match, token, True))
                        if Group.is_cat(token):
                            last_cat = True
                        else:
                            last_cat = False
                        if verbosity or self.debug:
                            fstring = " Group token {} matched node {} in {}, node index {}, last_sindex {}"
                            print(fstring.format(token, node, self, snode_indices, last_sindex))
                        last_sindex = snode_end
                        if verbosity > 1 or self.debug:
                            print("  Matched node {}".format(node))
                        matched = True
                        snindex = node.index + 1
                        nodegap += 1
                        # Don't look further
                        break
                    elif match_snodes1:
                        # There's already at least one snode matching token, so don't tolerate another gap
                        break
                    else:
                        nodegap += 1
            if matcheddel:
                # Matched a left deleted element; move on to next group token
                if verbosity or self.debug:
                    print("  Matched left del; move on to next group token; {}".format(match_snodes1))
                match_snodes.append(match_snodes1)
                continue
            if not matched:
                if verbosity > 1 or self.debug:
                    print("  {} not matched; failed".format(token))
                return False
            else:
                match_snodes.append(match_snodes1)
        if verbosity or self.debug:
            print("Group {}, s_indices {}".format(self, match_snodes))
        return match_snodes

    @staticmethod
    def from_string(string, language, trans_strings=None, target=None, trans=False, n_src_tokens=1,
                    tstrings=None, cat='', posindex=0):
        """Convert a group string and (if trans is False) possibly a set of translation group strings
        to one or more groups. [trans=True means this is for a target-language Group.]"""
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
        failif = None
        count = 0
#        nogap = False
        intervening = None
        if '[' in string:
            hasfeats = True
            features = []
        else:
            hasfeats = False
        comment = ''
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
                continue
            match = INTERVENE.match(attrib)
            if match:
                position, i_min, i_max = match.groups()
                position = int(position)
                i_min = int(i_min) if i_min else 0
                i_max = int(i_max) if i_max else 5
#                print("Matched intervening: pos {}, min {}, max {}".format(position, i_min, i_max))
                intervening = position, (i_min, i_max)
                continue
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
#            match = NO_GAP.match(attrib)
#            if match:
#                nogap = True
#                continue
            match = COMMENT.match(attrib)
            if match:
                c = match.groups()[0]
                comment = c
                continue
            # Translation group
            if trans:
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
        realtokens = []
        for index, token in enumerate(tokens):
            foundfeats = False
#            negm = NEG_FEATS.match(token)
#            if negm:
#                negfeats, counts = negm.groups()
#                print("Negative match: {}, {}".format(negfeats, counts))
#                continue
            m = FAILIF.match(token)
            if m:
                failif_spec = m.groups()[0]
                # This could be a set of specs separated by '|'
                failif_specs = failif_spec.split('|')
                for findex, f_spec in enumerate(failif_specs):
                    # This is either a category (beginning with '$') or POS (just a string)
                    # or a feature structure
                    if '[' in f_spec:
                        # This is a feature structure that must fail to match
                        f_spec = FeatStruct(f_spec)
                        failif_specs[findex] = f_spec
                failif = (index, failif_specs)
                continue
            # separate features if any
            m = FORM_FEATS.match(token)
            if not m:
                print("No form/feats match for {}".format(tokens))
            tok, feats = m.groups()
            realtokens.append(tok)
            name_toks.append(token)
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
                                                          n_src_tokens=len(realtokens))
                tattribs = {'agr': tagr}
                if alg:
                    tattribs['align'] = alg
                if tc:
                    tattribs['count'] = tc
                tgroups.append((tgroup, tattribs))
        # Check to see whether a group with this name has already been created for language;
        # if so, use it
        gname = Group.make_name(name_toks)
        existing_group = language.get_group(gname, key=head)
        g = existing_group or Group(realtokens, head_index=head_index, head=head, features=features, agr=within_agrs,
                                    failif=failif, name=gname, count=count, string=string,
                                    trans_strings=tstrings, cat=cat, comment=comment, intervening=intervening)
        if target and not trans:
            g.trans = tgroups
        if not existing_group:
            language.add_group(g, posindex=posindex, cat=cat)
        return g, trans_agrs, alignment, trans_count

    ## Methods for creating additional Groups and modifying existing Groups

    @staticmethod
    def add_trans_default(tstring, language, cat, defaults=None):
        '''Augment tstring to include defaults for the given category.'''
        tlang, x, tgroup = tstring.partition(' ')
        defaults = defaults or language.group_defaults.get(cat)
        if defaults:
            for default in defaults:
                # Assume it's a translation default
                typ, addition = default
                if typ not in tgroup:
                    tgroup += " " + addition
        return tgroup
    
    @staticmethod
    def from_rawstring(string, language, cat, target=None, trans=False, n_src_tokens=1, tstrings=None):
        """Like from_string, except that it incorporates the default group translation features for this group class, along
        with any features that are specified."""
        trans_strings = []
        defaults = language.group_defaults.get(cat)
        if defaults:
            trans_strings = [Group.add_trans_default(tstring, language, cat, defaults=defaults) for tstring in tstrings]
        else:
            trans_strings = [t.partition(' ')[2] for t in tstrings]
        return Group.from_string(string, language, trans_strings=trans_strings, target=target,
                                 trans=trans, n_src_tokens=n_src_tokens, tstrings=tstrings, cat=cat)

    def add_trans(self, target=None, tstring=None, default=True, cat='v'):
        """Add translation in tstring to the group's translations."""
        if target and tstring:
            if default:
                tstring_plus = Group.add_trans_default(tstring, self.language, cat)
            else:
                tstring_plus = tstring
            tgroup, tagr, alg, tc = Group.from_string(tstring_plus, target, trans_strings=None, trans=True,
                                                      n_src_tokens=len(self.tokens), cat=cat)
            tattribs = {'agr': tagr}
            if alg:
                tattribs['align'] = alg
            if tc:
                tattribs['count'] = tc
            self.trans.append((tgroup, tattribs))
            self.trans_strings.append(tstring)

    def write(self, stream):
        """Write the group to stream."""
        print("** {}".format(self.string), file=stream)
        for tstring in self.trans_strings:
            print("->{}".format(tstring), file=stream)

    @staticmethod
    def write_groups(language, cat, groups=None, path=''):
        """Write the groups belonging to a given category to the file at path.
        If groups is None, use all of language's groups belonging to cat."""
        groups = groups or Group.get_cat_groups(language, cat)
        path = path or cat + '.grp'
        with open(path, 'w', encoding='utf8') as file:
            # First write the defaults for this category
            language.write_group_defaults(cat, file)
            for group in groups:
                group.write(file)

    @staticmethod
    def rewrite_groups(language, cat, groups=None):
        """Overwrite the groups file for cat with groups."""
        path = language.get_cat_group_file(cat)
        with open(path, 'w', encoding='utf8') as file:
            # First write the defaults for this category
            language.write_group_defaults(cat, file)
            for group in groups:
                group.write(file)

    @staticmethod
    def get_cat_groups(language, cat, filt=None):
        """Return all groups in language with category cat that satisfy filter function."""
        cat_groups = []
        for groups in language.groups.values():
            for group in filter(filt, groups):
                if group.cat == cat:
                    cat_groups.append(group)
        return cat_groups

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
        if len(translations) > 1:
            translations.sort(key=lambda x: x[1].get('count', 0), reverse=True)

class MorphoSyn(Entry):
    """Within-language patterns that modify morphology and can delete words on the basis of
    the occurrence of other words or features.
    """

    def __init__(self, language, name=None, pattern=None,
                 del_indices=None, swap_indices=None, add_items=None, featmod=None, failif=None, agr=None,
                 strict=None, expanded=False):
        """pattern and change are strings, which get expanded at initialization.
        direction = True is left-to-right matching, False right-to-left matching.
        """
        name = name or MorphoSyn.make_name(pattern)
        Entry.__init__(self, name, language)
        self.direction = True
        ## These will be set in expand()
        self.agr = agr
        self.del_indices = del_indices or []
        self.add_items = add_items or []
        self.swap_indices = swap_indices or []
        self.failif = failif
        self.featmod = featmod or []
        # dict of forms, features, with indices as keys, for optional elements
        self.optional = {}
        # Pattern indices of items that must not match
        self.neg_matches = []
        # Wordform token (no features) near left end of pattern (for left-to-right direction)
        self.head_index = -1
        # If there are optional features, additional morphosyns are created.
        self.optional_ms = []
        # For each item, whether the associated feature structure (if there is one) applies strictly to input.
        # This is filled in in expand()
        self.strict = strict
        # Expand unless this already happened (with optional form-feats)
        # This also sets self.agr, self.del_indices, self.featmod; may also set direction
        if not expanded:
            self.pattern = self.expand(pattern)
        else:
            self.pattern = pattern
        # Whether to print out verbose messages
        self.debug = False

    @staticmethod
    def make_name(pattern):
        """Pattern is a string."""
        return "{{ " + pattern + " }}"

    def is_ambig(self):
        """Is this an optional transformation; that is, is the sentence it succeeds on syntactically ambiguous?"""
        return self.name[0] == AMBIG_CHAR

    def is_not_preferred(self):
        """For ambiguous sentences, whether the version to be modified syntactically is not preferred over the non-modified
        version. '**' means not preferred."""
        return self.name.startswith('**')

    def is_feat_ambig(self):
        """For ambiguous patterns, whether the ambiguity depends on an
        alternate set of features that fails to match the morphosyn.
        """
        return '=' in self.name

    def is_disambig(self):
        """Whether this is an MS that disambiguates source words,
        rejecting analyses that don't match it if it matches one analysis.
        """
        return self.name[0] == DISAMBIG_CHAR

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
                self.agr = [int(srci), int(trgi), feat_pairs]
                continue
            # Indices of pattern elements to be marked for deletion (and optionally their "target" indices)
            match = MS_DELETE.match(attrib)
            if match:
                del_string = match.groups()[0]
#                print("{} matched delete: {} :: {}".format(self, attrib, del_string))
                for d in del_string.split():
                    d1, x, d2 = d.partition(':')
                    d1 = int(d1)
                    d2 = int(d2) if d2 else -1
                    self.del_indices.append([d1, d2])
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
                self.swap_indices =  [int(i) for i in match.groups()[0].split()]
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
                self.featmod.append([int(fm_index), FeatStruct(fm_feats)])
                continue
            print("Something wrong with MS attribute {}".format(attrib))
        p = []
        items = tokens.split(MS_PATTERN_SEP)
        self.strict = [False] * len(items)
        for index, item in enumerate(items):
            forms = None
            feats = None
            optmatch = MS_OPT.match(item)
            if optmatch:
                opt = optmatch.groups()[0]
#                print("Found optional match {}".format(opt))
                item = opt
            negmatch = MS_NEG_FEATS.match(item)
            if negmatch:
                negfeats = negmatch.groups()[0]
                self.neg_matches.append(index)
                negfeats = FeatStruct(negfeats)
                forms = []
                feats = negfeats
#                p.append(([], negfeats))
            else:
                match = MS_FORM_FEATS.match(item)
                if not match:
                    print("Something wrong: {} failed to match".format(item))
                head_pref, forms, feats = MS_FORM_FEATS.match(item).groups()
                if feats:
                    if feats[0] == '*':
                        feats = feats[1:]
#                        print("{} setting feature match {} to strict".format(self, index))
                        self.strict[index] = True
                    if "][" in feats:
                        # Multiple features
                        feats = feats.split("][")
                        feats = [feats[0] + "]"] + ["[" + f + "]" for f in feats[1:-1]] + ["[" + feats[-1]]
                        feats = FSSet(*feats)
                    else:
                        feats = FeatStruct(feats)
                forms = [f.strip() for f in forms.split(FORMALT_SEP) if f]
                if head_pref:
#                    print("Found head prefix for {}, head index {}".format(item, index))
                    self.head_index = index
                elif not feats and self.head_index == -1:
                    self.head_index = index
            p.append((forms, feats))
            if optmatch:
                self.optional[index] = (forms, feats)
        if self.optional:
#            print("Creating Morphosyns for optional elements {}".format(self.optional))
            opt_pattern1 = []
            del_indices = self.del_indices[:]
            swap_indices = self.swap_indices[:]
            add_items = self.add_items[:]
            featmod = self.featmod[:]
            agr = self.agr[:] if self.agr else None
            for index, (forms, feats) in enumerate(p):
                if index in self.optional:
                    if self.head_index > index:
                        self.head_index -= 1
                    for i, (d, t) in enumerate(del_indices):
                        if d > index:
                            del_indices[i][0] -= 1
                        if t > index:
                            del_indices[i][1] -= 1
                    if agr:
                        if agr[0] > index:
                            agr[0] -= 1
                        if agr[1] > index:
                            agr[1] -= 1
                    for i, (fi, fs) in featmod:
                        if fi > index:
                            featmod[i][0] -= 1
                else:
                    opt_pattern1.append((forms, feats))
            # This assumes no strict matching in optional MSs
            strict = [False] * len(opt_pattern1)
            self.optional_ms.append(MorphoSyn(self.language, name=self.name + '_opt1',
                                              del_indices=del_indices, swap_indices=swap_indices, agr=agr,
                                              add_items=add_items, featmod=featmod, failif=self.failif,
                                              pattern=opt_pattern1, strict=strict,
                                              expanded=True))
#            print("Optional MS: {}".format(self.optional_ms))
        return p

    def pattern_length(self):
        return len(self.pattern)

    def apply(self, sentence, ambig=False, verbosity=0, terse=False):
        """Apply the MorphoSyn pattern to the sentence if there is at least one match on some portion.
        2015.10.17: if ambig is True and this is an "ambiguous" MorphoSyn, copy the sentence
        before enforcing constraints.
        2015.10.20: constraints can be applied either to sentence or its copy (in altsyns list)
        2016.03.11: returns True if it copies the sentence.
        """
        if verbosity > 1 or self.debug:
            print("Attempting to apply {} to {}".format(self, sentence))
        matches = self.match(sentence, verbosity=verbosity, terse=terse)
        s = sentence
        copied = False
        copy = None
        if matches:
            if ambig and self.is_ambig():
                # Ambiguous patterns
                print("{} matches ({}) with ambiguity".format(self, matches))
                if self.is_feat_ambig():
                    matchfail = False
                    for m in matches:
                        x, y, toks = m
#                        print(" x {}, y {}, toks {}".format(x, y, toks))
                        matched = []
                        for t, a, aa in toks:
                            if isinstance(a, list):
                                for aaa in a:
                                    if aaa is False:
#                                        print("Some anal does not match ({})".format(a))
                                        matchfail = True
                                    else:
                                        matched.append((x, t, aaa))
                            x += 1
                    if matchfail:
#                        print(" Feature ambiguity, exclude {} from copy".format(matched))
                        # Copy the sentence as an altsyn
                        copy = sentence.copy(skip=matched)
                        copied = True
                        if self.is_not_preferred():
                            s = copy
                else:
                    # Copy the sentence as an altsyn
                    copy = sentence.copy()
                    copied = True
                    if self.is_not_preferred():
                        s = copy
            for match in matches:
                start, end, elements = match
                # %%
                # All of the crap between %% and %% is to create sentence copies if some analysis doesn't match this MS
                # but not if enough copies have already been created for a given word to handle the different possibilities.
                # All of this is skipped if the MS is a disambiguator, that is, if its name starts with DISAMBIG_CHAR.
                anal_fail = -1
                anal_fail_index = -1
                anal_succeed = 0
                for eindex, elem in enumerate(elements):
                    word, feats_list, dicts = elem
                    if isinstance(feats_list, list):
                        for index, (fl, d) in enumerate(zip(feats_list, dicts)):
                            if not fl:
                                if verbosity > 1 or self.debug:
                                    print("Match fails for {} for word {}, analysis {}".format(self, word, d))
                                anal_fail = index
                                anal_fail_index = eindex
                            else:
                                anal_succeed = index
                if anal_fail > -1 and not self.is_disambig():
                    # At least one of the analyses for some word is not compatible with this morphosyn, so create an altsyn
                    # See if other morphosyns have matched this section with ambiguity for the same word
                    all_ms = sentence.morphosyns[:]
                    if sentence.parent:
                        all_ms.extend(sentence.parent.morphosyns)
                        for asyn in sentence.parent.altsyns:
                            if asyn != sentence:
                                all_ms.extend(asyn.morphosyns)
                    else:
                        for asyn in sentence.altsyns:
                            all_ms.extend(asyn.morphosyns)
                    if verbosity or self.debug:
                        print("Previous and current morphosyns: {}".format(all_ms))
                    # Count how many previous matches there are for this section and this word
                    matching_previous_ms = 0
                    for ms in all_ms:
                        m1, s1, e1, f1 = ms
                        if s1 == start and e1 == end and f1 == anal_fail_index:
                            matching_previous_ms += 1
                    if verbosity or self.debug:
                        print("{} matching previous MS for word {}".format(matching_previous_ms, anal_fail_index))
                    # See if the number is one less than the number of analyses for the ambiguous word
                    n_fail_analyses = len(sentence.analyses[anal_fail_index])
                    if verbosity or self.debug:
                        print("# analyses for word {}: {}".format(anal_fail_index, n_fail_analyses))
                    if matching_previous_ms == n_fail_analyses - 1:
                        # Don't make another copy
                        if verbosity or self.debug:
                            print("Already matched enough MSs for word {}, no new copy necessary".format(anal_fail_index))
                    else:
                        # Make a copy to keep trying for further MSs
                        if verbosity or self.debug:
                            print("Analysis {} fails, so sentence copied by {}".format(anal_fail, self))
                        copy = sentence.copy()
                        copied = True
                        if anal_fail < anal_succeed:
                            if verbosity or self.debug:
                                print("Failing analysis has priority; swapping original sentence and copy")
                            # The analysis that fails has priority, so make the one that implements the morphosyn the altsyn
                            s = copy
                # %%
                if verbosity or self.debug:
                    print("Appending {}, {}, {}, {} to morphosyns".format(self, start, end, anal_fail_index))
                s.morphosyns.append((self, start, end, anal_fail_index))
                # Change either the sentence or the latest altsyn copy
                if verbosity > 1 or self.debug:
                    print(" Match {}".format(match))
                self.enforce_constraints(start, end, elements, anal_fail_index, verbosity=verbosity)
                self.insert_match(start, end, elements, s, verbosity=verbosity)
        return copied

    @staticmethod
    def del_token(token):
        return token and token[0] == '~'

    def match(self, sentence, verbosity=0, terse=False):
        """
        Match sentence, a list of pairs of words and their analyses, against the MorphoSyn's pattern.
        Match records the index of a matching analysis within the list of analyses for a given
        sentence word.
        """
        results = []
        if verbosity > 1 or self.debug:
            print("MS {} matching {}".format(self, sentence))
        if self.direction:
            # Left-to-right; index of item within the pattern
            pindex = 0
            # Index of sentence token where successful matching starts
            mindex = -1
            # Index if sentence token of last successful match
            lastmindex = -1
            result = []
            sindex = 0
            while sindex < len(sentence.analyses):
                if verbosity > 1 or self.debug:
                    if mindex > -1:
                        if lastmindex > -1:
                            print(" Item {} matched sentence item {}, moving forward".format(pindex-1, lastmindex))
                if mindex == -1:
                    # Some sentence item matched part of the pattern and failed later
                    if lastmindex > -1:
                        sindex = lastmindex + 1
                        if self.debug or verbosity > 1:
                            print("  Backtracking to sentence item {}".format(sindex))
                        # Resetting lastmindex
                        lastmindex = -1
                if self.debug:
                    print(" MS {} matching item {} against sentence item {}".format(self, pindex, sindex))
                    print("  First match {}, last match {}".format(mindex, lastmindex))
                stoken, sanals = sentence.analyses[sindex]
                if MorphoSyn.del_token(stoken):
                    sindex += 1
                    continue
                # Check next whether this is a FAILIF Morphosysn that should fail because of what
                # MorphoSyns have already succeeded for the sentence
                if self.failif:
                    failed = False
                    for ms, start, end, fail_word in sentence.morphosyns:
                        # For each of MSs that have already matched portions of this sentence
                        if ms.name.startswith(self.failif) and start <= sindex <= end:
                            if verbosity > 1 or self.debug:
                                print(" {} fails because {} has already succeeded".format(self, ms))
                            failed = True
                            break
                    if failed:
                        sindex += 1
                        continue
                # sentence.analyses consists of pairs of word tokens and a list of analysis dicts
                match = self.match_item(stoken, sanals, pindex, verbosity=verbosity)
                if match:
                    # If there are no anals but True, replace [True] with []
                    if match[1] == [True]:
                        match[1] = []
                    if self.debug:
                        print(" {} found match {} for token {}".format(self, match, stoken))
                    result.append(match)
                    # Is this the end of the pattern? If so, succeed.
                    if self.pattern_length() == pindex + 1:
                        if not terse:
                            print("  MS {} tuvo éxito".format(self))
#                        con resultado {}".format(self, result))
#                        print("  Match result {}, stoken {}, sanals {}".format(result, stoken, sanals))
                        if mindex < 0:
                            mindex = sindex
                        results.append((mindex, sindex+1, result))
#                        print("Results for {}: {}".format(self, results))
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
                        lastmindex = sindex
                else:
                    # Start over
                    mindex = -1
                    pindex = 0
                    result = []
                sindex += 1
            if results:
                return results
            return False
        return False

    def match_item(self, stoken, sanals, pindex, verbosity=0):
        """Match a sentence item against a pattern item."""
        pforms, pfeats = self.pattern[pindex]
        # Whether to match features strictly
        strict = self.strict[pindex]
        isneg = pindex in self.neg_matches
        if verbosity > 1 or self.debug:
            print("  MS {} matching {}:{} against {}:{}".format(self, stoken, sanals, pforms, pfeats.__repr__()))
            if isneg:
                print("  MS {} negative match: {}, {}, {}, {}".format(self, stoken, sanals, pforms, pfeats))
        ## CHANGE THIS LATER SO ONLY ONE ANAL IS POSSIBLE
        if not isinstance(sanals, list):
            sanals = [sanals]
        # No FS to match
        if not pfeats:
            return self.match_token(stoken, sanals, pforms, verbosity=verbosity)
        else:
            if not sanals:
                # No morphological analyses for sentence item; fail
                if verbosity > 1 or self.debug:
                    print("   No feats, match item failed")
                return False
            # pattern FS must match features in one or more anals; record the results in
            # last corresponding to the list of anals in sentence
            anal_matches = []
            for sanal in sanals:
                anal_matches.append(self.match_anal(stoken, sanal, pforms, pfeats, strict=strict, neg=isneg,
                                                    verbosity=verbosity))
            if any(anal_matches):
                return [stoken, anal_matches, sanals]
        if verbosity > 1 or self.debug:
            print("   Match item failed")
        return False

    def match_token(self, stoken, sanals, pforms, verbosity=0):
        """Match the word or roots in a sentence against the set of forms in a pattern item."""
        if verbosity > 1 or self.debug:
            print("   Matching sentence token {} and analyses {} against pattern forms {}".format(stoken, sanals, pforms))
        if any([stoken == f for f in pforms]):
            # Do any of the pattern items match the sentence word?
            if verbosity > 1 or self.debug:
                print("   Succeeded on token")
            return [stoken, False, sanals]
        if Entry.match_special(stoken, pforms):
            # If stoken and pforms are special, do they match?
            if verbosity > 1 or self.debug:
                print("   Succeeded on special token")
            return [stoken, False, sanals]
        # Do any of the pattern items match a root in any sentence item analysis?
        matched_anals = []
        for anal in sanals:
            root = anal['root']
            if FORMALT_SEP in root:
                roots, pos = root.split('_')
                roots = roots.split(FORMALT_SEP)
                roots = [(r + '_' + pos) for r in roots]
                if self.debug:
                    print("  Roots {}".format(roots))
                if any([r == f for f in pforms for r in roots]):
                    matched_anals.append(anal['features'])
                else:
                    matched_anals.append(False)
            elif any([root == f for f in pforms]):
                matched_anals.append(anal['features'])
            else:
                matched_anals.append(False)
        if any(matched_anals):
            if verbosity > 1 or self.debug:
                print("   Succeeded on root")
            return [stoken, matched_anals, sanals]
        if verbosity > 1 or self.debug:
            print("    Match token failed")
        return False

    def match_anal(self, stoken, sanal, pforms, pfeats, strict=False, neg=False, verbosity=0):
        """Match the sentence analysis against pforms and pfeats in a pattern.
        sanal is either a dict or a pair (root, features)."""
        if isinstance(sanal, dict):
            sfeats = sanal.get('features')
            sroot = sanal.get('root')
            spos = sanal.get('pos')
        else:
            sroot, sfeats = sanal
            spos = None
        ppos = pfeats.get('pos') if pfeats else None
        if verbosity > 1 or self.debug:
            s = "   Attempting to match pattern forms {} (strict? {}), pos {} and feats {} against sentence item root {}, pos {} and feats {}"
            print(s.format(pforms, strict, ppos, pfeats.__repr__(), sroot, spos, sfeats.__repr__()))
        if not pforms or any([sroot == f for f in pforms]):
            if verbosity > 1 or self.debug:
                print("    Root matched")
                print("    {} unifying {}/{} and {}/{}".format(self, sroot, sfeats.__repr__(), pforms, pfeats.__repr__()))
            if isinstance(sfeats, FSSet):
                # This returns an FSSet too
#                print("   Unifying FSSet {} with {}".format(sfeats, pfeats))
#                u = sfeats.unify_FS(pfeats, strict=strict)
                u = sfeats.u(pfeats, strict=strict)
            elif not sfeats:
                # No sentence item features but there are match item features. See if the parts of speech match.
                if ppos and spos and ppos == spos:
                    if neg:
                        return False
                    else:
                        return True
                elif neg:
                    return True
                else:
                    return False
            elif isinstance(pfeats, FSSet):
                u = pfeats.unify_FS(sfeats, strict=strict)
            else:
                u = simple_unify(sfeats, pfeats, strict=strict)
            if verbosity > 1 or self.debug:
                print("    Result of unification: {} (neg? {})".format(u.__repr__(), neg))
            if u != 'fail':
                if not neg:
                    # result could be frozen if nothing changed; we need an unfrozen FS for later changes
                    if isinstance(u, FSSet):
                        u = u.unfreeze(cast=True)
                    else:
                        u = u.unfreeze()
                    if verbosity > 1 or self.debug:
                        print("    Feats matched: {}, (type {})".format(u.__repr__(), type(u)))
                    return u
                elif verbosity > 1 or self.debug:
                    print("    Anals failed")
            elif neg:
                if verbosity > 1 or self.debug:
                    print("    Neg feats match succeeded")
                return True
            elif verbosity > 1 or self.debug:
                print("    Anals failed")
        return False

    def enforce_constraints(self, start, end, elements, anal_fail_index, verbosity=0):
        """If there is an agreement constraint, modify the match element features to reflect it.
        Works by mutating the features in match.
        If there are deletion constraints, prefix ~ to the relevant tokens.
        """
        if verbosity > 1 or self.debug:
            print(" Enforcing constraints for match {}/{} {}".format(start, end, elements))
        # Exclude the source features
        if self.agr:
            srci, trgi, feats = self.agr
#            print(" Agr {} {} {}".format(srci, trgi, feats))
            src_elem = elements[srci]
            trg_elem = elements[trgi]
            if verbosity > 1 or self.debug:
                print("  Enforcing agreement on features {} from {} to {}".format(feats, src_elem, trg_elem))
            src_tok, src_feats_list, x = src_elem
            trg_tok, trg_feats_list, y = trg_elem
#            print("  Target features list: {}".format(trg_feats_list))
            for tf_index, trg_feats in enumerate(trg_feats_list):
                if not trg_feats:
                    # target features could be False
                    continue
#                print("trg_feats {}, frozen? {}".format(trg_feats.__repr__(), trg_feats.frozen()))
                # Because it may be mutated, use a copy of trg_feats
                for src_feats in src_feats_list:
                    if src_feats:
                        # It might not be an FSSet, but needs to be for agree_FSS()
                        src_feats = FSSet(src_feats)
                        if verbosity > 1 or self.debug:
                            print("    Agreeing: {}, {}".format(src_feats.__repr__(), trg_feats.__repr__()))
                            print("    Types: source {}, target {}".format(type(src_feats), type(trg_feats)))
                        # source features could be False
                        # Force target to agree with source on feature pairs
                        trg_feats_list[tf_index] = src_feats.agree_FSS(trg_feats, feats, force=True)
                        if verbosity > 1 or self.debug:
                            print("    Result of agreement: {}".format(trg_feats.__repr__()))
                        # Only do this for the first set of src_feats that succeeds
                        break
        if self.del_indices:
            for i, j in self.del_indices:
                elements[i][0] = '~' + elements[i][0]
                if j != -1:
                    elements[i][2][0]['target'] = j-i

        if self.add_items:
            print("Warning: Adding items in Morphosyn not yet implemented!")
            for i, item in self.add_items:
                print("Adding item {} in position {}".format(item, i))

        if self.featmod:
            # Modify features in indexed element
            for fm_index, fm_feats in self.featmod:
                elem = elements[fm_index]
                feats_list = elem[1]
                if verbosity > 1 or self.debug:
                    print("    Modifying features: {}, {}, {}".format(fm_index, fm_feats.__repr__(), feats_list))
                if not feats_list:
                    elem[1] = [fm_feats.copy()]
                else:
                    for index, feats in enumerate(feats_list):
                        if index == anal_fail_index:
                            # The MS didn't match
                            if verbosity > 1 or self.debug:
                                print("   Analysis {} fails to match MS!".format(index))
                            continue
                        if verbosity > 1 or self.debug:
                            if isinstance(feats, FeatStruct):
                                print("      Feats {}, frozen? {}".format(feats.__repr__(), feats.frozen()))
                            else:
                                print("      Feats (FSSet) {}".format(feats.__repr__()))
                        feats.update_inside(fm_feats)
            
    def insert_match(self, start, end, m_elements, sentence, verbosity=0):
        """Replace matched portion of sentence with elements in match.
        Works by mutating sentence elements (tokens and analyses).
        """
        if verbosity > 1 or self.debug:
            print(" Inserting match {}/{} {}".format(start, end, m_elements))
        # start and end are indices within the sentence; some may have been
        # ignored within the pattern during matching
        m_index = 0
        s_index = start
        for s_elem in sentence.analyses[start:end]:
            s_token = s_elem[0]
            if MorphoSyn.del_token(s_token):
                s_index += 1
                # Skip this sentence element; don't increment m_index
                continue
            m_elem = m_elements[m_index]
            m_index += 1
            # Replace the token (could have ~ now)
            s_elem[0] = m_elem[0]
            # Replace the features if match element has any
            m_feats_list = m_elem[1]
            s_anals = s_elem[1]
            # FIX THIS LATER; s_anals DOESN'T REALLY NEED TO BE A LIST
            if not isinstance(s_anals, list):
                s_anals = [s_anals]
            new_s_anals = []
            if m_elem[0][0] == '~':
                if 'target' in s_anals[0]:                    
                    s_anals[0]['target-node'] = s_anals[0]['target'] + s_index
            if m_feats_list:
                if not s_anals:
                    new_s_anals = [{'features': mfl, 'root': s_token} for mfl in m_feats_list]
                for m_feats, s_anal in zip(m_feats_list, s_anals):
                    if not m_feats:
                        # This anal failed to match pattern; filter it out
                        continue
                    else:
                        s_feats = s_anal['features']
                        if self.debug:
                            print("  m_feats {} (type {}), s_feats {}".format(m_feats, type(m_feats), s_feats.__repr__()))
                        if s_feats != m_feats:
                            # Replace sentence features with match features if something
                            # has changed
                            s_anal['features'] = m_feats
                        new_s_anals.append(s_anal)
            else:
                new_s_anals = s_anals
            s_elem[1] = new_s_anals
            s_index += 1
        # Swap sentence.analyses and tokens elements if there are swap_indices in the MS
        # This has to take into consideration deleted elements, so it's a little ugly.
        # Basically swapping should be avoided in Morphosyns if at all possible.
        if self.swap_indices:
            mstart, mend = self.swap_indices
            sstart, send = start+mstart, start+mend
            sindex = 0
            swapi1 = -1
            swapi2 = -1
            mindex = 0
            deleted_targets = {}
            for srawindex, (tok, anal) in enumerate(sentence.analyses):
                if MorphoSyn.del_token(tok):
                    anal1 = anal[0]
                    if 'target-node' in anal1:
                        targ = anal1['target-node']
                        if targ in deleted_targets:
                            deleted_targets[targ].append(srawindex)
                        else:
                            deleted_targets[targ] = [srawindex]
                    continue
                if srawindex == sstart and swapi1 == -1:
                    swapi1 = srawindex
                    sindex += 1
                    mindex += 1
                elif mindex == mend:
                    swapi2 = srawindex
                    s_indices1 = deleted_targets.get(swapi1, [])
                    s_indices1.append(swapi1)
                    s_indices1.sort()
                    s_indices2 = deleted_targets.get(swapi2, [])
                    s_indices2.append(swapi2)
                    s_indices2.sort()
                    range1 = s_indices1[0], s_indices1[-1]+1
                    range2 = s_indices2[0], s_indices2[-1]+1
                    toks = sentence.tokens
                    anals = sentence.analyses
                    toks[range1[0]:range1[1]], toks[range2[0]:range2[1]] = toks[range2[0]:range2[1]], toks[range1[0]:range1[1]]
                    anals[range1[0]:range1[1]], anals[range2[0]:range2[1]] = anals[range2[0]:range2[1]], anals[range1[0]:range1[1]]
                    return
                else:
                    sindex += 1
                    mindex += 1

class Join(Entry):
    """
    Pattern specifying how bilingual Segments can be merged to form SuperSegs.
    """
    ## Symbols in Join files
    attrib_sep = ';'
    # separates tokens (segments)
    pattern_sep = ' '
    ## Regex for Join files
    form_feats= re.compile("\s*(\^?)([$%<'|\w¿¡?!]*)\s*((?:\*?\[.+\])*)$")
    does_agree = re.compile("\s*(\d)\s*=\?\s*(\d)\s*(.+)$")
    must_agree = re.compile("\s*(\d)\s*=!\s*(\d)\s*(.+)$")
    head_index = re.compile("\s*\^\s*(\d)$")
    swap_order = re.compile("\s*>\s*((?:\d\s*)+)$")
    add_feats = re.compile("\s*(\d)\s*(\[.+\])$")

    def __init__(self, source, target, name=None, pattern=None, expanded=False):
        Entry.__init__(self, name, source)
        self.target = target
        self.name = name
        self.pattern = pattern
        self.agree_conditions = []
        self.agree_changes = []
        self.targ_feats = []
        self.head_index = -1
        self.segment_order = None
        # Expand unless this already happened (with optional form-feats)
        # This also sets self.agr, self.del_indices, self.featmod; may also set direction
        if not expanded:
            self.expand(pattern)
            expanded = True
        else:
            self.pattern = pattern

    def expand(self, pattern, verbose=0):
        """Expand pattern from string in Join file."""
        if verbose:
            print("Expanding Join pattern {}".format(pattern))
        self.pattern = []
        # split the string into tokens
        pattern = pattern.split(Join.attrib_sep)
        # Actual pattern
        for token in pattern[0].strip().split():
            if "[" in token:
                # Feature specification
                # Make it into a FSSet
                token = FSSet(token)
                self.pattern.append(token)
            else:
                # Special token: %C, %N
                # Category: $vt
                # Token: con
                self.pattern.append(token)
        # Attributes: agree?, agree!, swap
        attribs = pattern[1:]
        # Expand attributes
        for attrib in attribs:
            attrib = attrib.strip()
            if verbose:
                print("Join attribute {}".format(attrib))
            match = Join.does_agree.match(attrib)
            if match:
                s1, s2, feats = match.groups()
                f1, f2 = feats.split(':')
                s1 = int(s1)
                s2 = int(s2)
                if verbose:
                    print("  Matched 'does agree' condition {}, s1 {}, s2 {}, f1 {}, f2 {}".format(attrib, s1, s2, f1, f2))
                self.agree_conditions.append((s1, s2, f1, f2))
                continue
            match = Join.must_agree.match(attrib)
            if match:
                s1, s2, feats = match.groups()
                f1, f2 = feats.split(':')
                s1 = int(s1)
                s2 = int(s2)
                if verbose:
                    print("  Matched 'must agree' condition {}, s1 {}, s2 {}, f1 {}, f2 {}".format(attrib, s1, s2, f1, f2))
                self.agree_changes.append((s1, s2, f1, f2))
                continue
            match = Join.head_index.match(attrib)
            if match:
                head_index = match.groups()[0]
                head_index = int(head_index)
                if verbose:
                    print("  Matched head index: {}".format(head_index))
                self.head_index = head_index
                continue
            match = Join.swap_order.match(attrib)
            if match:
                indices = match.groups()[0]
                indices = indices.replace(" ", "")
                indices = [int(i) for i in indices]
                if verbose:
                    print("  Matched swap order: {}".format(indices))
                self.segment_order = indices
                continue
            match = Join.add_feats.match(attrib)
            if match:
                index, feats = match.groups()
                index = int(index)
                feats = FeatStruct(feats)
                if verbose:
                    print("  Matched 'add feats' action {}, {}".format(index, feats.__repr__()))
                self.targ_feats.append((index, feats))
                continue

    def match(self, segments, startindex=0, verbosity=0):
        """Match this Join against segments in Solution starting with
        position startindex."""
        matched = True
        pattern = self.pattern
        patlength = len(pattern)
        patindex = 0
        segindex = startindex
        match1 = []
        while matched and patindex < patlength:
            patelem = pattern[patindex]
            segment = segments[segindex]
            match2 = segment.match_join(patelem, verbosity=verbosity)
            if match2:
                print(" {} matched {}".format(segment, self))
                match1.append((segindex, segment, match2))
                segindex += 1
                patindex += 1
            else:
                return False
        return match1

    def match_conds(self, segments, startindex=0, verbosity=1):
        """Match the conditions in this Join against segments in Solution
        starting with position startindex."""
        for s1, s2, f1, f2 in self.agree_conditions:
            if verbosity:
                print("  Matching condition {} {}; {} {}".format(s1, s2, f1, f2))
            seg1 = segments[s1+startindex]
            seg2 = segments[s2+startindex]
            segfeats1 = seg1.get_shead_feats()
            segfeats2 = seg2.get_shead_feats()
            if verbosity:
                print("    Features {} and {} must match on {} and {}".format(segfeats1, segfeats2, f1, f2))
            for feats1 in segfeats1:
                v1 = feats1.get(f1)
                # Allow match when one or the other feature has no value for the feature
                if v1 == None:
                    continue
                for feats2 in segfeats2:
                    v2 = feats2.get(f2)
                    if verbosity:
                        print("      Feats {} {}, vals {} {}".format(feats1.__repr__(), feats2.__repr__(), v1, v2))
                    if v2 == None:
                        continue
                    if v1 != v2:
                        return False
            if verbosity:
                print("  {} and {} matched condition {}|{}".format(seg1, seg2, f1, f2))
        return True

    def apply(self, superseg, verbosity=1):
        """Make changes specified in Join to segments matching it."""
        # Feature agreement, change
        segments = superseg.segments
        for change in self.agree_changes:
            seg1index, seg2index, feat1, feat2 = change
            if verbosity:
                print("  Must agree {} {} ; {} {}".format(seg1index, seg2index, feat1, feat2))
            seg1 = segments[seg1index]
            seg2 = segments[seg2index]
            segfeats1 = seg1.get_thead_feats()
            segfeats2 = seg2.get_thead_feats()
            if verbosity:
                print("  Seg1 {} feats {}, seg2 {} feats {}".format(seg1, segfeats1, seg2, segfeats2))
        if self.targ_feats:
            for segindex, addfeats in self.targ_feats:
                # Add targfeats to feats in segindex Seg
                segment = superseg.segments[segindex]
                tfeats = segment.get_thead_feats()
                print("Segment {}, thead {}, tfeats {}".format(segment, segment.thead, tfeats))
                print("Adding features {} to targ features {}".format(addfeats.__repr__(), tfeats.__repr__()))
                for ti, th in enumerate(segment.thead):
#                    troot, tpos, tf = th
                    tf = th[2]
                    print("th {}".format(th))
                    newtf = tf.unify_FS(addfeats)
                    if newtf != 'fail':
                        th[2] = newtf
#                    segment.thead[ti] = troot, tpos, newtf
                print("New thead {}".format(segment.thead))
        if self.segment_order:
            if verbosity:
                print("  Swap {}".format(self.segment_order))
            i1, i2 = self.segment_order
            sso = superseg.order
            sso[i1], sso[i2] = sso[i2], sso[i1]
            to_delete = []
            for index in sso:
                if index not in self.segment_order:
                    to_delete.append(index)
            for d in to_delete:
                sso.remove(d)
            if verbosity:
                print("  Indices swapped {}".format(sso))

class EntryError(Exception):
    '''Class for errors encountered when attempting to update an entry.'''

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
    
