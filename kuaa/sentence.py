#   
#   Mainumby: sentences and how to parse and translate them.
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

# 2014.04.15
# -- Created.
# 2014.04.19-20
# -- Group matching. GInst, GNode, and SNode classes.
# 2014.04.22
# -- Solution class.
# 2014.04.26-7
# -- Translation class and realization.
# 2014.04.28
# -- Variables for sentence analysis.
# 2014.04.29-30
# -- Fixed some constraints and initial variables values.
# 2014.05.01
# -- Handling source words that aren't "covered" (no group candidate matches them):
#    variables and source constraints.
# 2014.05.02
# -- Uncovered source words: target ordering constraints.
#    Introduced "chunks": target output units that are not connected.
# 2014.05.04-5
# -- New agreement variables and constraints.
# 2014.05.09
# -- Fixed output ordering so that order between nodes in merged groups
#    is right: all nodes in outer group before merged node must
#    precede all nodes in inner group, and all nodes in outer group
#    after merged node must follow all nodes in inner group.
# 2014.05.11
# -- Tree variables for unselected groups get removed from essential
#    variable list so the list of undetermined essential variables can
#    end up empty when it should be.
# 2014.05.15
# -- Fixed how group trees are worked out: using the snode->gnodes variables
#    rather than merger-related variables and tree variables.
# -- Search in group selection and output ordering.
# 2014.05.16
# -- Fixed a bug in how SL snodes with no corresponding TL snodes are
#    handled during node merging.
# 2014.05.18
# -- Target-language within-group agreement ("GIVES them a piece of HER/HIS mind").
# 2014.05.19
# -- all_sols argument to solve() and other methods that search finds all
#    solutions without querying user.
# -- Alignments is inferred from lexicon if not explicit.
# 2015.05.18
# -- Cache search and morphological analysis replaces form lookup in tokenize().
# 2015.05.20
# -- Generation now handled by morphology FSTs.
# 2015.06.10
# -- MorphoSyns applied in Sentence.tokenize().
# 2015.07.04
# -- Text class, including sentence tokenizer and splitter.
# 2015.07.05
# -- Fixed SNode - Group matching so it works for features added during
#    MorphoSyn matching, like +r (reflexive) in Spanish. Required adding
#    explicit negative features in groups.
#      se abrió matches abrir_v[+r] but not abrir_v[-r]
#      abrió matchs abrir_v[-r] but not abrir_v[+r]
# 2015.07.11
# -- Changed Text to Document (to agree with database class)
# 2015.07.17-25
# -- Translation class replaced by TreeTrans class, with instances
#    for each GInst
# 2015.07.28
# -- all_sols and all_trans options are separate. (Usually we'll want only
#    one solution but multiple translations?)
# 2015.07.29
# -- Segmentation of contractions; lowercasing of capitalized words.
#    Optional capitalization of first word in sentence translation.
# 2015.08.03
# -- Matching of "set items" in groups, like $$pro_3oj for 3p object pronouns
#    in Spanish. These don't result in "abstract" GNodes that must merge
#    with "concrete" GNodes. Rather they are concrete.
# 2015.08.06
# -- Sentence can create HTML for translated segments from solutions treetrans
#    objects.
# 2015.08.13
# -- TreeTrans objects aren't recreated for segments that already have one,
#    unless that one resulted from a merger.
# 2015.08.16
# -- Working on evaluator function for search states.
# 2015.09.24
# -- Changed evaluator function so it favors preferred analyses of cached words
#    (these have lower group indices).
# 2015.09.25
# -- For each key in the groups dict, only allow one to match (the entries are
#    ordered from most to least specific). Later allow exceptions to this. See
#    lexicalize().
# 2016.01.06
# -- Split off segment.py.
# 2016.01.11
# -- Added ?! to end-of-sentence characters.
# 2016.01.18
# -- Fixed TreeTrans.build() call so that multiple translations work with groups involving merging.
# 2016.02.23
# -- Sentence copy() can skip some features for one or more tokens.
# 2016.02.24
# -- No complicated figuring out what the max number of translations for nodes that aren't merged. Since similar group translations
#    were collapsed, it's just the number of group translations.
# 2016.03.01
# -- Adjusted which segments are created and how segments are displayed when corresponding source tokens are discontinuous
# 2016.05.03
# -- Fixed bug that prevented the same group (actually group head) from applying to different words.
# 2016.05.05
# -- Made the tokenizer more sophisticated (see RE in Document).

import copy, re, random
from .ui import *
from .segment import *
from .record import SentRecord

class Document(list):
    """A ist of of Sentences, split from a text string."""

    id = 0

    start = ['¿', '¡']
    end = ['.', '?', '!']
    markers = [('\"', '\"'), ("(", ")"), ("{", "}")]
    wordsplit = ['—']

    ## regular expressions for matching tokens
    # adjoining punctuation (except .)
    # before: ([{¡¿"*'`«“‘-–—=
    # after: )]}!?":;*'»”’-–—=
    # within token: letters and digits, _-+.'@$^&=|/,~<>
    # within word: letters and digits, _-.'`&=|/~
    # beginning of token: letters and digits, -+#.@$~
    # end of token: letters and digits, -+#.$%/º
    # end of word: letters and digits, #./º
    # only digits
    number1_re = re.compile(r"([(\[{¡¿–—\"\'«“‘`*=]*)([\-+±$£€]?[\d]+[%¢]?)([)\]}!?\"\'»”’*\-–—,.:;]*)$")
    # digits with intermediate characters (.,=><), which must be followed by one or more digits
    number_re = re.compile(r"([(\[{¡¿–—\"\'«“‘`*=]*)([\-+±$£€]?[\d]+[\d,.=><+\-±/×÷≤≥]*[\d]+[%¢]?)([)\]}!?\"\'»”’*\-–—,.:;]*)$")
    # separated punctuation, including some that might be separated by error
    punc_re = re.compile(r"([\-–—&=.,:;\"+<>/?!]{1,3})")
    # word of one character
    word1_re = re.compile(r"([(\[{¡¿\-–—\"\'«“‘`*=]*)(\w)([)\]}!?\"\'»”’*\-–—,:;=]*)$")
    # word of more than one character: one beginning character, one end character, 0 or more within characters
    word_re = re.compile(r"([(\[{¡¿\-–—\"\'«“‘`*=]*)([\w#@~][\w\-/:;+.'`~&=\|]*[\w/º#.])([)\]}!?\"\'»”’*\-–—,:;=]*)$")
    start_re = re.compile('[\-–—¿¡\'\"«“‘(\[]+$')
    poss_end_re = re.compile('[")\]}]{0,2}[?!][)"\]]{0,2}')
    # 0-2 pre-end characters (like ")"), 1 end character (.?!), 0-2 post-end characters (like ")")
    end_re = re.compile('[\"\'”’»)\]}]{0,2}[.?!][.)»”’\'\"\]\-–—]{0,2}')

    def __init__(self, language=None, target=None, text='', proc=True, session=None):
        self.set_id()
        self.language = language
        self.target = target
        self.text = text
        self.session = session
        # Intermediate representations: list of word-like tokens and ints representing types
        self.tokens = []
        list.__init__(self)
        # A list of pairs of raw source-target sentences, the result of the user's interaction
        # with the system.
        self.output = []
        if proc:
            self.process()
