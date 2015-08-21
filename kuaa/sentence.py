#   
#   Mbojereha sentences and how to parse and translate them.
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

import itertools, copy, re, random
from .ui import *
from .cs import *

class Document(list):
    """A ist of of Sentences, split from a text string."""

    id = 0

    start = ['¿', '¡']
    end = ['.', '?', '!']
    markers = [('\"', '\"'), ("(", ")"), ("{", "}")]
    wordsplit = ['—']

    ## regular expressions for matching tokens
    # adjoining punctuation (except .)
    # before: ([{¡¿"*
    # after: )]}!?":;*
    # within: letters and digits, _-+#.'`@$%^&=|
    puncsep_re = re.compile(r"([(\[{¡¿—\"*]*)([\w\-/+#.'`~@$%^&=\|<>]+)([)\]}!?\"*,:;]*)$")
    start_re = re.compile('[—¿¡"(\[]+$')
    poss_end_re = re.compile('[")\]}]{0,2}[?!][)"\]]{0,2}')
    end_re = re.compile('[")\]}]{0,2}\.[.)"\]]{0,2}')

    def __init__(self, language=None, target=None, text='', proc=True):
        self.set_id()
        self.language = language
        self.target = target
        self.text = text
        # Intermediate representations: list of word-like tokens and ints representing types
        self.tokens = []
        list.__init__(self)
        if proc:
            self.process()

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
            # Segment off punctuation 1 characters
            match = Document.puncsep_re.match(token)
            if not match:
                print("Something wrong: {} fails to be an acceptable token".format(token))
                return
            pre, word, suf = match.groups()
            if pre:
                self.tokens.append((pre, 0))
            # Check to see if word ends in . and is not an abbreviation
            if word.endswith('.'):
                if word not in self.language.abbrevs:
                    word = word[:-1]
                    suf = '.' + suf
            self.tokens.append((word, 1))
            if suf:
                self.tokens.append((suf, 2))

    @staticmethod
    def is_sent_start(token):
        return token[0].isupper()

    @staticmethod
    def start_next(tokens):
        # Does a new sentence begin at the start of tokens?
        if not tokens:
            return False
        tok, typ = tokens[0]
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
            token, toktype = self.tokens[tokindex]
            if toktype in (0, 1):
                current_sentence.append((token, toktype))
            # Check whether this is a sentence end
            elif Document.end_re.match(token):
                if not current_sentence:
                    print("Something wrong: sentence end with empty sentence: {}".format(self.tokens[:tokindex]))
                    return
                else:
                    # End sentence
                    current_sentence.append((token, toktype))
                    sentences.append(current_sentence)
                    current_sentence = []
            elif Document.poss_end_re.match(token):
                if current_sentence and (tokindex == ntokens-1 or Document.start_next(self.tokens[tokindex:])):
                    # End sentence
                    current_sentence.append((token, toktype))
                    sentences.append(current_sentence)
                    current_sentence = []
                else:
                    current_sentence.append((token, toktype))
            else:
                current_sentence.append((token, toktype))
            tokindex += 1
        # Make Sentence objects for each list of tokens and types
        for sentence in sentences:
            self.append(Sentence(language=self.language, tokens=sentence, target=self.target))

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
    tt_colors = ['red', 'blue', 'sienna', 'green', 'purple', 'red', 'blue', 'sienna', 'green', 'purple', 'red', 'blue', 'sienna', 'green', 'purple']

    def __init__(self, raw='', language=None, tokens=None,
                 nodes=None, groups=None, target=None, init=False,
                 verbosity=0):
        self.set_id()
        # A list of string tokens, created by a Document object including this sentence
        # or None if the Sentence is created outside of Document
        if tokens:
            self.tokens = [t[0] for t in tokens]
            self.toktypes = [t[1] for t in tokens]
            self.raw = ' '.join(self.tokens)
        else:
            self.raw = raw
            self.tokens = None
            self.toktypes = None
#        # A string representing the raw sentence (if it hasn't been tokenized)
#        self.raw = raw
        # Source language: a language object
        self.language = language
        # Target language: a language object or None
        self.target = target
        # A list of tuples of analyzed words
        self.analyses = []
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
        if verbosity:
            print("Created Sentence object {}".format(self))
        if init:
            self.initialize()

    def set_id(self):
        self.id = Sentence.id
        Sentence.id += 1

    def __repr__(self):
        """Print name."""
        if self.tokens:
            return '|| ({}) {} ||'.format(self.id, ' '.join(self.tokens))
        elif self.raw:
            return '|| ({}) {} ||'.format(self.id, self.raw)
        else:
            return '|| {} sentence {} ||'.format(self.language, self.id)

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

#    def trans_strings(self, sol_index=-1):
#        """Translation strings for indexed solution or all solutions."""
#        solutions = self.solutions if sol_index < 0 else [self.solutions[index]]
#        strings = []
#        for solution in solutions:
#            strings.extend(solution.trans_strings())
#        return strings

    def segment(self, token, tok_index, verbosity=0):
        """Segment token if possible, replacing it in self.tokens with segmentation."""
        segmentation = self.language.segs.get(token)
        if segmentation:
            self.tokens[tok_index:tok_index+1] = segmentation

    def lowercase(self):
        for index, token in enumerate(self.tokens):
            if token.istitle():
                self.tokens[index] = token.lower()

    def preprocess(self, verbosity=0):
        """Segment contracted expressions, and lowercase all words. Must follow word tokenization.
        Segmentation can add to the number of tokens in the sentence."""
        self.lowercase()
        for index, token in zip(range(len(self.tokens)-1, -1, -1), self.tokens[-1::-1]):
#            print('index {}, token {}'.format(index, token))
            self.segment(token, index)

    def initialize(self, verbosity=0):
        """Things to do before running constraint satisfaction."""
        if verbosity:
            print("Initializing {}".format(self))
        self.tokenize(verbosity=verbosity)
        self.lexicalize(verbosity=verbosity)
        if not self.groups:
            print("Ningunos grupos encontrados para {}".format(self))
            return False
        else:
            self.create_variables(verbosity=verbosity)
            self.create_constraints(verbosity=verbosity)
            return True

    def solve(self, translate=True, all_sols=False, all_trans=True, interactive=False,
              verbosity=0, tracevar=None):
        """Generate solutions and translations (if translate is true)."""
        if not self.groups:
            print("NINGUNOS GRUPOS encontrados para {}, así que NO HAY SOLUCIÓN POSIBLE".format(self))
            return
        generator = self.solver.generator(test_verbosity=verbosity, expand_verbosity=verbosity,
                                          tracevar=tracevar)
        try:
            proceed = True
            while proceed:
                succeeding_state = next(generator)
                solution = self.create_solution(dstore=succeeding_state.dstore, verbosity=verbosity)
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
            print("NINGUNAS SOLUCIONES encontradas para {}".format(self))
#        elif translate and self.target:
#            self.translate(all_trans=all_trans, verbosity=verbosity)

    def translate(self, sol_index=-1, all_trans=False, verbosity=0):
        """Translate the solution with sol_index or all solutions if index is negative."""
        solutions = self.solutions if sol_index < 0 else [self.solutions[sol_index]]
        for solution in solutions:
            solution.translate(all_trans=all_trans, verbosity=verbosity)

    def tokenize(self, incl_del=False, verbosity=0):
        """Segment the sentence string into tokens, analyze them morphologically,
        and create a SNode object for each.
        2015.06.07: Save the analyzed tokens as well as nodes.
        2015.06.10: Apply MorphoSyns before creating nodes.
        2015.06.11: If incl_del is True, create nodes for elements deleted by MorphoSyns.
        2015.07: Document normally does the tokenization, so only morphological
        analysis and morphosyn matching happen here.
        2015.07.29: Segmentation and lowercasing of first word.
        """
        if verbosity:
            print("Tokenizing {}".format(self))
        if not self.nodes:
            # (Otherwise it's already done.)
            # Split at spaces by default (later allow for dedicated language-specific tokenizers).
            if not self.tokens:
                self.tokens = self.raw.split()
            # Lower-case capitalized words and segment contractions, possibly adding new tokens.
            self.preprocess()
            # Next do morphological analysis (2015.06.07)
            self.analyses = [[token, self.language.anal_word(token)] for token in self.tokens]
            # Then run MorphoSyns on analyses to collapse syntax into morphology where relevant for target
            if verbosity:
                print("Running Morphosyns for {} on {}".format(self.language, self))
            for ms in self.language.ms:
                ms.apply(self, verbosity=verbosity)
            self.nodes = []
            index = 0
            incorp_indices = []
            for tokindex, (token, anals) in enumerate(self.analyses):
                if not incl_del and MorphoSyn.del_token(token):
                    # Ignore elements deleted by MorphoSyns
                    incorp_indices.append(tokindex)
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
#                    print("Creating node for {} with incorp_indices {}".format(token, incorp_indices))
                    incorp_indices.append(tokindex)
                    self.nodes.append(SNode(token, index, anals, self, incorp_indices))
                    incorp_indices = []
                    index += 1
                else:
                    # No analysis, just use the raw string
                    # First check for categories
                    cats = self.language.get_cats(token)
                    if cats:
                        anals = [{'cats': cats}]
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
        for node in self.nodes:
            # Get keys into lexicon for this node
            keys = {node.token}
            anals = node.analyses
            if anals:
                if not isinstance(anals, list):
                    # Is this still possible?
                    anals = [anals]
                for a in anals:
                    root = a.get('root')
                    keys.add(root)
                    pos = a.get('pos')
                    if pos:
                        keys.add(root + '_' +pos)
