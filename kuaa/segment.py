#   
#   Mainumby: sentences and solution segments
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

# 2016.01.05
# -- Split off from sentence.py
# 2016.01.16
# -- Added SolSeg class for sentence solution segments with translations.

import itertools, copy
from .cs import *
# needed for a few static methods
from .entry import Entry, Group

class SolSeg:
    """Sentence solution segment, realization of a single Group."""

    # colors to display segments in interface
    tt_colors = ['red', 'blue', 'sienna', 'green', 'purple', 'red', 'blue', 'sienna', 'green', 'purple', 'red', 'blue', 'sienna', 'green', 'purple']

    def __init__(self, solution, indices, translation, tokens, color=None):
        self.solution = solution
        self.indices = indices
        self.translation = translation
        self.tokens = tokens
        self.token_str = ' '.join(tokens)
        self.color = color
        self.html = []
        print("Created {}".format(self))

    def __repr__(self):
        """Print name."""
        return "<<{}>>".format(self.token_str)

    def set_html(self, index):
        "Set the HTML markup for this segment, given its position in the sentence."""
        self.color = 'Silver' if not self.translation else SolSeg.tt_colors[index]
        transhtml = '<table border=1>'
        for t in self.translation:
            if '|' in t:
                t = t.replace('|', '<br/>')
            if ' ' in t:
                transhtml += '<tr>'
                ts = t.split()
                for tt in ts:
                    if '/' in tt:
                        transhtml += '<td><table>'
                        for ttt in tt.split('/'):
                            transhtml += '<tr><td>' + ttt + '</td></tr>'
                        transhtml += '</table></td>'
                    else:
                        transhtml += '<td>' + tt + '</td>'
                transhtml += '</tr>'
            else:
                transhtml += '<tr><td>' + t + '</td></tr>'
        transhtml = transhtml.replace('_', ' ')
        transhtml += '</table>'
        tokens = self.token_str
        if index==0:
            tokens = tokens.capitalize()
        self.html = (tokens, self.color, transhtml)

    @staticmethod
    def list_html(segments):
        """Set the HTML for the list of segments in a sentence."""
        for i, segment in enumerate(segments):
            segment.set_html(i)

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