#        print("Created document with session {}".format(session))

    def set_id(self):
        self.id = Document.id
        Document.id += 1

    def __repr__(self):
        return "||| text {} |||".format(self.id)

    def process(self):
        """Use tokenize and split to generate tokenized sentences."""
        self.tokenize()
        self.split()

    def tokenize(self):
        """Split the text into word tokens, separating off punctuation except for
        abbreviations and numerals. Later use a language-specific tokenizer."""
        # Later split at \n to get paragraphs.
        # Separate at whitespace.
        tokens = self.text.split()
        for token in tokens:
            tok_subtype = 0
            word_tok = False
            number = False
            punctuation = False
            match = Document.punc_re.match(token)
            if match:
                tok_subtype = 1
                pre = ''; suf = ''; word = match.groups()[0]
            else:
                match = Document.number1_re.match(token)
                if match:
                    tok_subtype = 2
                else:
                    match = Document.number_re.match(token)
                    if match:
                        tok_subtype = 2
                    else:
                        match = Document.word1_re.match(token)
                        if match:
                            word_tok = True
                        else:
                            match = Document.word_re.match(token)
                            if match:
                                word_tok = True
                            else:
                                print("Something wrong: {} fails to be an acceptable token".format(token))
                                return
                pre, word, suf = match.groups()
                if pre:
                    self.tokens.append((pre, 0, 0))
                # Check to see if word ends in . and is not an abbreviation
                if word_tok and word.endswith('.'):
                    if word not in self.language.abbrevs:
                        # Strip of all trailing .s
                        word, x, y = word.partition('.')
                        suf = x + y + suf
#                print("pre {}, word {}, suf {}".format(pre, word, suf))
                self.tokens.append((word, 1, tok_subtype))
                if suf:
                    self.tokens.append((suf, 2, 0))

    @staticmethod
    def is_sent_start(token):
        return token[0].isupper()

    @staticmethod
    def start_next(tokens):
        # Does a new sentence begin at the start of tokens?
        if not tokens:
            return False
        tok, typ, subtyp = tokens[0]
        if typ == 1:
            if Document.is_sent_start(tok):
                return True
        elif Document.start_re.match(tok):
            # sentence-inital punctuation
            if len(tokens) > 1 and Document.is_sent_start(tokens[1][0]):
                return True
        return False
            
    def split(self):
        """Split tokenized text into sentences. Later use a language-specific splitter."""
        current_sentence = []
        sentences = []
        ntokens = len(self.tokens)
        tokindex = 0
        token = ''
        toktype = 1
        while tokindex < ntokens:
            token, toktype, toksubtype = self.tokens[tokindex]
#            print("token {}, toktype {}".format(token, toktype, toksubtype))
            if toktype in (0, 1):
                current_sentence.append((token, toktype, toksubtype))
            # Check whether this is a sentence end
            elif Document.end_re.match(token):
                if not current_sentence:
                    print("Something wrong: empty sentence: {}".format(self.tokens[:tokindex]))
                    return
                else:
                    # End sentence
                    current_sentence.append((token, toktype, toksubtype))
                    sentences.append(current_sentence)
                    current_sentence = []
            elif Document.poss_end_re.match(token):
                if current_sentence and (tokindex == ntokens-1 or Document.start_next(self.tokens[tokindex:])):
                    # End sentence
                    current_sentence.append((token, toktype, toksubtype))
                    sentences.append(current_sentence)
                    current_sentence = []
                else:
                    current_sentence.append((token, toktype, toksubtype))
            else:
                current_sentence.append((token, toktype, toksubtype))
            tokindex += 1
        # Make Sentence objects for each list of tokens and types
        for sentence in sentences:
            self.append(Sentence(language=self.language, tokens=sentence, target=self.target,
                                 session=self.session))

#            if Document.start_re(token) and tokindex < ntokens-1 and Document.is_sent_start(token[tokindex+1]):
#                # Sentence beginning
#                if current_sentence:

class Sentence:
    """A sentence is a list of words (or other lexical tokens) that gets
    assigned a set of variables and constraints that are run during
    parsing or translation. Starts either with raw or tokens generated by
    Document."""

    id = 0
    word_width = 10
    # colors to display sentence segments in interface
    tt_colors = ['red', 'blue', 'sienna', 'green', 'purple', 'red', 'blue', 'sienna', 'green', 'purple', 'red', 'blue', 'sienna', 'green', 'purple']

    def __init__(self, raw='', language=None, tokens=None, toktypes=None, toksubtypes=None,
                 nodes=None, groups=None, target=None, init=False,
                 analyses=None,
                 session=None,
                 verbosity=0):
        self.set_id()
        # A list of string tokens, created by a Document object including this sentence
        # or None if the Sentence is created outside of Document
        if toktypes:
            # if copying these will already be assigned
            self.tokens = tokens
            self.toktypes = toktypes
            self.toksubtypes = toksubtypes
            self.raw = raw
        elif tokens:
            # tokens is a list of pairs passed from Document object
            self.tokens = [t[0] for t in tokens]
            self.toktypes = [t[1] for t in tokens]
            self.toksubtypes = [t[2] for t in tokens]
#            print("Joining tokens: {}".format(self.tokens))
            self.raw = tokens[0][0]
            lasttyp = 1
            for tok, typ, subtyp in tokens[1:-1]:
                if lasttyp == 0 or typ == 2:
                    # Last token was a punc prefix or current token is a punc suffix
                    self.raw += tok
                else:
                    self.raw += " " + tok
                lasttyp = typ
            self.raw += tokens[-1][0]