#            print("Found lex keys {} for node {}".format(keys, node))
            # Look up candidate groups in lexicon
            for k in keys:
                if k in self.language.groups:
                    for group in self.language.groups[k]:
#                        print("Checking group {} for {}".format(group, node))
                        # Reject group if it doesn't have a translation in the target language
                        if self.target and not group.get_translations():
                            print("No translation for {}".format(group))
                            continue
                        candidates.append((node.index, group))
#            print("Found candidates {}".format(candidates))
        # Now filter candidates to see if all words are present in the sentence
        # For each group, save a list of sentence token indices that correspond
        # to the group's words
#        print("{} candidatos para grupos encontrados".format(len(candidates)))
        groups = []
        for head_i, group in candidates:
            # Matching snodes, along with root and unified features if any
            if verbosity > 1:
                print("Matching group {}".format(group))
            snodes = group.match_nodes(self.nodes, head_i)
            if not snodes:
                # This group is out
                if verbosity > 1:
                    print("Failed to match")
                continue
            if verbosity > 1:
                print('Group {} matches snodes {}'.format(group, snodes))
            groups.append((head_i, snodes, group))
        # Create a GInst object and GNodes for each surviving group
        self.groups = [GInst(group, self, head_i, snodes, index) for index, (head_i, snodes, group) in enumerate(groups)]
        print("{} grupos encontrados".format(len(self.groups)))
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
        """Assign a score to the domain store based on the number of undetermined essential variables
        and how much the selected variable's value leads to large groups.
        group_size_wt controls how much these two components are weighted in the sum."""
        # No point in checking dstore since it's the same across states at time of evaluation
        varscore = 0
        if var_value:
            variable, value = var_value
            typ = Sentence.get_var_type(variable)
            if typ == 'sn->gn':
                # sn->gn variables are good to the extent they point to gnodes in large groups
                if value:
                    for gni in value:
                        gn = self.gnodes[gni]
                        varscore -= gn.ginst.ngnodes
                    varscore /= len(value)
            elif typ == 'groups':
                # groups variable is good if it's big
                if value:
                    for gi in value:
                        group = self.groups[gi]
                        varscore += group.ngnodes
                    varscore /= len(value)
#            print(" Varscore for {} with {} in {}: {}".format(variable, value, dstore, varscore))
        undet = dstore.ess_undet
        undet_count = len(undet)
#        print(" Undet score for {}: {}".format(dstore, undet_count))
        # Tie breaker
        ran = random.random() / 100.0
        return undet_count + group_size_wt*varscore + ran # - multiword_groups + len(group_upper_indices)

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
            gnodes = list(node.variables['gnodes'].get_value(dstore=dstore))
            s2gnodes.append(gnodes)
        # Create trees for each group
        tree_attribs = {}
        for snindex, sg in enumerate(s2gnodes):
            for gn in sg:
                gnode = self.gnodes[gn]
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
                            trees=trees, dstore=dstore)
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

    def get_sol_segs(self, solution=None):
        """A list of triples: (start/end_within_sentence, translation, snode_tokens)."""
        if not solution:
            if not self.solutions:
                return
            solution = self.solutions[0]
        tt = solution.get_ttrans_outputs()
        tt_segs = []
        end_index = -1
        for indices, forms in tt:
            start, end = indices[0], indices[-1]
            if start > end_index+1:
                src_tokens = self.tokens[end_index+1:start]
                tt_segs.append(((end_index+1, start-1), [], src_tokens))
#                                [n.token for n in self.nodes[end_index+1:start]]))
                # Some word(s) not translated; use source forms with # prefix
#                verbatim = [self.verbatim(n) for n in self.nodes[end_index+1:start]]
#                tt_segs.append([' '.join(verbatim)])
            src_tokens = self.tokens[start:end+1]
            tt_segs.append((indices, forms, src_tokens))
#                            [n.token for n in self.nodes[start:end+1]]))
            end_index = end
        if end_index+1 < len(self.tokens):
#            len(self.nodes):
            # Some word(s) not translated; use source forms with # prefix
            src_tokens = self.tokens[end_index+1:len(self.tokens)]
            tt_segs.append(((end_index+1, len(self.tokens)-1), [], src_tokens))
#                            [n.token for n in self.nodes[end_index+1:len(self.nodes)]]))
        return tt_segs

    def html_segs(self, segs):
        """Convert a list of segments (from the last method) to a list of marked-up phrases."""
        res = []
        for i, (indices, trans, tokens) in enumerate(segs):
            color = 'Silver' if not trans else Sentence.tt_colors[i]
            transhtml = '<table border=1>'
            for t in trans:
                if '|' in t:
                    t = t.replace('|', '<br/>')
                if ' ' in t:
                    transhtml += '<tr>'
                    ts = t.split()
                    for tt in ts:
                        transhtml += '<td>' + tt + '</td>'
                    transhtml += '</tr>'
                else:
                    transhtml += '<tr><td>' + t + '</td></tr>'
            transhtml = transhtml.replace('_', ' ')
            transhtml += '</table>'
            tokens = ' '.join(tokens)
            if i==0:
                tokens = tokens.capitalize()
            res.append((tokens, color, transhtml))
        return res

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

#    @staticmethod
#    def webify_trans(translation):
#        """Make a translation (a list of TreeTrans outputs and verbatim words)
#        into a list more suitable for template processing."""
#        trans = []
#        for tt in translation:
#            # Each tt is the output of a TreeTrans object; a list of alternative translations within a given solution
#            # Mark each as single with or without morphological alternatives,
#            # multiple with or without morphological alternatives
#            mult = False
#            morphalt = False
#            if len(tt) > 1:
#                mult = True
#            tx = []
#            for ttt in tt:
#                # An alternative may be two or more words separated by spaces, but they only need to be separated
#                # if one has alternative morphological outputs separated by '|'
#                if '|' in ttt:
#                    morphalt = True
#                    ttx = []
#                    # Create a sublist separated by spaces
#                    for tttt in ttt.split():
#                        if '|' in tttt:
#                            ttx.append(tttt.split('|'))
#                        else:
#                            ttx.append(tttt)
#                    tx.append(ttx)
#                else:
#                    tx.append(ttt)
#            if mult and morphalt:
#                trans.append([3, tx])
#            elif mult:
#                trans.append([2, tx])
#            elif morphalt:
#                trans.append([1, tx[0]])
#            else:
#                trans.append([0, tx[0]])
#        return trans

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

class SNode:
    """Sentence token and its associated analyses and variables."""

    def __init__(self, token, index, analyses, sentence, raw_indices):
#        print("Creating SNode with args {}, {}, {}, {}".format(token, index, analyses, sentence))
        # Raw form in sentence (possibly result of segmentation)
        self.token = token
        # Position in sentence
        self.index = index
        # Positions in original sentence
        self.raw_indices = raw_indices
        # List of analyses
        if analyses and not isinstance(analyses, list):
            analyses = [analyses]
        self.analyses = analyses
        # Back pointer to sentence
        self.sentence = sentence
        # We'll need these for multiple matchings
        self.cats = self.get_cats()
        # Indices of candidate gnodes for this snode found during lexicalization
        self.gnodes = None
        # Dict of variables specific to this SNode
        self.variables = {}
        ## Tokens in target language for this SNode
        self.translations = []

    def __repr__(self):
        """Print name."""
        return "*{}:{}".format(self.token, self.index)

    ## Create IVars and (set) Vars with sentence DS as root DS

    def ivar(self, key, name, domain, ess=False):
        self.variables[key] = IVar(name, domain, rootDS=self.sentence.dstore,
                                   essential=ess)

    def svar(self, key, name, lower, upper, lower_card=0, upper_card=MAX,
             ess=False):
        self.variables[key] = Var(name, lower, upper, lower_card, upper_card,
                                  rootDS=self.sentence.dstore, essential=ess)

    def lvar(self, key, name, lower, upper, lower_card=0, upper_card=MAX,
             ess=False):
        self.variables[key] = LVar(name, lower, upper, lower_card, upper_card,
                                   rootDS=self.sentence.dstore, essential=ess)

    def create_variables(self, verbosity=0):
        if not self.gnodes:
            # Nothing matched this snode; all variables empty
            self.variables['gnodes'] = EMPTY
            self.variables['cgnodes'] = EMPTY
            self.variables['agnodes'] = EMPTY
#            self.variables['mgnodes'] = EMPTY
            self.variables['features'] = EMPTY
        else:
            # GNodes associated with this SNode: 0, 1, or 2
            self.svar('gnodes', "w{}->gn".format(self.index), set(),
                      set(range(self.sentence.ngnodes)),
                      0, 2, ess=True)
            # Concrete GNodes associated with this SNode: must be 1
            self.svar('cgnodes', "w{}->cgn".format(self.index), set(),
                      {gn.sent_index for gn in self.sentence.gnodes if not gn.cat},
                      1, 1)
            # Abstract GNodes associated with this SNode: 0 or 1
            self.svar('agnodes', "w{}->agn".format(self.index), set(),
                      {gn.sent_index for gn in self.sentence.gnodes if gn.cat},
                      0, 1)
            # Merged concrete GNodes associated with this SNode: 0 or 1
