#   
#   Mainumby: sentences and how to parse and translate them.
#
########################################################################
#
#   This file is part of the HLTDI L^3 project
#   for parsing, generation, translation, and computer-assisted
#   human translation.
#
#   Copyright (C) 2016 HLTDI <gasser@indiana.edu>
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

# 2016.02.29
# -- Created.

import datetime

def get_time():
    return datetime.datetime.utctime()

class Session:
    """A record of a single user's responses to a set of sentences."""

    def __init__(self, user=None):
        self.start = get_time()
        self.user = user
        self.end = None
        self.running = True
        self.sentences = []

    def quit(self):
        self.running = False
        self.end = get_time()

class SentRecord:
    """A record of a Sentence and a single user's response to it."""

    def __init__(self, sentence, user=None):
        self.raw = sentence.raw
        self.tokens = sentence.tokens
        self.time = get_time()
        self.user = user
        # a list of SolRecord objects.
        self.solutions = []

class SolRecord:
    """A record of a sentence segmentation into groups and their translations."""

    def __init__(self, solution, srecord):
        # a SentRecord object
        self.sentence = sentence
        # a list of SolSeg objects
        self.segments = []

        