#            self.raw = ' '.join(self.tokens)
        else:
            self.raw = raw
            self.tokens = None
            self.toktypes = None
            self.toksubtypes = None
#        # A string representing the raw sentence (if it hasn't been tokenized)
#        self.raw = raw
        # Source language: a language object
        self.language = language
        # Target language: a language object or None
        self.target = target
        # A list of tuples of analyzed words
        self.analyses = analyses or []
        # A list of SNode objects, one for each token
        self.nodes = nodes or []
        # A list of candidate groups (realized as GInst objects) found during lexicalization
        self.groups = groups or []
        # Control messages
        self.verbosity = verbosity
        # GNodes in GInsts
        self.gnodes = []
        # Indices of covered SNodes
        self.covered_indices = []
        # A list of constraints to run
        self.constraints = []
        # Root domain store for variables
        self.dstore = DStore(name="S{}".format(self.id))
        # A dict of sentence-level variables
        self.variables = {}
        # Modified copies of the sentence for cases of syntactic ambiguity; "alternate syntax"
        self.altsyns = []
        # MorphoSyns applied to sentence along with their start and end
        self.morphosyns = []
        # Solver to find solutions
        self.solver = Solver(self.constraints, self.dstore,
                             evaluator=self.state_eval,
                             varselect=self.get_w2gn_vars,
                             description='group selection', verbosity=verbosity)
        # Solutions found during parsing
        self.solutions = []
        # Outputs from tree translation
        self.trans_outputs = []
        # Complete translations
        self.complete_trans = []
        # Session and associated SentRecord object; create if there is an active Session
        self.session = session
        if session and session.running:
            self.record = self.make_record(session)
        else:
            self.record = None
        if verbosity:
            print("Created Sentence object {}".format(self))
        if init:
            self.initialize()

    def set_id(self):
        self.id = Sentence.id
        Sentence.id += 1

    ## Display
    def __repr__(self):
        """Print name."""
        if self.tokens:
            return '|| ({}) {} ||'.format(self.id, ' '.join(self.tokens))
        elif self.raw:
            return '|| ({}) {} ||'.format(self.id, self.raw)
        else:
            return '|| {} sentence {} ||'.format(self.language, self.id)

    def get_final_punc(self):
        """Return sentence-final punctuation as a string or empty string if there is none."""
        # Final token
        fintok = self.nodes[-1].token
        if self.language.is_punc(fintok):
            return fintok
        return ''

    def pretty(self):
        """Print sentence more or less as it originally appeared."""
        # Later combine ending punctuation with preceding word.
        return self.raw

    def display(self, show_all_sols=True, show_trans=True, word_width=0):
        """Show the sentence and one or more solutions in terminal."""
        s = "   "
        word_width = word_width or Sentence.word_width
        for node in self.nodes:
            s += "{}".format(node.token).center(word_width)
        print(s)
        solutions = self.solutions if show_all_sols else self.solutions[:1]
        for solution in solutions:
            solution.display(word_width=word_width)

    ## Copying, for alternate syntactic representations

    def copy(self, skip=None):
        """Make a copy of the sentence, assumed to happen following analysis but before node creation.
        For ambiguous morphosyntax. Return the copy so it can be used by MorphoSyn.apply().
        skip is None or a list of triples: (position, token, feats). For each triple, the copy excludes the feats
        in the analysis of token in position."""
        s = Sentence(raw=self.raw[:],
                     tokens=self.tokens[:], toktypes=self.toktypes[:], toksubtypes= self.toksubtypes[:],
                     language=self.language, target=self.target,
                     analyses=copy.deepcopy(self.analyses))
        if skip:
#            print("Skipping {} in copy of {}".format(skip, self))
            for position, token, anal in skip:
                tok_anal = s.analyses[position]
#                print("  Token {}, analyses: {}".format(tok_anal[0], tok_anal[1]))
                res_anals = []
                for a in tok_anal[1]:
                    if a['features'] != anal:
                        res_anals.append(a)
#                print("  Replacing anals with {}".format(res_anals))
                tok_anal[1] = res_anals
#        print("Copied {} as {}".format(self, s))
        self.altsyns.append(s)
        return s

    def make_record(self, session):
        """Create a SentRecord object to this sentence."""
        return SentRecord(self, session=session)

    ## Initial processing
    
    def segment(self, token, tok_index, verbosity=0):
        """Segment token if possible, replacing it in self.tokens with segmentation."""
        segmentation = self.language.segs.get(token)
        if segmentation:
            self.tokens[tok_index:tok_index+1] = segmentation

    def lowercase(self):
        """Make capitalized tokens lowercase. 2106.05.08: only do this for the first word."""
        self.tokens[0] = self.tokens[0].lower()
#        for index, token in enumerate(self.tokens):
#            if token.istitle():
#                self.tokens[index] = token.lower()

    def preprocess(self, verbosity=0):
        """Segment contractions, and lowercase all words. Must follow word tokenization.
        Segmentation can add to the number of tokens in the sentence."""
        self.lowercase()
        for index, token in zip(range(len(self.tokens)-1, -1, -1), self.tokens[-1::-1]):