#            self.svar('mgnodes', "w{}->mgn".format(self.index), set(),
#                      {gn.sent_index for gn in self.sentence.gnodes if not gn.cat},
#                      0, 1)
            # Features
            features = self.get_features()
            if len(features) > 1:
                self.lvar('features', 'w{}f'.format(self.index),
                          [], features, 1, 1)
            else:
                # Only one choice so features are determined for this SNode
                self.variables['features'] = DetLVar('w{}f'.format(self.index), features)

    def get_cats(self):
        """The set of categories for the node's token, or None."""
        if not self.analyses:
            return None
        cats = set()
        for analysis in self.analyses:
            if 'cats' in analysis:
                cats.update(analysis['cats'])
        return cats

    def get_features(self):
        """The list of possible FeatStruct objects for the SNode."""
        features = []
        if self.analyses:
            for analysis in self.analyses:
                if 'features' in analysis:
                    features.append(analysis['features'])
                else:
                    features.append(FeatStruct({}))
        return features

    def match(self, grp_item, grp_feats, verbosity=0):
        """Does this node match the group item (word, root, category) and
        any features associated with it?"""
        if verbosity:
            print('   SNode {} with features {} trying to match item {} with features {}'.format(self, self.analyses, grp_item, grp_feats.__repr__()))
        # If item is a category, don't bother looking at token
        if Entry.is_cat(grp_item):
            if verbosity:
                print('    Cat item, looking in {}'.format(self.cats))
            # Check whether this group item is really a set item (starting with '$$'); if so, drop the first '$' before matching
            if Entry.is_set(grp_item):
                grp_item = grp_item[1:]
            if self.cats and grp_item in self.cats:
#                print("   Token {} is in cat {}".format(self.token, grp_item))
                if not self.analyses or not grp_feats:
                    # Match; failure would be False
                    return None
                else:
                    for analysis in self.analyses:
                        node_features = analysis.get('features')
                        if node_features:
                            # 2015.7.5: strict option added to force True feature in grp_features
                            # to be present in node_features, e.g., for Spanish reflexive
                            u_features = simple_unify(node_features, grp_feats, strict=True)
#                            u_features = node_features.unify(grp_feats, strict=True)
#                            print("Unifying {} and {}".format(node_features.__repr__(), grp_feats.__repr__()))
                            if u_features != 'fail':
                                return analysis.get('root'), u_features
#                        print("   Matching group features {} and sentence features {}".format(grp_feats, node_features))
#                        if node_features and node_features.unify(grp_feats) != 'fail':
#                            return True
                    # None succeeded
                    return False
        elif self.token == grp_item:
            # grp_item matches this node's token; features are irrelevant
            return None
        elif self.analyses:
            # Check each combination of root and analysis features
            for analysis in self.analyses:
                root = analysis.get('root', '')
                node_features = analysis.get('features')
                if root == grp_item:
#                    if grp_feats:
#                        print("Matching group item features {} against snode features {}".format(grp_feats.__repr__(), node_features.__repr__()))
                    if not grp_feats:
                        return root, node_features
                    elif not node_features:
                        # Fail because there must be an explicit match with group features
                        return False
#                        return root, grp_feats
                    else:
                        # There must be an explicit match with group features, so strict=True
#                        u_features = node_features.unify(grp_feats, strict=True)
                        u_features = simple_unify(node_features, grp_feats, strict=True)
#                        print("   Unifying node features {} with group features {}".format(node_features.__repr__(), grp_feats.__repr__()))
                        if u_features != 'fail':
#                            print(" Succeeded by unification")
                            return root, u_features
        return False

class GInst:

    """Instantiation of a group; holds variables and GNode objects."""

    def __init__(self, group, sentence, head_index, snode_indices, index):
        # The Group object that this "instantiates"
        self.group = group
        self.sentence = sentence
        self.target = sentence.target
        # Index of group within the sentence
        self.index = index
        # Index of SNode associated with group head
        self.head_index = head_index
#        self.head_pos = group.pos
        # List of GNodes
        self.nodes = [GNode(self, index, indices) for index, indices in enumerate(snode_indices)]
        # Dict of variables specific to this group
        self.variables = {}
        # List of target language groups, gnodes, tnodes
        self.translations = []
        self.ngnodes = len(self.nodes)
        # Number of abstract nodes
        self.nanodes = len([n for n in self.nodes if n.cat])
        # Number of concrete nodes
        self.ncgnodes = self.ngnodes - self.nanodes
        # TreeTrans instance for this GInst; saved here so to prevent multiple TreeTrans translations
        self.treetrans = None

    def __repr__(self):
        return '<<{}:{}>>'.format(self.group.name, self.group.id)

    def display(self, word_width=10, s2gnodes=None):
        """Show group in terminal."""
        s = '<{}>'.format(self.index)
        n_index = 0
        n = self.nodes[n_index]
        ngnodes = len(self.nodes)
        for gn_indices in s2gnodes:
            if n.sent_index in gn_indices:
                i = '*{}*' if n.head else "{}"
                s += i.format(n.index).center(word_width)
                n_index += 1
                if n_index >= ngnodes:
                    break
                else:
                    n = self.nodes[n_index]
            else:
                s += ' '*word_width
        print(s)

    def pos_pairs(self):
        """Return position constraint pairs for gnodes in the group."""
        gnode_pos = [gn.sent_index for gn in self.nodes]
        return set(itertools.combinations(gnode_pos, 2))

    def gnode_sent_index(self, index):
        """Convert gnode index to gnode sentence index."""
        return self.nodes[index].sent_index

    def get_agr(self):
        """Return agr constraints for group, converted to tuples."""
        result = []
        if self.group.agr:
            for a in copy.deepcopy(self.group.agr):
                feats = [tuple(pair) for pair in a[2:]]
                a[2:] = feats
                # Convert gnode positions to sentence positions
                a[0] = self.gnode_sent_index(a[0])
                a[1] = self.gnode_sent_index(a[1])
                result.append(tuple(a))
        return set(result)

    ## Create IVars and (set) Vars with sentence DS as root DS

    def ivar(self, key, name, domain, ess=False):
        self.variables[key] = IVar(name, domain, rootDS=self.sentence.dstore,
                                   essential=ess)

    def svar(self, key, name, lower, upper, lower_card=0, upper_card=MAX,
             ess=False):
        self.variables[key] = Var(name, lower, upper, lower_card, upper_card,
                                  rootDS=self.sentence.dstore,
                                  essential=ess)

    def create_variables(self, verbosity=0):
        ngroups = len(self.sentence.groups)
        nsnodes = len(self.sentence.nodes)
        cand_snodes = self.sentence.covered_indices
#        print("Creating variables for {}, # abs nodes {}".format(self, self.nanodes))
        # GNode indices for this GInst (determined)
        self.variables['gnodes'] = DetVar('g{}->gnodes'.format(self.index), {gn.sent_index for gn in self.nodes})
        # Abstract GNode indices for GInst (determined)
        if self.nanodes:
            self.variables['agnodes'] = DetVar('g{}->agnodes'.format(self.index), {gn.sent_index for gn in self.nodes if gn.cat})
            # Concrete GNode indices for GInst (determined)
            self.variables['cgnodes'] = DetVar('g{}->cgnodes'.format(self.index), {gn.sent_index for gn in self.nodes if not gn.cat})
        else:
            self.variables['agnodes'] = EMPTY
            self.variables['cgnodes'] = self.variables['gnodes']
        # SNode positions of GNodes for this GInst
        self.svar('gnodes_pos', 'g{}->gnodes_pos'.format(self.index),
                  set(), set(cand_snodes), self.ngnodes, self.ngnodes)
        # SNode positions of abstract GNodes for this GInst
        if self.nanodes == 0:
            # No abstract nodes
            self.variables['agnodes_pos'] = EMPTY
            # SNode positions of concrete GNodes for this GInst
            self.variables['cgnodes_pos'] = self.variables['gnodes_pos']
        else:
            # Position for each abstract node in the group
            self.svar('agnodes_pos', 'g{}->agnodes_pos'.format(self.index),
                      set(), set(cand_snodes), self.nanodes, self.nanodes)
            # Position for each concrete node in the group
            self.svar('cgnodes_pos', 'g{}->cgnodes_pos'.format(self.index),
                      set(), set(cand_snodes), self.ncgnodes, self.ncgnodes)
        # Determined variable for within-source agreement constraints, gen: 0}
        agr = self.get_agr()
        if agr:
            self.variables['agr'] = DetVar('g{}agr'.format(self.index), agr)
        
    def set_translations(self, verbosity=0):
        """Find the translations of the group in the target language."""
        translations = self.group.get_translations()
        # Sort group translations by their translation frequency
        Group.sort_trans(translations)
        if verbosity:
            print("Translations {}".format(translations))
            # self.target.abbrev, False)
        # If alignments are missing, add default alignment
        for i, t in enumerate(translations):
            if len(t) == 1:
                translations[i] = [t[0], {}]
