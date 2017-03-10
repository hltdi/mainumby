# Mainumby. Parsing and translation with minimal dependency grammars.
#
########################################################################
#
#   This file is part of the Mainumby project within the PLoGS metaproject
#   for parsing, generation, translation, and computer-assisted
#   human translation.
#
#   Copyright (C) 2017; PLoGS <gasser@indiana.edu>
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

# This eventually loads ui, segment, record, cs, utils, language, entry
# some morphology functions (more needed?)
from .sentence import *

class Trainer:
    """Take a bilingual Document and the two associated languages, and learn
    new groups based on current groups."""

    def __init__(self, doc, verbose=False):
        self.doc = doc

    def initialize(self):
        # Initialize sentences if they're not already
        if not doc.initialized:
            doc.initialize()

    def train1(self, srcsent, targsent):
        """Process a sentence pair."""
        # Groups find in target language initialization
        targgroups = targsent.groups
        # First find all solutions for the source sentence
        srcsent.solve(translate=True, all_sols=True)
        for solution in srcsent.solutions:
            print("Checking solution {}".format(solution))
            for ginst in solution.ginsts:
                tgroup, gnodes, tnodes = ginst.translations
                # Check whether tgroup is among groups found target initialization