#            print('index {}, token {}'.format(index, token))
            self.segment(token, index)

    def initialize(self, ambig=True, verbosity=0):
        """Things to do before running constraint satisfaction."""
        if verbosity:
            print("Initializing {}".format(self))
        self.tokenize(verbosity=verbosity, ambig=ambig)
        # Tokenization could result in altsyns
        self.nodify(verbosity=verbosity)
        self.lexicalize(verbosity=verbosity)
        for s in self.altsyns:
            s.nodify(verbosity=verbosity)
            s.lexicalize(verbosity=verbosity)
        anygroups=False
        for s in [self] + self.altsyns:
            if not s.groups:
                continue
            s.create_variables(verbosity=verbosity)
            s.create_constraints(verbosity=verbosity)
            anygroups=True
        if not anygroups:
            print("Ningunos grupos encontrados para {}".format(self))
            return False
        else:
            return True

    def tokenize(self, ambig=True, verbosity=0):
        """Segment the sentence string into tokens, analyze them morphologically,
        and create a SNode object for each.
        2015.06.07: Save the analyzed tokens as well as nodes.
        2015.06.10: Apply MorphoSyns before creating nodes.
        2015.06.11: If incl_del is True, create nodes for elements deleted by MorphoSyns.
        2015.07: Document normally does the tokenization, so only morphological
        analysis and morphosyn matching happen here.
        2015.07.29: Segmentation and lowercasing of first word.
        2015.10.17: Added copy() possibility when there is morphosyntactic ambiguity.
        ambig option determines whether this happens.
        """
        if verbosity:
            print("Tokenizing {}".format(self))
        if not self.nodes:
            # Don't do this if nodes have already been created.
            # Split at spaces by default (later allow for dedicated language-specific tokenizers).
            if not self.tokens:
                self.tokens = self.raw.split()
            # Lowercase capitalized words and segment contractions, possibly adding new tokens.
            self.preprocess()
            # Do morphological analysis (added 2015.06.07)
            self.analyses = [[token, self.language.anal_word(token)] for token in self.tokens]
            # Then run MorphoSyns on analyses to collapse syntax into morphology where relevant for target
            if verbosity:
                print("Running Morphosyns for {} on {}".format(self.language, self))
            for mi, ms in enumerate(self.language.ms):
                # If ms applies and is "ambiguous", create a new copy of the sentence and add to altsyns
                # (this happens in MorphoSyn)
                if ms.apply(self, ambig=ambig, verbosity=verbosity):
                    scopy = self.altsyns[-1]
                    print("{} copied sentence: {}".format(ms, scopy))
                    for ms1 in self.language.ms[mi+1:]:
                        ms1.apply(scopy, ambig=ambig, verbosity=verbosity)

    def nodify(self, incl_del=False, verbosity=0):
        """Create nodes for sentence.
        2015.10.17: Split off from tokenize().
        """
        self.nodes = []
        index = 0
#        incorp_indices = []
        del_indices = {}
        for tokindex, (token, anals) in enumerate(self.analyses):
            if not incl_del and MorphoSyn.del_token(token):
                # Ignore elements deleted by MorphoSyns
                if anals and 'target' in anals[0]:
                    target_index = tokindex + anals[0]['target']
                else:
                    # Find the next element that's not deleted; that's the target
                    dist = 1
                    for tok, an in self.analyses[tokindex + 1:]:
                        if not MorphoSyn.del_token(tok):
                            break
                        else:
                            dist += 1
                    target_index = tokindex + dist
                if target_index in del_indices:
                    del_indices[target_index].append(tokindex)
                else:
                    del_indices[target_index] = [tokindex]
#                incorp_indices.append(tokindex)
#                del_indices.append(tokindex)
                continue
            if anals:
                # Multiple dicts: ambiguity; let node handle it
                # Get cats
                for anal in anals:
                    root = anal['root']   # there has to be one of these
                    cats = self.language.get_cats(root)
                    if cats:
                        anal['cats'] = cats
                    features = anal['features']
                    pos = features.get('pos') if features else ''
                    if pos:
                        anal['pos'] = pos
                raw_indices = del_indices.get(tokindex, [])
#                if raw_indices:
#                    print("Adding del indices {} to SNode: {}:{}".format(raw_indices, token, index))
                raw_indices.append(tokindex)
#                incorp_indices.append(tokindex)
                self.nodes.append(SNode(token, index, anals, self, raw_indices))
#                                        incorp_indices, del_indices=del_indices.get(tokindex, [])))
#                incorp_indices = []
#                del_indices = []
                index += 1
            else:
                # No analysis, just use the raw string
                # First check for categories
                cats = self.language.get_cats(token)
                if cats:
                    anals = [{'cats': cats}]
                elif token.istitle():
                    # If token is capitalized, it's a name.
                    anals = [{'cats': ['$nm']}]
                else:
                    anals = None
                self.nodes.append(SNode(token, index, anals, self, [tokindex]))
                incorp_indices = []
                index += 1

    def split(self):
        """Split the raw sentence into words, separating off punctuation."""

    def lexicalize(self, verbosity=0):
        """Find and instantiate all groups that are compatible with the tokens in the sentence."""
        if verbosity:
            print("Lexicalizing {}".format(self))
        if not self.nodes:
            print("Tokenization must precede lexicalization.")
            return
        candidates = []
        for index, node in enumerate(self.nodes):
            # Get keys into lexicon for this node
            keys = [node.token]
            if index == 0:
                # For first word in sentence, try both capitalized an uncapitalized versions.
                keys.append(node.token.capitalize())
            anals = node.analyses
            if anals:
                if not isinstance(anals, list):
                    # Is this still possible?
                    anals = [anals]
                for a in anals:
                    root = a.get('root')
                    if root not in keys:
                        keys.append(root)
#                    keys.add(root)
                    pos = a.get('pos')
                    if pos and '_' not in root:
                        k = root + '_' + pos
                        if k not in keys:
                            keys.append(k)
#                        keys.add(root + '_' +pos)
            # Look up candidate groups in lexicon
            for k in keys:
                if k in self.language.groups:
                    for group in self.language.groups[k]:
#                        print("Checking group {} for {}".format(group, node))
                        # Reject group if it doesn't have a translation in the target language
                        if self.target and not group.get_translations():
                            print("No translation for {}".format(group))
                            continue
                        candidates.append((node.index, k, group))
        # Now filter candidates to see if all words are present in the sentence
        # For each group, save a list of sentence token indices that correspond
        # to the group's words
#        print("{} candidatos para grupos encontrados".format(len(candidates)))
        groups = []
        matched_keys = []
        for head_i, key, group in candidates:
            # Matching snodes, along with root and unified features if any
            if verbosity > 1:
                print("Matching group {}".format(group))
            if (head_i, key) in matched_keys:
                # Already matched one for this key, so don't bother checking.
                if verbosity:
                    print("Not considering {} because already matched group with key {}".format(group, key))
                continue
            snodes = group.match_nodes(self.nodes, head_i, verbosity=verbosity)
            if not snodes:
                # This group is out
                if verbosity > 1:
                    print("Failed to match")
                continue
#            print("{} matched with snodes {}".format(group, snodes))
            matched_keys.append((head_i, key))
            if verbosity > 1:
                print('Group {} matches snodes {}'.format(group, snodes))
            groups.append((head_i, snodes, group))