#                                    {'align': list(range(len(self.nodes)))}]
        ntokens = len(self.group.tokens)
        for tgroup, s2t_dict in translations:
            nttokens = len(tgroup.tokens)
            if verbosity > 1:
                print(" set_translations(): tgroup {}', s2t_dict {}".format(tgroup, s2t_dict))
            # If there's no explicit alignment, it's the obvious default
            if 'align' in s2t_dict:
                alignment = s2t_dict.get('align')
            else:
                alignment = list(range(ntokens))
                for ia, a in enumerate(alignment):
                    if a >= nttokens:
                        alignment[ia] = -1
            if isinstance(tgroup, str):
                # First find the target Group object
                tgroup = self.target.groupnames[tgroup]
#            print("Alignment: {}".format(alignment))
            # Make any TNodes (for target words not corresponding to any source words)
            tnodes = []
            if nttokens > ntokens:
                # Target group has more nodes than source group.
                # Indices of groups that are not empty:
                full_t_indices = set(alignment)
                empty_t_indices = set(range(nttokens)) - full_t_indices
                for i in empty_t_indices:
                    empty_t_token = tgroup.tokens[i]
                    empty_t_feats = tgroup.features[i] if tgroup.features else None
                    tnodes.append(TNode(empty_t_token, empty_t_feats, self, i))
            # Deal with individual gnodes in the group
            gnodes = []
            tokens = tgroup.tokens
            features = tgroup.features
            # Go through source group nodes, finding alignments and agreement constraints
            # with target group nodes
            for gn_index, gnode in enumerate(self.nodes):
#                print("tgroup {}, gnode {}, gn_index {}".format(tgroup, gnode, gn_index))
                # Align gnodes with target tokens and features
                targ_index = alignment[gn_index]
                if targ_index < 0:
#                    print("No targ item for gnode {}".format(gnode))
                    # This means there's no target language token for this GNode.
                    continue
                agrs = None
                if s2t_dict.get('agr'):
                    agr = s2t_dict['agr'][gn_index]
                    if agr:
                        tindex, stagr = agr
                        targ_index = tindex
#                        print(" s2t_dict agrs {}, tindex {}, stagr {}".format(agrs, tindex, stagr))
#                    agrs = s2t_dict['agr'][targ_index]
                        agrs = stagr
                token = tokens[targ_index]
                feats = features[targ_index] if features else None
                gnodes.append((gnode, token, feats, agrs, targ_index))
            self.translations.append((tgroup, gnodes, tnodes))

class GNode:

    """Representation of a single node (word, position) within a GInst object."""

    def __init__(self, ginst, index, snodes):
#        print("Creating GNode for {} with snodes {}".format(ginst, snodes))
        self.ginst = ginst
        self.index = index
        self.sentence = ginst.sentence
        self.snode_indices = [s[0] for s in snodes]
        self.snode_anal = [s[1] for s in snodes]
        # Whether this is the head of the group
        self.head = index == ginst.group.head_index
        # Group word, etc. associated with this node
        gtoken = ginst.group.tokens[index]
        # If this is a set node, use the sentence token instead of the cat name
        if Entry.is_set(gtoken):
            self.token = self.sentence.nodes[snodes[0][0]].token
        else:
            self.token = gtoken
#        self.pos = ''
#        if self.head:
#            self.pos = self.token.partition('_')[-1]
#        print("Getting POS for GNode: {}, {}".format(self.token, self.pos))
        # Whether the associated token is abstract (a category)
        self.cat = Entry.is_cat(self.token)
        # Features associated with this group node
        groupfeats = ginst.group.features
        if groupfeats:
            self.features = groupfeats[index]
        else:
            self.features = None
        self.variables = {}
        # List of target-language token and features associated with this gnode
#        self.translations = []

    def __repr__(self):
        return "{}|{}".format(self.ginst, self.token)

    ## Create IVars and (set) Vars with sentence DS as root DS

    def ivar(self, key, name, domain, ess=False):
        self.variables[key] = IVar(name, domain, rootDS=self.sentence.dstore,
                                   essential=ess)

    def svar(self, key, name, lower, upper, lower_card=0, upper_card=MAX,
             ess=False):
        self.variables[key] = Var(name, lower, upper, lower_card, upper_card,
                                  rootDS=self.sentence.dstore,
                                  essential=ess)

    def create_variables(self, verbosity=0):
        nsnodes = len(self.sentence.nodes)
        # SNode index for this GNode
        self.ivar('snodes', "gn{}->w".format(self.sent_index), set(self.snode_indices))

class TNode:

    """Representation of a node within a target language group that doesn't
    have a corresponding node in the source language group that it's the
    translation of."""

    def __init__(self, token, features, ginst, index):
        self.token = token
        self.features = features
        self.ginst = ginst
        self.sentence = ginst.sentence
        self.index = index

    def generate(self, verbosity=0):
        """Generate forms for the TNode."""
        print("Generating form for target token {} and features {}".format(self.token, self.features))
        if Entry.is_lexeme(self.token):
            return self.sentence.target.generate(self.token, self.features)
        else:
            return [self.token]

    def __repr__(self):
        return "~{}|{}".format(self.ginst, self.token)

class Solution:
    
    """A non-conflicting set of groups for a sentence, at most one instance
    GNode for each sentence token, exactly one sentence token for each obligatory
    GNode in a selected group. Created when a complete variable assignment
    is found for a sentence."""

    def __init__(self, sentence, ginsts, s2gnodes, index, trees=None, dstore=None):
        self.sentence = sentence
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
        print("Created solution with ginsts {}".format(ginsts))

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
                self.ttrans_outputs.append((raw_indices, tt.output_strings))
#            self.ttrans_outputs = [((tt.snode_indices[0], tt.snode_indices[-1]), tt.output_strings)\
#                                    for tt in self.treetranss if tt.output_strings]
        return self.ttrans_outputs

#    def trans_strings(self, index=-1):
#        """Return a list of translation strings for the translation indexed or all translations
#        for this solution."""
#        translations = self.translations if index < 0 else [self.translation[index]]
#        strings = []
#        for translation in translations:
#            strings.extend(translation.output_strings)
#        return strings

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
            # gn_indices is either one or two ints indexing gnodes in self.gnodes
            gnodes = [self.sentence.gnodes[index] for index in gn_indices]
            features = []
            for gnode in gnodes:
#                print("gnode {}, snode_anal {}".format(gnode, gnode.snode_anal))
                snode_indices = gnode.snode_indices
                snode_index = snode_indices.index(snode.index)
                snode_anal = gnode.snode_anal[snode_index]
                if snode_anal:
#                    print("snode_anal {}".format(snode_anal))
                    features.append(snode_anal[1])
            # Could this fail??
            features = FeatStruct.unify_all(features)
            self.gnodes_feats.append((gnodes, features))

    def make_translations(self, verbosity=0, display=True, all_trans=False, interactive=False):
        """Combine GInsts for each translation in translation products, and
        separate gnodes into a dict for each translation."""
        if verbosity:
            print("Making translations for {} with ginsts {}".format(self, self.ginsts))
#        for g in self.ginsts:
#            print("Translations ({}) for GInst {}".format(len(g.translations), g))
#            for t in g.translations:
#                print("  {}".format(t))
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
                is_top = not any([(tree < other_tree) for other_tree in self.trees])
                treetrans = TreeTrans(self, tree=tree.copy(),
                                      ginst=ginst, attribs=ginst.translations,
                                      gnode_dict=gnode_dict, abs_gnode_dict=abs_gnode_dict,
                                      index=ttindex, top=is_top)
                treetranss.append(treetrans)
                ttindex += 1
        self.treetranss = treetranss
        for tt in treetranss:
            if tt.outputs:
                print("TreeTrans {} already processed".format(tt))
                tt.display_all()
            else:
                trans_index=0
                built = True
                while built:
                    if verbosity:
                        print("Building {}".format(tt))
                    built = tt.build(trans_index=trans_index)
                    if not built:
                        print("No more translations for {}".format(tt))
                        break
                    if tt.top:
                        tt.generate_words()
                        tt.make_order_pairs()
                        tt.create_variables()
                        tt.create_constraints()
                        tt.realize(all_trans=all_trans, interactive=interactive)
                    trans_index += 1
                    if all_trans:
                        continue
                    if not interactive or not input('SEARCH FOR ANOTHER TRANSLATION FOR {}? [yes/NO] '.format(tt)):
                        break

#        # Now relate treetrans to each other
#        for tt in self.treetranss:
#            tree = tt.tree
#            for tt1 in self.treetranss:
#                if tt1 != tt and tt1.tree < tree:
#                    tt.sub_tts.append(tt1)
#                    tt1.super_tts.append(tt)
#        # This is wrong; there's lots of duplication; each group may be translated multiple times
#        translations = itertools.product(*[g.translations for g in self.ginsts])
#        for index, translation in enumerate(translations):
#            t = Translation(self, translation, index, trees=copy.deepcopy(self.trees), verbosity=verbosity)
#            t.initialize(verbosity=verbosity)
#            t.realize(verbosity=verbosity, display=display, all_trans=all_trans)
#            self.translations.append(t)
#            if all_trans:
#                continue
#            if not input('SEARCH FOR ANOTHER TRANSLATION FOR ANALYSIS {}? [yes/NO] '.format(self)):
#                return
#        if verbosity:
#            print("No more translations for analysis")

