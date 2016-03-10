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

ZERO_TIME = datetime.timedelta() 

def get_time():
    return datetime.datetime.utcnow()

class Session:
    """A record of a single user's responses to a set of sentences."""

    id = 0

    def __init__(self, user=None):
        self.start = get_time()
        self.user = user
        self.end = None
        self.running = True
        # List of SentRecord objects
        self.sentences = []
        self.id = Session.id
        Session.id += 1

    def __repr__(self):
        return "@{}".format(self.id)

    def length(self):
        """Length of the session as a time delta object."""
        if self.running:
            return ZERO_TIME
        else:
            return self.end - self.start

    def quit(self):
        """Set the end time and stop running."""
        self.running = False
        self.end = get_time()

    def record(self, sentence, segs, trans_dict):
        """Record feedback about a segment's translation within a sentence."""
        sentrecord = sentence.record
        print("{} recording translation for {} in {}".format(self, segs, sentrecord))
        segment_key = trans_dict.get('seg')
        # It might be capitalized
        segment_key = lower(segment_key)
        segrecord = sentrecord.segments.get(segment_key)
        print("Segment to record: {}".format(segrecord))
        filter_dict = {}
        for key, value in trans_dict.items():
            if key.isdigit():
#                seg_key, x, segpart_key = key.partition(':')
                print("  feedback key {}: value {}".format(key, value))
                filter_dict[key] = value
        if not filter_dict:
            # No translation selected, get alternate translation submitted
            print("Alternate translation: {}".format(trans_dict.get('tra')))
        else:
            print("Filter dict: {}".format(filter_dict))

class SentRecord:
    """A record of a Sentence and a single user's response to it."""

    def __init__(self, sentence, session=None, user=None):
        self.session = session
        self.raw = sentence.raw
        self.tokens = sentence.tokens
        self.time = get_time()
        self.user = user
        # Add to parent Session
        session.sentences.append(self)
        # a dict of SegRecord objects, with token strings as keys
        self.segments = {}

    def __repr__(self):
        session = "{}".format(self.session) if self.session else ""
        return "{}:{}".format(session, self.raw)

class SegRecord:
    """A record of a sentence segment and its translation by a user."""

    def __init__(self, solseg, feedback=None, sentence=None, session=None):
        # a SentRecord instance
        self.sentence = sentence
        self.session = session
        self.indices = solseg.indices
        self.translation = solseg.translation
        self.tokens = solseg.token_str
        # Add to parent SentRecord
        self.sentence.segments[self.tokens] = self
        self.feedback = feedback

    def __repr__(self):
        session =  "{}".format(self.session) if self.session else ""
        return "{}:{}".format(session, self.tokens) 

class Feedback:
    """Feedback from a user about a segment and its translation."""

    def __init__(self, accept=True, pos_indices=(-1, -1), choice_index=-1, translation=None):
        """
        EITHER the user simply
        -- accepts the system's translation (accept=True) OR
        -- makes a selection from the alternatives offered by the system
           (pos_indices and choice_index are non-negative) OR
        -- provides an alternate translation (translation is not None).
        No backpointer to the SegRecord that this refers to.
        """
        self.accept = accept
        self.pos_indices = pos_indices
        self.choice_index = choice_index
        self.translation = translation
        self.id = '@'
        if accept:
            self.id += "ACC"
        else:
            self.id += "REJ:"
            if translation:
                self.id += translation
            else:
                self.id += "{}={}".format(pos_index, choice_index)

ACCEPT = Feedback()