#        print("Matched groups: {}".format(groups))
        # Create a GInst object and GNodes for each surviving group
        self.groups = [GInst(group, self, head_i, snodes, index) for index, (head_i, snodes, group) in enumerate(groups)]
        print("{} grupo(s) encontrado(s) para {}".format(len(self.groups), self))
        for g in self.groups:
            print("  {}".format(g))
        # Assign sentence-level indices to each GNode; store gnodes in list
        sent_index = 0
        for group in self.groups:
            for gnode in group.nodes:
                gnode.sent_index = sent_index
                self.gnodes.append(gnode)
                sent_index += 1
        # Number of GNodes
        self.ngnodes = sent_index
        # Record uncovered snodes
        covered = {}
        for gnode in self.gnodes:
            si = gnode.snode_indices
            for i in si:
                if i not in covered:
                    covered[i] = []
                covered[i].append(gnode.sent_index)
        for snode in self.nodes:
            gnodes = covered.get(snode.index, [])
            snode.gnodes = gnodes
            if gnodes:
                self.covered_indices.append(snode.index)

    ## Solving: parsing and translation

    def solve(self, translate=True, all_sols=False, all_trans=True, interactive=False,
              verbosity=0, tracevar=None):
        """Generate solutions (for all analyses if all_sols is True) and translations (if translate is True)."""
        self.solve1(translate=translate, all_sols=all_sols, all_trans=all_trans, interactive=interactive,
                    verbosity=verbosity, tracevar=tracevar)
        if all_sols:
            for s in self.altsyns:
                s.solve1(translate=translate, all_sols=all_sols, all_trans=all_trans, interactive=interactive,
                         verbosity=verbosity, tracevar=tracevar)
    
    def solve1(self, translate=True, all_sols=False, all_trans=True, interactive=False,
              verbosity=0, tracevar=None):
        """Generate solutions and translations (if translate is true)."""
        if not self.groups:
            print("NINGUNOS GRUPOS encontrados para {}, así que NO HAY SOLUCIÓN POSIBLE".format(self))
            return
        print("Solving {}".format(self))
#        if self.altsyns:
#            print("Alt analyses: {}".format(self.altsyns))
        ds = None
        generator = self.solver.generator(test_verbosity=verbosity, expand_verbosity=verbosity,
                                          tracevar=tracevar)
        try:
            proceed = True
            while proceed:
                succeeding_state = next(generator)
                ds = succeeding_state.dstore
                solution = self.create_solution(dstore=ds, verbosity=verbosity)
                if verbosity:
                    print('FOUND ANALYSIS', solution)
                if translate and self.target:
                    solution.translate(verbosity=verbosity, all_trans=all_trans, interactive=interactive)
                else:
#                if not translate:
                    # Display the parse
                    self.display(show_all_sols=False)
                if all_sols:
                    continue
                if not interactive or not input('SEARCH FOR ANOTHER ANALYSIS? [yes/NO] '):
                    proceed = False
        except StopIteration:
            if verbosity:
                print('No more solutions')
        if not self.solutions:
            print("Last DS: {}".format(ds))
            print("NINGUNAS SOLUCIONES encontradas para {}".format(self))

    def translate(self, sol_index=-1, all_trans=False, verbosity=0):
        """Translate the solution with sol_index or all solutions if index is negative."""
        solutions = self.solutions if sol_index < 0 else [self.solutions[sol_index]]
        for solution in solutions:
            solution.translate(all_trans=all_trans, verbosity=verbosity)

    ## Create IVars and (set) Vars with sentence DS as root DS

    def ivar(self, name, domain, ess=False):
        self.variables[name] = IVar(name, domain, rootDS=self.dstore,
                                    essential=ess)

    def svar(self, name, lower, upper, lower_card=0, upper_card=MAX,
             ess=False):
        self.variables[name] = Var(name, lower, upper, lower_card, upper_card,
                                  essential=ess, rootDS=self.dstore)

    def create_variables(self, verbosity=0):
        # All abstract (category) and instance (word or lexeme) gnodes
        catnodes = set()
        instnodes = set()
        for group in self.groups:
            for node in group.nodes:
                if node.cat:
                    catnodes.add(node.sent_index)
                else:
                    instnodes.add(node.sent_index)

        self.svar('groups', set(), set(range(len(self.groups))),
                  # At least 1, at most all groups
                  1, len(self.groups),
                  ess=True)
        self.svar('gnodes', set(), set(range(self.ngnodes)),
                  # At least size of smallest group, at most all
                  min([len(g.nodes) for g in self.groups]),
                  self.ngnodes)
        # covered snodes
        covered_snodes = {sn.index for sn in self.nodes if sn.gnodes}
        self.variables['snodes'] = DetVar('snodes', covered_snodes)
        # Category (abstract) nodes
        self.svar('catgnodes', set(), catnodes)
        # Position pairs
        pos_pairs = set()
        for group in self.groups:
            pos_pairs.update(group.pos_pairs())
        self.svar('gnode_pos', set(), pos_pairs)
        ## Create variables for SNodes, GInsts, and GNodes
        for snode in self.nodes:
            snode.create_variables()
        for ginst in self.groups:
            ginst.create_variables()
        for gnode in self.gnodes:
            gnode.create_variables()

    def create_constraints(self, verbosity=0):
        if verbosity:
            print("Creating constraints for {}".format(self))
        # Relation among abstract, concrete, and all gnodes for each snode
        for snode in self.nodes:
            if snode.gnodes:
                # Only do this for covered snodes
                self.constraints.extend(Union([snode.variables['gnodes'],
                                               snode.variables['cgnodes'],
                                               snode.variables['agnodes']]).constraints)
        # Constraints involved groups with category (abstract) nodes
        for group in self.groups:
            if group.nanodes > 0:
                # Only do this for groups with abstract nodes
                # For each group, the set of snodes is the union of the concrete and abstract nodes
                self.constraints.extend(Union([group.variables['gnodes_pos'],
                                               group.variables['agnodes_pos'],
                                               group.variables['cgnodes_pos']]).constraints)
        # The set of category (abstract) nodes used is the union of the category nodes of the groups used
        self.constraints.append(UnionSelection(self.variables['catgnodes'],
                                               self.variables['groups'],
                                               [g.variables['agnodes'] for g in self.groups]))
        # All snodes must have distinct category nodes
        self.constraints.extend(Disjoint([sn.variables['agnodes'] for sn in self.nodes]).constraints)
        # All position constraints for snodes
        self.constraints.append(PrecedenceSelection(self.variables['gnode_pos'],
                                                    [gn.variables['snodes'] for gn in self.gnodes]))
        # Position constraint pairs are the group position pairs for all groups used
        self.constraints.append(UnionSelection(self.variables['gnode_pos'],
                                               self.variables['groups'],
                                               [DetVar("g{}pos".format(g.index), g.pos_pairs()) for g in self.groups]))
        # Union selection on gnodes for each snode:
        #  the union of the snode indices associated with the gnodes of an snode is the snode's index
        gn2s = [gn.variables['snodes'] for gn in self.gnodes]
        s2gn = [s.variables['gnodes'] for s in self.nodes]
        for snode in self.nodes:
            if snode.gnodes:
                # Only for covered snodes
                self.constraints.append(UnionSelection(DetVar("sn{}".format(snode.index), {snode.index}),
                                                       snode.variables['gnodes'],
                                                       gn2s))
        # Union of all gnodes used for snodes is all gnodes used
        self.constraints.append(UnionSelection(self.variables['gnodes'],
                                               self.variables['snodes'],
                                               s2gn))
        # Union of all gnodes for groups used is all gnodes used
        self.constraints.append(UnionSelection(self.variables['gnodes'],
                                               self.variables['groups'],
                                               [g.variables['gnodes'] for g in self.groups]))
        # Union of all snodes for gnodes used is all snodes
        self.constraints.append(UnionSelection(self.variables['snodes'],
                                               self.variables['gnodes'],
                                               [gn.variables['snodes'] for gn in self.gnodes]))
        # Complex union selection by groups on positions of all concrete gnodes in each selected group
        self.constraints.append(ComplexUnionSelection(selvar=self.variables['groups'],
                                                      selvars=[g.variables['cgnodes_pos'] for g in self.groups],
                                                      seqvars=[s.variables['cgnodes'] for s in self.nodes],
                                                      mainvars=[g.variables['cgnodes'] for g in self.groups]))
        # Complex union selection by groups on positions of all category gnodes in each selected group
        self.constraints.append(ComplexUnionSelection(selvar=self.variables['groups'],
                                                      selvars=[g.variables['agnodes_pos'] for g in self.groups],
                                                      seqvars=[s.variables['agnodes'] for s in self.nodes],
                                                      mainvars=[g.variables['agnodes'] for g in self.groups]))
        # Agreement