class TreeTrans:
    """Translation of a tree: a group or two or more groups joined by merged nodes."""

    def __init__(self, solution, tree=None, ginst=None, abs_gnode_dict=None, gnode_dict=None,
                 attribs=None, index=0, top=False, verbosity=0):
        # The solution generating this translation
        self.solution = solution
        self.sentence = solution.sentence
        # Dict keeping information about each gnode; this dict is shared across different TreeTrans instances
        self.abs_gnode_dict = abs_gnode_dict
        self.gnode_dict = gnode_dict
#        # TreeTrans instances under this one within the same tree
#        self.sub_tts = []
#        # TreeTrans instance above this one if any within the same tree
#        self.super_tts = []
        # A set of sentence node indices
        self.tree = tree
        # Whether this is the top of a tree
        self.top = top
        # Merged group indices
        self.mergers = []
        snode_indices = list(tree)
        snode_indices.sort()
        self.snode_indices = snode_indices
        self.snodes = [self.sentence.nodes[i] for i in snode_indices]
        self.sol_gnodes_feats = [solution.gnodes_feats[i] for i in snode_indices]
        self.nodes = []
        # The GInst at the top of the tree
        self.ginst = ginst
        # Save this TreeTrans in the GInst
        ginst.treetrans = self
        self.index = index
        # A list of triples: (tgroup, tgnodes, tnodes), where
        # gnodes is (tgnode_inst, tnode_string, tnode_feats, agr_pairs, gnode_index)
        self.attribs = attribs
        self.group_attribs = []
#        self.gnode_dict = {}
        for tgroup, tgnodes, tnodes in attribs:
#            print('tgroup {}, tgnodes {}, tnodes {}, ginst {}'.format(tgroup, tgnodes, tnodes, ginst))
            for tgnode, tokens, feats, agrs, t_index in tgnodes:
#                print("Adding to gnode dicts: {}, cat? {}".format(tgnode, tgnode.cat))
                if tgnode.cat:
#                    print(" tgnode {} is abstract".format(tgnode))
                    self.abs_gnode_dict[tgnode] = (tgroup, tokens, feats, agrs, t_index)
                elif tgnode in self.gnode_dict:
                    self.gnode_dict[tgnode].append((tgroup, tokens, feats, agrs, t_index))
#                    print(" tgnode {} already in gnode_dict with value {}".format(tgnode, self.gnode_dict[tgnode]))
                else:
#                    print("Adding tgnode {} to gnode_dict".format(tgnode))
                    self.gnode_dict[tgnode] = [(tgroup, tokens, feats, agrs, t_index)]
#                    self.gnode_dict[tgnode] = (tgroup, tokens, feats, agrs, t_index)
            self.group_attribs.append((tgroup, tnodes, tgroup.agr))
#            print("Tgroups for TT: {}".format([t[0] for t in self.group_attribs]))
        # Root domain store for variables
        self.dstore = DStore(name="TT{}".format(self.index))
        # Order variables for each node, tree variables for groups
        self.variables = {}
        # pairs of node indices representing order constraints
        self.order_pairs = []
        # Order and disjunction constraints
        self.constraints = []
        self.solver = Solver(self.constraints, self.dstore, description='target tree realization',
                             verbosity=verbosity)
#        # Positions of target words
#        self.positions = []
        # These are produced in self.build()
        self.node_features = None
        self.group_nodes = None
        self.agreements = None
        # Final outputs; different ones have alternate word orders
        self.outputs = []
        # Strings representing outputs
        self.output_strings = []
#        print("Created TreeTrans {} with gnode_dict {}, abs_gnode_dict {}".format(self, self.gnode_dict, self.abs_gnode_dict))

    def __repr__(self):
        return "[{}] ->".format(self.ginst)

    def display(self, index):
        print("{}  {}".format(self, self.output_strings[index]))

    def display_all(self):
        for index in range(len(self.outputs)):
            self.display(index)

    @staticmethod
    def output_string(output):
#        print("Converting output {} to string".format(output))
        l = []
        for word_list in output:
            if len(word_list) == 1:
                l.append(word_list[0])
            else:
                l.append('|'.join(word_list))
        string = ' '.join(l)
        # _ is a placeholder for space
#        string = string.replace('_', ' ')
        return string

#    def initialize(self, verbosity=0):
#        """Set up everything needed to run the constraints and generate the translation."""
#        if verbosity:
#            print("Initializing treetrans {}".format(self))
#        self.build(verbosity=verbosity)
#        self.generate_words(verbosity=verbosity)
#        self.make_order_pairs(verbosity=verbosity)
#        self.create_variables(verbosity=verbosity)
#        self.create_constraints(verbosity=verbosity)

    def build(self, trans_index=0, verbosity=0):
        """Unify translation features for merged nodes, map agr features from source to target,
        generate surface target forms from resulting roots and features."""
        if verbosity:
            print('Building {} with trans index {}'.format(self, trans_index))
        # Reinitialize mergers
        self.mergers = []
        # Dictionary mapping source node indices to initial target node indices
        tnode_index = 0
        node_index_map = {}
        node_features = []
        agreements = {}
        group_nodes = {}
        for snode, (gnodes, features) in zip(self.snodes, self.sol_gnodes_feats):
            if verbosity > 1:
                print(" build(): snode {}, trans_index {}, gnodes {}, features {}, tnode_index {}".format(snode, trans_index,
                                                                                                          gnodes, features.__repr__(), tnode_index))
                print("   gnode_dict: {}".format(self.gnode_dict))
            if not gnodes:
                # snode is not covered by any group
                node_index_map[snode.index] = tnode_index
                node_features.append((snode.token, None, []))
                tnode_index += 1
            else:
                gna, gnc, token = None, None, None
                t_indices = []
                targ_feats, agrs = None, None
                if verbosity:
                    if len(gnodes) > 1:
                        print(" Gnodes: {}".format(gnodes))
                        print(" Abs gnode dict: {}".format(self.abs_gnode_dict))
                if gnodes[0] in self.abs_gnode_dict:
                    if verbosity:
                        print("{}: gnodes {} contain an abs gnode dict in first position".format(self, gnodes))
                        print(" Looking for concrete node in gnode_dict {}".format(self.gnode_dict))
                    gna = self.abs_gnode_dict[gnodes[0]]
                    gnc = self.gnode_dict[gnodes[1]]
                elif len(gnodes) > 1 and gnodes[1] in self.abs_gnode_dict:
                    if verbosity:
                        print("{}: gnodes {} contain an abs gnode dict in second position".format(self, gnodes))
                    gna = self.abs_gnode_dict[gnodes[1]]
                    gnc = self.gnode_dict[gnodes[0]]
                if gna:
#                    print(" gna: {}, gnc: {}".format(gna, gnc))
                    # There are two gnodes for this snode; only the concrete node can have translations
                    # Check if there is no translation for one or the other; if so, skip this snode and
                    # don't increment tnode_index
                    # gna is a single tuple, gnc is a list of tuples for different translations
                    if len(gnc) <= trans_index:
                        if verbosity:
                            print(" No more translations for {}".format(self))
                        return False
                    # Select the tuple to be used (trans_index)
#                    gnc1 = gnc[trans_index]
#                    print(" Selected {}th gnc: {}".format(trans_index, gnc1))
#                    merge_attribs = [zip(gna, gnc1) for gnc1 in gnc]
#                    tgroups, tokens, targ_feats, agrs, t_index = merge_attribs[0]
#                    # The token that's not a cat
#                    token = tokens[1]
#                    targ_feats = FeatStruct.unify_all(targ_feats)
                    # Needs to be fixed; for now it only merges the abstract node with the *first*
                    # translation of the concrete node (that is the first tuple in gnc)
                    if self.top:
#                        if verbosity and len(gnc) > 1:
#                        print("Multiple translations {} for concrete node".format(gnc))
                        gnc1 = gnc[trans_index]
                        tgroups, tokens, targ_feats, agrs, t_index = zip(gna, gnc1)
                        token = tokens[1]
                        targ_feats = FeatStruct.unify_all(targ_feats)
                        # Merge the agreements
                        agrs = TreeTrans.merge_agrs(agrs)
                        t_indices.append((tgroups[0], gna[-1]))
                        t_indices.append((tgroups[1], gnc1[-1]))
                        ## Record this node and its groups in mergers
                        tg = list(zip(tgroups, gnodes))
                        # Sort the groups by which is the "outer" group in the merger
                        tg.sort(key=lambda x: x[1].cat)
                        tg = [x[0] for x in tg]
                        print("Creating merger {} for snode index {}, tnode index {}".format(tg, snode.index, tnode_index))
                        self.mergers.append([tnode_index, tg])
                else:
                    # only one gnode in list
                    gnode = gnodes[0]
                    if gnode not in self.gnode_dict:
                        if verbosity:
                            print("Gnode {} not in gnode dict".format(gnode, self.gnode_dict))
#                        return False
                        continue
                    else:
                        gnode_tuple_list = self.gnode_dict[gnode]
#                        print("Gnode tuple list {}, trans_index {}".format(gnode_tuple_list, trans_index))
                        if len(gnode_tuple_list) <= trans_index:
                            print("No more translations for {}".format(self))
                            return False
#                        tgroup, token, targ_feats, agrs, t_index = self.gnode_dict[gnode]
                        tgroup, token, targ_feats, agrs, t_index = gnode_tuple_list[trans_index]
                        if len(tgroup.tokens) > 1:
                            t_indices.append((tgroup, t_index))
                            
                # Make target and source features agree as required
                if not targ_feats:
                    targ_feats = FeatStruct({})
                if agrs and self.top:
                    # Use an (unfrozen) copy of target features
                    targ_feats = targ_feats.copy(True)
                    features.agree(targ_feats, agrs)
                node_index_map[snode.index] = tnode_index
                tnode_index += 1
                node_features.append((token, targ_feats, t_indices))
                for t_index in t_indices:
                    group_nodes[t_index] = (token, targ_feats)
        # Fix indices in tgroup trees
        tree = []
        for src_index in tree:
            if src_index in node_index_map:
                tree.append(node_index_map[src_index])
        self.tree = tree
        # Add TNode elements
        tgnode_elements = []
        for ginst_i, (tginst, tnodes, agr) in enumerate(self.group_attribs):
#            print("  tginst {}".format(tginst))
            if agr:
                agreements[tginst] = agr
                if verbosity:
                    print(" build(): tginst {} agr {}, agreements {}".format(tginst, agr, agreements))
            if tnodes:
                for tnode in tnodes:
                    features = tnode.features or FeatStruct({})
                    src_index = len(node_features)
                    self.tree.append(src_index)
                    index = [(tginst, tnode.index)]
                    node_features.append((tnode.token, features, index))
                    group_nodes[index[0]] = (tnode.token, features)
        self.node_features = node_features
        self.group_nodes = group_nodes
        self.agreements = agreements
        return True

    @staticmethod
    def get_root_POS(token):
        """Token may be something like guata_, guata_v, or guata_v_t."""
        root, x, pos = token.partition("_")
        return root, pos

    @staticmethod
    def merge_agrs(agr_list):
        """Merge agr dicts in agr_list into a single agr dict."""
#        print("  Merging agreements for merged nodes {}".format(agr_list))
        result = {}
        for agr in agr_list:
            if not agr:
                continue
            for k, v in agr:
                if k in result:
                    if result[k] != v:
                        print("Warning: agrs in {} failed to merge; {} and {} don't match".format(agr_list, result[k], v))
                        return 'fail'
                    else:
                        continue
                else:
                    result[k] = v
#        print("  Result", result)
        return result

    def generate_words(self, verbosity=0):
        """Do inter-group agreement constraints, and generate wordforms for each target node."""
#        print('Generating words for {}'.format(self))
        # Reinitialize nodes
        self.nodes = []
        for group, agr_constraints in self.agreements.items():
            for agr_constraint in agr_constraints:
                i1, i2 = agr_constraint[0], agr_constraint[1]
                feature_pairs = agr_constraint[2:]
                # Find the sentence nodes for the agreeing group nodes in the group_nodes dict
                agr_node1 = self.group_nodes[(group, i1)]
                agr_node2 = self.group_nodes[(group, i2)]
#                print("Found node1 {} and node2 {} for constraint {}".format(agr_node1, agr_node2, feature_pairs))
                agr_feats1, agr_feats2 = agr_node1[1], agr_node2[1]
                agr_feats1.mutual_agree(agr_feats2, feature_pairs)
        generator = self.sentence.target.generate
        for token, features, index in self.node_features:
            if verbosity:
                print("Token {}, features {}, index {}".format(token, features.__repr__(), index))
            root, pos = TreeTrans.get_root_POS(token)
            output = [token]
            if not pos:
                # This word doesn't require generation, just return it in a list
                self.nodes.append((output, index))
            else:
#                print("Generating {} : {} : {}".format(root, features.__repr__(), pos))
                output = generator(root, features, pos=pos)
                self.nodes.append((output, index))
            if verbosity:
                print("Generating target node {}: {}".format(index, output))
#        print("nodes after generation: {}".format(self.nodes))

    def make_order_pairs(self, verbosity=0):
        """Convert group/index pairs to integer (index) order pairs.
        Constrain order in merged groups."""
        # Reinitialize order pairs
        self.order_pairs.clear()
#        print("Ordering pairs for {}, mergers {}, nodes {}".format(self, self.mergers, self.nodes))
        tgroup_dict = {}
        for index, (forms, constraints) in enumerate(self.nodes):
#            print("Order pairs for node {} with forms {} and constraints {}".format(index, forms, constraints))
#            print("Constraints {} for tdict {}".format(index, constraints))
            for tgroup, tg_index in constraints:
                if tgroup not in tgroup_dict:
                    tgroup_dict[tgroup] = []
                tgroup_dict[tgroup].append((index, tg_index))
        for pairs in tgroup_dict.values():
            for pairpair in itertools.combinations(pairs, 2):
                pairpair = list(pairpair)
                # Sort by the target index
                pairpair.sort(key=lambda x: x[1])
                self.order_pairs.append([x[0] for x in pairpair])
        # Order nodes within merged groups
        for node, (inner, outer) in self.mergers:
#            print("Merger: tnode index {}, inner group {}, outer group {}".format(node, inner, outer))
            # node is sentence node index; inner and outer are groups
            # Indices (input, tgroup) in inner and outer groups
            inner_nodes = tgroup_dict[inner]
            outer_nodes = tgroup_dict[outer]
            # Get the tgroup index for the merge node
            merge_tg_i = dict(outer_nodes)[node]
            # Get input indices for outer group's units before and after the merged node
            prec_outer = [n for n, i in outer_nodes if i < merge_tg_i]
            foll_outer = [n for n, i in outer_nodes if i > merge_tg_i]
            if prec_outer or foll_outer:
                # Get input indices for inner group nodes other than the merge node
                other_inner = [n for n, i in inner_nodes if n != node]
                # Each outer group node before the merge node must precede all inner group nodes,
                # and each outer group node after the merge node must follow all inner group nodes.
                # Add order pair constraints (using input indices) for these constraints.
                for o in prec_outer:
                    for i in other_inner:
                        self.order_pairs.append([o, i])
                for o in foll_outer:
                    for i in other_inner:
                        self.order_pairs.append([i, o])
#        print('  Order pairs: {}'.format(self.order_pairs))

    def svar(self, name, lower, upper, lower_card=0, upper_card=MAX, ess=True):
        return Var(name, lower, upper, lower_card, upper_card,
                   essential=ess, rootDS=self.dstore)

    def create_variables(self, verbosity=0):
        """Create an order IVar for each translation node and variables for each group tree."""
        # Reinitialize variables
        self.variables.clear()
        nnodes = len(self.nodes)
#        print("Creating variables: nnodes {}, order pairs {}".format(nnodes, self.order_pairs))
        self.variables['order_pairs'] = DetVar("order_pairs", set([tuple(positions) for positions in self.order_pairs]))
        self.variables['order'] = [IVar("o{}".format(i), set(range(nnodes)), rootDS=self.dstore, essential=True) for i in range(nnodes)]
#        # target-language trees
#        self.variables['tree_sindices'] = []
#        self.variables['trees'] = []
#        for i, t in enumerate(self.trees):
#            if len(t) > 1:
#                # Only make a variable if the tree has more than one node.
#                self.variables['tree_sindices'].append(DetVar("tree{}_sindices".format(i), set(t)))
#                self.variables['trees'].append(self.svar("tree{}".format(i), set(), set(range(nnodes)), len(t), len(t), ess=False))

    def create_constraints(self, verbosity=0):
        """Make order and disjunction constraints."""
        # Reinitialize constraints
        self.constraints.clear()
        if verbosity:
            print("Creating constraints for {}".format(self))
        ## Order constraints
        order_vars = self.variables['order']
        self.constraints.append(PrecedenceSelection(self.variables['order_pairs'], order_vars))
        self.constraints.append(Order(order_vars))
#        ## Tree constraints
#        for i_var, tree in zip(self.variables['tree_sindices'], self.variables['trees']):
#            self.constraints.append(UnionSelection(tree, i_var, order_vars))
#            # Convexity (projectivity)
#            self.constraints.append(SetConvexity(tree))

    def realize(self, verbosity=0, display=True, all_trans=False, interactive=False):
        """Run constraint satisfaction on the order and disjunction constraints,
        and convert variable values to sentence positions."""
#        print("Realizing {}".format(self))
        generator = self.solver.generator(test_verbosity=verbosity, expand_verbosity=verbosity)
        try:
            proceed = True
            while proceed:
                # Run solver to find positions (values of 'order' variables)
                succeeding_state = next(generator)
                order_vars = self.variables['order']
                positions = [list(v.get_value(dstore=succeeding_state.dstore))[0] for v in order_vars]
#                print("Found positions {}".format(positions))
                # list of (form, position) pairs; sort by position
                node_pos = list(zip([n[0] for n in self.nodes], positions))
                node_pos.sort(key=lambda x: x[1])
                # just the form
                output = [n[0] for n in node_pos]
                self.outputs.append(output)
                self.output_strings.append(TreeTrans.output_string(output))
                if display:
                    self.display(len(self.outputs)-1)
                if verbosity:
                    print('FOUND REALIZATION {}'.format(self.outputs[-1]))
                if all_trans:
                    continue
                if not interactive or not input('SEARCH FOR ANOTHER REALIZATION FOR TRANSLATION {}? [yes/NO] '.format(self)):
                    proceed = False
        except StopIteration:
            if verbosity:
                print('No more realizations for translation')