#        print("snode variables")
#        for sn in self.nodes:
#            print(' {} variables: {}'.format(sn, sn.variables))
        if any([g.variables.get('agr') for g in self.groups]):
            self.constraints.append(ComplexAgrSelection(selvar=self.variables['groups'],
                                                        seqvars=[gn.variables['snodes'] for gn in self.gnodes],
                                                        featvars=[sn.variables['features'] for sn in self.nodes],
                                                        selvars=[g.variables.get('agr', EMPTY) for g in self.groups]))

    @staticmethod
    def make_tree(group_dict, group_i, tree):
        """Make a tree (a set of snode indices) for the group with index group_i
        by searching for merged groups and their trees in group_dict."""
        if not group_dict[group_i][1]:
            return
        else:
            for mgi in group_dict[group_i][1]:
                tree.update(group_dict[mgi][0])
                Sentence.make_tree(group_dict, mgi, tree)

    # Methods to help constrain search
    def state_eval(self, dstore, var_value, group_size_wt=2):
        """Assign a score to the domain store based on how much the selected variable's value leads to large groups
        and how low the indices are (since preferred analyses have lower indices).
        Changed 2015.09.24, adding second constraint and eliminating number of undetermined esssential variables."""
        # No point in checking dstore since it's the same across states at time of evaluation
        varscore = 0
        if var_value:
            variable, value = var_value
            typ = Sentence.get_var_type(variable)
            if typ == 'sn->gn':
                # sn->gn variables are good to the extent they point to gnodes in large groups
                # and have lower indices (because preferred interpretations are earlier)
                if value:
                    total = 0
                    for gni in value:
                        total += gni
                        gn = self.gnodes[gni]
                        varscore -= gn.ginst.ngnodes
                    av = total / len(value)
                    varscore /= len(value)
                    varscore += av
            elif typ == 'groups':
                # groups variable is good if it's big and has lower indices
                if value:
                    total = 0
                    for gi in value:
                        total += gi
                        group = self.groups[gi]
                        varscore += group.ngnodes
                    av = total / len(value)
                    varscore /= len(value)
                    varscore += av
#            print(" Varscore for {} with {} in {}: {}".format(variable, value, dstore, varscore))
        # Tie breaker
        ran = random.random() / 100.0
        return varscore + ran
    #undet_count + group_size_wt*varscore + ran # - multiword_groups + len(group_upper_indices)

    @staticmethod
    def get_var_type(variable):
        name = variable.name
        if 'groups' in name:
            return 'groups'
        if '->gn' in name:
            return 'sn->gn'
        return None

    def get_w2gn_vars(self, undecvars, dstore):
        """Given a set of undecided variables in a domain store, find a snode->gnode variable
        that has at last one value that is part of a group with more than one node and
        at least one other value that is part of a group with only one node. Use this
        to select variable and values in search (distribution).
        """
#        group_var = self.variables['groups']
#        print("Values for group var {}, {}".format(group_var.get_upper(dstore), group_var.get_lower(dstore)))
        variables = [node.variables.get('gnodes') for node in self.nodes]
        # Variable whose possible values are tuples of gnodes for individual groups
        gn_pos = self.variables.get('gnode_pos')
        if gn_pos:
            gn_pairs = gn_pos.get_upper(dstore=dstore)
            for var in variables:
                if var not in undecvars:
                    continue
                # gnode indices that are in pairs or not in pairs
                inpair = []
                notinpair = []
                varundec = var.get_undecided(dstore=dstore)
                for value in varundec:
                    if any([value in pair for pair in gn_pairs]):
                        inpair.append(value)
                    else:
                        notinpair.append(value)
                if inpair and notinpair:
                    prefval = inpair[0]
                    return var, {prefval}, varundec - {prefval}

    def create_solution(self, dstore=None, verbosity=0):
        """Assuming essential variables are determined in a domain store, make a Solution object.
        Adds solution to self.solutions and also returns the solution."""
        dstore = dstore or self.dstore
        # Get the indices of the selected groups
        groups = self.variables['groups'].get_value(dstore=dstore)
        ginsts = [self.groups[g] for g in groups]
        s2gnodes = []
        for node in self.nodes:
#            print("Creating solution for {}, gnodes {}".format(node, node.variables['gnodes'].get_value(dstore=dstore)))
            gnodes = list(node.variables['gnodes'].get_value(dstore=dstore))
            s2gnodes.append(gnodes)
        # Create trees for each group
        tree_attribs = {}
        for snindex, sg in enumerate(s2gnodes):
            for gn in sg:
                gnode = self.gnodes[gn]
#                print("  Creating solution for {}: {}".format(snindex, gnode))
                gn_group = gnode.ginst.index
                if gn_group not in tree_attribs:
                    tree_attribs[gn_group] = [[], []]
                tree_attribs[gn_group][0].append(snindex)
            if len(sg) == 2:
                # Record group merger when an snode is associated with two gnodes
                gn0, gn1 = self.gnodes[sg[0]], self.gnodes[sg[1]]
                group0, group1 = gn0.ginst.index, gn1.ginst.index
                if gn0.cat:
                    # Group for gnode0 is merged with group for gnode1
                    tree_attribs[group0][1].append(group1)
                else:
                    tree_attribs[group1][1].append(group0)
#        print("Tree attribs {}".format(tree_attribs))
        for gindex, sn in tree_attribs.items():
            # First store the group's own tree as a set of sn indices
            sn.append(set(sn[0]))
            # Next check for mergers
            Sentence.make_tree(tree_attribs, gindex, sn[2])
#        print("Tree attribs {}".format(tree_attribs))
        # Convert the dict to a list and sort by group indices
        trees = list(tree_attribs.items())
        trees.sort(key=lambda x: x[0])
        # Just keep the snode indices in each tree
        trees = [x[1][2] for x in trees]
        # Get the indices of the GNodes for each SNode
        solution = Solution(self, ginsts, s2gnodes, len(self.solutions),
                            trees=trees, dstore=dstore, session=self.session)
        self.solutions.append(solution)
        return solution

    ### Various ways of displaying translation outputs.
    
    def set_trans_outputs(self):
        """Combine the tree trans outputs from all solutions, excluding repeated ones."""
        if not self.solutions:
            return
        for solution in self.solutions:
            t1 = solution.get_ttrans_outputs()
            for tt1 in t1:
                if tt1 not in self.trans_outputs:
                    self.trans_outputs.append(tt1)
        self.trans_outputs.sort()

    def get_complete_trans(self, capfirst=True):
        """Produce complete translations (list of lists of strings) from tree trans outputs for solutions, filling
        in gaps with source words where necessary."""
        if self.complete_trans:
            return self.complete_trans
        trans = []
        for solution in self.solutions:
            tt = solution.get_ttrans_outputs()
            tt_complete = []
            end_index = -1
            for indices, forms in tt:
                start, end = indices[0], indices[-1]
                if start > end_index+1:
                    # Some word(s) not translated; use source forms with # prefix
                    verbatim = [self.verbatim(n) for n in self.nodes[end_index+1:start]]
                    tt_complete.append([' '.join(verbatim)])
#                    tt_complete.append([self.verbatim(n) for n in self.nodes[end_index+1:start]])
                tt_complete.append(forms)
                end_index = end
            if end_index+1 < len(self.nodes):
                # Some word(s) not translated; use source forms with # prefix
                verbatim = [self.verbatim(n) for n in self.nodes[end_index+1:len(self.nodes)]]
                tt_complete.append([' '.join(verbatim)])
            if capfirst:
                # Capitalize first word
                tt_complete[0] = [Sentence.capitalize(w) for w in tt_complete[0]]
            trans.append(tt_complete)
        self.complete_trans = trans
        return trans

    def get_html(self):
        """Create HTML for a sentence with no solution."""
        return [(self.raw, "Silver", "<table border=1></table>")]
        
    def verbatim(self, node):
        """Use the source token in the target complete translation."""
        # If token consists of only punctuation or digits, just return it
        token = node.token
        if token[0].isdigit() or token[0] in self.language.morphology.punctuation:
            return token
        else:
            return '#' + token

    @staticmethod
    def capitalize(token):
        if token[0] == '#':
            return '#' + token[1:].capitalize()
        elif '|' in token:
            return '|'.join([t.capitalize() for t in token.split('|')])
        return token.capitalize()

class Solution:
    
    """A non-conflicting set of groups for a sentence, at most one instance
    GNode for each sentence token, exactly one sentence token for each obligatory
    GNode in a selected group. Created when a complete variable assignment
    is found for a sentence."""

    def __init__(self, sentence, ginsts, s2gnodes, index, trees=None, dstore=None, session=None):
        self.sentence = sentence
        # Source language
        self.source = sentence.language
        # List of sets of gnode indices
        self.s2gnodes = s2gnodes
        self.ginsts = ginsts
        self.trees = trees
        self.index = index
        # A list of pairs for each snode: (gnodes, features)
        self.gnodes_feats = []
##        # List of Translation objects; multiple translations are possible
##        # for a given solution because of multiple translations for groups
##        self.translations = []
        # A list of TreeTrans objects making up this solution
        self.ttrans = None
        self.ttrans_outputs = None
        # Variable domain store for solution state
        self.dstore = dstore
        # List of SolSegs, sentence segments with translations
        self.segments = []
        # Current session (need for creating SegRecord objects)
        self.session = session
        print("Created solution with dstore {} and ginsts {}".format(dstore, ginsts))

    def __repr__(self):
        return "|< {} >|({})".format(self.sentence.raw, self.index)

    def display(self, word_width=10):
        """Show solution groups (GInsts) in terminal."""
        for g in self.ginsts:
            g.display(word_width=word_width, s2gnodes=self.s2gnodes)

    def get_ttrans_outputs(self):
        """Return a list of (snode_indices, translation_strings) for the solution's tree translations."""
        if not self.ttrans_outputs:
            self.ttrans_outputs = []
            last_indices = [-1]
            for tt in self.treetranss:
                if not tt.output_strings:
                    continue
                indices = tt.snode_indices
                raw_indices = []
                for index in indices:
                    node = self.sentence.nodes[index]
                    raw1 = node.raw_indices
                    raw_indices.extend(raw1)
                raw_indices.sort()
                self.ttrans_outputs.append([raw_indices, tt.output_strings])
                last_indices = raw_indices
        return self.ttrans_outputs

    def get_segs(self):
        """Set the segments (instances of SolSegment) for the solution, including their translations."""
        tt = self.get_ttrans_outputs()
        end_index = -1
        max_index = -1
        tokens = self.sentence.tokens
        for raw_indices, forms in tt:
            late = False
            start, end = raw_indices[0], raw_indices[-1]