##class Translation:
##    """Representation of a single translation for an input sentence (with
##    multiple possible orders and morphological realizations of individual
##    words). Multiple translations are possible with a single Solution."""
##
##    def __init__(self, solution, attribs, index, trees=None, verbosity=0):
##        self.solution = solution
##        self.index = index
##        self.sentence = solution.sentence
##        self.verbosity = verbosity
##        # Create GNode dict and list of target group, gnodes and tnodes
##        # from attributes
##        self.gnode_dict = {}
##        self.group_attribs = []
##        for tgroup, tgnodes, tnodes, ginst in attribs: 
##            print('Translation: tgroup {}, tgnodes {}, tnodes {}, ginst {}'.format(tgroup, tgnodes, tnodes, ginst))
##            for tgnode, tokens, feats, agrs, t_index in tgnodes:
##                if tgnode in self.gnode_dict:
##                    print(" Translation: tgnode {} already in gnode_dict with value {}".format(tgnode, self.gnode_dict[tgnode]))
##                self.gnode_dict[tgnode] = (tgroup, tokens, feats, agrs, t_index)
##            self.group_attribs.append((tgroup, tnodes, ginst, tgroup.agr))
##        # form list / order constraint pairs for each sentence position
##        self.nodes = []
##        # Ordered units: merged groups or uncovered words
##        self.chunks = []
##        # Merged group indices
##        self.mergers = []
##        # pairs of node indices representing order constraints
##        self.order_pairs = []
##        # Source-sentence indices for tgroup trees
##        self.trees = trees
##        # Root domain store for variables
##        self.dstore = DStore(name="T{}".format(self.index))
##        # Order variables for each node, tree variables for groups
##        self.variables = {}
##        # Order and disjunction constraints
##        self.constraints = []
##        # Translation needs a solver to figure out positions of words
##        self.solver = Solver(self.constraints, self.dstore,
##                             description='target realization',
##                             verbosity=verbosity)
##        # These are produced in self.build()
##        self.node_features = None
##        self.group_nodes = None
##        self.agreements = None
##        # Final outputs; different ones have alternate word orders
##        self.outputs = []
##        # Strings representing outputs
##        self.output_strings = []
##
##    def __repr__(self):
##        return "{}[{}] ->".format(self.solution, self.index)
##
##    def display(self, index):
##        print("{}  {}".format(self, self.output_strings[index]))
##                              #self.out_string(index)))
##
##    def display_all(self):
##        for index in range(len(self.outputs)):
##            self.display(index)
##
###    def out_string(self, index):
###        '''Convert output to a string for pretty printing.'''
###        l = []
###        for word_list in self.outputs[index]:
###            if len(word_list) == 1:
###                l.append(word_list[0])
###            else:
###                l.append('|'.join(word_list))
###        return ' '.join(l)
##
##    @staticmethod
##    def output_string(output):
##        l = []
##        for word_list in output:
##            if len(word_list) == 1:
##                l.append(word_list[0])
##            else:
##                l.append('|'.join(word_list))
##        return ' '.join(l)
##
##    def initialize(self, verbosity=0):
##        """Set up everything needed to run the constraints and generate the translation."""
##        if verbosity:
##            print("Initializing translation {}".format(self))
##        self.build(verbosity=verbosity)
##        self.generate_words(verbosity=verbosity)
##        self.set_chunks(verbosity=verbosity)
##        self.make_order_pairs(verbosity=verbosity)
##        self.create_variables(verbosity=verbosity)
##        self.create_constraints(verbosity=verbosity)
##
##    def build(self, verbosity=0):
##        """Unify translation features for merged nodes, map agr features from source to target,
##        generate surface target forms from resulting roots and features."""
##        if verbosity:
##            print('Building {}'.format(self))
##        tginsts, tgnodes, trans_index = self.group_attribs, self.gnode_dict, self.index
###        print("Tginsts {}, tgnodes {}, trans_index {}".format(tginsts, tgnodes, trans_index))
##        # Figure out the target forms for each snode
###        print('tgnodes {}'.format(tgnodes))
##        # Dictionary mapping source node indices to initial target node indices
##        tnode_index = 0
##        node_index_map = {}
##        node_features = []
##        agreements = {}
##        group_nodes = {}
##        for snode, (gnodes, features) in zip(self.sentence.nodes, self.solution.snodes):
##            if verbosity > 1:
##                print(" Translation: build(): snode {}, gnodes {}, features {}, tnode_index {}".format(snode, gnodes, features.__repr__(), tnode_index))
##                print("   gnode_dict: {}".format(self.gnode_dict))
##            if not gnodes:
##                # snode is not covered by any group
##                node_index_map[snode.index] = tnode_index
##                node_features.append((snode.token, None, []))
##                tnode_index += 1
##            else:
##                t_indices = []
##                if len(gnodes) > 1:
##                    # There are two gnodes for this snode; only the concrete node can have translations
##                    # Check if there is no translation for one or the other; if so, skip this snode and
##                    # don't increment tnode_index
##                    if gnodes[0] not in tgnodes or gnodes[1] not in tgnodes:
###                        print("No translation for {}".format(snode))
##                        continue
##                    gn0, gn1 = tgnodes[gnodes[0]], tgnodes[gnodes[1]]
##                    if verbosity > 1:
##                        print(" build(): gn0 {}".format(gn0))
##                        print("          gn1 {}".format(gn1))
##                    tgroups, tokens, targ_feats, agrs, t_index = zip(gn0, gn1)
##                    token = False
##                    i = 0
##                    # Find the token that's not a cat
##                    while not token:
##                        t = tokens[i]
##                        if not Entry.is_cat(t):
##                            token = t
##                        i += 1
##                    targ_feats = FeatStruct.unify_all(targ_feats)
###                    print(" token {}, targ feats {}".format(token, targ_feats.__repr__()))
##                    # Merge the agreements
##                    agrs = Translation.merge_agrs(agrs)
###                    print(" merged agrs {}".format(agrs))
##                    t_indices.append((tgroups[0], gn0[-1]))
##                    t_indices.append((tgroups[1], gn1[-1]))
##                    ## Record this node and its groups in mergers
##                    tg = list(zip(tgroups, gnodes))
###                    print(" tgroups/gnodes {}".format(tg))
##                    # Sort the groups by which is the "outer" group in the merger
##                    tg.sort(key=lambda x: x[1].cat)
##                    tg = [x[0] for x in tg]
###                    print("  sorted tg {}".format(tg))
##                    print("Creating merger for snode index {}, tnode index {}".format(snode.index, tnode_index))
##                    self.mergers.append([tnode_index, tg])
###                    print(' tgroups {}, token {}, t_indices {}'.format(tgroups, token, t_indices))
##                else:
##                    gnode = gnodes[0]
##                    if gnode not in tgnodes:
###                        print(' snode {} / gnode {} has no translation'.format(snode, gnode))
##                        continue
##                    else:
##                        gnode = gnodes[0]
##                        tgroup, token, targ_feats, agrs, t_index = tgnodes[gnode]
###                        if targ_feats:
###                            print("targ feats {}, frozen? {}".format(targ_feats.__repr__(), targ_feats.frozen()))
##                        if len(tgroup.tokens) > 1:
##                            t_indices.append((tgroup, t_index))
###                    print(' tgroup {}, token {}, t_index {}'.format(tgroup, token, t_index))
##                            
##                # Make target and source features agree as required
##                if not targ_feats:
##                    targ_feats = FeatStruct({})
###                print("Making targ feats {} and agrs {} agree".format(targ_feats.__repr__(), agrs))
##                if agrs:
##                    # Use an (unfrozen) copy of target features
##                    targ_feats = targ_feats.copy(True)
##                    features.agree(targ_feats, agrs)
##                node_index_map[snode.index] = tnode_index
##                tnode_index += 1
##                node_features.append((token, targ_feats, t_indices))
##                for t_index in t_indices:
##                    group_nodes[t_index] = (token, targ_feats)
###        print("S->T index mapping {}".format(node_index_map))
###        print('Trees {}'.format(self.trees))
##        # Fix indices in tgroup trees
##        trees = []
##        for t in self.trees:
##            tree = []
##            for src_index in t:
##                if src_index in node_index_map:
##                    tree.append(node_index_map[src_index])
##            trees.append(tree)
##        self.trees = trees
###        print('Mapped tree indices {}'.format(self.trees))
##        # Add TNode elements
##        tgnode_elements = []
##        for ginst_i, (tginst, tnodes, ginst, agr) in enumerate(tginsts):
##            if agr:
##                agreements[tginst] = agr
##                if verbosity:
##                    print(" build(): ginst {} agr {}, agreements {}".format(ginst, agr, agreements))
##            if tnodes:
##                for tnode in tnodes:
##                    features = tnode.features or FeatStruct({})
##                    src_index = len(node_features)
###                    print('TG {}, tnode {}, sindex {}, ginst {}'.format(tginst, tnode, src_index, ginst))
##                    self.trees[ginst_i].append(src_index)
##                    index = [(tginst, tnode.index)]
##                    node_features.append((tnode.token, features, index))
##                    group_nodes[index[0]] = (tnode.token, features)
###        if agreements:
###            print("Agreements {}".format(agreements))
###        print("Node features: {}".format(node_features))
##        self.node_features = node_features
##        self.group_nodes = group_nodes
##        self.agreements = agreements
##
##    def generate_words(self, verbosity=0):
##        """Do inter-group agreement constraints, and generate wordforms for each target node."""
##        for group, agr_constraints in self.agreements.items():
##            for agr_constraint in agr_constraints:
##                i1, i2 = agr_constraint[0], agr_constraint[1]
##                feature_pairs = agr_constraint[2:]
##                # Find the sentence nodes for the agreeing group nodes in the group_nodes dict
##                agr_node1 = self.group_nodes[(group, i1)]
##                agr_node2 = self.group_nodes[(group, i2)]
###                print("Found node1 {} and node2 {} for constraint {}".format(agr_node1, agr_node2, feature_pairs))
##                agr_feats1, agr_feats2 = agr_node1[1], agr_node2[1]
##                agr_feats1.mutual_agree(agr_feats2, feature_pairs)
##        generator = self.sentence.target.generate
##        for token, features, index in self.node_features:
##            if verbosity:
##                print("Token {}, features {}, index {}".format(token, features.__repr__(), index))
##            root, pos = Translation.get_root_POS(token)
##            output = [token]
##            if not pos:
##                # This word doesn't require generation, just return it in a list
##                self.nodes.append((output, index))
##            else:
##                output = generator(root, features, pos=pos)
##                self.nodes.append((output, index))
##            if verbosity:
##                print("Generating target node {}: {}".format(index, output))
##
##    @staticmethod
##    def get_root_POS(token):
##        """Token may be something like guata_, guata_v, or guata_v_t."""
##        root, x, pos = token.partition("_")
##        return root, pos
##
##    def set_chunks(self, verbosity=0):
##        """Find output chunks: a list of sets of snode indices."""
##        chunk_attribs = []
##        for index, (tokens, constraints) in enumerate(self.nodes):
##            # Is this an uncovered node/token
##            if not constraints:
##                chunk_attribs.append((tokens[0], {index}))
##            else:
##                # Groups that the node belongs to
##                for g in [c[0] for c in constraints]:
##                    # Find previous chunk list if it exists
##                    found = False
##                    for c, i in chunk_attribs:
##                        if c == g:
##                            i.add(index)
##                            found = True
##                            break
##                    if not found:
##                        chunk_attribs.append((g, {index}))
##        # Merge chunks that share nodes
##        for index, (label, indices) in enumerate(chunk_attribs):
##            if self.chunks and indices.intersection(self.chunks[-1]):
##                # merged this chunk with the last
##                self.chunks[-1].update(indices)
##            else:
##                self.chunks.append(indices)
##
##    @staticmethod
##    def merge_agrs(agr_list):
##        """Merge agr dicts in agr_list into a single agr dict."""
###        print("  Merging agreements for merged nodes {}".format(agr_list))
##        result = {}
##        for agr in agr_list:
##            if not agr:
##                continue
##            for k, v in agr:
##                if k in result:
##                    if result[k] != v:
##                        print("Warning: agrs in {} failed to merge".format(agr_list))
##                        return 'fail'
##                    else:
##                        continue
##                else:
##                    result[k] = v
###        print("  Result", result)
##        return result
##
##    def make_order_pairs(self, verbosity=0):
##        """Convert group/index pairs to integer (index) order pairs.
##        Constrain chunks to appear in source-language order.
##        Constrain order in merged groups."""
##        tgroup_dict = {}
##        for index, (forms, constraints) in enumerate(self.nodes):
###            print("Order pairs for node {} with forms {} and constraints {}".format(index, forms, constraints))
##            for tgroup, tg_index in constraints:
##                if tgroup not in tgroup_dict:
##                    tgroup_dict[tgroup] = []
##                tgroup_dict[tgroup].append((index, tg_index))
###                print(" Tgroup_dict entry for tgroup {}: node index {}, tg index {}".format(tgroup, index, tg_index))
##        for pairs in tgroup_dict.values():
###            print(' pairs {}'.format(pairs))
##            for pairpair in itertools.combinations(pairs, 2):
##                pairpair = list(pairpair)
###                print('  pairpair {}'.format(pairpair))
##                # Sort by the target index
##                pairpair.sort(key=lambda x: x[1])
##                self.order_pairs.append([x[0] for x in pairpair])
##        # Chunks; order every node in each chunk before every node in the next chunk
##        for ci, indices in enumerate(self.chunks[:-1]):
##            next_indices = self.chunks[ci+1]
##            for index in indices:
##                for next_index in next_indices:
##                    self.order_pairs.append([index, next_index])
##        # Order nodes within merged groups
##        for node, (inner, outer) in self.mergers:
###            print("Merger: tnode index {}, inner group {}, outer group {}".format(node, inner, outer))
##            # node is sentence node index; inner and outer are groups
##            # Indices (input, tgroup) in inner and outer groups
##            inner_nodes = tgroup_dict[inner]
##            outer_nodes = tgroup_dict[outer]
##            # Get the tgroup index for the merge node
###            print("tgroup_dict {}, inner {}, outer {}, node {}".format(tgroup_dict, inner, outer, node))
##            merge_tg_i = dict(outer_nodes)[node]
###            print("pos of merge node in outer group: {}".format(merge_tg_i))
##            # Get input indices for outer group's units before and after the merged node
##            prec_outer = [n for n, i in outer_nodes if i < merge_tg_i]
##            foll_outer = [n for n, i in outer_nodes if i > merge_tg_i]
###            print("outer nodes before {} / after {} merger node".format(prec_outer, foll_outer))
##            if prec_outer or foll_outer:
##                # Get input indices for inner group nodes other than the merge node
##                other_inner = [n for n, i in inner_nodes if n != node]
###                print('inner nodes other than merge node: {}'.format(other_inner))
##                # Each outer group node before the merge node must precede all inner group nodes,
##                # and each outer group node after the merge node must follow all inner group nodes.
##                # Add order pair constraints (using input indices) for these constraints.
##                for o in prec_outer:
##                    for i in other_inner:
##                        self.order_pairs.append([o, i])
##                for o in foll_outer:
##                    for i in other_inner:
##                        self.order_pairs.append([i, o])
###        print('Order pairs: {}'.format(self.order_pairs))
##
##    def svar(self, name, lower, upper, lower_card=0, upper_card=MAX, ess=True):
##        return Var(name, lower, upper, lower_card, upper_card,
##                   essential=ess, rootDS=self.dstore)
##
##    def create_variables(self, verbosity=0):
##        """Create an IVar for each translation node and variables for each group tree."""
##        nnodes = len(self.nodes)
##        self.variables['order_pairs'] = DetVar("order_pairs", set([tuple(positions) for positions in self.order_pairs]))
##        self.variables['order'] = [IVar("o{}".format(i), set(range(nnodes)), rootDS=self.dstore, essential=True) for i in range(nnodes)]
##        # target-language trees
##        self.variables['tree_sindices'] = []
##        self.variables['trees'] = []
##        for i, t in enumerate(self.trees):
###            print('Tree {}: {}'.format(i, t))
##            if len(t) > 1:
##                # Only make a variable if the tree has more than one node.
##                self.variables['tree_sindices'].append(DetVar("tree{}_sindices".format(i), set(t)))
##                self.variables['trees'].append(self.svar("tree{}".format(i), set(), set(range(nnodes)), len(t), len(t), ess=False))
##
##    def create_constraints(self, verbosity=0):
##        """Make order and disjunction constraints."""
##        if verbosity:
##            print("Creating constraints for {}".format(self))
##        ## Order constraints
##        order_vars = self.variables['order']
###        print("Order pairs {}".format(self.variables['order_pairs']))
##        self.constraints.append(PrecedenceSelection(self.variables['order_pairs'], order_vars))
##        self.constraints.append(Order(order_vars))
##        ## Tree constraints
##        for i_var, tree in zip(self.variables['tree_sindices'], self.variables['trees']):
##            self.constraints.append(UnionSelection(tree, i_var, order_vars))
###            i_var.pprint()
###            tree.pprint()
###            print("Tree union {}".format(self.constraints[-1]))
##            # Convexity (projectivity)
##            self.constraints.append(SetConvexity(tree))
###        for c in self.constraints:
###            print(c)
##
##    def realize(self, verbosity=0, display=True, all_trans=False):
##        """Run constraint satisfaction on the order and disjunction constraints,
##        and convert variable values to sentence positions."""
##        generator = self.solver.generator(test_verbosity=verbosity, expand_verbosity=verbosity)
##        try:
##            proceed = True
##            while proceed:
##                succeeding_state = next(generator)
##                order_vars = self.variables['order']
##                positions = [list(v.get_value(dstore=succeeding_state.dstore))[0] for v in order_vars]
##                node_pos = list(zip([n[0] for n in self.nodes], positions))
##                node_pos.sort(key=lambda x: x[1])
##                output = [n[0] for n in node_pos]
##                self.outputs.append(output)
##                self.output_strings.append(Translation.output_string(output))
##                if display:
##                    self.display(len(self.outputs)-1)
##                if verbosity:
##                    print('FOUND REALIZATION {}'.format(self.outputs[-1]))
##                if all_trans:
##                    continue
##                if not input('SEARCH FOR ANOTHER REALIZATION FOR TRANSLATION {}? [yes/NO] '.format(self)):
##                    proceed = False
##        except StopIteration:
##            if verbosity:
##                print('No more realizations for translation')