#            print("Segment {}->{}".format(start, end))
            if start > max_index+1:
                # there's a gap between the farthest segment to the right and this one; make an untranslated segment
                src_tokens = tokens[end_index+1:start]
                seg = SolSeg(self, (end_index+1, start-1), [], src_tokens, session=self.session)
                self.segments.append(seg)
#            src_tokens = tokens[start:end+1]
            if start < max_index:
#                print("Segment {} / {} actually appears earlier".format(raw_indices, forms))
                late = True
            # There may be gaps in the source tokens for a group; fill these with ...
            src_tokens = [(tokens[i] if i in raw_indices else '...') for i in range(start, end+1)]
            if late:
                src_tokens[0] = "←" + src_tokens[0]
            seg = SolSeg(self, raw_indices, forms, src_tokens, session=self.session)
            self.segments.append(seg)
            max_index = max(max_index, end)
            end_index = end
        if max_index+1 < len(tokens):
            # Some word(s) at beginning not translated; use source forms with # prefix
            src_tokens = tokens[max_index+1:len(tokens)]
            seg = SolSeg(self, (max_index+1, len(tokens)-1), [], src_tokens, session=self.session)
            self.segments.append(seg)
        self.seg_html()

    def seg_html(self):
        for i, segment in enumerate(self.segments):
            segment.set_html(i)

    def get_seg_html(self):
        return [segment.html for segment in self.segments]

    def translate(self, verbosity=0, all_trans=False, interactive=False):
        """Do everything you need to create the translation."""
        self.merge_nodes(verbosity=verbosity)
        for ginst in self.ginsts:
            if ginst.translations:
                if verbosity:
                    print("{} translations already set in other solution".format(ginst))
            else:
                ginst.set_translations(verbosity=verbosity)
        self.make_translations(verbosity=verbosity, all_trans=all_trans, interactive=interactive)

    def merge_nodes(self, verbosity=0):
        """Merge the source features of cat and inst GNodes associated with each SNode."""
        if verbosity:
            print("Merging target nodes for {}".format(self))
        for snode, gn_indices in zip(self.sentence.nodes, self.s2gnodes):
#            print("snode {}, gn_indices {}".format(snode, gn_indices))
            # gn_indices is either one or two ints indexing gnodes in self.gnodes
            gnodes = [self.sentence.gnodes[index] for index in gn_indices]
            features = []
            for gnode in gnodes:
#                print("  gnode {}, snode_anal {}, snode_indices {}".format(gnode, gnode.snode_anal, gnode.snode_indices))
                snode_indices = gnode.snode_indices
#                if snode.index in snode_indices:
                snode_index = snode_indices.index(snode.index)
                snode_anal = gnode.snode_anal[snode_index]
                if snode_anal:
#                    print("snode_anal {}".format(snode_anal))
                    features.append(snode_anal[1])
            # Could this fail??
            features = FeatStruct.unify_all(features)
            self.gnodes_feats.append((gnodes, features))

    def make_translations(self, verbosity=0, display=True, all_trans=False, interactive=False):
        """Create a TreeTrans object for each GInst and tree. build() each top TreeTrans and
        realize translation."""
        if verbosity:
            print("Making translations for {} with ginsts {}".format(self, self.ginsts))
            for g in self.ginsts:
                for t in g.translations:
                    print("  {}".format(t))
        # Create TreeTrans instances here
        abs_gnode_dict = {}
        gnode_dict = {}
        treetranss = []
        ttindex = 0
        for tree, ginst in zip(self.trees, self.ginsts):
            if ginst.treetrans and ginst.treetrans.top and ginst.treetrans.solution == self:
                # There's a treetrans already and it's not the result of a merger,
                # so just use it rather than creating a new one.
                print("Not recreating treetrans for {}".format(ginst))
                treetranss.append(ginst.treetrans)
            else:
                # Figure the various features for the next TreeTrans instance.
                is_top = not any([(tree < other_tree) for other_tree in self.trees])
                group_attribs = []
                for tgroup, tgnodes, tnodes in ginst.translations:
#                    print("TGROUP {}, TGNODES {}, TNODES {}".format(tgroup, tgnodes, tnodes))
                    for tgnode, tokens, feats, agrs, t_index in tgnodes:
                        if tgnode.cat:
                            if tgnode in abs_gnode_dict:
                                abs_gnode_dict[tgnode].append((tgroup, tokens, feats, agrs, t_index))
                            else:
                                abs_gnode_dict[tgnode] = [(tgroup, tokens, feats, agrs, t_index)]
                        elif tgnode in gnode_dict:
                            gnode_dict[tgnode].append((tgroup, tokens, feats, agrs, t_index))
                        else:
                            gnode_dict[tgnode] = [(tgroup, tokens, feats, agrs, t_index)]
                    group_attribs.append((tgroup, tnodes, tgroup.agr, tgnodes))

                treetrans = TreeTrans(self, tree=tree.copy(),
                                      ginst=ginst, # attribs=ginst.translations,
                                      gnode_dict=gnode_dict, abs_gnode_dict=abs_gnode_dict, group_attribs=group_attribs,
                                      index=ttindex, top=is_top)
                treetranss.append(treetrans)
                ttindex += 1
        self.treetranss = treetranss
        for tt in treetranss:
            if tt.outputs:
                print("TreeTrans {} already processed".format(tt))
                tt.display_all()
            elif tt.top:
                # Figure out the maximum number of translations of merge nodes and non-merge nodes
                # For non-merge nodes it's the number of translations of the group
                n_trans_nomerge = len(tt.group_attribs)
                n_trans_merge = 1
                merge = [s for s, f in tt.sol_gnodes_feats if len(s) > 1]
                if merge:
                    n_trans_merge = max([max([len(tt.gnode_dict.get(ss,[0])) for ss in s]) for s in merge])
#                print("TT {}: max merge {}, max no merge {}".format(tt, n_trans_merge, n_trans_nomerge))
                for tm_i in range(n_trans_merge):
                    for tnm_i in range(n_trans_nomerge):
#                        print(" Build indices: {}, {}".format(tm_i, tnm_i))
                        tt.build(merge_index=tm_i, nomerge_index=tnm_i, verbosity=verbosity)
                        tt.generate_words()
                        tt.make_order_pairs()
                        tt.create_variables()
                        tt.create_constraints()
                        tt.realize(all_trans=all_trans, interactive=interactive)
                    if all_trans:
                        continue
                    if not interactive or not input('SEARCH FOR ANOTHER TRANSLATION FOR {}? [yes/NO] '.format(tt)):
                        break
